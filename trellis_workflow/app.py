from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models import WorkflowConfig, WorkflowState
from .workflow import WorkflowError, WorkflowRunner

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

runner = WorkflowRunner(PROJECT_ROOT)

app = FastAPI(title="TRELLIS Workflow API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/workflows/default")
def workflow_definition():
    return runner.get_definition()


@app.post("/api/sessions", response_model=WorkflowState)
def create_session(config: WorkflowConfig) -> WorkflowState:
    return runner.create_session(config)


@app.get("/api/sessions", response_model=list[WorkflowState])
def list_sessions() -> list[WorkflowState]:
    return [record.state for record in runner.records.values()]


@app.get("/api/sessions/{session_id}", response_model=WorkflowState)
def get_session(session_id: str) -> WorkflowState:
    try:
        return runner.get_state(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow session not found.") from exc


@app.post("/api/sessions/{session_id}/steps/{step_id}/run", response_model=WorkflowState)
def run_step(session_id: str, step_id: str) -> WorkflowState:
    try:
        return runner.start_step(session_id, step_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow session or step not found.") from exc
    except WorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/sessions/{session_id}/run-next", response_model=WorkflowState)
def run_next(session_id: str) -> WorkflowState:
    try:
        return runner.start_next(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow session not found.") from exc
    except WorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/sessions/{session_id}/run-all", response_model=WorkflowState)
def run_all(session_id: str) -> WorkflowState:
    try:
        return runner.start_all(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow session not found.") from exc
    except WorkflowError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.delete("/api/sessions/{session_id}", status_code=204)
def delete_session(session_id: str) -> None:
    try:
        runner.delete_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow session not found.") from exc


def main() -> None:
    import uvicorn

    uvicorn.run("trellis_workflow.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
