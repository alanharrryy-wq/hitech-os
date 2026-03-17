from pathlib import Path

from .policies import default_policy
from .dry_apply import apply_overlay_to_candidate
from .review_pack import build_review_pack

def run_shadow_apply_engine(workspace, overlay_source, finalize_callable, policy=None):
    policy = policy or default_policy()

    apply_result = apply_overlay_to_candidate(
        workspace=workspace,
        overlay_source=overlay_source,
        policy=policy,
    )

    finalize_result = finalize_callable(workspace)

    review_result = build_review_pack(
        workspace=workspace,
        apply_result=apply_result,
        finalize_result=finalize_result,
    )

    return {
        "apply_result": apply_result,
        "finalize_result": finalize_result,
        "review_result": review_result,
    }
