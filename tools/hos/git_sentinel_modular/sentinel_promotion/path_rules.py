from pathlib import Path

def normalize_relpath(relpath):
    return str(Path(relpath)).replace("\\", "/")

def _prefix_match(relpath, prefixes):
    relpath = normalize_relpath(relpath)
    hits = []
    for prefix in prefixes:
        prefix = normalize_relpath(prefix)
        if relpath == prefix or relpath.startswith(prefix):
            hits.append(prefix)
    return sorted(set(hits))

def classify_path(relpath, policy):
    relpath = normalize_relpath(relpath)
    path = Path(relpath)

    blocked_reasons = []

    for part in path.parts:
        if part in policy.get("blocked_path_parts", []):
            blocked_reasons.append(f"blocked_part:{part}")

    if path.suffix.lower() in {s.lower() for s in policy.get("blocked_suffixes", [])}:
        blocked_reasons.append(f"blocked_suffix:{path.suffix.lower()}")

    manual_review_hits = _prefix_match(relpath, policy.get("manual_review_prefixes", []))
    high_risk_hits = _prefix_match(relpath, policy.get("high_risk_prefixes", []))
    hard_block_remove_hits = _prefix_match(relpath, policy.get("hard_block_removed_prefixes", []))

    return {
        "path": relpath,
        "blocked_reasons": blocked_reasons,
        "manual_review_hits": manual_review_hits,
        "high_risk_hits": high_risk_hits,
        "hard_block_remove_hits": hard_block_remove_hits,
        "is_blocked": len(blocked_reasons) > 0,
        "needs_manual_review": len(manual_review_hits) > 0,
        "is_high_risk": len(high_risk_hits) > 0,
    }

def classify_many(paths, policy):
    return [classify_path(path, policy) for path in sorted(set(paths))]
