"""Path model for the one-button runtime.

Wave 4 extends the path graph with lock, ledger, export, coordination, report,
packet, and prompt locations used by the robust operational flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    framework_root: Path
    ops_root: Path
    projects_root: Path
    project_root: Path
    project_manifest_path: Path
    runs_root: Path
    run_root: Path
    run_manifest_path: Path
    rounds_root: Path
    round_root: Path
    round_manifest_path: Path
    bundles_root: Path
    sessions_root: Path
    state_root: Path
    locks_root: Path
    sessions_state_root: Path
    lock_file_path: Path
    session_ledger_path: Path
    coordination_root: Path
    coordination_snapshots_root: Path
    coordination_snapshot_json_path: Path
    coordination_snapshot_md_path: Path
    reports_root: Path
    readiness_report_path: Path
    acceptance_report_path: Path
    packets_root: Path
    prompts_root: Path


@dataclass(frozen=True)
class ExportHints:
    canonical_zip_path: Path
    canonical_manifest_sidecar_path: Path
    canonical_sha256_sidecar_path: Path
    handoff_copy_filename: str


@dataclass(frozen=True)
class ResolvedPaths:
    project: ProjectPaths
    export_hints: ExportHints



def build_paths(framework_root: Path, project_id: str, run_id: str, round_id: str, session_id: str) -> ResolvedPaths:
    ops_root = framework_root / 'ops'
    projects_root = ops_root / 'projects'
    project_root = projects_root / project_id
    project_manifest_path = project_root / 'project_manifest.json'

    runs_root = project_root / 'runs'
    run_root = runs_root / run_id
    run_manifest_path = run_root / 'run_manifest.json'

    rounds_root = run_root / 'rounds'
    round_root = rounds_root / round_id
    round_manifest_path = round_root / 'round_manifest.json'

    bundles_root = project_root / 'bundles'
    sessions_root = bundles_root / 'sessions'

    state_root = project_root / 'state'
    locks_root = state_root / 'locks'
    sessions_state_root = state_root / 'sessions'
    lock_file_path = locks_root / 'one_button.lock.json'
    session_ledger_path = sessions_state_root / 'session_ledger.jsonl'

    coordination_root = round_root / 'coordination'
    coordination_snapshots_root = coordination_root / 'snapshots'
    coordination_snapshot_json_path = coordination_snapshots_root / 'coordination_snapshot.latest.json'
    coordination_snapshot_md_path = coordination_snapshots_root / 'coordination_snapshot.latest.md'

    reports_root = round_root / 'reports'
    readiness_report_path = reports_root / 'readiness_report.json'
    acceptance_report_path = reports_root / 'acceptance_report.json'

    packets_root = round_root / 'packets'
    prompts_root = round_root / 'prompts'

    canonical_zip_path = sessions_root / f'{session_id}.zip'
    export_hints = ExportHints(
        canonical_zip_path=canonical_zip_path,
        canonical_manifest_sidecar_path=sessions_root / f'{session_id}.manifest.json',
        canonical_sha256_sidecar_path=sessions_root / f'{session_id}.sha256',
        handoff_copy_filename=f'{session_id}.zip',
    )

    return ResolvedPaths(
        project=ProjectPaths(
            framework_root=framework_root,
            ops_root=ops_root,
            projects_root=projects_root,
            project_root=project_root,
            project_manifest_path=project_manifest_path,
            runs_root=runs_root,
            run_root=run_root,
            run_manifest_path=run_manifest_path,
            rounds_root=rounds_root,
            round_root=round_root,
            round_manifest_path=round_manifest_path,
            bundles_root=bundles_root,
            sessions_root=sessions_root,
            state_root=state_root,
            locks_root=locks_root,
            sessions_state_root=sessions_state_root,
            lock_file_path=lock_file_path,
            session_ledger_path=session_ledger_path,
            coordination_root=coordination_root,
            coordination_snapshots_root=coordination_snapshots_root,
            coordination_snapshot_json_path=coordination_snapshot_json_path,
            coordination_snapshot_md_path=coordination_snapshot_md_path,
            reports_root=reports_root,
            readiness_report_path=readiness_report_path,
            acceptance_report_path=acceptance_report_path,
            packets_root=packets_root,
            prompts_root=prompts_root,
        ),
        export_hints=export_hints,
    )
