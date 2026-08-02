#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PRISMA dark-only managed packshot builder.

This is the dark runtime companion to the historical registry updater. The
historical updater remains available for human review and registry maintenance;
this motor consumes reviewed PNGs, matches the registry by SHA-256, creates a
portable managed library, aliases legacy target filenames, thumbnails, manifests,
snapshots and QA evidence without touching PC/Tablet databases or live processes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

VERSION = "2.0.0"
DEFAULT_REPO = Path(r"F:\repos\hitech-os")
DEFAULT_OUTPUT = Path(r"F:\descargasf")
MANAGED_REL = Path("tools/_local/data/terminal-de-venta-system/product-media")
REGISTRY_REL = Path("tools/prisma_packshots/data/prisma_packshot_registry.json")

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def png_size(data: bytes) -> tuple[int, int]:
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    return 0, 0

def discover_repo(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "apps/terminal-de-venta-system").exists() and (candidate / "tools").exists():
            return candidate
    return DEFAULT_REPO

def iter_pngs(sources: Iterable[Path]):
    for source in sources:
        if source.is_dir():
            for path in sorted(source.rglob("*.png"), key=lambda item: str(item).lower()):
                yield path.name, path.read_bytes(), str(path)
        elif source.is_file() and source.suffix.lower() == ".zip":
            with zipfile.ZipFile(source, "r") as archive:
                for info in sorted(archive.infolist(), key=lambda item: item.filename.lower()):
                    if info.is_dir() or not info.filename.lower().endswith(".png"):
                        continue
                    yield Path(info.filename).name, archive.read(info.filename), f"{source}!/{info.filename}"
        else:
            raise FileNotFoundError(f"Fuente no válida: {source}")

def load_json(path: Path, default: Any):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))

def registry_by_sha(path: Path) -> dict[str, list[dict[str, Any]]]:
    raw = load_json(path, {})
    items = raw.get("items", raw if isinstance(raw, list) else [])
    result: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        digest = str(item.get("sha256") or "").lower()
        if digest:
            result.setdefault(digest, []).append(item)
    return result

def safe_filename(value: str) -> str:
    name = Path(value).name
    if not name.lower().endswith(".png"):
        raise ValueError(f"Nombre no PNG: {value}")
    if not all(char.isalnum() or char in "._-" for char in name):
        raise ValueError(f"Nombre no portable: {value}")
    return name

def ensure_alias(source: Path, target: Path) -> str:
    if target.exists():
        if sha256_file(target) != sha256_file(source):
            raise RuntimeError(f"Colisión con contenido distinto: {target}")
        return "already_present"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
        return "hardlink"
    except OSError:
        shutil.copy2(source, target)
        return "copy"

