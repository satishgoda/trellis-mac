from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def configure_trellis_runtime(project_root: Path = PROJECT_ROOT) -> None:
    """Prepare env vars and import paths before torch/TRELLIS imports."""
    project_root = Path(project_root)
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    os.environ.setdefault("ATTN_BACKEND", "sdpa")
    os.environ.setdefault("SPARSE_ATTN_BACKEND", "sdpa")

    try:
        import flex_gemm  # noqa: F401
        os.environ.setdefault("SPARSE_CONV_BACKEND", "flex_gemm")
    except (ImportError, RuntimeError):
        os.environ.setdefault("SPARSE_CONV_BACKEND", "none")

    trellis_root = str(project_root / "TRELLIS.2")
    stubs_root = str(project_root / "stubs")
    if trellis_root not in sys.path:
        sys.path.insert(0, trellis_root)
    if stubs_root not in sys.path:
        sys.path.append(stubs_root)
