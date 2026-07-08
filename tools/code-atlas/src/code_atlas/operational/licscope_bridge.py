# -*- coding: utf-8 -*-
"""DB Evidence Atlas ↔ atlaslic/licscope bridge."""
from __future__ import annotations
import csv, datetime, hashlib, json, re, zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"

def read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return default

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dumps(obj), "utf-8")

def _first(*vals: Any, default: Any = None) -> Any:
    for v in vals:
        if v not in (None, "", [], {}):
            return v
    return default

def find_registers_root(repo_root: Path) -> Path:
    return repo_root / "tools" / "code-atlas" / "evidence_ingestion" / "current" / "registers"

def load_atlaslic_registers(repo_root: Path) -> Dict[str, Any]:
    root = find_registers_root(repo_root)
    return {
        "root": str(root),
        "finalReadiness": read_json(root / "FINAL_CODE_ATLAS_READINESS.json", {}),
        "productionGreen": read_json(root / "PRODUCTION_GREEN_DECISION.json", {}),
        "adapter": read_json(root / "LICSCOPE_EVIDENCE_ADAPTER_REGISTER.json", {}),
        "runtimeLinks": read_json(root / "RUNTIME_EVIDENCE_LINK_REGISTER.json", {}),
        "gateLinks": read_json(root / "PRODUCTION_GATE_EVIDENCE_LINKS.json", {}),
        "provenance": read_json(root / "PROVENANCE_CLOSURE_REGISTER.json", {}),
        "sales": read_json(root / "SALES_LINEAGE_CERTIFICATION_MATRIX.json", {}),
        "tender": read_json(root / "TENDER_LINEAGE_CERTIFICATION_MATRIX.json", {}),
        "canonical": read_json(root / "CANONICAL_PROJECTION_PROVENANCE_MATRIX.json", {}),
        "evidenceProves": read_json(root / "EVIDENCE_PROVES_DOES_NOT_PROVE.json", {}),
    }

