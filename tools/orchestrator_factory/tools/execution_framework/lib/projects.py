from __future__ import annotations

from pathlib import Path

from .common import build_default_run_id, ensure_dir, write_json, write_text
from .config import load_system_config


def build_project_manifest(project_id: str, project_name: str, initiative_type: str, objective: str, repo_root: Path) -> dict:
    system = load_system_config(repo_root)
    project_root = f"{system['projects_root']}/{project_id}"
    return {
        'schema_version': '1.0',
        'project_id': project_id,
        'project_name': project_name,
        'initiative_type': initiative_type,
        'package_topology': system['active_package_ids'],
        'default_run_objective': objective,
        'project_root': project_root,
        'canonical_source_register': f"{project_root}/canonical_source_register.md",
        'contract_register': f"{project_root}/contract_register.md",
        'runtime_path_policy': 'configs/execution_framework/path_policies.json',
        'status': 'homologating',
    }


def initialize_project_baseline(project_id: str, project_name: str, initiative_type: str, objective: str, repo_root: Path, force: bool = False) -> dict:
    system = load_system_config(repo_root)
    project_root = repo_root / system['projects_root'] / project_id
    if project_root.exists() and any(project_root.iterdir()) and not force:
        raise FileExistsError(f"Project baseline already exists: {project_root}")

    ensure_dir(project_root)
    suggested_run_id = build_default_run_id(project_id, sequence=1)
    manifest = build_project_manifest(project_id, project_name, initiative_type, objective, repo_root)
    write_json(project_root / 'project_manifest.json', manifest)
    write_text(
        project_root / 'README.md',
        f"# {project_id}\n\nThis folder stores the homologated project baseline for {project_name}.\n",
    )
    write_text(
        project_root / 'idea_intake.md',
        "# Idea Intake\n\n"
        "- raw request:\n"
        "- problem statement:\n"
        "- desired outcome:\n"
        "- current repo or system reality:\n"
        "- constraints:\n"
        "- risks:\n"
        "- obvious non-goals:\n"
        "- unknowns blocking homologation:\n",
    )
    write_text(
        project_root / 'homologation_record.md',
        f"# Homologation Record\n\n"
        f"- `project_id`: {project_id}\n"
        f"- project name: {project_name}\n"
        f"- initiative type: {initiative_type}\n"
        f"- project root: `ops/projects/{project_id}/`\n"
        f"- baseline summary:\n"
        f"- success conditions:\n"
        f"- default topology confirmed or overridden:\n"
        f"- runtime path ownership draft:\n"
        f"- approved path policy path: `configs/execution_framework/path_policies.json`\n"
        f"- canonical source register path: `ops/projects/{project_id}/canonical_source_register.md`\n"
        f"- contract register path: `ops/projects/{project_id}/contract_register.md`\n"
        f"- first `run_id`: {suggested_run_id}\n"
        f"- first run objective: {objective}\n"
        f"- open risks:\n"
        f"- approval status:\n",
    )
    write_text(
        project_root / 'canonical_source_register.md',
        f"# Canonical Source Register\n\n"
        f"| Artifact type | Canonical source path | Owner | Notes |\n"
        f"|---|---|---|---|\n"
        f"| project manifest | `ops/projects/{project_id}/project_manifest.json` | governance | |\n"
        f"| homologation record | `ops/projects/{project_id}/homologation_record.md` | governance | |\n"
        f"| contract register | `ops/projects/{project_id}/contract_register.md` | governance | |\n"
        f"| path ownership | `configs/execution_framework/path_policies.json` plus governance docs | governance | |\n",
    )
    write_text(
        project_root / 'contract_register.md',
        "# Contract Register\n\n"
        "| contract_id | owner_package | source_path | version | freeze_state | status | consumers | supersedes | notes |\n"
        "|---|---|---|---|---|---|---|---|---|\n",
    )
    return {
        'project_id': project_id,
        'project_root': str(project_root),
        'project_manifest': manifest,
        'suggested_first_run_id': suggested_run_id,
    }
