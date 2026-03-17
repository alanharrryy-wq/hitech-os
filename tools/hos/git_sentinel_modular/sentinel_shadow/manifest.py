from pathlib import Path
import json
import time

def read_manifest(path: str | Path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))

def write_manifest(path: str | Path, payload: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

def build_run_manifest(workspace, source_root, runtime_root):
    payload = {
        "run_id": workspace.run_id,
        "created_at_epoch": time.time(),
        "source_root": str(source_root),
        "runtime_root": str(runtime_root),
        "workspace_root": str(workspace.root),
        "baseline_dir": str(workspace.baseline_dir),
        "candidate_dir": str(workspace.candidate_dir),
        "manifests_dir": str(workspace.manifests_dir),
        "mode": "shadow",
        "promotion": "disabled_by_default",
    }

    path = workspace.manifests_dir / "run_manifest.json"
    write_manifest(path, payload)
    return path, payload
