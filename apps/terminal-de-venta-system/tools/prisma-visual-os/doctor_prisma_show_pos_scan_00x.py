from pathlib import Path
import runpy
import sys

_TARGET = Path(__file__).resolve().parent / 'doctors' / 'doctor_prisma_show_pos_scan_00x.py'
if not _TARGET.exists():
    raise SystemExit(f'PRISMA 00ZD shim target missing: {_TARGET}')
sys.argv[0] = str(_TARGET)
runpy.run_path(str(_TARGET), run_name='__main__')
