from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass

from .constants import DEBT_TOKENS, REPORTS_DIR_REL
from .hashing import deterministic_debt_id


@dataclass(frozen=True)
class DebtItem:
    debt_id: str
    repo: str
    source_file: str
    line_number: int
    text: str


def parse_repo_debt(repo_name: str, repo_root: pathlib.Path) -> list[DebtItem]:
    reports_dir = repo_root / REPORTS_DIR_REL
    if not reports_dir.is_dir():
        return []

    items: list[DebtItem] = []
    report_files = sorted(reports_dir.rglob("*.md"), key=lambda p: str(p).lower())
    for report in report_files:
        rel = str(report.relative_to(repo_root)).replace("\\", "/")
        for idx, line in enumerate(report.read_text(encoding="utf-8").splitlines(), start=1):
            if _is_debt_line(line):
                text = " ".join(line.strip().split())
                debt_id = deterministic_debt_id(repo_name, text)
                items.append(
                    DebtItem(
                        debt_id=debt_id,
                        repo=repo_name,
                        source_file=rel,
                        line_number=idx,
                        text=text,
                    )
                )

    dedup: dict[str, DebtItem] = {item.debt_id: item for item in items}
    return [dedup[key] for key in sorted(dedup)]


def _is_debt_line(line: str) -> bool:
    if not line.strip():
        return False
    upper = line.upper()
    for token in DEBT_TOKENS:
        if token in upper:
            return True
    # dedicated section heuristic with deterministic fallback.
    return bool(re.search(r"\bRISK\b|\bBACKLOG\b", upper))


def debt_totals(items: list) -> dict[str, int]:
    totals: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            repo = str(item.get("repo", ""))
        else:
            repo = str(getattr(item, "repo", ""))
        if not repo:
            continue
        totals[repo] = totals.get(repo, 0) + 1
    totals["global_total"] = len(items)
    return dict(sorted(totals.items(), key=lambda kv: kv[0]))
