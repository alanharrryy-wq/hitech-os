"""Code Atlas Legal / Investor Readiness backend.

The package provides a sequential, evidence-aware orchestrator. It does not add UI
widgets by itself; the next package wires this backend into PySide6.
"""

from .contracts import LegalPipelineConfig, LegalStageSpec, LegalStageResult
from .authority import validate_authority_chain
from .registry import build_legal_stage_registry
from .pipeline import run_pipeline

__all__ = [
    "LegalPipelineConfig",
    "LegalStageSpec",
    "LegalStageResult",
    "validate_authority_chain",
    "build_legal_stage_registry",
    "run_pipeline",
]

__version__ = "1.0.0"
