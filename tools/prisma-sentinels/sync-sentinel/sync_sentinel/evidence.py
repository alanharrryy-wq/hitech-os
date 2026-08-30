from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .fixtures import fixture_matrix_csv, load_fixture_registry
from .safety import sanitize_text, scan_secrets_text


FAULT_ZONE_HINTS = (
    ("license", "LICENSE"),
    ("origin", "TABLET_ORIGIN"),
    ("outbox", "TABLET_OUTBOX"),
    ("dispatcher", "TABLET_DISPATCHER"),
    ("network", "NETWORK"),
    ("bridge", "NETWORK"),
    ("ingest", "PC_INGEST"),
    ("payload", "CONTRACT_VALIDATION"),
    ("checksum", "CONTRACT_VALIDATION"),
    ("scope", "SCOPE"),
    ("idempot", "IDEMPOTENCY"),
    ("project", "PC_PROJECTION"),
    ("ack", "ACK"),
    ("reconcil", "TABLET_RECONCILIATION"),
    ("catalog_export", "PC_CATALOG_EXPORT"),
    ("catalog_pull", "TABLET_CATALOG_PULL"),
    ("checkpoint", "CHECKPOINT"),
    ("drift", "DATA_DRIFT"),
    ("dependency", "CONFIG"),
    ("prisma", "CONFIG"),
    ("toolchain", "CONFIG"),
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n")


def _fault_zone(check: dict[str, Any]) -> str:
    haystack = (str(check.get("id", "")) + " " + str(check.get("detail", ""))).lower()
    for needle, zone in FAULT_ZONE_HINTS:
        if needle in haystack:
            return zone
    return "UNKNOWN"


def _matrix_csv(checks: list[dict[str, Any]]) -> str:
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["checkId", "verdict", "faultZone", "detail"])
    for check in checks:
        writer.writerow([
            check.get("id", ""),
            check.get("verdict", "UNKNOWN"),
            _fault_zone(check),
            check.get("detail", ""),
        ])
    return out.getvalue()


def _failure_localization(report: dict[str, Any]) -> dict[str, Any]:
    failures = []
    for check in report.get("checks", []):
        if check.get("verdict") in {"FAIL", "BLOCKED", "UNKNOWN"}:
            failures.append({
                "checkId": check.get("id"),
                "verdict": check.get("verdict"),
                "faultZone": _fault_zone(check),
                "detail": check.get("detail"),
            })
    return {
        "schemaVersion": "prisma.sync-sentinel.failure-localization.v1",
        "status": "CLEAR" if not failures else "LOCALIZED_FAILURES_PRESENT",
        "failures": failures,
        "unknownCount": sum(1 for item in failures if item["faultZone"] == "UNKNOWN"),
    }


def _timeline(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "prisma.sync-sentinel.timeline.v1",
        "generatedAt": report.get("generatedAt"),
        "events": [
            {
                "sequence": index + 1,
                "checkId": check.get("id"),
                "verdict": check.get("verdict"),
                "detail": check.get("detail"),
            }
            for index, check in enumerate(report.get("checks", []))
        ],
    }


def _contracts(report: dict[str, Any]) -> dict[str, Any]:
    facts = report.get("facts") or {}
    return {
        "schemaVersion": "prisma.sync-sentinel.contracts.v1",
        "runtimeRegistry": "contracts/runtime-registry.v1.json",
        "fixtureRegistry": "fixtures/registry.v1.json",
        "productionCertified": False,
        "mandatoryUnknownMayPass": False,
        "liveDatabaseMutationAllowed": False,
        "businessLogicReimplementationAllowed": False,
        "sourceHead": report.get("repoHead") or facts.get("repoHead"),
    }


