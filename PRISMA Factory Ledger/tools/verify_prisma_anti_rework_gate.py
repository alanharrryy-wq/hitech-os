#!/usr/bin/env python3
"""Universal fail-closed PRISMA Factory Ledger anti-rework gate.

PRISMA_FACTORY_LEDGER.json is the only canonical capability truth. The DNR and
registration indexes are supplemental reconciliation evidence and never create
a capability by themselves.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "prisma.factory-ledger.anti-rework-gate.v1"
RESULT_SCHEMA = "prisma.factory-ledger.anti-rework-decision.v1"
CLASSIFICATIONS = {"DONE", "VERIFY", "FIX", "BUILD", "EXTERNAL"}
ACTIONS = {"REUSE", "VERIFY", "ADVANCE", "FIX", "BUILD", "REBUILD", "EXTERNAL"}
MODES = {"PROPOSAL", "MUTATION"}
AUTH = {
    "ledger": Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json"),
    "dnr": Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_DO_NOT_REBUILD_MAP.json"),
    "registration": Path("PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_REGISTRATION_INDEX.json"),
    "evidence": Path("PRISMA Factory Ledger/PRISMA_EVIDENCE_INDEX.json"),
}

class GateError(RuntimeError):
    pass

def root() -> Path:
    here = Path.cwd().resolve()
    for p in [here, *here.parents, *Path(__file__).resolve().parents]:
        if (p / ".git").exists() and (p / AUTH["ledger"]).is_file():
            return p
    raise GateError("REPO_ROOT_NOT_FOUND")

def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, encoding="utf-8",
                       errors="replace", timeout=30, check=False)
    if p.returncode:
        raise GateError("GIT_FAILED:" + " ".join(args) + ":" + p.stderr.strip()[:300])
    return p.stdout.strip()

def read_authority(repo: Path) -> dict[str, Any]:
    missing = [str(rel) for rel in AUTH.values() if not (repo / rel).is_file()]
    if missing:
        raise GateError("AUTHORITY_FILE_MISSING:" + ",".join(missing))
    out = {name: load(repo / rel) for name, rel in AUTH.items()}
    out["digests"] = {name: sha(repo / rel) for name, rel in AUTH.items()}
    return out

def authority_dirty(repo: Path) -> list[str]:
    raw = git(repo, "status", "--porcelain", "--", *[p.as_posix() for p in AUTH.values()])
    return [line for line in raw.splitlines() if line.strip()]

def canonical_records(ledger: Any) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    if not isinstance(ledger, dict) or not isinstance(ledger.get("capabilities"), list):
        return {}, ["LEDGER_CAPABILITIES_LIST_REQUIRED"]
    records: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(ledger["capabilities"]):
        if not isinstance(row, dict):
            errors.append(f"LEDGER_CAPABILITY_OBJECT_REQUIRED:{i}")
            continue
        cid = str(row.get("id") or "").strip()
        if not cid:
            errors.append(f"LEDGER_CAPABILITY_ID_REQUIRED:{i}")
            continue
        if cid in records:
            errors.append("DUPLICATE_CAPABILITY_ID:" + cid)
            continue
        records[cid] = row
        cls = row.get("classification")
        if cls not in CLASSIFICATIONS:
            errors.append(f"INVALID_CLASSIFICATION:{cid}:{cls}")
        if not row.get("status"):
            errors.append("STATUS_REQUIRED:" + cid)
        if not isinstance(row.get("doNotRebuild"), bool):
            errors.append("DNR_BOOL_REQUIRED:" + cid)
        if not row.get("nextGate"):
            errors.append("NEXT_GATE_REQUIRED:" + cid)
        if not isinstance(row.get("evidence"), list) or not row.get("evidence"):
            errors.append("EVIDENCE_REQUIRED:" + cid)
        if not isinstance(row.get("doesNotProve"), list) or not row.get("doesNotProve"):
            errors.append("DOES_NOT_PROVE_REQUIRED:" + cid)
        if cls == "BUILD" and row.get("doNotRebuild") is True:
            errors.append("CONTRADICTION_BUILD_DNR:" + cid)
        if cls == "EXTERNAL" and row.get("status") != "EXTERNAL_BLOCKED":
            errors.append("EXTERNAL_STATUS_CONTRADICTION:" + cid)
    return records, errors

def supplemental(authority: dict[str, Any], cid: str) -> dict[str, Any]:
    dnr_root = authority.get("dnr") if isinstance(authority.get("dnr"), dict) else {}
    reg_root = authority.get("registration") if isinstance(authority.get("registration"), dict) else {}
    section = None
    dnr_row = None
    for name in ("doNotRebuild", "verifyOrFix"):
        rows = dnr_root.get(name)
        if isinstance(rows, dict) and cid in rows:
            section, dnr_row = name, rows[cid]
            break
    regs = reg_root.get("registrations") if isinstance(reg_root, dict) else None
    return {
        "dnrSection": section,
        "dnr": dnr_row,
        "registration": regs.get(cid) if isinstance(regs, dict) else None,
    }

def supplemental_has(authority: dict[str, Any], cid: str) -> bool:
    s = supplemental(authority, cid)
    return s.get("dnr") is not None or s.get("registration") is not None

def reconcile(cap: dict[str, Any], sup: dict[str, Any]) -> list[str]:
    cid = str(cap["id"])
    errors: list[str] = []
    dnr = sup.get("dnr")
    if sup.get("dnrSection") == "doNotRebuild" and isinstance(dnr, dict) and isinstance(dnr.get("value"), bool):
        if dnr["value"] != cap.get("doNotRebuild"):
            errors.append("CONTRADICTORY_DNR_MAP:" + cid)
    reg = sup.get("registration")
    if isinstance(reg, dict):
        if isinstance(reg.get("doNotRebuild"), bool) and reg["doNotRebuild"] != cap.get("doNotRebuild"):
            errors.append("CONTRADICTORY_REGISTRATION_DNR:" + cid)
        status = str(reg.get("status") or "").upper()
        if status.startswith("DONE") and cap.get("classification") != "DONE":
            errors.append("CONTRADICTORY_REGISTRATION_DONE:" + cid)
        if "EXTERNAL_BLOCKED" in status and cap.get("classification") != "EXTERNAL":
            errors.append("CONTRADICTORY_REGISTRATION_EXTERNAL:" + cid)
    return errors

def action_errors(cap: dict[str, Any], action: str) -> list[str]:
    cid = str(cap["id"])
    cls = str(cap.get("classification"))
    status = str(cap.get("status"))
    errors: list[str] = []
    allowed = {
        "DONE": {"REUSE", "VERIFY", "ADVANCE"},
        "VERIFY": {"REUSE", "VERIFY", "ADVANCE"},
        "FIX": {"REUSE", "VERIFY", "ADVANCE", "FIX"},
        "BUILD": {"VERIFY", "ADVANCE", "BUILD"},
        "EXTERNAL": {"VERIFY", "ADVANCE", "EXTERNAL"},
    }
    if cap.get("doNotRebuild") is True and action in {"BUILD", "REBUILD"}:
        errors.append("ANTI_REWORK_DNR_REBUILD:" + cid)
    if cls in allowed and action not in allowed[cls]:
        errors.append(f"ACTION_EXCEEDS_{cls}_NEXT_GATE:{cid}:{action}")
    if status in {"SOURCE_READY", "LOCAL_VERIFIED", "RUNTIME_VERIFIED", "LIVE_CERTIFIED", "VISUAL_CERTIFIED"}:
        if action in {"BUILD", "REBUILD"} and cls != "BUILD":
            errors.append(f"MATURE_STATUS_NO_REBUILD:{cid}:{status}")
    if status == "EXTERNAL_BLOCKED" and action in {"BUILD", "REBUILD", "FIX"}:
        errors.append("EXTERNAL_BLOCKED_NO_INTERNAL_FIX:" + cid)
    return errors

def request_errors(request: Any) -> list[str]:
    if not isinstance(request, dict):
        return ["REQUEST_OBJECT_REQUIRED"]
    errors: list[str] = []
    unknown = set(request) - {"schemaVersion", "mode", "expectedHead", "task", "capabilities", "authorityMesh", "visualMutation"}
    if unknown:
        errors.append("UNKNOWN_REQUEST_FIELDS:" + ",".join(sorted(unknown)))
    mode = str(request.get("mode") or "").upper()
    if mode not in MODES:
        errors.append("REQUEST_MODE_INVALID:" + mode)
    if not str(request.get("expectedHead") or "").strip():
        errors.append("EXPECTED_HEAD_REQUIRED")
    task = str(request.get("task") or "").strip()
    if not 10 <= len(task) <= 6000:
        errors.append("TASK_LENGTH_INVALID")
    rows = request.get("capabilities")
    if not isinstance(rows, list) or not rows:
        return errors + ["CAPABILITIES_REQUIRED"]
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"CAPABILITY_REQUEST_OBJECT_REQUIRED:{i}")
            continue
        if set(row) - {"id", "requestedAction"}:
            errors.append(f"CAPABILITY_REQUEST_FIELDS:{i}")
        cid = str(row.get("id") or "").strip()
        action = str(row.get("requestedAction") or "").upper().strip()
        if not cid:
            errors.append(f"CAPABILITY_ID_REQUIRED:{i}")
        elif cid in seen:
            errors.append("DUPLICATE_REQUEST_CAPABILITY_ID:" + cid)
        seen.add(cid)
        if action not in ACTIONS:
            errors.append(f"REQUESTED_ACTION_INVALID:{cid}:{action}")
    return errors

def mesh_errors(mesh: Any, head: str, visual: bool) -> list[str]:
    if not isinstance(mesh, dict):
        return ["MUTATION_MESH_REQUIRED"]
    errors: list[str] = []
    if mesh.get("status") != "PASS_COMPOSED_AUTHORITY_MESH":
        errors.append("MUTATION_MESH_NOT_PASS")
    if mesh.get("repoHead") != head:
        errors.append(f"MUTATION_MESH_STALE_HEAD:{mesh.get('repoHead')}:{head}")
    if mesh.get("requiredAuthorityCoveragePct") != 100:
        errors.append("MUTATION_MESH_COVERAGE_NOT_100")
    if mesh.get("blockers") != 0:
        errors.append("MUTATION_MESH_BLOCKERS")
    if not str(mesh.get("requestDigest") or ""):
        errors.append("MUTATION_MESH_REQUEST_DIGEST_REQUIRED")
    if not str(mesh.get("artifactDigest") or ""):
        errors.append("MUTATION_MESH_ARTIFACT_DIGEST_REQUIRED")
    if visual and mesh.get("layerMapPresent") is not True:
        errors.append("VISUAL_LAYER_MAP_REQUIRED")
    return errors

def decide(repo: Path, authority: dict[str, Any], request: Any, *, current_head: str | None = None,
           dirty: list[str] | None = None) -> dict[str, Any]:
    head = current_head if current_head is not None else git(repo, "rev-parse", "HEAD")
    dirt = dirty if dirty is not None else authority_dirty(repo)
    records, canonical_errors = canonical_records(authority.get("ledger"))
    errors = [*canonical_errors, *request_errors(request)]
    if dirt:
        errors.append("AUTHORITY_FILES_DIRTY")
    if isinstance(request, dict) and request.get("expectedHead") != head:
        errors.append(f"EXPECTED_HEAD_MISMATCH:{request.get('expectedHead')}:{head}")
    selected: list[dict[str, Any]] = []
    rows = request.get("capabilities") if isinstance(request, dict) and isinstance(request.get("capabilities"), list) else []
    for row in rows:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("id") or "").strip()
        action = str(row.get("requestedAction") or "").upper().strip()
        cap = records.get(cid)
        if not cap:
            errors.append(("SHADOW_ONLY_CAPABILITY_NOT_CANONICAL:" if supplemental_has(authority, cid) else "UNKNOWN_CANONICAL_CAPABILITY:") + cid)
            continue
        sup = supplemental(authority, cid)
        errors.extend(reconcile(cap, sup))
        if action in ACTIONS:
            errors.extend(action_errors(cap, action))
        selected.append({
            "id": cid, "requestedAction": action, "classification": cap.get("classification"),
            "status": cap.get("status"), "doNotRebuild": cap.get("doNotRebuild"),
            "nextGate": cap.get("nextGate"), "evidence": cap.get("evidence"),
            "doesNotProve": cap.get("doesNotProve"), "supplemental": sup,
        })
    mode = str(request.get("mode") or "").upper() if isinstance(request, dict) else ""
    if mode == "MUTATION":
        errors.extend(mesh_errors(request.get("authorityMesh"), head, bool(request.get("visualMutation"))))
    result = {
        "schemaVersion": RESULT_SCHEMA,
        "gateSchemaVersion": SCHEMA,
        "result": "PASS_ANTI_REWORK_GATE" if not errors else "BLOCKED_ANTI_REWORK",
        "mode": mode,
        "repoHead": head,
        "authorityDigests": authority.get("digests", {}),
        "authorityDirty": dirt,
        "task": request.get("task") if isinstance(request, dict) else None,
        "selected": selected,
        "errors": sorted(set(errors)),
        "rules": {
            "canonicalCapabilityTruth": AUTH["ledger"].as_posix(),
            "supplementalIndexesMayCreateAuthority": False,
            "freshExactAuthorityMeshRequiredForMutation": True,
            "layerMapRequiredForVisualMutation": True,
            "noGreenWithoutEvidence": True,
        },
    }
    result["decisionDigest"] = digest(result)
    return result

def validate_live(authority: dict[str, Any]) -> dict[str, Any]:
    records, errors = canonical_records(authority.get("ledger"))
    out = {
        "schemaVersion": "prisma.factory-ledger.anti-rework-validation.v1",
        "result": "PASS_PRISMA_ANTI_REWORK_AUTHORITY" if not errors else "FAIL_PRISMA_ANTI_REWORK_AUTHORITY",
        "capabilityCount": len(records), "authorityDigests": authority.get("digests", {}), "errors": errors,
    }
    out["validationDigest"] = digest(out)
    return out

def fixture() -> dict[str, Any]:
    def cap(cid: str, cls: str, status: str, dnr: bool) -> dict[str, Any]:
        return {"id": cid, "classification": cls, "status": status, "doNotRebuild": dnr,
                "nextGate": "NEXT", "evidence": ["e"], "doesNotProve": ["production"]}
    return {
        "ledger": {"capabilities": [
            cap("cap.done", "DONE", "LOCAL_VERIFIED", True),
            cap("cap.source", "DONE", "SOURCE_READY", True),
            cap("cap.verify", "VERIFY", "LOCAL_VERIFIED", False),
            cap("cap.fix", "FIX", "VERIFY_REQUIRED", False),
            cap("cap.build", "BUILD", "NOT_STARTED", False),
            cap("cap.external", "EXTERNAL", "EXTERNAL_BLOCKED", True),
        ]},
        "dnr": {"doNotRebuild": {"cap.done": {"value": True}}, "verifyOrFix": {}},
        "registration": {"registrations": {"cap.done": {"status": "DONE_LOCAL_VERIFIED", "doNotRebuild": True}}},
        "evidence": {"artifacts": []}, "digests": {"ledger": "L", "dnr": "D", "registration": "R", "evidence": "E"},
    }

def req(cid: str, action: str, *, mode: str = "PROPOSAL", visual: bool = False,
        mesh: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {"schemaVersion": SCHEMA, "mode": mode, "expectedHead": "a" * 40,
           "task": "Synthetic anti-rework self-test request.",
           "capabilities": [{"id": cid, "requestedAction": action}], "visualMutation": visual}
    if mesh is not None:
        out["authorityMesh"] = mesh
    return out

def good_mesh(**overrides: Any) -> dict[str, Any]:
    out = {"status": "PASS_COMPOSED_AUTHORITY_MESH", "repoHead": "a" * 40,
           "requiredAuthorityCoveragePct": 100, "blockers": 0, "requestDigest": "r",
           "artifactDigest": "d", "layerMapPresent": True}
    out.update(overrides)
    return out

def selftest() -> None:
    a = fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        assert decide(repo, a, req("cap.done", "ADVANCE"), current_head="a" * 40, dirty=[])["result"] == "PASS_ANTI_REWORK_GATE"
        for cid, action in [("missing.cap", "BUILD"), ("cap.done", "REBUILD"),
                            ("cap.source", "BUILD"), ("cap.verify", "REBUILD"),
                            ("cap.external", "FIX")]:
            assert decide(repo, a, req(cid, action), current_head="a" * 40, dirty=[])["result"] == "BLOCKED_ANTI_REWORK"
        shadow = copy.deepcopy(a); shadow["dnr"]["doNotRebuild"]["shadow.cap"] = {"value": True}
        assert decide(repo, shadow, req("shadow.cap", "VERIFY"), current_head="a" * 40, dirty=[])["result"] == "BLOCKED_ANTI_REWORK"
        contradiction = copy.deepcopy(a); contradiction["dnr"]["doNotRebuild"]["cap.done"]["value"] = False
        assert decide(repo, contradiction, req("cap.done", "ADVANCE"), current_head="a" * 40, dirty=[])["result"] == "BLOCKED_ANTI_REWORK"
        cases = [
            req("cap.fix", "FIX", mode="MUTATION"),
            req("cap.fix", "FIX", mode="MUTATION", mesh=good_mesh(repoHead="b" * 40)),
            req("cap.fix", "FIX", mode="MUTATION", mesh=good_mesh(requiredAuthorityCoveragePct=99.9)),
            req("cap.fix", "FIX", mode="MUTATION", mesh=good_mesh(blockers=1)),
            req("cap.fix", "FIX", mode="MUTATION", visual=True, mesh=good_mesh(layerMapPresent=False)),
        ]
        for case in cases:
            assert decide(repo, a, case, current_head="a" * 40, dirty=[])["result"] == "BLOCKED_ANTI_REWORK"
        dup = copy.deepcopy(a); dup["ledger"]["capabilities"].append(copy.deepcopy(dup["ledger"]["capabilities"][0]))
        assert decide(repo, dup, req("cap.done", "ADVANCE"), current_head="a" * 40, dirty=[])["result"] == "BLOCKED_ANTI_REWORK"
        assert decide(repo, a, req("cap.fix", "FIX", mode="MUTATION", mesh=good_mesh()), current_head="a" * 40, dirty=[])["result"] == "PASS_ANTI_REWORK_GATE"
    print("PASS_PRISMA_UNIVERSAL_ANTI_REWORK_GATE_SELF_TEST")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--fingerprint", action="store_true")
    ap.add_argument("--request")
    ns = ap.parse_args()
    if ns.self_test:
        selftest(); return 0
    repo = root(); authority = read_authority(repo)
    if ns.fingerprint:
        out = {"schemaVersion": SCHEMA, "repoHead": git(repo, "rev-parse", "HEAD"),
               "authorityDigests": authority["digests"], "authorityDirty": authority_dirty(repo)}
        out["fingerprintDigest"] = digest(out)
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if not out["authorityDirty"] else 2
    if ns.request:
        p = Path(ns.request); p = p if p.is_absolute() else repo / p
        out = decide(repo, authority, load(p))
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if out["result"] == "PASS_ANTI_REWORK_GATE" else 2
    out = validate_live(authority)
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if out["result"] == "PASS_PRISMA_ANTI_REWORK_AUTHORITY" else 1

if __name__ == "__main__":
    raise SystemExit(main())
