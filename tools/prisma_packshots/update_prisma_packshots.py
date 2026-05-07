#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
PRISMA packshot registry updater.

Repo placement recommended:
  F:\repos\hitech-os\tools\prisma_packshots\update_prisma_packshots.py

Purpose:
  - Scan PRISMA generic packshot PNG source folders.
  - Match already-classified images by SHA256 / size / filename hints.
  - Copy known images into F:\light packshots and F:\dark packshots.
  - Generate a pending-review CSV for truly new PNGs.
  - Apply a completed review CSV back into the registry.
  - Never guess product names silently. Humanity already invented enough chaos.

No external dependency is required for core usage. Pillow is optional only for
contact-sheet generation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

TOOL_VERSION = "1.0.0"
PROJECT_NAME = "PRISMA Tablet POS generic packshots"

DEFAULT_REPO_ROOT = Path(r"F:\repos\hitech-os")
DEFAULT_TOOL_RELATIVE_DIR = Path("tools") / "prisma_packshots"
DEFAULT_DATA_RELATIVE_DIR = DEFAULT_TOOL_RELATIVE_DIR / "data"
DEFAULT_DOWNLOADS_ROOT = Path(r"F:\descargasf")
DEFAULT_LIGHT_TARGET = Path(r"F:\light packshots")
DEFAULT_DARK_TARGET = Path(r"F:\dark packshots")
DEFAULT_REVIEW_TARGET = Path(r"F:\packshots review")
DEFAULT_SOURCE_ROOTS = [Path(fr"F:\Imagenes packshot {i}") for i in range(1, 11)]
DEFAULT_EXTERNAL_MANIFEST_CANDIDATES = [
    DEFAULT_DOWNLOADS_ROOT / "prisma_packshot_classification_manifest.json",
    DEFAULT_DOWNLOADS_ROOT / "prisma_packshot_registry_snapshot.json",
]

REGISTRY_JSON_NAME = "prisma_packshot_registry.json"
REGISTRY_CSV_NAME = "prisma_packshot_registry.csv"

REVIEW_FIELDS = [
    "source_root",
    "relative_path",
    "original_filename",
    "size_bytes",
    "sha256",
    "width",
    "height",
    "skin_guess",
    "skin_guess_confidence",
    "product_name",
    "brand",
    "variant",
    "size",
    "category",
    "skin",
    "confidence",
    "target_filename",
    "action",
    "notes",
]

REGISTRY_FIELDS = [
    "source_hint",
    "source_root",
    "original_filename",
    "relative_path",
    "size_bytes",
    "sha256",
    "width",
    "height",
    "product_name",
    "brand",
    "variant",
    "size",
    "category",
    "skin",
    "confidence",
    "target_filename",
    "action",
    "notes",
    "created_at",
    "updated_at",
]

VALID_SKINS = {"light", "dark", "unknown"}
VALID_ACTIONS = {"organize", "review", "skip"}

EXIT_OK = 0
EXIT_VALIDATION_ERROR = 2
EXIT_IO_ERROR = 3
EXIT_UNRESOLVED = 4
EXIT_INTERNAL_ERROR = 10


@dataclass(frozen=True)
class ScanFile:
    path: Path
    source_root: Path
    relative_path: str
    original_filename: str
    size_bytes: int
    sha256: str
    width: Optional[int]
    height: Optional[int]
    skin_guess: str
    skin_guess_confidence: float


