# 03. Architecture and Design

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-DES-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Architectural Goals

- Provide a local browser UI for discrete TRELLIS pipeline execution.
- Keep GPU/model-heavy execution in Python.
- Keep UI and backend contracts typed and testable.
- Preserve the original CLI path while adding a modular workflow runtime.
- Make pipeline progress observable through status, metrics, logs, and artifacts.

## Architectural Style

The system uses a client/server architecture:

- Client: React single-page app served by Vite during development.
- Server: FastAPI application that exposes workflow state and commands.
- Runtime: In-memory session records managed by `WorkflowRunner`.
- Execution: Background thread execution with one worker by default.
- Storage: File-system artifacts under `outputs/<session-id>/`.

## Component View

![React frontend component architecture diagram](diagrams/02-frontend-component-architecture.svg)

| Component | Path | Responsibility |
|---|---|---|
| React app shell | `web/src/App.tsx` | Top-level state, API calls, session polling, command handlers |
| API client | `web/src/api/client.ts` | HTTP wrapper for workflow endpoints |
| Parameter panel | `web/src/components/ParameterPanel.tsx` | Renders grouped workflow parameter controls |
| Step list | `web/src/components/StepList.tsx` | Renders ordered pipeline steps and per-step run controls |
| Step details | `web/src/components/StepDetails.tsx` | Renders selected step description, status, metrics, and errors |
| Log panel | `web/src/components/LogPanel.tsx` | Renders captured server logs |
| Artifact panel | `web/src/components/ArtifactPanel.tsx` | Renders generated artifact links |
| FastAPI app | `trellis_workflow/app.py` | HTTP routes, CORS, static artifact serving |
| Domain models | `trellis_workflow/models.py` | Pydantic contracts for config, state, logs, artifacts |
| Workflow definitions | `trellis_workflow/definitions.py` | Canonical steps and parameter metadata |
| Workflow runner | `trellis_workflow/workflow.py` | Session lifecycle, dependency enforcement, background execution |
| Exporter | `trellis_workflow/exporter.py` | GLB/OBJ export, texture baking, artifact metadata |
| Runtime bootstrap | `trellis_workflow/runtime/bootstrap.py` | Environment variables and TRELLIS import path setup |

## Runtime Data Flow

![TRELLIS data and artifact flow diagram](diagrams/05-data-artifact-flow.svg)

1. UI calls `GET /api/workflows/default`.
2. API returns step and parameter metadata.
3. User edits config and calls `POST /api/sessions`.
4. Server normalizes config and creates `SessionRecord`.
5. User requests `run-next`, `run-all`, or `run step`.
6. Server validates dependency order and busy state.
7. `WorkflowRunner` submits a background job.
8. Step handler updates runtime context and emits logs.
9. UI polls `GET /api/sessions/{session_id}` while busy.
10. Export step writes artifacts and returns artifact metadata.

## Session State Design

### `WorkflowState`

External JSON state returned to the UI:

- `session_id`: Unique session identifier.
- `config`: Normalized workflow configuration.
- `steps`: Ordered step states.
- `logs`: Bounded log entries.
- `artifacts`: Generated artifact metadata.
- `busy`: Whether background work is active.
- `active_step_id`: Current step id, when known.
- `created_at`: UTC creation timestamp.
- `updated_at`: UTC update timestamp.

### `RuntimeContext`

Internal in-memory state not returned to the browser:

- Loaded TRELLIS pipeline.
- Raw and preprocessed images.
- Conditioning tensors.
- Sparse coordinates.
- Shape and texture latents.
- Decode resolution.
- Decoded mesh.
- RNG snapshots after sparse and shape sampling.

The separation is intentional: the UI receives serializable summaries, while Python retains non-serializable model and tensor objects.

## Step Dependency Design

![Workflow step dependency graph](diagrams/08-step-dependency-graph.svg)

The backend enforces the canonical step order from `PIPELINE_STEPS`. A step may run only if every earlier step has status `completed` or `skipped`. Re-running a step resets downstream steps to `pending` and clears downstream artifacts where appropriate.

This protects runtime consistency. For example, changing a sparse structure requires shape sampling, texture sampling, decode, and export to be repeated.

## Execution Model

| Design element | Decision |
|---|---|
| Worker model | `ThreadPoolExecutor(max_workers=1)` |
| Reason | Avoid concurrent GPU/model memory contention during local workflows |
| API response timing | Step start endpoints return immediately after scheduling work |
| UI update model | Poll session state every 1.5 seconds while busy |
| Failure handling | Step state becomes `failed`, error text is recorded, `run-all` stops |
| Log capture | Stdout/stderr redirected through `LogCapture` during step execution |

## API Server Design

The server exposes a local development API with CORS restricted to Vite origins. It mounts `/outputs` to serve generated files from the project output directory.

The server owns `WorkflowRunner` as a module-level singleton. This is suitable for local development and one-user operation. Production deployments should replace this with persistent job/session storage and access control.

## UI Design

The UI is organized into three work zones:

- Left column: workflow parameters grouped by pipeline step.
- Middle column: ordered pipeline steps and selected step details.
- Right column: generated artifacts and live logs.

The UI uses typed API responses and does not hard-code step definitions. It depends on the backend workflow definition for step and parameter metadata, which keeps the UI aligned with server behavior.

## Error Handling Design

| Error source | Handling |
|---|---|
| API request failure | UI displays error banner |
| Missing session | API returns 404 |
| Missing step | API returns 404 |
| Busy workflow | API returns 409 |
| Out-of-order execution | API returns 409 |
| Runtime exception | Step state becomes failed and log includes error |
| Empty mesh/watchdog condition | Runtime raises actionable workflow error |

## Artifact Design

Artifacts are represented by:

- `name`: Filename.
- `kind`: image, model, mesh, texture, or other.
- `path`: Repository-relative file path.
- `url`: API-served URL when under `outputs/`.
- `size_bytes`: File size if present.

Relative output directories are scoped by session id: `outputs/<session-id>/<output-name>.*`.

## Maintainability Design Decisions

| Decision | Rationale |
|---|---|
| Pydantic backend models | Enforce API schema and validation |
| TypeScript frontend models | Catch UI/API integration errors at build time |
| Separate workflow definitions | Single source of truth for UI controls and step order |
| Separate exporter module | Keeps runtime orchestration independent from mesh export details |
| Runtime bootstrap module | Ensures TRELLIS environment variables and paths are configured before imports |
| Contract tests without model loading | Fast verification in development and CI without heavy model dependencies |

## Known Limitations

- Sessions are process-local and non-persistent.
- A server restart clears session state.
- No authentication or authorization is implemented.
- The frontend uses polling rather than server-sent events or websockets.
- Long model steps cannot currently be cancelled from the UI.
- The API is designed for local development, not internet exposure.

## Future Design Extensions

- Add persistent job records using SQLite or PostgreSQL.
- Add cancel/retry controls with cooperative step cancellation.
- Add server-sent events for live log streaming.
- Add user authentication for shared environments.
- Add browser-side GLB preview after export.
- Add upload endpoint for image files instead of path-only input.

## Design Review Checklist

| Question | Status |
|---|---|
| Are requirements allocated to components? | Yes |
| Are external interfaces documented? | Yes |
| Is state ownership defined? | Yes |
| Is error handling defined? | Yes |
| Is dependency order defined? | Yes |
| Are known limitations documented? | Yes |
