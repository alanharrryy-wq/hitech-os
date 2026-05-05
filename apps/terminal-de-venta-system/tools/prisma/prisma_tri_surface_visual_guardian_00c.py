#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CANONICAL_SURFACE_IDS = {
    "prisma.pc.backoffice",
    "prisma.tablet.pos",
    "prisma.mobile.app",
}
VALID_STATES = {"TOUCHED", "VALIDATED", "EXCLUDED"}
FORBIDDEN_PHRASES = [
    "PC gobierna",
    "Tablet depende de PC",
    "Mobile es parte de PC",
    "App móvil es hija de PC",
]

PATH_PREFIXES = {
    "prisma.pc.backoffice": ["products/pc/app/"],
    "prisma.tablet.pos": ["products/tablet/app/"],
    "prisma.mobile.app": ["products/mobile/app/"],
}
LEGACY_MOBILE_PREFIXES = [
    "products/pc/app/app/prisma-app/",
    "products/pc/app/src/lib/prisma-app/",
    "products/pc/app/docs/prisma-app/",
    "products/pc/app/app/pulso/",
    "products/pc/app/src/lib/pulso/",
]
SHARED_VISUAL_PREFIXES = [
    "products/shared-ui/prisma/tokens/",
    "products/shared-ui/prisma/components/",
    "shared/contracts/ui/",
    "docs/design/",
    "docs/qa/",
    "tools/prisma/",
    "manifests/",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_files(value) -> list[str]:
    if not value:
        return []
    if not isinstance(value, list):
        return []
    return [str(x).replace("\\", "/") for x in value]


def classify_changed_file(path: str) -> set[str]:
    out = set()
    p = path.replace("\\", "/")
    for prefix in LEGACY_MOBILE_PREFIXES:
        if p.startswith(prefix):
            out.add("prisma.mobile.app")
            return out
    for sid, prefixes in PATH_PREFIXES.items():
        for prefix in prefixes:
            if p.startswith(prefix):
                out.add(sid)
    if any(p.startswith(prefix) for prefix in SHARED_VISUAL_PREFIXES):
        out.update(CANONICAL_SURFACE_IDS)
    return out


def validate_manifest(manifest: dict) -> list[str]:
    failures: list[str] = []
    coverage = manifest.get("surfaceCoverage")
    if not isinstance(coverage, list):
        return ["surfaceCoverage must be a list"]

    by_id = {}
    for item in coverage:
        sid = item.get("surfaceId")
        if sid in by_id:
            failures.append(f"duplicate surface coverage: {sid}")
        by_id[sid] = item
        if sid not in CANONICAL_SURFACE_IDS:
            failures.append(f"invalid surfaceId: {sid}")
        state = item.get("state")
        if state == "OMITTED":
            failures.append(f"surface {sid} uses forbidden state OMITTED")
        if state not in VALID_STATES:
            failures.append(f"surface {sid} has invalid state: {state}")
        touched = normalize_files(item.get("touchedFiles"))
        reviewed = normalize_files(item.get("reviewedFiles"))
        evidence = str(item.get("evidence") or "").strip()
        if not evidence:
            failures.append(f"surface {sid} missing evidence")
        if state == "TOUCHED" and not touched:
            failures.append(f"surface {sid} is TOUCHED but touchedFiles is empty")
        if state == "VALIDATED" and not reviewed and not evidence:
            failures.append(f"surface {sid} is VALIDATED but lacks reviewedFiles/evidence")
        if state == "EXCLUDED":
            exclusion = item.get("exclusion")
            if not isinstance(exclusion, dict):
                failures.append(f"surface {sid} is EXCLUDED but exclusion object is missing")
            else:
                if not str(exclusion.get("reason") or "").strip():
                    failures.append(f"surface {sid} exclusion missing reason")
                if exclusion.get("noSharedImpact") is not True:
                    failures.append(f"surface {sid} exclusion must confirm noSharedImpact=true")
                if not str(exclusion.get("reevaluateIn") or "").strip():
                    failures.append(f"surface {sid} exclusion missing reevaluateIn")
                if not str(exclusion.get("owner") or "").strip():
                    failures.append(f"surface {sid} exclusion missing owner")

    missing = CANONICAL_SURFACE_IDS - set(by_id)
    for sid in sorted(missing):
        failures.append(f"missing required surface coverage: {sid}")

    changed_files = set(normalize_files(manifest.get("changedFiles")))
    for item in coverage:
        changed_files.update(normalize_files(item.get("touchedFiles")))

    required_touched: set[str] = set()
    for path in changed_files:
        required_touched.update(classify_changed_file(path))

    for sid in sorted(required_touched):
        state = (by_id.get(sid) or {}).get("state")
        if state != "TOUCHED":
            failures.append(f"changed/touched files require {sid}=TOUCHED, got {state}")

    # reviewedFiles are evidence only. They intentionally do not force TOUCHED.
    return failures


def scan_language(root: Path, scan_roots: list[str]) -> list[str]:
    failures = []
    for rel in scan_roots:
        base = root / rel
        if not base.exists():
            continue
        files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".ts", ".tsx", ".json"}]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    failures.append(f"forbidden phrase '{phrase}' in {path.relative_to(root)}")
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="PRISMA tri-surface visual guardian 00C")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--scan-root", action="append", default=[])
    args = parser.parse_args(argv)

    failures = validate_manifest(load_json(args.manifest))
    if args.root and args.scan_root:
        failures.extend(scan_language(args.root, args.scan_root))

    if failures:
        print("PRISMA tri-surface visual guardian 00C failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("VERIFY OK. PRISMA tri-surface visual guardian 00C passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