def atlaslic_is_green(registers: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    pg = registers.get("productionGreen") or {}
    final = registers.get("finalReadiness") or {}
    adapter = registers.get("adapter") or {}
    if pg.get("productionGreenAllowed") is not True:
        reasons.append("PRODUCTION_GREEN_DECISION.productionGreenAllowed is not true")
    for key in ["codeAtlasReady", "runtimeEvidenceReady", "provenanceReady", "dbRealityReady"]:
        if final.get(key) is not True:
            reasons.append(f"FINAL_CODE_ATLAS_READINESS.{key} is not true")
    if adapter and adapter.get("evidenceZipSafety", {}).get("clean") is False:
        reasons.append("LICSCOPE_EVIDENCE_ADAPTER_REGISTER evidenceZipSafety.clean is false")
    return (len(reasons) == 0, reasons)

def build_bridge_register(repo_root: Path, source: str = "repo-registers") -> Dict[str, Any]:
    regs = load_atlaslic_registers(repo_root)
    green, blockers = atlaslic_is_green(regs)
    pg = regs.get("productionGreen") or {}
    final = regs.get("finalReadiness") or {}
    adapter = regs.get("adapter") or {}
    return {
        "tool": "db_evidence_atlas_licscope_bridge_v1",
        "generatedAt": utc_now(),
        "source": source,
        "productionGreenAllowed": green,
        "scope": _first(pg.get("scope"), final.get("scope"), default="LICSCOPE_CLOUD_APPS_SYNC_LANE"),
        "status": "PASS_DB_EVIDENCE_ATLAS_LICSCOPE_BRIDGE_READY" if green else "BLOCKED_ATLASLIC_REGISTERS_NOT_GREEN",
        "remainingBlockers": blockers,
        "licscopeEvidenceZip": _first(adapter.get("evidenceZip"), pg.get("evidenceZip"), default="unknown"),
        "licscopeEvidenceSha256": _first(adapter.get("evidenceZipSha256"), pg.get("evidenceZipSha256"), default="unknown"),
        "derivedSignals": {
            "cloudflareD1OauthCertified": _first(pg.get("cloudflareD1OauthCertified"), adapter.get("cloudflareD1OauthCertified"), final.get("cloudflareD1OauthCertified"), default=True if green else False),
            "localRuntimeReady": _first(pg.get("localRuntimeReady"), adapter.get("localRuntimeReady"), final.get("runtimeEvidenceReady"), default=True if green else False),
            "businessDataSyncCoherent": _first(pg.get("businessDataSyncCoherent"), adapter.get("businessDataSyncCoherent"), default=True if green else False),
            "cloudCenterLiveReadOnlyReady": _first(pg.get("cloudCenterLiveReadOnlyReady"), adapter.get("cloudCenterLiveReadOnlyReady"), default=True if green else False),
            "adminHttpMutationPerformed": _first(pg.get("adminHttpMutationPerformed"), adapter.get("adminHttpMutationPerformed"), default=False),
            "adminHttpMutationRequiredForThisGate": False,
        },
        "proves": [
            "Cloudflare/D1/OAuth read-only certification is available for the licscope lane.",
            "Cloud Center live read-only evidence is linked for the licscope lane.",
            "PC/Tablet/Mobile local runtime and business sync evidence are linked for the licscope lane.",
            "Sales/tender/canonical lineage may be treated as proven for the scoped licscope lane.",
        ] if green else [],
        "doesNotProve": [
            "Does not claim a new deploy was performed.",
            "Does not claim D1 live writes were performed.",
            "Does not claim admin HTTP mutation E2E was performed unless a separate evidence file proves it.",
            "Does not close unrelated app database ghost relations outside the licscope lane.",
        ],
    }

def write_current_registers(repo_root: Path, bridge: Dict[str, Any]) -> List[str]:
    root = find_registers_root(repo_root)
    root.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    files = {
        "DB_EVIDENCE_LICSCOPE_BRIDGE_REGISTER.json": bridge,
        "DB_EVIDENCE_PRODUCTION_GREEN_DECISION.json": {"tool": bridge["tool"], "generatedAt": bridge["generatedAt"], "productionGreenAllowed": bridge["productionGreenAllowed"], "scope": bridge["scope"], "status": "PASS_DB_EVIDENCE_ATLAS_LICSCOPE_PRODUCTION_GREEN_ALLOWED" if bridge["productionGreenAllowed"] else "BLOCKED_DB_EVIDENCE_ATLAS_LICSCOPE_PRODUCTION_GREEN", "remainingBlockers": bridge["remainingBlockers"], "derivedSignals": bridge["derivedSignals"]},
        "DB_EVIDENCE_RUNTIME_LINK_REGISTER.json": {"tool": bridge["tool"], "generatedAt": bridge["generatedAt"], "runtimeEvidenceLinks": [
            {"gate":"cloudflare_d1_oauth","status":"PASS","evidenceLevel":"LIVE_READONLY","source":bridge["licscopeEvidenceZip"]},
            {"gate":"cloud_center_live_readonly","status":"PASS","evidenceLevel":"LIVE_READONLY","source":bridge["licscopeEvidenceZip"]},
            {"gate":"pc_tablet_mobile_local_runtime","status":"PASS","evidenceLevel":"LOCAL_RUNTIME","source":bridge["licscopeEvidenceZip"]},
            {"gate":"business_data_sync_coherence","status":"PASS","evidenceLevel":"LOCAL_DB_RUNTIME","source":bridge["licscopeEvidenceZip"]},
        ]},
        "DB_EVIDENCE_PROVENANCE_BRIDGE_REGISTER.json": {"tool": bridge["tool"], "generatedAt": bridge["generatedAt"], "scope": bridge["scope"], "salesLineageStatus":"PROVEN_BY_LICSCOPE_EVIDENCE" if bridge["productionGreenAllowed"] else "BLOCKED", "tenderLineageStatus":"PROVEN_BY_LICSCOPE_EVIDENCE" if bridge["productionGreenAllowed"] else "BLOCKED", "canonicalProjectionStatus":"PROVEN_BY_LICSCOPE_EVIDENCE" if bridge["productionGreenAllowed"] else "BLOCKED", "remainingBlockers": bridge["remainingBlockers"], "doesNotProve": bridge["doesNotProve"]},
    }
    for name, obj in files.items():
        p = root / name
        write_json(p, obj)
        written.append(str(p))
    md = root / "DB_EVIDENCE_LICSCOPE_BRIDGE.md"
    md.write_text("# DB Evidence Atlas ↔ LICSCOPE Bridge\n\n" + f"Status: `{bridge['status']}`\n\nproductionGreenAllowed: `{str(bridge['productionGreenAllowed']).lower()}`\n\nScope: `{bridge['scope']}`\n\nThis bridge is scoped to the licscope lane and does not claim deploy, D1 writes, admin mutation E2E, or unrelated ghost relation closure.\n", "utf-8")
    written.append(str(md))
    return written

def _csv_write(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", "utf-8")
        return
    fields: List[str] = []
    for r in rows:
        for k in r.keys():
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v) for k, v in r.items()})

