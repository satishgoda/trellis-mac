from __future__ import annotations

import contextlib
import io
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Callable
from uuid import uuid4

from PIL import Image as PILImage

from .definitions import PIPELINE_STEPS, build_initial_step_states, get_workflow_definition
from .exporter import _artifact_for, _session_output_dir, export_mesh_outputs
from .models import Artifact, LogEntry, StepState, StepStatus, WorkflowConfig, WorkflowDefinition, WorkflowState
from .runtime.bootstrap import configure_trellis_runtime

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
STEP_ORDER = [step.id for step in PIPELINE_STEPS]
SUCCESS_STATUSES = {StepStatus.completed, StepStatus.skipped}


@dataclass
class StepOutcome:
    status: StepStatus = StepStatus.completed
    summary: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)


@dataclass
class RuntimeContext:
    pipeline: Any = None
    raw_image: Any = None
    image: Any = None
    cond_512: dict[str, Any] | None = None
    cond_1024: dict[str, Any] | None = None
    coords: Any = None
    shape_slat: Any = None
    tex_slat: Any = None
    resolution: int | None = None
    mesh: Any = None
    rng_after_sparse: Any = None
    rng_after_shape: Any = None


@dataclass
class SessionRecord:
    state: WorkflowState
    context: RuntimeContext = field(default_factory=RuntimeContext)
    lock: RLock = field(default_factory=RLock)


class WorkflowError(RuntimeError):
    pass


class LogCapture(io.TextIOBase):
    def __init__(self, append: Callable[[str], None]) -> None:
        self.append = append

    def write(self, text: str) -> int:
        if not text:
            return 0
        normalized = text.replace("\r", "\n")
        for line in normalized.splitlines():
            cleaned = ANSI_RE.sub("", line).strip()
            if cleaned:
                self.append(cleaned)
        return len(text)

    def flush(self) -> None:
        return None


