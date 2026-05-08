# 04. API Contract

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-API-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Base URL

Development base URL:

```text
http://127.0.0.1:8000
```

The Vite development server proxies `/api` and `/outputs` to this server.

## Content Type

Requests and responses use JSON unless otherwise specified.

```http
Content-Type: application/json
```

Generated artifacts are served as static files under `/outputs`.

## Authentication

No authentication is implemented in the current local-development baseline. The API must not be exposed beyond a trusted local machine without adding authentication, authorization, request validation hardening, and network controls.

## CORS

Allowed origins:

- `http://127.0.0.1:5173`
- `http://localhost:5173`

## Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 204 | Successful delete with no response body |
| 404 | Workflow session or step not found |
| 409 | Workflow state conflict, such as busy session or out-of-order step request |
| 422 | FastAPI/Pydantic validation error |
| 500 | Unexpected server error |

## API Session Flow

![API session and step execution flow diagram](diagrams/03-api-session-flow.svg)

## Endpoints

### Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok"
}
```

### Get Workflow Definition

```http
GET /api/workflows/default
```

Returns canonical step definitions and parameter definitions.

Response schema:

```json
{
  "steps": [
    {
      "id": "load_pipeline",
      "title": "Load Pipeline",
      "description": "Load TRELLIS.2 weights, initialize samplers, and move runtime components to the selected device.",
      "parameter_keys": ["model_id", "device"]
    }
  ],
  "parameters": [
    {
      "key": "image_path",
      "label": "Input image",
      "control": "text",
      "step_id": "load_image",
      "description": "",
      "default": "assets/shoe_input.png",
      "options": null,
      "minimum": null,
      "maximum": null
    }
  ]
}
```

### Create Session

```http
POST /api/sessions
```

Request body: `WorkflowConfig`.

Minimal example:

```json
{
  "image_path": "assets/shoe_input.png",
  "output_name": null,
  "output_dir": "outputs",
  "model_id": "microsoft/TRELLIS.2-4B",
  "device": "mps",
  "seed": 42,
  "pipeline_type": "512",
  "texture_size": 1024,
  "no_texture": false,
  "sampler_steps": null,
  "num_samples": 1,
  "max_num_tokens": 49152,
  "preprocess_image": true,
  "texture_backend": "auto",
  "decimation_target": 200000
}
```

Response: `WorkflowState`.

Normalization behavior:

- Empty `output_name` becomes the input image stem.
- `output_name` equal to `same name as the image` also becomes the input image stem.
- Empty `output_dir` becomes `outputs`.
- Empty or zero `sampler_steps` becomes `null`.

### List Sessions

```http
GET /api/sessions
```

Returns all active in-memory workflow sessions.

Response:

```json
[
  {
    "session_id": "ca4c27b2d98f",
    "config": {},
    "steps": [],
    "logs": [],
    "artifacts": [],
    "busy": false,
    "active_step_id": null,
    "created_at": "2026-05-07T00:00:00+00:00",
    "updated_at": "2026-05-07T00:00:00+00:00"
  }
]
```

### Get Session

```http
GET /api/sessions/{session_id}
```

Returns current session state.

Not found response:

```json
{
  "detail": "Workflow session not found."
}
```

### Run Specific Step

```http
POST /api/sessions/{session_id}/steps/{step_id}/run
```

Starts background execution for the requested step.

Success response: updated `WorkflowState` with `busy=true` and `active_step_id` set.

Conflict responses:

```json
{
  "detail": "A workflow step is already running."
}
```

```json
{
  "detail": "Run earlier steps first: Load Pipeline, Load Image"
}
```

### Run Next Step

```http
POST /api/sessions/{session_id}/run-next
```

Starts the first step whose status is not `completed` or `skipped`.

Conflict response when no work remains:

```json
{
  "detail": "All workflow steps are already complete."
}
```

### Run All Remaining Steps

```http
POST /api/sessions/{session_id}/run-all
```

Starts ordered execution from the first incomplete step. Execution stops when all steps complete or a step fails.

### Delete Session

```http
DELETE /api/sessions/{session_id}
```

Success response: HTTP 204 with no body.

### Serve Artifacts

```http
GET /outputs/{session_id}/{filename}
```

Serves generated artifacts stored under the server output directory.

## Data Models

### WorkflowConfig

| Field | Type | Default | Notes |
|---|---|---|---|
| `image_path` | string | `assets/shoe_input.png` | Relative to repo root or absolute path |
| `output_name` | string or null | null | Normalized to input image stem if empty |
| `output_dir` | string | `outputs` | Relative output dirs are scoped by session id |
| `model_id` | string | `microsoft/TRELLIS.2-4B` | Hugging Face model id or local model path |
| `device` | `mps` or `cpu` | `mps` | MPS requires Apple Silicon PyTorch support |
| `seed` | integer | 42 | Used before sparse sampling |
| `pipeline_type` | `512`, `1024`, `1024_cascade` | `512` | Selects model flow path |
| `texture_size` | 512, 1024, or 2048 | 1024 | PBR texture resolution |
| `no_texture` | boolean | false | Exports geometry-only GLB when true |
| `sampler_steps` | integer or null | null | Overrides sampler steps when provided |
| `num_samples` | integer | 1 | Current UI constrains max to one sample |
| `max_num_tokens` | integer | 49152 | Used by cascade shape sampling |
| `preprocess_image` | boolean | true | Enables background removal and crop preprocessing |
| `texture_backend` | `auto`, `metal`, `kdtree`, `none` | `auto` | Export backend preference |
| `decimation_target` | integer | 200000 | Target face count before texture baking |

### StepStatus

Allowed values:

- `pending`
- `running`
- `completed`
- `skipped`
- `failed`

### StepState

| Field | Type | Notes |
|---|---|---|
| `id` | string | Canonical step id |
| `title` | string | Display title |
| `status` | StepStatus | Current lifecycle status |
| `started_at` | string or null | UTC timestamp |
| `finished_at` | string or null | UTC timestamp |
| `duration_seconds` | number or null | Duration when step exits |
| `summary` | string or null | Human-readable outcome |
| `error` | string or null | Error message when failed |
| `metrics` | object | Step-specific metrics |

### LogEntry

| Field | Type | Notes |
|---|---|---|
| `timestamp` | string | UTC timestamp |
| `step_id` | string or null | Null for session-level logs |
| `level` | `info`, `warning`, `error` | Current implementation primarily emits info and error |
| `message` | string | Captured or generated log message |

### Artifact

| Field | Type | Notes |
|---|---|---|
| `name` | string | Filename |
| `kind` | `image`, `model`, `mesh`, `texture`, or `other` | UI display classification |
| `path` | string | Repository-relative path |
| `url` | string or null | API-served URL when available |
| `size_bytes` | integer or null | File size |

GLB and OBJ artifacts are previewable in the UI when `url` is populated. The previewer loads the same `/outputs/...` URLs exposed by this contract and does not require a separate API endpoint.

### WorkflowState

| Field | Type | Notes |
|---|---|---|
| `session_id` | string | Unique id |
| `config` | WorkflowConfig | Normalized config |
| `steps` | StepState array | Ordered step states |
| `logs` | LogEntry array | Bounded to latest 500 entries |
| `artifacts` | Artifact array | Current generated outputs |
| `busy` | boolean | Background work active flag |
| `active_step_id` | string or null | Currently running step |
| `created_at` | string | UTC timestamp |
| `updated_at` | string | UTC timestamp |

## Canonical Step IDs

| Step ID | Title |
|---|---|
| `load_pipeline` | Load Pipeline |
| `load_image` | Load Image |
| `preprocess_image` | Preprocess Image |
| `build_conditioning` | Build Conditioning |
| `sample_sparse_structure` | Sample Sparse Structure |
| `sample_shape_slat` | Sample Shape SLat |
| `sample_texture_slat` | Sample Texture SLat |
| `decode_mesh` | Decode Mesh |
| `export_model` | Export Model |

## Versioning Policy

- Additive response fields require a minor version bump.
- Removing or renaming fields requires a major version bump.
- Step ID changes require requirements and traceability updates.
- Parameter key changes require UI and API contract updates.

## API Verification Checklist

| Check | Command or method |
|---|---|
| Health endpoint | `GET /api/health` |
| Workflow definition | `GET /api/workflows/default` |
| Session creation | `POST /api/sessions` |
| Poll state | `GET /api/sessions/{session_id}` |
| Dependency enforcement | Attempt out-of-order step and expect 409 |
| Artifact serving | Verify `/outputs/...` after export |