def _environment(report: dict[str, Any]) -> dict[str, Any]:
    facts = report.get("facts") or {}
    sandbox = facts.get("sandboxManifest") or {}
    dependencies = facts.get("dependencyResolution") or sandbox.get("dependencyResolution") or {}
    return {
        "schemaVersion": "prisma.sync-sentinel.environment.v1",
        "repoHead": report.get("repoHead") or facts.get("repoHead"),
        "repoTree": facts.get("repoTree"),
        "dependencyResolution": dependencies,
        "sandboxOwnership": sandbox.get("ownership"),
        "sandboxGuards": sandbox.get("guards"),
        "liveDbTouched": report.get("liveDbTouched", False),
        "productionCertified": False,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# PRISMA Sync Sentinel Evidence",
        "",
        f"- status: **{report.get('status', report.get('verdict', 'UNKNOWN'))}**",
        f"- generatedAt: `{report.get('generatedAt', '')}`",
        f"- repoHead: `{report.get('repoHead', '')}`",
        f"- liveDbTouched: `{str(report.get('liveDbTouched')).lower()}`",
        f"- sourceDrift: `{str(report.get('sourceDrift')).lower()}`",
        f"- cleanupPass: `{str(report.get('cleanupPass')).lower()}`",
        f"- orphanProcesses: `{str(report.get('orphanProcesses')).lower()}`",
        f"- secretFindings: `{report.get('secretFindings', 0)}`",
        f"- productionCertified: `{str(report.get('productionCertified', False)).lower()}`",
        "",
        "## Checks",
        "",
    ]
    for check in report.get("checks", []):
        lines.append(f"- **{check.get('id')}**: `{check.get('verdict')}` · {check.get('detail')}")
    lines.extend([
        "",
        "## Scope statement",
        "",
        "This bundle certifies only the exact isolated synthetic runtime/source evidence named in the bundle. It does not certify hosted/customer production operation.",
        "",
    ])
    return "\n".join(lines)


def _continuation(report: dict[str, Any], localization: dict[str, Any]) -> str:
    failures = localization.get("failures", [])
    next_step = "No failing mandatory assertion remains in this run." if not failures else (
        "Resume from the first failing check: " + str(failures[0].get("checkId")) +
        " in fault zone " + str(failures[0].get("faultZone")) + "."
    )
    return "\n".join([
        "# PRISMA Sync Sentinel Continuation",
        "",
        f"- status: `{report.get('status', report.get('verdict', 'UNKNOWN'))}`",
        f"- repoHead: `{report.get('repoHead', '')}`",
        f"- productionCertified: `false`",
        "",
        next_step,
        "",
        "Do not reinterpret UNKNOWN, BLOCKED or FAIL as PASS. Re-run against the exact source HEAD after any source or dependency drift.",
        "",
    ])


