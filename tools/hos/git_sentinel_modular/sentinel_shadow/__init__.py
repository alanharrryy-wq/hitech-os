"""Public surface for sentinel_shadow."""

from .config import modular_root, runtime_root, shadow_root
from .diff_manifest import build_diff, snapshot_tree, write_diff_manifest
from .manifest import build_run_manifest, read_manifest, write_manifest
from .promotion_gate import assert_promotion_ready, evaluate_promotion_gate
from .runner import finalize_shadow_run, prepare_shadow_run, stage_candidate_overlay
from .workspace import ShadowWorkspace, bootstrap_from_modular_source, create_shadow_workspace

__all__ = ['modular_root', 'runtime_root', 'shadow_root', 'build_diff', 'snapshot_tree', 'write_diff_manifest', 'build_run_manifest', 'read_manifest', 'write_manifest', 'assert_promotion_ready', 'evaluate_promotion_gate', 'finalize_shadow_run', 'prepare_shadow_run', 'stage_candidate_overlay', 'ShadowWorkspace', 'bootstrap_from_modular_source', 'create_shadow_workspace']
