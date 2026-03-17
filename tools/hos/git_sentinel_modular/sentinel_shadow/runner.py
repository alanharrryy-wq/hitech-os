from pathlib import Path
import shutil

from .config import runtime_root, modular_root
from .workspace import bootstrap_from_modular_source
from .manifest import build_run_manifest, write_manifest
from .diff_manifest import build_diff, write_diff_manifest
from .promotion_gate import evaluate_promotion_gate

def prepare_shadow_run(source_root=None, run_id=None):
    source_root = Path(source_root or modular_root())
    runtime = runtime_root()

    workspace = bootstrap_from_modular_source(
        run_id=run_id,
        source_root=source_root,
    )

    run_manifest_path, run_manifest_payload = build_run_manifest(
        workspace=workspace,
        source_root=source_root,
        runtime_root=runtime,
    )

    return {
        "workspace": workspace,
        "run_manifest_path": run_manifest_path,
        "run_manifest": run_manifest_payload,
    }

def stage_candidate_overlay(workspace, overlay_source):
    overlay_source = Path(overlay_source)

    for path in overlay_source.rglob("*"):
        rel = path.relative_to(overlay_source)
        target = workspace.candidate_dir / rel

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

def finalize_shadow_run(workspace):
    diff_payload = build_diff(
        baseline_root=workspace.baseline_dir,
        candidate_root=workspace.candidate_dir,
    )

    diff_path = workspace.manifests_dir / "diff_manifest.json"
    write_diff_manifest(diff_path, diff_payload)

    gate_payload = evaluate_promotion_gate(
        candidate_root=workspace.candidate_dir,
        diff_payload=diff_payload,
    )

    gate_path = workspace.manifests_dir / "promotion_gate.json"
    write_manifest(gate_path, gate_payload)

    return {
        "diff_path": diff_path,
        "gate_path": gate_path,
        "diff": diff_payload,
        "gate": gate_payload,
    }
