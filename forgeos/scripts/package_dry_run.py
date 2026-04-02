from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


FORGEOS_ROOT = Path(__file__).resolve().parents[1]
KERNEL_SRC = FORGEOS_ROOT / "platform" / "forge_kernel" / "src"
if str(KERNEL_SRC) not in sys.path:
    sys.path.insert(0, str(KERNEL_SRC))

from forge_kernel import (  # noqa: E402
    PackageLayer,
    PackageManifest,
    PackagingGate,
    compute_integrity_hash,
)


@dataclass(frozen=True)
class PackageResult:
    package_id: str
    manifest_path: str
    status: str
    reasons: tuple[str, ...]


def dry_run_package(manifest_path: Path, root: Path, kernel_version: str) -> PackageResult:
    package_dir = manifest_path.parent
    reasons: list[str] = []
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    package_id = str(raw.get("package_id", "unknown"))

    for required_file in ("BOM.md", "ROLLBACK_PLAN.md", "RELEASE_NOTES.md"):
        if not (package_dir / required_file).exists():
            reasons.append(f"missing {required_file}")

    source_anchor_raw = raw.get("source_anchor")
    if not source_anchor_raw:
        reasons.append("missing source_anchor")
        source_anchor = None
    else:
        source_anchor = (root / str(source_anchor_raw)).resolve()
        if not source_anchor.exists():
            reasons.append(f"source_anchor not found: {source_anchor}")

    manifest = None
    try:
        manifest = PackageManifest(
            package_id=package_id,
            layer=PackageLayer(str(raw["layer"])),
            owner=str(raw["owner"]),
            version=str(raw["version"]),
            required_kernel_range=str(raw["required_kernel_range"]),
            integrity_hash=str(raw["integrity_hash"]),
        )
    except Exception as exc:  # noqa: BLE001
        reasons.append(f"invalid package manifest fields: {exc}")

    compatibility = raw.get("compatibility")
    if not isinstance(compatibility, dict):
        reasons.append("missing compatibility block")
    else:
        if "kernel" not in compatibility:
            reasons.append("compatibility.kernel is required")
        if "commons" not in compatibility:
            reasons.append("compatibility.commons is required")

    if manifest is not None and source_anchor is not None and source_anchor.exists():
        verified_hash = compute_integrity_hash(source_anchor)
        gate = PackagingGate()
        result = gate.validate(
            manifest=manifest,
            kernel_version=kernel_version,
            verified_integrity_hash=verified_hash,
        )
        if not result.approved:
            reasons.extend(result.reasons)

    status = "PASS" if not reasons else "FAIL"
    return PackageResult(
        package_id=package_id,
        manifest_path=str(manifest_path),
        status=status,
        reasons=tuple(reasons),
    )


def run_dry_run(root: Path, kernel_version: str) -> list[PackageResult]:
    package_manifests = sorted((root / "packages").rglob("PACKAGE_MANIFEST.json"))
    return [
        dry_run_package(
            manifest_path=manifest_path,
            root=root,
            kernel_version=kernel_version,
        )
        for manifest_path in package_manifests
    ]


def write_report(report_path: Path, results: list[PackageResult]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    failures = [result for result in results if result.status != "PASS"]
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "package_count": len(results),
        "failure_count": len(failures),
        "results": [
            {
                "package_id": result.package_id,
                "manifest_path": result.manifest_path,
                "status": result.status,
                "reasons": list(result.reasons),
            }
            for result in results
        ],
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ForgeOS package dry-run validation.")
    parser.add_argument("--root", default=str(FORGEOS_ROOT))
    parser.add_argument("--kernel-version", default="0.1.0")
    parser.add_argument(
        "--report",
        default=str(FORGEOS_ROOT.parent / "tools" / "_local" / "evidence" / "forgeos_package_dry_run_report.json"),
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve()
    results = run_dry_run(root=root, kernel_version=args.kernel_version)
    write_report(report_path=report_path, results=results)

    failures = [result for result in results if result.status != "PASS"]
    if failures:
        print(
            f"[ForgeOS] Package dry-run FAILED for {len(failures)} of {len(results)} package(s)."
        )
        for failure in failures:
            print(f"- {failure.package_id}: {'; '.join(failure.reasons)}")
        print(f"[ForgeOS] Report: {report_path}")
        return 1

    print(f"[ForgeOS] Package dry-run PASSED for {len(results)} package(s).")
    print(f"[ForgeOS] Report: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
