from pathlib import Path

import pytest

from trellis_workflow.artifacts import resolve_artifact_path
from trellis_workflow.exporter import _artifact_for
from trellis_workflow.models import WorkflowConfig
from trellis_workflow.workflow import WorkflowError, WorkflowRunner


def test_workflow_definition_parameters_reference_known_steps():
    runner = WorkflowRunner(Path.cwd())
    definition = runner.get_definition()
    step_ids = {step.id for step in definition.steps}

    assert "load_pipeline" in step_ids
    assert "export_model" in step_ids
    assert all(parameter.step_id in step_ids for parameter in definition.parameters)


def test_session_uses_image_stem_when_output_name_is_empty():
    runner = WorkflowRunner(Path.cwd())
    state = runner.create_session(WorkflowConfig(image_path="assets/shoe_input.png", output_name="same name as the image"))

    assert state.config.output_name == "shoe_input"
    assert state.steps[0].status == "pending"


def test_runner_blocks_out_of_order_steps_before_runtime_imports():
    runner = WorkflowRunner(Path.cwd())
    state = runner.create_session(WorkflowConfig())

    with pytest.raises(WorkflowError, match="Run earlier steps first"):
        runner.start_step(state.session_id, "sample_sparse_structure")


def test_artifact_url_is_created_for_non_outputs_directory(tmp_path: Path):
    artifact_path = tmp_path / "assets" / "dev" / "session-1" / "popeye.glb"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"glb")

    artifact = _artifact_for(tmp_path, artifact_path, "model")

    assert artifact.path == "assets/dev/session-1/popeye.glb"
    assert artifact.url == "/api/artifacts/assets/dev/session-1/popeye.glb"


def test_artifact_path_resolution_rejects_traversal(tmp_path: Path):
    with pytest.raises(ValueError, match="outside the project root"):
        resolve_artifact_path(tmp_path, "../secret.glb")
