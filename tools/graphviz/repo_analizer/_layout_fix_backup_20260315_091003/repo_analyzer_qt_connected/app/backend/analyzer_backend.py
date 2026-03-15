#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import json
import os
import re
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from app.config import (
    DEFAULT_MAX_RESULTS,
    DEFAULT_SEARCH_EXTS,
    EXCLUDED_DIRS,
    IMPORT_SCAN_EXTS,
    MAX_PREVIEW_FILE_SIZE,
    SETTINGS_FILE,
)
from app.helpers import extract_imports, human_size, read_text_safe, resolve_import

ProgressCallback = Callable[[str], None]


@dataclass
class SearchResult:
    relpath: str
    abspath: str
    display_path: str
    modified: str
    modified_ts: float
    size: int
    ext: str
    line: int
    matches: int
    snippet: str


@dataclass
class PreviewData:
    relpath: str
    abspath: str
    title: str
    rendered_text: str
    line: int
    imports: list[tuple[str, str]]
    dependents: list[str]


class AnalyzerBackend:
    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.settings_path = self.project_root / SETTINGS_FILE
        self.settings = self.load_settings()
        self.preview_text_exts = {
            ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
            ".json", ".md", ".mdx", ".txt", ".csv", ".tsv", ".log", ".svg", ".xml",
            ".html", ".htm", ".css", ".scss", ".yml", ".yaml", ".toml", ".ini", ".cfg",
            ".sql", ".sh", ".bat", ".ps1", ".java", ".kt", ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
        }

    def load_settings(self) -> dict[str, Any]:
        defaults = {
            "recent_repos": [],
            "recent_searches": [],
            "last_repo": "",
            "last_folder_filter": "(todo)",
            "last_ext_filter": "(todas)",
            "bookmarks": {},
        }
        if not self.settings_path.exists():
            return defaults
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                defaults.update(data)
        except Exception:
            pass
        return defaults

    def save_settings(self) -> None:
        self.settings_path.write_text(
            json.dumps(self.settings, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @staticmethod
    def _dedupe_keep_order(items: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for item in items:
            x = (item or "").strip()
            if not x:
                continue
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def remember_repo(self, repo_path: str) -> None:
        repo_path = repo_path.strip()
        if not repo_path:
            return
        self.settings["recent_repos"] = self._dedupe_keep_order([repo_path, *self.settings.get("recent_repos", [])])[:20]
        self.settings["last_repo"] = repo_path
        self.save_settings()

    def remember_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            return
        self.settings["recent_searches"] = self._dedupe_keep_order([query, *self.settings.get("recent_searches", [])])[:50]
        self.save_settings()

    def update_filter_settings(self, folder_filter: str, ext_filter: str) -> None:
        self.settings["last_folder_filter"] = folder_filter
        self.settings["last_ext_filter"] = ext_filter
        self.save_settings()

    def get_repo_bookmarks(self, repo_path: str) -> list[str]:
        repo = repo_path.strip()
        return list(self.settings.setdefault("bookmarks", {}).get(repo, []))

    def add_bookmark(self, repo_path: str, relpath: str) -> None:
        repo = repo_path.strip()
        bookmarks = self.get_repo_bookmarks(repo)
        bookmarks.append(relpath)
        self.settings.setdefault("bookmarks", {})[repo] = sorted(set(bookmarks))
        self.save_settings()

    def remove_bookmark(self, repo_path: str, relpath: str) -> None:
        repo = repo_path.strip()
        bookmarks = [x for x in self.get_repo_bookmarks(repo) if x != relpath]
        self.settings.setdefault("bookmarks", {})[repo] = bookmarks
        self.save_settings()

    def index_repo(self, repo_path: Path, include_hidden: bool = False, progress: ProgressCallback | None = None) -> dict[str, Any]:
        t0 = time.time()
        files: dict[str, dict[str, Any]] = {}
        folder_counts: Counter[str] = Counter()
        top_level_counts: Counter[str] = Counter()
        ext_counts: Counter[str] = Counter()
        dependents: dict[str, list[str]] = defaultdict(list)
        skipped = 0
        all_paths: list[Path] = []

        for dirpath, dirnames, filenames in os.walk(repo_path):
            dir_path = Path(dirpath)
            filtered: list[str] = []
            for d in dirnames:
                if d in EXCLUDED_DIRS:
                    continue
                if not include_hidden and d.startswith('.'):
                    continue
                filtered.append(d)
            dirnames[:] = filtered

            for fn in filenames:
                if not include_hidden and fn.startswith('.'):
                    continue
                all_paths.append(dir_path / fn)

        total_candidates = len(all_paths)
        if progress:
            progress(f"Escaneando {total_candidates} archivos candidatos…")

        for idx, path in enumerate(all_paths, start=1):
            try:
                rel = path.relative_to(repo_path).as_posix()
                ext = path.suffix.lower()
                stat = path.stat()
                size = stat.st_size
                mtime = stat.st_mtime
                modified = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                is_text = path.suffix.lower() in DEFAULT_SEARCH_EXTS

                imports: list[str] = []
                if path.suffix.lower() in IMPORT_SCAN_EXTS and size <= MAX_PREVIEW_FILE_SIZE:
                    try:
                        txt = read_text_safe(path)
                        imports = extract_imports(txt)
                    except Exception:
                        imports = []

                files[rel] = {
                    'relpath': rel,
                    'abspath': str(path),
                    'ext': ext,
                    'size': size,
                    'mtime': mtime,
                    'modified': modified,
                    'imports': imports,
                    'is_text': is_text,
                }
                ext_counts[ext] += 1

                parts = rel.split('/')
                if len(parts) > 1:
                    for i in range(1, len(parts)):
                        folder = '/'.join(parts[:i])
                        folder_counts[folder] += 1
                    top_level_counts[parts[0]] += 1
                else:
                    folder_counts['(root)'] += 1
                    top_level_counts['(root)'] += 1

                if progress and (idx % 100 == 0 or idx == total_candidates):
                    progress(f"Indexando {idx}/{total_candidates}…")
            except Exception:
                skipped += 1
                continue

        for rel, info in files.items():
            src_path = Path(info['abspath'])
            for raw_imp in info.get('imports', []):
                resolved = resolve_import(repo_path, src_path, raw_imp)
                if resolved and resolved in files:
                    dependents[resolved].append(rel)

        elapsed = time.time() - t0
        return {
            'root': str(repo_path),
            'files': files,
            'folder_counts': dict(sorted(folder_counts.items())),
            'top_level_counts': dict(sorted(top_level_counts.items(), key=lambda x: (-x[1], x[0]))),
            'ext_counts': dict(sorted(ext_counts.items(), key=lambda x: (-x[1], x[0]))),
            'dependents': {k: sorted(set(v)) for k, v in dependents.items()},
            'stats': {
                'total_candidates': total_candidates,
                'total_files': len(files),
                'skipped': skipped,
                'elapsed_sec': round(elapsed, 2),
                'largest_files': sorted(
                    [{'relpath': r, 'size': f['size']} for r, f in files.items()],
                    key=lambda x: x['size'],
                    reverse=True,
                )[:15],
            },
        }

    def search(
        self,
        index_data: dict[str, Any],
        query: str,
        folder: str,
        ext_filter: str,
        sort_mode: str,
        case_sensitive: bool,
        is_regex: bool,
        whole_word: bool,
        names_only: bool,
        max_results: int = DEFAULT_MAX_RESULTS,
        progress: ProgressCallback | None = None,
    ) -> list[SearchResult]:
        files_snapshot = dict(index_data.get('files', {}))
        results: list[SearchResult] = []

        def file_allowed(rel: str, ext: str) -> bool:
            normalized_ext_filter = ext_filter.strip() or '(todas)'
            if folder != '(todo)':
                if rel != folder and not rel.startswith(folder + '/'):
                    return False
            if normalized_ext_filter == 'TS/JS':
                return ext in {'.ts', '.tsx', '.js', '.jsx'}
            if normalized_ext_filter == '(todas)':
                return True
            if normalized_ext_filter == '(sin extensión)':
                return not ext
            return ext == normalized_ext_filter

        compiled = None
        if query:
            if is_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                compiled = re.compile(query, flags)
            else:
                q = re.escape(query)
                if whole_word:
                    q = rf"\b{q}\b"
                flags = 0 if case_sensitive else re.IGNORECASE
                compiled = re.compile(q, flags)

        candidates = [(rel, info) for rel, info in files_snapshot.items() if file_allowed(rel, info.get('ext', ''))]
        total = len(candidates)

        for idx, (rel, info) in enumerate(candidates, start=1):
            abspath = info['abspath']
            ext = info.get('ext', '')
            display_path = os.path.splitext(abspath)[0]
            modified = info.get('modified', '')
            modified_ts = float(info.get('mtime', 0.0) or 0.0)
            size = int(info.get('size', 0) or 0)

            if progress and (idx % 75 == 0 or idx == total):
                progress(f'Buscando {idx}/{total}…')

            if names_only:
                haystack = rel if case_sensitive else rel.lower()
                needle = query if case_sensitive else query.lower()
                if not query or (needle in haystack):
                    results.append(SearchResult(
                        relpath=rel,
                        abspath=abspath,
                        display_path=display_path,
                        modified=modified,
                        modified_ts=modified_ts,
                        size=size,
                        ext=ext or '(sin extensión)',
                        line=0,
                        matches=1 if query else 0,
                        snippet=rel,
                    ))
                if len(results) >= max_results:
                    break
                continue

            if not query:
                results.append(SearchResult(
                    relpath=rel,
                    abspath=abspath,
                    display_path=display_path,
                    modified=modified,
                    modified_ts=modified_ts,
                    size=size,
                    ext=ext or '(sin extensión)',
                    line=0,
                    matches=0,
                    snippet=rel,
                ))
                if len(results) >= max_results:
                    break
                continue

            path = Path(abspath)
            try:
                if not info.get('is_text', False):
                    continue
                if path.stat().st_size > MAX_PREVIEW_FILE_SIZE:
                    continue
                text = read_text_safe(path)
            except Exception:
                continue

            first_line = 0
            first_snippet = ''
            total_hits = 0
            for line_no, line in enumerate(text.splitlines(), start=1):
                if compiled is None:
                    continue
                line_hits = compiled.findall(line)
                if line_hits:
                    hits_count = len(line_hits) if isinstance(line_hits, list) else 1
                    total_hits += hits_count
                    if first_line == 0:
                        first_line = line_no
                        first_snippet = line.strip()

            if total_hits:
                results.append(SearchResult(
                    relpath=rel,
                    abspath=abspath,
                    display_path=display_path,
                    modified=modified,
                    modified_ts=modified_ts,
                    size=size,
                    ext=ext or '(sin extensión)',
                    line=first_line,
                    matches=total_hits,
                    snippet=first_snippet,
                ))
                if len(results) >= max_results:
                    break

        if sort_mode == 'path':
            results.sort(key=lambda r: (r.display_path.lower(), r.line, r.relpath.lower()))
        elif sort_mode == 'modified':
            results.sort(key=lambda r: (-r.modified_ts, r.display_path.lower()))
        elif sort_mode == 'size':
            results.sort(key=lambda r: (-r.size, r.display_path.lower()))
        elif sort_mode == 'ext':
            results.sort(key=lambda r: (r.ext.lower(), r.display_path.lower()))

        return results

    def build_preview(
        self,
        index_data: dict[str, Any],
        relpath: str,
        line: int = 0,
    ) -> PreviewData:
        info = index_data.get('files', {}).get(relpath)
        if not info:
            raise FileNotFoundError(f'No existe relpath en índice: {relpath}')

        abspath = info['abspath']
        path = Path(abspath)
        if not path.exists():
            raise FileNotFoundError(f'El archivo ya no existe: {abspath}')

        size = path.stat().st_size
        ext = path.suffix.lower()

        if self._is_probably_binary(path):
            text = self._build_file_fact_sheet(relpath, path, size, 'archivo binario')
        elif size > MAX_PREVIEW_FILE_SIZE:
            text = self._build_file_fact_sheet(relpath, path, size, 'archivo demasiado grande para preview completo')
        elif ext and ext not in self.preview_text_exts and size > 250_000:
            text = self._build_file_fact_sheet(relpath, path, size, 'tipo no textual grande')
        else:
            raw_text = read_text_safe(path)
            if len(raw_text) > 300_000:
                raw_text = raw_text[:300_000] + '\n\n[Preview truncado: archivo muy grande]'
            lines = raw_text.splitlines()
            if len(lines) > 2000:
                raw_text = '\n'.join(lines[:2000]) + '\n\n[Preview truncado: demasiadas líneas]'
            text = raw_text

        imports: list[tuple[str, str]] = []
        repo_root = Path(index_data.get('root', self.project_root))
        src = Path(abspath)
        for raw_imp in info.get('imports', []):
            resolved = resolve_import(repo_root, src, raw_imp) or ''
            imports.append((raw_imp, resolved))

        dependents = list(index_data.get('dependents', {}).get(relpath, []))
        return PreviewData(
            relpath=relpath,
            abspath=abspath,
            title=f"{relpath}   ({human_size(size)})",
            rendered_text=self._render_with_line_numbers(text),
            line=line,
            imports=imports,
            dependents=dependents,
        )

    def export_results(self, results: list[SearchResult], out_path: Path) -> None:
        if out_path.suffix.lower() == '.csv':
            with out_path.open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'display_path', 'modified', 'size_bytes', 'size_human', 'ext',
                    'relpath', 'abspath', 'line', 'matches', 'snippet',
                ])
                for r in results:
                    writer.writerow([
                        r.display_path, r.modified, r.size, human_size(r.size), r.ext,
                        r.relpath, r.abspath, r.line, r.matches, r.snippet,
                    ])
        elif out_path.suffix.lower() == '.json':
            payload = [asdict(r) for r in results]
            out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
        else:
            lines = [
                f"{r.display_path} | {r.modified} | {human_size(r.size)} | {r.ext} | line={r.line} | hits={r.matches}"
                for r in results
            ]
            out_path.write_text('\n'.join(lines), encoding='utf-8')

    @staticmethod
    def _is_probably_binary(path: Path) -> bool:
        try:
            with path.open('rb') as f:
                chunk = f.read(8192)
            return b'\x00' in chunk
        except Exception:
            return False

    @staticmethod
    def _build_file_fact_sheet(relpath: str, path: Path, size: int, reason: str) -> str:
        ext = path.suffix.lower() or '(sin extensión)'
        return '\n'.join([
            '[Preview no cargado]',
            f'Relpath: {relpath}',
            f'Ruta: {path}',
            f'Extensión: {ext}',
            f'Tamaño: {human_size(size)}',
            f'Motivo: {reason}',
            '',
            'Usa "Abrir con sistema" si quieres verlo completo.',
        ])

    @staticmethod
    def _render_with_line_numbers(text: str) -> str:
        lines = text.splitlines()
        if not lines:
            return '    1 | \n'
        width = max(4, len(str(len(lines))))
        return '\n'.join(f"{str(i).rjust(width)} | {line}" for i, line in enumerate(lines, start=1)) + '\n'
