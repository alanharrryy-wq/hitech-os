from pathlib import Path
import hashlib
import json

IGNORE_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def snapshot_tree(root: str | Path) -> dict:
    root = Path(root)
    snapshot = {}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        rel = path.relative_to(root)

        if any(part in IGNORE_NAMES for part in rel.parts):
            continue

        snapshot[str(rel).replace("\\", "/")] = {
            "sha256": _sha256(path),
            "size": path.stat().st_size,
        }

    return snapshot

def build_diff(baseline_root: str | Path, candidate_root: str | Path) -> dict:
    baseline = snapshot_tree(baseline_root)
    candidate = snapshot_tree(candidate_root)

    baseline_keys = set(baseline)
    candidate_keys = set(candidate)

    added = sorted(candidate_keys - baseline_keys)
    removed = sorted(baseline_keys - candidate_keys)

    changed = sorted(
        key for key in (baseline_keys & candidate_keys)
        if baseline[key] != candidate[key]
    )

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "total_touched": len(added) + len(removed) + len(changed),
        },
        "baseline_snapshot": baseline,
        "candidate_snapshot": candidate,
    }

def write_diff_manifest(path: str | Path, diff_payload: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(diff_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
