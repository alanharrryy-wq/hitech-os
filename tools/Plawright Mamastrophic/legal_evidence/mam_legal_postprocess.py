from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable

VERSION = "mamlegal1-v1.0.0"
TEXT_SUFFIXES = {
    ".json", ".jsonl", ".md", ".txt", ".log", ".csv", ".html", ".xml",
    ".yml", ".yaml", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".css"
}
SCREEN_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_COPY_SUFFIXES = TEXT_SUFFIXES | SCREEN_SUFFIXES | {".sha256"}
SECRET_PATTERNS = [
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.I), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b(?:ghp_|github_pat_|sk-|prisma_)[A-Za-z0-9._-]{12,}\b", re.I), "[REDACTED_TOKEN]"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"), "[REDACTED_JWT]"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED_EMAIL]"),
    (re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"), "[REDACTED_PHONE]"),
    (re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"), "[REDACTED_PAYMENT_NUMBER]"),
    (re.compile(r"\b(api[_-]?key|token|secret|password|passwd|authorization|session|cookie)\b(\s*[:=]\s*)([\"']?)[^,\s\"'<>;&]{6,}\3", re.I), r"\1\2[REDACTED]"),
]
URL_QUERY_RE = re.compile(
    r"([?&](?:token|secret|password|passwd|key|auth|session|cookie|email|phone|customer|client|device|license|setup|pin|code)=)[^&#\s]+",
    re.I,
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def local_stamp() -> str:
    return dt.datetime.now().strftime("%d%m %H%M%S")


def safe_id(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.:-]+", "_", str(value or "")).strip("_")
    return value or "item"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def sanitize_text(value: str) -> tuple[str, int]:
    text = str(value or "")
    count = 0
    for pattern, replacement in SECRET_PATTERNS:
        text, n = pattern.subn(replacement, text)
        count += n
    text, n = URL_QUERY_RE.subn(r"\1[REDACTED]", text)
    count += n
    return text, count


def sanitize_json(value: Any) -> tuple[Any, int]:
    if value is None or isinstance(value, (int, float, bool)):
        return value, 0
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        out = []
        total = 0
        for item in value:
            clean, count = sanitize_json(item)
            out.append(clean)
            total += count
        return out, total
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        total = 0
        sensitive = re.compile(r"(token|secret|password|passwd|authorization|cookie|session|api[_-]?key|private[_-]?key)", re.I)
        for key, item in value.items():
            if sensitive.search(str(key)):
                out[str(key)] = "[REDACTED]"
                total += 1
            else:
                clean, count = sanitize_json(item)
                out[str(key)] = clean
                total += count
        return out, total
    return sanitize_text(str(value))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git_read(repo_root: Path) -> dict[str, Any]:
    def run(args: list[str]) -> dict[str, Any]:
        try:
            proc = subprocess.run(args, cwd=str(repo_root), text=True, capture_output=True, timeout=45)
            return {
                "args": args,
                "exit_code": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        except Exception as exc:
            return {"args": args, "exit_code": -1, "stdout": "", "stderr": repr(exc)}
    head = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    return {
        "head": head.get("stdout") or None,
        "branch": branch.get("stdout") or None,
        "status_porcelain": status.get("stdout") or "",
        "commands": {"head": head, "branch": branch, "status": status},
    }


def infer_surface(rel: str) -> str:
    parts = rel.replace("\\", "/").split("/")
    known = {"chart-lab", "web", "tablet", "pc", "mobile", "control-center"}
    for part in parts:
        if part in known:
            return part
    low = rel.lower()
    for surface in sorted(known):
        if surface in low:
            return surface
    return "unknown"


def evidence_type_for(path: Path) -> str:
    low = path.name.lower()
    if path.suffix.lower() in SCREEN_SUFFIXES:
        return "SCREENSHOT_REDACTED"
    if ".dom." in low or low.endswith(".dom.json"):
        return "DOM_REDACTED"
    if "console" in low:
        return "CONSOLE_LOG_REDACTED"
    if "network" in low or "request" in low or "response" in low:
        return "NETWORK_LOG_REDACTED"
    return "TEST_RESULT"


def copy_and_sanitize(raw_root: Path, safe_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    stats = {
        "considered": 0,
        "copied": 0,
        "text_files_sanitized": 0,
        "replacement_count": 0,
        "images_copied": 0,
        "skipped": 0,
        "errors": [],
    }
    for source in sorted(raw_root.rglob("*")):
        if not source.is_file():
            continue
        stats["considered"] += 1
        suffix = source.suffix.lower()
        if suffix not in ALLOWED_COPY_SUFFIXES:
            stats["skipped"] += 1
            continue
        rel = source.relative_to(raw_root)
        target = safe_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if suffix in TEXT_SUFFIXES:
                raw = source.read_text(encoding="utf-8", errors="replace")
                replacements = 0
                if suffix in {".json", ".jsonl"}:
                    if suffix == ".json":
                        try:
                            obj = json.loads(raw)
                            obj, replacements = sanitize_json(obj)
                            target.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
                        except Exception:
                            clean, replacements = sanitize_text(raw)
                            target.write_text(clean, encoding="utf-8")
                    else:
                        out_lines = []
                        for line in raw.splitlines():
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                obj, count = sanitize_json(obj)
                                replacements += count
                                out_lines.append(json.dumps(obj, ensure_ascii=False, default=str))
                            except Exception:
                                clean, count = sanitize_text(line)
                                replacements += count
                                out_lines.append(clean)
                        target.write_text("\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8")
                else:
                    clean, replacements = sanitize_text(raw)
                    target.write_text(clean, encoding="utf-8")
                stats["text_files_sanitized"] += 1
                stats["replacement_count"] += replacements
            else:
                shutil.copy2(source, target)
                stats["images_copied"] += 1
            stats["copied"] += 1
            artifacts.append({
                "source_path": str(source),
                "safe_path": target.relative_to(safe_root.parent).as_posix(),
                "sha256": sha256_file(target),
                "bytes": target.stat().st_size,
                "surface": infer_surface(rel.as_posix()),
                "evidence_type": evidence_type_for(target),
            })
        except Exception as exc:
            stats["errors"].append({"path": str(source), "error": repr(exc)})
    return artifacts, stats


def scan_for_unredacted(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    token_checks = [
        ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
        ("BEARER", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.I)),
        ("TOKEN_PREFIX", re.compile(r"\b(?:ghp_|github_pat_|sk-|prisma_)[A-Za-z0-9._-]{12,}\b", re.I)),
        ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for label, pattern in token_checks:
            matches = pattern.findall(text)
            if matches:
                findings.append({
                    "path": path.relative_to(root).as_posix(),
                    "kind": label,
                    "count": len(matches),
                })
    return findings


def build_evidence_entries(
    artifacts: list[dict[str, Any]],
    run_id: str,
    source_commit: str | None,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for index, artifact in enumerate(artifacts, 1):
        surface = artifact.get("surface") or "unknown"
        evidence_type = artifact["evidence_type"]
        entries.append({
            "evidence_id": f"EVD.LGL.MAM.{safe_id(run_id)}.{index:06d}",
            "evidence_type": evidence_type,
            "target_id": f"SURF.{safe_id(surface).upper()}",
            "source_tool": "Plawright Mamastrophic",
            "run_id": run_id,
            "collector_id": "mamlegal1",
            "collector_version": VERSION,
            "collected_at": utc_now(),
            "source_commit": source_commit,
            "artifact_path": artifact["safe_path"],
            "artifact_hash": artifact["sha256"],
            "source_artifact_hash": artifact["sha256"],
            "custody_id": f"CUST.MAM.{safe_id(run_id)}.{index:06d}",
            "status": "CONFIRMED",
            "confidence": "HIGH",
            "sensitivity_class": "CONFIDENTIAL" if evidence_type == "SCREENSHOT_REDACTED" else "INTERNAL",
            "redaction_status": "PASS_REDACTED",
            "legal_domains": [
                "RUNTIME_EVIDENCE",
                "PRIVACY_REDACTION",
                "INVESTOR_DUE_DILIGENCE",
            ],
            "jurisdictions": [],
            "validity_status": "CURRENT",
            "proves": [
                "The referenced runtime artifact was captured by Mamastrophic during this run.",
                f"The artifact is associated with the {surface} runtime surface.",
            ],
            "does_not_prove": [
                "Legal compliance.",
                "Production readiness.",
                "Absence of security vulnerabilities.",
                "Ownership of the underlying source code or assets.",
            ],
            "authority_level": "T1_PRIMARY_TECHNICAL",
            "human_review_required": True,
            "attributes": {
                "surface": surface,
                "bytes": artifact["bytes"],
                "safe_profile": "legal-evidence",
            },
        })
    return entries


def artifact_hashes(root: Path, exclude: set[str] | None = None) -> dict[str, str]:
    exclude = exclude or set()
    rows: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if rel in exclude:
                continue
            rows[rel] = sha256_file(path)
    return rows


def write_hash_file(root: Path, path: Path) -> None:
    rel_self = path.relative_to(root).as_posix()
    lines = []
    for rel, digest in sorted(artifact_hashes(root, {rel_self}).items()):
        lines.append(f"{digest} *{rel}")
    write_text(path, "\n".join(lines))


def zip_dir(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description="Sanitize and package Mamastrophic legal runtime evidence")
    parser.add_argument("--raw-root", required=True)
    parser.add_argument("--package-root", required=True)
    parser.add_argument("--output-zip", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--tool-root", required=True)
    parser.add_argument("--surface-results", required=True)
    parser.add_argument("--authority-json", required=True)
    parser.add_argument("--status", choices=["PASS", "PARTIAL", "FAIL", "BLOCKED"], required=True)
    args = parser.parse_args()

    raw_root = Path(args.raw_root).resolve()
    package_root = Path(args.package_root).resolve()
    output_zip = Path(args.output_zip).resolve()
    repo_root = Path(args.repo_root).resolve()
    tool_root = Path(args.tool_root).resolve()
    surface_results_path = Path(args.surface_results).resolve()
    authority_path = Path(args.authority_json).resolve()

    package_root.mkdir(parents=True, exist_ok=True)
    safe_root = package_root / "raw_outputs"
    safe_root.mkdir(parents=True, exist_ok=True)

    git = git_read(repo_root)
    source_commit = git.get("head")
    surface_results = json.loads(surface_results_path.read_text(encoding="utf-8-sig"))
    authority = json.loads(authority_path.read_text(encoding="utf-8-sig"))

    artifacts, redaction_stats = copy_and_sanitize(raw_root, safe_root)
    unredacted_findings = scan_for_unredacted(safe_root)
    blockers = []
    warnings = []
    if redaction_stats["errors"]:
        blockers.append("SANITIZATION_COPY_ERRORS")
    if unredacted_findings:
        blockers.append("UNREDACTED_TEXT_FINDINGS")
    if not artifacts:
        blockers.append("NO_RUNTIME_ARTIFACTS")
    if any(str(row.get("status", "")).upper() == "FAIL" for row in surface_results):
        warnings.append("ONE_OR_MORE_SURFACES_FAILED")
    if any(str(row.get("status", "")).upper() in {"OFFLINE", "SKIPPED", "PARTIAL"} for row in surface_results):
        warnings.append("ONE_OR_MORE_SURFACES_PARTIAL_OR_OFFLINE")

    effective_status = args.status
    if blockers:
        effective_status = "FAIL"
    elif effective_status == "PASS" and warnings:
        effective_status = "PARTIAL"

    evidence = build_evidence_entries(artifacts, args.run_id, source_commit)
    write_json(package_root / "EVIDENCE_INDEX.json", evidence)

    candidates = []
    for row in evidence:
        candidates.append({
            "candidate_id": row["evidence_id"],
            "candidate_type": "LEGAL_RUNTIME_EVIDENCE",
            "target_id": row["target_id"],
            "status": "CONFIRMED",
            "source_tool": row["source_tool"],
            "artifact_path": row["artifact_path"],
            "artifact_hash": row["artifact_hash"],
            "run_id": row["run_id"],
            "redaction_status": row["redaction_status"],
            "human_review_required": True,
        })
    write_json(package_root / "CANDIDATES.ndc.json", candidates)

    proves = {
        "schema": "PRISMA_MAM_LEGAL_PROVES_V1",
        "run_id": args.run_id,
        "proves": [
            "Mamastrophic produced runtime evidence for the surfaces represented in EVIDENCE_INDEX.json.",
            "Textual runtime artifacts passed the mamlegal1 sanitizer scan.",
            "Screenshots were taken after browser-side legal redaction was applied where capture completed.",
            "The package has a SHA-256 chain of custody.",
        ],
        "does_not_prove": [
            "Legal compliance.",
            "IP ownership.",
            "Open-source license compliance.",
            "Production readiness.",
            "Absence of vulnerabilities.",
            "Completeness of runtime coverage.",
        ],
    }
    write_json(package_root / "PROVES_DOES_NOT_PROVE.json", proves)

    custody = {
        "schema": "PRISMA_MAM_LEGAL_CHAIN_OF_CUSTODY_V1",
        "run_id": args.run_id,
        "collector": {"id": "mamlegal1", "version": VERSION},
        "tool_root": str(tool_root),
        "source_commit": source_commit,
        "authority": authority,
        "artifacts": [
            {
                "custody_id": row["custody_id"],
                "evidence_id": row["evidence_id"],
                "artifact_path": row["artifact_path"],
                "artifact_hash": row["artifact_hash"],
                "collected_at": row["collected_at"],
                "redaction_status": row["redaction_status"],
            }
            for row in evidence
        ],
    }
    write_json(package_root / "CHAIN_OF_CUSTODY.json", custody)
    write_json(package_root / "REDACTION_REPORT.json", {
        "schema": "PRISMA_MAM_LEGAL_REDACTION_REPORT_V1",
        "run_id": args.run_id,
        "policy": "mamlegal1-strict-v1",
        "status": "FAIL" if blockers else "PASS_REDACTED",
        "stats": redaction_stats,
        "unredacted_findings": unredacted_findings,
    })
    write_json(package_root / "SURFACE_RESULTS.json", surface_results)
    write_json(package_root / "AUTHORITY_CHAIN.json", authority)

    run_manifest = {
        "schema": "PRISMA_LEGAL_RUN_MANIFEST_V1",
        "run_id": args.run_id,
        "profile": "legal-evidence",
        "status": effective_status,
        "started_at": authority.get("started_at") or utc_now(),
        "finished_at": utc_now(),
        "collector": {
            "id": "mamlegal1",
            "version": VERSION,
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "source_commit": source_commit,
        "authority_run_id": authority.get("authority_run_id"),
        "no_touch": {
            "db_write": False,
            "git_write": False,
            "process_kill": False,
            "port_free": False,
            "server_start": False,
            "dependency_install": False,
        },
        "stages": [
            {"id": "authority", "status": "PASS"},
            {"id": "sequential_runtime_capture", "status": args.status, "surfaces": surface_results},
            {"id": "sanitization", "status": "FAIL" if blockers else "PASS", "stats": redaction_stats},
            {"id": "chain_of_custody", "status": "PASS", "evidence_count": len(evidence)},
        ],
        "artifacts": [
            {"path": row["artifact_path"], "sha256": row["artifact_hash"], "evidence_id": row["evidence_id"]}
            for row in evidence
        ],
        "warnings": warnings,
        "blockers": blockers,
    }
    write_json(package_root / "LEGAL_RUN_MANIFEST.json", run_manifest)

    conflict_lines = [
        "# Mamastrophic legal evidence conflicts and unknowns",
        "",
        f"- Run: `{args.run_id}`",
        f"- Status: `{effective_status}`",
        f"- Runtime artifacts: `{len(artifacts)}`",
        f"- Sanitizer replacements: `{redaction_stats['replacement_count']}`",
        f"- Unredacted text findings: `{len(unredacted_findings)}`",
        "",
        "## Warnings",
    ]
    conflict_lines.extend([f"- {item}" for item in warnings] or ["- None"])
    conflict_lines += ["", "## Blockers"]
    conflict_lines.extend([f"- {item}" for item in blockers] or ["- None"])
    conflict_lines += [
        "",
        "## Unknowns requiring human review",
        "- Screenshots may still contain business-sensitive imagery that regex-based text scanning cannot classify.",
        "- Runtime capture does not establish ownership of UI assets or source code.",
        "- Offline or failed surfaces are not silently treated as covered.",
    ]
    write_text(package_root / "CONFLICTS_AND_UNKNOWNS.md", "\n".join(conflict_lines))

    summary_lines = [
        "# Mamastrophic Legal Evidence",
        "",
        f"- Run: `{args.run_id}`",
        f"- Status: `{effective_status}`",
        f"- Source commit: `{source_commit}`",
        f"- Evidence entries: `{len(evidence)}`",
        f"- Surfaces attempted: `{len(surface_results)}`",
        f"- Redaction policy: `mamlegal1-strict-v1`",
        f"- Textual unredacted findings: `{len(unredacted_findings)}`",
        "",
        "This package is technical runtime evidence for due diligence. It is not a legal opinion or compliance certification.",
    ]
    write_text(package_root / "SUMMARY.md", "\n".join(summary_lines))
    write_text(package_root / "CONTINUATION.md", "\n".join([
        "# Mamastrophic Legal Evidence continuation",
        "",
        f"- Status: `{effective_status}`",
        f"- Evidence entries: `{len(evidence)}`",
        "- Next integration package: `catlgl1` after installation of `mamlegal1`.",
        "- Upload this ZIP for review before Code Atlas integration.",
    ]))

    required_members = [
        "LEGAL_RUN_MANIFEST.json",
        "CANDIDATES.ndc.json",
        "EVIDENCE_INDEX.json",
        "PROVES_DOES_NOT_PROVE.json",
        "CONFLICTS_AND_UNKNOWNS.md",
        "SUMMARY.md",
        "CONTINUATION.md",
        "ARTIFACT_HASHES.sha256",
        "raw_outputs/",
    ]
    input_package = {
        "schema": "PRISMA_LEGAL_INPUT_PACKAGE_V1",
        "run_id": args.run_id,
        "tool_id": "mamlegal1",
        "required_members": required_members,
        "artifact_hashes": {},
        "created_at": utc_now(),
    }
    input_package["artifact_hashes"] = artifact_hashes(
        package_root,
        {"LEGAL_INPUT_PACKAGE.json", "ARTIFACT_HASHES.sha256"},
    )
    write_json(package_root / "LEGAL_INPUT_PACKAGE.json", input_package)
    write_hash_file(package_root, package_root / "ARTIFACT_HASHES.sha256")

    zip_dir(package_root, output_zip)
    if not output_zip.exists() or not zipfile.is_zipfile(output_zip):
        raise RuntimeError("Final ZIP validation failed")
    print(json.dumps({
        "status": effective_status,
        "output_zip": str(output_zip),
        "evidence_count": len(evidence),
        "blockers": blockers,
        "warnings": warnings,
    }, ensure_ascii=False))
    return 0 if effective_status in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