class WorkflowRunner:
    def __init__(self, project_root: Path, max_workers: int = 1) -> None:
        self.project_root = Path(project_root)
        self.definition = get_workflow_definition()
        self.records: dict[str, SessionRecord] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="trellis-workflow")
        self.lock = RLock()

    def get_definition(self) -> WorkflowDefinition:
        return self.definition

    def create_session(self, config: WorkflowConfig) -> WorkflowState:
        normalized = _normalize_config(config)
        session_id = uuid4().hex[:12]
        now = _now()
        state = WorkflowState(
            session_id=session_id,
            config=normalized,
            steps=build_initial_step_states(),
            created_at=now,
            updated_at=now,
        )
        record = SessionRecord(state=state)
        with self.lock:
            self.records[session_id] = record
        self._append_log(record, None, "info", "Created workflow session.")
        return record.state

    def get_state(self, session_id: str) -> WorkflowState:
        return self._record(session_id).state

    def delete_session(self, session_id: str) -> None:
        with self.lock:
            if session_id not in self.records:
                raise KeyError(session_id)
            del self.records[session_id]

    def start_step(self, session_id: str, step_id: str) -> WorkflowState:
        record = self._record(session_id)
        with record.lock:
            self._ensure_not_busy(record)
            self._validate_step_id(step_id)
            self._validate_dependencies(record, step_id)
            self._reset_downstream(record, step_id)
            record.state.busy = True
            record.state.active_step_id = step_id
            record.state.updated_at = _now()
        self.executor.submit(self._run_step_job, record, step_id)
        return record.state

    def start_next(self, session_id: str) -> WorkflowState:
        record = self._record(session_id)
        with record.lock:
            self._ensure_not_busy(record)
            next_step = self._next_step_id(record)
            if next_step is None:
                raise WorkflowError("All workflow steps are already complete.")
        return self.start_step(session_id, next_step)

    def start_all(self, session_id: str) -> WorkflowState:
        record = self._record(session_id)
        with record.lock:
            self._ensure_not_busy(record)
            if self._next_step_id(record) is None:
                raise WorkflowError("All workflow steps are already complete.")
            record.state.busy = True
            record.state.active_step_id = None
            record.state.updated_at = _now()
        self.executor.submit(self._run_all_job, record)
        return record.state

    def run_step_sync_for_tests(self, session_id: str, step_id: str) -> WorkflowState:
        record = self._record(session_id)
        with record.lock:
            self._validate_step_id(step_id)
            self._validate_dependencies(record, step_id)
        self._execute_step(record, step_id)
        return record.state

    def _run_step_job(self, record: SessionRecord, step_id: str) -> None:
        try:
            self._execute_step(record, step_id)
        finally:
            with record.lock:
                record.state.busy = False
                record.state.active_step_id = None
                record.state.updated_at = _now()

    def _run_all_job(self, record: SessionRecord) -> None:
        try:
            while True:
                with record.lock:
                    step_id = self._next_step_id(record)
                    if step_id is None:
                        break
                    record.state.active_step_id = step_id
                    record.state.updated_at = _now()
                self._execute_step(record, step_id)
                with record.lock:
                    state = self._step_state(record, step_id)
                    if state.status == StepStatus.failed:
                        break
        finally:
            with record.lock:
                record.state.busy = False
                record.state.active_step_id = None
                record.state.updated_at = _now()

    def _execute_step(self, record: SessionRecord, step_id: str) -> None:
        step_state = self._step_state(record, step_id)
        with record.lock:
            step_state.status = StepStatus.running
            step_state.started_at = _now()
            step_state.finished_at = None
            step_state.duration_seconds = None
            step_state.error = None
            step_state.summary = None
            step_state.metrics = {}
            record.state.active_step_id = step_id
            record.state.updated_at = _now()
        started = time.time()
        append_line = lambda message: self._append_log(record, step_id, "info", message)
        capture = LogCapture(append_line)
        try:
            with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
                outcome = STEP_HANDLERS[step_id](record, self.project_root, append_line)
            with record.lock:
                step_state.status = outcome.status
                step_state.summary = outcome.summary
                step_state.metrics = outcome.metrics
                step_state.finished_at = _now()
                step_state.duration_seconds = round(time.time() - started, 3)
                if outcome.artifacts:
                    existing = {artifact.path: artifact for artifact in record.state.artifacts}
                    for artifact in outcome.artifacts:
                        existing[artifact.path] = artifact
                    record.state.artifacts = list(existing.values())
                record.state.updated_at = _now()
        except Exception as exc:
            with record.lock:
                step_state.status = StepStatus.failed
                step_state.error = str(exc)
                step_state.finished_at = _now()
                step_state.duration_seconds = round(time.time() - started, 3)
                record.state.updated_at = _now()
            self._append_log(record, step_id, "error", str(exc))

    def _record(self, session_id: str) -> SessionRecord:
        with self.lock:
            try:
                return self.records[session_id]
            except KeyError:
                raise KeyError(session_id) from None

    def _append_log(self, record: SessionRecord, step_id: str | None, level: str, message: str) -> None:
        with record.lock:
            record.state.logs.append(
                LogEntry(timestamp=_now(), step_id=step_id, level=level, message=message)  # type: ignore[arg-type]
            )
            record.state.logs = record.state.logs[-500:]
            record.state.updated_at = _now()

    def _step_state(self, record: SessionRecord, step_id: str) -> StepState:
        for step in record.state.steps:
            if step.id == step_id:
                return step
        raise KeyError(step_id)

    def _next_step_id(self, record: SessionRecord) -> str | None:
        for step in record.state.steps:
            if step.status not in SUCCESS_STATUSES:
                return step.id
        return None

    def _ensure_not_busy(self, record: SessionRecord) -> None:
        if record.state.busy:
            raise WorkflowError("A workflow step is already running.")

    def _validate_step_id(self, step_id: str) -> None:
        if step_id not in STEP_ORDER:
            raise KeyError(step_id)

    def _validate_dependencies(self, record: SessionRecord, step_id: str) -> None:
        index = STEP_ORDER.index(step_id)
        incomplete = [record.state.steps[i].title for i in range(index) if record.state.steps[i].status not in SUCCESS_STATUSES]
        if incomplete:
            raise WorkflowError(f"Run earlier steps first: {', '.join(incomplete)}")

    def _reset_downstream(self, record: SessionRecord, step_id: str) -> None:
        index = STEP_ORDER.index(step_id)
        for downstream in record.state.steps[index + 1:]:
            downstream.status = StepStatus.pending
            downstream.started_at = None
            downstream.finished_at = None
            downstream.duration_seconds = None
            downstream.summary = None
            downstream.error = None
            downstream.metrics = {}
        if step_id != "export_model":
            record.state.artifacts = []


