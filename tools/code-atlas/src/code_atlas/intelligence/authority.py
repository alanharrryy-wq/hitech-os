from __future__ import annotations

import fnmatch
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .common import digest_json, safe_repo_relative, unique

AUTHORITY_STATES = (
    "DISCOVERED", "CANDIDATE", "SUPPORTED", "AUTHORITATIVE",
    "CONFLICTED", "STALE", "MISSING",
)
DECLARATION_FILES = (
    ".code-atlas/authority.json",
    ".code-atlas/authorities.json",
)
CANDIDATE_NAMES = {
    "AGENTS.md": 84,
    "CODEOWNERS": 82,
    "SECURITY.md": 76,
    "CONTRIBUTING.md": 62,
    "README.md": 48,
    "LICENSE": 44,
    "NOTICE": 40,
    "pyproject.toml": 42,
    "package.json": 42,
    "schema.prisma": 68,
}
PATH_SIGNALS = (
    ("governance", 26), ("policy", 22), ("contract", 22), ("canonical", 24),
    ("architecture", 18), ("schema", 18), ("workflow", 14), ("migration", 12),
)
DOMAIN_TERMS = {
    "governance": {"governance", "policy", "contract", "owner", "authority"},
    "security": {"security", "auth", "permission", "secret", "threat"},
    "data": {"schema", "database", "migration", "orm", "sql", "persistence"},
    "runtime": {"deploy", "runtime", "container", "worker", "service", "infra"},
    "testing": {"test", "e2e", "qa", "coverage", "verification"},
    "legal": {"license", "terms", "privacy", "trademark", "copyright"},
    "commercial": {"pricing", "billing", "plan", "customer", "revenue"},
    "visual": {"css", "style", "component", "ui", "theme", "visual"},
}

class AuthorityRequirementError(RuntimeError):
    pass

@dataclass(frozen=True)
class AuthorityRequest:
    required_authorities: tuple[str, ...] = ()
    required_directories: tuple[str, ...] = ()
    excluded_authorities: tuple[str, ...] = ()
    intent: str = "DISCOVER"
    domain: str = ""
    fail_on_missing: bool = True

def _path_score(rel: str, domain: str) -> tuple[int, list[str]]:
    path = Path(rel)
    low = rel.lower()
    score = CANDIDATE_NAMES.get(path.name, 0)
    reasons: list[str] = []
    if score:
        reasons.append(f"name:{path.name}")
    for signal, value in PATH_SIGNALS:
        if signal in low:
            score += value
            reasons.append(f"path:{signal}")
    terms = DOMAIN_TERMS.get(domain.lower(), set())
    hits = sorted(term for term in terms if term in low)
    if hits:
        score += min(40, len(hits) * 10)
        reasons.extend(f"domain:{term}" for term in hits)
    if "/archive/" in f"/{low}/" or "/backup/" in f"/{low}/":
        score -= 35
        reasons.append("historical-penalty")
    if "/generated/" in f"/{low}/":
        score -= 25
        reasons.append("generated-penalty")
    return score, reasons

def _load_declarations(repo: Path) -> tuple[list[dict[str, Any]], list[str]]:
    declarations: list[dict[str, Any]] = []
    errors: list[str] = []
    for rel in DECLARATION_FILES:
        path = repo / rel
        if not path.is_file():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            entries = raw.get("authorities") if isinstance(raw, dict) else None
            if not isinstance(entries, list):
                raise ValueError("authorities must be a list")
            for item in entries:
                if not isinstance(item, dict):
                    continue
                declared = str(item.get("path") or "").strip()
                scope = str(item.get("scope") or "*").strip()
                if not declared:
                    continue
                normalized = safe_repo_relative(repo, declared)
                declarations.append({
                    "declarationFile": rel,
                    "path": normalized,
                    "scope": scope,
                    "kind": str(item.get("kind") or "repo-declared"),
                    "priority": int(item.get("priority") or 0),
                })
        except Exception as exc:
            errors.append(f"{rel}:{type(exc).__name__}:{exc}")
    return declarations, errors

