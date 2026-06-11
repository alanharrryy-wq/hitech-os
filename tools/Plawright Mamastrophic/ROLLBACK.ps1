param(
  [string]$StatePath = 'F:\descargasf\plawshot_latest_rollback.json'
)

$ErrorActionPreference = 'Stop'

$engine = @'
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import traceback
import zipfile
from pathlib import Path

STATE_PATH = Path(os.environ.get('PLAWSHOT_STATE_PATH', r'F:\descargasf\plawshot_latest_rollback.json'))
OUT = Path(r'F:\descargasf')
TRASH = Path(r'F:\Trash-old')
STAMP = dt.datetime.now().strftime('%d%m %H%M%S')
RUN_NAME = f'plawshot rollback {STAMP}'
RUN_DIR = OUT / RUN_NAME
REPORTS = RUN_DIR / 'reports'
LOGS = RUN_DIR / 'logs'
RESULT_ZIP = OUT / f'{RUN_NAME} result.zip'
FAIL_ZIP = OUT / f'{RUN_NAME} fail.zip'
TOTAL = 9
STEP = 0

def ensure_dirs():
    for p in [OUT, TRASH, RUN_DIR, REPORTS, LOGS]:
        p.mkdir(parents=True, exist_ok=True)

def log(msg: str):
    ensure_dirs()
    line = f'[{dt.datetime.now().strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with (LOGS / 'rollback.log').open('a', encoding='utf-8') as f:
        f.write(line + '\n')

def progress(msg: str):
    global STEP
    STEP += 1
    pct = min(100, int(round(STEP / TOTAL * 100)))
    rem = 100 - pct
    filled = int(28 * pct / 100)
    bar = '█' * filled + '░' * (28 - filled)
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

def copy_with_tmp(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + f'.plawrbtmp-{os.getpid()}')
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

def rollback_overlay(state: dict) -> dict:
    target = Path(state['target'])
    backup_root = Path(state['backupRoot'])
    stale_files = state.get('staleFiles', [])
    files = state.get('files', [])
    current_new_root = TRASH / f'plawshot rollback current-new {STAMP}'
    displaced_root = TRASH / f'plawshot rollback displaced {STAMP}'
    restored_existing = []
    moved_new = []
    restored_stale = []
    errors = []

    progress('moviendo archivos nuevos del paquete a Trash-old')
    for row in reversed(files):
        rel = row.get('relative')
        if not rel:
            continue
        dest = target / rel
        try:
            if row.get('existed'):
                continue
            if dest.exists():
                moved = move_to_unique(dest, current_new_root / rel)
                moved_new.append({'relative': rel, 'movedTo': str(moved)})
        except Exception as exc:
            errors.append(f'move new file failed {rel}: {exc!r}')

    progress('restaurando archivos existentes desde backup individual')
    for row in reversed(files):
        rel = row.get('relative')
        if not rel or not row.get('existed'):
            continue
        backup = backup_root / rel
        dest = target / rel
        try:
            if backup.exists():
                copy_with_tmp(backup, dest)
                restored_existing.append({'relative': rel, 'backup': str(backup)})
        except Exception as exc:
            errors.append(f'restore existing failed {rel}: {exc!r}')

    progress('restaurando archivos obsoletos movidos durante install')
    for row in stale_files:
        rel = row.get('relative')
        moved_from = Path(row.get('movedTo', ''))
        dest = target / rel if rel else None
        try:
            if not rel or not dest or not moved_from.exists():
                continue
            if dest.exists():
                displaced = move_to_unique(dest, displaced_root / rel)
                row['displacedCurrentTo'] = str(displaced)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(moved_from), str(dest))
            restored_stale.append({'relative': rel, 'restoredTo': str(dest)})
        except Exception as exc:
            errors.append(f'restore stale failed {rel}: {exc!r}')

    progress('limpiando carpetas vacias')
    cleanup_empty_dirs(target)

    return {
        'target': str(target),
        'restoredExistingCount': len(restored_existing),
        'movedNewCount': len(moved_new),
        'restoredStaleCount': len(restored_stale),
        'currentNewRoot': str(current_new_root),
        'displacedRoot': str(displaced_root),
        'restoredExisting': restored_existing,
        'movedNew': moved_new,
        'restoredStale': restored_stale,
        'errors': errors,
    }

def rollback_legacy_folder_move(state: dict) -> dict:
    target = Path(state['target'])
    backup = Path(state['backup'])
    if not backup.exists():
        raise RuntimeError(f'No existe backup para restaurar: {backup}')
    current_trash = TRASH / f'plawshot rollback current {STAMP}' / target.name
    if target.exists():
        move_to_unique(target, current_trash)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(backup, target)
    return {'target': str(target), 'backupRestoredFrom': str(backup), 'currentMovedTo': str(current_trash)}

def main() -> int:
    ensure_dirs()
    progress('leyendo estado de rollback')
    if not STATE_PATH.exists():
        raise RuntimeError(f'No existe state file: {STATE_PATH}')
    state = json.loads(STATE_PATH.read_text(encoding='utf-8', errors='replace'))
    write_json(REPORTS / 'rollback_state_used.json', state)

    version = state.get('version', 'legacy-folder-move')
    if version == 'overlay-v1':
        progress('rollback overlay sin mover carpeta target completa')
        details = rollback_overlay(state)
        if details.get('errors'):
            raise RuntimeError('Rollback overlay tuvo errores: ' + '; '.join(details['errors']))
    else:
        progress('rollback legacy por carpeta completa')
        details = rollback_legacy_folder_move(state)

    progress('validando restauracion minima')
    target = Path(details['target'])
    required = ['RUN.ps1', 'MENU.ps1', 'core/run-surf8-capture.ps1']
    missing = [x for x in required if not (target / x).exists()]
    if missing:
        raise RuntimeError('Restauracion incompleta, faltan: ' + ', '.join(missing))

    progress('escribiendo manifiestos')
    payload = {
        'status': 'PASS',
        'statePath': str(STATE_PATH),
        'version': version,
        'details': details,
        'targetFileCount': len(manifest_dir(target)),
        'createdAt': dt.datetime.now().isoformat(timespec='seconds'),
    }
    write_json(REPORTS / 'rollback_result.json', payload)
    write_text(REPORTS / 'ROLLBACK_RESULT.md', f'# plawshot rollback result\n\n- status: PASS\n- mode: `{version}`\n- target: `{target}`\n- result zip: `{RESULT_ZIP}`\n')

    progress('empaquetando result zip')
    zip_dir(RUN_DIR, RESULT_ZIP)
    print(f'ROLLBACK_OK_RESULT_ZIP: {RESULT_ZIP}')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        ensure_dirs()
        err = {'status': 'FAIL', 'error': repr(exc), 'traceback': traceback.format_exc(), 'statePath': str(STATE_PATH)}
        write_json(REPORTS / 'rollback_fail.json', err)
        log('FAIL ' + repr(exc))
        zip_dir(RUN_DIR, FAIL_ZIP)
        print(f'ROLLBACK_FAIL_ZIP: {FAIL_ZIP}')
        raise
'@

$env:PLAWSHOT_STATE_PATH = $StatePath
$tmp = Join-Path $env:TEMP ('plawshot_rollback_' + [Guid]::NewGuid().ToString('N') + '.py')
Set-Content -LiteralPath $tmp -Encoding UTF8 -Value $engine
try {
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { & $py.Source -3 $tmp }
  else { & (Get-Command python -ErrorAction Stop).Source $tmp }
  exit $LASTEXITCODE
} finally {
  Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}
