from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from .runtime_profile import OperationalRuntimeProfile, public_path, resolve_runtime_profile

VERSION = "2.0.0"
MAX_WORKERS = 18
SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".json", ".md", ".yaml", ".yml", ".toml", ".css", ".html",
}
EXCLUDED_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "venv", ".venv",
    "reports",
}
CATALOG_FILES = (
    "catalogs/support-error-codes.json",
    "catalogs/resolver-actions.json",
    "catalogs/feature-gates.json",
    "catalogs/surface-status-catalog.json",
)
TEST_NAME_PATTERN = re.compile(
    r"(?i)(?:^test[_-]|^verify[_-]|^smoke[_-]|(?:^|[._-])e2e(?:[._-]|$)|(?:[._-])(?:test|spec)\.(?:[cm]?[jt]sx?|py)$)"
)
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?im)^[ \t]*(?:(?:export[ \t]+)?(?:const|let|var)[ \t]+)?(?P<name>[A-Z0-9_]*(?:TOKEN|PASSWORD|API_KEY|PRIVATE_KEY)[A-Z0-9_]*)[ \t]*(?::[^=\r\n]+)?[ \t]*=[ \t]*(?P<quote>['\"])(?P<value>[^'\"\r\n]{4,})(?P=quote)"
)
BEARER_LITERAL_PATTERN = re.compile(r"(?i)authorization\s*[:=]\s*['\"]?bearer\s+(?P<value>[a-z0-9._~+/-]{12,})")
PEM_PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SAFE_SECRET_VALUE_PATTERN = re.compile(
    r"(?i)^(?:<[^>]+>|\$\{[^}]+\}|%[A-Z0-9_]+%|REDACTED|MASKED|CHANGEME|EXAMPLE|PLACEHOLDER|YOUR[_-]|ENV[_-]|process\.env|os\.environ)"
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _write_json(path: Path, value: Any) -> Path:
    return _write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["status"]
        rows = [{"status": "EMPTY"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False, sort_keys=True) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})
    return path


def _export(out: Path, stem: str, rows: list[dict[str, Any]]) -> dict[str, str]:
    return {
        "json": str(_write_json(out / f"{stem}.json", rows)),
        "csv": str(_write_csv(out / f"{stem}.csv", rows)),
    }


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in EXCLUDED_DIRS and not name.startswith(".")]
        for name in files:
            path = Path(current) / name
            if path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            try:
                if path.stat().st_size <= 2_500_000:
                    found.append(path)
            except OSError:
                continue
    return found


def _safe_read(path: Path) -> tuple[Path, str, str]:
    try:
        raw = path.read_bytes()
        if b"\x00" in raw[:4096]:
            return path, "", "BINARY_SKIPPED"
        return path, raw.decode("utf-8", errors="replace"), "OK"
    except Exception as exc:
        return path, "", f"READ_ERROR:{type(exc).__name__}"


def _is_test(path: Path) -> bool:
    low = path.as_posix().lower()
    return any(token in low for token in ("/tests/", "/test/", "/__tests__/", "/e2e/", "/spec/")) or bool(TEST_NAME_PATTERN.search(path.name))


def _role(path: Path, repo: Path, support_root: Optional[Path]) -> str:
    if support_root is not None:
        try:
            path.resolve().relative_to(support_root.resolve())
            return "CANON_SUPPORT"
        except Exception:
            pass
    low = path.as_posix().lower()
    if any(token in low for token in ("/backup/", "/backups/", "/archive/", "/archives/", "/trash/")):
        return "ARCHIVED_OR_BACKUP"
    if _is_test(path):
        return "TEST"
    if path.name in {"route.ts", "route.js", "route.mjs", "router.py"}:
        return "API_ROUTE"
    if path.name in {"page.tsx", "page.jsx", "page.ts", "page.js", "view.py"}:
        return "UI_ROUTE"
    if path.suffix.lower() == ".md":
        return "DOC"
    try:
        path.resolve().relative_to(repo.resolve())
        return "ACTIVE_SOURCE"
    except Exception:
        return "OTHER"


def _scan_repo(repo: Path, support_root: Optional[Path]) -> list[dict[str, Any]]:
    paths = list(_iter_files(repo))
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_safe_read, path) for path in paths]
        for future in as_completed(futures):
            path, text, status = future.result()
            rows.append({
                "path": public_path(path, repo),
                "name": path.name,
                "role": _role(path, repo, support_root),
                "text": text,
                "readStatus": status,
            })
    rows.sort(key=lambda row: row["path"].lower())
    return rows


def _directory_is_canon(path: Path) -> bool:
    return all((path / rel).is_file() for rel in CATALOG_FILES)


def _zip_prefix(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path) as bundle:
            names = [name.replace("\\", "/") for name in bundle.namelist()]
    except Exception:
        return None
    for name in names:
        if name.endswith(CATALOG_FILES[0]):
            prefix = name[: -len(CATALOG_FILES[0])]
            if all(prefix + rel in names for rel in CATALOG_FILES):
                return prefix
    return None


