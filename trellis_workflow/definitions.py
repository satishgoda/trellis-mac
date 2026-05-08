from __future__ import annotations

from .models import ParameterDefinition, StepDefinition, WorkflowDefinition

PIPELINE_STEPS: list[StepDefinition] = [
    StepDefinition(
        id="load_pipeline",
        title="Load Pipeline",
        description="Load TRELLIS.2 weights, initialize samplers, and move runtime components to the selected device.",
        parameter_keys=["model_id", "device"],
    ),
    StepDefinition(
        id="load_image",
        title="Load Image",
        description="Open the source image from disk and capture its dimensions.",
        parameter_keys=["image_path"],
    ),
    StepDefinition(
        id="preprocess_image",
        title="Preprocess Image",
        description="Resize, remove background when needed, and crop the image for conditioning.",
        parameter_keys=["preprocess_image"],
    ),
    StepDefinition(
        id="build_conditioning",
        title="Build Conditioning",
        description="Extract image-conditioning tensors for the selected pipeline resolution.",
        parameter_keys=["pipeline_type"],
    ),
    StepDefinition(
        id="sample_sparse_structure",
        title="Sample Sparse Structure",
        description="Sample the occupancy structure that defines where 3D tokens exist.",
        parameter_keys=["seed", "sampler_steps", "num_samples"],
    ),
    StepDefinition(
        id="sample_shape_slat",
        title="Sample Shape SLat",
        description="Sample the structured latent representation used by the shape decoder.",
        parameter_keys=["pipeline_type", "sampler_steps", "max_num_tokens"],
    ),
    StepDefinition(
        id="sample_texture_slat",
        title="Sample Texture SLat",
        description="Sample texture attributes conditioned on the generated shape latent.",
        parameter_keys=["sampler_steps"],
    ),
    StepDefinition(
        id="decode_mesh",
        title="Decode Mesh",
        description="Decode shape and texture latents into a mesh with voxel texture attributes.",
        parameter_keys=[],
    ),
    StepDefinition(
        id="export_model",
        title="Export Model",
        description="Bake textures when enabled, then export GLB and OBJ artifacts.",
        parameter_keys=["output_name", "output_dir", "texture_size", "texture_backend", "no_texture", "decimation_target"],
    ),
]

PARAMETERS: list[ParameterDefinition] = [
    ParameterDefinition(key="image_path", label="Input image", control="text", step_id="load_image", default="assets/shoe_input.png"),
    ParameterDefinition(key="output_name", label="Output name", control="text", step_id="export_model", default=""),
    ParameterDefinition(key="output_dir", label="Output directory", control="text", step_id="export_model", default="outputs"),
    ParameterDefinition(key="model_id", label="Model id", control="text", step_id="load_pipeline", default="microsoft/TRELLIS.2-4B"),
    ParameterDefinition(key="device", label="Device", control="select", step_id="load_pipeline", default="mps", options=["mps", "cpu"]),
    ParameterDefinition(key="seed", label="Seed", control="number", step_id="sample_sparse_structure", default=42, minimum=0),
    ParameterDefinition(key="pipeline_type", label="Pipeline", control="select", step_id="build_conditioning", default="512", options=["512", "1024", "1024_cascade"]),
    ParameterDefinition(key="texture_size", label="Texture size", control="select", step_id="export_model", default=1024, options=["512", "1024", "2048"]),
    ParameterDefinition(key="no_texture", label="Geometry only", control="checkbox", step_id="export_model", default=False),
    ParameterDefinition(key="sampler_steps", label="Sampler steps", control="number", step_id="sample_sparse_structure", default="", minimum=1),
    ParameterDefinition(key="num_samples", label="Samples", control="number", step_id="sample_sparse_structure", default=1, minimum=1, maximum=1),
    ParameterDefinition(key="max_num_tokens", label="Max tokens", control="number", step_id="sample_shape_slat", default=49152, minimum=1024),
    ParameterDefinition(key="preprocess_image", label="Preprocess image", control="checkbox", step_id="preprocess_image", default=True),
    ParameterDefinition(key="texture_backend", label="Texture backend", control="select", step_id="export_model", default="auto", options=["auto", "metal", "kdtree", "none"]),
    ParameterDefinition(key="decimation_target", label="Decimation target", control="number", step_id="export_model", default=200000, minimum=10000),
]


def get_workflow_definition() -> WorkflowDefinition:
    return WorkflowDefinition(steps=PIPELINE_STEPS, parameters=PARAMETERS)


def build_initial_step_states():
    from .models import StepState

    return [StepState(id=step.id, title=step.title) for step in PIPELINE_STEPS]
