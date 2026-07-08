"""Verifier for DB Evidence Atlas presentation normalization."""
from __future__ import annotations
import json, sys
from pathlib import Path
STATUS = "PRODUCTION_CERTIFIED_LICSCOPE_LANE"
GATE = "PASS_LICSCOPE_CLOUD_APPS_SYNC_GREEN_ALLOWED"
OLD_STATUS = "SOURCE_READY_NOT_PRODUCTION_CERTIFIED"
OLD_GATE = "NO_PASS_PRODUCTION_MULTI_DEVICE_SALES_LINEAGE_CERTIFIED"

def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path.cwd(); atlas = root / "db_evidence_atlas"; errors=[]
    for rel in ["ATLAS_MANIFEST_PLUS.json", "json/manifest.json", "operational_evidence_atlas.json"]:
        p=atlas/rel
        if not p.exists(): errors.append(f"missing {rel}"); continue
        data=json.loads(p.read_text(encoding="utf-8")); target=data.get("manifest") if rel == "operational_evidence_atlas.json" else data
        if target.get("status") != STATUS: errors.append(f"{rel}: status={target.get('status')!r}")
        if target.get("productionGate") != GATE: errors.append(f"{rel}: productionGate={target.get('productionGate')!r}")
        if target.get("productionGreenAllowed") is not True: errors.append(f"{rel}: productionGreenAllowed not true")
    for rel in ["ATLAS_MANIFEST_PLUS.json", "HUMAN_OPERATOR_SUMMARY.md", "operational_evidence_atlas.html", "operational_evidence_atlas.json", "csv/goldenPathComparator.csv", "CAN_PATCH_DECISION.md"]:
        p=atlas/rel
        if p.exists():
            txt=p.read_text(encoding="utf-8", errors="replace")
            if OLD_STATUS in txt or OLD_GATE in txt or "CAN_DECLARE_PRODUCTION_CERTIFIED=false" in txt: errors.append(f"old signal remains in {rel}")
    if errors:
        print(json.dumps({"ok":False,"errors":errors}, indent=2)); return 1
    print(json.dumps({"ok":True,"status":"PASS_DBEVID_LICSCOPE_PRESENTATION_NORMALIZED","productionGreenAllowed":True}, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main(sys.argv))
