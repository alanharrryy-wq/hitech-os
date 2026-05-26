#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")

def is_identifier_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_" or ch == "$"

def find_matching_bracket(text: str, start: int, open_ch: str="[", close_ch: str="]") -> int:
    depth = 0
    i = start
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    while i < len(text):
        ch = text[i]
        nxt = text[i+1] if i+1 < len(text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def find_top_level_objects(array_text: str):
    # array_text includes [ ... ]
    objs = []
    depth = 0
    start = None
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    i = 0
    while i < len(array_text):
        ch = array_text[i]
        nxt = array_text[i+1] if i+1 < len(array_text) else ""
        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                objs.append((start, i+1))
                start = None
        i += 1
    return objs

def property_exists(obj: str, prop: str) -> bool:
    return re.search(r"(^|[,{]\s*)"+re.escape(prop)+r"\s*:", obj, flags=re.M) is not None

def patch_object(obj: str) -> tuple[str, bool]:
    if property_exists(obj, "kind"):
        return obj, False
    if not (property_exists(obj, "label") and property_exists(obj, "value")):
        return obj, False

    # Inline object
    if "\n" not in obj:
        return obj[:1] + ' kind: "source",' + obj[1:], True

    # Multiline: infer indent from next non-empty line
    lines = obj.splitlines(True)
    if len(lines) >= 2:
        m = re.match(r"(\s*)", lines[1])
        prop_indent = m.group(1) if m else "  "
    else:
        prop_indent = "  "
    insert = f'\n{prop_indent}kind: "source",'
    return obj[:1] + insert + obj[1:], True

def patch_evidence_arrays(text: str) -> tuple[str, int]:
    out = []
    last = 0
    patches = 0

    pattern = re.compile(r"\bevidence\s*:\s*\[")
    for m in pattern.finditer(text):
        start_bracket = text.find("[", m.start())
        if start_bracket < 0:
            continue
        end_bracket = find_matching_bracket(text, start_bracket, "[", "]")
        if end_bracket < 0:
            continue

        array_text = text[start_bracket:end_bracket+1]
        objs = find_top_level_objects(array_text[1:-1])
        if not objs:
            continue

        inner = array_text[1:-1]
        patched_inner_parts = []
        inner_last = 0
        local_patches = 0
        for s, e in objs:
            obj = inner[s:e]
            new_obj, changed = patch_object(obj)
            patched_inner_parts.append(inner[inner_last:s])
            patched_inner_parts.append(new_obj)
            inner_last = e
            if changed:
                local_patches += 1
        patched_inner_parts.append(inner[inner_last:])

        if local_patches:
            out.append(text[last:start_bracket+1])
            out.append("".join(patched_inner_parts))
            out.append("]")
            last = end_bracket + 1
            patches += local_patches

    if patches:
        out.append(text[last:])
        return "".join(out), patches
    return text, 0

def collect_targets(pc_app: Path) -> list[Path]:
    roots = [
        pc_app / "app",
        pc_app / "src",
        pc_app / "components",
    ]
    files = []
    for root in roots:
        if not root.exists():
            continue
        for ext in ("*.tsx", "*.ts"):
            files.extend(root.rglob(ext))
    # Avoid generated folders and node modules
    clean = []
    for p in files:
        parts = {part.lower() for part in p.parts}
        if "node_modules" in parts or ".next" in parts or ".generated" in parts:
            continue
        clean.append(p)
    return sorted(set(clean))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--workroot", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    workroot = Path(args.workroot)
    pc_app = root / "products" / "pc" / "app"
    reports = workroot / "reports"
    backups = workroot / "backups"
    reports.mkdir(parents=True, exist_ok=True)
    backups.mkdir(parents=True, exist_ok=True)

    if not pc_app.exists():
        raise SystemExit(f"PC app not found: {pc_app}")

    touched = []
    scanned = 0
    total_patches = 0

    for path in collect_targets(pc_app):
        txt = read_text(path)
        if "evidence" not in txt or "label" not in txt or "value" not in txt:
            continue
        scanned += 1
        new_txt, patches = patch_evidence_arrays(txt)
        if patches:
            rel = path.relative_to(root).as_posix()
            backup = backups / rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            write_text(path, new_txt)
            touched.append({
                "file": rel,
                "backup": str(backup),
                "patches": patches,
            })
            total_patches += patches

    manifest = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "root": str(root),
        "pcApp": str(pc_app),
        "scannedCandidateFiles": scanned,
        "patchedFiles": len(touched),
        "patchedEvidenceRecords": total_patches,
        "files": [{"target": str(root / item["file"]), "backup": item["backup"], "patches": item["patches"]} for item in touched],
    }

    (backups / "backup-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports / "pc-evidence-kind-hotfix-04-report.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PRISMA PC Evidence Kind Hotfix 04 Report",
        "",
        f"- Scanned candidate files: {scanned}",
        f"- Patched files: {len(touched)}",
        f"- Patched evidence records: {total_patches}",
        "",
        "## Patched files",
        "",
    ]
    if touched:
        for item in touched:
            md.append(f"- `{item['file']}`: {item['patches']} evidence records")
    else:
        md.append("- No changes needed. Evidence records already had kind or no matching legacy arrays were found.")
    (reports / "pc-evidence-kind-hotfix-04-report.md").write_text("\n".join(md)+"\n", encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "patchedFiles": len(touched),
        "patchedEvidenceRecords": total_patches,
        "report": str(reports / "pc-evidence-kind-hotfix-04-report.json"),
    }, indent=2))

if __name__ == "__main__":
    main()
