from __future__ import annotations

ENGINE_LIFECYCLE = [
    "discovered",
    "admitted",
    "loaded",
    "running",
    "succeeded",
    "failed",
    "rolled_back",
]

EXECUTION_POLICY = {
    "abort_on_admission_failure": True,
    "abort_on_ownership_violation": True,
    "continue_after_validation_errors": True,
    "require_deterministic_order": True,
}