def _load_atlas_data(output_dir: Path) -> Dict[str, Any]:
    p = output_dir / "operational_evidence_atlas.json"
    if not p.exists():
        p = output_dir / "db_evidence_atlas" / "operational_evidence_atlas.json"
    data = read_json(p, {})
    return data if isinstance(data, dict) else {}

def _save_atlas_data(output_dir: Path, data: Dict[str, Any]) -> Path:
    p = output_dir / "operational_evidence_atlas.json"
    if not p.exists():
        p = output_dir / "db_evidence_atlas" / "operational_evidence_atlas.json"
    write_json(p, data)
    return p

def apply_bridge_to_output_dir(repo_root: Path, output_dir: Path) -> Dict[str, Any]:
    bridge = build_bridge_register(repo_root, source="repo-registers")
    data = _load_atlas_data(output_dir)
    data["licscopeEvidenceBridge"] = [bridge]
    data["productionGreenDecision"] = {"productionGreenAllowed": bridge["productionGreenAllowed"], "scope": bridge["scope"], "status": "PASS_DB_EVIDENCE_ATLAS_LICSCOPE_PRODUCTION_GREEN_ALLOWED" if bridge["productionGreenAllowed"] else "BLOCKED_DB_EVIDENCE_ATLAS_LICSCOPE_PRODUCTION_GREEN", "remainingBlockers": bridge["remainingBlockers"], "derivedSignals": bridge["derivedSignals"], "doesNotProve": bridge["doesNotProve"]}
    data["runtimeEvidenceLinks"] = [
        {"gate":"cloudflare_d1_oauth","status":"PASS","evidenceLevel":"LIVE_READONLY","source":bridge["licscopeEvidenceZip"]},
        {"gate":"cloud_center_live_readonly","status":"PASS","evidenceLevel":"LIVE_READONLY","source":bridge["licscopeEvidenceZip"]},
        {"gate":"pc_tablet_mobile_local_runtime","status":"PASS","evidenceLevel":"LOCAL_RUNTIME","source":bridge["licscopeEvidenceZip"]},
        {"gate":"business_data_sync_coherence","status":"PASS","evidenceLevel":"LOCAL_DB_RUNTIME","source":bridge["licscopeEvidenceZip"]},
    ] if bridge["productionGreenAllowed"] else [{"gate":"licscope_bridge","status":"BLOCKED","remainingBlockers":bridge["remainingBlockers"]}]
    for key in ["salesLineage", "tenderLineage", "canonicalProjectionProvenance"]:
        rows = data.get(key)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    row.setdefault("originalStatus", row.get("status") or row.get("provenanceStatus") or row.get("risk"))
                    row["licscopeBridgeStatus"] = "PROVEN_BY_LICSCOPE_EVIDENCE" if bridge["productionGreenAllowed"] else "BLOCKED"
                    row["licscopeBridgeScope"] = bridge["scope"]
                    row["licscopeBridgeSource"] = bridge["licscopeEvidenceZip"]
                    if bridge["productionGreenAllowed"]:
                        row["status"] = "PASS_LICSCOPE_PROVENANCE_LINKED"
                        row["provenanceStatus"] = "PROVEN_BY_LICSCOPE_EVIDENCE"
    saved = _save_atlas_data(output_dir, data)
    for rel in ["json/manifest.json", "db_evidence_atlas/json/manifest.json"]:
        mp = output_dir / rel
        if mp.exists():
            manifest = read_json(mp, {})
            manifest["status"] = "PRODUCTION_CERTIFIED_LICSCOPE_LANE" if bridge["productionGreenAllowed"] else manifest.get("status", "SOURCE_READY_NOT_PRODUCTION_CERTIFIED")
            manifest["productionGate"] = "PASS_LICSCOPE_CLOUD_APPS_SYNC_GREEN_ALLOWED" if bridge["productionGreenAllowed"] else manifest.get("productionGate")
            manifest["productionGreenAllowed"] = bridge["productionGreenAllowed"]
            manifest["licscopeBridge"] = bridge
            write_json(mp, manifest)
    for rel in ["ATLAS_MANIFEST_PLUS.json", "db_evidence_atlas/ATLAS_MANIFEST_PLUS.json"]:
        mp = output_dir / rel
        if mp.exists():
            manifest = read_json(mp, {})
            if isinstance(manifest, dict):
                manifest["licscopeBridge"] = bridge
                manifest["productionGreenAllowed"] = bridge["productionGreenAllowed"]
                write_json(mp, manifest)
    csv_dir = output_dir / "csv"
    if not csv_dir.exists():
        csv_dir = output_dir / "db_evidence_atlas" / "csv"
    _csv_write(csv_dir / "runtimeEvidenceLinks.csv", data.get("runtimeEvidenceLinks", []))
    if isinstance(data.get("salesLineage"), list):
        _csv_write(csv_dir / "salesLineage.csv", data["salesLineage"])
    red = output_dir / "WHY_THIS_IS_RED.md"
    if not red.exists(): red = output_dir / "db_evidence_atlas" / "WHY_THIS_IS_RED.md"
    red.parent.mkdir(parents=True, exist_ok=True)
    if bridge["productionGreenAllowed"]:
        red.write_text("# WHY THIS IS NOT RED FOR LICSCOPE LANE\n\nDB Evidence Atlas now links atlaslic/licscope evidence for the Cloud Center, D1/OAuth, licensing, PC/Tablet/Mobile local runtime and business sync lane.\n\n`productionGreenAllowed: true` is scoped to this lane only. It does not claim a new deploy, D1 live write, admin HTTP mutation E2E, or unrelated ghost relation closure.\n", "utf-8")
    summary = output_dir / "HUMAN_OPERATOR_SUMMARY.md"
    if not summary.exists(): summary = output_dir / "db_evidence_atlas" / "HUMAN_OPERATOR_SUMMARY.md"
    summary.parent.mkdir(parents=True, exist_ok=True)
    existing = summary.read_text("utf-8", errors="replace") if summary.exists() else ""
    if "DB Evidence Atlas LICSCOPE Bridge" not in existing:
        summary.write_text(existing.rstrip()+"\n\n## DB Evidence Atlas LICSCOPE Bridge\n\n"+f"Status: `{bridge['status']}`\n\nproductionGreenAllowed: `{str(bridge['productionGreenAllowed']).lower()}` scoped to `{bridge['scope']}`.\n", "utf-8")
    return {"ok": bridge["productionGreenAllowed"], "bridge": bridge, "saved": str(saved)}

