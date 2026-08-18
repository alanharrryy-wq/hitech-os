from __future__ import annotations

import json
import os
import re
import tempfile
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from .contracts import ContractError, normalize_repo_path, require_nonempty_string, sha256_json

SCANNER_ID = "code-atlas-artifact-hygiene.v1"

INSPECTABLE_SUFFIXES = {
    ".csv",
    ".html",
    ".json",
    ".log",
    ".md",
    ".sarif",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
SOURCE_CODE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".mjs",
    ".mts",
    ".php",
    ".ps1",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}
SOURCE_CODE_NAMES = {"dockerfile", "makefile", "rakefile"}

_SECRET_KEYS = {
    "accesskey",
    "access_key",
    "apikey",
    "api_key",
    "authorization",
    "bearer",
    "clientsecret",
    "client_secret",
    "credential",
    "credentials",
    "password",
    "passwd",
    "privatekey",
    "private_key",
    "refreshtoken",
    "refresh_token",
    "secret",
    "secretvalue",
    "token",
    "tokenvalue",
}
_COMPACT_SECRET_KEYS = {item.replace("_", "") for item in _SECRET_KEYS}
_EMAIL = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
    re.S,
)
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}")
_GITHUB_TOKEN = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
_GENERIC_ASSIGNMENT = re.compile(
    r"(?im)(\b(?:api[_-]?key|client[_-]?secret|password|passwd|access[_-]?token|refresh[_-]?token|token)\b\s*[:=]\s*)([^\s,;]+)"
)

_RULESET_DIGEST = sha256_json(
    {
        "scanner": SCANNER_ID,
        "inspectableSuffixes": sorted(INSPECTABLE_SUFFIXES),
        "sourceCodeSuffixes": sorted(SOURCE_CODE_SUFFIXES),
        "rules": ["json-secret-key", "email", "private-key", "bearer-token", "github-token", "generic-secret-assignment"],
    }
)


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def _secret_key(name: Any) -> bool:
    normalized = str(name).replace("-", "_").replace(" ", "").lower()
    compact = normalized.replace("_", "")
    return normalized in _SECRET_KEYS or compact in _COMPACT_SECRET_KEYS


def _redact_json(value: Any, findings: dict[str, int]) -> Any:
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if _secret_key(key) and item is not None and item != "":
                findings["json-secret-key"] = findings.get("json-secret-key", 0) + 1
                out[str(key)] = "<REDACTED_SECRET>"
            else:
                out[str(key)] = _redact_json(item, findings)
        return out
    if isinstance(value, list):
        return [_redact_json(item, findings) for item in value]
    if isinstance(value, str):
        return _redact_text(value, findings)
    return value


def _redact_text(text: str, findings: dict[str, int]) -> str:
    def replace(pattern: re.Pattern[str], label: str, replacement: str, value: str) -> str:
        updated, count = pattern.subn(replacement, value)
        if count:
            findings[label] = findings.get(label, 0) + count
        return updated

    text = replace(_PRIVATE_KEY, "private-key", "<REDACTED_PRIVATE_KEY>", text)
    text = replace(_BEARER, "bearer-token", "Bearer <REDACTED_TOKEN>", text)
    text = replace(_GITHUB_TOKEN, "github-token", "<REDACTED_TOKEN>", text)
    text = replace(_EMAIL, "email", "<REDACTED_EMAIL>", text)

    def assignment(match: re.Match[str]) -> str:
        findings["generic-secret-assignment"] = findings.get("generic-secret-assignment", 0) + 1
        return match.group(1) + "<REDACTED_SECRET>"

    return _GENERIC_ASSIGNMENT.sub(assignment, text)


def _remaining_sensitive(text: str) -> list[str]:
    remaining: list[str] = []
    for label, pattern in (
        ("private-key", _PRIVATE_KEY),
        ("bearer-token", _BEARER),
        ("github-token", _GITHUB_TOKEN),
        ("email", _EMAIL),
    ):
        if pattern.search(text):
            remaining.append(label)
    return remaining


