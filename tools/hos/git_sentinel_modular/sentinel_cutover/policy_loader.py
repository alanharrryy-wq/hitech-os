from pathlib import Path
import copy
import json

DEFAULT_POLICY = {
    "blocked_suffixes": [".tmp", ".bak", ".pyc", ".pyo"],
    "blocked_path_parts": ["_local", ".git", "__pycache__", ".pytest_cache", ".mypy_cache"],
    "critical_prefixes": [
        "legacy/",
        "shared/",
        "configs/",
        "tools/",
        "core/",
    ],
    "max_total_touched_for_easy_cutover": 5,
    "max_total_touched_before_attention": 15,
    "fail_on_removed_legacy": True,
    "require_python_parse_for_changed_py": True,
    "promotion_status_blockers": ["blocked"],
    "promotion_status_attention": ["needs_review"],
    "cutover_mode": "manual_only"
}

def default_policy():
    return copy.deepcopy(DEFAULT_POLICY)

def load_policy(path=None):
    policy = default_policy()

    if not path:
        return policy

    path = Path(path)
    if not path.exists():
        raise RuntimeError(f"Cutover policy not found: {path}")

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
