from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capatch_contracts.versions import BASELINE_SCHEMA_VERSION

from .renderers import read_json, render_baseline_md, sha256_file, write_json, write_text


@dataclass(slots=True)
class BaselineRecord:
    baseline_id: str
    label: str
    created_at: str
    root_dir: str
    git_branch: str | None
    git_head: str | None
    target_files: list[str]
    hashes: dict[str, str]
    verification_snapshot: list[dict[str, Any]]
    notes: str


def baseline_record_to_dict(record: BaselineRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload["schema_version"] = BASELINE_SCHEMA_VERSION
    return payload


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_baseline(root_dir: Path, *, label: str, target_files: list[str], verification_snapshot: list[dict[str, Any]] | None = None, notes: str = "", git_branch: str | None = None, git_head: str | None = None) -> BaselineRecord:
    root_dir = Path(root_dir).resolve()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    baseline_id = f"baseline_{stamp}"
    hashes = {
        relative_path: sha256_file(root_dir / relative_path) or ""
        for relative_path in target_files
    }
    record = BaselineRecord(
        baseline_id=baseline_id,
        label=label,
        created_at=_utc_now_iso(),
        root_dir=str(root_dir),
        git_branch=git_branch,
        git_head=git_head,
        target_files=list(target_files),
        hashes=hashes,
        verification_snapshot=list(verification_snapshot or []),
        notes=notes,
    )
    base_dir = root_dir / "reports/baselines"
    write_json(base_dir / f"{baseline_id}.json", baseline_record_to_dict(record))
    write_text(base_dir / f"{baseline_id}.md", render_baseline_md(record))
    index_path = base_dir / "index.json"
    index_payload = read_json(index_path, {"baselines": []})
    baselines = index_payload.setdefault("baselines", [])
    baselines.append({
        "baseline_id": baseline_id,
        "label": label,
        "created_at": record.created_at,
        "target_files": list(target_files),
    })
    write_json(index_path, index_payload)
    return record


def load_baseline(root_dir: Path, baseline_id: str) -> BaselineRecord | None:
    payload = read_json(Path(root_dir).resolve() / "reports/baselines" / f"{baseline_id}.json", None)
    if not isinstance(payload, dict):
        return None
    payload.pop("schema_version", None)
    return BaselineRecord(**payload)


def list_baselines(root_dir: Path) -> list[dict[str, Any]]:
    payload = read_json(Path(root_dir).resolve() / "reports/baselines/index.json", {"baselines": []})
    baselines = payload.get("baselines") if isinstance(payload, dict) else []
    return [item for item in baselines if isinstance(item, dict)]
