from __future__ import annotations

from pathlib import Path
from typing import Any

from capatch_fs.rollback import rollback_to_checkpoints


def rollback_strategy_plan(ctx: Any, strategy_decision: dict[str, Any] | None = None) -> dict[str, Any]:
    decision = dict(strategy_decision or {})
    selected = str(decision.get('selected_strategy') or 'guarded')
    advisory_only = bool(decision.get('advisory_only', False))
    root_dir = Path(getattr(ctx, 'root_dir')).expanduser().resolve()
    checkpoint_dir = Path(getattr(ctx, 'checkpoint_dir')).expanduser().resolve()
    return {
        'selected_strategy': selected,
        'advisory_only': advisory_only,
        'root_dir': str(root_dir),
        'checkpoint_dir': str(checkpoint_dir),
        'rollback_mode': 'preview-first' if advisory_only or selected in {'probe-only', 'structural'} else 'apply',
    }


def rollback_with_strategy(ctx: Any, strategy_decision: dict[str, Any] | None = None, *, dry_run: bool = False):
    plan = rollback_strategy_plan(ctx, strategy_decision)
    return rollback_to_checkpoints(
        Path(plan['root_dir']),
        checkpoint_root=Path(plan['checkpoint_dir']),
        dry_run=bool(dry_run or plan['rollback_mode'] == 'preview-first'),
    )


__all__ = ['rollback_strategy_plan', 'rollback_to_checkpoints', 'rollback_with_strategy']
