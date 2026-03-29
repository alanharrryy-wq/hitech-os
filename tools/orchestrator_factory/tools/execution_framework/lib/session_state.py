"""State resolution for the one-button runtime core.

Wave 3 keeps this deliberately pragmatic: the launcher can inspect existing
project state, resolve the next run/round identifiers, and materialize minimal
manifest files when not running in dry-run mode.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from session_paths import ResolvedPaths, build_paths

RUN_PATTERN = re.compile(r'^run_(\d+)$')
ROUND_PATTERN = re.compile(r'^round_(\d+)$')


@dataclass(frozen=True)
class ProjectRecord:
    project_id: str
    project_name: str
    initiative_type: str
    project_root: Path
    latest_run_id: Optional[str]
    latest_round_id: Optional[str]
    readiness: str


@dataclass(frozen=True)
class PlannedSession:
    session_id: str
    session_mode: str
    policy: str
    project_id: str
    project_name: str
    initiative_type: str
    intent_raw: str
    intent_normalized: str
    run_id: str
    round_id: str
    parent_round_id: Optional[str]
    created_at_utc: str
    paths: ResolvedPaths
    dry_run: bool
    notes: Sequence[str]


class SessionStateError(Exception):
    pass


class SessionStateManager:
    def __init__(self, framework_root: Path) -> None:
        self.framework_root = framework_root
        self.projects_root = framework_root / 'ops' / 'projects'

    def list_projects(self) -> List[ProjectRecord]:
        if not self.projects_root.exists():
            return []
        records: List[ProjectRecord] = []
        for project_dir in sorted(self.projects_root.iterdir()):
            if not project_dir.is_dir():
                continue
            project_id = project_dir.name
            manifest_path = project_dir / 'project_manifest.json'
            manifest = self._read_json_if_exists(manifest_path)
            project_name = str(manifest.get('project_name', project_id))
            initiative_type = str(manifest.get('initiative_type', 'unknown'))
            latest_run_id = self._find_latest_id(project_dir / 'runs', RUN_PATTERN)
            latest_round_id = None
            if latest_run_id:
                latest_round_id = self._find_latest_id(project_dir / 'runs' / latest_run_id / 'rounds', ROUND_PATTERN)
            readiness = 'ready' if manifest_path.exists() else 'partial'
            records.append(
                ProjectRecord(
                    project_id=project_id,
                    project_name=project_name,
                    initiative_type=initiative_type,
                    project_root=project_dir,
                    latest_run_id=latest_run_id,
                    latest_round_id=latest_round_id,
                    readiness=readiness,
                )
            )
        return records

    def plan_session(
        self,
        *,
        session_mode: str,
        policy: str,
        project_id: str,
        project_name: Optional[str],
        initiative_type: Optional[str],
        intent_raw: str,
        dry_run: bool,
    ) -> PlannedSession:
        created_at = self._utc_now()
        normalized_intent = self._normalize_intent(intent_raw)
        notes: List[str] = []

        if session_mode == 'new_project':
            effective_project_name = project_name or project_id
            effective_initiative = initiative_type or 'unspecified'
            run_id = 'run_001'
            round_id = 'round_001'
            parent_round_id = None
            notes.append('Planned as a new project bootstrap session.')
        else:
            existing = self._load_project_record(project_id)
            if existing is None:
                raise SessionStateError(f"Existing project '{project_id}' was not found under {self.projects_root}.")
            effective_project_name = existing.project_name
            effective_initiative = existing.initiative_type
            if policy == 'resume_latest_round':
                if not existing.latest_run_id or not existing.latest_round_id:
                    raise SessionStateError(
                        f"Project '{project_id}' does not have a latest run/round to resume."
                    )
                run_id = existing.latest_run_id
                round_id = existing.latest_round_id
                parent_round_id = existing.latest_round_id
                notes.append('Planned to resume the latest known round without creating a new run or round.')
            elif policy == 'open_new_round':
                if not existing.latest_run_id:
                    raise SessionStateError(
                        f"Project '{project_id}' does not have an existing run. Use new_project or upgrade after bootstrap."
                    )
                run_id = existing.latest_run_id
                latest_round = existing.latest_round_id or 'round_000'
                round_id = self._next_identifier(latest_round, ROUND_PATTERN, 'round')
                parent_round_id = existing.latest_round_id
                notes.append('Planned to create a new round under the latest run.')
            elif policy == 'upgrade':
                latest_run = existing.latest_run_id or 'run_000'
                run_id = self._next_identifier(latest_run, RUN_PATTERN, 'run')
                round_id = 'round_001'
                parent_round_id = existing.latest_round_id
                notes.append('Planned to create a new run and start at round_001.')
            else:
                raise SessionStateError(f'Unsupported policy: {policy}')

        session_id = self._build_session_id(project_id, run_id, round_id, created_at)
        paths = build_paths(self.framework_root, project_id, run_id, round_id, session_id)

        return PlannedSession(
            session_id=session_id,
            session_mode=session_mode,
            policy=policy,
            project_id=project_id,
            project_name=effective_project_name,
            initiative_type=effective_initiative,
            intent_raw=intent_raw,
            intent_normalized=normalized_intent,
            run_id=run_id,
            round_id=round_id,
            parent_round_id=parent_round_id,
            created_at_utc=created_at,
            paths=paths,
            dry_run=dry_run,
            notes=tuple(notes),
        )

    def materialize_minimal_state(self, plan: PlannedSession) -> Dict[str, Path]:
        paths = plan.paths.project
        touched: Dict[str, Path] = {
            'project_manifest': paths.project_manifest_path,
            'run_manifest': paths.run_manifest_path,
            'round_manifest': paths.round_manifest_path,
        }
        if plan.dry_run:
            return touched

        for directory in (
            paths.project_root,
            paths.runs_root,
            paths.run_root,
            paths.rounds_root,
            paths.round_root,
            paths.bundles_root,
            paths.sessions_root,
            paths.state_root,
            paths.locks_root,
            paths.sessions_state_root,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        self._write_json(
            paths.project_manifest_path,
            {
                'schema_version': '1.0',
                'project_id': plan.project_id,
                'project_name': plan.project_name,
                'initiative_type': plan.initiative_type,
                'created_at_utc': plan.created_at_utc,
                'updated_at_utc': plan.created_at_utc,
                'source': 'one-button-wave3',
            },
        )
        self._write_json(
            paths.run_manifest_path,
            {
                'schema_version': '1.0',
                'project_id': plan.project_id,
                'run_id': plan.run_id,
                'policy': plan.policy,
                'created_at_utc': plan.created_at_utc,
                'updated_at_utc': plan.created_at_utc,
                'source': 'one-button-wave3',
            },
        )
        self._write_json(
            paths.round_manifest_path,
            {
                'schema_version': '1.0',
                'project_id': plan.project_id,
                'run_id': plan.run_id,
                'round_id': plan.round_id,
                'parent_round_id': plan.parent_round_id,
                'intent_raw': plan.intent_raw,
                'intent_normalized': plan.intent_normalized,
                'created_at_utc': plan.created_at_utc,
                'updated_at_utc': plan.created_at_utc,
                'source': 'one-button-wave3',
            },
        )
        return touched

    def _load_project_record(self, project_id: str) -> Optional[ProjectRecord]:
        for record in self.list_projects():
            if record.project_id == project_id:
                return record
        return None

    def _find_latest_id(self, directory: Path, pattern: re.Pattern[str]) -> Optional[str]:
        if not directory.exists():
            return None
        matches: List[tuple[int, str]] = []
        for item in directory.iterdir():
            if not item.is_dir():
                continue
            match = pattern.match(item.name)
            if match:
                matches.append((int(match.group(1)), item.name))
        if not matches:
            return None
        matches.sort()
        return matches[-1][1]

    def _next_identifier(self, latest_value: str, pattern: re.Pattern[str], prefix: str) -> str:
        match = pattern.match(latest_value)
        if not match:
            return f'{prefix}_001'
        next_number = int(match.group(1)) + 1
        return f'{prefix}_{next_number:03d}'

    def _build_session_id(self, project_id: str, run_id: str, round_id: str, created_at_utc: str) -> str:
        timestamp = created_at_utc.replace(':', '-').replace('.', '-').replace('Z', 'Z')
        return f'session_{project_id}_{run_id}_{round_id}_{timestamp}'

    def _normalize_intent(self, raw: str) -> str:
        normalized = ' '.join(raw.strip().split())
        if not normalized:
            raise SessionStateError('Intent cannot be empty after normalization.')
        return normalized

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    def _read_json_if_exists(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
