# 06. Operations Runbook

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-OPS-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This runbook defines the operational procedures for starting, verifying, using, stopping, and troubleshooting the TRELLIS Workflow UI and API server in a local development environment.

## Supported Environment

| Component | Requirement |
|---|---|
| OS | macOS on Apple Silicon for MPS workflow execution |
| Python | Repo virtual environment with TRELLIS dependencies installed |
| Node | Node.js and npm available on PATH |
| Backend port | `127.0.0.1:8000` |
| Frontend port | `127.0.0.1:5173` |
| Artifact root | Configured output directory, commonly `outputs/` or `assets/dev/` |

## Operations Flow

![Local operations and deployment flow diagram](diagrams/06-operations-deployment-flow.svg)

## Pre-Startup Checklist

- Confirm repository setup has completed successfully.
- Confirm `.venv` exists and can import core TRELLIS dependencies.
- Confirm Hugging Face authentication and gated model access are configured when required.
- Confirm Node dependencies are installed under `web/node_modules`.
- Confirm no existing process occupies ports 8000 or 5173.

## Install and Update Commands

### Python Backend

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
pip install -e ".[dev]"
```

### React Frontend

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac/web
npm install
```

## Startup Procedure

### Terminal 1: API Server

Preferred console script:

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
trellis-workflow-api
```

Alternative uvicorn command:

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
uvicorn trellis_workflow.app:app --host 127.0.0.1 --port 8000
```

Expected result:

```text
Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: React UI

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac/web
npm run dev
```

Expected result:

```text
Local: http://127.0.0.1:5173/
```

## Smoke Verification

### API Health

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{"status":"ok"}
```

### Workflow Definition

```bash
curl http://127.0.0.1:8000/api/workflows/default
```

Expected response includes:

- `steps`
- `parameters`
- Step id `load_pipeline`
- Step id `export_model`

### Browser Check

Open:

```text
http://127.0.0.1:5173
```

Expected page elements:

- `TRELLIS Workflow` heading.
- Create Session button.
- Parameter controls.
- Pipeline steps.
- Artifacts panel.
- Logs panel.

## Standard User Workflow

1. Open the UI.
2. Confirm or edit parameters.
3. Click Create Session.
4. Click Run Next for controlled execution, or Run Remaining to continue automatically.
5. Watch the step status and log panel.
6. Inspect artifacts after Export Model completes.
7. Open generated GLB or OBJ from the Artifacts panel.

## Artifact Locations

For relative output directories, generated files are written under:

```text
outputs/<session-id>/
```

Typical files:

- `<output-name>.glb`
- `<output-name>.obj`
- `preprocessed.png`
- `<output-name>_basecolor.png` when KDTree texture export writes a base color texture

## Shutdown Procedure

Stop both servers with `Ctrl+C` in their respective terminals.

Shutdown impact:

- UI process exits.
- API process exits.
- In-memory session state is lost.
- Files already written under `outputs/` remain on disk.

## Monitoring

| Signal | Location |
|---|---|
| API startup and request logs | API terminal |
| Vite dev server status | Frontend terminal |
| Pipeline stdout/stderr | UI Logs panel and API session state |
| Step status | UI Pipeline panel |
| Artifacts | UI Artifacts panel and `outputs/` directory |

## Troubleshooting

### API Does Not Start

Symptoms:

- Import error for FastAPI or Pydantic.
- Console script not found.

Actions:

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
pip install -e ".[dev]"
```

### UI Does Not Start

Symptoms:

- `package.json` not found.
- Vite command missing.

Actions:

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac/web
npm install
npm run dev
```

If a command is launched from the wrong directory, use:

```bash
npm --prefix /Users/sgoda/dev/GenAI/trellis-mac/web run dev -- --host 127.0.0.1
```

### UI Cannot Reach API

Symptoms:

- Workflow console remains in loading or error state.
- Browser shows API request failures.

Actions:

- Confirm API is running on port 8000.
- Confirm Vite proxy includes `/api` and `/outputs`.
- Confirm CORS origin is `http://127.0.0.1:5173` or `http://localhost:5173`.

### Step Fails Because Earlier Steps Are Missing

Symptoms:

- API returns 409 conflict.
- Detail says earlier steps must run first.

Actions:

- Use Run Next.
- Or manually execute steps in documented order.

### Pipeline Loading Is Slow

Cause:

- Model deserialization and first-use setup are expensive.

Actions:

- Wait for Load Pipeline to complete.
- Avoid restarting the API process between sessions when testing repeated runs.
- Keep only one heavy workflow active.

### MPS or Metal Runtime Failure

Symptoms:

- Empty mesh.
- Metal or watchdog-related runtime error.

Actions:

- Reduce machine display/GPU load.
- Run headless where feasible.
- Try environment variable `MTL_CAPTURE_ENABLED=1` before starting the API.
- Try `SPARSE_CONV_BACKEND=none` before starting the API for a slower fallback path.

### Artifacts Do Not Appear

Actions:

- Confirm Decode Mesh completed successfully.
- Confirm Export Model completed successfully.
- Check `outputs/<session-id>/` on disk.
- Confirm `/outputs/...` URL is present in artifact metadata.

## Backup and Cleanup

Generated artifacts may be copied or archived from `outputs/`. The directory is ignored by git and should be cleaned periodically.

Cleanup command:

```bash
rm -rf /Users/sgoda/dev/GenAI/trellis-mac/outputs/*
```

Use cleanup only after confirming no generated artifacts need to be retained.

## Release Readiness Operations Checklist

| Check | Required result |
|---|---|
| Backend tests | `pytest tests` passes |
| Frontend tests | `npm run test` passes |
| Frontend build | `npm run build` passes |
| API health | `/api/health` returns `ok` |
| UI smoke | Create Session succeeds from browser |
| Artifact smoke | Exported artifacts appear after a full workflow run |
