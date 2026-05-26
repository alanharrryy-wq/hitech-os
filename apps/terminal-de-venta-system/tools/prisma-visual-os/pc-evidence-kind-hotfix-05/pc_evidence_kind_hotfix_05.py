#!/usr/bin/env python3
# PRISMA PC Evidence Kind Hotfix 05
# Adds valid PcEvidenceRecord.kind values as literal const expressions.
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

VALID_KINDS = {"operational", "technical", "governance"}
DEFAULT_KIND = "operational"

def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def rel_to(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")

def backup_file(root: Path, path: Path, backup_dir: Path, manifest: Dict) -> None:
    rel = rel_to(root, path)
    dst = backup_dir / "files" / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(path, dst)
        manifest["files"].append({
            "target": str(path),
            "backup": str(dst),
            "relative": rel,
            "before_sha256": sha256_path(path),
        })

def strip_comments_and_strings_light(s: str) -> str:
    # Only for detection heuristics, not for rewriting.
    out = []
    i = 0
    n = len(s)
    state = None
    while i < n:
        c = s[i]
        if state is None:
            if c in ("'", '"', "`"):
                quote = c
                state = quote
                out.append(" ")
                i += 1
                continue
            if c == "/" and i + 1 < n and s[i+1] == "/":
                j = s.find("\n", i)
                if j == -1:
                    out.append(" " * (n - i))
                    break
                out.append(" " * (j - i))
                i = j
                continue
            if c == "/" and i + 1 < n and s[i+1] == "*":
                j = s.find("*/", i + 2)
                if j == -1:
                    out.append(" " * (n - i))
                    break
                out.append(" " * (j + 2 - i))
                i = j + 2
                continue
            out.append(c)
            i += 1
        else:
            if c == "\\":
                out.append(" ")
                if i + 1 < n:
                    out.append(" ")
                    i += 2
                else:
                    i += 1
                continue
            if c == state:
                state = None
            out.append(" ")
            i += 1
    return "".join(out)

def find_matching(text: str, start: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    i = start
    n = len(text)
    state = None
    line_comment = False
    block_comment = False
    while i < n:
        c = text[i]
        nxt = text[i+1] if i + 1 < n else ""
        if line_comment:
            if c == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if c == "*" and nxt == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue
        if state:
            if c == "\\":
                i += 2
                continue
            if c == state:
                state = None
            i += 1
            continue
        if c in ("'", '"', "`"):
            state = c
            i += 1
            continue
        if c == "/" and nxt == "/":
            line_comment = True
            i += 2
            continue
        if c == "/" and nxt == "*":
            block_comment = True
            i += 2
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def find_object_spans(array_text: str) -> List[Tuple[int, int]]:
    spans = []
    i = 0
    n = len(array_text)
    while i < n:
        if array_text[i] == "{":
            end = find_matching(array_text, i, "{", "}")
            if end == -1:
                i += 1
                continue
            spans.append((i, end + 1))
            i = end + 1
        else:
            i += 1
    return spans

def detect_kind_for_object(obj: str, file_path: Path) -> str:
    lower = (str(file_path).lower() + "\n" + obj.lower())
    if any(token in lower for token in ["license", "gobierno", "governance", "settings", "audit", "auditoria"]):
        return "governance"
    if any(token in lower for token in ["sync", "runtime", "system", "sistema", "device", "tablet-communication", "outbox"]):
        return "technical"
    return DEFAULT_KIND

def patch_object(obj: str, file_path: Path) -> Tuple[str, bool]:
    # Only patch legacy evidence records that look like { label, value }.
    if not re.search(r"\blabel\s*:", obj) or not re.search(r"\bvalue\s*:", obj):
        return obj, False

    kind_match = re.search(r"\bkind\s*:\s*(['\"])(.*?)\1(\s+as\s+const)?", obj)
    desired = detect_kind_for_object(obj, file_path)

    if kind_match:
        current = kind_match.group(2)
        # Normalize invalid kinds and force literal typing with as const.
        replacement = f'kind: "{desired}" as const'
        if current not in VALID_KINDS or "as const" not in kind_match.group(0):
            return obj[:kind_match.start()] + replacement + obj[kind_match.end():], True
        return obj, False

    # Insert after opening brace, preserving indentation.
    after_open = 1
    nl = obj.find("\n")
    if nl != -1:
        # Determine indentation of the first property.
        m = re.match(r"\n([ \t]*)", obj[after_open:])
        prop_indent = m.group(1) if m else "  "
        insertion = "\n" + prop_indent + f'kind: "{desired}" as const,'
        return obj[:after_open] + insertion + obj[after_open:], True
    return "{" + f' kind: "{desired}" as const, ' + obj[1:], True

def patch_evidence_arrays(text: str, path: Path) -> Tuple[str, int]:
    patches = 0
    search_pos = 0
    out_parts = []
    while True:
        m = re.search(r"\bevidence\s*:\s*\[", text[search_pos:])
        if not m:
            out_parts.append(text[search_pos:])
            break
        start = search_pos + m.start()
        bracket_start = search_pos + m.end() - 1
        bracket_end = find_matching(text, bracket_start, "[", "]")
        if bracket_end == -1:
            out_parts.append(text[search_pos:])
            break

        out_parts.append(text[search_pos:bracket_start + 1])
        array_body = text[bracket_start + 1: bracket_end]
        spans = find_object_spans(array_body)

        body_parts = []
        pos = 0
        for a, b in spans:
            body_parts.append(array_body[pos:a])
            obj = array_body[a:b]
            new_obj, changed = patch_object(obj, path)
            if changed:
                patches += 1
            body_parts.append(new_obj)
            pos = b
        body_parts.append(array_body[pos:])
        out_parts.append("".join(body_parts))
        search_pos = bracket_end
        # Preserve closing bracket as part of future text.
    return "".join(out_parts), patches

def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in {".ts", ".tsx"}:
        return False
    s = str(path).replace("\\", "/")
    skip = ["/node_modules/", "/.next/", "/.generated/", "/dist/", "/build/", "/out/"]
    return not any(x in s for x in skip)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--backup-dir", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    pc_app = root / "products" / "pc" / "app"
    backup_dir = Path(args.backup_dir).resolve()
    report_path = Path(args.report).resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema": "PRISMA_PC_EVIDENCE_KIND_HOTFIX_05_BACKUP_MANIFEST_V1",
        "root": str(root),
        "files": [],
    }

    files = []
    for base in [pc_app / "src" / "uiux", pc_app / "app", pc_app / "components", pc_app / "src"]:
        if base.exists():
            files.extend(p for p in base.rglob("*") if p.is_file() and should_scan(p))

    # Dedupe preserving order
    seen = set()
    unique_files = []
    for f in files:
        key = str(f.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique_files.append(f)

    patched = []
    files_scanned = 0
    objects_patched = 0

    for path in unique_files:
        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")
        if "evidence" not in text or "label" not in text or "value" not in text:
            continue
        new_text, count = patch_evidence_arrays(text, path)
        if count <= 0 or new_text == text:
            continue

        before = sha256_path(path)
        backup_file(root, path, backup_dir, manifest)
        path.write_text(new_text, encoding="utf-8", newline="")
        after = sha256_path(path)
        patched.append({
            "path": str(path),
            "relative": rel_to(root, path),
            "objectsPatched": count,
            "beforeSha256": before,
            "afterSha256": after,
        })
        objects_patched += count
        print(f"PATCHED {path} objects={count}")

    manifest_path = backup_dir / "backup_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "schema": "PRISMA_PC_EVIDENCE_KIND_HOTFIX_05_REPORT_V1",
        "root": str(root),
        "pcApp": str(pc_app),
        "filesScanned": files_scanned,
        "filesPatched": len(patched),
        "objectsPatched": objects_patched,
        "patchedFiles": patched,
        "note": 'Adds valid PcEvidenceRecord.kind values using string literal const expressions: "operational" | "technical" | "governance".',
        "backupManifest": str(manifest_path),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "status": "OK",
        "filesScanned": files_scanned,
        "filesPatched": len(patched),
        "objectsPatched": objects_patched,
        "report": str(report_path),
        "backupManifest": str(manifest_path),
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
