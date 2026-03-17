from pathlib import Path

def normalize_relpath(relpath):
    return str(Path(relpath)).replace("\\", "/")

def assert_safe_relpath(relpath, policy):
    relpath = normalize_relpath(relpath)
    path = Path(relpath)

    if path.is_absolute():
        raise RuntimeError(f"Absolute path not allowed: {relpath}")

    for part in path.parts:
        if part in ("", ".."):
            raise RuntimeError(f"Unsafe relative path: {relpath}")
        if part in set(policy.get("blocked_path_parts", [])):
            raise RuntimeError(f"Blocked path part in relative path: {relpath}")

    if path.suffix.lower() in {x.lower() for x in policy.get("blocked_suffixes", [])}:
        raise RuntimeError(f"Blocked suffix in relative path: {relpath}")

    return relpath

def is_protected_path(relpath, policy):
    relpath = normalize_relpath(relpath)
    prefixes = [normalize_relpath(x) for x in policy.get("protected_prefixes", [])]
    for prefix in prefixes:
        if relpath == prefix or relpath.startswith(prefix):
            return True
    return False

def resolve_target_path(target_root, relpath):
    target_root = Path(target_root).resolve()
    target = (target_root / relpath).resolve()
    try:
        target.relative_to(target_root)
    except ValueError as exc:
        raise RuntimeError(f"Resolved path escapes target root: {target}") from exc
    return target
