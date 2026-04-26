from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

TEXT_EXTS = {".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".d.ts"}
RE_IMPORT = re.compile(r"(?:import|export)\s+(?:[^\"']+?\s+from\s+)?[\"']([^\"']+)[\"']")
RE_DYNAMIC = re.compile(r"import\([\"']([^\"']+)[\"']\)")
ALIASES = {
    "@/": "src/",
    "@components/": "components/",
    "@shared-kernel/": "../../../shared/twin-kernel/src/"
}
CHECK_FILES = [
    'package.json',
    'tsconfig.json',
    'tsconfig.base.json',
    'app/layout.tsx',
    'app/page.tsx',
    'src/lib/utils.ts',
    'src/lib/core/types.ts',
    'src/composition/module-registry.ts',
    '../../../shared/twin-kernel/src/types/module.ts',
    'prisma/schema.prisma',
]


def candidate_paths(base: Path) -> list[Path]:
    return [
        base,
        Path(str(base) + '.ts'),
        Path(str(base) + '.tsx'),
        Path(str(base) + '.js'),
        Path(str(base) + '.mjs'),
        Path(str(base) + '.d.ts'),
        base.with_suffix('.ts') if base.suffix else base,
        base.with_suffix('.tsx') if base.suffix else base,
        base / 'index.ts',
        base / 'index.tsx',
    ]


def existing_target(spec: str, current: Path) -> bool:
    if spec.startswith("./.next/"):
        return True
    candidates: list[Path] = []
    if spec.startswith('./') or spec.startswith('../'):
        base = (current.parent / spec).resolve()
        candidates.extend(candidate_paths(base))
    else:
        for prefix, mapped in ALIASES.items():
            if spec.startswith(prefix):
                base = (ROOT / mapped / spec[len(prefix):]).resolve()
                candidates.extend(candidate_paths(base))
                break
        else:
            return True
    return any(candidate.exists() for candidate in candidates)

errors = []

for rel in CHECK_FILES:
    if not (ROOT / rel).exists():
        errors.append(f'Missing required file: {rel}')

for json_rel in ['package.json', 'tsconfig.json', 'tsconfig.base.json']:
    try:
        json.loads((ROOT / json_rel).read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'Invalid JSON {json_rel}: {exc}')

SKIP_DIRS = {'node_modules', '.next', '.cache'}

for path in ROOT.rglob('*'):
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if path.suffix not in TEXT_EXTS or not path.is_file():
        continue
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'External Interaction Template' in text:
        errors.append(f'Legacy naming found in {path.relative_to(ROOT)}')
    for match in list(RE_IMPORT.finditer(text)) + list(RE_DYNAMIC.finditer(text)):
        spec = match.group(1)
        if not existing_target(spec, path):
            errors.append(f'Unresolved import in {path.relative_to(ROOT)} -> {spec}')

if errors:
    print('PACKAGE VALIDATION FAILED')
    for error in errors:
        print('-', error)
    raise SystemExit(1)

print('PACKAGE VALIDATION OK')
