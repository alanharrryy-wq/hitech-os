"""Public surface for sentinel_shadow_apply."""

from .dry_apply import apply_overlay_to_candidate
from .overlay_plan import build_overlay_plan
from .policies import ApplyPolicy, default_policy
from .review_pack import build_review_pack
from .safe_paths import assert_safe_relative_path, assert_within_directory, normalize_relpath

__all__ = [
    "apply_overlay_to_candidate",
    "build_overlay_plan",
    "ApplyPolicy",
    "default_policy",
    "build_review_pack",
    "assert_safe_relative_path",
    "assert_within_directory",
    "normalize_relpath",
]
