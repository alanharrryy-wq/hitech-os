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

VERSION = "1.1.0"
MAX_WORKERS = 18
SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts",
    ".json", ".md", ".yaml", ".yml", ".toml", ".css", ".html",
}
EXCLUDED_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "coverage", ".turbo",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "venv", ".venv",
    ".prisma_installer_backups", ".prisma_backups", "reports",
}
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


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _write_json(path: Path, value: Any) -> Path:
    return _write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


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
            cooked = {}
            for key in fields:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    cooked[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
                else:
                    cooked[key] = value
            writer.writerow(cooked)
    return path


def _markdown_table(title: str, rows: list[dict[str, Any]], note: str = "") -> str:
    lines = [f"# {title}", "", f"Generated: `{_now()}`", ""]
    if note:
        lines.extend([note, ""])
    if not rows:
        lines.append("No rows.")
        return "\n".join(lines) + "\n"
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    lines.append("| " + " | ".join(fields) + " |")
    lines.append("| " + " | ".join(["---"] * len(fields)) + " |")
    for row in rows:
        vals = []
        for key in fields:
            value = row.get(key, "")
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, sort_keys=True)
            vals.append(str(value).replace("\n", " ").replace("|", "\\|")[:900])
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def _export(out: Path, stem: str, rows: list[dict[str, Any]], title: str, note: str = "") -> dict[str, str]:
    return {
        "json": str(_write_json(out / f"{stem}.json", rows)),
        "csv": str(_write_csv(out / f"{stem}.csv", rows)),
        "md": str(_write_text(out / f"{stem}.md", _markdown_table(title, rows, note))),
    }


def _app_root(repo_root: Path) -> Path:
    repo_root = repo_root.resolve()
    candidate = repo_root / "apps" / "terminal-de-venta-system"
    if candidate.exists():
        return candidate
    if (repo_root / "products").exists() and (repo_root / "shared").exists():
        return repo_root
    return candidate


def _is_test_artifact(path: Path, low: str) -> bool:
    name = path.name.lower()
    if any(token in low for token in ("/tests/", "/test/", "/__tests__/")):
        return True
    if re.search(r"(?:^|/)(?:e2e|playwright|specs?)(?:/|$)", low):
        return True
    if TEST_NAME_PATTERN.search(name):
        return True
    if any(folder in low for folder in ("/tools/", "/scripts/")) and re.search(r"(?i)(verify|smoke|e2e|test|spec)", name):
        return True
    return False


def _path_role(path: Path, app_root: Path, support_root: Optional[Path]) -> str:
    low = path.as_posix().lower()
    if support_root is not None:
        try:
            path.resolve().relative_to(support_root.resolve())
            return "CANON_SUPPORT"
        except Exception:
            pass
    if any(token in low for token in ("/docs/ops/licscope/changed_files/", "/_chatgpt_", "/backup/", "/backups/", "/trash-old/")):
        return "ARCHIVED_OR_BACKUP"
    if _is_test_artifact(path, low):
        return "TEST"
    if path.name in {"route.ts", "route.js", "route.mjs"}:
        return "API_ROUTE"
    if path.name in {"page.tsx", "page.jsx", "page.ts", "page.js"}:
        return "UI_ROUTE"
    if "/prisma cloud ctr/internal/py/" in low:
        return "ACTIVE_SERVICE_CANON"
    if "/prisma-control-center/" in low:
        return "LEGACY_SERVICE"
    if "/shared/licensing/" in low or "/shared/runtime/" in low:
        return "ACTIVE_CONTRACT"
    if path.suffix.lower() == ".md":
        return "DOC"
    try:
        path.resolve().relative_to(app_root.resolve())
        return "ACTIVE_SOURCE"
    except Exception:
        return "OTHER"


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for name in files:
            path = Path(current) / name
            if path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > 2_500_000:
                    continue
            except OSError:
                continue
            found.append(path)
    return found


def _safe_read(path: Path) -> tuple[Path, str, str]:
    try:
        raw = path.read_bytes()
        if b"\x00" in raw[:4096]:
            return path, "", "BINARY_SKIPPED"
        text = raw.decode("utf-8", errors="replace")
        return path, text, "OK"
    except Exception as exc:
        return path, "", f"READ_ERROR:{type(exc).__name__}"


