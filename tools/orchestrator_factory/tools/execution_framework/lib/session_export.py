"""Canonical session export for one-button v1.2.

This module stages the required runtime artifacts, emits a canonical session ZIP,
validates it with validate_session_zip_contract.py, writes sidecars, and copies a
handoff bundle to the configured operator directory when enabled.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from copy import deepcopy
from typing import Any, Dict, List, Optional

from acceptance_stub import build_acceptance_stub
from session_manifest import SessionManifestBuilder
from session_state import PlannedSession


class SessionExportError(Exception):
    pass


@dataclass(frozen=True)
class SessionExportResult:
    canonical_zip_path: str
    canonical_zip_sha256: str
    canonical_zip_size_bytes: int
    handoff_copy_path: Optional[str]
    validation_report: Dict[str, Any]
    issues: List[Dict[str, Any]]


class SessionExporter:
    LAUNCHER_VERSION = '1.2.0-wave4'
    INTERNAL_MANIFEST_PLACEHOLDER_SHA256 = '0' * 64

    def __init__(self, framework_root: Path) -> None:
        self.framework_root = framework_root
        self.execution_framework_root = framework_root / 'tools' / 'execution_framework'
        self.validator_path = self.execution_framework_root / 'validate_session_zip_contract.py'
        self.config_path = framework_root / 'configs' / 'execution_framework' / 'one_button_config.json'

    def export_session(
        self,
        *,
        plan: PlannedSession,
        checks: Dict[str, str],
        idempotency_key: str,
        idempotency_decision: str,
        context_hashes: Dict[str, str],
        lock_id: Optional[str],
        lock_path: Path,
        lock_pid: int,
        lock_host: str,
    ) -> SessionExportResult:
        config = self._load_config()
        issues: List[Dict[str, Any]] = []

        self._ensure_runtime_stubs(plan)

        with tempfile.TemporaryDirectory(prefix='one_button_export_') as tmp_dir_str:
            tmp_dir = Path(tmp_dir_str)
            stage_root = tmp_dir / 'stage'
            stage_root.mkdir(parents=True, exist_ok=True)

            self._stage_required_files(stage_root=stage_root, plan=plan)
            manifest_builder = SessionManifestBuilder()
            # Integrity source-of-truth model:
            # - session/session_manifest.json (inside ZIP) is a staging/runtime record and does
            #   not carry self-referential final ZIP hash/size values.
            # - <session_id>.manifest.json (sidecar) is the authoritative record for final ZIP
            #   bytes, checksum, and size.
            internal_manifest_payload = manifest_builder.build(
                plan=plan,
                launcher_version=self.LAUNCHER_VERSION,
                status='ready_for_dispatch',
                checks=checks,
                idempotency_key=idempotency_key,
                idempotency_decision=idempotency_decision,
                context_hashes=context_hashes,
                lock_id=lock_id,
                lock_path=str(lock_path),
                lock_pid=lock_pid,
                lock_host=lock_host,
                session_zip_path=str(plan.paths.export_hints.canonical_zip_path),
                session_zip_sha256=self.INTERNAL_MANIFEST_PLACEHOLDER_SHA256,
                session_zip_size_bytes=0,
                handoff_copy_path=None,
                issues=[],
            )
            session_manifest_relpath = 'session/session_manifest.json'
            self._write_json(stage_root / session_manifest_relpath, internal_manifest_payload)

            file_index_relpath = 'session/session_file_index.json'
            self._write_json(stage_root / file_index_relpath, self._build_file_index(stage_root, exclude={file_index_relpath}))

            canonical_zip_path = plan.paths.export_hints.canonical_zip_path
            canonical_zip_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_zip(stage_root, canonical_zip_path)

            zip_sha256 = self._sha256_file(canonical_zip_path)
            zip_size = canonical_zip_path.stat().st_size

            validation_report = self._validate_zip(canonical_zip_path)
            validation_errors = validation_report.get('validation', {}).get('errors', [])
            validation_warnings = validation_report.get('validation', {}).get('warnings', [])
            if validation_errors:
                raise SessionExportError('Session ZIP failed contract validation: ' + '; '.join(validation_errors))
            for warning in validation_warnings:
                issues.append({'severity': 'warning', 'code': 'zip_contract_warning', 'message': warning})

            handoff_copy_path = self._copy_handoff_if_enabled(
                canonical_zip_path=canonical_zip_path,
                config=config,
                issues=issues,
            )

            sidecar_manifest_payload = self._build_authoritative_sidecar_manifest(
                internal_manifest_payload=internal_manifest_payload,
                canonical_zip_path=canonical_zip_path,
                zip_sha256=zip_sha256,
                zip_size=zip_size,
                handoff_copy_path=handoff_copy_path,
                issues=issues,
            )

            self._emit_sidecars(
                canonical_zip_path=canonical_zip_path,
                canonical_sha256_sidecar_path=plan.paths.export_hints.canonical_sha256_sidecar_path,
                canonical_manifest_sidecar_path=plan.paths.export_hints.canonical_manifest_sidecar_path,
                manifest_payload=sidecar_manifest_payload,
                zip_sha256=zip_sha256,
                config=config,
            )

            return SessionExportResult(
                canonical_zip_path=str(canonical_zip_path),
                canonical_zip_sha256=zip_sha256,
                canonical_zip_size_bytes=zip_size,
                handoff_copy_path=handoff_copy_path,
                validation_report=validation_report,
                issues=issues,
            )

    def _build_authoritative_sidecar_manifest(
        self,
        *,
        internal_manifest_payload: Dict[str, Any],
        canonical_zip_path: Path,
        zip_sha256: str,
        zip_size: int,
        handoff_copy_path: Optional[str],
        issues: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        sidecar_payload = deepcopy(internal_manifest_payload)
        sidecar_payload['artifacts']['session_zip_path'] = str(canonical_zip_path)
        sidecar_payload['artifacts']['session_zip_sha256'] = zip_sha256
        sidecar_payload['artifacts']['session_zip_size_bytes'] = zip_size
        sidecar_payload['artifacts']['handoff_copy_path'] = handoff_copy_path
        sidecar_payload['issues'] = list(issues)
        return sidecar_payload

    def _load_config(self) -> Dict[str, Any]:
        with self.config_path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def _ensure_runtime_stubs(self, plan: PlannedSession) -> None:
        p = plan.paths.project
        for directory in (
            p.coordination_snapshots_root,
            p.reports_root,
            p.packets_root,
            p.prompts_root,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        if not p.coordination_snapshot_json_path.exists():
            self._write_json(
                p.coordination_snapshot_json_path,
                {
                    'schema_version': '1.0',
                    'project_id': plan.project_id,
                    'run_id': plan.run_id,
                    'round_id': plan.round_id,
                    'generated_at_utc': plan.created_at_utc,
                    'status': 'initialized',
                    'agents': [],
                    'notes': ['Wave 4 generated a stub coordination snapshot because no runtime snapshot existed yet.'],
                },
            )
        if not p.coordination_snapshot_md_path.exists():
            p.coordination_snapshot_md_path.write_text(
                '\n'.join([
                    '# Coordination Snapshot',
                    '',
                    f'- Project: {plan.project_id}',
                    f'- Run: {plan.run_id}',
                    f'- Round: {plan.round_id}',
                    '- Status: initialized',
                    '- Note: Stub snapshot generated by wave 4 export path.',
                ]),
                encoding='utf-8',
            )
        if not p.readiness_report_path.exists():
            self._write_json(
                p.readiness_report_path,
                {
                    'schema_version': '1.0',
                    'project_id': plan.project_id,
                    'run_id': plan.run_id,
                    'round_id': plan.round_id,
                    'generated_at_utc': plan.created_at_utc,
                    'readiness_stage_install': 'ready',
                    'readiness_stage_round': 'ready',
                    'issues': [],
                },
            )
        if not p.acceptance_report_path.exists():
            self._write_json(
                p.acceptance_report_path,
                build_acceptance_stub(
                    project_id=plan.project_id,
                    run_id=plan.run_id,
                    round_id=plan.round_id,
                    generated_at_utc=plan.created_at_utc,
                ),
            )

    def _stage_required_files(self, *, stage_root: Path, plan: PlannedSession) -> Dict[str, Path]:
        p = plan.paths.project
        stage_map: Dict[str, Path] = {}
        copies = {
            'project/project_manifest.json': p.project_manifest_path,
            'run/run_manifest.json': p.run_manifest_path,
            'round/round_manifest.json': p.round_manifest_path,
            'round/coordination/snapshots/coordination_snapshot.latest.json': p.coordination_snapshot_json_path,
            'round/coordination/snapshots/coordination_snapshot.latest.md': p.coordination_snapshot_md_path,
            'round/reports/readiness_report.json': p.readiness_report_path,
            'round/reports/acceptance_report.json': p.acceptance_report_path,
        }
        for relpath, source in copies.items():
            target = stage_root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            stage_map[relpath] = target

        (stage_root / 'session').mkdir(parents=True, exist_ok=True)
        (stage_root / 'session' / 'session_summary.md').write_text(
            self._build_session_summary(plan), encoding='utf-8'
        )
        (stage_root / 'session' / 'operator_instructions.md').write_text(
            self._build_operator_instructions(plan), encoding='utf-8'
        )
        (stage_root / 'session' / 'intake_normalized.md').write_text(
            self._build_intake_normalized(plan), encoding='utf-8'
        )
        stage_map['session/session_summary.md'] = stage_root / 'session' / 'session_summary.md'
        stage_map['session/operator_instructions.md'] = stage_root / 'session' / 'operator_instructions.md'
        stage_map['session/intake_normalized.md'] = stage_root / 'session' / 'intake_normalized.md'

        packet_matches = sorted(p.packets_root.glob('*/work_packet.json'))
        for packet_path in packet_matches:
            relpath = 'round/packets/' + '/'.join(packet_path.relative_to(p.packets_root).parts)
            target = stage_root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(packet_path, target)
            stage_map[relpath] = target

        prompt_matches = sorted(p.prompts_root.glob('*.prompt.md'))
        for prompt_path in prompt_matches:
            relpath = 'round/prompts/' + prompt_path.name
            target = stage_root / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(prompt_path, target)
            stage_map[relpath] = target
        return stage_map

    def _validate_zip(self, canonical_zip_path: Path) -> Dict[str, Any]:
        report_path = canonical_zip_path.with_suffix('.validation.json')
        cmd = [
            sys.executable,
            str(self.validator_path),
            '--framework-root',
            str(self.framework_root),
            '--zip-path',
            str(canonical_zip_path),
            '--output-report',
            str(report_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode not in (0, 1):
            raise SessionExportError(
                'ZIP contract validator failed to run: ' + (proc.stderr.strip() or proc.stdout.strip())
            )
        if not report_path.exists():
            raise SessionExportError('ZIP validator did not emit the expected validation report.')
        with report_path.open('r', encoding='utf-8') as fh:
            report = json.load(fh)
        try:
            report_path.unlink(missing_ok=True)
        except TypeError:
            if report_path.exists():
                report_path.unlink()
        return report

    def _copy_handoff_if_enabled(self, *, canonical_zip_path: Path, config: Dict[str, Any], issues: List[Dict[str, Any]]) -> Optional[str]:
        handoff_cfg = config.get('handoff_copy', {})
        if not handoff_cfg.get('enabled', True):
            return None
        target_dirs: List[str] = []
        preferred = handoff_cfg.get('handoff_copy_dir')
        if preferred:
            target_dirs.append(str(preferred))
        target_dirs.extend(str(item) for item in handoff_cfg.get('fallback_directories', []))
        normalized_dirs: List[Path] = []
        for raw in target_dirs:
            expanded = os.path.expandvars(raw)
            normalized_dirs.append(Path(expanded))
        for target_dir in normalized_dirs:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / canonical_zip_path.name
                shutil.copy2(canonical_zip_path, target_path)
                return str(target_path)
            except Exception as exc:
                issues.append({'severity': 'warning', 'code': 'handoff_copy_failed', 'message': f'Failed to copy session ZIP to {target_dir}: {exc}'})
                continue
        if handoff_cfg.get('fail_session_if_copy_fails', False):
            raise SessionExportError('Handoff copy failed and configuration requires the session to fail.')
        return None

    def _emit_sidecars(
        self,
        *,
        canonical_zip_path: Path,
        canonical_sha256_sidecar_path: Path,
        canonical_manifest_sidecar_path: Path,
        manifest_payload: Dict[str, Any],
        zip_sha256: str,
        config: Dict[str, Any],
    ) -> None:
        export_cfg = config.get('session_export', {})
        if export_cfg.get('emit_sha256_sidecar', True):
            canonical_sha256_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
            canonical_sha256_sidecar_path.write_text(f'{zip_sha256}  {canonical_zip_path.name}\n', encoding='utf-8')
        if export_cfg.get('emit_manifest_sidecar', True):
            canonical_manifest_sidecar_path.parent.mkdir(parents=True, exist_ok=True)
            with canonical_manifest_sidecar_path.open('w', encoding='utf-8') as fh:
                json.dump(manifest_payload, fh, indent=2, ensure_ascii=False)

    def _build_file_index(self, stage_root: Path, exclude: Optional[set[str]] = None) -> List[Dict[str, Any]]:
        exclude = exclude or set()
        rows: List[Dict[str, Any]] = []
        for path in sorted(stage_root.rglob('*')):
            if not path.is_file():
                continue
            relpath = path.relative_to(stage_root).as_posix()
            if relpath in exclude:
                continue
            rows.append({
                'path': relpath,
                'sha256': self._sha256_file(path),
                'size_bytes': path.stat().st_size,
            })
        return rows

    @staticmethod
    def _build_session_summary(plan: PlannedSession) -> str:
        return '\n'.join([
            '# Session Summary',
            '',
            f'- Session ID: {plan.session_id}',
            f'- Session mode: {plan.session_mode}',
            f'- Policy: {plan.policy}',
            f'- Project: {plan.project_id}',
            f'- Run: {plan.run_id}',
            f'- Round: {plan.round_id}',
            f'- Intent: {plan.intent_normalized}',
        ])

    @staticmethod
    def _build_operator_instructions(plan: PlannedSession) -> str:
        return '\n'.join([
            '# Operator Instructions',
            '',
            '1. Verify the canonical ZIP path and optional handoff copy path.',
            '2. If this session is marked ready_for_dispatch, deliver the ZIP back into ChatGPT for prompt generation.',
            '3. If warnings exist, review session_manifest.json issues[] before proceeding.',
            '',
            f'- Project: {plan.project_id}',
            f'- Session: {plan.session_id}',
        ])

    @staticmethod
    def _build_intake_normalized(plan: PlannedSession) -> str:
        return '\n'.join([
            '# Intake Normalized',
            '',
            f'- Raw intent: {plan.intent_raw}',
            f'- Normalized intent: {plan.intent_normalized}',
            f'- Session mode: {plan.session_mode}',
            f'- Policy: {plan.policy}',
        ])

    @staticmethod
    def _write_json(path: Path, payload: Dict[str, Any] | List[Dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    @staticmethod
    def _write_zip(stage_root: Path, zip_path: Path) -> None:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage_root.rglob('*')):
                if not path.is_file():
                    continue
                archive.write(path, path.relative_to(stage_root).as_posix())

    @staticmethod
    def _sha256_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open('rb') as fh:
            while True:
                chunk = fh.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
