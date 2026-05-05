#!/usr/bin/env python3
r"""PRISMA tri-surface visual guardian 00B.

Validates that visual changes declare coverage for Tablet, PC, and App móvil while
preserving Tablet standalone autonomy.

Examples:
  python tools/prisma/prisma_tri_surface_visual_guardian_00b.py --root F:\repos\hitech-os\apps\terminal-de-venta-system --manifest manifests\PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B.manifest.json --text
  python tools/prisma/prisma_tri_surface_visual_guardian_00b.py --manifest path\visual-change.manifest.json --changed-files changed_files.txt --text
  python tools/prisma/prisma_tri_surface_visual_guardian_00b.py --payload PRISMA_BLACK_VISUAL_REFINEMENT_01G_payload.zip --text
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath
from typing import Any

PACKAGE = "PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B"

TABLET = "prisma.tablet.pos"
PC = "prisma.pc.backoffice"
MOBILE = "prisma.mobile.app"
REQUIRED_SURFACES = [TABLET, PC, MOBILE]
ALLOWED_STATES = {"TOUCHED", "VALIDATED", "EXCLUDED"}
FORBIDDEN_STATES = {"OMITTED"}

TABLET_PATTERNS = ["products/tablet/app/**"]
MOBILE_PATTERNS = [
    "products/mobile/app/**",
]
MOBILE_LEGACY_PATTERNS = [
    "products/pc/app/app/prisma-app/**",
    "products/pc/app/src/lib/prisma-app/**",
    "products/pc/app/docs/prisma-app/**",
    "products/pc/app/app/pulso/**",
    "products/pc/app/src/lib/pulso/**",
]
PC_PATTERNS = ["products/pc/app/**"]
SHARED_VISUAL_PATTERNS = ["products/shared-ui/prisma/**"]
SHARED_GOVERNANCE_PATTERNS = [
    "shared/contracts/ui/**",
    "docs/design/**",
    "docs/qa/**",
    "tools/prisma/**",
    "manifests/**",
]

REQUIRED_AUTONOMY_TRUE = [
    "tabletSellsStandalone",
    "tabletDoesNotRequirePc",
    "tabletDoesNotRequireMobile",
    "pcIsBackofficeAsset",
    "mobileIsPulseAsset",
    "noAssetRequiredForTabletSale",
]

BAD_EXCLUSION_REASONS = {"", "n/a", "na", "no aplica", "no se toca", "no se toco", "luego vemos", "none", "null"}

FORBIDDEN_NARRATIVE_PATTERNS = [
    r"\bpc\s+manda\b",
    r"\bpc\s+es\s+requisito\s+para\s+vender\b",
    r"\btablet\s+depende\s+de\s+pc\b",
    r"\btablet\s+requiere\s+pc\s+para\s+vender\b",
    r"\bapp\s+m[oó]vil\s+es\s+requisito\s+para\s+vender\b",
    r"\bmobile\s+is\s+required\s+for\s+tablet\s+sales\b",
]

@dataclass
class Report:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.ok = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.info.append(message)


def normalize_rel(value: str) -> str:
    value = value.replace("\\", "/").strip()
    if not value:
        return value
    # Drop common ZIP payload prefixes without losing package paths.
    if value.startswith("files/"):
        value = value[len("files/"):]
    if value.startswith("./"):
        value = value[2:]
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or ":" in value:
        raise ValueError(f"Unsafe path: {value}")
    return str(pure)


def matches_any(path: str, patterns: list[str]) -> bool:
    path = normalize_rel(path)
    return any(fnmatch(path, pattern) for pattern in patterns)


def classify_path(path: str) -> set[str]:
    path = normalize_rel(path)
    classes: set[str] = set()
    if matches_any(path, TABLET_PATTERNS):
        classes.add(TABLET)
    if matches_any(path, MOBILE_PATTERNS) or matches_any(path, MOBILE_LEGACY_PATTERNS):
        classes.add(MOBILE)
    if matches_any(path, PC_PATTERNS) and MOBILE not in classes:
        classes.add(PC)
    if matches_any(path, SHARED_VISUAL_PATTERNS):
        classes.add("shared_visual")
    if matches_any(path, SHARED_GOVERNANCE_PATTERNS):
        classes.add("shared_governance")
    return classes


def load_json_file(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Could not read JSON manifest {path}: {exc}") from exc


def load_payload_manifest(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        raise RuntimeError(f"Payload ZIP not found: {path}")
    if not zipfile.is_zipfile(path):
        raise RuntimeError(f"Not a ZIP file: {path}")
    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        manifest_candidates = [
            "VISUAL_CHANGE_MANIFEST.json",
            "INSTALL_MANIFEST.json",
            "PAYLOAD_MANIFEST.json",
        ]
        manifest: dict[str, Any] | None = None
        for candidate in manifest_candidates:
            if candidate in names:
                manifest = json.loads(archive.read(candidate).decode("utf-8"))
                break
        if manifest is None:
            # Last chance: use first manifest-looking JSON at root.
            root_jsons = [n for n in names if "/" not in n.rstrip("/") and n.lower().endswith(".json")]
            for n in root_jsons:
                try:
                    data = json.loads(archive.read(n).decode("utf-8"))
                except Exception:
                    continue
                if "surfaceCoverage" in data or "visualChangeCoverage" in data:
                    manifest = data
                    break
        if manifest is None:
            raise RuntimeError("Payload ZIP does not contain a visual manifest with surfaceCoverage.")
        changed = [normalize_rel(n) for n in names if n.startswith("files/") and not n.endswith("/")]
        if not changed:
            changed = [normalize_rel(n) for n in names if not n.endswith("/") and not n.upper().endswith("MANIFEST.JSON")]
    return manifest, changed


def read_changed_files(path: Path) -> list[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        values.append(normalize_rel(line))
    return values


def coverage_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    value = manifest.get("surfaceCoverage")
    if value is None:
        value = manifest.get("visualChangeCoverage")
    if isinstance(value, dict):
        value = value.get("surfaces")
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def field_as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [normalize_rel(value)] if value.strip() else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(normalize_rel(item))
        return out
    return []


def merged_changed_files(manifest: dict[str, Any], extra_changed: list[str]) -> list[str]:
    changed: list[str] = []
    changed.extend(field_as_list(manifest.get("changedFiles")))
    for item in coverage_items(manifest):
        changed.extend(field_as_list(item.get("touchedFiles")))
    changed.extend(extra_changed)
    # Preserve order and uniqueness.
    seen: set[str] = set()
    result: list[str] = []
    for item in changed:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def validate_autonomy(manifest: dict[str, Any], report: Report) -> None:
    policy = manifest.get("autonomyPolicy") or manifest.get("autonomyInvariants") or {}
    if not isinstance(policy, dict):
        report.error("autonomyPolicy must be an object.")
        return
    for key in REQUIRED_AUTONOMY_TRUE:
        if policy.get(key) is not True:
            report.error(f"autonomyPolicy.{key} must be true.")

    # Optional text fields: catch the worst hierarchy claims in new manifests.
    text_blobs: list[str] = []
    for key in ["canonicalStatement", "summary", "description", "notes"]:
        value = manifest.get(key)
        if isinstance(value, str):
            text_blobs.append(value)
    for item in coverage_items(manifest):
        for key in ["evidence", "exclusionReason", "notes"]:
            value = item.get(key)
            if isinstance(value, str):
                text_blobs.append(value)
    combined = "\n".join(text_blobs).lower()
    for pattern in FORBIDDEN_NARRATIVE_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            report.error(f"Forbidden hierarchy/autonomy claim detected: {pattern}")


def validate_coverage(manifest: dict[str, Any], changed_files: list[str], report: Report) -> None:
    items = coverage_items(manifest)
    if not items:
        report.error("Missing surfaceCoverage array.")
        return

    by_surface: dict[str, dict[str, Any]] = {}
    for item in items:
        surface = str(item.get("surface", "")).strip()
        if not surface:
            report.error("A surfaceCoverage item is missing surface.")
            continue
        if surface in by_surface:
            report.error(f"Duplicate surfaceCoverage item: {surface}")
        by_surface[surface] = item

    for required in REQUIRED_SURFACES:
        if required not in by_surface:
            report.error(f"Missing required surface: {required}")

    for surface, item in by_surface.items():
        state = str(item.get("state", "")).strip().upper()
        if state in FORBIDDEN_STATES:
            report.error(f"Forbidden state {state} for {surface}.")
        if state not in ALLOWED_STATES:
            report.error(f"Invalid state {state or '<missing>'} for {surface}. Allowed: {sorted(ALLOWED_STATES)}")
        evidence = str(item.get("evidence", "")).strip()
        if not evidence:
            report.error(f"Missing evidence for {surface}.")
        owner = str(item.get("owner", "")).strip()
        if not owner:
            report.error(f"Missing owner for {surface}.")
        if state == "EXCLUDED":
            reason = str(item.get("exclusionReason", "")).strip()
            reevaluation = str(item.get("reevaluation", "")).strip()
            reason_key = reason.lower().strip(". ")
            if len(reason) < 18 or reason_key in BAD_EXCLUSION_REASONS:
                report.error(f"EXCLUDED surface {surface} needs a concrete exclusionReason.")
            if not reevaluation:
                report.error(f"EXCLUDED surface {surface} needs reevaluation.")

    changed_classes: dict[str, list[str]] = {TABLET: [], PC: [], MOBILE: [], "shared_visual": [], "shared_governance": [], "mobile_legacy": []}
    for path in changed_files:
        classes = classify_path(path)
        for cls in classes:
            changed_classes.setdefault(cls, []).append(path)
        if matches_any(path, MOBILE_LEGACY_PATTERNS):
            changed_classes["mobile_legacy"].append(path)

    def require_touched(surface: str, reason: str) -> None:
        item = by_surface.get(surface)
        if not item:
            return
        state = str(item.get("state", "")).strip().upper()
        if state != "TOUCHED":
            report.error(f"{surface} must be TOUCHED because {reason}.")

    if changed_classes[TABLET]:
        require_touched(TABLET, "Tablet paths changed: " + ", ".join(changed_classes[TABLET][:5]))
    if changed_classes[MOBILE]:
        require_touched(MOBILE, "App móvil/Pulso paths changed: " + ", ".join(changed_classes[MOBILE][:5]))
    if changed_classes[PC]:
        require_touched(PC, "PC paths changed: " + ", ".join(changed_classes[PC][:5]))

    if changed_classes["shared_visual"]:
        for surface in REQUIRED_SURFACES:
            item = by_surface.get(surface)
            if not item:
                continue
            state = str(item.get("state", "")).strip().upper()
            if state == "EXCLUDED":
                report.error(f"{surface} cannot be EXCLUDED because shared visual paths changed.")
            if state not in {"TOUCHED", "VALIDATED"}:
                report.error(f"{surface} must be TOUCHED or VALIDATED because shared visual paths changed.")
        report.note("Shared visual paths detected; all surfaces must be covered.")

    if changed_classes["shared_governance"]:
        report.note("Shared governance paths detected; coverage matrix is required.")

    if changed_classes["mobile_legacy"]:
        legacy_flag = manifest.get("legacyMobilePathsReviewed")
        if legacy_flag is not True:
            report.warn("Legacy /pulso mobile paths detected. Set legacyMobilePathsReviewed=true after review.")

    report.note(f"Changed/reviewed files considered: {len(changed_files)}")


def validate_manifest(manifest: dict[str, Any], changed_files: list[str]) -> Report:
    report = Report()
    package = manifest.get("package") or manifest.get("name") or "<unknown>"
    report.note(f"Package: {package}")
    change_type = str(manifest.get("changeType", "visual-governance"))
    report.note(f"Change type: {change_type}")
    validate_autonomy(manifest, report)
    validate_coverage(manifest, changed_files, report)
    return report


def print_text(report: Report) -> None:
    print("PRISMA tri-surface visual guardian 00B")
    print("Status:", "OK" if report.ok else "BLOCKED")
    if report.info:
        print("Info:")
        for item in report.info:
            print(f"- {item}")
    if report.warnings:
        print("Warnings:")
        for item in report.warnings:
            print(f"- {item}")
    if report.errors:
        print("Errors:")
        for item in report.errors:
            print(f"- {item}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate PRISMA visual manifests against tri-surface/autonomy rules.")
    parser.add_argument("--root", default=".", help="PRISMA target root. Used to resolve relative --manifest or --changed-files paths.")
    parser.add_argument("--manifest", help="Visual manifest JSON to validate.")
    parser.add_argument("--changed-files", help="Text file with one changed/reviewed path per line.")
    parser.add_argument("--payload", help="Payload ZIP containing a visual manifest and files.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report JSON.")
    parser.add_argument("--text", action="store_true", help="Print human-readable report. Default when --json is not set.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    extra_changed: list[str] = []

    try:
        if args.payload:
            manifest, payload_changed = load_payload_manifest(Path(args.payload))
            extra_changed.extend(payload_changed)
        elif args.manifest:
            manifest_path = Path(args.manifest)
            if not manifest_path.is_absolute():
                candidate = root / manifest_path
                manifest_path = candidate if candidate.exists() else Path(args.manifest)
            manifest = load_json_file(manifest_path)
        else:
            raise RuntimeError("Provide --manifest or --payload.")

        if args.changed_files:
            changed_path = Path(args.changed_files)
            if not changed_path.is_absolute():
                candidate = root / changed_path
                changed_path = candidate if candidate.exists() else Path(args.changed_files)
            extra_changed.extend(read_changed_files(changed_path))

        changed = merged_changed_files(manifest, extra_changed)
        report = validate_manifest(manifest, changed)
    except Exception as exc:  # noqa: BLE001
        report = Report(ok=False)
        report.error(str(exc))

    if args.json:
        print(json.dumps({"ok": report.ok, "info": report.info, "warnings": report.warnings, "errors": report.errors}, indent=2, ensure_ascii=False))
    else:
        print_text(report)
    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
