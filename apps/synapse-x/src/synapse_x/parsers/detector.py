from pathlib import Path


def detect_kind(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix in {".log", ".txt"}:
        return "log"
    if suffix in {".md", ".report"}:
        return "report"
    return "unknown"
