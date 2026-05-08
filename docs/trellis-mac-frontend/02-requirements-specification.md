# 02. Requirements Specification

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-REQ-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Requirement Classification

| Prefix | Category |
|---|---|
| FR | Functional requirement |
| NFR | Non-functional requirement |
| API | API requirement |
| UI | User interface requirement |
| OPS | Operational requirement |
| SEC | Security requirement |
| QA | Quality and verification requirement |

## Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-001 | The system shall expose the TRELLIS pipeline as ordered workflow steps. | Must | Workflow definition contains all approved step IDs in the defined sequence. |
| FR-002 | The system shall allow users to configure tunable workflow parameters before session creation. | Must | UI exposes controls for image path, output name, output directory, model id, device, seed, pipeline type, texture size, texture backend, geometry-only export, sampler steps, sample count, max token count, preprocessing, and decimation target. |
| FR-003 | The system shall create a workflow session from a submitted configuration. | Must | API returns a `WorkflowState` with a unique session id, normalized config, pending steps, and session creation log. |
| FR-004 | The system shall execute a single requested step only after prior dependencies are complete or skipped. | Must | Out-of-order execution returns a conflict response and does not mutate downstream runtime state. |
| FR-005 | The system shall execute the next incomplete step. | Must | `run-next` starts the first non-complete and non-skipped step. |
| FR-006 | The system shall execute all remaining steps in order until completion or failure. | Should | `run-all` advances sequentially and stops on first failed step. |
| FR-007 | The system shall preserve runtime objects between steps within the same API process. | Must | Pipeline, image, conditioning, sparse coordinates, latents, resolution, and mesh remain available in the session runtime context. |
| FR-008 | The system shall capture stdout and stderr emitted by TRELLIS step execution. | Must | Session logs include captured pipeline messages with timestamp, level, optional step id, and message. |
| FR-009 | The system shall report status, timing, summary, metrics, and errors for each step. | Must | Step states include status, timestamps, duration, summary, error, and metric fields. |
| FR-010 | The system shall export generated model artifacts after decode. | Must | Export step writes GLB and OBJ files and exposes artifact metadata. |
| FR-011 | The system shall support optional texture baking. | Must | Export uses texture backend unless geometry-only mode or texture backend `none` is selected. |
| FR-012 | The system shall provide artifact links for generated outputs. | Should | UI displays artifact name, path, size, type, and URL where available. |
| FR-013 | The system shall preview generated model artifacts in the browser. | Should | Served GLB and OBJ artifacts can be selected and rendered in the UI without leaving the workflow console. |
| FR-014 | The system shall allow users to reset the UI view without deleting server state. | Could | Reset clears local session view and leaves API process unaffected. |

## API Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| API-001 | The API shall provide a health endpoint. | Must | `GET /api/health` returns status `ok`. |
| API-002 | The API shall provide the workflow definition. | Must | `GET /api/workflows/default` returns steps and parameter definitions. |
| API-003 | The API shall create sessions. | Must | `POST /api/sessions` accepts `WorkflowConfig` and returns `WorkflowState`. |
| API-004 | The API shall return session state by id. | Must | `GET /api/sessions/{session_id}` returns current `WorkflowState` or 404. |
| API-005 | The API shall list sessions. | Should | `GET /api/sessions` returns workflow states for active in-memory sessions. |
| API-006 | The API shall run a step by id. | Must | `POST /api/sessions/{session_id}/steps/{step_id}/run` starts background execution or returns 409/404. |
| API-007 | The API shall run the next step. | Must | `POST /api/sessions/{session_id}/run-next` starts the next available step. |
| API-008 | The API shall run all remaining steps. | Should | `POST /api/sessions/{session_id}/run-all` starts ordered execution. |
| API-009 | The API shall delete active sessions. | Could | `DELETE /api/sessions/{session_id}` removes in-memory session state. |
| API-010 | The API shall serve generated artifacts. | Must | Static output files are available under `/outputs/...`. |