def build_bundle(out_dir: Path, report: dict[str, Any], extra_files: list[Path] | None = None) -> tuple[Path, int, list[str]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = dict(report)
    report.setdefault("generatedAt", now_iso())
    report.setdefault("productionCertified", False)
    checks = list(report.get("checks", []))
    localization = _failure_localization(report)

    generated: list[Path] = []
    def add_json(name: str, value: Any) -> None:
        path = out_dir / name
        atomic_write_json(path, value)
        generated.append(path)
    def add_text(name: str, value: str) -> None:
        path = out_dir / name
        atomic_write_text(path, value)
        generated.append(path)

    # Legacy pair retained for downstream compatibility.
    add_json("SYNC_SENTINEL_REPORT.json", report)
    add_text("SYNC_SENTINEL_REPORT.md", render_markdown(report))

    add_json("SYNC_SUMMARY.json", report)
    add_text("SYNC_MATRIX.csv", _matrix_csv(checks))
    add_json("SYNC_FAILURE_LOCALIZATION.json", localization)
    add_json("SYNC_TIMELINE.json", _timeline(report))
    add_json("SYNC_ASSERTIONS.json", {"schemaVersion": "prisma.sync-sentinel.assertions.v1", "checks": checks})
    add_json("SYNC_ENVIRONMENT_SANITIZED.json", _environment(report))
    add_json("SYNC_CONTRACTS.json", _contracts(report))
    add_text("CONTINUATION.md", _continuation(report, localization))

    facts = report.get("facts") or {}
    sandbox = facts.get("sandboxManifest")
    dependencies = facts.get("dependencyResolution") or (sandbox or {}).get("dependencyResolution")
    if sandbox:
        add_json("SYNC_SANDBOX_MANIFEST.json", sandbox)
    if dependencies:
        add_json("SYNC_DEPENDENCY_RESOLUTION.json", dependencies)

    try:
        fixture_registry = load_fixture_registry()
        add_text("SYNC_FIXTURE_MATRIX.csv", fixture_matrix_csv(fixture_registry))
    except Exception as exc:
        add_text("SYNC_FIXTURE_MATRIX.csv", "fixtureId,direction,topic,kind,expectedOutcome,expectedFaultZone,implemented,mandatoryAssertions\n")
        report.setdefault("warnings", []).append(f"fixture_registry_evidence:{type(exc).__name__}")

    if report.get("mode") == "certify" or "CERTIFICATION" in str(report.get("status", "")):
        add_json("SYNC_CERTIFICATION.json", report)

    for p in extra_files or []:
        if p.is_file() and p not in generated:
            generated.append(p)

    roles = {
        "SYNC_SUMMARY.json": "run summary",
        "SYNC_MATRIX.csv": "check matrix",
        "SYNC_FAILURE_LOCALIZATION.json": "causal localization",
        "SYNC_TIMELINE.json": "ordered assertions",
        "SYNC_ASSERTIONS.json": "assertion evidence",
        "SYNC_ENVIRONMENT_SANITIZED.json": "sanitized runtime environment",
        "SYNC_CONTRACTS.json": "certification boundaries",
        "SYNC_SANDBOX_MANIFEST.json": "isolated capsule ownership and cleanup",
        "SYNC_DEPENDENCY_RESOLUTION.json": "declared/resolved dependency proof",
        "SYNC_FIXTURE_MATRIX.csv": "versioned fixture coverage",
        "SYNC_CERTIFICATION.json": "final certification decision",
        "CONTINUATION.md": "fail-closed continuation",
    }
    index = {
        "schemaVersion": "prisma.sync-sentinel.evidence-index.v1",
        "createdAt": now_iso(),
        "productionCertified": False,
        "files": [{"name": p.name, "role": roles.get(p.name, "supporting evidence")} for p in generated],
    }
    index_path = out_dir / "SYNC_EVIDENCE_INDEX.json"
    atomic_write_json(index_path, index)
    generated.append(index_path)

    sanitized_findings: list[str] = []
    text_suffixes = {".json", ".md", ".txt", ".log", ".csv"}
    for p in generated:
        if p.suffix.lower() in text_suffixes:
            text = p.read_text(encoding="utf-8", errors="replace")
            local_findings = scan_secrets_text(text)
            if local_findings:
                sanitized_findings.extend(f"{p.name}:{item}" for item in local_findings)
                atomic_write_text(p, sanitize_text(text))

    remaining_findings: list[str] = []
    for p in generated:
        if p.suffix.lower() in text_suffixes:
            for item in scan_secrets_text(p.read_text(encoding="utf-8", errors="replace")):
                remaining_findings.append(f"{p.name}:{item}")

    manifest = {
        "schemaVersion": "prisma.sync-sentinel.evidence.v2",
        "createdAt": now_iso(),
        "sanitizedFindingCount": len(sanitized_findings),
        "remainingSecretFindings": len(remaining_findings),
        "productionCertified": False,
        "files": [],
    }
    for p in generated:
        raw = p.read_bytes()
        manifest["files"].append({"name": p.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    manifest_path = out_dir / "SYNC_SENTINEL_MANIFEST.json"
    atomic_write_json(manifest_path, manifest)
    generated.append(manifest_path)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    final_zip = out_dir / f"SYNC_SENTINEL_EVIDENCE_{stamp}.zip"
    tmp_zip = out_dir / (final_zip.name + ".tmp")
    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in generated:
            zf.write(p, arcname=p.name)
    os.replace(tmp_zip, final_zip)
    return final_zip, len(remaining_findings), remaining_findings