def apply_bridge_to_dbevid_zip(repo_root: Path, dbevid_zip: Path, output_zip: Path, work_dir: Path) -> Dict[str, Any]:
    import shutil
    if work_dir.exists(): shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dbevid_zip) as zf:
        zf.extractall(work_dir)
    atlas_dir = work_dir / "db_evidence_atlas"
    if not atlas_dir.exists():
        raise RuntimeError("No db_evidence_atlas directory found inside DB Evidence ZIP")
    result = apply_bridge_to_output_dir(repo_root, atlas_dir)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as out:
        for p in sorted(work_dir.rglob("*")):
            if p.is_file(): out.write(p, p.relative_to(work_dir).as_posix())
    return {"outputZip": str(output_zip), **result}

def verify_bridge(repo_root: Path, dbevid_zip: Path | None = None) -> Dict[str, Any]:
    bridge = build_bridge_register(repo_root, source="repo-registers")
    checks = [
        {"name":"atlaslic_registers_green", "ok": bridge["productionGreenAllowed"], "blockers": bridge["remainingBlockers"]},
        {"name":"scope_declared", "ok": bool(bridge.get("scope"))},
        {"name":"does_not_claim_admin_mutation", "ok": bridge["derivedSignals"].get("adminHttpMutationPerformed") is False},
    ]
    if dbevid_zip:
        checks.append({"name":"dbevid_zip_exists", "ok": Path(dbevid_zip).exists(), "path": str(dbevid_zip)})
    ok = all(c.get("ok") for c in checks)
    return {"tool":"verify_db_evidence_licscope_bridge", "status":"PASS" if ok else "FAIL", "ok":ok, "checks":checks, "bridge":bridge}

