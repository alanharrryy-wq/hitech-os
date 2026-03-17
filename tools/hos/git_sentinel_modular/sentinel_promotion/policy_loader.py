from pathlib import Path
import copy
import json

DEFAULT_POLICY = {
    "blocked_path_parts": [
        "_local",
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
    ],
    "blocked_suffixes": [
        ".tmp",
        ".bak",
        ".pyc",
        ".pyo",
    ],
    "hard_block_removed_prefixes": [
        "legacy/",
    ],
    "manual_review_prefixes": [
        "legacy/",
        "shared/",
        "configs/",
        "tools/",
    ],
    "high_risk_prefixes": [
        "legacy/",
        "shared/provider.py",
        "shared/contracts.py",
        "shared/foundation.py",
    ],
    "review_thresholds": {
        "needs_review_total_touched": 5,
        "high_risk_total_touched": 15,
    },
    "reviewer_map": {
        "legacy/": ["platform", "architecture"],
        "shared/": ["platform"],
        "configs/": ["ops"],
        "tools/": ["repo-owner"],
        "default": ["repo-owner"],
    },
    "promotion_mode": "manual_only"
}

def default_policy():
    return copy.deepcopy(DEFAULT_POLICY)

def load_policy(path=None):
    policy = default_policy()

    if not path:
        return policy

    path = Path(path)
    if not path.exists():
        raise RuntimeError(f"Promotion policy not found: {path}")

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
