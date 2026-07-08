"""Backward-compatible module entrypoint for Code Atlas Operational Evidence.

The implementation remains in ``code_atlas.operational.cli``.  This shim keeps
``code_atlas.operational.main`` imports and module execution stable.
"""

from __future__ import annotations

from typing import Any, Sequence

from .cli import main as _cli_main
from .cli import run_operational_atlas


def run_operational_evidence(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for older imports."""
    return run_operational_atlas(*args, **kwargs)


def run_operational_evidence_atlas(*args: Any, **kwargs: Any) -> Any:
    """Legacy alias for previous operational atlas callers."""
    return run_operational_atlas(*args, **kwargs)


def run(*args: Any, **kwargs: Any) -> Any:
    """Legacy shorthand alias."""
    return run_operational_atlas(*args, **kwargs)


def main(argv: Sequence[str] | None = None) -> Any:
    """Delegate to the modular operational CLI without assuming its signature."""
    if argv is None:
        return _cli_main()
    try:
        return _cli_main(argv)
    except TypeError:
        # Some internal CLI builds read sys.argv directly.
        return _cli_main()


__all__ = [
    "main",
    "run_operational_atlas",
    "run_operational_evidence",
    "run_operational_evidence_atlas",
    "run",
]


if __name__ == "__main__":
    raise SystemExit(main())

# DBEVLINK_LICSCOPE_BRIDGE_AUTOPATCH_START
def _dbevlink_bridge_wrap(fn):
    def _wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        try:
            from pathlib import Path as _Path
            from code_atlas.operational.licscope_bridge import apply_bridge_to_output_dir as _apply_bridge
            _repo = kwargs.get('repo_root') or kwargs.get('repo') or kwargs.get('root')
            _out = kwargs.get('output_dir') or kwargs.get('out_dir') or kwargs.get('output_root') or kwargs.get('output')
            if isinstance(result, dict):
                _repo = _repo or result.get('repo') or result.get('repo_root')
                _out = _out or result.get('output_dir') or result.get('out_dir') or result.get('output')
                _html = result.get('html_path') or result.get('viewer_html')
                if not _out and _html:
                    _out = str(_Path(_html).parent)
            if _repo and _out:
                _apply_bridge(_Path(_repo), _Path(_out))
        except Exception as _exc:
            try:
                if isinstance(result, dict): result.setdefault('licscopeBridgeWarning', str(_exc))
            except Exception:
                pass
        return result
    return _wrapped
for _dbevlink_name in ('run', 'run_operational_atlas', 'generate', 'generate_operational_atlas', 'build_operational_atlas'):
    try:
        if _dbevlink_name in globals() and callable(globals()[_dbevlink_name]) and not getattr(globals()[_dbevlink_name], '_dbevlink_wrapped', False):
            _dbevlink_fn = _dbevlink_bridge_wrap(globals()[_dbevlink_name])
            _dbevlink_fn._dbevlink_wrapped = True
            globals()[_dbevlink_name] = _dbevlink_fn
    except Exception:
        pass
# DBEVLINK_LICSCOPE_BRIDGE_AUTOPATCH_END