def _load_pipeline(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    configure_trellis_runtime(project_root)
    import torch
    from trellis2.pipelines.trellis2_image_to_3d import Trellis2ImageTo3DPipeline

    config = record.state.config
    device = torch.device(config.device)
    if config.device == "mps" and not torch.backends.mps.is_available():
        raise WorkflowError("MPS device was requested, but PyTorch MPS is not available.")

    started = time.time()
    pipeline = Trellis2ImageTo3DPipeline.from_pretrained(config.model_id)
    pipeline.to(device)
    record.context.pipeline = pipeline
    elapsed = round(time.time() - started, 1)
    log(f"Pipeline loaded on {config.device} in {elapsed}s.")
    return StepOutcome(summary=f"Loaded {config.model_id} on {config.device}.", metrics={"seconds": elapsed})


def _load_image(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    image_path = _resolve_input_path(project_root, record.state.config.image_path)
    if not image_path.exists():
        raise WorkflowError(f"Input image not found: {image_path}")
    image = PILImage.open(image_path)
    record.context.raw_image = image
    record.context.image = image
    log(f"Loaded image: {image_path} ({image.width}x{image.height}, mode={image.mode}).")
    return StepOutcome(summary=f"Loaded {image.width}x{image.height} image.", metrics={"width": image.width, "height": image.height, "mode": image.mode})


def _preprocess_image(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.raw_image, "Image is not loaded.")
    config = record.state.config
    if not config.preprocess_image:
        record.context.image = record.context.raw_image
        log("Image preprocessing is disabled; using the original image.")
        return StepOutcome(status=StepStatus.skipped, summary="Preprocessing disabled.")

    image = record.context.pipeline.preprocess_image(record.context.raw_image)
    record.context.image = image
    output_dir = _session_output_dir(project_root, config.output_dir, record.state.session_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_path = output_dir / "preprocessed.png"
    image.save(preview_path)
    artifact = _artifact_for(project_root, preview_path, "image")
    log(f"Preprocessed image saved: {preview_path.name} ({image.width}x{image.height}).")
    return StepOutcome(
        summary=f"Prepared {image.width}x{image.height} conditioning image.",
        metrics={"width": image.width, "height": image.height},
        artifacts=[artifact],
    )


def _build_conditioning(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.image, "Image is not loaded.")
    import torch

    pipeline_type = str(record.state.config.pipeline_type)
    with torch.no_grad():
        record.context.cond_512 = record.context.pipeline.get_cond([record.context.image], 512)
        if pipeline_type == "512":
            record.context.cond_1024 = None
        else:
            record.context.cond_1024 = record.context.pipeline.get_cond([record.context.image], 1024)
    log(f"Built conditioning tensors for pipeline {pipeline_type}.")
    resolutions = [512] if pipeline_type == "512" else [512, 1024]
    return StepOutcome(summary="Image conditioning is ready.", metrics={"conditioning_resolutions": resolutions})


def _sample_sparse_structure(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.cond_512, "Conditioning tensors are not ready.")
    import torch

    config = record.state.config
    pipeline_type = str(config.pipeline_type)
    sampler_params = _sampler_params(config)
    ss_res = {"512": 32, "1024": 64, "1024_cascade": 32}[pipeline_type]
    torch.manual_seed(config.seed)
    with torch.no_grad():
        coords = record.context.pipeline.sample_sparse_structure(record.context.cond_512, ss_res, config.num_samples, sampler_params)
    record.context.coords = coords
    record.context.rng_after_sparse = torch.get_rng_state()
    tokens = int(coords.shape[0])
    log(f"Sparse structure sampled with {tokens:,} active tokens at sparse resolution {ss_res}.")
    return StepOutcome(summary=f"Sampled {tokens:,} sparse tokens.", metrics={"tokens": tokens, "sparse_resolution": ss_res})


def _sample_shape_slat(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.coords, "Sparse structure is not sampled.")
    import torch

    config = record.state.config
    pipeline = record.context.pipeline
    pipeline_type = str(config.pipeline_type)
    sampler_params = _sampler_params(config)
    if record.context.rng_after_sparse is not None:
        torch.set_rng_state(record.context.rng_after_sparse)

    with torch.no_grad():
        if pipeline_type == "512":
            shape_slat = pipeline.sample_shape_slat(
                record.context.cond_512,
                pipeline.models["shape_slat_flow_model_512"],
                record.context.coords,
                sampler_params,
            )
            resolution = 512
        elif pipeline_type == "1024":
            shape_slat = pipeline.sample_shape_slat(
                record.context.cond_1024,
                pipeline.models["shape_slat_flow_model_1024"],
                record.context.coords,
                sampler_params,
            )
            resolution = 1024
        else:
            shape_slat, resolution = pipeline.sample_shape_slat_cascade(
                record.context.cond_512,
                record.context.cond_1024,
                pipeline.models["shape_slat_flow_model_512"],
                pipeline.models["shape_slat_flow_model_1024"],
                512,
                1024,
                record.context.coords,
                sampler_params,
                config.max_num_tokens,
            )
    record.context.shape_slat = shape_slat
    record.context.resolution = int(resolution)
    record.context.rng_after_shape = torch.get_rng_state()
    token_count = int(shape_slat.coords.shape[0])
    log(f"Shape SLat sampled with {token_count:,} tokens at decode resolution {resolution}.")
    return StepOutcome(summary=f"Shape latent ready at {resolution}.", metrics={"tokens": token_count, "resolution": resolution})


def _sample_texture_slat(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.shape_slat, "Shape SLat is not sampled.")
    import torch

    config = record.state.config
    pipeline = record.context.pipeline
    pipeline_type = str(config.pipeline_type)
    sampler_params = _sampler_params(config)
    if record.context.rng_after_shape is not None:
        torch.set_rng_state(record.context.rng_after_shape)

    with torch.no_grad():
        if pipeline_type == "512":
            tex_slat = pipeline.sample_tex_slat(
                record.context.cond_512,
                pipeline.models["tex_slat_flow_model_512"],
                record.context.shape_slat,
                sampler_params,
            )
        else:
            tex_slat = pipeline.sample_tex_slat(
                record.context.cond_1024,
                pipeline.models["tex_slat_flow_model_1024"],
                record.context.shape_slat,
                sampler_params,
            )
    record.context.tex_slat = tex_slat
    token_count = int(tex_slat.coords.shape[0])
    log(f"Texture SLat sampled with {token_count:,} tokens.")
    return StepOutcome(summary="Texture latent ready.", metrics={"tokens": token_count})


def _decode_mesh(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.pipeline, "Pipeline is not loaded.")
    _require(record.context.shape_slat, "Shape SLat is not sampled.")
    _require(record.context.tex_slat, "Texture SLat is not sampled.")
    _require(record.context.resolution, "Decode resolution is not set.")

    outputs = record.context.pipeline.decode_latent(record.context.shape_slat, record.context.tex_slat, record.context.resolution)
    mesh = outputs[0] if isinstance(outputs, list) else outputs
    verts = mesh.vertices.cpu().numpy()
    faces = mesh.faces.cpu().numpy()
    if verts.shape[0] == 0 or faces.shape[0] == 0:
        raise WorkflowError(_watchdog_help_message())
    record.context.mesh = mesh
    log(f"Decoded mesh: {verts.shape[0]:,} vertices, {faces.shape[0]:,} triangles.")
    return StepOutcome(
        summary=f"Decoded {verts.shape[0]:,} vertices and {faces.shape[0]:,} triangles.",
        metrics={"vertices": int(verts.shape[0]), "triangles": int(faces.shape[0])},
    )


def _export_model(record: SessionRecord, project_root: Path, log: Callable[[str], None]) -> StepOutcome:
    _require(record.context.mesh, "Mesh is not decoded.")
    result = export_mesh_outputs(record.context.mesh, record.state.config, project_root, record.state.session_id, log)
    return StepOutcome(summary="Model artifacts exported.", metrics=result.metrics, artifacts=result.artifacts)


STEP_HANDLERS: dict[str, Callable[[SessionRecord, Path, Callable[[str], None]], StepOutcome]] = {
    "load_pipeline": _load_pipeline,
    "load_image": _load_image,
    "preprocess_image": _preprocess_image,
    "build_conditioning": _build_conditioning,
    "sample_sparse_structure": _sample_sparse_structure,
    "sample_shape_slat": _sample_shape_slat,
    "sample_texture_slat": _sample_texture_slat,
    "decode_mesh": _decode_mesh,
    "export_model": _export_model,
}


def _normalize_config(config: WorkflowConfig) -> WorkflowConfig:
    data = config.model_dump()
    output_name = data.get("output_name")
    if not output_name or str(output_name).strip().lower() == "same name as the image":
        data["output_name"] = Path(str(data.get("image_path") or "output_3d")).stem
    if data.get("sampler_steps") in {"", 0}:
        data["sampler_steps"] = None
    data["output_dir"] = data.get("output_dir") or "outputs"
    return WorkflowConfig(**data)


def _resolve_input_path(project_root: Path, image_path: str) -> Path:
    path = Path(image_path).expanduser()
    if path.is_absolute():
        return path
    return project_root / path


def _sampler_params(config: WorkflowConfig) -> dict[str, int]:
    return {"steps": config.sampler_steps} if config.sampler_steps else {}


def _require(value: Any, message: str) -> None:
    if value is None:
        raise WorkflowError(message)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _watchdog_help_message() -> str:
    return (
        "The decoder produced an empty mesh. On Apple Silicon this is usually the macOS GPU watchdog "
        "interrupting a long-running Metal kernel. Try running headless, enabling MTL_CAPTURE_ENABLED=1, "
        "or switching SPARSE_CONV_BACKEND=none for a slower fallback."
    )
