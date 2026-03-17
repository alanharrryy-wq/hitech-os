from pathlib import Path

def normalize_relpath(pathlike) -> str:
    return str(Path(pathlike)).replace("\\", "/")

def assert_safe_relative_path(relpath: str, forbidden_parts=None, forbidden_suffixes=None):
    relpath = normalize_relpath(relpath)
    path = Path(relpath)

    forbidden_parts = forbidden_parts or set()
    forbidden_suffixes = forbidden_suffixes or set()

    if path.is_absolute():
        raise RuntimeError(f"Absolute paths are not allowed in shadow apply: {relpath}")

    for part in path.parts:
        if part in ("..", ""):
            raise RuntimeError(f"Unsafe relative path in shadow apply: {relpath}")
        if part in forbidden_parts:
            raise RuntimeError(f"Forbidden path part in shadow apply: {relpath}")

    if path.suffix.lower() in forbidden_suffixes:
        raise RuntimeError(f"Forbidden file suffix in shadow apply: {relpath}")

    return relpath

def assert_within_directory(base_dir, candidate_path):
    base_dir = Path(base_dir).resolve()
    candidate_path = Path(candidate_path).resolve()

    try:
        candidate_path.relative_to(base_dir)
    except ValueError as exc:
        raise RuntimeError(
            f"Target path escapes candidate workspace: {candidate_path}"
        ) from exc

    return candidate_path