def _scan_repo(repo_root: Path, support_root: Optional[Path]) -> list[dict[str, Any]]:
    app_root = _app_root(repo_root)
    scan_roots = [app_root]
    quality = app_root / "quality"
    if quality.exists() and quality not in scan_roots:
        scan_roots.append(quality)
    paths: list[Path] = []
    seen: set[str] = set()
    for root in scan_roots:
        for path in _iter_files(root):
            key = str(path.resolve()).lower()
            if key not in seen:
                seen.add(key)
                paths.append(path)
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(_safe_read, path) for path in paths]
        for future in as_completed(futures):
            path, text, status = future.result()
            try:
                rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
            except Exception:
                rel = str(path)
            rows.append({
                "path": rel,
                "abs": str(path),
                "name": path.name,
                "role": _path_role(path, app_root, support_root),
                "text": text,
                "readStatus": status,
            })
    rows.sort(key=lambda row: row["path"].lower())
    return rows


def _find_support_source(repo_root: Path, result_root: Optional[Path]) -> tuple[str, Optional[Path], Optional[Path]]:
    app = _app_root(repo_root)
    dirs = [
        app / "prisma-support-resolver",
        repo_root / "prisma-support-resolver",
        app / "docs" / "ops" / "prisma-support-resolver",
    ]
    for path in dirs:
        if (path / "catalogs" / "support-error-codes.json").exists():
            return "directory", path.resolve(), None
    zip_candidates: list[Path] = []
    if result_root and result_root.exists():
        zip_candidates.extend(sorted(result_root.glob("prisma-support-resolver*.zip"), key=lambda p: p.stat().st_mtime, reverse=True))
    zip_candidates.extend([app / "prisma-support-resolver.zip", repo_root / "prisma-support-resolver.zip"])
    for path in zip_candidates:
        if not path.exists():
            continue
        try:
            with zipfile.ZipFile(path) as zf:
                names = {name.replace("\\", "/") for name in zf.namelist()}
                if any(name.endswith("prisma-support-resolver/catalogs/support-error-codes.json") for name in names):
                    return "zip", None, path.resolve()
        except Exception:
            continue
    return "missing", None, None


def _source_read_json(kind: str, root: Optional[Path], zip_path: Optional[Path], rel: str) -> Any:
    rel = rel.replace("\\", "/").lstrip("/")
    if kind == "directory" and root:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    if kind == "zip" and zip_path:
        with zipfile.ZipFile(zip_path) as zf:
            candidates = [name for name in zf.namelist() if name.replace("\\", "/").endswith("prisma-support-resolver/" + rel)]
            if not candidates:
                raise FileNotFoundError(rel)
            return json.loads(zf.read(candidates[0]).decode("utf-8"))
    raise FileNotFoundError(rel)


def _source_list(kind: str, root: Optional[Path], zip_path: Optional[Path], prefix: str, suffix: str) -> list[str]:
    if kind == "directory" and root:
        base = root / prefix
        return sorted(path.relative_to(root).as_posix() for path in base.rglob(f"*{suffix}") if path.is_file()) if base.exists() else []
    if kind == "zip" and zip_path:
        with zipfile.ZipFile(zip_path) as zf:
            out = []
            for name in zf.namelist():
                norm = name.replace("\\", "/")
                marker = "prisma-support-resolver/"
                if marker not in norm:
                    continue
                rel = norm.split(marker, 1)[1]
                if rel.startswith(prefix.rstrip("/") + "/") and rel.endswith(suffix):
                    out.append(rel)
            return sorted(out)
    return []


def _active(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["role"] in {"ACTIVE_SERVICE_CANON", "ACTIVE_CONTRACT", "ACTIVE_SOURCE", "API_ROUTE", "UI_ROUTE"}]


def _test_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["role"] == "TEST"]


def _count_token(rows: list[dict[str, Any]], token: str) -> tuple[int, list[str]]:
    hits = [row["path"] for row in rows if token in row["text"]]
    return len(hits), hits[:20]


def _contains_any(text: str, tokens: Iterable[str]) -> list[str]:
    low = text.lower()
    return [token for token in tokens if token.lower() in low]


