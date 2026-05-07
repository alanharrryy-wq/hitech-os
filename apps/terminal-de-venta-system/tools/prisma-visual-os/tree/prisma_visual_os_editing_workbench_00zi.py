from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PACKAGE = "PRISMA_VISUAL_OS_EDITING_WORKBENCH_00ZI"
REQUIRED_LANES = [
    "realtime-api", "tablet-realtime-ui", "tablet-pro-ui", "doctors", "ai-doctor",
    "gates", "qa", "scoring", "generators", "launchers", "compatibility-shims", "legacy-tolerated",
]
CANONICAL_URLS = [
    "http://127.0.0.1:3120/", "http://127.0.0.1:3130/", "http://127.0.0.1:3140/",
    "http://127.0.0.1:4177/health", "http://127.0.0.1:4177/state",
    "http://127.0.0.1:3120/visual-os/realtime", "http://127.0.0.1:3120/visual-os/pro",
]
LEGACY_URLS = ["http://127.0.0.1:3120/prisma-dark-pos-reference", "http://127.0.0.1:3140/prisma-app"]


def resolve_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def load_manifest(target_root: Path) -> Dict[str, Any]:
    path = target_root / "tools" / "prisma-visual-os" / "config" / "visual-os-editing-map.json"
    if not path.exists():
        raise RuntimeError(f"Missing manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def lane_by_id(manifest: Dict[str, Any], lane_id: str) -> Optional[Dict[str, Any]]:
    for lane in manifest.get("lanes", []):
        if lane.get("id") == lane_id:
            return lane
    return None


def validator_target_exists(target_root: Path, command: str) -> bool:
    for token in command.split()[1:]:
        if token.endswith((".mjs", ".py", ".cmd", ".json", ".md")):
            return (target_root / token).exists()
    return True


def verify_manifest(target_root: Path, manifest: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    docs = target_root / "tools" / "prisma-visual-os" / "docs" / "VISUAL_OS_EDITING_MAP.md"
    if not docs.exists():
        errors.append(f"Missing docs map: {docs}")
    elif PACKAGE not in docs.read_text(encoding="utf-8", errors="replace"):
        errors.append("Docs map missing package marker")
    if manifest.get("package") != PACKAGE and manifest.get("marker") != PACKAGE:
        errors.append("Manifest missing package marker")
    lane_ids = {lane.get("id") for lane in manifest.get("lanes", [])}
    for lane in REQUIRED_LANES:
        if lane not in lane_ids:
            errors.append(f"Missing lane: {lane}")
    canonical = set(manifest.get("canonicalUrls", []))
    legacy = set(manifest.get("legacyUrls", []))
    for url in CANONICAL_URLS:
        if url not in canonical:
            errors.append(f"Missing canonical URL: {url}")
    for url in LEGACY_URLS:
        if url not in legacy:
            errors.append(f"Missing legacy URL: {url}")
        if url in canonical:
            errors.append(f"Legacy URL incorrectly canonical: {url}")
    for lane in manifest.get("lanes", []):
        lane_id = lane.get("id", "<missing>")
        for rel in lane.get("canonicalFiles", []):
            if not (target_root / rel).exists():
                errors.append(f"Lane {lane_id} missing canonical file/dir: {rel}")
        for command in lane.get("validators", []):
            if not validator_target_exists(target_root, command):
                errors.append(f"Lane {lane_id} missing validator target: {command}")
    return errors


def print_lane(lane: Dict[str, Any]) -> None:
    print(f"Lane: {lane.get('id')} - {lane.get('name')}")
    print(f"Purpose: {lane.get('purpose')}")
    for label, key in [("Canonical files", "canonicalFiles"), ("Compatibility shims", "compatibilityShims"), ("Validators", "validators"), ("Safe edit rules", "safeEditRules"), ("Forbidden edits", "forbiddenEdits")]:
        print(label + ":")
        for item in lane.get(key, []):
            print(f"  - {item}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PRISMA Visual OS 00ZI editing workbench helper")
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--list-lanes", action="store_true")
    parser.add_argument("--lane")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not Path(args.target_root).is_absolute():
        parser.error("--target-root must be absolute")
    if not (args.list_lanes or args.lane or args.verify):
        parser.error("Choose --list-lanes, --lane, or --verify")
    return args


def main() -> int:
    args = parse_args()
    target_root = resolve_path(args.target_root)
    if not target_root.exists():
        print(f"Target root does not exist: {target_root}", file=sys.stderr)
        return 2
    try:
        manifest = load_manifest(target_root)
        if args.verify:
            errors = verify_manifest(target_root, manifest)
            result = {"ok": not errors, "package": PACKAGE, "targetRoot": str(target_root), "errors": errors}
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif errors:
                print("PRISMA Visual OS editing workbench verify FAILED")
                for error in errors:
                    print(f"- {error}")
            else:
                print("PRISMA Visual OS editing workbench verify OK")
            return 0 if not errors else 3
        if args.list_lanes:
            lanes = manifest.get("lanes", [])
            if args.json:
                print(json.dumps({"lanes": lanes}, ensure_ascii=False, indent=2))
            else:
                for lane in lanes:
                    print(f"{lane.get('id')}: {lane.get('name')}")
            return 0
        if args.lane:
            lane = lane_by_id(manifest, args.lane)
            if not lane:
                print(f"Unknown lane: {args.lane}", file=sys.stderr)
                return 4
            if args.json:
                print(json.dumps(lane, ensure_ascii=False, indent=2))
            else:
                print_lane(lane)
            return 0
        return 0
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
