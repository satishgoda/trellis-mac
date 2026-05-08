# GraphViz DOT Diagram Set

This folder contains GraphViz DOT source diagrams for the TRELLIS workflow frontend and API server documentation package. The diagrams are designed for CMM/CMMI Level 3 aligned delivery evidence: they use named system boundaries, explicit control flow, traceable responsibilities, and verification relationships.

## Files

| File | Purpose |
| --- | --- |
| `01-system-context.dot` | Shows the browser client, FastAPI server, TRELLIS runtime, and local storage boundaries. |
| `02-frontend-component-architecture.dot` | Shows React app shell, panels, API client, typed helpers, and backend integration. |
| `03-api-session-flow.dot` | Shows API route behavior from session creation through step execution and polling. |
| `04-workflow-step-state-machine.dot` | Shows valid step status transitions, backend guards, and observable outputs. |
| `05-data-artifact-flow.dot` | Shows image ingestion, conditioning, sampling, mesh decode, export, and UI artifact surfacing. |
| `06-operations-deployment-flow.dot` | Shows local setup, startup, validation, and runtime operations. |
| `07-quality-gate-and-traceability.dot` | Shows requirements mapped to design elements, verification evidence, and governance docs. |
| `08-step-dependency-graph.dot` | Shows ordered workflow step dependencies and data handoffs. |

## Preview Catalog

| Diagram | Preview |
| --- | --- |
| System context | <img src="01-system-context.svg" alt="TRELLIS Workflow system context diagram" width="520"> |
| Frontend component architecture | <img src="02-frontend-component-architecture.svg" alt="React frontend component architecture diagram" width="520"> |
| API session flow | <img src="03-api-session-flow.svg" alt="API session and step execution flow diagram" width="520"> |
| Workflow step state machine | <img src="04-workflow-step-state-machine.svg" alt="Workflow step state machine diagram" width="520"> |
| Data and artifact flow | <img src="05-data-artifact-flow.svg" alt="TRELLIS data and artifact flow diagram" width="520"> |
| Operations deployment flow | <img src="06-operations-deployment-flow.svg" alt="Local operations and deployment flow diagram" width="520"> |
| Quality gate and traceability | <img src="07-quality-gate-and-traceability.svg" alt="Quality gates and requirements traceability diagram" width="520"> |
| Workflow step dependencies | <img src="08-step-dependency-graph.svg" alt="Workflow step dependency graph" width="520"> |

## Rendering

Render an individual diagram with GraphViz:

```bash
dot -Tsvg docs/trellis-mac-frontend/diagrams/01-system-context.dot \
  -o docs/trellis-mac-frontend/diagrams/01-system-context.svg
```

Render every DOT file from the repository root:

```bash
for file in docs/trellis-mac-frontend/diagrams/*.dot; do
  dot -Tsvg "$file" -o "${file%.dot}.svg"
done
```

The source files use `rankdir`, clusters, subgraphs, color-coded domains, and polyline routing to keep edge flow readable and review friendly.
