# 09. Risk, Security, and Quality Plan

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-RSQ-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This plan identifies risks, security considerations, quality controls, and release gates for the TRELLIS Workflow UI and API server.

## Risk Rating Scale

| Rating | Meaning |
|---|---|
| Low | Unlikely or minor impact |
| Medium | Plausible with moderate impact |
| High | Likely or severe impact |
| Critical | Immediate mitigation required before release |

## Risk Register

| ID | Risk | Probability | Impact | Rating | Mitigation | Owner |
|---|---|---|---|---|---|---|
| RSK-001 | Model loading consumes significant memory and degrades system responsiveness. | Medium | High | High | Use single worker by default; document expected load time and memory; avoid concurrent heavy workflows. | Backend owner |
| RSK-002 | MPS or Metal watchdog interrupts long-running GPU operations. | Medium | High | High | Document headless mode, `MTL_CAPTURE_ENABLED=1`, and `SPARSE_CONV_BACKEND=none` fallback. | ML/graphics owner |
| RSK-003 | Session state is lost when API process restarts. | High | Medium | High | Document in-memory limitation; consider persistent job storage in future release. | Backend owner |
| RSK-004 | UI displays stale state during long-running steps. | Medium | Medium | Medium | Poll active sessions every 1.5 seconds; future improvement: server-sent events. | Frontend owner |
| RSK-005 | User runs steps out of order and corrupts runtime assumptions. | Medium | High | High | Backend enforces dependency order and resets downstream steps on rerun. | Backend owner |
| RSK-006 | Local API is exposed on an untrusted network. | Low | High | Medium | Bind to `127.0.0.1`; document development-only security posture. | Release owner |
| RSK-007 | Large generated artifacts consume disk space. | Medium | Medium | Medium | Store under ignored `outputs/`; document cleanup procedure. | User/operator |
| RSK-008 | API contract changes break UI behavior. | Medium | Medium | Medium | Maintain API contract, TypeScript interfaces, and traceability matrix. | Frontend and backend owners |
| RSK-009 | NPM development dependencies have audit findings. | Medium | Low | Medium | Verify production audit with `npm audit --omit=dev`; review dev findings before release. | Frontend owner |
| RSK-010 | External model license restrictions are overlooked. | Low | High | Medium | Reference upstream model license requirements; do not embed model weights in frontend docs. | Release owner |

## Security Baseline

| Area | Current control | Required for production |
|---|---|---|
| Network binding | API and UI run on local loopback | Keep loopback or deploy behind authenticated gateway |
| CORS | Localhost/Vite origins only | Environment-specific allowlist |
| Authentication | Not implemented | Required for shared or remote deployment |
| Authorization | Not implemented | Role-based access for sessions and artifacts |
| Secrets | No secrets committed or documented | Secret manager or environment variables |
| Artifacts | Served from output directory | Access control, retention policy, malware/content scanning if shared |
| Input image path | User-provided path resolved by server | Upload validation or path allowlist in shared deployments |
| Logs | Captured in session state | Redaction policy for sensitive paths/tokens |

## Security Requirements for Future Production Deployment

- Add authentication before exposing beyond localhost.
- Add authorization checks for session and artifact access.
- Replace path-based image input with controlled upload or a server-side allowlist.
- Add artifact retention and cleanup policy.
- Add structured logging with secret redaction.
- Add rate limiting and request size limits.
- Disable development reload in production.
- Configure CORS by environment.
- Run dependency vulnerability scans as a release gate.

## Quality Objectives

| Objective | Measurement |
|---|---|
| API correctness | Endpoint smoke tests pass |
| UI correctness | Frontend unit tests pass |
| Build integrity | TypeScript/Vite production build passes |
| Workflow correctness | Manual step-by-step validation passes |
| Maintainability | Requirements, design, API, UI, and traceability docs remain current |
| Operational reliability | Runbook startup, smoke, and shutdown procedures succeed |

## Quality Gates

| Gate | Exit criteria |
|---|---|
| Design review | Architecture, API, and UI specs approved |
| Code review | Implementation matches requirements and design |
| Unit/contract test | `pytest tests` and `npm run test` pass |
| Build verification | `npm run build` passes |
| Smoke verification | API health, workflow definition, and session creation pass |
| Manual validation | Create session and at least one step execution scenario pass |
| Risk review | High risks accepted or mitigated |
| Release approval | Change record and evidence are complete |

## Review Checklist

### Security Review

- API is not bound to a public interface for local development.
- CORS allowlist is limited to expected local origins.
- No credentials or tokens are committed.
- Artifact serving is scoped to output directory.
- Logs do not intentionally print secrets.
- Production limitations are documented.

### Quality Review

- New requirements include acceptance criteria.
- Tests or manual validation steps cover new behavior.
- UI behavior is documented when controls or state transitions change.
- API contract is updated for endpoint or model changes.
- Traceability matrix is updated.
- Runbook remains executable.

## Known Security Limitations

- No authentication.
- No authorization.
- No request rate limiting.
- No persistent audit log.
- No server-side path allowlist for image input.
- No cancellation or timeout control for long-running model steps.

These limitations are acceptable for local development only and must be remediated before shared deployment.

## Audit Evidence Expectations

For CMM/CMMI Level 3 aligned review, collect:

- Requirements baseline approval.
- Architecture and interface review notes.
- Test run logs.
- Build logs.
- API smoke output.
- Browser validation screenshots or notes.
- Risk acceptance records for known limitations.
- Change approval records.
