# 10. Configuration and Change Management

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-CCM-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This document defines configuration management, baseline control, change control, release readiness, and documentation maintenance practices for the TRELLIS Workflow UI and API server.

## Configuration Items

| Configuration item | Path | Control level |
|---|---|---|
| React app source | `web/src/` | Version controlled |
| Frontend package manifest | `web/package.json` | Version controlled |
| Frontend lockfile | `web/package-lock.json` | Version controlled |
| Frontend build config | `web/vite.config.ts`, `web/tsconfig.json` | Version controlled |
| Backend API package | `trellis_workflow/` | Version controlled |
| Backend package metadata | `pyproject.toml` | Version controlled |
| Setup script | `setup.sh` | Version controlled |
| Backend tests | `tests/` | Version controlled |
| Documentation set | `docs/trellis-mac-frontend/` | Version controlled |
| Generated artifacts | `outputs/` | Ignored by git |
| Python virtual environment | `.venv/` | Ignored by git |
| Frontend dependencies | `web/node_modules/` | Ignored by git |
| Frontend build output | `web/dist/` | Ignored by git |

## Baseline Definition

A baseline is a reviewed and approved set of:

- Requirements.
- Architecture/design documentation.
- API contract.
- UI specification.
- Source code.
- Dependency manifests and lockfiles.
- Verification evidence.
- Known risk acceptance records.

## Current Baseline

| Field | Value |
|---|---|
| Baseline name | TRELLIS Workflow UI/API initial documentation baseline |
| Version | 0.1.0 |
| Status | Draft pending owner approval |
| Included code | `web/`, `trellis_workflow/`, tests, package metadata |
| Included docs | `docs/trellis-mac-frontend/` |

## Change Classification

| Class | Description | Approval required |
|---|---|---|
| Class A | API model, endpoint, workflow step order, artifact path, or security posture change | Technical lead and QA |
| Class B | UI behavior, parameter controls, logs, artifacts, test coverage, or runbook change | Component owner and QA |
| Class C | Documentation-only clarification with no behavior change | Document owner |
| Emergency | Blocking defect or unsafe operation fix | Technical lead, with retrospective review |

## Change Request Template

| Field | Value |
|---|---|
| Change ID |  |
| Title |  |
| Requester |  |
| Date |  |
| Class |  |
| Description |  |
| Reason |  |
| Affected requirements |  |
| Affected files |  |
| Risk impact |  |
| Test impact |  |
| Documentation impact |  |
| Approval |  |
| Implementation commit |  |
| Verification evidence |  |

## Required Change Analysis

For every non-trivial change, assess:

- Does a requirement need to be added, removed, or modified?
- Does the API contract change?
- Does the UI behavior change?
- Does the workflow order or runtime state model change?
- Does artifact generation or serving change?
- Does the runbook change?
- Are new tests required?
- Does traceability need to be updated?
- Does the security/risk posture change?

## Versioning Policy

| Change | Version impact |
|---|---|
| Documentation clarification only | Patch version |
| Additive UI/API behavior | Minor version |
| Breaking API/model/step behavior | Major version |
| Security control addition | Minor or major depending on compatibility |
| Dependency update without behavior change | Patch version |

## Branching and Review Policy

Recommended process:

1. Create a focused change branch.
2. Update source, tests, and documentation together.
3. Run required verification commands.
4. Attach evidence to the change request.
5. Complete code and documentation review.
6. Merge only after approval.

## Required Verification by Change Type

| Change type | Required verification |
|---|---|
| Backend API change | `pytest tests`, API smoke test, contract doc update |
| Workflow runtime change | `pytest tests`, manual step execution, traceability update |
| Frontend UI change | `npm run test`, `npm run build`, browser smoke |
| Dependency change | Relevant tests, build, vulnerability review |
| Documentation change | Link/path review, document control review |
| Export/artifact change | Full workflow export validation |

## Release Readiness Checklist

| Item | Complete |
|---|---|
| Requirements updated and approved |  |
| Architecture/design updated |  |
| API contract updated |  |
| UI specification updated |  |
| Traceability matrix updated |  |
| Risk/security review completed |  |
| Backend tests passed |  |
| Frontend tests passed |  |
| Frontend build passed |  |
| API smoke test passed |  |
| Browser smoke test passed |  |
| Known limitations documented |  |
| Release notes prepared |  |
| Approval recorded |  |

## Release Notes Template

```markdown
# Release Notes: TRELLIS Workflow UI/API <version>

## Summary

## Added

## Changed

## Fixed

## Removed

## Verification Evidence

- Backend tests:
- Frontend tests:
- Frontend build:
- API smoke:
- Manual validation:

## Known Limitations

## Approval
```

## Documentation Maintenance

- Update document control metadata when documents materially change.
- Keep file names stable after baseline approval.
- Update traceability matrix for every requirements-affecting change.
- Preserve historical release notes outside generated runtime folders.
- Do not store generated model artifacts in documentation directories.

## Configuration Audit Checklist

| Check | Expected result |
|---|---|
| Ignored generated files | `.venv/`, `outputs/`, `web/node_modules/`, `web/dist/`, caches ignored |
| Lockfile present | `web/package-lock.json` present after npm install |
| Python package metadata current | `pyproject.toml` includes API dependencies and scripts |
| Frontend scripts current | `web/package.json` includes dev, build, preview, test |
| Documentation current | This folder reflects current app/server behavior |
| Test evidence current | Latest test/build commands recorded for release candidate |
