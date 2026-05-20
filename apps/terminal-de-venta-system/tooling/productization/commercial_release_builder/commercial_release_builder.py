from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

TABLET_SOLO_POLICY = {
    "tabletMaySellWithoutPc": True,
    "tabletMaySellWithoutInternet": True,
    "tabletMaySellWithoutMobile": True,
    "pcRequiredForSales": False,
    "mobileRequiredForSales": False,
    "remoteCareRequiredForSales": False,
    "cloudRequiredForSales": False,
    "canonicalDbRequiredForSales": False,
}

DEFAULT_VERSION = "1.0.0-pilot.1"
DEFAULT_CLIENT_ID = "pilot-001"
DEFAULT_BRANCH_ID = "matriz-001"

DENY_DIRS = {
    ".git", "node_modules", ".next", ".turbo", ".cache", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", ".prisma_installer_backups",
    ".prisma_tree_backups",
}

DENY_PATH_PARTS = {
    "tools/prisma-salvage",
    "products/chart-lab/app/out",
    "tablet-pc-required",
    "tablet_pc_required",
    "TABLET_PC_REQUIRED",
}

DENY_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development", ".npmrc",
    "pnpm-lock.yaml", "package-lock.json",
    "tablet-pc-required.active.license.json",
    "tablet-pc-required.active.signed.license.json",
}

DENY_SUFFIXES = {
    ".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm", ".log",
    ".pem", ".key", ".pfx", ".p12", ".bak", ".dump",
}

PACKAGE_SOURCES = {
    "tablet": ["products/tablet/app", "shared", "tooling/productization/schemas", "tooling/productization/examples/license-local"],
    "pc": ["products/pc/app", "shared", "tooling/productization/schemas"],
    "mobile": ["products/mobile/app", "shared", "tooling/productization/schemas"],
    "remote-care": ["tooling/productization", "docs/productization"],
    "config": ["tooling/productization/examples", "tooling/productization/schemas", "docs/productization"],
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 512), b""):
            h.update(chunk)
    return h.hexdigest()


def zip_dir(source_dir: Path, dest_zip: Path) -> None:
    if dest_zip.exists():
        dest_zip.unlink()
    with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(source_dir).as_posix())


def normalized(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def should_exclude(path: Path, repo_root: Path) -> Tuple[bool, Optional[str]]:
    rel = normalized(path.relative_to(repo_root)) if path.is_absolute() else normalized(path)
    lower = rel.lower()
    name = path.name.lower()

    if any(part.lower() in DENY_DIRS for part in path.parts):
        return True, "deny_dir"
    for deny_part in DENY_PATH_PARTS:
        if deny_part.lower() in lower:
            return True, "deny_path_part"
    if name in DENY_NAMES:
        return True, "deny_name"
    if path.suffix.lower() in DENY_SUFFIXES:
        return True, "deny_suffix"
    if "secret" in name or "token" in name or "password" in name or "credential" in name:
        return True, "sensitive_name"
    return False, None


def iter_package_files(repo_root: Path, source_rels: List[str]) -> Iterable[Tuple[Path, Path]]:
    seen = set()
    for source_rel in source_rels:
        source_root = repo_root / source_rel
        if not source_root.exists():
            continue
        for current, dirs, files in os.walk(source_root):
            current_path = Path(current)
            dirs[:] = [d for d in dirs if d not in DENY_DIRS]
            for filename in files:
                path = current_path / filename
                excluded, _reason = should_exclude(path, repo_root)
                if excluded:
                    continue
                rel = path.relative_to(repo_root)
                key = normalized(rel)
                if key in seen:
                    continue
                seen.add(key)
                yield path, rel


def copy_package_payload(repo_root: Path, staging_dir: Path, package_name: str, source_rels: List[str]) -> Dict[str, Any]:
    payload_dir = staging_dir / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    files = []
    source_notes = []
    for source_rel in source_rels:
        source_root = repo_root / source_rel
        if not source_root.exists():
            source_notes.append({"source": source_rel, "reason": "source_missing"})
    for source_path, rel in iter_package_files(repo_root, source_rels):
        dest = payload_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest)
        files.append({"path": normalized(rel), "bytes": source_path.stat().st_size, "sha256": sha256_file(source_path)})
    return {"package": package_name, "file_count": len(files), "files": files, "source_notes": source_notes}


