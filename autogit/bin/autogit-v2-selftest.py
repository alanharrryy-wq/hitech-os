from __future__ import annotations

import json
import py_compile
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
engine = root / 'engine'
files = [
    engine / 'autogit_engine' / 'flight_cli.py',
    engine / 'autogit_engine' / 'cli.py',
    engine / 'autogit_engine' / 'ag100_learning.py',
    engine / 'autogit_engine' / 'ag98_selfheal.py',
]

for f in files:
    if not f.exists():
        raise SystemExit(f'MISSING: {f}')
    py_compile.compile(str(f), doraise=True)

flight = (engine / 'autogit_engine' / 'flight_cli.py').read_text(encoding='utf-8', errors='replace')

blocked_patterns = [
    'ParseFile($args[0]',
    '"-Command",ps,str(p)',
    "'-Command',ps,str(p)",
    '-Command", ps, str(p)',
    "-Command', ps, str(p)",
    'json.loads(text_or_empty(p))',
    '--delete-branch',
]

for pattern in blocked_patterns:
    if pattern in flight:
        raise SystemExit(f'LEGACY_UNSAFE_PATTERN: {pattern}')

required_patterns = [
    'def write_ps_parse_tool',
    '-LiteralTargetPath',
    'parse_one.ps1',
    'powershell.exe',
    '-File',
    'AG100_SELF_HEAL_CACHED_CHECK_V1',
    'AG100_FAIL_ZIP_CONTEXT_V1',
    'AG100_LARGE_JSON_VALIDATION_V1',
    'AG100_POST_RUN_HYGIENE_V1',
]

for pattern in required_patterns:
    if pattern not in flight:
        raise SystemExit(f'MISSING_REQUIRED_PATTERN: {pattern}')

sys.path.insert(0, str(engine))
from autogit_engine.ag100_learning import json_text_for_validation, clean_text_file

with tempfile.TemporaryDirectory() as td:
    root_tmp = Path(td)

    big = root_tmp / 'big.json'
    big.write_text(json.dumps({'kind': 'BIG_JSON_TEST', 'payload': 'x' * (2 * 1024 * 1024 + 100)}), encoding='utf-8')
    parsed = json.loads(json_text_for_validation(big, max_text_bytes=128))
    assert parsed['kind'] == 'BIG_JSON_TEST'

    dirty = root_tmp / 'dirty.md'
    dirty.write_text('uno   \n\n\n', encoding='utf-8')
    result = clean_text_file(dirty)
    assert result['changed'] is True
    assert dirty.read_text(encoding='utf-8') == 'uno\n'

print('AUTOGIT V2 SELFTEST OK')
print('AUTOGIT V2 SAFE_PS_PARSE OK')
print('AUTOGIT AG100 LARGE_JSON OK')
print('AUTOGIT AG100 TEXT_SELF_HEAL OK')
