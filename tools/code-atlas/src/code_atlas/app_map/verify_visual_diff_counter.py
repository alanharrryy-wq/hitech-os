# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, json, sys, tempfile
from pathlib import Path

THIS = Path(__file__).resolve()
SRC = THIS.parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from code_atlas.app_map.safety_contracts import build_visual_diff_probe, append_safety_contracts

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    collapse = []
    for i in range(300):
        collapse.append({"risk":"medium","node":f"n{i}","file":"x.tsx","classification":"NEEDS_RUNTIME_PROBE"})
    for i in range(7):
        collapse.append({"risk":"low","node":f"l{i}","file":"x.tsx","classification":"REPLACE_WITH_FRAGMENT"})
    probe = build_visual_diff_probe(collapse)
    errors = []
    candidates = probe.get("candidates", [])
    if probe.get("candidateCount") != len(candidates):
        errors.append("candidateCount does not equal len(candidates)")
    if probe.get("candidateCount") != 250:
        errors.append(f"candidateCount expected 250, got {probe.get('candidateCount')}")
    if probe.get("candidateLimit") != 250:
        errors.append(f"candidateLimit expected 250, got {probe.get('candidateLimit')}")
    if probe.get("totalMediumRisk") != 300:
        errors.append(f"totalMediumRisk expected 300, got {probe.get('totalMediumRisk')}")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        app = root / "products" / "tablet"
        app.mkdir(parents=True, exist_ok=True)
        (app / "Visual.tsx").write_text(
            "export function Visual(){return <>" + "".join("<div className='layoutOnly'>x</div>" for _ in range(300)) + "</>}",
            encoding="utf-8"
        )
        (app / "Visual.css").write_text(".layoutOnly{display:flex;gap:4px}", encoding="utf-8")
        atlas = root / "atlas"
        summary = append_safety_contracts(
            atlas_dir=atlas,
            repo_root=root,
            targets=[("tablet", app)],
            surface_registry=[],
            route_component=[],
            component_owner=[],
            selector_rows=[],
            token_rows=[],
            file_index=[],
        )
        visual_file = json.loads((atlas / "23_VISUAL_DIFF_PROBE.json").read_text(encoding="utf-8"))
        summary_file = json.loads((atlas / "27_VISUAL_SAFETY_SUMMARY.json").read_text(encoding="utf-8"))
        if summary_file.get("visualDiffProbeCandidates") != visual_file.get("candidateCount"):
            errors.append("summary visualDiffProbeCandidates != 23_VISUAL_DIFF_PROBE candidateCount")
        if summary_file.get("visualDiffProbeCandidates") != len(visual_file.get("candidates", [])):
            errors.append("summary visualDiffProbeCandidates != len(23 candidates)")
        if summary_file.get("visualDiffProbeTotalMediumRisk", 0) < summary_file.get("visualDiffProbeCandidates", 0):
            errors.append("totalMediumRisk should be >= candidate count")
        if summary_file.get("visualDiffProbeCandidateLimit") != visual_file.get("candidateLimit"):
            errors.append("summary candidateLimit != visual probe candidateLimit")

    result = {
        "ok": not errors,
        "status": "PASS_APP_MAP_VISUAL_DIFF_COUNTER_NORMALIZED" if not errors else "FAIL_APP_MAP_VISUAL_DIFF_COUNTER_NORMALIZED",
        "errors": errors,
        "probe": {
            "candidateCount": probe.get("candidateCount"),
            "candidateLimit": probe.get("candidateLimit"),
            "totalMediumRisk": probe.get("totalMediumRisk"),
            "candidatesLen": len(candidates),
        }
    }
    if args.json_out:
        write_json(Path(args.json_out), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