def sanitize_artifact_bytes(*, name: str, kind: str, content: bytes) -> tuple[bytes, dict[str, Any]]:
    """Inspect and sanitize one export artifact without mutating its source bytes.

    V1 deliberately supports inspectable UTF-8 evidence formats only. Unknown or
    binary formats fail closed rather than being waved through as "probably safe".
    """

    normalized_name = normalize_repo_path(name)
    require_nonempty_string(kind, "kind")
    path = Path(normalized_name)
    suffix = path.suffix.lower()
    if suffix in SOURCE_CODE_SUFFIXES or path.name.lower() in SOURCE_CODE_NAMES:
        raise ContractError(f"source-code artifact egress rejected: {normalized_name}")
    if suffix not in INSPECTABLE_SUFFIXES:
        raise ContractError(f"artifact format is not inspectable by {SCANNER_ID}: {normalized_name}")
    if b"\x00" in content:
        raise ContractError(f"binary-like artifact rejected by fail-closed scanner: {normalized_name}")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ContractError(f"artifact is not valid UTF-8 text: {normalized_name}") from exc

    findings: dict[str, int] = {}
    if suffix in {".json", ".sarif"}:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ContractError(f"structured JSON artifact is invalid: {normalized_name}") from exc
        sanitized_value = _redact_json(parsed, findings)
        text = json.dumps(sanitized_value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    else:
        text = _redact_text(text, findings)

    remaining = _remaining_sensitive(text)
    if remaining:
        raise ContractError(f"artifact sanitization could not be proven for {normalized_name}: {sorted(set(remaining))}")

    sanitized = text.encode("utf-8")
    attestation = {
        "schemaVersion": "code_atlas_artifact_sanitization.v1",
        "name": normalized_name,
        "kind": require_nonempty_string(kind, "kind"),
        "scannerId": SCANNER_ID,
        "rulesetDigest": _RULESET_DIGEST,
        "contentInspection": "FULL_UTF8_TEXT",
        "originalDigest": _sha256_bytes(content),
        "originalSize": len(content),
        "sanitizedDigest": _sha256_bytes(sanitized),
        "sanitizedSize": len(sanitized),
        "findings": [
            {"class": label, "count": findings[label]}
            for label in sorted(findings)
        ],
        "decision": "PASS_SANITIZED" if findings else "PASS_CLEAN",
        "sourceCodeIncluded": False,
        "certifiable": False,
        "productionCertified": False,
    }
    attestation["attestationDigest"] = sha256_json(attestation)
    return sanitized, attestation


def sanitize_artifacts_for_egress(
    *,
    artifacts: list[Mapping[str, Any]],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Sanitize every artifact in a private staging directory, then publish atomically.

    Each input row requires ``localPath``, ``name`` and ``kind``. If any artifact
    fails inspection, the staging directory is removed and no new final artifact
    is intentionally left behind. If publication itself fails, files published by
    this call are rolled back before the error is raised.
    """

    if not artifacts:
        raise ContractError("at least one artifact is required for hardened egress")
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    rows: list[tuple[Path, str, str]] = []
    for index, row in enumerate(artifacts):
        if not isinstance(row, Mapping):
            raise ContractError(f"artifacts[{index}] must be an object")
        source = Path(require_nonempty_string(row.get("localPath"), f"artifacts[{index}].localPath")).resolve()
        name = normalize_repo_path(row.get("name"))
        kind = require_nonempty_string(row.get("kind"), f"artifacts[{index}].kind")
        if name in seen:
            raise ContractError(f"duplicate artifact name: {name}")
        if not source.is_file():
            raise ContractError(f"artifact source file does not exist: {name}")
        target = (out / name).resolve()
        if out not in target.parents and target != out:
            raise ContractError(f"artifact target escapes output root: {name}")
        if target.exists():
            raise ContractError(f"hardened egress refuses to overwrite existing artifact: {name}")
        seen.add(name)
        rows.append((source, name, kind))

    descriptors: list[dict[str, Any]] = []
    attestations: list[dict[str, Any]] = []
    published: list[Path] = []
    stage_parent = out.parent
    try:
        with tempfile.TemporaryDirectory(prefix="code-atlas-egress-", dir=stage_parent) as tmp:
            stage = Path(tmp)
            staged_targets: list[tuple[Path, Path]] = []
            for source, name, kind in rows:
                sanitized, attestation = sanitize_artifact_bytes(name=name, kind=kind, content=source.read_bytes())
                staged = stage / name
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(sanitized)
                final = out / name
                staged_targets.append((staged, final))
                descriptors.append({
                    "name": name,
                    "kind": kind,
                    "digest": attestation["sanitizedDigest"],
                    "size": attestation["sanitizedSize"],
                })
                attestations.append(attestation)

            for staged, final in staged_targets:
                final.parent.mkdir(parents=True, exist_ok=True)
                os.replace(staged, final)
                published.append(final)
    except Exception:
        for path in reversed(published):
            try:
                if path.is_file():
                    path.unlink()
            except OSError:
                pass
        for parent in sorted({path.parent for path in published}, key=lambda value: len(value.parts), reverse=True):
            try:
                if parent != out and parent.is_dir() and not any(parent.iterdir()):
                    parent.rmdir()
            except OSError:
                pass
        raise

    return {
        "schemaVersion": "code_atlas_hardened_egress_artifacts.v1",
        "scannerId": SCANNER_ID,
        "rulesetDigest": _RULESET_DIGEST,
        "artifacts": sorted(descriptors, key=lambda row: row["name"]),
        "sanitizationAttestations": sorted(attestations, key=lambda row: row["name"]),
        "publishedFiles": [str(path) for path in sorted(published)],
        "sourceCodeIncluded": False,
        "allArtifactsInspected": True,
        "failClosed": True,
        "certifiable": False,
        "productionCertified": False,
    }


def cleanup_published_artifacts(*, published_files: list[str], output_root: str | Path) -> dict[str, Any]:
    """Remove only files previously published by the hardened egress stage."""

    root = Path(output_root).resolve()
    removed_files = 0
    removed_bytes = 0
    for raw in published_files:
        path = Path(raw).resolve()
        if root not in path.parents:
            raise ContractError("published artifact path is outside the declared output root")
        if path.is_file():
            removed_bytes += path.stat().st_size
            path.unlink()
            removed_files += 1
    remaining = [raw for raw in published_files if Path(raw).exists()]
    if remaining:
        raise ContractError("artifact cleanup verification failed")
    return {
        "schemaVersion": "code_atlas_artifact_cleanup.v1",
        "removedFiles": removed_files,
        "removedBytes": removed_bytes,
        "remainingPublishedFiles": 0,
        "cleanupVerified": True,
        "secureEraseGuaranteed": False,
        "certifiable": False,
        "productionCertified": False,
    }


__all__ = [
    "SCANNER_ID",
    "cleanup_published_artifacts",
    "sanitize_artifact_bytes",
    "sanitize_artifacts_for_egress",
]