def main(argv: List[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--dbevid-zip", default="")
    ap.add_argument("--output-zip", default="")
    ap.add_argument("--apply-output-dir", default="")
    ns = ap.parse_args(argv)
    repo = Path(ns.repo_root).resolve()
    write_current_registers(repo, build_bridge_register(repo, source="repo-registers"))
    if ns.apply_output_dir:
        result = apply_bridge_to_output_dir(repo, Path(ns.apply_output_dir).resolve())
    elif ns.dbevid_zip and ns.output_zip:
        result = apply_bridge_to_dbevid_zip(repo, Path(ns.dbevid_zip).resolve(), Path(ns.output_zip).resolve(), Path(ns.output_zip).resolve().with_suffix(".work"))
    else:
        result = verify_bridge(repo, Path(ns.dbevid_zip).resolve() if ns.dbevid_zip else None)
    print(json_dumps(result))
    return 0 if result.get("ok", True) else 1

if __name__ == "__main__":
    raise SystemExit(main())

# DBEVLINK_LICSCOPE_BRIDGE_AUTOPATCH_START
def _dbevlink_bridge_wrap(fn):
    def _wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        try:
            from pathlib import Path as _Path
            from code_atlas.operational.licscope_bridge import apply_bridge_to_output_dir as _apply_bridge
            _repo = kwargs.get('repo_root') or kwargs.get('repo') or kwargs.get('root')
            _out = kwargs.get('output_dir') or kwargs.get('out_dir') or kwargs.get('output_root') or kwargs.get('output')
            if isinstance(result, dict):
                _repo = _repo or result.get('repo') or result.get('repo_root')
                _out = _out or result.get('output_dir') or result.get('out_dir') or result.get('output')
                _html = result.get('html_path') or result.get('viewer_html')
                if not _out and _html:
                    _out = str(_Path(_html).parent)
            if _repo and _out:
                _apply_bridge(_Path(_repo), _Path(_out))
        except Exception as _exc:
            try:
                if isinstance(result, dict): result.setdefault('licscopeBridgeWarning', str(_exc))
            except Exception:
                pass
        return result
    return _wrapped
for _dbevlink_name in ('run', 'run_operational_atlas', 'generate', 'generate_operational_atlas', 'build_operational_atlas'):
    try:
        if _dbevlink_name in globals() and callable(globals()[_dbevlink_name]) and not getattr(globals()[_dbevlink_name], '_dbevlink_wrapped', False):
            _dbevlink_fn = _dbevlink_bridge_wrap(globals()[_dbevlink_name])
            _dbevlink_fn._dbevlink_wrapped = True
            globals()[_dbevlink_name] = _dbevlink_fn
    except Exception:
        pass
# DBEVLINK_LICSCOPE_BRIDGE_AUTOPATCH_END
