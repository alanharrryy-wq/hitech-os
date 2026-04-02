from typing import Any

from .capabilities import capability_matrix_delta, load_capability_contract
from .comparator import compare_semantic_baseline
from .specs import (
    BASELINE_ROOT,
    BASELINE_VERSION,
    GOLDEN_SESSIONS_PATH,
    SEMANTIC_BASELINE_PATH,
    VISUAL_BASELINE_PATH,
    load_golden_sessions,
    load_semantic_baseline,
    load_visual_baseline_manifest,
)


def run_ux_release_proof(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from .runner import run_ux_release_proof as _run

    return _run(*args, **kwargs)


__all__ = [
    "capability_matrix_delta",
    "load_capability_contract",
    "compare_semantic_baseline",
    "BASELINE_ROOT",
    "BASELINE_VERSION",
    "GOLDEN_SESSIONS_PATH",
    "SEMANTIC_BASELINE_PATH",
    "VISUAL_BASELINE_PATH",
    "load_golden_sessions",
    "load_semantic_baseline",
    "load_visual_baseline_manifest",
    "run_ux_release_proof",
]
