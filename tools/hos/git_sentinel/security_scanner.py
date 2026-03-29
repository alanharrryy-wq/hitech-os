#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any

from .config import SentinelConfig
from .false_positive import apply_false_positive_feedback, load_feedback, write_false_positive_audit


SECRET_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("aws_access_key", r"\bAKIA[0-9A-Z]{16}\b", "high"),
    ("github_pat", r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", "high"),
    ("openai_key", r"\bsk-[A-Za-z0-9]{20,}\b", "high"),
    ("generic_api_key", r"(?i)\b(api[_-]?key|token|secret)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]", "medium"),
    ("private_key_block", r"-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) PRIVATE KEY-----", "critical"),
    ("password_assignment", r"(?i)\bpassword\b\s*[:=]\s*['\"][^'\"]{6,}['\"]", "medium"),
)

DANGEROUS_SCRIPT_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("destructive_rm", r"\brm\s+-rf\b", "high"),
    ("destructive_del", r"\bdel\s+/s\s+/q\b", "high"),
    ("destructive_git_clean", r"\bgit\s+clean\s+-fdx\b", "high"),
    ("destructive_git_reset", r"\bgit\s+reset\s+--hard\b", "high"),
)

ENTROPY_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]([A-Za-z0-9_\-+=/.]{12,})['\"]"
)


def _is_scannable_text_file(path: str, config: SentinelConfig) -> bool:
    ext = Path(path).suffix.lower()
    return ext in set(config.secret_scan_extensions) or ext == ""


def _mask_snippet(text: str, max_len: int = 160) -> str:
    collapsed = " ".join(text.strip().split())
    if len(collapsed) <= max_len:
        return collapsed
    return collapsed[: max_len - 3] + "..."


def _finding_fingerprint(path: str, kind: str, line: int, snippet: str) -> str:
    raw = f"{path}|{kind}|{line}|{snippet}".encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()


def _path_in_doc_context(path: str, config: SentinelConfig) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in config.security_doc_path_globs:
        regex = re.escape(pattern.replace("\\", "/"))
        regex = regex.replace(r"\*\*", "__DOUBLE_STAR__")
        regex = regex.replace(r"\*", "[^/]*")
        regex = regex.replace("__DOUBLE_STAR__", ".*")
        if re.fullmatch(regex, normalized):
            return True
    return False


def _downgrade_for_context(kind: str, severity: str, doc_context: bool) -> tuple[str, float]:
    if not doc_context:
        return severity, 1.0
    lowered = kind.lower()
    if lowered in {"generic_api_key", "password_assignment"} or lowered.startswith("dangerous_script:"):
        return "low", 0.35
    if lowered == "openai_key":
        return "medium", 0.55
    return severity, 0.7