def make_release_manifest(version: str, channel: str, generated_at: str) -> Dict[str, Any]:
    return {
        "product": "PRISMA Commerce",
        "releaseVersion": version,
        "channel": channel,
        "generatedAt": generated_at,
        "packages": {
            "tablet": {"required": True, "role": "sales-local-first"},
            "pc": {"required": False, "role": "optional-backoffice-governance"},
            "mobile": {"required": False, "role": "supervision-only"},
            "remoteCare": {"required": False, "role": "support-evidence-only"},
            "config": {"required": True, "role": "client-branch-device-configuration"},
        },
        "tabletSoloPolicy": TABLET_SOLO_POLICY,
        "commercialExclusions": {"noRepo": True, "noGit": True, "noNodeModules": True, "noEnv": True, "noRawDb": True, "noRawLogs": True, "noSecrets": True},
    }


def make_client_manifest(client_id: str, branch_id: str, version: str, generated_at: str) -> Dict[str, Any]:
    return {
        "clientId": client_id,
        "branchId": branch_id,
        "environment": "pilot-paid",
        "releaseVersion": version,
        "generatedAt": generated_at,
        "devices": [
            {"deviceId": "tablet-001", "role": "tablet", "requiredForSales": True, "canSellOffline": True, "requiresPc": False, "requiresInternet": False, "requiresMobile": False},
            {"deviceId": "pc-001", "role": "pc-backoffice", "requiredForSales": False, "canGovern": True},
            {"deviceId": "mobile-001", "role": "mobile-supervisor", "requiredForSales": False, "canSell": False},
        ],
        "policies": TABLET_SOLO_POLICY,
    }


def make_install_plan(package_name: str) -> Dict[str, Any]:
    base = "C:\\ProgramData\\PRISMA\\Commerce"
    role_root = {"tablet": "Tablet", "pc": "PC", "mobile": "Mobile", "remote-care": "RemoteCare", "config": "Config"}.get(package_name, package_name)
    return {
        "package": package_name,
        "mode": "assisted-pilot-install",
        "targetRoot": f"{base}\\{role_root}",
        "steps": ["preflight", "backup-existing", "copy-payload", "write-manifests", "healthcheck", "evidence-export"],
        "rollbackRequired": True,
        "tabletSoloPolicyMustRemain": TABLET_SOLO_POLICY,
    }


def validate_zip_contents(zip_path: Path) -> List[Dict[str, str]]:
    errors = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            lower = member.lower()
            if "/.git/" in lower or lower.startswith(".git/"):
                errors.append({"member": member, "reason": "git included"})
            if "node_modules/" in lower:
                errors.append({"member": member, "reason": "node_modules included"})
            if lower.endswith(".env") or "/.env" in lower:
                errors.append({"member": member, "reason": "env included"})
            if any(lower.endswith(suffix) for suffix in DENY_SUFFIXES):
                errors.append({"member": member, "reason": "denied suffix included"})
            if "tablet_pc_required" in lower or "tablet-pc-required" in lower:
                errors.append({"member": member, "reason": "old required naming included"})
    return errors


