from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FILES = [
    "docs/live-scene-composer/governance/AUTHORING_WORKBENCH_V1_WAVE1.md",
    "tools/live-scene-composer/validate_authoring_workbench_v1_wave1.py",
    "apps/keystone/components/live-scene-composer/authoring-workbench-v1/AuthoringWorkbench.tsx",
    "apps/keystone/components/runtime-mutation-bridge/authoring-workbench-v1/contract.ts",
]

FORBIDDEN_IMPORT_FRAGMENTS = [
    "runtime-debug-console",
    "pitch-scene-runtime-bridge",
    "scene-studio",
]

def scan_repo(repo_root: Path) -> dict:
    result = {
        "repo_root": str(repo_root),
        "missing": [],
        "forbidden_import_hits": [],
    }
    for relative_path in REQUIRED_FILES:
        candidate = repo_root / relative_path
        if not candidate.exists():
            result["missing"].append(relative_path)
    source_root = repo_root / "apps/keystone/components/live-scene-composer/authoring-workbench-v1"
    if source_root.exists():
        for path in source_root.rglob("*.ts*"):
            text = path.read_text(encoding="utf-8")
            for fragment in FORBIDDEN_IMPORT_FRAGMENTS:
                if fragment in text:
                    result["forbidden_import_hits"].append({"path": str(path.relative_to(repo_root)), "fragment": fragment})
    result["ok"] = not result["missing"] and not result["forbidden_import_hits"]
    return result

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Authoring Workbench v1 wave 1 installation seams.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--json-out")
    args = parser.parse_args()
    payload = scan_repo(Path(args.repo_root).resolve())
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
