from pathlib import Path

import pytest

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
