from __future__ import annotations
from ..paths import repo_path

def validate(repo, paths):
    rows = []
    for rel in paths:
        full = repo_path(repo, rel)
        if full.suffix.lower() == ".py" and full.exists():
            source = full.read_text(encoding="utf-8-sig", errors="replace")
            compile(source, str(full), "exec")
            rows.append({"path": rel, "ok": True})
    return rows
