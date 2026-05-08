from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PipelineType(str, Enum):
    size_512 = "512"
    size_1024 = "1024"
    cascade_1024 = "1024_cascade"


class TextureBackend(str, Enum):
    auto = "auto"
    metal = "metal"
    kdtree = "kdtree"
    none = "none"


class StepStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    skipped = "skipped"
    failed = "failed"


class ParameterDefinition(BaseModel):
    key: str
    label: str
    control: Literal["text", "number", "select", "checkbox"]
    step_id: str
    description: str = ""
    default: Any = None
    options: list[str] | None = None
    minimum: float | None = None
    maximum: float | None = None


class StepDefinition(BaseModel):
    id: str
    title: str
    description: str
    parameter_keys: list[str] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    steps: list[StepDefinition]
    parameters: list[ParameterDefinition]


class WorkflowConfig(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    image_path: str = "assets/shoe_input.png"
    output_name: str | None = None
    output_dir: str = "outputs"
    model_id: str = "microsoft/TRELLIS.2-4B"
    device: Literal["mps", "cpu"] = "mps"
    seed: int = 42
    pipeline_type: PipelineType = PipelineType.size_512
    texture_size: Literal[512, 1024, 2048] = 1024
    no_texture: bool = False
    sampler_steps: int | None = None
    num_samples: int = 1
    max_num_tokens: int = 49152
    preprocess_image: bool = True
    texture_backend: TextureBackend = TextureBackend.auto
    decimation_target: int = 200000


class StepState(BaseModel):
    id: str
    title: str
    status: StepStatus = StepStatus.pending
    started_at: str | None = None
    finished_at: str | None = None
    duration_seconds: float | None = None
    summary: str | None = None
    error: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class LogEntry(BaseModel):
    timestamp: str
    step_id: str | None = None
    level: Literal["info", "warning", "error"] = "info"
    message: str


class Artifact(BaseModel):
    name: str
    kind: Literal["image", "model", "mesh", "texture", "other"]
    path: str
    url: str | None = None
    size_bytes: int | None = None


class WorkflowState(BaseModel):
    session_id: str
    config: WorkflowConfig
    steps: list[StepState]
    logs: list[LogEntry] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    busy: bool = False
    active_step_id: str | None = None
    created_at: str
    updated_at: str