def _shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts: dict[str, int] = {}
    for char in value:
        counts[char] = counts.get(char, 0) + 1
    length = float(len(value))
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def scan_text_security(config: SentinelConfig, rel_path: str, text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    doc_context = _path_in_doc_context(path=rel_path, config=config)

    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        for kind, pattern, base_severity in SECRET_PATTERNS:
            if not re.search(pattern, line):
                continue
            severity, confidence = _downgrade_for_context(kind=kind, severity=base_severity, doc_context=doc_context)
            snippet = _mask_snippet(line)
            findings.append(
                {
                    "kind": kind,
                    "severity": severity,
                    "path": rel_path,
                    "line": index,
                    "snippet": snippet,
                    "confidence": round(confidence, 4),
                    "context": "documentation" if doc_context else "runtime",
                    "fingerprint": _finding_fingerprint(rel_path, kind, index, snippet),
                }
            )

        if rel_path.endswith((".sh", ".bat", ".cmd", ".ps1", ".py")):
            for script_kind, pattern, base_severity in DANGEROUS_SCRIPT_PATTERNS:
                if not re.search(pattern, line, flags=re.IGNORECASE):
                    continue
                line_compact = line.strip()
                if line_compact.startswith(("\"", "'")):
                    # Treat quoted tokens as documentation/policy text, not executable command usage.
                    continue
                kind = f"dangerous_script:{script_kind}"
                severity, confidence = _downgrade_for_context(kind=kind, severity=base_severity, doc_context=doc_context)
                snippet = _mask_snippet(line)
                findings.append(
                    {
                        "kind": kind,
                        "severity": severity,
                        "path": rel_path,
                        "line": index,
                        "snippet": snippet,
                        "confidence": round(confidence, 4),
                        "context": "documentation" if doc_context else "runtime",
                        "fingerprint": _finding_fingerprint(rel_path, kind, index, snippet),
                    }
                )

        for match in ENTROPY_ASSIGNMENT_PATTERN.finditer(line):
            token = str(match.group(2) or "")
            if len(token) < int(config.security_entropy_min_length):
                continue
            entropy = _shannon_entropy(token)
            if entropy < float(config.security_entropy_threshold):
                continue
            kind = "high_entropy_secret"
            severity, confidence = _downgrade_for_context(kind=kind, severity="medium", doc_context=doc_context)
            snippet = _mask_snippet(line)
            findings.append(
                {
                    "kind": kind,
                    "severity": severity,
                    "path": rel_path,
                    "line": index,
                    "snippet": snippet,
                    "confidence": round(min(1.0, 0.45 + entropy / 8.0), 4),
                    "entropy": round(entropy, 4),
                    "context": "documentation" if doc_context else "runtime",
                    "fingerprint": _finding_fingerprint(rel_path, kind, index, snippet),
                }
            )

    return findings


def scan_security(
    config: SentinelConfig,
    scan_state: dict[str, Any],
    include_paths: set[str] | None = None,
) -> dict[str, Any]:
    repo_root = config.repo_root
    findings: list[dict[str, Any]] = []

    includes = {path.replace("\\", "/") for path in include_paths} if include_paths else None
    files = sorted(scan_state.get("files", []), key=lambda item: str(item.get("path", "")))
    scanned_files = 0
    for row in files:
        if scanned_files >= max(1, int(config.max_security_scan_files)):
            break
        rel_path = str(row.get("path", "")).replace("\\", "/")
        if not rel_path:
            continue
        if includes is not None and rel_path not in includes:
            continue
        if bool(row.get("binary", False)):
            continue
        if not _is_scannable_text_file(rel_path, config):
            continue
        size = int(row.get("size", 0))
        if size > config.max_text_scan_bytes:
            continue

        abs_path = (repo_root / rel_path).resolve()
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned_files += 1
        findings.extend(scan_text_security(config=config, rel_path=rel_path, text=text))

    unique_by_key: dict[str, dict[str, Any]] = {}
    for finding in findings:
        unique_by_key[str(finding["fingerprint"])] = finding
    deduped = sorted(unique_by_key.values(), key=lambda item: (str(item["path"]), int(item["line"]), str(item["kind"])))

    feedback = load_feedback(config)
    filtered_findings, suppressed_findings, false_positive_summary, audit_payload = apply_false_positive_feedback(
        findings=deduped,
        feedback=feedback,
    )
    false_positive_summary["auditPath"] = write_false_positive_audit(config=config, payload=audit_payload)

    counts: dict[str, int] = {}
    for finding in filtered_findings:
        sev = str(finding.get("severity", "low")).lower()
        counts[sev] = counts.get(sev, 0) + 1

    alert_level = "none"
    if counts.get("critical", 0) > 0:
        alert_level = "critical"
    elif counts.get("high", 0) > 0:
        alert_level = "high"
    elif counts.get("medium", 0) > 0:
        alert_level = "medium"
    elif counts.get("low", 0) > 0:
        alert_level = "low"

    return {
        "summary": {
            **false_positive_summary,
            "severityCounts": dict(sorted(counts.items())),
            "alertLevel": alert_level,
            "scannedFiles": scanned_files,
            "scanLimit": int(config.max_security_scan_files),
            "mode": "incremental" if includes is not None else "full",
            "scopedFileCount": 0 if includes is None else len(includes),
        },
        "findings": filtered_findings,
        "suppressedFindings": suppressed_findings,
    }
