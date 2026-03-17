from pathlib import Path
import copy
import json

DEFAULT_POLICY = {
    "cutover_status_allowed_for_execution": ["ready", "needs_attention"],
    "blocked_path_parts": ["_local", ".git", "__pycache__", ".pytest_cache", ".mypy_cache"],
    "blocked_suffixes": [".tmp", ".bak", ".pyc", ".pyo"],
    "protected_prefixes": ["legacy/"],
    "allow_delete": False,
    "require_confirm_token": True,
    "confirm_token": "EXECUTE_MANUAL_PROMOTION",
    "backup_enabled": True,
    "verify_python_parse_after_apply": True,
    "post_smoke_required": True,
    "execution_mode": "manual_only",
    "backup_dir_name": "backups",
    "execution_dir_name": "execution_bundle"
}

def default_policy():
    return copy.deepcopy(DEFAULT_POLICY)

def load_policy(path=None):
    policy = default_policy()
    if not path:
        return policy

    path = Path(path)
    if not path.exists():
        raise RuntimeError(f"Execution policy not found: {path}")

    override = json.loads(path.read_text(encoding="utf-8"))
    return _deep_merge(policy, override)

def _deep_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        merged = dict(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = _deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return override