def _candidate_files(rows: list[dict[str, Any]], patterns: Iterable[str], roles: Optional[set[str]] = None) -> list[dict[str, Any]]:
    compiled = [re.compile(pattern, re.I) for pattern in patterns]
    out = []
    for row in rows:
        if roles and row["role"] not in roles:
            continue
        hay = row["path"] + "\n" + row["text"][:100000]
        if any(pattern.search(hay) for pattern in compiled):
            out.append(row)
    return out


def _status_for_reference(active_count: int, test_count: int) -> str:
    if active_count and test_count:
        return "IMPLEMENTED_AND_TESTED"
    if active_count:
        return "IMPLEMENTED_UNTESTED"
    if test_count:
        return "TEST_ONLY"
    return "CONTRACT_ONLY"


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def _secret_risks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in rows:
        if row["role"] in {"CANON_SUPPORT", "ARCHIVED_OR_BACKUP"}:
            continue
        text = row["text"]
        pem = PEM_PRIVATE_KEY_PATTERN.search(text)
        if pem:
            risks.append({
                "path": row["path"], "role": row["role"], "status": "BLOCKING_SECRET_EVIDENCE",
                "patternClass": "PEM_PRIVATE_KEY", "severity": "CRITICAL", "confidence": "HIGH",
                "blocking": True, "lineNumber": _line_number(text, pem.start()),
                "reason": "A private-key PEM header exists in source. Secret values are not exported.",
            })
            continue
        bearer = BEARER_LITERAL_PATTERN.search(text)
        if bearer and not SAFE_SECRET_VALUE_PATTERN.search(bearer.group("value").strip()):
            severity = "MEDIUM" if row["role"] in {"TEST", "DOC"} else "HIGH"
            risks.append({
                "path": row["path"], "role": row["role"], "status": "REVIEW_CONCRETE_SECRET_LITERAL",
                "patternClass": "BEARER_LITERAL", "severity": severity, "confidence": "HIGH",
                "blocking": row["role"] not in {"TEST", "DOC"}, "lineNumber": _line_number(text, bearer.start()),
                "reason": "A concrete bearer-like literal was detected. The literal itself is not exported.",
            })
            continue
        assignment = SECRET_ASSIGNMENT_PATTERN.search(text)
        if assignment:
            value = assignment.group("value").strip()
            if SAFE_SECRET_VALUE_PATTERN.search(value):
                continue
            severity = "LOW" if row["role"] in {"TEST", "DOC"} else "HIGH"
            risks.append({
                "path": row["path"], "role": row["role"], "status": "REVIEW_CONCRETE_SECRET_LITERAL",
                "patternClass": "CREDENTIAL_ASSIGNMENT", "severity": severity, "confidence": "MEDIUM",
                "blocking": row["role"] not in {"TEST", "DOC"}, "lineNumber": _line_number(text, assignment.start()),
                "reason": "A quoted credential-like assignment was detected. The assigned value is not exported.",
            })
    return risks[:100]


