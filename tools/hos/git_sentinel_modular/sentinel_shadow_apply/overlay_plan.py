from pathlib import Path
from .safe_paths import assert_safe_relative_path

def build_overlay_plan(overlay_source, policy):
    overlay_source = Path(overlay_source)

    if not overlay_source.exists():
        raise RuntimeError(f"Overlay source does not exist: {overlay_source}")

    if not overlay_source.is_dir():
        raise RuntimeError(f"Overlay source must be a directory: {overlay_source}")

    actions = []
    skipped = []

    for path in sorted(overlay_source.rglob("*")):
        if path.is_dir():
            continue

        rel = path.relative_to(overlay_source)
        rel_posix = str(rel).replace("\\", "/")

        if path.name in policy.excluded_file_names:
            skipped.append({
                "path": rel_posix,
                "reason": "excluded_file_name",
            })
            continue

        if any(part in policy.forbidden_parts for part in rel.parts):
            skipped.append({
                "path": rel_posix,
                "reason": "forbidden_path_part",
            })
            continue

        if path.suffix.lower() in policy.forbidden_suffixes:
            skipped.append({
                "path": rel_posix,
                "reason": "forbidden_suffix",
            })
            continue

        rel_checked = assert_safe_relative_path(
            rel_posix,
            forbidden_parts=policy.forbidden_parts,
            forbidden_suffixes=policy.forbidden_suffixes,
        )

        actions.append({
            "source": str(path),
            "relative_path": rel_checked,
        })

    return {
        "overlay_source": str(overlay_source),
        "actions": actions,
        "skipped": skipped,
        "counts": {
            "actions": len(actions),
            "skipped": len(skipped),
        },
    }
