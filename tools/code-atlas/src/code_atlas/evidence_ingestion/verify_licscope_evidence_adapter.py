
# -*- coding: utf-8 -*-
"""Verify Code Atlas LICSCOPE ingestion registers."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED_JSON = [
    "LICSCOPE_EVIDENCE_ADAPTER_REGISTER.json",
    "RUNTIME_EVIDENCE_LINK_REGISTER.json",
    "PRODUCTION_GATE_EVIDENCE_LINKS.json",
    "PROVENANCE_CLOSURE_REGISTER.json",
    "SALES_LINEAGE_CERTIFICATION_MATRIX.json",
    "TENDER_LINEAGE_CERTIFICATION_MATRIX.json",
    "CANONICAL_PROJECTION_PROVENANCE_MATRIX.json",
    "DB_GHOST_RELATION_DECISION_REGISTER.json",
    "FINAL_CODE_ATLAS_READINESS.json",
    "PRODUCTION_GREEN_DECISION.json",
    "EVIDENCE_PROVES_DOES_NOT_PROVE.json",
    "CODE_ATLAS_INGESTION_HINTS.json",
]
REQUIRED_MD = ["NEXT_GATES_QUEUE.md", "WHY_PRODUCTION_IS_GREEN_OR_RED.md"]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--registers-dir")
    args = ap.parse_args(argv)
    repo = Path(args.repo_root).resolve()
    registers = Path(args.registers_dir).resolve() if args.registers_dir else repo / "tools" / "code-atlas" / "evidence_ingestion" / "current" / "registers"
    errors = []
    for name in REQUIRED_JSON:
        p = registers / name
        if not p.exists():
            errors.append(f"missing {name}")
            continue
        try:
            read_json(p)
        except Exception as exc:
            errors.append(f"invalid json {name}: {exc}")
    for name in REQUIRED_MD:
        p = registers / name
        if not p.exists():
            errors.append(f"missing {name}")
        elif not p.read_text(encoding="utf-8", errors="replace").strip():
            errors.append(f"empty markdown {name}")
    if not errors:
        final = read_json(registers / "FINAL_CODE_ATLAS_READINESS.json")
        decision = read_json(registers / "PRODUCTION_GREEN_DECISION.json")
        adapter = read_json(registers / "LICSCOPE_EVIDENCE_ADAPTER_REGISTER.json")
        if final.get("productionGreenAllowed") is not True:
            errors.append("FINAL_CODE_ATLAS_READINESS.productionGreenAllowed is not true")
        if decision.get("productionGreenAllowed") is not True:
            errors.append("PRODUCTION_GREEN_DECISION.productionGreenAllowed is not true")
        if adapter.get("summary", {}).get("cloudflareD1OauthCertified") is not True:
            errors.append("cloudflareD1OauthCertified not true")
        if adapter.get("summary", {}).get("localRuntimeReady") is not True:
            errors.append("localRuntimeReady not true")
        if adapter.get("summary", {}).get("secretsPrinted") is True:
            errors.append("secretsPrinted must be false")
        if adapter.get("summary", {}).get("d1LiveWritePerformed") is True:
            errors.append("d1LiveWritePerformed must be false for this read-only certification")
    result = {"status": "PASS_CODE_ATLAS_LICSCOPE_INGESTION_VERIFIED" if not errors else "FAIL_CODE_ATLAS_LICSCOPE_INGESTION_VERIFICATION", "errors": errors, "registersDir": str(registers)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 2

if __name__ == "__main__":
    raise SystemExit(main())
