from __future__ import annotations
BANNED_SNIPPETS=["rm -rf","remove-item -recurse -force","del /","git clean","git push --delete","push origin --delete"]
def forbid_delete_command(cmd: list[str]) -> None:
    joined=" ".join(cmd).lower()
    if any(b in joined for b in BANNED_SNIPPETS):
        raise RuntimeError("Permanent delete command blocked: "+joined)
