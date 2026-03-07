from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .client_index import ClientBoundaryIndex
from .context import FileFacts, Finding, ImportReference, ScanConfig

_IMPORT_RE = re.compile(
    r"""
    ^\s*(?:import|export)\s+(?:type\s+)?(?:[^;]*?\s+from\s+)?[\"'](?P<import1>[^\"']+)[\"']
    |^\s*const\s+[^=]+?=\s*require\([\"'](?P<import2>[^\"']+)[\"']\)
    |^\s*import\([\"'](?P<import3>[^\"']+)[\"']\)
    """,
    re.VERBOSE,
)


class RepoScanner:
    def __init__(self, repo_root: str | Path, config: ScanConfig) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.config = config

    def discover_files(self) -> list[Path]:
        discovered: list[Path] = []
        for abs_path in self.repo_root.rglob('*'):
            if not abs_path.is_file():
                continue
            relpath = self._relpath(abs_path)
            if not self._should_scan(relpath=relpath, abs_path=abs_path):
                continue
            discovered.append(abs_path)
        discovered.sort()
        return discovered

    def build_file_facts(self, abs_path: Path) -> FileFacts | None:
        relpath = self._relpath(abs_path)
        stat = abs_path.stat()
        if stat.st_size > self.config.max_file_bytes:
            return None
        text = abs_path.read_text(encoding='utf-8', errors='replace')
        lines = text.splitlines()
        probable_minified = any(len(line) > self.config.ignore_minified_lines_over for line in lines[:20])
        imports = self._extract_imports(lines)
        has_use_client, has_use_server = self._detect_directives(lines)
        lower_relpath = relpath.lower()
        probable_tooling_path = any(marker.lower() in lower_relpath for marker in self.config.probable_tooling_path_markers)
        probable_serverish_path = any(marker.lower() in lower_relpath for marker in self.config.serverish_path_markers)
        sha1 = hashlib.sha1(text.encode('utf-8', errors='replace')).hexdigest()
        return FileFacts(
            abs_path=abs_path,
            relpath=relpath,
            extension=abs_path.suffix.lower(),
            size_bytes=stat.st_size,
            line_count=len(lines),
            sha1=sha1,
            text=text,
            lines=lines,
            imports=imports,
            has_use_client=has_use_client,
            has_use_server=has_use_server,
            probable_tooling_path=probable_tooling_path,
            probable_serverish_path=probable_serverish_path,
            probable_minified=probable_minified,
        )

    def scan_file(self, file_facts: FileFacts, client_index: ClientBoundaryIndex) -> list[Finding]:
        findings: list[Finding] = []
        per_rule_counts: defaultdict[str, int] = defaultdict(int)
        lines = file_facts.lines
        lower_lines = [line.lower() for line in lines]

        def push(finding: Finding) -> None:
            if per_rule_counts[finding.rule_id] >= self.config.finding_limit_per_rule_per_file:
                return
            finding.ensure_fingerprint()
            per_rule_counts[finding.rule_id] += 1
            findings.append(finding)

        imports_client = client_index.imports_client(file_facts.relpath)
        if imports_client and (file_facts.probable_serverish_path or not file_facts.has_use_client):
            for target in imports_client[:10]:
                push(
                    self._make_finding(
                        file_facts=file_facts,
                        rule_id='server_to_client_import_hint',
                        severity='low',
                        line_number=1,
                        column_number=1,
                        message=f'File imports explicit client module: {target}',
                        snippet=target,
                        details={'target': target, 'kind': 'boundary-hint'},
                        tags=('boundary', 'client-index'),
                    )
                )

        browser_hits = 0
        dynamic_ssr_false_hits = 0
        for line_number, line in enumerate(lines, start=1):
            lowered = lower_lines[line_number - 1]
            if not lowered.strip():
                continue
            if self._looks_like_comment(lowered):
                continue
            if 'suppresshydrationwarning' in lowered:
                push(
                    self._make_finding(
                        file_facts=file_facts,
                        rule_id='suppress_hydration_warning',
                        severity='medium',
                        line_number=line_number,
                        column_number=max(1, lowered.index('suppresshydrationwarning') + 1),
                        message='suppressHydrationWarning detected. Keep this as a narrow exception with documented root cause.',
                        snippet=line.strip(),
                        details={'kind': 'hydration-suppression'},
                        tags=('hydration', 'suppression'),
                    )
                )
            if 'ssr: false' in lowered or 'ssr:false' in lowered:
                dynamic_ssr_false_hits += 1
                push(
                    self._make_finding(
                        file_facts=file_facts,
                        rule_id='dynamic_ssr_false',
                        severity='medium',
                        line_number=line_number,
                        column_number=max(1, lowered.find('ssr') + 1),
                        message='dynamic(..., { ssr: false }) style pattern detected. Confirm it is narrowly scoped.',
                        snippet=line.strip(),
                        details={'kind': 'dynamic-ssr-false'},
                        tags=('hydration', 'dynamic-import'),
                    )
                )
            for token in self.config.browser_api_tokens:
                if not self._contains_token(lowered, token.lower()):
                    continue
                browser_hits += 1
                if not file_facts.has_use_client:
                    push(
                        self._make_finding(
                            file_facts=file_facts,
                            rule_id='browser_api_in_non_client',
                            severity='low',
                            line_number=line_number,
                            column_number=max(1, lowered.find(token.lower()) + 1),
                            message=f'Browser API token {token} found outside an explicit client file.',
                            snippet=line.strip(),
                            details={'token': token, 'kind': 'browser-api'},
                            tags=('browser-api', 'ssr-boundary'),
                        )
                    )
            for keyword in self.config.hydration_keywords:
                if keyword.lower() in lowered:
                    push(
                        self._make_finding(
                            file_facts=file_facts,
                            rule_id='hydration_keyword',
                            severity='info',
                            line_number=line_number,
                            column_number=max(1, lowered.find(keyword.lower()) + 1),
                            message=f'Hydration keyword matched: {keyword}',
                            snippet=line.strip(),
                            details={'keyword': keyword, 'kind': 'context-signal'},
                            tags=('hydration', 'context'),
                        )
                    )

        if (browser_hits > 0 or dynamic_ssr_false_hits > 0) and file_facts.probable_tooling_path:
            push(
                self._make_finding(
                    file_facts=file_facts,
                    rule_id='client_boundary_hint',
                    severity='low',
                    line_number=1,
                    column_number=1,
                    message='Probable tooling surface touches browser APIs. Consider a narrow client-only boundary.',
                    snippet=file_facts.relpath,
                    details={'browser_hit_count': browser_hits, 'dynamic_ssr_false_hits': dynamic_ssr_false_hits, 'kind': 'tooling-boundary'},
                    tags=('boundary', 'tooling'),
                )
            )

        return findings

    def _should_scan(self, *, relpath: str, abs_path: Path) -> bool:
        if abs_path.suffix.lower() not in self.config.include_extensions:
            return False
        parts = {part.lower() for part in Path(relpath).parts}
        if any(excluded.lower() in parts for excluded in self.config.exclude_dir_names):
            return False
        lowered = relpath.lower()
        for needle in self.config.exclude_path_substrings:
            if needle.lower().replace('\\', '/') in lowered:
                return False
        return True

    def _extract_imports(self, lines: Iterable[str]) -> list[ImportReference]:
        refs: list[ImportReference] = []
        for line_number, line in enumerate(lines, start=1):
            match = _IMPORT_RE.search(line)
            if not match:
                continue
            specifier = match.group('import1') or match.group('import2') or match.group('import3')
            is_type_only = 'import type' in line or 'export type' in line
            refs.append(ImportReference(specifier=specifier, line_number=line_number, is_type_only=is_type_only))
        return refs

    def _detect_directives(self, lines: list[str]) -> tuple[bool, bool]:
        has_use_client = False
        has_use_server = False
        meaningful = 0
        for line in lines:
            stripped = line.strip().strip(';')
            if not stripped:
                continue
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            meaningful += 1
            if stripped in {'"use client"', "'use client'"}:
                has_use_client = True
            if stripped in {'"use server"', "'use server'"}:
                has_use_server = True
            if meaningful >= self.config.client_directive_window:
                break
        return has_use_client, has_use_server

    def _make_finding(
        self,
        *,
        file_facts: FileFacts,
        rule_id: str,
        severity: str,
        line_number: int,
        column_number: int,
        message: str,
        snippet: str,
        details: dict[str, object],
        tags: tuple[str, ...],
    ) -> Finding:
        excerpt = self._excerpt(file_facts.lines, line_number)
        return Finding(
            rule_id=rule_id,
            severity=severity,
            relpath=file_facts.relpath,
            line_number=line_number,
            column_number=column_number,
            message=message,
            snippet=snippet[:500],
            excerpt=excerpt,
            tags=tags,
            details=details,
        ).ensure_fingerprint()

    def _excerpt(self, lines: list[str], line_number: int) -> str:
        start = max(1, line_number - self.config.line_context_radius)
        end = min(len(lines), line_number + self.config.line_context_radius)
        fragments = []
        for current in range(start, end + 1):
            prefix = '>' if current == line_number else ' '
            fragments.append(f'{prefix} {current:04d}: {lines[current - 1]}')
        return '\n'.join(fragments)

    @staticmethod
    def _contains_token(line: str, token: str) -> bool:
        if token in {'window', 'document', 'navigator', 'location', 'history'}:
            return f'{token}.' in line or f'{token}[' in line or f'{token}?' in line or f'{token} ' in line
        return token in line

    @staticmethod
    def _looks_like_comment(line: str) -> bool:
        stripped = line.lstrip()
        return stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*')

    def _relpath(self, abs_path: Path) -> str:
        return str(abs_path.relative_to(self.repo_root)).replace('\\', '/')
