from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from .ag98_policy import safe_self_heal_extensions

_EOF_RE = re.compile(r"^(?P<path>.+?):(?P<line>\d+): new blank line at EOF\.", re.MULTILINE)

def _sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _strip_extra_blank_eof(path: Path) -> bool:
    data = path.read_bytes()
    if b"\x00" in data[:4096]:
        return False
    text = data.decode("utf-8", errors="replace")
    newline = "\r\n" if "\r\n" in text and text.count("\r\n") >= max(1, text.count("\n") // 2) else "\n"
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    new_text = "\n".join(lines) + "\n"
    if newline == "\r\n":
        new_text = new_text.replace("\n", "\r\n")
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8", errors="replace")
    return True

def autofix_staged_whitespace(repo: Path, runner, report: Path, group_paths: list[str] | None = None) -> dict:
    group_set = set((p or "").replace("\\", "/") for p in (group_paths or []))
    before = runner.run(["git", "diff", "--cached", "--check"], timeout=180, name="ag98_cached_diff_check_before")
    text = (before.stdout or "") + "\n" + (before.stderr or "")
    allowed_exts = safe_self_heal_extensions(repo)
    paths = []
    for m in _EOF_RE.finditer(text):
        rel = (m.group("path") or "").strip().replace("\\", "/")
        if group_set and rel not in group_set:
            continue
        if rel not in paths:
            paths.append(rel)

    root = report / "ag98_self_heal"
    backups = root / "backups_before_changes"
    current = root / "current_files_after_fix"
    backups.mkdir(parents=True, exist_ok=True)
    current.mkdir(parents=True, exist_ok=True)

    fixed = []
    skipped = []
    for rel in paths:
        p = repo / rel
        if not p.exists() or not p.is_file():
            skipped.append({"path": rel, "reason": "missing"})
            continue
        if p.suffix.lower() not in allowed_exts:
            skipped.append({"path": rel, "reason": "extension_not_allowlisted"})
            continue
        try:
            old_hash = _sha256(p)
            b = backups / rel
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, b)
            changed = _strip_extra_blank_eof(p)
            if changed:
                c = current / rel
                c.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, c)
                fixed.append({"path": rel, "sha256_before": old_hash, "sha256_after": _sha256(p), "backup": str(b)})
            else:
                skipped.append({"path": rel, "reason": "no_text_change"})
        except Exception as exc:
            skipped.append({"path": rel, "reason": repr(exc)})

    if fixed:
        runner.run(["git", "add", "--", *[x["path"] for x in fixed]], check=True, timeout=180, name="ag98_git_add_self_healed")

    after = runner.run(["git", "diff", "--cached", "--check"], timeout=180, name="ag98_cached_diff_check_after")
    summary = {
        "schema": "autogit.ag98_self_heal.v1",
        "before_returncode": before.returncode,
        "after_returncode": after.returncode,
        "fixed": fixed,
        "skipped": skipped,
        "ok": after.returncode == 0,
    }
    (root / "AG98_SELF_HEAL.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
