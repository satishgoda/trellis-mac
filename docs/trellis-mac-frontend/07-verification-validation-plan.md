# 07. Verification and Validation Plan

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-VVP-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This plan defines the verification and validation strategy for the TRELLIS Workflow UI and API server. It supports CMM/CMMI Level 3 aligned evidence by defining repeatable test activities, acceptance gates, and review records.

## Verification vs Validation

| Activity | Objective |
|---|---|
| Verification | Confirm the product was built according to requirements, design, and interface specifications |
| Validation | Confirm the product supports the intended user workflow for configuring and executing TRELLIS pipeline stages |

## Test Levels

| Level | Scope | Owner |
|---|---|---|
| Static review | Documentation, requirements, architecture, API contract | Technical lead and QA |
| Unit tests | Frontend helper functions and backend contract logic | Developers |
| Contract tests | API schema, session creation, dependency enforcement | Backend developer and QA |
| Build verification | TypeScript and Vite production build | Frontend developer |
| Smoke tests | API health, workflow definition, session creation, UI load | QA or release owner |
| Manual validation | Step-by-step workflow execution through the browser | Product owner and QA |
| Full integration | End-to-end TRELLIS generation and artifact export | ML/graphics engineer and QA |

## Verification Commands

### Backend Contract Tests

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
pytest tests
```

Expected result:

```text
3 passed
```

### Frontend Unit Tests

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac/web
npm run test
```

Expected result:

```text
Test Files  1 passed
Tests       3 passed
```

### Frontend Build Verification

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac/web
npm run build
```

Expected result:

```text
tsc && vite build
built
```

### API Smoke Test

```bash
cd /Users/sgoda/dev/GenAI/trellis-mac
source .venv/bin/activate
python - <<'PY'
from fastapi.testclient import TestClient
from trellis_workflow.app import app

client = TestClient(app)
assert client.get('/api/health').json()['status'] == 'ok'
definition = client.get('/api/workflows/default')
assert definition.status_code == 200
assert any(step['id'] == 'export_model' for step in definition.json()['steps'])
session = client.post('/api/sessions', json={'image_path': 'assets/shoe_input.png', 'output_name': ''})
assert session.status_code == 200, session.text
assert session.json()['config']['output_name'] == 'shoe_input'
print('api smoke ok')
PY
```

Expected result:

```text
api smoke ok
```

## Manual Validation Scenarios

### VAL-001: Load UI and Create Session

Preconditions:

- API server running.
- Vite server running.

Steps:

1. Open `http://127.0.0.1:5173`.
2. Confirm workflow definition renders.
3. Click Create Session.

Expected results:

- Session chip displays a session id.
- Run Next and Run Remaining become enabled.
- Logs panel shows session creation message.
- Load Pipeline is selected and pending.

### VAL-002: Enforce Step Order

Steps:

1. Create a new session.
2. Attempt to run Sample Sparse Structure before Load Pipeline.

Expected results:

- API rejects the request with 409.
- UI displays an error banner.
- No downstream state is marked complete.

### VAL-003: Run Next Through Initial Steps

Steps:

1. Create a new session.
2. Click Run Next for Load Pipeline.
3. Wait for completion.
4. Click Run Next for Load Image.

Expected results:

- Load Pipeline status transitions from pending to running to completed.
- Logs include pipeline load output.
- Load Image status transitions to completed.
- Step metrics include image dimensions.

### VAL-004: Full Workflow Artifact Generation

Steps:

1. Create a session with `assets/shoe_input.png`.
2. Run remaining steps.
3. Wait for Export Model to complete.

Expected results:

- Each step completes or the workflow stops on a documented failure.
- GLB and OBJ artifacts appear in Artifacts panel.
- Files exist under `outputs/<session-id>/`.
- Artifact URLs open through `/outputs/...`.

### VAL-005: Error Visibility

Steps:

1. Enter an invalid image path.
2. Create a session.
3. Run Load Pipeline if needed, then Load Image.

Expected results:

- Load Image step fails.
- Step detail displays error.
- Logs panel records the error.

## Acceptance Gates

| Gate | Required evidence |
|---|---|
| Requirements baseline | Requirements reviewed and traceability matrix populated |
| Design baseline | Architecture, API, and UI specs reviewed |
| Development complete | Source changes reviewed and tests added or updated |
| Verification complete | Backend tests, frontend tests, frontend build, API smoke pass |
| Validation complete | Manual UI session creation and at least one workflow execution scenario recorded |
| Release approval | Change record, risk review, and known limitations approved |

## Test Evidence Template

| Field | Value |
|---|---|
| Test run ID |  |
| Date |  |
| Build/revision |  |
| Tester |  |
| Environment |  |
| Commands run |  |
| Results |  |
| Failures |  |
| Artifacts attached |  |
| Approval |  |

## Defect Handling

Defects shall be recorded with:

- Unique defect ID.
- Environment.
- Steps to reproduce.
- Expected behavior.
- Actual behavior.
- Logs or screenshots.
- Severity.
- Owner.
- Fix version.
- Verification evidence.

## Regression Policy

Regression testing is required when any of the following changes occur:

- API endpoint path, request body, or response shape changes.
- Workflow step order or parameter metadata changes.
- Runtime execution logic changes.
- Artifact output path or serving behavior changes.
- Frontend command enablement rules change.
- Dependency versions change.

Minimum regression set:

- `pytest tests`
- `npm run test`
- `npm run build`
- API smoke test
- Browser create-session smoke test

## Quality Review Checklist

| Check | Required |
|---|---|
| Requirements are testable | Yes |
| Tests map to requirements | Yes |
| Manual validation scenarios cover user workflow | Yes |
| Build output is reproducible | Yes |
| Known limitations are documented | Yes |
| Defect process is documented | Yes |
