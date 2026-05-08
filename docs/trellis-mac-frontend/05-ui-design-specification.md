# 05. UI Design Specification

## Document Control

| Field | Value |
|---|---|
| Document ID | TMF-UI-001 |
| Version | 0.1.0 |
| Status | Draft baseline |
| Prepared on | 2026-05-07 |

## Purpose

This document defines the React user interface behavior for the TRELLIS Workflow console. It establishes the layout, controls, state transitions, accessibility expectations, and validation behavior needed to maintain a professional local workflow application.

## UI Technology Baseline

| Area | Decision |
|---|---|
| Framework | React 18 |
| Build tool | Vite |
| Language | TypeScript strict mode |
| Icons | `lucide-react` |
| 3D preview | Three.js with GLTFLoader, OBJLoader, and OrbitControls |
| Tests | Vitest with jsdom |
| Styling | Project CSS in `web/src/styles.css` |
| API integration | Fetch wrapper in `web/src/api/client.ts` |

## Page Inventory

The current UI is a single-page workflow console.

| Page/View | Route | Purpose |
|---|---|---|
| Workflow Console | `/` | Configure parameters, create session, run steps, preview model artifacts, inspect logs and artifacts |

## Primary Layout

The app shell has four main regions:

1. Top bar
   - Product name.
   - Brief purpose statement.
   - Session chip showing current session id or no session state.

2. Command bar
   - Create Session.
   - Run Next.
   - Run Remaining.
   - Reset View.

3. Workspace grid
   - Left: Parameter panel.
   - Middle: Pipeline step list and selected step detail.
   - Right: Model preview panel, artifact panel, and log panel.

4. Responsive behavior
   - Desktop: three columns.
   - Medium widths: right column moves below primary columns.
   - Small widths: all panels stack vertically.

## UI State Model

![Workflow step state machine diagram](diagrams/04-workflow-step-state-machine.svg)

| State | Source | UI behavior |
|---|---|---|
| `definition` | `GET /api/workflows/default` | Drives parameter and step rendering |
| `config` | Local React state | Edited before session creation |
| `session` | API `WorkflowState` | Drives step state, logs, artifacts, busy status |
| `selectedStepId` | Local React state plus active step updates | Drives selected step details |
| `error` | API/client error handling | Displays error banner |
| `loading` | Initial API load | Displays boot screen |

## Command Behavior

### Create Session

- Enabled when no workflow step is busy.
- Prepares config by trimming text fields and normalizing empty optional values.
- Calls `POST /api/sessions`.
- On success, stores returned session state and selects the first step.
- On failure, displays an error banner.

### Run Next

- Enabled when a session exists, the session is not busy, and at least one step is incomplete.
- Calls `POST /api/sessions/{session_id}/run-next`.
- On success, stores returned session state.
- On failure, displays an error banner.

### Run Remaining

- Enabled under the same conditions as Run Next.
- Calls `POST /api/sessions/{session_id}/run-all`.
- On success, stores returned session state.
- On failure, displays an error banner.

### Reset View

- Enabled when a session is not busy.
- Clears local session and error state.
- Does not delete server-side session state.

## Polling Behavior

When `session.busy` is true:

- UI polls `GET /api/sessions/{session_id}` every 1.5 seconds.
- Polling stops when the component unmounts or `busy` becomes false.
- Polling errors display an error banner.
- If `active_step_id` is present, the UI selects that step automatically.

## Parameter Panel

The parameter panel is generated from backend metadata. Parameters are grouped by `step_id` and displayed under the corresponding step title.

| Control type | UI element |
|---|---|
| `text` | Text input |
| `number` | Number input |
| `select` | Select dropdown |
| `checkbox` | Checkbox |

### Parameter Rules

- Parameter fields are disabled while a session step is busy.
- Numeric empty values are converted to `null` in local state.
- Select controls convert numeric keys to numbers where needed.
- Empty `output_name` is intentionally allowed and normalized by the server.

## Pipeline Step List

Each step row contains:

