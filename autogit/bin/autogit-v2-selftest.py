from __future__ import annotations

import py_compile
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = [
    root / 'engine' / 'autogit_engine' / 'flight_cli.py',
    root / 'engine' / 'autogit_engine' / 'cli.py',
]

for f in files:
    if not f.exists():
        raise SystemExit(f'MISSING: {f}')
    py_compile.compile(str(f), doraise=True)

flight = (root / 'engine' / 'autogit_engine' / 'flight_cli.py').read_text(encoding='utf-8', errors='replace')

blocked_patterns = [
    'ParseFile($args[0]',
    '"-Command",ps,str(p)',
    "'-Command',ps,str(p)",
    '-Command", ps, str(p)',
    "-Command', ps, str(p)",
]

for pattern in blocked_patterns:
    if pattern in flight:
        raise SystemExit(f'LEGACY_UNSAFE_PS_PARSE_PATTERN: {pattern}')

required_patterns = [
    'def write_ps_parse_tool',
    '-LiteralTargetPath',
    'parse_one.ps1',
    'powershell.exe',
    '-File',
]

for pattern in required_patterns:
    if pattern not in flight:
        raise SystemExit(f'MISSING_SAFE_PS_PARSE_PATTERN: {pattern}')

print('AUTOGIT V2 SELFTEST OK')
print('AUTOGIT V2 SAFE_PS_PARSE OK')
