from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


Severity = str


@dataclass(slots=True, frozen=True)
class ScanConfig:
    version: str
    repo_markers: list[str]
    include_extensions: tuple[str, ...]
    max_file_bytes: int
    exclude_dir_names: frozenset[str]
    exclude_path_substrings: tuple[str, ...]
    probable_tooling_path_markers: tuple[str, ...]
    serverish_path_markers: tuple[str, ...]
    browser_api_tokens: tuple[str, ...]
    hydration_keywords: tuple[str, ...]
    diff_enabled: bool
    diff_base_ref: str
    diff_include_untracked: bool
    diff_staged_only: bool
    line_context_radius: int
    client_directive_window: int
    ignore_minified_lines_over: int
    finding_limit_per_rule_per_file: int


@dataclass(slots=True)
class ImportReference:
    specifier: str
    line_number: int
    is_type_only: bool = False


@dataclass(slots=True)
class FileFacts:
    abs_path: Path
    relpath: str
    extension: str
    size_bytes: int
    line_count: int
    sha1: str
    text: str
    lines: list[str]
    imports: list[ImportReference] = field(default_factory=list)
    has_use_client: bool = False
    has_use_server: bool = False
    probable_tooling_path: bool = False
    probable_serverish_path: bool = False
    probable_minified: bool = False

    def brief(self) -> dict[str, Any]:
        return {
            'relpath': self.relpath,
            'extension': self.extension,
            'size_bytes': self.size_bytes,
            'line_count': self.line_count,
            'has_use_client': self.has_use_client,
            'has_use_server': self.has_use_server,
            'probable_tooling_path': self.probable_tooling_path,
            'probable_serverish_path': self.probable_serverish_path,
            'imports': [asdict(item) for item in self.imports],
        }


@dataclass(slots=True)
class Finding:
    rule_id: str
    severity: Severity
    relpath: str
    line_number: int
    column_number: int
    message: str
    snippet: str
    excerpt: str
    ignored: bool = False
    tags: tuple[str, ...] = field(default_factory=tuple)
    details: dict[str, Any] = field(default_factory=dict)
    fingerprint: str = ''

    def ensure_fingerprint(self) -> 'Finding':
        if self.fingerprint:
            return self
        stable = '|'.join([
            self.rule_id,
            self.relpath,
            str(self.line_number),
            self._normalize(self.snippet),
        ])
        self.fingerprint = hashlib.sha1(stable.encode('utf-8')).hexdigest()
        return self

    def clone_with(self, **updates: Any) -> 'Finding':
        payload = self.to_dict()
        payload.update(updates)
        cloned = Finding.from_dict(payload)
        return cloned

    def to_dict(self) -> dict[str, Any]:
        self.ensure_fingerprint()
        return {
            'rule_id': self.rule_id,
            'severity': self.severity,
            'relpath': self.relpath,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'message': self.message,
            'snippet': self.snippet,
            'excerpt': self.excerpt,
            'ignored': self.ignored,
            'tags': list(self.tags),
            'details': self.details,
            'fingerprint': self.fingerprint,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> 'Finding':
        finding = cls(
            rule_id=str(payload['rule_id']),
            severity=str(payload['severity']),
            relpath=str(payload['relpath']),
            line_number=int(payload['line_number']),
            column_number=int(payload['column_number']),
            message=str(payload['message']),
            snippet=str(payload.get('snippet', '')),
            excerpt=str(payload.get('excerpt', '')),
            ignored=bool(payload.get('ignored', False)),
            tags=tuple(payload.get('tags', [])),
            details=dict(payload.get('details', {})),
            fingerprint=str(payload.get('fingerprint', '')),
        )
        return finding.ensure_fingerprint()

    @staticmethod
    def _normalize(value: str) -> str:
        return ' '.join(value.strip().split())[:280]


@dataclass(slots=True)
class ScanStats:
    files_discovered: int = 0
    files_scanned: int = 0
    files_skipped: int = 0
    findings_total: int = 0
    findings_active: int = 0
    baseline_ignored: int = 0


@dataclass(slots=True)
class ScanOutput:
    repo_root: str
    config_version: str
    baseline_path: str
    diff_mode: dict[str, Any]
    stats: ScanStats
    findings: list[Finding]
    inventory: list[FileFacts]
    meta: dict[str, Any] = field(default_factory=dict)

    def findings_by_rule(self, *, include_ignored: bool = False) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            if finding.ignored and not include_ignored:
                continue
            counts[finding.rule_id] = counts.get(finding.rule_id, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))

    def findings_by_severity(self, *, include_ignored: bool = False) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            if finding.ignored and not include_ignored:
                continue
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[0]))

    def to_summary(self) -> dict[str, Any]:
        return {
            'repo_root': self.repo_root,
            'config_version': self.config_version,
            'baseline_path': self.baseline_path,
            'stats': asdict(self.stats),
            'findings_by_rule': self.findings_by_rule(),
            'findings_by_severity': self.findings_by_severity(),
            'diff_mode': self.diff_mode,
            'meta': self.meta,
        }

    def to_findings_payload(self) -> dict[str, Any]:
        return {
            'summary': self.to_summary(),
            'findings': [finding.to_dict() for finding in self.findings],
            'inventory': [file_facts.brief() for file_facts in self.inventory],
        }
