#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from .config import SentinelConfig


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


def scan_security(config: SentinelConfig, scan_state: dict[str, Any]) -> dict[str, Any]:
    repo_root = config.repo_root
    findings: list[dict[str, Any]] = []

    files = sorted(scan_state.get("files", []), key=lambda item: str(item.get("path", "")))
    scanned_files = 0
    for row in files:
        if scanned_files >= max(1, int(config.max_security_scan_files)):
            break
        rel_path = str(row.get("path", ""))
        if not rel_path:
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

        lines = text.splitlines()
        for index, line in enumerate(lines, start=1):
            for kind, pattern, severity in SECRET_PATTERNS:
                if re.search(pattern, line):
                    snippet = _mask_snippet(line)
                    findings.append(
                        {
                            "kind": kind,
                            "severity": severity,
                            "path": rel_path,
                            "line": index,
                            "snippet": snippet,
                            "fingerprint": _finding_fingerprint(rel_path, kind, index, snippet),
                        }
                    )
            if rel_path.endswith((".sh", ".bat", ".cmd", ".ps1", ".py")):
                for kind, pattern, severity in DANGEROUS_SCRIPT_PATTERNS:
                    if re.search(pattern, line, flags=re.IGNORECASE):
                        snippet = _mask_snippet(line)
                        findings.append(
                            {
                                "kind": f"dangerous_script:{kind}",
                                "severity": severity,
                                "path": rel_path,
                                "line": index,
                                "snippet": snippet,
                                "fingerprint": _finding_fingerprint(rel_path, kind, index, snippet),
                            }
                        )

    unique_by_key: dict[str, dict[str, Any]] = {}
    for finding in findings:
        unique_by_key[finding["fingerprint"]] = finding
    deduped = sorted(unique_by_key.values(), key=lambda item: (item["path"], item["line"], item["kind"]))

    counts: dict[str, int] = {}
    for finding in deduped:
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
            "findingCount": len(deduped),
            "severityCounts": dict(sorted(counts.items())),
            "alertLevel": alert_level,
            "scannedFiles": scanned_files,
            "scanLimit": int(config.max_security_scan_files),
        },
        "findings": deduped,
    }