## UI Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| UI-001 | The UI shall load and render workflow definitions from the API. | Must | Parameter panel and step list reflect the API response. |
| UI-002 | The UI shall provide a parameter panel grouped by pipeline step. | Must | Controls are grouped under step titles and disabled while a workflow step is busy. |
| UI-003 | The UI shall provide workflow command controls. | Must | Create Session, Run Next, Run Remaining, and Reset View are visible and correctly enabled/disabled. |
| UI-004 | The UI shall present pipeline step state. | Must | Step list shows title, status, duration, and per-step run command. |
| UI-005 | The UI shall present selected step details. | Must | Details show description, status, started time, duration, summary, error, and metrics. |
| UI-006 | The UI shall present logs. | Must | Logs show timestamp, step id or session, level, and message. |
| UI-007 | The UI shall present generated artifacts. | Should | Artifacts panel shows generated files and opens URLs in a new browser tab. |
| UI-008 | The UI shall preview served GLB and OBJ artifacts. | Should | Preview panel lists model artifacts, renders the selected file in a canvas, and keeps a direct open link. |
| UI-009 | The UI shall poll active sessions while work is running. | Must | Polling occurs during `busy=true` and stops when the session is idle. |
| UI-010 | The UI shall surface API errors to the user. | Must | Failed API calls display an error banner. |
| UI-011 | The UI shall remain usable at desktop and tablet widths. | Should | Layout reflows using the documented responsive grid breakpoints. |

## Non-Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| NFR-001 | The system shall avoid concurrent heavy TRELLIS work by default. | Must | Workflow runner uses a single worker by default. |
| NFR-002 | The system shall preserve existing CLI behavior. | Must | Existing `generate.py` remains independent from the workflow UI/API. |
| NFR-003 | The system shall use typed data contracts. | Must | Backend models use Pydantic; frontend uses TypeScript interfaces. |
| NFR-004 | The UI shall build successfully with TypeScript strict mode. | Must | `npm run build` completes without TypeScript errors. |
| NFR-005 | Backend tests shall avoid requiring model weights unless explicitly marked as integration tests. | Must | Contract tests cover API/session behavior without loading TRELLIS weights. |
| NFR-006 | The system shall produce actionable failure messages. | Should | Errors include dependency, missing input, busy workflow, not found, or runtime failure detail. |
| NFR-007 | Generated artifacts shall be isolated by session. | Must | Output path is `outputs/<session-id>/<output-name>.*` for relative output directories. |
| NFR-008 | The system shall be maintainable with modular package organization. | Must | Runtime bootstrap, models, definitions, workflow orchestration, exporter, API app, and UI components are separate modules. |

## Operational Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| OPS-001 | The API shall start with a documented command. | Must | Runbook includes `trellis-workflow-api` and `uvicorn` startup paths. |
| OPS-002 | The UI shall start with a documented command. | Must | Runbook includes `npm run dev`. |
| OPS-003 | The system shall document generated artifact location. | Must | Runbook identifies `outputs/<session-id>/`. |
| OPS-004 | The system shall document shutdown procedure. | Must | Runbook includes stopping the API and UI processes. |

## Security Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| SEC-001 | The development API shall restrict CORS to local development origins. | Must | CORS allowlist includes `http://127.0.0.1:5173` and `http://localhost:5173`. |
| SEC-002 | The system shall not expose secrets in documentation or logs by design. | Must | Documentation states secret handling and no token values are embedded. |
| SEC-003 | File artifact serving shall be scoped to the outputs directory. | Must | Static mount serves files from the configured outputs path. |
| SEC-004 | Production deployment shall require additional authentication and authorization controls. | Should | Risk plan lists unauthenticated local API as development-only. |

## Quality Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| QA-001 | Backend contract tests shall pass before release. | Must | `pytest tests` passes. |
| QA-002 | Frontend unit tests shall pass before release. | Must | `npm run test` passes. |
| QA-003 | Frontend production build shall pass before release. | Must | `npm run build` passes. |
| QA-004 | API smoke test shall pass before release. | Should | Health, workflow definition, and session creation endpoints respond correctly. |
| QA-005 | Documentation shall trace requirements to design and verification artifacts. | Must | Traceability matrix maps all baseline requirements. |

## Requirement Approval Criteria

A requirement is baseline-ready when it has:

- A stable ID.
- A single testable statement.
- A priority.
- Acceptance criteria.
- Traceability to design and verification artifacts.