def build_release(repo_root: Path, out_root: Path, version: str, client_id: str, branch_id: str, channel: str) -> Dict[str, Any]:
    generated_at = now_iso()
    safe_stamp = generated_at.replace(":", "").replace("-", "").replace(".", "")
    release_root = out_root / f"PRISMA-Commerce-{version}-{client_id}-{branch_id}"
    work_root = out_root / f"_work_PRISMA-Commerce-{version}-{client_id}-{branch_id}-{safe_stamp}"
    packages_root = release_root / "packages"
    manifests_root = release_root / "manifests"
    evidence_root = release_root / "evidence"

    if release_root.exists():
        shutil.rmtree(release_root)
    if work_root.exists():
        shutil.rmtree(work_root)

    for folder in (packages_root, manifests_root, evidence_root, work_root):
        folder.mkdir(parents=True, exist_ok=True)

    release_manifest = make_release_manifest(version, channel, generated_at)
    client_manifest = make_client_manifest(client_id, branch_id, version, generated_at)
    write_json(manifests_root / "manifest.release.json", release_manifest)
    write_json(manifests_root / "manifest.client.json", client_manifest)

    package_results = []
    validation_errors = []

    for package_name, source_rels in PACKAGE_SOURCES.items():
        package_staging = work_root / package_name
        package_staging.mkdir(parents=True, exist_ok=True)
        payload_result = copy_package_payload(repo_root, package_staging, package_name, source_rels)
        write_json(package_staging / "manifest.release.json", release_manifest)
        write_json(package_staging / "manifest.client.json", client_manifest)
        write_json(package_staging / "install-plan.json", make_install_plan(package_name))
        write_json(package_staging / "healthcheck-profile.json", {"package": package_name, "checks": ["payload-present", "manifest-present", "no-denied-files", "tablet-solo-policy-present"]})
        write_json(package_staging / "rollback-plan.json", {"package": package_name, "rollback": "restore-previous-package-and-data-backup", "dataDestructive": False})
        write_json(package_staging / "package-index.json", payload_result)
        zip_name = f"PRISMA-Commerce-{package_name}-{version}-{client_id}-{branch_id}.zip"
        zip_path = packages_root / zip_name
        zip_dir(package_staging, zip_path)
        zip_errors = validate_zip_contents(zip_path)
        validation_errors.extend([{"package": package_name, **error} for error in zip_errors])
        package_results.append({"package": package_name, "zip": str(zip_path), "sha256": sha256_file(zip_path), "bytes": zip_path.stat().st_size, "file_count": payload_result["file_count"], "source_notes": payload_result["source_notes"], "validation_errors": zip_errors})

    checksums = {Path(item["zip"]).name: item["sha256"] for item in package_results}
    write_json(manifests_root / "checksums.sha256.json", checksums)

    result_without_final = {
        "status": "PASS" if not validation_errors else "FAIL_VALIDATION",
        "generatedAt": generated_at,
        "releaseRoot": str(release_root),
        "packageResults": package_results,
        "validationErrors": validation_errors,
        "tabletSoloPolicy": TABLET_SOLO_POLICY,
    }
    write_json(evidence_root / "commercial-release-builder-result.json", result_without_final)

    final_release_zip = out_root / f"PRISMA-Commerce-Commercial-Release-{version}-{client_id}-{branch_id}.zip"
    zip_dir(release_root, final_release_zip)
    final_errors = validate_zip_contents(final_release_zip)
    validation_errors.extend([{"package": "final-release", **error} for error in final_errors])

    result = {
        "status": "PASS" if not validation_errors else "FAIL_VALIDATION",
        "generatedAt": generated_at,
        "releaseRoot": str(release_root),
        "finalReleaseZip": str(final_release_zip),
        "finalReleaseSha256": sha256_file(final_release_zip),
        "finalReleaseBytes": final_release_zip.stat().st_size,
        "packageResults": package_results,
        "validationErrors": validation_errors,
        "tabletSoloPolicy": TABLET_SOLO_POLICY,
    }
    write_json(evidence_root / "commercial-release-builder-result.json", result)
    shutil.rmtree(work_root, ignore_errors=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA Commercial Release Builder 01 Fixed")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_ID)
    parser.add_argument("--branch-id", default=DEFAULT_BRANCH_ID)
    parser.add_argument("--channel", default="pilot-paid")
    args = parser.parse_args()
    repo_root = Path(args.repo_root)
    out_root = Path(args.out_root)
    if not repo_root.exists():
        raise FileNotFoundError(f"Repo root not found: {repo_root}")
    out_root.mkdir(parents=True, exist_ok=True)
    result = build_release(repo_root, out_root, args.version, args.client_id, args.branch_id, args.channel)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
