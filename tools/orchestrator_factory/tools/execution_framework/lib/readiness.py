
from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import match_any, normalize_relpath, utc_now, read_json
from .config import load_system_config, load_target_layout, load_path_policies


def _check(name: str, ok: bool, details: str) -> dict[str, Any]:
    return {'name': name, 'ok': ok, 'details': details}


def _stage(status: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {'status': status, 'checks': checks}


def _default_path_policies(policies: dict[str, Any]) -> bool:
    for package_id, policy in policies.items():
        allowed = policy.get('allowed_paths', [])
        if allowed != [f'{package_id}/**']:
            return False
    return True


def _load_tree_hygiene(repo_root: Path) -> dict[str, Any]:
    system = load_system_config(repo_root)
    cfg = system.get('tree_hygiene_config')
    if not cfg:
        return {'excluded_paths': [], 'excluded_names': []}
    return read_json(repo_root / cfg)


def _runtime_junk(repo_root: Path) -> list[str]:
    cfg = _load_tree_hygiene(repo_root)
    patterns = cfg.get('excluded_paths', [])
    names = set(cfg.get('excluded_names', []))
    junk: list[str] = []
    for path in repo_root.rglob('*'):
        rel = normalize_relpath(path.relative_to(repo_root))
        if not rel:
            continue
        if path.name in names or match_any(rel, patterns):
            junk.append(rel)
    return sorted(set(junk))


def build_readiness_report(repo_root: Path, project_id: str | None = None, run_id: str | None = None, round_id: str | None = None) -> dict[str, Any]:
    system = load_system_config(repo_root)
    layout = load_target_layout(repo_root)
    policies = load_path_policies(repo_root)
    stages: dict[str, Any] = {}

    install_checks: list[dict[str, Any]] = []
    missing_dirs = [rel for rel in layout.get('required_directories', []) if not (repo_root / rel).exists()]
    install_checks.append(_check('required_directories', not missing_dirs, 'missing: ' + ', '.join(missing_dirs) if missing_dirs else 'all required directories present'))
    required_files = [
        'README.md',
        'OPERATOR_ONE_PAGE_FLOW.md',
        'STARTER_INDEX.md',
        'MASTER_INDEX.md',
        'parallel_manifest.json',
        'parallel_launch_order.md',
        'master_chat_routing.md',
        '00-governance-core/docs/control/framework_readiness_gates.md',
        '00-governance-core/docs/control/inter_chat_communication_policy.md',
        '00-governance-core/docs/control/waiver_and_exception_policy.md',
        '00-governance-core/docs/contracts/contract_versioning_policy.md',
        'universal_execution_starter_kit_v1.zip',
    ]
    missing_files = [rel for rel in required_files if not (repo_root / rel).exists()]
    install_checks.append(_check('required_files', not missing_files, 'missing: ' + ', '.join(missing_files) if missing_files else 'all required files present'))
    junk = _runtime_junk(repo_root)
    install_checks.append(_check('canonical_tree_hygiene', not junk, 'junk: ' + ', '.join(junk[:20]) if junk else 'no excluded runtime junk found'))
    install_status = 'ready' if all(item['ok'] for item in install_checks) else 'not_ready'
    stages['install'] = _stage(install_status, install_checks)

    if run_id and not project_id:
        run_manifest_path = repo_root / system['runs_root'] / run_id / 'run_manifest.json'
        if run_manifest_path.exists():
            project_id = read_json(run_manifest_path).get('project_id')

    if project_id:
        project_root = repo_root / system['projects_root'] / project_id
        bootstrap_checks: list[dict[str, Any]] = []
        bootstrap_checks.append(_check('project_root', project_root.exists(), f'expected {project_root}'))
        for rel in ['README.md', 'project_manifest.json', 'idea_intake.md', 'homologation_record.md', 'canonical_source_register.md', 'contract_register.md']:
            bootstrap_checks.append(_check(rel, (project_root / rel).exists(), f'expected {(project_root / rel)}'))
        bootstrap_checks.append(_check('path_policies_homologated', not _default_path_policies(policies), 'replace starter placeholder package paths with real project runtime paths'))
        bootstrap_status = 'ready' if all(item['ok'] for item in bootstrap_checks) else 'not_ready'
        stages['bootstrap'] = _stage(bootstrap_status, bootstrap_checks)
    else:
        stages['bootstrap'] = _stage('not_requested', [])

    if run_id:
        run_root = repo_root / system['runs_root'] / run_id
        run_checks: list[dict[str, Any]] = []
        run_checks.append(_check('run_root', run_root.exists(), f'expected {run_root}'))
        run_manifest_path = run_root / 'run_manifest.json'
        run_checks.append(_check('run_manifest', run_manifest_path.exists(), f'expected {run_manifest_path}'))
        if run_manifest_path.exists():
            manifest = read_json(run_manifest_path)
            run_checks.append(_check('run_objective', bool(str(manifest.get('objective', '')).strip()), 'run objective must be non-empty'))
            if project_id:
                run_checks.append(_check('project_id_match', manifest.get('project_id') == project_id, 'run manifest project_id must match requested project_id'))
        run_checks.append(_check('decisions_dir', (run_root / system['decisions_dir_name']).exists(), f'expected {(run_root / system["decisions_dir_name"])}'))
        run_status = 'ready' if all(item['ok'] for item in run_checks) else 'not_ready'
        stages['run'] = _stage(run_status, run_checks)
    else:
        stages['run'] = _stage('not_requested', [])

    if run_id and round_id:
        round_root = repo_root / system['runs_root'] / run_id / system['rounds_dir_name'] / round_id
        round_checks: list[dict[str, Any]] = []
        round_checks.append(_check('round_root', round_root.exists(), f'expected {round_root}'))
        round_manifest_path = round_root / 'round_manifest.json'
        round_checks.append(_check('round_manifest', round_manifest_path.exists(), f'expected {round_manifest_path}'))
        for dirname in [system['incoming_dir_name'], system['reports_dir_name'], system['packets_dir_name'], system['prompts_dir_name']]:
            round_checks.append(_check(dirname, (round_root / dirname).exists(), f'expected {(round_root / dirname)}'))
        expected_packet_paths = [round_root / system['packets_dir_name'] / pkg / 'work_packet.json' for pkg in system['active_package_ids']]
        round_checks.append(_check('work_packets', all(path.exists() for path in expected_packet_paths), 'one work_packet.json expected per active package'))
        expected_prompt_paths = [round_root / system['prompts_dir_name'] / f'{pkg}.prompt.md' for pkg in system['active_package_ids']]
        round_checks.append(_check('prompts', all(path.exists() for path in expected_prompt_paths), 'one prompt expected per active package'))
        round_status = 'ready' if all(item['ok'] for item in round_checks) else 'not_ready'
        stages['round'] = _stage(round_status, round_checks)

        acceptance_checks: list[dict[str, Any]] = []
        acceptance_checks.append(_check('validate_worker_bundle_tool', (repo_root / 'tools/execution_framework/validate_worker_bundle.py').exists(), 'validation tool must exist'))
        acceptance_checks.append(_check('emit_acceptance_report_tool', (repo_root / 'tools/execution_framework/emit_acceptance_report.py').exists(), 'acceptance tool must exist'))
        acceptance_checks.append(_check('compute_overlap_report_tool', (repo_root / 'tools/execution_framework/compute_overlap_report.py').exists(), 'overlap tool must exist'))
        acceptance_checks.append(_check('incoming_dir', (round_root / system['incoming_dir_name']).exists(), 'incoming directory must exist'))
        acceptance_checks.append(_check('reports_dir', (round_root / system['reports_dir_name']).exists(), 'reports directory must exist'))
        acceptance_status = 'ready' if all(item['ok'] for item in acceptance_checks) else 'not_ready'
        stages['acceptance'] = _stage(acceptance_status, acceptance_checks)

        integration_checks: list[dict[str, Any]] = []
        acceptance_report_path = round_root / system['reports_dir_name'] / 'acceptance_report.json'
        integration_summary_path = round_root / system['reports_dir_name'] / 'integration_ready_summary.md'
        if acceptance_report_path.exists():
            acceptance = read_json(acceptance_report_path)
            overall = acceptance.get('overall_status', '')
            integration_checks.append(_check('acceptance_report', True, f'overall_status={overall}'))
            integration_checks.append(_check('overall_status_non_reject', overall != 'reject', 'integration cannot proceed while overall status is reject'))
            integration_checks.append(_check('integration_summary', integration_summary_path.exists(), f'expected {integration_summary_path}'))
            integration_status = 'ready' if all(item['ok'] for item in integration_checks) else 'not_ready'
        else:
            integration_checks.append(_check('acceptance_report', False, 'acceptance report not generated yet'))
            integration_status = 'pending_inputs'
        stages['integration'] = _stage(integration_status, integration_checks)
    else:
        stages['round'] = _stage('not_requested', [])
        stages['acceptance'] = _stage('not_requested', [])
        stages['integration'] = _stage('not_requested', [])

    statuses = [stage['status'] for stage in stages.values() if stage['status'] not in {'not_requested'}]
    if any(status == 'not_ready' for status in statuses):
        overall_status = 'not_ready'
    elif any(status == 'pending_inputs' for status in statuses):
        overall_status = 'pending_inputs'
    else:
        overall_status = 'ready'

    return {
        'schema_version': '1.0',
        'checked_at_utc': utc_now(),
        'project_id': project_id,
        'run_id': run_id,
        'round_id': round_id,
        'overall_status': overall_status,
        'stages': stages,
    }
