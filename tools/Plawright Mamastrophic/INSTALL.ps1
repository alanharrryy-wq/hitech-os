param(
  [string]$Target = 'F:\repos\hitech-os\tools\Plawright Mamastrophic'
)

$ErrorActionPreference = 'Stop'
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$engine = @'
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
import zipfile
from pathlib import Path

PACKAGE_ROOT = Path(os.environ['PLAWSHOT_PACKAGE_ROOT'])
TARGET = Path(os.environ.get('PLAWSHOT_TARGET', r'F:\repos\hitech-os\tools\Plawright Mamastrophic'))

OUT = Path(r'F:\descargasf')
TRASH = Path(r'F:\Trash-old')
STAMP = dt.datetime.now().strftime('%d%m %H%M%S')
RUN_NAME = f'plawshot install {STAMP}'
RUN_DIR = OUT / RUN_NAME
REPORTS = RUN_DIR / 'reports'
LOGS = RUN_DIR / 'logs'
RESULT_ZIP = OUT / f'{RUN_NAME} result.zip'
FAIL_ZIP = OUT / f'{RUN_NAME} fail.zip'
STATE_PATH = OUT / 'plawshot_latest_rollback.json'
TOTAL = 14
STEP = 0

REQUIRED = [
    'RUN.ps1',
    'MENU.ps1',
    'mamenu.bat',
    'ROLLBACK.ps1',
    'core/run-surf8-capture.ps1',
    'core/surf8_discovery.py',
    'core/visualqa_aggregate.py',
    'core/deep_capture.py',
    'tests/surf8.deep-capture.cjs',
    'tests/surf8.all-surfaces.engine.cjs',
    'tests/surf8.all-surfaces.spec.cjs',
    'tests/surf8.visualqa.engine.cjs',
    'tests/surf8.visualqa.spec.cjs',
]

TEXT_NOTICE = 'Installer mode: in-place overlay. It does not rename, delete, or move the whole tool folder. This avoids WinError 32 when the folder is your current PowerShell location or held by another process.'

def looks_like_source(root: Path) -> bool:
    return all((root / rel).exists() for rel in ['RUN.ps1', 'MENU.ps1', 'core/run-surf8-capture.ps1', 'tests/surf8.deep-capture.cjs'])

def resolve_source(package_root: Path) -> Path:
    candidates = [package_root, package_root / 'Plawright Mamastrophic', package_root.parent / 'Plawright Mamastrophic']
    seen = set()
    for c in candidates:
        key = str(c.resolve()) if c.exists() else str(c)
        if key in seen:
            continue
        seen.add(key)
        if c.exists() and c.is_dir() and looks_like_source(c):
            return c
    nested = []
    try:
        nested = [x for x in package_root.iterdir() if x.is_dir()]
    except Exception:
        nested = []
    for c in nested:
        if looks_like_source(c):
            return c
    existing = []
    for c in candidates + nested:
        try:
            files = [x.name for x in c.iterdir()] if c.exists() and c.is_dir() else []
        except Exception as exc:
            files = [f'<error listing: {exc!r}>']
        existing.append({'candidate': str(c), 'exists': c.exists(), 'files': files})
    raise RuntimeError('No pude resolver carpeta fuente dentro del ZIP. Candidatos: ' + json.dumps(existing, ensure_ascii=False))

SOURCE = resolve_source(PACKAGE_ROOT)

def ensure_dirs():
    for p in [OUT, TRASH, RUN_DIR, REPORTS, LOGS]:
        p.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    ensure_dirs()
    line = f'[{dt.datetime.now().strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with (LOGS / 'install.log').open('a', encoding='utf-8') as f:
        f.write(line + '\n')

def progress(msg: str):
    global STEP
    STEP += 1
    pct = min(100, int(round(STEP / TOTAL * 100)))
    rem = 100 - pct
    filled = int(30 * pct / 100)
    bar = '█' * filled + '░' * (30 - filled)
    log(f'PROGRESS {pct:03d}% [{bar}] remaining {rem:03d}% :: {msg}')

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def manifest_dir(root: Path) -> list[dict]:
    rows = []
    if not root.exists():
        return rows
    for p in sorted(root.rglob('*')):
        if p.is_file():
            rel = str(p.relative_to(root)).replace('\\', '/')
            try:
                rows.append({'relative': rel, 'bytes': p.stat().st_size, 'sha256': sha256_file(p)})
            except Exception as exc:
                rows.append({'relative': rel, 'error': repr(exc)})
    return rows

