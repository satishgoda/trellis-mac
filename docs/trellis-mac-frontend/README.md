# TRELLIS Workflow Frontend Documentation Set

## Document Control

| Field | Value |
|---|---|
| Document set ID | TMF-DOC-SET-001 |
| System | TRELLIS Workflow UI and API Server |
| Version | 0.1.0 |
| Status | Draft baseline for internal review |
| Prepared for | CMM/CMMI Level 3 aligned delivery evidence |
| Prepared on | 2026-05-07 |
| Primary code areas | `web/`, `trellis_workflow/` |

## Certification Position

This document set is CMM/CMMI Level 3 aligned. It is not an external certification claim. Formal CMM/CMMI certification requires an authorized appraisal, objective evidence review, organizational process audit, and appraisal records outside this repository.

## Purpose

The TRELLIS Workflow UI provides a browser-based console for configuring and executing TRELLIS image-to-3D generation as discrete, observable pipeline steps. The Python API server owns execution of the TRELLIS runtime, stateful workflow sessions, logs, and generated artifacts.

This documentation package defines requirements, architecture, interface contracts, operations, verification, risk controls, traceability, and change management for the app and server.

## Document Map

| Document | Purpose |
|---|---|
| [01-system-overview.md](01-system-overview.md) | Product scope, stakeholders, context, process alignment |
| [02-requirements-specification.md](02-requirements-specification.md) | Functional and non-functional requirements |
| [03-architecture-and-design.md](03-architecture-and-design.md) | App/server architecture and runtime design |
| [04-api-contract.md](04-api-contract.md) | FastAPI endpoint, model, and error contract |
| [05-ui-design-specification.md](05-ui-design-specification.md) | React UI behavior, layout, and control specification |
| [06-operations-runbook.md](06-operations-runbook.md) | Setup, startup, shutdown, monitoring, recovery |
| [07-verification-validation-plan.md](07-verification-validation-plan.md) | Test strategy, acceptance criteria, evidence capture |
| [08-traceability-matrix.md](08-traceability-matrix.md) | Requirements-to-design-to-test traceability |
| [09-risk-security-quality-plan.md](09-risk-security-quality-plan.md) | Risk, security, quality, and compliance controls |
| [10-configuration-change-management.md](10-configuration-change-management.md) | Baseline, versioning, change control, release records |

## Diagram Map

GraphViz DOT sources are maintained under [diagrams](diagrams) as reviewable architecture evidence. The diagram set includes system context, frontend component architecture, API session execution, workflow state transitions, data/artifact flow, operations, quality gates, and step dependencies.

| Diagram | Purpose |
|---|---|
| [diagrams/README.md](diagrams/README.md) | Diagram inventory and rendering instructions |
| [diagrams/01-system-context.dot](diagrams/01-system-context.dot) | System boundaries and external interactions |
| [diagrams/02-frontend-component-architecture.dot](diagrams/02-frontend-component-architecture.dot) | React component and API-client structure |
| [diagrams/03-api-session-flow.dot](diagrams/03-api-session-flow.dot) | API route behavior for sessions and step execution |
| [diagrams/04-workflow-step-state-machine.dot](diagrams/04-workflow-step-state-machine.dot) | Step status lifecycle and backend guards |
| [diagrams/05-data-artifact-flow.dot](diagrams/05-data-artifact-flow.dot) | Runtime data movement and generated artifacts |
| [diagrams/06-operations-deployment-flow.dot](diagrams/06-operations-deployment-flow.dot) | Setup, startup, smoke validation, and cleanup |
| [diagrams/07-quality-gate-and-traceability.dot](diagrams/07-quality-gate-and-traceability.dot) | Requirements, design, verification, and governance links |
| [diagrams/08-step-dependency-graph.dot](diagrams/08-step-dependency-graph.dot) | Ordered workflow step dependencies |

### Visual Diagram Catalog

| Diagram | Preview |
|---|---|
| System context | <img src="diagrams/01-system-context.svg" alt="TRELLIS Workflow system context diagram" width="480"> |
| Frontend component architecture | <img src="diagrams/02-frontend-component-architecture.svg" alt="React frontend component architecture diagram" width="480"> |
| API session flow | <img src="diagrams/03-api-session-flow.svg" alt="API session and step execution flow diagram" width="480"> |
| Workflow step state machine | <img src="diagrams/04-workflow-step-state-machine.svg" alt="Workflow step state machine diagram" width="480"> |
| Data and artifact flow | <img src="diagrams/05-data-artifact-flow.svg" alt="TRELLIS data and artifact flow diagram" width="480"> |
| Operations deployment flow | <img src="diagrams/06-operations-deployment-flow.svg" alt="Local operations and deployment flow diagram" width="480"> |
| Quality gate and traceability | <img src="diagrams/07-quality-gate-and-traceability.svg" alt="Quality gates and requirements traceability diagram" width="480"> |
| Workflow step dependencies | <img src="diagrams/08-step-dependency-graph.svg" alt="Workflow step dependency graph" width="480"> |

## CMM/CMMI Level 3 Alignment Summary

| Process Area | Evidence in this package |
|---|---|
| Requirements Development | Requirements specification and traceability matrix |
| Requirements Management | Change management process and requirement IDs |
| Technical Solution | Architecture, design, API, and UI specifications |
| Product Integration | App/server integration design and runbook |
| Verification | Verification and validation plan, test evidence expectations |
| Validation | User workflow acceptance scenarios and UI acceptance criteria |
| Configuration Management | Baseline, artifact control, dependency control, release records |
| Project Planning | Scope, assumptions, constraints, responsibilities |
| Project Monitoring and Control | Operational monitoring, status model, logs, acceptance gates |
| Risk Management | Risk register and mitigation controls |
| Process and Product Quality Assurance | Review checklist, quality gates, documentation baseline |

## Baseline Scope

Included:

- React/Vite workflow console under `web/`.
- FastAPI workflow API under `trellis_workflow/`.
- Session-based step orchestration for TRELLIS pipeline execution.
- Artifact serving from `outputs/` through the API server.
- Development and verification procedures.

Excluded:

- External CMM/CMMI appraisal records.
- Production identity provider integration.
- Multi-user authorization and persistence beyond in-memory sessions.
- Model weight governance beyond references to upstream model licenses.

## Maintenance Rules

- Requirements must retain stable IDs after baseline acceptance.
- API changes must update [04-api-contract.md](04-api-contract.md) and [08-traceability-matrix.md](08-traceability-matrix.md).
- UI behavior changes must update [05-ui-design-specification.md](05-ui-design-specification.md).
- Operational changes must update [06-operations-runbook.md](06-operations-runbook.md).
- Every release candidate must attach verification evidence from [07-verification-validation-plan.md](07-verification-validation-plan.md).