def make_thumbnail(source: Path, target: Path) -> str:
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return "pillow_unavailable"
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = image.convert("RGBA")
        image.thumbnail((192, 192), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (192, 192), (7, 9, 14, 255))
        canvas.alpha_composite(image, ((192 - image.width) // 2, (192 - image.height) // 2))
        canvas.convert("RGB").save(target, "PNG", optimize=True)
    return "written"

def run(args: argparse.Namespace) -> int:
    repo = discover_repo(args.repo)
    output = Path(args.output_root)
    output.mkdir(parents=True, exist_ok=True)
    managed = Path(args.managed_root) if args.managed_root else repo / MANAGED_REL
    registry = Path(args.registry_json) if args.registry_json else repo / REGISTRY_REL
    sources = [Path(value) for value in args.source]
    if not sources:
        sources = [Path(r"F:\dark packshots")]

    packaged_manifest = load_json(Path(args.manifest), {}) if args.manifest else {}
    packaged_by_name = {str(item.get("canonicalName")): item for item in packaged_manifest.get("items", [])}
    registry_index = registry_by_sha(registry)
    records: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    seen_hashes: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []

    for name, data, source_hint in iter_pngs(sources):
        name = safe_filename(name)
        if name in seen_names:
            raise RuntimeError(f"Nombre repetido entre fuentes: {name}")
        seen_names.add(name)
        digest = sha256_bytes(data)
        width, height = png_size(data)
        base = dict(packaged_by_name.get(name, {}))
        base.update({
            "canonicalName": name,
            "sourceNameReceived": name,
            "sourceHint": source_hint,
            "sha256Source": digest,
            "sha256Runtime": digest,
            "width": width,
            "height": height,
            "darkVerified": True,
            "runtimePath": f"/product-media/catalog/{name}",
            "thumbnailPath": f"/product-media/thumbnails/{name}",
        })
        if digest in seen_hashes:
            base["duplicateOfCanonicalName"] = seen_hashes[digest]
            duplicates.append({"alias": name, "canonical": seen_hashes[digest], "sha256": digest})
        else:
            seen_hashes[digest] = name
        legacy_targets = []
        for item in registry_index.get(digest, []):
            if str(item.get("skin") or "").lower() == "dark" and item.get("target_filename"):
                legacy_targets.append(safe_filename(str(item["target_filename"])))
        base["legacyRuntimeNames"] = sorted(set(legacy_targets))
        records.append(base)

    if args.expected_count and len(records) != args.expected_count:
        raise RuntimeError(f"Total inesperado: {len(records)}; esperado {args.expected_count}")

    timestamp = stamp()
    inventory = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "version": VERSION,
        "mode": "dark_only",
        "sources": [str(source) for source in sources],
        "counts": {
            "records": len(records),
            "uniqueVisuals": len(seen_hashes),
            "duplicateAliases": len(duplicates),
        },
        "items": records,
    }
    (output / f"prisma_dark_packshot_inventory_{timestamp}.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.dry_run:
        print(json.dumps(inventory["counts"], indent=2))
        return 0

    catalog_dir = managed / "catalog"
    thumbnail_dir = managed / "thumbnails"
    manifest_dir = managed / "manifest"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    operations = []
    with tempfile.TemporaryDirectory(prefix="prisma_dark_packshots_") as td:
        temp = Path(td)
        data_by_name = {name: data for name, data, _ in iter_pngs(sources)}
        for record in records:
            name = record["canonicalName"]
            source = temp / name
            source.write_bytes(data_by_name[name])
            target = catalog_dir / name
            if target.exists() and sha256_file(target) != record["sha256Source"]:
                raise RuntimeError(f"El target existente no coincide: {target}")
            if not target.exists():
                shutil.copy2(source, target)
            thumb_status = make_thumbnail(target, thumbnail_dir / name)
            aliases = []
            for alias in record.get("legacyRuntimeNames", []):
                aliases.append({"name": alias, "status": ensure_alias(target, catalog_dir / alias)})
            operations.append({"name": name, "thumbnail": thumb_status, "aliases": aliases})

    catalog_payload = dict(packaged_manifest) if packaged_manifest else {}
    catalog_payload.update({
        "schemaVersion": catalog_payload.get("schemaVersion", "2.0.0"),
        "libraryId": catalog_payload.get("libraryId", "PRISMA_DARK_PACKSHOTS"),
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "mode": "dark_only",
        "counts": inventory["counts"],
        "items": records,
    })
    (manifest_dir / "PACKSHOT_CATALOG.json").write_text(
        json.dumps(catalog_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    search_items = [
        {key: item.get(key) for key in ("assetId", "displayName", "category", "keywords", "runtimePath", "thumbnailPath", "canonicalName")}
        for item in records if item.get("selectable", True)
    ]
    (manifest_dir / "PACKSHOT_SEARCH_INDEX.json").write_text(
        json.dumps({"schemaVersion": "1.0.0", "items": search_items}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    qa = {
        "status": "PASS",
        "counts": inventory["counts"],
        "duplicates": duplicates,
        "operations": operations,
        "managedRoot": str(managed),
    }
    (output / f"prisma_dark_packshot_qa_{timestamp}.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(qa["counts"], indent=2))
    return 0

def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Construye la biblioteca oscura administrada de packshots PRISMA.")
    value.add_argument("--run", action="store_true")
    value.add_argument("--repo")
    value.add_argument("--source", action="append", default=[])
    value.add_argument("--manifest")
    value.add_argument("--registry-json")
    value.add_argument("--managed-root")
    value.add_argument("--output-root", default=str(DEFAULT_OUTPUT))
    value.add_argument("--expected-count", type=int, default=0)
    value.add_argument("--dry-run", action="store_true")
    value.add_argument("--contact-sheet", action="store_true", help="Reservado; las miniaturas se generan con Pillow cuando está disponible.")
    value.add_argument("--version", action="version", version=VERSION)
    return value

def main() -> int:
    args = parser().parse_args()
    if not args.run:
        parser().print_help(sys.stderr)
        return 2
    try:
        return run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