def run_support_resolver_atlas(repo_root: str | Path, output_dir: str | Path, result_root: str | Path | None = None) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    out = Path(output_dir).resolve() / "support_resolver"
    out.mkdir(parents=True, exist_ok=True)
    rr = Path(result_root).resolve() if result_root else None
    source_kind, support_root, support_zip = _find_support_source(repo, rr)

    source_summary = [{
        "sourceKind": source_kind,
        "sourcePath": str(support_root or support_zip or ""),
        "status": "PASS_CANON_FOUND" if source_kind != "missing" else "BLOCKED_NO_SUPPORT_CANON",
    }]

    if source_kind == "missing":
        summary = {
            "tool": "code_atlas_support_resolver_consumer",
            "version": VERSION,
            "generatedAt": _now(),
            "status": "BLOCKED_NO_SUPPORT_CANON",
            "decision": "VERIFY_SOURCE_LOCATION",
            "doNotRebuild": True,
            "blockers": ["prisma-support-resolver canonical root or ZIP was not found"],
        }
        exports = _export(out, "supportResolverSummary", [summary], "Support Resolver Summary")
        payload = {
            "supportResolverSummary": [summary],
            "supportCanonicalSource": source_summary,
            "supportCapabilityMatrix": [{"capability": "support_canon", "status": "BLOCKED_MISSING", "decision": "VERIFY_SOURCE_LOCATION"}],
            "supportErrorCodeCoverage": [],
            "supportActionCoverage": [],
            "supportUiRouteMap": [],
            "supportE2eCoverage": [],
            "supportDuplicateImplementations": [],
            "supportDoNotRebuildMap": [{"capability": "Support Resolver", "decision": "DO_NOT_REBUILD", "reason": "Canonical package is known but source location is unavailable to this run."}],
            "supportContractCoverage": [],
            "supportSecurityRisks": [],
        }
        _write_json(out / "SUPPORT_ATLAS_MANIFEST.json", {**summary, "exports": exports})
        return {"summary": summary, "payload": payload, "exports": exports}

    errors_obj = _source_read_json(source_kind, support_root, support_zip, "catalogs/support-error-codes.json")
    actions_obj = _source_read_json(source_kind, support_root, support_zip, "catalogs/resolver-actions.json")
    gates_obj = _source_read_json(source_kind, support_root, support_zip, "catalogs/feature-gates.json")
    status_obj = _source_read_json(source_kind, support_root, support_zip, "catalogs/surface-status-catalog.json")
    errors = list(errors_obj.get("codes", []))
    actions = list(actions_obj.get("actions", []))
    schemas = _source_list(source_kind, support_root, support_zip, "schemas", ".json")
    contracts = _source_list(source_kind, support_root, support_zip, "contracts", ".md")
    case_tests = _source_list(source_kind, support_root, support_zip, "tests/cases", ".json")

    repo_rows = _scan_repo(repo, support_root)
    active_rows = _active(repo_rows)
    test_rows = _test_rows(repo_rows)
    error_catalog_tests = [
        row for row in test_rows
        if any(token in (row["path"] + "\n" + row["text"]).lower() for token in (
            "support-error-codes", "errorcodecount", "error_code_count", "codes.length", "68 codes", "68 códigos"
        ))
    ]
    action_catalog_tests = [
        row for row in test_rows
        if any(token in (row["path"] + "\n" + row["text"]).lower() for token in (
            "resolver-actions", "resolveractioncount", "resolver_action_count", "actions.length", "13 actions", "13 acciones"
        ))
    ]

    error_coverage: list[dict[str, Any]] = []
    for item in errors:
        code = str(item.get("code", ""))
        active_count, active_paths = _count_token(active_rows, code)
        test_count, test_paths = _count_token(test_rows, code)
        catalog_test_paths = [row["path"] for row in error_catalog_tests]
        has_test_evidence = bool(test_count or catalog_test_paths)
        api_count = sum(1 for path in active_paths if "/api/" in path.lower() or path.lower().endswith("_api.py"))
        ui_count = sum(1 for path in active_paths if path.lower().endswith((".tsx", ".jsx", ".css", ".html")))
        error_coverage.append({
            "code": code,
            "category": item.get("category", ""),
            "severity": item.get("severity", ""),
            "activeReferenceCount": active_count,
            "testReferenceCount": test_count,
            "catalogVerifierCount": len(catalog_test_paths),
            "testEvidenceMode": "DIRECT_AND_CATALOG" if test_count and catalog_test_paths else ("DIRECT" if test_count else ("CATALOG_WIDE" if catalog_test_paths else "NONE")),
            "apiReferenceCount": api_count,
            "uiReferenceCount": ui_count,
            "status": _status_for_reference(active_count, int(has_test_evidence)),
            "activePaths": "|".join(active_paths),
            "testPaths": "|".join(test_paths),
            "catalogVerifierPaths": "|".join(catalog_test_paths[:20]),
            "safeActions": "|".join(item.get("safeActions", [])),
        })

    action_coverage: list[dict[str, Any]] = []
    for item in actions:
        action_id = str(item.get("id", ""))
        active_count, active_paths = _count_token(active_rows, action_id)
        test_count, test_paths = _count_token(test_rows, action_id)
        catalog_test_paths = [row["path"] for row in action_catalog_tests]
        has_test_evidence = bool(test_count or catalog_test_paths)
        action_coverage.append({
            "action": action_id,
            "mode": item.get("mode", item.get("authority", "")),
            "mutates": item.get("mutates", item.get("wouldMutate", "")),
            "requiresDryRun": item.get("requiresDryRun", ""),
            "requiresConfirmation": item.get("requiresConfirmation", ""),
            "activeReferenceCount": active_count,
            "testReferenceCount": test_count,
            "catalogVerifierCount": len(catalog_test_paths),
            "testEvidenceMode": "DIRECT_AND_CATALOG" if test_count and catalog_test_paths else ("DIRECT" if test_count else ("CATALOG_WIDE" if catalog_test_paths else "NONE")),
            "status": _status_for_reference(active_count, int(has_test_evidence)),
            "activePaths": "|".join(active_paths),
            "testPaths": "|".join(test_paths),
            "catalogVerifierPaths": "|".join(catalog_test_paths[:20]),
        })

    support_api = [
        row for row in repo_rows
        if row["role"] in {"ACTIVE_SERVICE_CANON", "ACTIVE_SOURCE", "LEGACY_SERVICE"}
        and (
            row["name"].lower() == "support_resolver_api.py"
            or re.search(r"(?m)^\s*class\s+SupportResolver(?:\s|\(|:)", row["text"])
        )
    ]
    route_candidates = _candidate_files(
        repo_rows, [r"support", r"incident", r"customer[-_ ]?setup", r"setup[-_ ]?claim", r"license.*device"],
        {"UI_ROUTE", "API_ROUTE"},
    )
    e2e_candidates = _candidate_files(
        repo_rows, [r"support[-_ ]?resolver", r"customer[-_ ]?setup", r"setup[-_ ]?claim", r"identity[-_ ]?reconciliation", r"incident"],
        {"TEST"},
    )

    ui_route_map = [{
        "path": row["path"],
        "role": row["role"],
        "artifactType": row["role"],
        "status": "ACTIVE",
        "signals": "|".join(_contains_any(row["path"] + " " + row["text"][:60000], ["support", "incident", "customer setup", "customer-setup", "setup_claim", "license", "device"])),
    } for row in route_candidates[:300]]

    flow_tokens = {
        "diagnose": ["diagnose", "/api/support/diagnose"],
        "simulate": ["simulate", "/api/support/simulate"],
        "apply_preflight": ["apply", "preflight", "no_rollback"],
        "export_case": ["export-case", "export_evidence", "support bundle"],
        "identity_reconciliation": ["CROSS_SOURCE_IDENTITY_SPLIT", "identityReconciliation"],
        "setup_claim_or_refresh": ["setup_claim_or_refresh_guided", "setup_claim", "license_refresh"],
        "customer_setup_claim": ["customer-setup/claim", "setup code"],
        "incident_timeline": ["incidents/timeline", "timeline"],
    }
    e2e_coverage = []
    all_test_text = "\n".join(row["text"] for row in e2e_candidates)
    for flow, tokens in flow_tokens.items():
        matched = [token for token in tokens if token.lower() in all_test_text.lower()]
        paths = [row["path"] for row in e2e_candidates if any(token.lower() in row["text"].lower() or token.lower() in row["path"].lower() for token in tokens)]
        dedicated_paths = [path for path in paths if re.search(r"(?i)(?:^|[/_.-])(?:e2e|playwright)(?:[/_.-]|$)", path)]
        status_value = "E2E_TEST_EVIDENCE_FOUND" if dedicated_paths else ("VERIFIER_TEST_EVIDENCE_FOUND" if paths else "MISSING_DEDICATED_TEST_EVIDENCE")
        e2e_coverage.append({
            "flow": flow,
            "status": status_value,
            "matchedSignals": "|".join(matched),
            "paths": "|".join(paths[:30]),
            "dedicatedE2ePaths": "|".join(dedicated_paths[:30]),
        })

    contract_coverage = []
    for rel in schemas + contracts:
        name = Path(rel).name
        stem = Path(rel).stem
        token_candidates = [name, stem, stem.replace(".schema", "")]
        active_hits = [row["path"] for row in active_rows if any(token.lower() in row["text"].lower() for token in token_candidates)]
        test_hits = [row["path"] for row in test_rows if any(token.lower() in row["text"].lower() for token in token_candidates)]
        contract_coverage.append({
            "artifact": rel,
            "kind": "schema" if rel.endswith(".json") else "contract",
            "activeReferenceCount": len(active_hits),
            "testReferenceCount": len(test_hits),
            "status": _status_for_reference(len(active_hits), len(test_hits)),
            "activePaths": "|".join(active_hits[:20]),
            "testPaths": "|".join(test_hits[:20]),
        })

    role_groups = {
        "support_resolver_api": [row for row in support_api if row["role"] in {"ACTIVE_SERVICE_CANON", "ACTIVE_SOURCE", "API_ROUTE", "LEGACY_SERVICE"}],
        "license_ops_api": [row for row in repo_rows if row["name"].lower() == "license_ops_api.py" and row["role"] in {"ACTIVE_SERVICE_CANON", "LEGACY_SERVICE"}],
        "license_ops_console": [row for row in repo_rows if row["name"].lower() == "license_ops_console.js" and row["role"] in {"ACTIVE_SERVICE_CANON", "LEGACY_SERVICE", "ACTIVE_SOURCE"}],
    }
    duplicates = []
    for concept, rows in role_groups.items():
        canon = [row for row in rows if row["role"] == "ACTIVE_SERVICE_CANON"]
        legacy = [row for row in rows if row["role"] == "LEGACY_SERVICE"]
        status = "PASS_SINGLE_CANONICAL"
        if len(canon) > 1:
            status = "BLOCKED_MULTIPLE_CANONICAL_IMPLEMENTATIONS"
        elif canon and legacy:
            status = "KNOWN_CANON_PLUS_DEPRECATED_DUPLICATE"
        elif not canon and legacy:
            status = "BLOCKED_ONLY_LEGACY_IMPLEMENTATION"
        elif not rows:
            status = "MISSING_IMPLEMENTATION"
        duplicates.append({
            "concept": concept,
            "status": status,
            "canonicalPaths": "|".join(row["path"] for row in canon),
            "legacyPaths": "|".join(row["path"] for row in legacy),
            "allPaths": "|".join(row["path"] for row in rows),
        })

    active_paths = {row["path"].replace("\\", "/").lower() for row in active_rows}
    def has_path(fragment: str) -> bool:
        fragment = fragment.replace("\\", "/").lower()
        return any(fragment in path for path in active_paths)

    capability_matrix = [
        {"capability": "canonical_support_root", "status": "DONE", "decision": "USE_AS_IS", "evidence": str(support_root or support_zip)},
        {"capability": "support_error_code_catalog", "status": "DONE" if len(errors) == 68 else "FIX", "decision": "USE_AS_IS" if len(errors) == 68 else "FIX_EXISTING", "evidence": f"codes={len(errors)}"},
        {"capability": "resolver_action_catalog", "status": "DONE" if actions else "FIX", "decision": "USE_AS_IS" if actions else "FIX_EXISTING", "evidence": f"actions={len(actions)}"},
        {"capability": "support_schemas", "status": "DONE" if len(schemas) >= 9 else "FIX", "decision": "USE_AS_IS" if len(schemas) >= 9 else "FIX_EXISTING", "evidence": f"schemas={len(schemas)}"},
        {"capability": "support_resolver_api", "status": "VERIFY" if any(row["role"] == "ACTIVE_SERVICE_CANON" for row in support_api) else "BUILD", "decision": "VERIFY_EXISTING" if support_api else "CREATE_MISSING", "evidence": "|".join(row["path"] for row in support_api[:10])},
        {"capability": "customer_setup_claim_route", "status": "VERIFY" if has_path("customer-setup/claim/route") else "BUILD", "decision": "USE_AND_CONNECT" if has_path("customer-setup/claim/route") else "CREATE_MISSING", "evidence": "products/*/app/api/customer-setup/claim/route"},
        {"capability": "customer_setup_resolve_route", "status": "VERIFY" if has_path("customer-setup/resolve/route") else "BUILD", "decision": "USE_AND_CONNECT" if has_path("customer-setup/resolve/route") else "CREATE_MISSING", "evidence": "products/*/app/api/customer-setup/resolve/route"},
        {"capability": "incidents_route", "status": "VERIFY" if has_path("app/api/incidents/route") else "BUILD", "decision": "USE_AND_CONNECT" if has_path("app/api/incidents/route") else "CREATE_MISSING", "evidence": "products/*/app/api/incidents/route"},
        {"capability": "incidents_timeline_route", "status": "VERIFY" if has_path("app/api/incidents/timeline/route") else "BUILD", "decision": "USE_AND_CONNECT" if has_path("app/api/incidents/timeline/route") else "CREATE_MISSING", "evidence": "products/*/app/api/incidents/timeline/route"},
        {"capability": "support_ui_surface", "status": "VERIFY" if any(row["role"] == "UI_ROUTE" for row in route_candidates) else "BUILD", "decision": "EXTEND_EXISTING" if route_candidates else "CREATE_MISSING", "evidence": "|".join(row["path"] for row in route_candidates if row["role"] == "UI_ROUTE")[:3000]},
        {"capability": "support_resolver_e2e", "status": "VERIFY" if any(row["status"] in {"E2E_TEST_EVIDENCE_FOUND", "VERIFIER_TEST_EVIDENCE_FOUND"} for row in e2e_coverage) else "BUILD", "decision": "VERIFY_EXISTING" if e2e_candidates else "CREATE_MISSING", "evidence": "|".join(row["path"] for row in e2e_candidates[:20])},
        {"capability": "quality_support_redaction", "status": "VERIFY" if has_path("quality/contracts/support-pack-redaction.contract.json") else "BUILD", "decision": "USE_AND_CONNECT" if has_path("quality/contracts/support-pack-redaction.contract.json") else "CREATE_MISSING", "evidence": "quality/contracts/support-pack-redaction.contract.json"},
    ]

    implemented_codes = sum(1 for row in error_coverage if row["activeReferenceCount"] > 0)
    direct_tested_codes = sum(1 for row in error_coverage if row["testReferenceCount"] > 0)
    tested_codes = sum(1 for row in error_coverage if row["testEvidenceMode"] != "NONE")
    implemented_actions = sum(1 for row in action_coverage if row["activeReferenceCount"] > 0)
    direct_tested_actions = sum(1 for row in action_coverage if row["testReferenceCount"] > 0)
    tested_actions = sum(1 for row in action_coverage if row["testEvidenceMode"] != "NONE")
    missing_e2e = [row["flow"] for row in e2e_coverage if row["status"] == "MISSING_DEDICATED_TEST_EVIDENCE"]
    secret_risks = _secret_risks(repo_rows)
    blocking_secret_risks = [row for row in secret_risks if row.get("blocking") is True]

    do_not_rebuild = []
    for row in capability_matrix:
        if row["status"] in {"DONE", "VERIFY"}:
            decision = "DO_NOT_REBUILD_VERIFY_OR_FIX"
        else:
            decision = "BUILD_ONLY_MISSING_SCOPE"
        do_not_rebuild.append({
            "capability": row["capability"],
            "decision": decision,
            "currentStatus": row["status"],
            "reason": row["evidence"],
        })

    blockers = []
    if not any(row["role"] == "ACTIVE_SERVICE_CANON" for row in support_api):
        blockers.append("active canonical support_resolver_api.py not found")
    if implemented_codes < len(errors):
        blockers.append(f"error code behavior coverage incomplete: {implemented_codes}/{len(errors)} active references")
    if tested_codes < len(errors):
        blockers.append(f"error code test evidence incomplete: {tested_codes}/{len(errors)} codes with direct or catalog-wide evidence")
    if implemented_actions < len(actions):
        blockers.append(f"resolver action coverage incomplete: {implemented_actions}/{len(actions)} active references")
    if missing_e2e:
        blockers.append("dedicated E2E evidence missing for: " + ", ".join(missing_e2e))
    if any(row["status"].startswith("BLOCKED_") for row in duplicates):
        blockers.append("multiple concrete implementation files require authority review")
    if blocking_secret_risks:
        blockers.append(f"concrete blocking secret evidence requires review in {len(blocking_secret_risks)} files; values were not exported")

    if not blockers:
        status = "VERIFY_EXISTING_SUPPORT_RESOLVER"
    elif any(row["role"] == "ACTIVE_SERVICE_CANON" for row in support_api):
        status = "PARTIAL_EXISTING_DO_NOT_REBUILD"
    else:
        status = "CONTRACT_READY_IMPLEMENTATION_GAPS"

    summary = {
        "tool": "code_atlas_support_resolver_consumer",
        "version": VERSION,
        "generatedAt": _now(),
        "status": status,
        "decision": "VERIFY_AND_FIX_EXISTING_NOT_REBUILD",
        "doNotRebuild": True,
        "canonicalSourceKind": source_kind,
        "canonicalSource": str(support_root or support_zip),
        "errorCodeCount": len(errors),
        "errorCodesWithActiveReferences": implemented_codes,
        "errorCodesWithTestReferences": direct_tested_codes,
        "errorCodesWithAnyTestEvidence": tested_codes,
        "errorCatalogVerifierCount": len(error_catalog_tests),
        "resolverActionCount": len(actions),
        "actionsWithActiveReferences": implemented_actions,
        "actionsWithTestReferences": direct_tested_actions,
        "actionsWithAnyTestEvidence": tested_actions,
        "actionCatalogVerifierCount": len(action_catalog_tests),
        "schemaCount": len(schemas),
        "contractCount": len(contracts),
        "canonicalCaseCount": len(case_tests),
        "featureGateMappings": len(gates_obj.get("supportMappings", [])),
        "surfaceStatuses": len(status_obj.get("operationStatuses", [])),
        "repoFilesScanned": len(repo_rows),
        "supportRouteCount": len(ui_route_map),
        "supportUiRouteCount": sum(1 for row in ui_route_map if row["artifactType"] == "UI_ROUTE"),
        "supportApiRouteCount": sum(1 for row in ui_route_map if row["artifactType"] == "API_ROUTE"),
        "securityReviewCandidateCount": len(secret_risks),
        "blockingSecretRiskCount": len(blocking_secret_risks),
        "workers": MAX_WORKERS,
        "blockers": blockers,
    }

    exports: dict[str, Any] = {}
    exports["summary"] = _export(out, "supportResolverSummary", [summary], "Support Resolver Summary")
    exports["canonicalSource"] = _export(out, "supportCanonicalSource", source_summary, "Support Canonical Source")
    exports["capabilityMatrix"] = _export(out, "supportCapabilityMatrix", capability_matrix, "Support Capability Matrix", "DONE/VERIFY means do not rebuild; BUILD is restricted to a proven missing scope.")
    exports["errorCodeCoverage"] = _export(out, "supportErrorCodeCoverage", error_coverage, "Support Error Code Coverage")
    exports["actionCoverage"] = _export(out, "supportActionCoverage", action_coverage, "Support Resolver Action Coverage")
    exports["uiRouteMap"] = _export(out, "supportUiRouteMap", ui_route_map, "Support UI and Route Map")
    exports["e2eCoverage"] = _export(out, "supportE2eCoverage", e2e_coverage, "Support E2E Coverage")
    exports["duplicates"] = _export(out, "supportDuplicateImplementations", duplicates, "Support Duplicate Implementations")
    exports["doNotRebuild"] = _export(out, "supportDoNotRebuildMap", do_not_rebuild, "Support Do Not Rebuild Map")
    exports["contracts"] = _export(out, "supportContractCoverage", contract_coverage, "Support Contract and Schema Coverage")
    exports["security"] = _export(out, "supportSecurityRisks", secret_risks, "Support Security Risk Review", "Only paths, line numbers, severity and pattern classes are exported. Secret values and matching source text are never exported.")

    payload = {
        "supportResolverSummary": [summary],
        "supportCanonicalSource": source_summary,
        "supportCapabilityMatrix": capability_matrix,
        "supportErrorCodeCoverage": error_coverage,
        "supportActionCoverage": action_coverage,
        "supportUiRouteMap": ui_route_map,
        "supportE2eCoverage": e2e_coverage,
        "supportDuplicateImplementations": duplicates,
        "supportDoNotRebuildMap": do_not_rebuild,
        "supportContractCoverage": contract_coverage,
        "supportSecurityRisks": secret_risks,
    }
    manifest = {**summary, "exports": exports}
    _write_json(out / "SUPPORT_ATLAS_MANIFEST.json", manifest)
    _write_text(out / "SUPPORT_CAN_PATCH_DECISION.md", "\n".join([
        "# Support Resolver CAN_PATCH Decision",
        "",
        f"Status: `{status}`",
        "",
        "- CAN_REBUILD_SUPPORT_RESOLVER=false",
        "- CAN_VERIFY_EXISTING=true",
        "- CAN_FIX_PROVEN_GAPS=true",
        "- CAN_BUILD_ONLY_MISSING_SCOPE=true",
        "- CAN_DECLARE_FULL_SUPPORT_COVERAGE=false unless every catalog code/action has active and test evidence.",
        "",
    ]))
    return {"summary": summary, "payload": payload, "exports": exports}


__all__ = ["run_support_resolver_atlas", "VERSION", "MAX_WORKERS"]