@dataclass
class RunStats:
    scanned_pngs: int = 0
    known_matches: int = 0
    pending_review: int = 0
    organized: int = 0
    copied: int = 0
    moved: int = 0
    skipped: int = 0
    unresolved: int = 0
    errors: int = 0
    light: int = 0
    dark: int = 0
    unknown: int = 0
    absent_source_roots: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scanned_pngs": self.scanned_pngs,
            "known_matches": self.known_matches,
            "pending_review": self.pending_review,
            "organized": self.organized,
            "copied": self.copied,
            "moved": self.moved,
            "skipped": self.skipped,
            "unresolved": self.unresolved,
            "errors": self.errors,
            "light": self.light,
            "dark": self.dark,
            "unknown": self.unknown,
            "absent_source_roots": self.absent_source_roots,
        }


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def log(stats: RunStats, message: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    stats.logs.append(line)
    print(message)


def strip_accents(value: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", value or "")
        if not unicodedata.combining(ch)
    )


def slugify(value: str) -> str:
    value = strip_accents(value).lower()
    value = value.replace("&", " y ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "packshot"


def normalize_size(value: str) -> str:
    value = strip_accents(value or "").lower().strip()
    value = value.replace(" ", "")
    value = value.replace("litro", "l").replace("litros", "l")
    value = value.replace("gramos", "g").replace("gramo", "g")
    value = value.replace("kilogramo", "kg").replace("kilogramos", "kg")
    value = value.replace("mililitros", "ml").replace("mililitro", "ml")
    value = re.sub(r"[^a-z0-9.-]+", "", value)
    return value


def build_target_filename(product_name: str, variant: str = "", size: str = "", brand: str = "") -> str:
    parts = []
    if brand.strip():
        parts.append(brand.strip())
    if product_name.strip():
        parts.append(product_name.strip())
    if variant.strip():
        parts.append(variant.strip())
    size_norm = normalize_size(size)
    if size_norm:
        parts.append(size_norm)
    return slugify(" ".join(parts)) + ".png"


def parse_windows_or_current_path(raw: str) -> Path:
    return Path(raw).expanduser()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_png_dimensions(path: Path) -> Tuple[Optional[int], Optional[int]]:
    try:
        with path.open("rb") as fh:
            header = fh.read(24)
        if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
            width = int.from_bytes(header[16:20], "big")
            height = int.from_bytes(header[20:24], "big")
            return width, height
    except OSError:
        pass
    return None, None


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_skin_from_png_bytes(path: Path) -> Tuple[str, float]:
    """Cheap, dependency-free guess using sampled PNG file bytes.

    This intentionally does NOT replace human review for new products. It only
    pre-fills a review hint so the reviewer does less donkey work.
    """
    try:
        data = path.read_bytes()
    except OSError:
        return "unknown", 0.0
    if not data:
        return "unknown", 0.0

    # PNG files are compressed, so raw bytes are not actual pixels. Still, for
    # these generated packshots, dark/light variants usually differ strongly in
    # compressed payload distribution. This is only a hint, not truth.
    sample = data[: min(len(data), 512 * 1024)]
    avg = sum(sample) / len(sample)
    # Weak heuristic. Human review remains contract owner.
    if avg >= 105:
        return "light", 0.55
    if avg <= 92:
        return "dark", 0.55
    return "unknown", 0.25


def scan_pngs(source_roots: Sequence[Path], stats: RunStats) -> List[ScanFile]:
    found: List[ScanFile] = []
    for root in source_roots:
        if not root.exists():
            stats.absent_source_roots.append(str(root))
            continue
        if not root.is_dir():
            stats.errors += 1
            log(stats, f"WARN source root is not a directory: {root}")
            continue
        for path in sorted(root.rglob("*.png"), key=lambda p: str(p).lower()):
            try:
                size_bytes = path.stat().st_size
                digest = sha256_file(path)
                width, height = read_png_dimensions(path)
                try:
                    rel = path.relative_to(root).as_posix()
                except ValueError:
                    rel = path.name
                skin_guess, skin_guess_confidence = guess_skin_from_png_bytes(path)
                found.append(
                    ScanFile(
                        path=path,
                        source_root=root,
                        relative_path=rel,
                        original_filename=path.name,
                        size_bytes=size_bytes,
                        sha256=digest,
                        width=width,
                        height=height,
                        skin_guess=skin_guess,
                        skin_guess_confidence=skin_guess_confidence,
                    )
                )
            except OSError as exc:
                stats.errors += 1
                log(stats, f"ERROR cannot scan PNG {path}: {exc}")
    stats.scanned_pngs = len(found)
    return found


def normalize_registry_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    item = {field: raw.get(field, "") for field in REGISTRY_FIELDS}
    # Accept prior manifest fields.
    item["source_hint"] = item["source_hint"] or raw.get("source_hint", "") or raw.get("relative_path", "")
    item["original_filename"] = item["original_filename"] or Path(str(item["source_hint"])).name
    item["relative_path"] = item["relative_path"] or raw.get("source_hint", "") or item["original_filename"]
    item["size_bytes"] = int(raw.get("size_bytes") or 0)
    item["sha256"] = str(raw.get("sha256") or "").lower()
    item["width"] = int(raw.get("width") or 0) if str(raw.get("width") or "").strip() else ""
    item["height"] = int(raw.get("height") or 0) if str(raw.get("height") or "").strip() else ""
    item["brand"] = raw.get("brand", "") or ""
    item["product_name"] = raw.get("product_name", "") or ""
    item["variant"] = raw.get("variant", "") or ""
    item["size"] = raw.get("size", "") or ""
    item["category"] = raw.get("category", "") or ""
    item["skin"] = (raw.get("skin", "") or "unknown").lower()
    item["confidence"] = float(raw.get("confidence") or 0)
    item["target_filename"] = raw.get("target_filename", "") or ""
    item["action"] = (raw.get("action", "") or "review").lower()
    item["notes"] = raw.get("notes", "") or ""
    item["created_at"] = raw.get("created_at", "") or ""
    item["updated_at"] = raw.get("updated_at", "") or ""
    return item


def load_registry(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        items = data.get("items", [])
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError(f"Registry JSON has unsupported shape: {path}")
    return [normalize_registry_item(item) for item in items]


def write_registry_json(path: Path, items: List[Dict[str, Any]], source_note: str = "") -> None:
    ensure_dir(path.parent)
    skin_counts = {"light": 0, "dark": 0, "unknown": 0}
    action_counts = {"organize": 0, "review": 0, "skip": 0}
    for item in items:
        skin = str(item.get("skin", "unknown") or "unknown").lower()
        action = str(item.get("action", "review") or "review").lower()
        skin_counts[skin if skin in skin_counts else "unknown"] += 1
        action_counts[action if action in action_counts else "review"] += 1
    payload = {
        "project": PROJECT_NAME,
        "tool_version": TOOL_VERSION,
        "updated_at": iso_now(),
        "source_note": source_note,
        "total_images": len(items),
        "skin_counts": skin_counts,
        "action_counts": action_counts,
        "items": items,
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def write_registry_csv(path: Path, items: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REGISTRY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for item in items:
            writer.writerow({field: item.get(field, "") for field in REGISTRY_FIELDS})


def resolve_repo_root(args: argparse.Namespace) -> Path:
    if args.repo_root:
        return parse_windows_or_current_path(args.repo_root)
    # If the script lives under tools/prisma_packshots, infer repo root.
    this_file = Path(__file__).resolve()
    parts = list(this_file.parts)
    try:
        idx = parts.index("tools")
        maybe_root = Path(*parts[:idx])
        if maybe_root.exists():
            return maybe_root
    except ValueError:
        pass
    return DEFAULT_REPO_ROOT


def registry_paths(repo_root: Path, args: argparse.Namespace) -> Tuple[Path, Path]:
    if args.registry_json:
        json_path = parse_windows_or_current_path(args.registry_json)
        csv_path = json_path.with_suffix(".csv")
        return json_path, csv_path
    data_dir = repo_root / DEFAULT_DATA_RELATIVE_DIR
    return data_dir / REGISTRY_JSON_NAME, data_dir / REGISTRY_CSV_NAME


def find_seed_manifest(repo_registry_path: Path, args: argparse.Namespace) -> Optional[Path]:
    if args.seed_manifest:
        p = parse_windows_or_current_path(args.seed_manifest)
        return p if p.exists() else None
    if repo_registry_path.exists():
        return repo_registry_path
    for candidate in DEFAULT_EXTERNAL_MANIFEST_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def build_indexes(items: List[Dict[str, Any]]) -> Dict[str, Dict[Any, Dict[str, Any]]]:
    by_sha: Dict[str, Dict[str, Any]] = {}
    by_rel: Dict[str, Dict[str, Any]] = {}
    by_name_size: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for item in items:
        sha = str(item.get("sha256", "") or "").lower()
        if sha:
            by_sha.setdefault(sha, item)
        rel = str(item.get("relative_path", "") or item.get("source_hint", "") or "").replace("\\", "/")
        if rel:
            by_rel.setdefault(rel.lower(), item)
        filename = str(item.get("original_filename", "") or "").lower()
        size = int(item.get("size_bytes") or 0)
        if filename and size:
            by_name_size.setdefault((filename, size), item)
    return {"sha": by_sha, "rel": by_rel, "name_size": by_name_size}


def match_item(scan: ScanFile, indexes: Dict[str, Dict[Any, Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    item = indexes["sha"].get(scan.sha256.lower())
    if item:
        return item
    rel_candidates = [scan.relative_path.lower(), f"{scan.source_root.name}/{scan.relative_path}".replace("\\", "/").lower()]
    for rel in rel_candidates:
        item = indexes["rel"].get(rel)
        if item:
            return item
    return indexes["name_size"].get((scan.original_filename.lower(), scan.size_bytes))


def scan_to_inventory_row(scan: ScanFile, status: str, matched_item: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "status": status,
        "source_root": str(scan.source_root),
        "relative_path": scan.relative_path,
        "original_filename": scan.original_filename,
        "size_bytes": scan.size_bytes,
        "sha256": scan.sha256,
        "width": scan.width or "",
        "height": scan.height or "",
        "skin_guess": scan.skin_guess,
        "skin_guess_confidence": f"{scan.skin_guess_confidence:.2f}",
        "matched_target_filename": matched_item.get("target_filename", "") if matched_item else "",
        "matched_skin": matched_item.get("skin", "") if matched_item else "",
        "matched_product_name": matched_item.get("product_name", "") if matched_item else "",
    }


def pending_review_row(scan: ScanFile) -> Dict[str, Any]:
    return {
        "source_root": str(scan.source_root),
        "relative_path": scan.relative_path,
        "original_filename": scan.original_filename,
        "size_bytes": scan.size_bytes,
        "sha256": scan.sha256,
        "width": scan.width or "",
        "height": scan.height or "",
        "skin_guess": scan.skin_guess,
        "skin_guess_confidence": f"{scan.skin_guess_confidence:.2f}",
        "product_name": "",
        "brand": "",
        "variant": "",
        "size": "",
        "category": "",
        "skin": "",
        "confidence": "",
        "target_filename": "",
        "action": "review",
        "notes": "Nuevo PNG: llenar producto, categoria, skin, confidence y target_filename antes de aplicar.",
    }


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: Sequence[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def safe_collision_path(target_dir: Path, filename: str) -> Path:
    base = Path(filename).stem
    suffix = Path(filename).suffix or ".png"
    candidate = target_dir / f"{base}{suffix}"
    if not candidate.exists():
        return candidate
    i = 2
    while True:
        candidate = target_dir / f"{base}-{i:02d}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def validate_registry_item(item: Dict[str, Any], allow_unknown: bool = False) -> List[str]:
    errors: List[str] = []
    action = str(item.get("action", "") or "").lower()
    if action not in VALID_ACTIONS:
        errors.append(f"invalid action {action!r}")
    skin = str(item.get("skin", "") or "").lower()
    if skin not in VALID_SKINS:
        errors.append(f"invalid skin {skin!r}")
    if action == "organize":
        if skin == "unknown" and not allow_unknown:
            errors.append("skin unknown requires --include-unknown")
        if not str(item.get("product_name", "") or "").strip():
            errors.append("product_name is required")
        if not str(item.get("category", "") or "").strip():
            errors.append("category is required")
        if not str(item.get("target_filename", "") or "").strip():
            errors.append("target_filename is required")
        if not str(item.get("target_filename", "") or "").lower().endswith(".png"):
            errors.append("target_filename must end with .png")
        try:
            confidence = float(item.get("confidence") or 0)
            if confidence < 0 or confidence > 1:
                errors.append("confidence must be between 0 and 1")
        except ValueError:
            errors.append("confidence must be numeric")
    return errors


def organize_known(
    scans: List[ScanFile],
    indexes: Dict[str, Dict[Any, Dict[str, Any]]],
    args: argparse.Namespace,
    stats: RunStats,
) -> List[Dict[str, Any]]:
    operations: List[Dict[str, Any]] = []
    for scan in scans:
        item = match_item(scan, indexes)
        if not item:
            continue
        stats.known_matches += 1
        action = str(item.get("action", "review") or "review").lower()
        skin = str(item.get("skin", "unknown") or "unknown").lower()
        if skin == "light":
            stats.light += 1
        elif skin == "dark":
            stats.dark += 1
        else:
            stats.unknown += 1
        if action != "organize":
            stats.skipped += 1
            operations.append({"source": str(scan.path), "status": "skipped_action", "action": action})
            continue
        if skin == "unknown" and not args.include_unknown:
            stats.skipped += 1
            operations.append({"source": str(scan.path), "status": "skipped_unknown_skin"})
            continue
        errors = validate_registry_item(item, allow_unknown=args.include_unknown)
        if errors:
            stats.errors += 1
            operations.append({"source": str(scan.path), "status": "validation_error", "errors": errors})
            continue
        if skin == "light":
            target_dir = args.light_target
        elif skin == "dark":
            target_dir = args.dark_target
        else:
            target_dir = args.review_target
        ensure_dir(target_dir)
        target_filename = str(item.get("target_filename") or build_target_filename(item.get("product_name", ""), item.get("variant", ""), item.get("size", ""), item.get("brand", "")))
        target_path = safe_collision_path(target_dir, target_filename)
        if args.dry_run:
            operations.append({"source": str(scan.path), "target": str(target_path), "status": "dry_run"})
            continue
        try:
            if args.mode == "move":
                shutil.move(str(scan.path), str(target_path))
                stats.moved += 1
                op_status = "moved"
            else:
                shutil.copy2(scan.path, target_path)
                stats.copied += 1
                op_status = "copied"
            stats.organized += 1
            operations.append({"source": str(scan.path), "target": str(target_path), "status": op_status})
        except OSError as exc:
            stats.errors += 1
            operations.append({"source": str(scan.path), "target": str(target_path), "status": "io_error", "error": str(exc)})
    return operations


def maybe_make_contact_sheets(pending_scans: List[ScanFile], out_dir: Path, stats: RunStats, thumb_size: int = 220, cols: int = 5) -> List[str]:
    if not pending_scans:
        return []
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        log(stats, "INFO Pillow no está instalado; se omiten contact sheets opcionales.")
        return []
    ensure_dir(out_dir)
    paths: List[str] = []
    rows = (len(pending_scans) + cols - 1) // cols
    margin = 18
    label_h = 52
    sheet_w = cols * (thumb_size + margin) + margin
    sheet_h = rows * (thumb_size + label_h + margin) + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, scan in enumerate(pending_scans):
        r = idx // cols
        c = idx % cols
        x = margin + c * (thumb_size + margin)
        y = margin + r * (thumb_size + label_h + margin)
        try:
            with Image.open(scan.path) as im:
                im.thumbnail((thumb_size, thumb_size))
                bg = Image.new("RGB", (thumb_size, thumb_size), "white")
                bg.paste(im.convert("RGBA"), ((thumb_size - im.width) // 2, (thumb_size - im.height) // 2), im.convert("RGBA"))
                sheet.paste(bg, (x, y))
        except Exception as exc:
            draw.rectangle([x, y, x + thumb_size, y + thumb_size], outline="red")
            draw.text((x + 5, y + 5), f"ERR {exc}", fill="red")
        label = f"{idx + 1}. {scan.original_filename[:38]}"
        draw.text((x, y + thumb_size + 6), label, fill="black")
        draw.text((x, y + thumb_size + 24), f"guess: {scan.skin_guess}", fill="black")
    out = out_dir / f"prisma_packshot_pending_contact_sheet_{now_stamp()}.jpg"
    sheet.save(out, quality=90)
    paths.append(str(out))
    return paths


def run_once(args: argparse.Namespace) -> int:
    stats = RunStats()
    ensure_dir(args.output_root)
    repo_root = resolve_repo_root(args)
    repo_registry_json, repo_registry_csv = registry_paths(repo_root, args)
    seed = find_seed_manifest(repo_registry_json, args)
    if seed:
        registry_items = load_registry(seed)
        log(stats, f"Registry loaded: {seed} ({len(registry_items)} items)")
    else:
        registry_items = []
        log(stats, "Registry not found; starting with empty registry. New PNGs will go to review.")

    if not repo_registry_json.exists() and registry_items:
        write_registry_json(repo_registry_json, registry_items, source_note=f"Bootstrapped from {seed}")
        write_registry_csv(repo_registry_csv, registry_items)
        log(stats, f"Repo registry bootstrapped: {repo_registry_json}")

    scans = scan_pngs(args.source_roots, stats)
    indexes = build_indexes(registry_items)
    inventory_rows: List[Dict[str, Any]] = []
    pending_rows: List[Dict[str, Any]] = []
    pending_scans: List[ScanFile] = []
    for scan in scans:
        item = match_item(scan, indexes)
        if item:
            inventory_rows.append(scan_to_inventory_row(scan, "known", item))
        else:
            stats.pending_review += 1
            inventory_rows.append(scan_to_inventory_row(scan, "pending_review", None))
            pending_rows.append(pending_review_row(scan))
            pending_scans.append(scan)

    stamp = now_stamp()
    inventory_csv = args.output_root / f"prisma_packshot_inventory_{stamp}.csv"
    inventory_json = args.output_root / f"prisma_packshot_inventory_{stamp}.json"
    write_csv(inventory_csv, inventory_rows, list(inventory_rows[0].keys()) if inventory_rows else ["status"])
    write_json(inventory_json, {"created_at": iso_now(), "total": len(inventory_rows), "items": inventory_rows})
    log(stats, f"Inventory written: {inventory_csv}")

    pending_csv: Optional[Path] = None
    if pending_rows:
        pending_csv = args.output_root / f"prisma_packshot_pending_review_{stamp}.csv"
        write_csv(pending_csv, pending_rows, REVIEW_FIELDS)
        log(stats, f"Pending review CSV written: {pending_csv}")
        if args.contact_sheet:
            contact_paths = maybe_make_contact_sheets(pending_scans, args.output_root, stats)
            for p in contact_paths:
                log(stats, f"Contact sheet written: {p}")

    operations = organize_known(scans, indexes, args, stats)
    operations_json = args.output_root / f"prisma_packshot_operations_{stamp}.json"
    write_json(operations_json, {"created_at": iso_now(), "mode": args.mode, "dry_run": args.dry_run, "items": operations})

    # Always emit registry snapshots from current registry, even if no review was applied.
    snapshot_json = args.output_root / f"prisma_packshot_registry_snapshot_{stamp}.json"
    snapshot_csv = args.output_root / f"prisma_packshot_registry_snapshot_{stamp}.csv"
    write_registry_json(snapshot_json, registry_items, source_note=f"Snapshot from {repo_registry_json}")
    write_registry_csv(snapshot_csv, registry_items)

    final_status = "READY" if stats.errors == 0 and stats.pending_review == 0 else "READY_WITH_REVIEW"
    if stats.errors:
        final_status = "READY_WITH_CAVEATS"
    summary = stats.as_dict()
    summary.update({
        "status": final_status,
        "repo_root": str(repo_root),
        "repo_registry_json": str(repo_registry_json),
        "inventory_csv": str(inventory_csv),
        "inventory_json": str(inventory_json),
        "pending_review_csv": str(pending_csv) if pending_csv else "",
        "operations_json": str(operations_json),
        "registry_snapshot_json": str(snapshot_json),
        "registry_snapshot_csv": str(snapshot_csv),
    })
    log_path = args.output_root / f"prisma_packshot_update_{stamp}.log"
    with log_path.open("w", encoding="utf-8") as fh:
        fh.write("PRISMA packshot updater log\n")
        fh.write(json.dumps(summary, ensure_ascii=False, indent=2))
        fh.write("\n\nEvents:\n")
        for line in stats.logs:
            fh.write(line + "\n")
    print("\n=== PRISMA PACKSHOT SUMMARY ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"log: {log_path}")
    if pending_csv:
        print("\nHay PNGs nuevos: llena el pending_review CSV y luego corre --apply-review.")
    return EXIT_OK if not stats.errors else EXIT_IO_ERROR


def read_review_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    # Normalize BOM weirdness.
    normalized = []
    for row in rows:
        clean = {k.lstrip("\ufeff"): v for k, v in row.items()}
        normalized.append(clean)
    return normalized


def apply_review(args: argparse.Namespace) -> int:
    stats = RunStats()
    repo_root = resolve_repo_root(args)
    repo_registry_json, repo_registry_csv = registry_paths(repo_root, args)
    seed = find_seed_manifest(repo_registry_json, args)
    registry_items = load_registry(seed) if seed else []
    review_path = parse_windows_or_current_path(args.apply_review)
    if not review_path.exists():
        print(f"ERROR review CSV not found: {review_path}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    review_rows = read_review_csv(review_path)
    existing_sha = {str(item.get("sha256", "") or "").lower() for item in registry_items if item.get("sha256")}
    errors: List[str] = []
    additions: List[Dict[str, Any]] = []
    seen_sha: set[str] = set()
    for index, row in enumerate(review_rows, start=2):
        sha = str(row.get("sha256", "") or "").lower().strip()
        if not sha:
            errors.append(f"row {index}: sha256 is required")
            continue
        if sha in existing_sha or sha in seen_sha:
            continue
        seen_sha.add(sha)
        product_name = str(row.get("product_name", "") or "").strip()
        variant = str(row.get("variant", "") or "").strip()
        size = str(row.get("size", "") or "").strip()
        brand = str(row.get("brand", "") or "").strip()
        target_filename = str(row.get("target_filename", "") or "").strip()
        if not target_filename and product_name:
            target_filename = build_target_filename(product_name, variant=variant, size=size, brand=brand)
        item = normalize_registry_item({
            "source_hint": f"{Path(str(row.get('source_root', ''))).name}/{row.get('relative_path', '')}".strip("/"),
            "source_root": row.get("source_root", ""),
            "original_filename": row.get("original_filename", ""),
            "relative_path": row.get("relative_path", ""),
            "size_bytes": row.get("size_bytes", 0),
            "sha256": sha,
            "width": row.get("width", ""),
            "height": row.get("height", ""),
            "product_name": product_name,
            "brand": brand,
            "variant": variant,
            "size": size,
            "category": row.get("category", ""),
            "skin": row.get("skin", "unknown"),
            "confidence": row.get("confidence", 0),
            "target_filename": target_filename,
            "action": row.get("action", "organize") or "organize",
            "notes": row.get("notes", ""),
            "created_at": iso_now(),
            "updated_at": iso_now(),
        })
        item_errors = validate_registry_item(item, allow_unknown=args.include_unknown)
        if item_errors:
            errors.append(f"row {index}: " + "; ".join(item_errors))
        else:
            additions.append(item)
    if errors:
        print("ERROR review CSV has validation problems:", file=sys.stderr)
        for err in errors[:100]:
            print(f"- {err}", file=sys.stderr)
        if len(errors) > 100:
            print(f"... {len(errors) - 100} more", file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    registry_items.extend(additions)
    write_registry_json(repo_registry_json, registry_items, source_note=f"Applied review CSV {review_path}")
    write_registry_csv(repo_registry_csv, registry_items)
    ensure_dir(args.output_root)
    stamp = now_stamp()
    write_registry_json(args.output_root / f"prisma_packshot_registry_after_review_{stamp}.json", registry_items, source_note=f"Applied review CSV {review_path}")
    write_registry_csv(args.output_root / f"prisma_packshot_registry_after_review_{stamp}.csv", registry_items)
    print("=== REVIEW APPLIED ===")
    print(f"review_csv: {review_path}")
    print(f"added_items: {len(additions)}")
    print(f"registry_json: {repo_registry_json}")
    print(f"registry_csv: {repo_registry_csv}")
    return EXIT_OK


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="update_prisma_packshots.py",
        description="Actualiza y organiza la librería de packshots PRISMA genéricos.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python \"F:\\repos\\hitech-os\\tools\\prisma_packshots\\update_prisma_packshots.py\" --run\n"
            "  python \"F:\\repos\\hitech-os\\tools\\prisma_packshots\\update_prisma_packshots.py\" --run --mode copy\n"
            "  python \"F:\\repos\\hitech-os\\tools\\prisma_packshots\\update_prisma_packshots.py\" --apply-review \"F:\\descargasf\\prisma_packshot_pending_review_YYYYMMDD_HHMMSS.csv\"\n"
            "  python \"F:\\repos\\hitech-os\\tools\\prisma_packshots\\update_prisma_packshots.py\" --run --source-root \"F:\\Imagenes packshot 11\"\n"
        ),
    )
    parser.add_argument("--run", action="store_true", help="Escanea fuentes, organiza conocidos y genera pending_review para nuevos PNGs.")
    parser.add_argument("--apply-review", help="CSV de revisión humana ya llenado; lo valida y lo agrega al registry.")
    parser.add_argument("--watch", action="store_true", help="Modo opcional: repite --run cada --interval segundos.")
    parser.add_argument("--interval", type=int, default=30, help="Segundos entre escaneos en --watch. Default: 30.")
    parser.add_argument("--repo-root", help=r"Raíz del repo. Default: inferido o F:\repos\hitech-os.")
    parser.add_argument("--registry-json", help="Ruta explícita al registry JSON dentro o fuera del repo.")
    parser.add_argument("--seed-manifest", help="Manifest inicial si el registry del repo todavía no existe.")
    parser.add_argument("--source-root", dest="source_roots", action="append", help="Raíz de PNGs. Se puede repetir. Si se omite usa F:\\Imagenes packshot 1..10.")
    parser.add_argument("--output-root", default=str(DEFAULT_DOWNLOADS_ROOT), help=r"Carpeta de logs/manifests de salida. Default: F:\descargasf.")
    parser.add_argument("--light-target", default=str(DEFAULT_LIGHT_TARGET), help=r"Target light. Default: F:\light packshots.")
    parser.add_argument("--dark-target", default=str(DEFAULT_DARK_TARGET), help=r"Target dark. Default: F:\dark packshots.")
    parser.add_argument("--review-target", default=str(DEFAULT_REVIEW_TARGET), help=r"Target unknown si --include-unknown. Default: F:\packshots review.")
    parser.add_argument("--mode", choices=["copy", "move"], default="copy", help="copy por defecto; move opcional.")
    parser.add_argument("--include-unknown", action="store_true", help="Permite organizar skin=unknown hacia review-target.")
    parser.add_argument("--dry-run", action="store_true", help="No copia/mueve; solo muestra y escribe inventario.")
    parser.add_argument("--contact-sheet", action="store_true", help="Opcional: genera contact sheet para pending review si Pillow está instalado.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {TOOL_VERSION}")
    return parser


def normalize_args(args: argparse.Namespace) -> argparse.Namespace:
    if args.source_roots:
        args.source_roots = [parse_windows_or_current_path(raw) for raw in args.source_roots]
    else:
        args.source_roots = DEFAULT_SOURCE_ROOTS
    args.output_root = parse_windows_or_current_path(args.output_root)
    args.light_target = parse_windows_or_current_path(args.light_target)
    args.dark_target = parse_windows_or_current_path(args.dark_target)
    args.review_target = parse_windows_or_current_path(args.review_target)
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = normalize_args(parser.parse_args(argv))
    if not args.run and not args.apply_review:
        parser.print_help(sys.stderr)
        return EXIT_VALIDATION_ERROR
    try:
        if args.apply_review:
            return apply_review(args)
        if args.watch:
            while True:
                code = run_once(args)
                if code not in (EXIT_OK, EXIT_IO_ERROR):
                    return code
                print(f"\nWatching... next scan in {args.interval} seconds. Ctrl+C para salir.")
                time.sleep(max(5, args.interval))
        return run_once(args)
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario.")
        return EXIT_OK
    except ValueError as exc:
        print(f"ERROR validation: {exc}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    except OSError as exc:
        print(f"ERROR io: {exc}", file=sys.stderr)
        return EXIT_IO_ERROR
    except Exception as exc:
        print(f"ERROR internal: {exc}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
