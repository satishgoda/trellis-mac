from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

ARTIFACT_EXTENSIONS = {".glb", ".obj", ".png", ".jpg", ".jpeg", ".webp"}


def artifact_url_for(project_root: Path, path: Path) -> str | None:
    try:
        relative_path = path.resolve().relative_to(project_root.resolve())
    except ValueError:
        return None

    if path.suffix.lower() not in ARTIFACT_EXTENSIONS:
        return None

    return f"/api/artifacts/{quote(relative_path.as_posix(), safe='/')}"


def resolve_artifact_path(project_root: Path, artifact_path: str) -> Path:
    requested = Path(artifact_path)
    if requested.is_absolute():
        raise ValueError("Artifact path must be relative.")

    resolved_root = project_root.resolve()
    resolved_path = (resolved_root / requested).resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError("Artifact path is outside the project root.")
    if resolved_path.suffix.lower() not in ARTIFACT_EXTENSIONS:
        raise ValueError("Artifact file type is not supported.")
    if not resolved_path.is_file():
        raise FileNotFoundError(artifact_path)
    return resolved_path