def manifest_map(root: Path) -> dict[str, dict]:
    return {row['relative']: row for row in manifest_dir(root) if 'relative' in row}

def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def zip_dir(src: Path, dest: Path):
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob('*'):
            if p.is_file():
                z.write(p, p.relative_to(src.parent))

def run_cmd(cmd: list[str], cwd: Path | None = None) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, timeout=120)
        return {'cmd': cmd, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except Exception as exc:
        return {'cmd': cmd, 'returncode': 999, 'stdout': '', 'stderr': repr(exc)}

def validate_tree(root: Path) -> tuple[list[str], list[dict]]:
    errors: list[str] = []
    checks: list[dict] = []
    for rel in REQUIRED:
        if not (root / rel).exists():
            errors.append(f'missing required file: {rel}')
    py_files = [root / 'core' / 'surf8_discovery.py', root / 'core' / 'visualqa_aggregate.py', root / 'core' / 'deep_capture.py']
    for py in py_files:
        if py.exists():
            res = run_cmd([sys.executable, '-m', 'py_compile', str(py)], cwd=root)
            checks.append({'type': 'py_compile', 'file': str(py), **res})
            if res['returncode'] != 0:
                errors.append(f'py_compile failed: {py}')
    node = shutil.which('node')
    if node:
        for js in sorted((root / 'tests').glob('*.cjs')):
            res = run_cmd([node, '--check', str(js)], cwd=root)
            checks.append({'type': 'node_check', 'file': str(js), **res})
            if res['returncode'] != 0:
                errors.append(f'node --check failed: {js}')
    else:
        checks.append({'type': 'node_check', 'status': 'SKIPPED', 'reason': 'node not found in PATH during install validation'})
    return errors, checks

def same_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except Exception:
        return str(a).lower() == str(b).lower()

def copy_with_tmp(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + f'.plawtmp-{os.getpid()}')
    if tmp.exists():
        try:
            tmp.unlink()
        except Exception:
            pass
    shutil.copy2(src, tmp)
    os.replace(tmp, dest)

def move_to_unique(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    final = dest
    i = 1
    while final.exists():
        final = dest.with_name(dest.name + f'.{i}')
        i += 1
    shutil.move(str(src), str(final))
    return final

def cleanup_empty_dirs(root: Path):
    if not root.exists():
        return
    for p in sorted([x for x in root.rglob('*') if x.is_dir()], key=lambda x: len(str(x)), reverse=True):
        try:
            p.rmdir()
        except Exception:
            pass

def restore_after_failed_overlay(copied: list[dict], backup_root: Path, failed_new_root: Path, errors: list[str]):
    for row in reversed(copied):
        rel = row['relative']
        dest = TARGET / rel
        try:
            if row.get('existed'):
                backup_file = backup_root / rel
                if backup_file.exists():
                    copy_with_tmp(backup_file, dest)
            else:
                if dest.exists():
                    moved = move_to_unique(dest, failed_new_root / rel)
                    row['failedNewMovedTo'] = str(moved)
        except Exception as exc:
            errors.append(f'rollback restore failed for {rel}: {exc!r}')

def main() -> int:
    ensure_dirs()
    log(TEXT_NOTICE)
    progress('validando paquete fuente')
    if not SOURCE.exists():
        raise RuntimeError(f'No existe carpeta fuente dentro del ZIP: {SOURCE}')
    src_errors, src_checks = validate_tree(SOURCE)
    write_json(REPORTS / 'source_checks.json', src_checks)
    if src_errors:
        raise RuntimeError('Fuente invalida: ' + '; '.join(src_errors))

    if same_path(SOURCE, TARGET):
        progress('source y target son la misma carpeta, solo valido sin reemplazar')
        target_errors, target_checks = validate_tree(TARGET)
        write_json(REPORTS / 'target_checks.json', target_checks)
        if target_errors:
            raise RuntimeError('Target invalido: ' + '; '.join(target_errors))
        result = {'status': 'PASS', 'mode': 'validate-only-source-is-target', 'target': str(TARGET), 'source': str(SOURCE), 'resultZip': str(RESULT_ZIP), 'createdAt': dt.datetime.now().isoformat(timespec='seconds'), 'notes': ['INSTALL.ps1 was executed from the installed tool folder; no replacement was needed.']}
        write_json(REPORTS / 'install_result.json', result)
        zip_dir(RUN_DIR, RESULT_ZIP)
        print(f'INSTALL_OK_RESULT_ZIP: {RESULT_ZIP}')
        return 0

    progress('preparando backup overlay en Trash-old')
    trash_root = TRASH / f'plawshot install {STAMP}'
    backup_root = trash_root / 'backup_existing_files'
    stale_root = trash_root / 'stale_files_moved_from_target'
    failed_new_root = trash_root / 'failed_install_new_files'
    trash_root.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)
    stale_root.mkdir(parents=True, exist_ok=True)

    progress('leyendo manifiestos fuente y target')
    source_manifest = manifest_map(SOURCE)
    target_pre_manifest = manifest_map(TARGET)
    write_json(REPORTS / 'source_manifest.json', list(source_manifest.values()))
    write_json(REPORTS / 'target_pre_manifest.json', list(target_pre_manifest.values()))

    progress('planeando copia archivo por archivo')
    plan = []
    for rel, src_row in sorted(source_manifest.items()):
        dest_row = target_pre_manifest.get(rel)
        plan.append({'relative': rel, 'sourceBytes': src_row.get('bytes'), 'sourceSha256': src_row.get('sha256'), 'existed': dest_row is not None, 'oldSha256': dest_row.get('sha256') if dest_row else None, 'sameHash': bool(dest_row and dest_row.get('sha256') == src_row.get('sha256'))})
    stale_rels = sorted(set(target_pre_manifest) - set(source_manifest))
    write_json(REPORTS / 'install_plan.json', {'files': plan, 'staleFiles': stale_rels})

    copied: list[dict] = []
    stale_moved: list[dict] = []
    rollback_errors: list[str] = []

    try:
        progress('copiando archivos completos sin mover carpeta target')
        TARGET.mkdir(parents=True, exist_ok=True)
        total_files = max(1, len(plan))
        last_bucket = -1
        for idx, row in enumerate(plan, start=1):
            rel = row['relative']
            src = SOURCE / rel
            dest = TARGET / rel
            bucket = int(idx / total_files * 10)
            if bucket != last_bucket:
                last_bucket = bucket
                log(f'COPY {idx}/{total_files} :: {rel}')
            if row.get('sameHash'):
                row['action'] = 'skip-same-hash'
                continue
            if row.get('existed') and dest.exists():
                backup_file = backup_root / rel
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, backup_file)
                row['backupPath'] = str(backup_file)
            copy_with_tmp(src, dest)
            row['action'] = 'copied'
            copied.append(row)

        progress('moviendo archivos obsoletos a Trash-old sin borrar permanente')
        for rel in stale_rels:
            stale_src = TARGET / rel
            if not stale_src.exists():
                continue
            moved = move_to_unique(stale_src, stale_root / rel)
            stale_moved.append({'relative': rel, 'original': str(stale_src), 'movedTo': str(moved), 'oldSha256': target_pre_manifest.get(rel, {}).get('sha256')})
        cleanup_empty_dirs(TARGET)

        progress('validando target instalado')
        target_errors, target_checks = validate_tree(TARGET)
        write_json(REPORTS / 'target_checks.json', target_checks)
        if target_errors:
            raise RuntimeError('Target invalido: ' + '; '.join(target_errors))

        progress('escribiendo estado de rollback overlay')
        state = {'version': 'overlay-v1', 'status': 'READY', 'target': str(TARGET), 'source': str(SOURCE), 'backupRoot': str(backup_root), 'staleRoot': str(stale_root), 'trashRoot': str(trash_root), 'runDir': str(RUN_DIR), 'createdAt': dt.datetime.now().isoformat(timespec='seconds'), 'files': plan, 'staleFiles': stale_moved, 'rollbackCommand': r'powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\ROLLBACK.ps1"'}
        write_json(STATE_PATH, state)
        write_json(trash_root / 'manifest.json', state)
        write_text(trash_root / 'manifest.md', f'# plawshot overlay install backup\n\n- target: `{TARGET}`\n- backup root: `{backup_root}`\n- stale files: `{stale_root}`\n- reason: in-place overlay install, no full-folder move, no permanent delete\n- files in package: `{len(plan)}`\n- stale files moved: `{len(stale_moved)}`\n')

        progress('escribiendo reportes finales')
        target_manifest = manifest_dir(TARGET)
        result = {'status': 'PASS', 'installMode': 'in-place-overlay', 'target': str(TARGET), 'source': str(SOURCE), 'backupRoot': str(backup_root), 'staleRoot': str(stale_root), 'statePath': str(STATE_PATH), 'sourceFileCount': len(source_manifest), 'targetFileCount': len(target_manifest), 'copiedOrUpdatedCount': len(copied), 'sameHashSkippedCount': len([x for x in plan if x.get('action') == 'skip-same-hash']), 'staleMovedCount': len(stale_moved), 'resultZip': str(RESULT_ZIP), 'createdAt': dt.datetime.now().isoformat(timespec='seconds'), 'notes': ['No process was killed or restarted.', 'No full-folder rename/move was attempted, avoiding WinError 32 on the tool directory.', 'Installed full files, not patches/diffs.', 'Old replaced files were backed up individually.', 'Files not present in the package were moved to Trash-old, not permanently deleted.']}
        write_json(REPORTS / 'install_result.json', result)
        write_json(REPORTS / 'target_manifest.json', target_manifest)
        write_text(REPORTS / 'INSTALL_RESULT.md', f'# plawshot install result\n\n- status: PASS\n- install mode: in-place overlay\n- target: `{TARGET}`\n- backup root: `{backup_root}`\n- stale files moved to: `{stale_root}`\n- state file: `{STATE_PATH}`\n- result zip: `{RESULT_ZIP}`\n\n## Runtime policy\n\n- no start\n- no kill\n- no DB\n- no deploy\n- no permanent delete\n- no full-folder target move\n\n## Rollback\n\n```powershell\npowershell -NoProfile -ExecutionPolicy Bypass -File "F:\\repos\\hitech-os\\tools\\Plawright Mamastrophic\\ROLLBACK.ps1"\n```\n')

        progress('empaquetando result zip')
        zip_dir(RUN_DIR, RESULT_ZIP)
        print(f'INSTALL_OK_RESULT_ZIP: {RESULT_ZIP}')
        return 0
    except Exception:
        progress('fallo detectado, intentando rollback automatico de overlay')
        restore_after_failed_overlay(copied, backup_root, failed_new_root, rollback_errors)
        write_json(REPORTS / 'overlay_rollback_after_fail.json', {'copied': copied, 'errors': rollback_errors})
        if rollback_errors:
            raise RuntimeError('Install failed and automatic overlay rollback had errors: ' + '; '.join(rollback_errors))
        raise

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        ensure_dirs()
        err = {'status': 'FAIL', 'error': repr(exc), 'traceback': traceback.format_exc(), 'target': str(TARGET), 'source': str(SOURCE), 'installMode': 'in-place-overlay'}
        write_json(REPORTS / 'install_fail.json', err)
        log('FAIL ' + repr(exc))
        zip_dir(RUN_DIR, FAIL_ZIP)
        print(f'INSTALL_FAIL_ZIP: {FAIL_ZIP}')
        raise
'@

$env:PLAWSHOT_PACKAGE_ROOT = $PackageRoot
$env:PLAWSHOT_TARGET = $Target
$tmp = Join-Path $env:TEMP ('plawshot_install_' + [Guid]::NewGuid().ToString('N') + '.py')
Set-Content -LiteralPath $tmp -Encoding UTF8 -Value $engine
try {
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { & $py.Source -3 $tmp }
  else { & (Get-Command python -ErrorAction Stop).Source $tmp }
  exit $LASTEXITCODE
} finally {
  Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}