def _find_support_source(profile: OperationalRuntimeProfile) -> tuple[str, Optional[Path], Optional[Path], str]:
    candidates = list(profile.support_resolver_roots)
    if not candidates:
        candidates = [profile.repo_root / "support-resolver", profile.repo_root / "docs" / "support-resolver"]
    for candidate in candidates:
        if _directory_is_canon(candidate):
            return "directory", candidate.resolve(), None, ""

    zip_candidates: list[Path] = []
    for root in profile.evidence_roots:
        if not root.exists():
            continue
        zip_candidates.extend(sorted(root.glob("**/*support*resolver*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)[:100])
    for candidate in candidates:
        if candidate.suffix.lower() == ".zip" and candidate.exists():
            zip_candidates.append(candidate)
        elif candidate.with_suffix(".zip").exists():
            zip_candidates.append(candidate.with_suffix(".zip"))
    for path in zip_candidates:
        prefix = _zip_prefix(path)
        if prefix is not None:
            return "zip", None, path.resolve(), prefix
    return "missing", None, None, ""


def _source_read_json(kind: str, root: Optional[Path], zip_path: Optional[Path], prefix: str, rel: str) -> Any:
    if kind == "directory" and root:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    if kind == "zip" and zip_path:
        with zipfile.ZipFile(zip_path) as bundle:
            return json.loads(bundle.read(prefix + rel).decode("utf-8"))
    raise FileNotFoundError(rel)


def _secret_risks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in rows:
        if row["role"] in {"CANON_SUPPORT", "ARCHIVED_OR_BACKUP"}:
            continue
        text = row["text"]
        if PEM_PRIVATE_KEY_PATTERN.search(text):
            risks.append({"path": row["path"], "role": row["role"], "status": "BLOCKING_SECRET_EVIDENCE", "patternClass": "PEM_PRIVATE_KEY", "severity": "CRITICAL", "blocking": True})
            continue
        bearer = BEARER_LITERAL_PATTERN.search(text)
        if bearer and not SAFE_SECRET_VALUE_PATTERN.search(bearer.group("value").strip()):
            risks.append({"path": row["path"], "role": row["role"], "status": "REVIEW_CONCRETE_SECRET_LITERAL", "patternClass": "BEARER_LITERAL", "severity": "MEDIUM" if row["role"] in {"TEST", "DOC"} else "HIGH", "blocking": row["role"] not in {"TEST", "DOC"}})
            continue
        assignment = SECRET_ASSIGNMENT_PATTERN.search(text)
        if assignment and not SAFE_SECRET_VALUE_PATTERN.search(assignment.group("value").strip()):
            risks.append({"path": row["path"], "role": row["role"], "status": "REVIEW_CONCRETE_SECRET_LITERAL", "patternClass": "CREDENTIAL_ASSIGNMENT", "severity": "LOW" if row["role"] in {"TEST", "DOC"} else "HIGH", "blocking": row["role"] not in {"TEST", "DOC"}})
    return risks[:100]


def _catalog_rows(obj: Any, preferred_keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [dict(row) if isinstance(row, dict) else {"value": row} for row in obj]
    if isinstance(obj, dict):
        for key in preferred_keys:
            value = obj.get(key)
            if isinstance(value, list):
                return [dict(row) if isinstance(row, dict) else {"value": row} for row in value]
        return [{"key": key, "value": value} for key, value in obj.items() if not isinstance(value, (dict, list))]
    return []


def run_support_resolver_atlas(
    repo_root: str | Path,
    output_dir: str | Path,
    result_root: str | Path | None = None,
    *,
    profile: OperationalRuntimeProfile | None = None,
) -> dict[str, Any]:
    repo = Path(repo_root).expanduser().resolve()
    out = Path(output_dir).expanduser().resolve() / "support_resolver"
    out.mkdir(parents=True, exist_ok=True)
    runtime_profile = profile or resolve_runtime_profile(repo, output_dir, result_root)
    source_kind, support_root, support_zip, prefix = _find_support_source(runtime_profile)

    source_ref = public_path(support_root or support_zip, repo) if (support_root or support_zip) else ""
    source_summary = [{"sourceKind": source_kind, "sourceRef": source_ref, "status": "PASS_CANON_FOUND" if source_kind != "missing" else "BLOCKED_NO_SUPPORT_CANON"}]

    if source_kind == "missing":
        summary = {
            "tool": "code_atlas_support_resolver_consumer",
            "version": VERSION,
            "generatedAt": _now(),
            "status": "BLOCKED_NO_SUPPORT_CANON",
            "decision": "VERIFY_SOURCE_LOCATION",
            "doNotRebuild": True,
            "blockers": ["Configured support-resolver canonical root or archive was not found."],
            "productionCertified": False,
        }
        exports = _export(out, "supportResolverSummary", [summary])
        payload = {
            "supportResolverSummary": [summary],
            "supportCanonicalSource": source_summary,
            "supportCapabilityMatrix": [{"capability": "support_canon", "status": "BLOCKED_MISSING", "decision": "VERIFY_SOURCE_LOCATION"}],
            "supportErrorCodeCoverage": [],
            "supportActionCoverage": [],
            "supportUiRouteMap": [],
            "supportE2eCoverage": [],
            "supportDuplicateImplementations": [],
            "supportDoNotRebuildMap": [],
            "supportContractCoverage": [],
            "supportSecurityRisks": [],
        }
        _write_json(out / "SUPPORT_ATLAS_MANIFEST.json", {**summary, "exports": exports})
        return {"summary": summary, "payload": payload, "exports": exports}

    errors_obj = _source_read_json(source_kind, support_root, support_zip, prefix, CATALOG_FILES[0])
    actions_obj = _source_read_json(source_kind, support_root, support_zip, prefix, CATALOG_FILES[1])
    gates_obj = _source_read_json(source_kind, support_root, support_zip, prefix, CATALOG_FILES[2])
    status_obj = _source_read_json(source_kind, support_root, support_zip, prefix, CATALOG_FILES[3])

    error_rows = _catalog_rows(errors_obj, ("codes", "errors", "items"))
    action_rows = _catalog_rows(actions_obj, ("actions", "items"))
    gate_rows = _catalog_rows(gates_obj, ("gates", "items"))
    status_rows = _catalog_rows(status_obj, ("statuses", "surfaces", "items"))
    repo_rows = _scan_repo(repo, support_root)
    security_risks = _secret_risks(repo_rows)

    active_rows = [row for row in repo_rows if row["role"] in {"ACTIVE_SOURCE", "API_ROUTE", "UI_ROUTE"}]
    tests = [row for row in repo_rows if row["role"] == "TEST"]
    support_terms = tuple({str(row.get("code") or row.get("id") or row.get("name") or "").strip() for row in [*error_rows, *action_rows] if str(row.get("code") or row.get("id") or row.get("name") or "").strip()})
    references = []
    for term in support_terms[:300]:
        source_hits = [row["path"] for row in active_rows if term in row["text"]][:20]
        test_hits = [row["path"] for row in tests if term in row["text"]][:20]
        references.append({"term": term, "activeReferences": source_hits, "testReferences": test_hits, "status": "IMPLEMENTED_AND_TESTED" if source_hits and test_hits else "IMPLEMENTED_UNTESTED" if source_hits else "TEST_ONLY" if test_hits else "CONTRACT_ONLY"})

    blockers = []
    if any(row.get("blocking") for row in security_risks):
        blockers.append("blocking_secret_risk")
    if not error_rows or not action_rows:
        blockers.append("required_support_catalog_empty")

    summary = {
        "tool": "code_atlas_support_resolver_consumer",
        "version": VERSION,
        "generatedAt": _now(),
        "status": "BLOCKED_SUPPORT_RESOLVER_CONTRACT" if blockers else "PASS_SUPPORT_RESOLVER_CONTRACT_OBSERVED",
        "decision": "FIX_OR_VERIFY" if blockers else "VERIFY_RUNTIME_WHEN_REQUIRED",
        "doNotRebuild": True,
        "blockers": blockers,
        "sourceKind": source_kind,
        "sourceRef": source_ref,
        "productionCertified": False,
    }

    exports = {
        "errors": _export(out, "supportErrorCodeCoverage", error_rows),
        "actions": _export(out, "supportActionCoverage", action_rows),
        "gates": _export(out, "supportContractCoverage", gate_rows),
        "statuses": _export(out, "supportSurfaceStatusCoverage", status_rows),
        "references": _export(out, "supportReferenceCoverage", references),
        "security": _export(out, "supportSecurityRisks", security_risks),
        "summary": _export(out, "supportResolverSummary", [summary]),
    }
    payload = {
        "supportResolverSummary": [summary],
        "supportCanonicalSource": source_summary,
        "supportCapabilityMatrix": references,
        "supportErrorCodeCoverage": error_rows,
        "supportActionCoverage": action_rows,
        "supportUiRouteMap": [row for row in repo_rows if row["role"] == "UI_ROUTE"],
        "supportE2eCoverage": [row for row in repo_rows if row["role"] == "TEST"],
        "supportDuplicateImplementations": [],
        "supportDoNotRebuildMap": [],
        "supportContractCoverage": [*gate_rows, *status_rows],
        "supportSecurityRisks": security_risks,
    }
    _write_json(out / "SUPPORT_ATLAS_MANIFEST.json", {**summary, "exports": exports})
    return {"summary": summary, "payload": payload, "exports": exports}


__all__ = ["run_support_resolver_atlas"]
