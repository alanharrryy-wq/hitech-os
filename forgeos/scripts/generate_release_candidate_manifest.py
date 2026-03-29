from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


FORGEOS_ROOT = Path(__file__).resolve().parents[1]


def collect_package_records(root: Path) -> list[dict[str, object]]:
    manifests = sorted((root / "packages").rglob("PACKAGE_MANIFEST.json"))
    records: list[dict[str, object]] = []
    for manifest_path in manifests:
        package_dir = manifest_path.parent
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        records.append(
            {
                "package_id": raw.get("package_id"),
                "layer": raw.get("layer"),
                "owner": raw.get("owner"),
                "version": raw.get("version"),
                "required_kernel_range": raw.get("required_kernel_range"),
                "integrity_hash": raw.get("integrity_hash"),
                "source_anchor": raw.get("source_anchor"),
                "compatibility": raw.get("compatibility"),
                "manifest_path": str(manifest_path),
                "bom_path": str(package_dir / "BOM.md"),
                "release_notes_path": str(package_dir / "RELEASE_NOTES.md"),
                "rollback_plan_path": str(package_dir / "ROLLBACK_PLAN.md"),
            }
        )
    records.sort(key=lambda item: str(item.get("package_id", "")))
    return records


def write_manifest(
    output_path: Path,
    records: list[dict[str, object]],
    git_sha: str,
    rc_label: str,
    kernel_version: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "PASS" if records else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha,
        "rc_label": rc_label,
        "kernel_version": kernel_version,
        "package_count": len(records),
        "packages": records,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ForgeOS release candidate manifest.")
    parser.add_argument("--root", default=str(FORGEOS_ROOT))
    parser.add_argument(
        "--output",
        default=str(
            FORGEOS_ROOT.parent / "tools" / "_local" / "evidence" / "forgeos_release_candidate_manifest.json"
        ),
    )
    parser.add_argument("--git-sha", default="unknown")
    parser.add_argument("--rc-label", default="manual")
    parser.add_argument("--kernel-version", default="0.1.0")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_path = Path(args.output).resolve()
    records = collect_package_records(root=root)
    write_manifest(
        output_path=output_path,
        records=records,
        git_sha=str(args.git_sha),
        rc_label=str(args.rc_label),
        kernel_version=str(args.kernel_version),
    )

    if not records:
        print("[ForgeOS] Release candidate manifest generation FAILED: no package manifests found.")
        print(f"[ForgeOS] Output: {output_path}")
        return 1

    print(f"[ForgeOS] Release candidate manifest generated for {len(records)} package(s).")
    print(f"[ForgeOS] Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

