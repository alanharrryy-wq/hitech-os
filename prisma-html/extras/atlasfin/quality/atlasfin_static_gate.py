from __future__ import annotations
import argparse, json, re
from pathlib import Path

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("atlas_root")
    parser.add_argument("--report", required=True)
    args=parser.parse_args()
    root=Path(args.atlas_root)
    css=(root/"assets/css/atlas.css").read_text(encoding="utf-8")
    html=(root/"i-paneles-cards.html").read_text(encoding="utf-8")
    fixture=(root/"quality/atlasfin_state_fixture.html").read_text(encoding="utf-8")
    block=css.split("/* UIMAPFINAL_ATLASFIN_STATE_EVIDENCE_V1",1)[-1]
    checks={
      "canonicalMarkerPresent":"UIMAPFINAL_ATLASFIN_STATE_EVIDENCE_V1" in css,
      "noImportantInGovernedBlock":"!important" not in block,
      "statusWrapAnywhere":"overflow-wrap: anywhere" in block,
      "statusWhiteSpaceNormal":"white-space: normal" in block,
      "canonicalPageDisabledLabeled":'data-atlas-evidence-state="disabled"' in html,
      "canonicalPageEnabledFixtureLabeled":'data-atlas-evidence-state="enabled-fixture"' in html,
      "canonicalPageLoadingLabeled":'data-atlas-evidence-state="loading"' in html,
      "fixtureSafeV1":'data-atlasfin-evidence-fixture="safe-v1"' in fixture,
      "fixtureStatesComplete":all(f'data-atlas-evidence-state="{s}"' in fixture for s in ("disabled","enabled","focus","loading","skipped")),
      "fixtureNoSalePaymentDb":all(word not in fixture.lower() for word in ("api/checkout","prisma.","fetch(","indexeddb","localstorage")),
    }
    report={"schema":"prisma.atlasfin.static-visual-gate.v1","schemaVersion":"1.0.0","status":"PASS" if all(checks.values()) else "FAIL","checks":checks}
    target=Path(args.report); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2))
    return 0 if report["status"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
