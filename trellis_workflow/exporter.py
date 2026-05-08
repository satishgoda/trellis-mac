from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image as PILImage

from .models import Artifact, WorkflowConfig

LogFn = Callable[[str], None]


@dataclass
class ExportResult:
    artifacts: list[Artifact]
    metrics: dict[str, Any]


def export_mesh_outputs(
    mesh_out: Any,
    config: WorkflowConfig,
    project_root: Path,
    session_id: str,
    log: LogFn,
) -> ExportResult:
    output_dir = _session_output_dir(project_root, config.output_dir, session_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = _safe_output_name(config.output_name or Path(config.image_path).stem)
    output_prefix = output_dir / output_name

    verts = mesh_out.vertices.cpu().numpy()
    faces = mesh_out.faces.cpu().numpy()
    metrics: dict[str, Any] = {
        "vertices": int(verts.shape[0]),
        "triangles": int(faces.shape[0]),
        "output_dir": str(output_dir.relative_to(project_root)),
    }

    has_voxels = hasattr(mesh_out, "attrs") and mesh_out.attrs is not None
    skip_texture = config.no_texture or str(config.texture_backend) == "none"

    glb_path = output_prefix.with_suffix(".glb")
    if has_voxels and not skip_texture:
        backend_used = _export_textured_glb(mesh_out, verts, faces, glb_path, config, log)
        metrics["texture_backend"] = backend_used
    else:
        log("Exporting GLB with vertex colors only.")
        import trimesh

        trimesh.Trimesh(vertices=verts, faces=faces).export(glb_path)
        metrics["texture_backend"] = "none"

    obj_path = output_prefix.with_suffix(".obj")
    _export_obj(obj_path, verts, faces)
    log(f"Saved OBJ: {obj_path.name}")

    artifacts = [
        _artifact_for(project_root, glb_path, "model"),
        _artifact_for(project_root, obj_path, "mesh"),
    ]
    base_color_path = output_prefix.with_name(f"{output_prefix.name}_basecolor.png")
    if base_color_path.exists():
        artifacts.append(_artifact_for(project_root, base_color_path, "texture"))

    return ExportResult(artifacts=artifacts, metrics=metrics)


def _export_textured_glb(
    mesh_out: Any,
    verts: np.ndarray,
    faces: np.ndarray,
    glb_path: Path,
    config: WorkflowConfig,
    log: LogFn,
) -> str:
    requested_backend = str(config.texture_backend)
    if requested_backend in {"auto", "metal"} and _metal_baker_available():
        try:
            _export_glb_with_metal(mesh_out, glb_path, config, log)
            return "metal"
        except RuntimeError as exc:
            if requested_backend == "metal":
                raise
            log(f"Metal bake failed: {exc}")
            log("Falling back to KDTree texture baker.")
    elif requested_backend == "metal":
        raise RuntimeError("Metal texture backend was requested, but o_voxel.postprocess with mtldiffrast is unavailable.")

    _export_glb_with_kdtree(mesh_out, verts, faces, glb_path, config, log)
    return "kdtree"


def _metal_baker_available() -> bool:
    try:
        import o_voxel.postprocess

        backend = getattr(o_voxel.postprocess, "_BACKEND", None)
        has_dr = getattr(o_voxel.postprocess, "_HAS_DR", False)
        if backend == "metal" and has_dr:
            _patch_grid_sample_if_needed(o_voxel.postprocess)
            return True
    except (ImportError, AttributeError):
        return False
    return False


def _patch_grid_sample_if_needed(postprocess: Any) -> None:
    if getattr(postprocess, "_HAS_FLEX_GEMM", False):
        return

    import torch
    import torch.nn.functional as functional

    def grid_sample_3d_fix(feats, coords, shape, grid, mode="trilinear"):
        batch_size, channels = shape[0], shape[1]
        depth, height, width = shape[2], shape[3], shape[4]
        device = feats.device
        dense_vol = torch.zeros(batch_size, channels, depth, height, width, dtype=feats.dtype, device=device)
        batch_idx = coords[:, 0].long()
        cx = coords[:, 1].long()
        cy = coords[:, 2].long()
        cz = coords[:, 3].long()
        dense_vol[batch_idx, :, cx, cy, cz] = feats
        grid_norm = torch.stack(
            [
                grid[..., 2] / (width - 1) * 2 - 1,
                grid[..., 1] / (height - 1) * 2 - 1,
                grid[..., 0] / (depth - 1) * 2 - 1,
            ],
            dim=-1,
        ).reshape(batch_size, 1, 1, -1, 3)
        sampled = functional.grid_sample(
            dense_vol,
            grid_norm,
            mode="bilinear",
            align_corners=True,
            padding_mode="border",
        )
        samples = grid.shape[1]
        return sampled.reshape(batch_size, channels, samples).permute(0, 2, 1).reshape(batch_size * samples, channels)

    postprocess._grid_sample_3d = grid_sample_3d_fix


def _export_glb_with_metal(mesh_out: Any, glb_path: Path, config: WorkflowConfig, log: LogFn) -> None:
    import fast_simplification
    import o_voxel
    import torch

    verts_np = mesh_out.vertices.cpu().numpy()
    faces_np = mesh_out.faces.cpu().numpy()
    target_faces = min(max(1, config.decimation_target), len(faces_np))
    if len(faces_np) > target_faces:
        ratio = 1.0 - (target_faces / len(faces_np))
        log(f"Simplifying mesh: {len(faces_np):,} -> ~{target_faces:,} faces")
        simp_verts, simp_faces = fast_simplification.simplify(verts_np, faces_np, ratio)
        simp_verts_t = torch.from_numpy(simp_verts).float().to(mesh_out.vertices.device)
        simp_faces_t = torch.from_numpy(simp_faces.astype("int32")).to(mesh_out.faces.device)
    else:
        simp_verts_t = mesh_out.vertices
        simp_faces_t = mesh_out.faces

    log(f"Baking PBR textures via Metal ({config.texture_size}x{config.texture_size})")
    glb = o_voxel.postprocess.to_glb(
        vertices=simp_verts_t.cpu(),
        faces=simp_faces_t.cpu(),
        attr_volume=mesh_out.attrs.cpu(),
        coords=mesh_out.coords.cpu(),
        attr_layout=mesh_out.layout,
        voxel_size=mesh_out.voxel_size,
        aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
        decimation_target=target_faces,
        texture_size=config.texture_size,
        verbose=True,
    )
    glb.export(glb_path)
    log(f"Saved GLB: {glb_path.name}")


def _export_glb_with_kdtree(
    mesh_out: Any,
    verts: np.ndarray,
    faces: np.ndarray,
    glb_path: Path,
    config: WorkflowConfig,
    log: LogFn,
) -> None:
    from backends.texture_baker import bake_texture, export_glb_with_texture, uv_unwrap

    voxel_coords = mesh_out.coords.cpu().float()
    voxel_attrs = mesh_out.attrs.cpu().float()
    origin = mesh_out.origin.cpu().float() if hasattr(mesh_out.origin, "cpu") else mesh_out.origin
    voxel_size = mesh_out.voxel_size

    bake_verts, bake_faces = verts, faces
    target_faces = min(max(1, config.decimation_target), len(faces))
    if len(faces) > target_faces:
        try:
            import fast_simplification

            ratio = 1.0 - (target_faces / len(faces))
            log(f"Simplifying mesh: {len(faces):,} -> ~{target_faces:,} faces")
            bake_verts, bake_faces = fast_simplification.simplify(verts, faces, ratio)
        except ImportError:
            log("fast_simplification is not installed; UV unwrapping the full mesh.")

    log("UV unwrapping with xatlas.")
    new_verts, new_faces, uvs, _vmapping = uv_unwrap(bake_verts, bake_faces)
    log(f"UV unwrap: {len(verts):,} -> {len(new_verts):,} vertices")
    base_color_img, mr_img, _mask = bake_texture(
        new_verts,
        new_faces,
        uvs,
        voxel_coords.numpy(),
        voxel_attrs.numpy(),
        origin.numpy() if hasattr(origin, "numpy") else origin,
        voxel_size,
        texture_size=config.texture_size,
    )
    base_color_path = glb_path.with_name(f"{glb_path.stem}_basecolor.png")
    PILImage.fromarray(base_color_img).save(base_color_path)
    export_glb_with_texture(new_verts, new_faces, uvs, base_color_img, mr_img, str(glb_path))
    log(f"Saved GLB: {glb_path.name}")


def _export_obj(path: Path, verts: np.ndarray, faces: np.ndarray) -> None:
    with path.open("w") as obj_file:
        for vertex in verts:
            obj_file.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
        for face in faces:
            obj_file.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")


def _artifact_for(project_root: Path, path: Path, kind: str) -> Artifact:
    relative_path = path.relative_to(project_root)
    url = None
    try:
        output_relative = path.relative_to(project_root / "outputs")
        url = f"/outputs/{output_relative.as_posix()}"
    except ValueError:
        pass
    return Artifact(
        name=path.name,
        kind=kind,  # type: ignore[arg-type]
        path=relative_path.as_posix(),
        url=url,
        size_bytes=path.stat().st_size if path.exists() else None,
    )


def _session_output_dir(project_root: Path, output_dir: str, session_id: str) -> Path:
    base = Path(output_dir)
    if base.is_absolute():
        return base / session_id
    return project_root / base / session_id


def _safe_output_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in name.strip())
    return cleaned or "output_3d"