def _profile_expectations(profile_metadata: dict[str, Any] | None) -> list[str]:
    if not isinstance(profile_metadata, dict):
        return []
    values = profile_metadata.get("authorityHints") or profile_metadata.get("authorityExpectations") or []
    if isinstance(values, str):
        values = [values]
    return unique(values if isinstance(values, list) else [])

def _expand_directories(repo: Path, rows: list[dict[str, Any]], directories: Iterable[str]) -> tuple[list[str], list[str]]:
    paths = {row["path"] for row in rows}
    expanded: list[str] = []
    missing: list[str] = []
    for raw in directories:
        rel = safe_repo_relative(repo, raw)
        prefix = rel.rstrip("/") + "/"
        matches = sorted(p for p in paths if p == rel or p.startswith(prefix))
        if matches:
            expanded.extend(matches)
        else:
            missing.append(rel)
    return unique(expanded), unique(missing)

def discover_authorities(
    repo_root: str | Path,
    inventory: dict[str, Any],
    *,
    request: AuthorityRequest | None = None,
    profile_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    request = request or AuthorityRequest()
    files = inventory.get("files") or []
    file_by_path = {row["path"]: row for row in files if isinstance(row, dict) and row.get("path")}
    required = [safe_repo_relative(repo, p) for p in request.required_authorities]
    excluded = {safe_repo_relative(repo, p) for p in request.excluded_authorities}
    expanded, missing_dirs = _expand_directories(repo, files, request.required_directories)
    required_all = unique([*required, *expanded])
    declarations, declaration_errors = _load_declarations(repo)
    declared_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    declared_scope: dict[str, list[str]] = defaultdict(list)
    for item in declarations:
        declared_by_path[item["path"]].append(item)
        declared_scope[item["scope"]].append(item["path"])
    conflicts = {
        scope: sorted(set(paths))
        for scope, paths in declared_scope.items()
        if len(set(paths)) > 1
    }

    profile_hints = _profile_expectations(profile_metadata)
    profile_hint_set = set()
    for raw in profile_hints:
        try:
            profile_hint_set.add(safe_repo_relative(repo, raw))
        except ValueError:
            continue

    missing_declared = sorted(path for path in declared_by_path if path not in file_by_path)
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rel, row in file_by_path.items():
        score, reasons = _path_score(rel, request.domain)
        explicitly_required = rel in required_all
        declared = declared_by_path.get(rel, [])
        hinted = rel in profile_hint_set
        if not (score > 0 or explicitly_required or declared or hinted):
            continue
        state = "CANDIDATE"
        if declared and (row.get("contentSha256") or row.get("fileSha256")):
            state = "AUTHORITATIVE"
        elif explicitly_required and (row.get("contentSha256") or row.get("fileSha256")):
            state = "SUPPORTED"
        elif hinted:
            state = "CANDIDATE"
        if any(rel in paths for paths in conflicts.values()):
            state = "CONFLICTED"
        if rel in excluded:
            continue
        why = list(reasons)
        if explicitly_required:
            why.insert(0, "required-by-task")
            score += 10000
        if declared:
            why.insert(0, "repo-declared-authority")
            score += 20000 + max((int(x.get("priority") or 0) for x in declared), default=0)
        if hinted:
            why.append("profile-expectation-not-proof")
            score += 5
        candidates.append({
            "path": rel,
            "state": state,
            "score": score,
            "whySelected": unique(why),
            "contentSha256": (row.get("contentSha256") or row.get("fileSha256")),
            "historical": bool(row.get("historical")),
            "generated": bool(row.get("generated")),
            "declarations": declared,
            "profileHint": hinted,
            "doesNotProve": [
                "Repository-external organizational authority.",
                "Freshness beyond the captured repository snapshot.",
            ],
        })
        seen.add(rel)

    missing_required = [rel for rel in required if rel not in file_by_path]
    missing_expanded = missing_dirs
    for rel in missing_required:
        candidates.append({
            "path": rel, "state": "MISSING", "score": 10000,
            "whySelected": ["required-by-task", "missing"],
            "contentSha256": None, "historical": False, "generated": False,
            "declarations": [], "profileHint": rel in profile_hint_set,
            "doesNotProve": [],
        })
    for rel in missing_declared:
        if rel in {x["path"] for x in candidates}:
            continue
        candidates.append({
            "path": rel, "state": "MISSING", "score": 20000,
            "whySelected": ["repo-declared-authority", "missing"],
            "contentSha256": None, "historical": False, "generated": False,
            "declarations": declared_by_path.get(rel, []), "profileHint": rel in profile_hint_set,
            "doesNotProve": [],
        })
    for rel in sorted(profile_hint_set - set(file_by_path)):
        if rel in {x["path"] for x in candidates}:
            continue
        candidates.append({
            "path": rel, "state": "MISSING", "score": 5,
            "whySelected": ["profile-expectation-not-proof", "missing"],
            "contentSha256": None, "historical": False, "generated": False,
            "declarations": [], "profileHint": True,
            "doesNotProve": [],
        })

    candidates.sort(key=lambda row: (-int(row["score"]), row["path"]))
    missing = unique([*missing_required, *missing_expanded, *missing_declared])
    coverage = {
        "requiredAuthorities": len(required),
        "requiredAuthoritiesResolved": len(required) - len(missing_required),
        "requiredAuthoritiesMissing": len(missing_required),
        "requiredDirectories": len(tuple(request.required_directories)),
        "requiredDirectoriesExpanded": len(tuple(request.required_directories)) - len(missing_dirs),
        "requiredDirectoriesMissing": len(missing_dirs),
        "resolvedPercent": round(
            100 * ((len(required) - len(missing_required)) + (len(tuple(request.required_directories)) - len(missing_dirs)))
            / max(1, len(required) + len(tuple(request.required_directories))), 4
        ) if (required or tuple(request.required_directories)) else 100.0,
    }
    result = {
        "schemaVersion": "code_atlas_authority_discovery.v1",
        "states": list(AUTHORITY_STATES),
        "intent": request.intent,
        "domain": request.domain,
        "profileExpectations": profile_hints,
        "profileRule": "EXPECTATIONS_ONLY_NOT_FACTS",
        "declarations": declarations,
        "declarationErrors": declaration_errors,
        "missingDeclaredAuthorities": missing_declared,
        "conflicts": conflicts,
        "candidates": candidates,
        "coverage": coverage,
        "missingRequired": missing,
        "requestDigest": digest_json({
            "requiredAuthorities": required,
            "requiredDirectories": list(request.required_directories),
            "excludedAuthorities": sorted(excluded),
            "intent": request.intent,
            "domain": request.domain,
            "failOnMissing": request.fail_on_missing,
        }),
        "readOnly": True,
        "productionCertified": False,
    }
    if request.fail_on_missing and missing:
        raise AuthorityRequirementError(
            "REQUIRED_AUTHORITY_MISSING:" + ",".join(missing)
        )
    return result

def semantic_retrieve(
    query: str,
    authority_result: dict[str, Any],
    *,
    limit: int = 20,
) -> dict[str, Any]:
    terms = {x.lower() for x in re.findall(r"[\w.-]{3,}", query, flags=re.UNICODE)}
    ranked: list[dict[str, Any]] = []
    for row in authority_result.get("candidates") or []:
        path_terms = set(re.findall(r"[\w.-]{3,}", str(row.get("path", "")).lower(), flags=re.UNICODE))
        reason_terms = set()
        for reason in row.get("whySelected") or []:
            reason_terms.update(re.findall(r"[\w.-]{3,}", str(reason).lower(), flags=re.UNICODE))
        overlap = len(terms & (path_terms | reason_terms))
        if overlap or not terms:
            ranked.append({
                "path": row.get("path"),
                "state": row.get("state"),
                "evidenceSha256": (row.get("contentSha256") or row.get("fileSha256")),
                "score": int(row.get("score") or 0) + overlap * 25,
                "confidence": "supported" if row.get("state") in {"SUPPORTED", "AUTHORITATIVE"} else "candidate",
                "doesNotProve": row.get("doesNotProve") or [],
            })
    ranked.sort(key=lambda item: (-item["score"], str(item["path"])))
    return {
        "query": query,
        "results": ranked[: max(1, min(100, int(limit)))],
        "retrievalRule": "SEMANTIC_RETRIEVAL_DISCOVERS_EVIDENCE_NOT_TRUTH",
        "productionCertified": False,
    }
