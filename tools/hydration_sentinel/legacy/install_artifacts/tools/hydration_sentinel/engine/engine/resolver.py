from __future__ import annotations

from pathlib import Path

MODULE_SUFFIXES = (
    '',
    '.ts',
    '.tsx',
    '.js',
    '.jsx',
    '.mjs',
    '.cjs',
    '/index.ts',
    '/index.tsx',
    '/index.js',
    '/index.jsx',
    '/index.mjs',
    '/index.cjs',
)


class ImportResolver:
    def __init__(self, repo_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()

    @staticmethod
    def normalize_relpath(path: str | Path) -> str:
        return str(path).replace('\\', '/').lstrip('./')

    def resolve(self, current_relpath: str, specifier: str) -> str | None:
        if not specifier.startswith('.'):
            return None
        current_abs = (self.repo_root / current_relpath).resolve()
        base_dir = current_abs.parent
        for suffix in MODULE_SUFFIXES:
            candidate = (base_dir / f'{specifier}{suffix}').resolve()
            if candidate.exists() and candidate.is_file():
                return self.normalize_relpath(candidate.relative_to(self.repo_root))
        return None
