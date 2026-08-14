#!/usr/bin/env python3
"""Explicit product adapter that composes neutral repository intelligence with the
existing product authority-mesh evidence bundle.

This module is intentionally product-specific and must remain outside the reusable
neutral-core trust boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from code_atlas.intelligence.authority import AuthorityRequest, discover_authorities
from code_atlas.intelligence.common import digest_json, git_identity, safe_repo_relative, sha256_file, unique
from code_atlas.intelligence.graphs import build_system_graphs
from code_atlas.intelligence.repository import discover_repository
from code_atlas.intelligence.snapshot import build_snapshot

SCHEMA = "prisma_remote_authority_gateway.v2"
VALID_INTENTS = {"DISCOVER", "AUDIT", "VERIFY", "FIX", "BUILD", "CERTIFY"}
VALID_DOMAINS = {
    "", "governance", "security", "data", "runtime", "testing", "legal",
    "commercial", "visual", "tooling", "distribution", "investor",
}
VALID_SURFACES = {"", "governance", "tablet", "pc", "mobile", "chart_lab", "shared_ui"}

CORE_REQUIRED_AUTHORITIES = (
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json",
    "PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json",
    "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md",
    "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
    "tools/code-atlas/CODE_ATLAS_NEUTRALITY_CONTRACT.json",
)

class GatewayError(RuntimeError):
    pass

def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _git_head(repo: Path) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
        timeout=30, shell=False,
    )
    if p.returncode:
        raise GatewayError("GIT_HEAD_UNAVAILABLE:" + p.stderr.strip()[:400])
    return p.stdout.strip()

def _normalize_task(repo: Path, raw: dict[str, Any], index: int) -> dict[str, Any]:
    allowed = {
        "id", "surface", "task", "intent", "domain", "requiredAuthorities",
        "requiredDirectories", "excludedAuthorities", "requiredCapabilities",
        "minimumCoverage", "failOnMissingAuthority",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise GatewayError(f"INVALID_TASK_FIELDS:{index}:{','.join(sorted(unknown))}")
    task_id = str(raw.get("id") or "").strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", task_id):
        raise GatewayError(f"INVALID_TASK_ID:{index}")
    surface = str(raw.get("surface") or "").strip()
    if surface not in VALID_SURFACES:
        raise GatewayError(f"INVALID_SURFACE:{task_id}:{surface}")
    text = str(raw.get("task") or "").strip()
    if not 20 <= len(text) <= 6000:
        raise GatewayError(f"INVALID_TASK_LENGTH:{task_id}")
    intent = str(raw.get("intent") or "AUDIT").upper().strip()
    if intent not in VALID_INTENTS:
        raise GatewayError(f"INVALID_INTENT:{task_id}:{intent}")
    domain = str(raw.get("domain") or "").lower().strip()
    if domain not in VALID_DOMAINS:
        raise GatewayError(f"INVALID_DOMAIN:{task_id}:{domain}")

    def paths(key: str) -> list[str]:
        value = raw.get(key) or []
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise GatewayError(f"INVALID_PATH_LIST:{task_id}:{key}")
        return [safe_repo_relative(repo, item) for item in value]

    capabilities = raw.get("requiredCapabilities") or []
    if not isinstance(capabilities, list) or any(not isinstance(item, str) for item in capabilities):
        raise GatewayError(f"INVALID_CAPABILITY_LIST:{task_id}")
    coverage = raw.get("minimumCoverage", 100)
    try:
        coverage = float(coverage)
    except (TypeError, ValueError) as exc:
        raise GatewayError(f"INVALID_MINIMUM_COVERAGE:{task_id}") from exc
    if not 0 <= coverage <= 100:
        raise GatewayError(f"INVALID_MINIMUM_COVERAGE:{task_id}:{coverage}")
    return {
        "id": task_id,
        "surface": surface,
        "task": text,
        "intent": intent,
        "domain": domain,
        "requiredAuthorities": paths("requiredAuthorities"),
        "requiredDirectories": paths("requiredDirectories"),
        "excludedAuthorities": paths("excludedAuthorities"),
        "requiredCapabilities": unique(capabilities),
        "minimumCoverage": coverage,
        "failOnMissingAuthority": bool(raw.get("failOnMissingAuthority", True)),
    }

def validate_request(repo: Path, raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise GatewayError("INVALID_REQUEST_OBJECT")
    allowed = {"tasks", "requestId", "expectedHead", "profile", "schemaVersion"}
    unknown = set(raw) - allowed
    if unknown:
        raise GatewayError("INVALID_REQUEST_FIELDS:" + ",".join(sorted(unknown)))
    tasks = raw.get("tasks")
    if not isinstance(tasks, list) or not 2 <= len(tasks) <= 12:
        raise GatewayError("TASK_COUNT_MUST_BE_2_TO_12")
    normalized = [_normalize_task(repo, item, i) for i, item in enumerate(tasks, 1) if isinstance(item, dict)]
    if len(normalized) != len(tasks):
        raise GatewayError("TASK_ENTRY_MUST_BE_OBJECT")
    ids = [task["id"] for task in normalized]
    if len(ids) != len(set(ids)):
        raise GatewayError("DUPLICATE_TASK_ID")
    expected = str(raw.get("expectedHead") or "").strip()
    head = _git_head(repo)
    if expected and expected != head:
        raise GatewayError(f"EXPECTED_HEAD_MISMATCH:{expected}:{head}")
    canonical = {
        "schemaVersion": SCHEMA,
        "expectedHead": expected or head,
        "profile": str(raw.get("profile") or "prisma"),
        "tasks": normalized,
    }
    canonical["requestDigest"] = hashlib.sha256(
        json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return canonical

def _capability_records(repo: Path) -> dict[str, dict[str, Any]]:
    base = repo / "PRISMA Factory Ledger"
    sources = [
        base / "PRISMA_FACTORY_LEDGER.json",
        base / "PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json",
        base / "PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json",
    ]
    records: dict[str, dict[str, Any]] = {}
    for path in sources:
        if not path.is_file():
            continue
        try:
            raw = _read_json(path)
        except Exception:
            continue
        if path.name == "PRISMA_FACTORY_LEDGER.json":
            for row in raw.get("capabilities", []) if isinstance(raw, dict) else []:
                if isinstance(row, dict) and row.get("id"):
                    records.setdefault(str(row["id"]), {})["ledger"] = row
        elif path.name.endswith("DO_NOT_REBUILD_MAP.json"):
            for section in ("doNotRebuild", "verifyOrFix"):
                value = raw.get(section, {}) if isinstance(raw, dict) else {}
                if isinstance(value, dict):
                    for cid, row in value.items():
                        records.setdefault(str(cid), {})["doNotRebuildMap"] = {"section": section, "value": row}
        elif path.name.endswith("REGISTRATION_INDEX.json"):
            value = raw.get("registrations", {}) if isinstance(raw, dict) else {}
            if isinstance(value, dict):
                for cid, row in value.items():
                    records.setdefault(str(cid), {})["registration"] = row
    return records

def _resolve_capabilities(repo: Path, requested: list[str]) -> dict[str, Any]:
    records = _capability_records(repo)
    rows = []
    missing = []
    for cid in requested:
        if cid in records:
            rows.append({"id": cid, "state": "FOUND", "sources": sorted(records[cid])})
        else:
            rows.append({"id": cid, "state": "MISSING", "sources": []})
            missing.append(cid)
    return {"requested": requested, "rows": rows, "missing": missing}

def preflight(repo: Path, request_path: Path, out_dir: Path) -> dict[str, Any]:
    raw = _read_json(request_path)
    request = validate_request(repo, raw)
    inventory = discover_repository(repo, workers=18)
    lanes = []
    union_candidates: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    capability_summary = {}
    for task in request["tasks"]:
        required = unique([*CORE_REQUIRED_AUTHORITIES, *task["requiredAuthorities"]])
        authority_request = AuthorityRequest(
            required_authorities=tuple(required),
            required_directories=tuple(task["requiredDirectories"]),
            excluded_authorities=tuple(task["excludedAuthorities"]),
            intent=task["intent"],
            domain=task["domain"],
            fail_on_missing=task["failOnMissingAuthority"],
        )
        try:
            authorities = discover_authorities(repo, inventory, request=authority_request)
        except Exception as exc:
            blockers.append(f"{task['id']}:AUTHORITY:{type(exc).__name__}:{exc}")
            authorities = discover_authorities(
                repo, inventory,
                request=AuthorityRequest(
                    required_authorities=tuple(required),
                    required_directories=tuple(task["requiredDirectories"]),
                    excluded_authorities=tuple(task["excludedAuthorities"]),
                    intent=task["intent"], domain=task["domain"], fail_on_missing=False,
                ),
            )
        coverage = float(authorities.get("coverage", {}).get("resolvedPercent") or 0)
        if coverage < task["minimumCoverage"]:
            blockers.append(f"{task['id']}:COVERAGE:{coverage}<{task['minimumCoverage']}")
        capabilities = _resolve_capabilities(repo, task["requiredCapabilities"])
        if capabilities["missing"]:
            blockers.append(f"{task['id']}:CAPABILITY_MISSING:{','.join(capabilities['missing'])}")
        capability_summary[task["id"]] = capabilities
        for row in authorities.get("candidates") or []:
            if row.get("path"):
                existing = union_candidates.get(row["path"])
                if existing is None or int(row.get("score") or 0) > int(existing.get("score") or 0):
                    union_candidates[row["path"]] = row
        lane_dir = out_dir / "lanes" / task["id"]
        _write_json(lane_dir / "authority_discovery.json", authorities)
        composed = {
            "kind": "PRISMA_AUTHORITY_READSET",
            "version": "universal-intelligence-v1",
            "taskId": task["id"],
            "task": task["task"],
            "intent": task["intent"],
            "domain": task["domain"],
            "surface": task["surface"],
            "repoHead": inventory.get("identity", {}).get("head"),
            "repoTree": inventory.get("identity", {}).get("tree"),
            "requestDigest": request["requestDigest"],
            "requiredAuthorities": required,
            "requiredDirectories": task["requiredDirectories"],
            "requiredCapabilities": task["requiredCapabilities"],
            "coverage": authorities.get("coverage"),
            "selected_files": [
                {
                    "path": row.get("path"),
                    "state": row.get("state"),
                    "score": row.get("score"),
                    "sha256": row.get("contentSha256"),
                    "whySelected": row.get("whySelected"),
                    "doesNotProve": row.get("doesNotProve"),
                }
                for row in authorities.get("candidates") or []
                if row.get("state") != "MISSING"
            ],
            "missing": authorities.get("missingRequired") or [],
            "profileRule": "EXPECTATIONS_ONLY_NOT_FACTS",
            "semanticRetrievalRule": "DISCOVERY_NOT_PROOF",
            "derivedIndexAuthoritative": False,
            "readOnly": True,
        }
        _write_json(lane_dir / "AUTHORITY_READSET.lock.json", composed)
        lanes.append({
            "id": task["id"],
            "coverage": authorities.get("coverage"),
            "missing": authorities.get("missingRequired") or [],
            "capabilities": capabilities,
            "authorityReadset": f"lanes/{task['id']}/AUTHORITY_READSET.lock.json",
        })

    union_authorities = {
        "candidates": sorted(union_candidates.values(), key=lambda row: (-int(row.get("score") or 0), str(row.get("path")))),
        "conflicts": {},
    }
    graphs = build_system_graphs(repo, inventory, union_authorities)
    snapshot = build_snapshot(
        repo, inventory, union_authorities,
        profile_id=request["profile"], profile_version=SCHEMA, request_digest=request["requestDigest"],
    )
    _write_json(out_dir / "repository_inventory.json", inventory)
    _write_json(out_dir / "system_graphs.json", graphs)
    _write_json(out_dir / "portable_snapshot.json", snapshot)
    _write_json(out_dir / "capability_requirements.json", capability_summary)
    legacy_spec = {"tasks": [{"id": t["id"], "surface": t["surface"], "task": t["task"]} for t in request["tasks"]]}
    _write_json(out_dir / "legacy_tasks.json", legacy_spec)
    manifest = {
        "schemaVersion": SCHEMA,
        "status": "PASS_PREFLIGHT" if not blockers else "BLOCKED_PREFLIGHT",
        "requestDigest": request["requestDigest"],
        "expectedHead": request["expectedHead"],
        "repoHead": inventory.get("identity", {}).get("head"),
        "repoTree": inventory.get("identity", {}).get("tree"),
        "physicalCoverage": inventory.get("physicalCoverage"),
        "semanticCoverage": inventory.get("semanticCoverage"),
        "lanes": lanes,
        "blockers": blockers,
        "readOnly": True,
        "productionCertified": False,
    }
    _write_json(out_dir / "PREFLIGHT_MANIFEST.json", manifest)
    _write_json(out_dir / "normalized_request.json", request)
    if blockers:
        raise GatewayError("PREFLIGHT_BLOCKED:" + "|".join(blockers[:20]))
    return manifest

def _find_parallel_result(path: Path) -> Path:
    if path.is_file() and path.suffix.lower() == ".zip":
        return path
    matches = sorted(path.glob("*_result.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not matches:
        raise GatewayError(f"PARALLEL_RESULT_NOT_FOUND:{path}")
    return matches[0]

def _parallel_evidence(mesh_zip: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(mesh_zip) as bundle:
        names = set(bundle.namelist())
        for required in ("PARALLEL_CERTIFICATION.json", "REPO_DRIFT_REPORT.json"):
            if required not in names:
                raise GatewayError(f"LEGACY_MESH_EVIDENCE_MISSING:{required}")
        certification = json.loads(bundle.read("PARALLEL_CERTIFICATION.json").decode("utf-8"))
        drift = json.loads(bundle.read("REPO_DRIFT_REPORT.json").decode("utf-8"))
        if certification.get("status") != "PASS" or not certification.get("read_only_repo"):
            raise GatewayError("LEGACY_MESH_CERTIFICATION_NOT_PASS")
        if not drift.get("stable") or drift.get("changed_count") not in (0, None):
            raise GatewayError("LEGACY_MESH_REPO_DRIFT")
        for name in bundle.namelist():
            match = re.fullmatch(r"tasks/([^/]+)/authority_mesh/\.governance/current/AUTHORITY_READSET\.lock\.json", name)
            if not match:
                continue
            rows[match.group(1)] = json.loads(bundle.read(name).decode("utf-8"))
    return rows, certification, drift

def compose(repo: Path, request_path: Path, preflight_dir: Path, mesh_result: Path, out_dir: Path) -> dict[str, Any]:
    request = validate_request(repo, _read_json(request_path))
    preflight_manifest = _read_json(preflight_dir / "PREFLIGHT_MANIFEST.json")
    if preflight_manifest.get("status") != "PASS_PREFLIGHT":
        raise GatewayError("PREFLIGHT_NOT_PASS")
    if preflight_manifest.get("requestDigest") != request["requestDigest"]:
        raise GatewayError("PREFLIGHT_REQUEST_DIGEST_MISMATCH")
    head = _git_head(repo)
    if head != preflight_manifest.get("repoHead"):
        raise GatewayError(f"HEAD_DRIFT_AFTER_PREFLIGHT:{preflight_manifest.get('repoHead')}:{head}")
    mesh_zip = _find_parallel_result(mesh_result)
    legacy, certification, drift = _parallel_evidence(mesh_zip)
    task_ids = {task["id"] for task in request["tasks"]}
    missing_legacy = sorted(task_ids - set(legacy))
    if missing_legacy:
        raise GatewayError("LEGACY_MESH_TASK_MISSING:" + ",".join(missing_legacy))
    for task in request["tasks"]:
        lane_readset = _read_json(preflight_dir / "lanes" / task["id"] / "AUTHORITY_READSET.lock.json")
        if lane_readset.get("repoHead") != head:
            raise GatewayError(f"LANE_HEAD_DRIFT:{task['id']}")
        legacy_head = ((legacy[task["id"]].get("git_state") or {}).get("head") or {}).get("stdout", "").strip()
        if legacy_head != head:
            raise GatewayError(f"LEGACY_HEAD_DRIFT:{task['id']}:{legacy_head}:{head}")

    out_dir.mkdir(parents=True, exist_ok=True)
    authority_dir = out_dir / "authority"
    shutil.copytree(preflight_dir, authority_dir, dirs_exist_ok=True)
    shutil.copy2(mesh_zip, out_dir / "legacy_surface_mesh.zip")
    report = {
        "schemaVersion": SCHEMA,
        "status": "PASS_COMPOSED_AUTHORITY_MESH",
        "requestDigest": request["requestDigest"],
        "repoHead": head,
        "repoTree": preflight_manifest.get("repoTree"),
        "laneCount": len(request["tasks"]),
        "neutralAuthorityPreflight": "authority/PREFLIGHT_MANIFEST.json",
        "legacySurfaceMesh": "legacy_surface_mesh.zip",
        "authoritySourceOfTruth": "authority/lanes/<taskId>/AUTHORITY_READSET.lock.json",
        "legacyMeshRole": "PRISMA_SURFACE_AND_LAYER_EVIDENCE",
        "legacyCertificationRunId": certification.get("run_id"),
        "legacyRepoDriftStable": bool(drift.get("stable")),
        "profileMayInventTruth": False,
        "semanticRetrievalIsProof": False,
        "derivedIndexAuthoritative": False,
        "readOnly": True,
        "productionCertified": False,
    }
    _write_json(out_dir / "PRISMA_MESH_GATEWAY_REPORT.json", report)
    manifest_files = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        manifest_files.append({
            "path": path.relative_to(out_dir).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
    _write_json(out_dir / "MANIFEST.json", {"report": report, "files": manifest_files})
    final = out_dir.parent / "prisma-automesh-composed-result.zip"
    with zipfile.ZipFile(final, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as bundle:
        for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
            bundle.write(path, path.relative_to(out_dir).as_posix())
    report["artifact"] = str(final)
    report["artifactSha256"] = sha256_file(final)
    return report

def _main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p1 = sub.add_parser("preflight")
    p1.add_argument("--repo", required=True)
    p1.add_argument("--request", required=True)
    p1.add_argument("--out", required=True)
    p2 = sub.add_parser("compose")
    p2.add_argument("--repo", required=True)
    p2.add_argument("--request", required=True)
    p2.add_argument("--preflight", required=True)
    p2.add_argument("--mesh-result", required=True)
    p2.add_argument("--out", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.command == "preflight":
        result = preflight(repo, Path(args.request), Path(args.out))
    else:
        result = compose(repo, Path(args.request), Path(args.preflight), Path(args.mesh_result), Path(args.out))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(_main())
