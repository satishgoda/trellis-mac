# 08. Traceability Matrix

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-RTM-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This matrix links requirements to design elements, implementation areas, verification activities, and validation scenarios. It provides change-impact analysis support and CMM/CMMI Level 3 aligned requirements management evidence.

## Quality Gate and Traceability Flow

![Quality gates and requirements traceability diagram](diagrams/07-quality-gate-and-traceability.svg)

## Traceability Matrix

| Requirement | Design reference | Implementation reference | Verification or validation |
|---|---|---|---|
| FR-001 | Step dependency design | `trellis_workflow/definitions.py` | Backend contract tests; VAL-001 |
| FR-002 | Parameter panel design | `web/src/components/ParameterPanel.tsx`, `trellis_workflow/definitions.py` | UI-AC-001, UI-AC-002 |
| FR-003 | Session state design | `trellis_workflow/workflow.py` | API smoke test; backend contract tests |
| FR-004 | Step dependency design | `WorkflowRunner._validate_dependencies` | Backend contract tests; VAL-002 |
| FR-005 | Execution model | `WorkflowRunner.start_next` | Manual validation; API contract test candidate |
| FR-006 | Execution model | `WorkflowRunner.start_all` | Manual validation; integration workflow test candidate |
| FR-007 | Session state design | `RuntimeContext` in `workflow.py` | Integration validation VAL-003, VAL-004 |
| FR-008 | Execution model | `LogCapture`, `_append_log` | Manual log review; API session state smoke |
| FR-009 | Session state design | `StepState`, `_execute_step` | Backend contract tests; VAL-003 |
| FR-010 | Artifact design | `trellis_workflow/exporter.py` | VAL-004 |
| FR-011 | Artifact design | `export_mesh_outputs`, `_export_textured_glb` | Full integration validation |
| FR-012 | Artifact panel design | `web/src/components/ArtifactPanel.tsx` | VAL-004; UI-AC-007 |
| FR-013 | Model preview design | `web/src/components/ModelPreview.tsx`, `web/src/lib/artifacts.ts` | Browser model preview smoke; UI-AC-010 |
| FR-014 | Command behavior | `App.resetSession` | UI manual validation |
| API-001 | API server design | `GET /api/health` | API smoke test |
| API-002 | API server design | `GET /api/workflows/default` | API smoke test |
| API-003 | API server design | `POST /api/sessions` | API smoke test; backend contract tests |
| API-004 | API server design | `GET /api/sessions/{session_id}` | Polling behavior; API smoke test candidate |
| API-005 | API server design | `GET /api/sessions` | API contract test candidate |
| API-006 | API server design | `POST /api/sessions/{session_id}/steps/{step_id}/run` | VAL-002; backend contract tests |
| API-007 | API server design | `POST /api/sessions/{session_id}/run-next` | VAL-003 |
| API-008 | API server design | `POST /api/sessions/{session_id}/run-all` | VAL-004 |
| API-009 | API server design | `DELETE /api/sessions/{session_id}` | API contract test candidate |
| API-010 | Artifact design | `app.mount('/outputs', StaticFiles(...))` | VAL-004 |
| UI-001 | UI state model | `App.useEffect` workflow definition load | Browser smoke test |
| UI-002 | Parameter panel design | `ParameterPanel` | Browser smoke test; UI-AC-001 |
| UI-003 | Command behavior | `App` command bar | Browser smoke test |
| UI-004 | Pipeline step list | `StepList` | Browser smoke test; UI-AC-005 |
| UI-005 | Step detail panel | `StepDetails` | Browser smoke test; VAL-003 |
| UI-006 | Log panel | `LogPanel` | VAL-001, VAL-003 |
| UI-007 | Artifact panel | `ArtifactPanel` | VAL-004 |
| UI-008 | Model preview panel | `ModelPreview`, `previewableModelArtifacts` | Browser model preview smoke; frontend unit tests |
| UI-009 | Polling behavior | `App.useEffect` polling timer | VAL-003 |
| UI-010 | Error handling | `App` error banner | VAL-002, VAL-005 |
| UI-011 | Responsive behavior | `web/src/styles.css` media queries | Browser viewport review |
| NFR-001 | Execution model | `ThreadPoolExecutor(max_workers=1)` | Code review |
| NFR-002 | Maintainability decisions | `generate.py` unchanged path | Regression check |
| NFR-003 | Typed contracts | Pydantic models, TypeScript interfaces | `pytest tests`, `npm run build` |
| NFR-004 | UI build verification | Vite/TypeScript config | `npm run build` |
| NFR-005 | Test strategy | Contract tests avoid TRELLIS load | `pytest tests` |
| NFR-006 | Error handling design | API HTTPException handling, `_execute_step` | VAL-002, VAL-005 |
| NFR-007 | Artifact design | `_session_output_dir` | VAL-004 |
| NFR-008 | Maintainability design | Module/package structure | Code review |
| OPS-001 | Startup procedure | `trellis-workflow-api` script | Runbook smoke |
| OPS-002 | Startup procedure | `npm run dev` | Runbook smoke |
| OPS-003 | Artifact locations | `outputs/<session-id>/` | VAL-004 |
| OPS-004 | Shutdown procedure | Terminal process stop | Runbook review |
| SEC-001 | CORS policy | FastAPI CORS middleware | Code review |
| SEC-002 | Secret handling | Documentation and code review | Security review |
| SEC-003 | Artifact serving scope | StaticFiles output mount | Code review |
| SEC-004 | Production risk control | Risk/security plan | Release approval |
| QA-001 | Backend verification | `pytest tests` | Verification command |
| QA-002 | Frontend verification | `npm run test` | Verification command |
| QA-003 | Build verification | `npm run build` | Verification command |
| QA-004 | API smoke verification | TestClient script | Verification command |
| QA-005 | Documentation traceability | This matrix | Documentation review |

## Change Impact Rules

| Change type | Required traceability action |
|---|---|
| New workflow step | Add requirement, update architecture, API contract, UI spec, traceability, tests |
| Removed workflow step | Update requirement baseline, step order, tests, validation scenarios |
| New parameter | Update requirements, API model, workflow definition, UI spec, tests |
| API response change | Update API contract, TypeScript types, traceability, tests |
| Artifact location change | Update operations, API contract, UI artifact behavior, tests |
| Authentication added | Update security requirements, API contract, operations, risk plan |

## Traceability Review Checklist

- Each baseline requirement has an implementation reference.
- Each baseline requirement has at least one verification or validation activity.
- Each API endpoint is tied to a requirement.
- Each UI panel is tied to a requirement.
- Known test gaps are explicitly marked as candidates or manual validation items.
