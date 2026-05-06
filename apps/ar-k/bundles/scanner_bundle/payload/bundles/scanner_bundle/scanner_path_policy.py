from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

EXCLUDED_SEGMENTS = {
    'reports', 'reports_real', '.ark_install', '__pycache__', '.pytest_cache', '.mypy_cache',
    '.venv', 'node_modules', 'dist', 'build', 'tmp', 'temp', 'runtime', 'generated'
}
OBSERVED_ONLY_TOP_LEVEL = {
    'docs': 'docs',
    'tests': 'tests',
    'tools': 'tooling',
    'scripts': 'scripts',
    'fixtures': 'fixtures',
    'examples': 'examples',
}

@dataclass(frozen=True)
class PathPolicy:
    action: str
    reason: str
    canonical_source: bool
    non_product_class: str | None


def classify_path_policy(relative_path: str) -> PathPolicy:
    parts = [p for p in PurePosixPath(relative_path).parts if p not in {'', '.'}]
    lowers = [p.lower() for p in parts]
    for part in lowers:
        if part in EXCLUDED_SEGMENTS:
            return PathPolicy('exclude', f'excluded_segment:{part}', False, 'excluded')
    if lowers and lowers[0].startswith('.'):
        return PathPolicy('observe_only', 'hidden_root', False, 'hidden')
    if lowers and lowers[0] in OBSERVED_ONLY_TOP_LEVEL:
        return PathPolicy('observe_only', f'non_product_top_level:{lowers[0]}', False, OBSERVED_ONLY_TOP_LEVEL[lowers[0]])
    filename = lowers[-1] if lowers else ''
    if '.spec.' in filename or '.test.' in filename or filename.endswith(('_spec.py', '_test.py')):
        return PathPolicy('observe_only', 'test_file', False, 'tests')
    return PathPolicy('canonical', 'scanner_readable_source', True, None)