- Select Step button.
- Status icon.
- Step title and sequence number.
- Status label.
- Duration when available.
- Run Step icon button.

### Step Status Rendering

| Status | Visual tone |
|---|---|
| `pending` | Neutral gray |
| `running` | Blue with spinner |
| `completed` | Green with check |
| `skipped` | Amber with skip icon |
| `failed` | Red with error icon |

## Step Detail Panel

When a step is selected, the detail panel shows:

- Step title.
- Status pill.
- Step description.
- Started time.
- Duration.
- Summary.
- Error block when failed.
- Metrics grid when metrics exist.

If no step state is available, the panel shows an empty state.

## Model Preview Panel

The model preview panel shows generated model artifacts that can be rendered in the browser.

Supported preview inputs:

- GLB artifacts with `artifact.url`.
- OBJ artifacts with `artifact.url`.

Behavior:

- The panel selects the first previewable model artifact automatically.
- A native select control switches between available GLB and OBJ artifacts.
- A direct open link remains available for the selected artifact.
- Three.js renders the selected artifact with orbit controls, lighting, grid reference, auto-rotation, and automatic camera framing.
- OBJ files receive a neutral material fallback when no material is available.
- If no previewable artifacts exist, the panel displays an empty state.

## Artifact Panel

The artifact panel shows generated files returned by the API.

For each artifact:

- Icon based on kind.
- Filename.
- Repository-relative path.
- File size.
- Download/open icon.
- Link to `artifact.url` when available.

If no artifacts exist, the panel shows an empty state.

## Log Panel

The log panel shows session and step logs.

For each log line:

- Localized timestamp.
- Step id or `session`.
- Message.
- Error messages use red text.

Logs are displayed in a monospace dark panel to preserve readability for technical pipeline output.

## Error Handling

| Error | User-facing behavior |
|---|---|
| Workflow definition load fails | Error banner after boot screen clears |
| Create session fails | Error banner |
| Run command fails | Error banner |
| Polling fails | Error banner |
| Step execution fails | Step detail error block from session state |

## Accessibility Requirements

- Controls must use native button, input, select, and checkbox elements.
- Major sections must include meaningful `aria-label` values.
- Icon-only run buttons must include descriptive `title` attributes.
- Text must not overflow fixed UI elements; long paths and metrics must wrap or truncate gracefully.
- Interactive controls must not be nested inside other interactive controls.
- Status is represented by both color and text.

## Visual Design Requirements

- Use a restrained professional interface appropriate for an operational ML workflow tool.
- Avoid decorative-only imagery or marketing layout patterns.
- Keep panel radius at 8px or less.
- Use dense but readable controls.
- Keep color palette balanced and not dominated by one hue family.
- Preserve stable panel dimensions during state updates.

## UI Acceptance Criteria

| ID | Acceptance test |
|---|---|
| UI-AC-001 | Initial load renders title, command bar, parameter panel, pipeline panel, artifacts panel, and log panel. |
| UI-AC-002 | Create Session sends config to the API and displays returned session id. |
| UI-AC-003 | Run Next becomes enabled only after a session exists and no step is busy. |
| UI-AC-004 | While busy, parameter controls are disabled and polling updates logs/status. |
| UI-AC-005 | Step selection updates the details panel. |
| UI-AC-006 | API errors are visible in the error banner. |
| UI-AC-007 | Generated artifacts appear with file size and link after export. |
| UI-AC-008 | The app builds successfully with `npm run build`. |
| UI-AC-009 | Unit tests pass with `npm run test`. |
| UI-AC-010 | Served GLB and OBJ artifacts can be selected and rendered in the model preview panel. |

## UI Maintenance Checklist

- Update TypeScript interfaces when backend models change.
- Update parameter handling if a new control type is introduced.
- Update responsive CSS after adding new panels.
- Update model preview loaders and artifact helper tests when supported preview formats change.
- Keep command button enablement rules aligned with backend conflict rules.
- Validate browser snapshot after major layout changes.
