#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any


SKIP_DIRS = {
    "node_modules", ".next", ".turbo", ".generated", "dist", "build", "out",
    ".git", ".prisma_installer_backups"
}

EXTS = {".ts", ".tsx"}


@dataclass
class Patch:
    start: int
    end: int
    replacement: str


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="surrogatepass")).hexdigest()


def iter_source_files(pc_app: Path) -> List[Path]:
    roots = [pc_app / "app", pc_app / "src", pc_app / "components"]
    files: List[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in EXTS:
                continue
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            files.append(p)
    return sorted(files)


def find_matching(text: str, open_index: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    quote = ""
    escape = False
    line_comment = False
    block_comment = False
    i = open_index
    n = len(text)

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = ""
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


def top_level_objects(array_text: str) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    quote = ""
    escape = False
    line_comment = False
    block_comment = False
    depth = 0
    start = -1
    i = 0
    n = len(array_text)

    while i < n:
        ch = array_text[i]
        nxt = array_text[i + 1] if i + 1 < n else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue
        if block_comment:
            if ch == "*" and nxt == "/":
                block_comment = False
                i += 2
                continue
            i += 1
            continue
        if quote:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                quote = ""
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
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    out.append((start, i + 1))
                    start = -1
        i += 1

    return out


def should_patch_object(obj: str) -> bool:
    has_label = re.search(r"(?<![\w$])label\s*:", obj) is not None
    has_value = re.search(r"(?<![\w$])value\s*:", obj) is not None
    has_kind = re.search(r"(?<![\w$])kind\s*:", obj) is not None
    return has_label and has_value and not has_kind


def patch_object(obj: str) -> str:
    # Multiline object: insert using the indentation of the first property.
    m = re.match(r"\{\s*\n([ \t]+)", obj)
    if m:
        indent = m.group(1)
        return obj[:1] + "\n" + indent + 'kind: "source",' + obj[1:]

    # Single line object.
    m2 = re.match(r"\{\s*", obj)
    if m2:
        insert_at = m2.end()
        return obj[:insert_at] + 'kind: "source", ' + obj[insert_at:]

    return obj


def patch_text(text: str) -> Tuple[str, int]:
    evidence_re = re.compile(r"\bevidence\s*:\s*\[", re.M)
    replacements: List[Patch] = []
    object_count = 0

    for m in evidence_re.finditer(text):
        open_idx = text.find("[", m.start(), m.end())
        if open_idx < 0:
            continue
        close_idx = find_matching(text, open_idx, "[", "]")
        if close_idx < 0:
            continue
        array_text = text[open_idx + 1:close_idx]
        local_patches: List[Patch] = []

        for s, e in top_level_objects(array_text):
            obj = array_text[s:e]
            if should_patch_object(obj):
                local_patches.append(Patch(s, e, patch_object(obj)))
                object_count += 1

        if local_patches:
            new_array = array_text
            for p in sorted(local_patches, key=lambda x: x.start, reverse=True):
                new_array = new_array[:p.start] + p.replacement + new_array[p.end:]
            replacements.append(Patch(open_idx + 1, close_idx, new_array))

    if not replacements:
        return text, 0

    out = text
    for p in sorted(replacements, key=lambda x: x.start, reverse=True):
        out = out[:p.start] + p.replacement + out[p.end:]
    return out, object_count


def backup_file(path: Path, root: Path, backup_dir: Path, manifest_files: List[Dict[str, Any]], before_hash: str) -> Path:
    rel = path.relative_to(root)
    backup_path = backup_dir / "files" / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)
    manifest_files.append({
        "target": str(path),
        "backup": str(backup_path),
        "relative": str(rel).replace("\\", "/"),
        "before_sha256": before_hash,
    })
    return backup_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--backup-dir", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    repo = Path(args.root).resolve()
    pc_app = repo / "products" / "pc" / "app"
    backup_dir = Path(args.backup_dir).resolve()
    report_path = Path(args.report).resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if not pc_app.exists():
        raise SystemExit(f"PC app not found: {pc_app}")

    manifest_files: List[Dict[str, Any]] = []
    patched_files: List[Dict[str, Any]] = []
    scanned = 0
    total_objects = 0

    for path in iter_source_files(pc_app):
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig")

        before_hash = sha256_text(text)
        new_text, changed_objects = patch_text(text)
        if changed_objects <= 0 or new_text == text:
            continue

        backup_file(path, repo, backup_dir, manifest_files, before_hash)
        path.write_text(new_text, encoding="utf-8", newline="")
        after_hash = sha256_text(new_text)
        total_objects += changed_objects
        patched_files.append({
            "path": str(path),
            "relative": str(path.relative_to(repo)).replace("\\", "/"),
            "objectsPatched": changed_objects,
            "beforeSha256": before_hash,
            "afterSha256": after_hash,
        })
        print(f"PATCHED {path} objects={changed_objects}")

    manifest = {
        "schema": "PRISMA_PC_EVIDENCE_KIND_HOTFIX_04_FIXED_BACKUP_MANIFEST_V1",
        "root": str(repo),
        "files": manifest_files,
    }
    (backup_dir / "backup_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = {
        "schema": "PRISMA_PC_EVIDENCE_KIND_HOTFIX_04_FIXED_REPORT_V1",
        "root": str(repo),
        "pcApp": str(pc_app),
        "filesScanned": scanned,
        "filesPatched": len(patched_files),
        "objectsPatched": total_objects,
        "patchedFiles": patched_files,
        "note": "Adds kind: \"source\" to legacy evidence objects that had label/value but no kind.",
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({
        "status": "OK",
        "filesScanned": scanned,
        "filesPatched": len(patched_files),
        "objectsPatched": total_objects,
        "report": str(report_path),
        "backupManifest": str(backup_dir / "backup_manifest.json"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
