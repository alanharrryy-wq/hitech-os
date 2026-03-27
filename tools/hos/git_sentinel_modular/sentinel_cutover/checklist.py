from __future__ import annotations

def build_cutover_checklist() -> list[str]:
    return [
        "review bundle present",
        "diff manifest present",
        "rollback manifest present",
        "execution bundle can be planned",
    ]
