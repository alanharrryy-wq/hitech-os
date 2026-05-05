#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
PACKAGE_ID="PRISMA_APP_MOBILE_34_DAILY_BRIEF_LEDGER_TIMELINE_FINAL_20260504_v01"
ZIP_FILE_NAME="PRISMA_APP_MOBILE_34_DAILY_BRIEF_LEDGER_TIMELINE_FINAL_20260504_v01.zip"
LOG_SLUG="34_daily_brief_ledger_timeline_final"
DEFAULT_TARGET_ROOT=r"F:\repos\hitech-os\apps\terminal-de-venta-system"
DEFAULT_LOG_ROOT=r"F:\descargasf"
ALLOWED_PREFIXES=("products/mobile/app/","products/mobile/android/")
def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def safe(path:str)->str:
    p=PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts: raise ValueError(f'unsafe path {path}')
    s=p.as_posix()
    if not s.startswith(ALLOWED_PREFIXES): raise ValueError(f'target outside mobile scope: {s}')
    return s
def log(args,msg):
    args.log_root.mkdir(parents=True,exist_ok=True)
    with args.log_file.open('a',encoding='utf-8',newline='\n') as f: f.write(msg.rstrip()+'\n')
def load(args):
    if not args.zip_path.exists(): raise FileNotFoundError(args.zip_path)
    z=zipfile.ZipFile(args.zip_path)
    m=json.loads(z.read('automation/manifest.json'))
    if m.get('package_id')!=PACKAGE_ID: raise RuntimeError(f'package mismatch {m.get("package_id")}')
    for e in m['files']:
        got=sha(z.read(e['payload_path'])); exp=m['checksums'][e['payload_path']]
        if got!=exp: raise RuntimeError(f'checksum mismatch {e["payload_path"]}')
        safe(e['target'])
    return z,m
def dry(args):
    z,m=load(args)
    try:
        print('DRY-RUN',PACKAGE_ID); log(args,'[DRY-RUN] '+PACKAGE_ID)
        for e in m['files']:
            t=args.target_root/safe(e['target']); print(('overwrite' if t.exists() else 'create'),t)
        return 0
    finally: z.close()
def verify(args):
    z,m=load(args)
    try:
        bad=[]
        for e in m['files']:
            rel=safe(e['target']); t=args.target_root/rel
            if not t.exists(): bad.append('missing '+rel); continue
            if sha(t.read_bytes())!=m['checksums'][e['payload_path']]: bad.append('checksum drift '+rel)
        if bad:
            [print('FAIL',x) for x in bad]; [log(args,'[VERIFY:FAIL] '+x) for x in bad]; return 2
        print('VERIFY OK',PACKAGE_ID); log(args,'[VERIFY:OK] '+PACKAGE_ID); return 0
    finally: z.close()
def latest_backup(root):
    b=root/'.prisma_backups'/PACKAGE_ID
    if not b.exists(): return None
    ds=sorted([p for p in b.iterdir() if p.is_dir()])
    return ds[-1] if ds else None
def rollback(args):
    b=latest_backup(args.target_root)
    if not b: print('No backup found',PACKAGE_ID); return 3
    state=json.loads((b/'backup_manifest.json').read_text(encoding='utf-8'))
    for item in reversed(state['files']):
        rel=safe(item['target']); t=args.target_root/rel
        if item['existed']:
            src=b/'files'/rel; t.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,t); log(args,'[ROLLBACK] restored '+str(t))
        elif t.exists(): t.unlink(); log(args,'[ROLLBACK] removed '+str(t))
    print('ROLLBACK OK',PACKAGE_ID); return 0
def apply(args):
    z,m=load(args)
    try:
        b=args.target_root/'.prisma_backups'/PACKAGE_ID/datetime.now().strftime('%Y%m%d_%H%M%S'); (b/'files').mkdir(parents=True,exist_ok=True)
        state={'package_id':PACKAGE_ID,'files':[]}
        for e in m['files']:
            rel=safe(e['target']); t=args.target_root/rel; existed=t.exists(); state['files'].append({'target':rel,'existed':existed})
            if existed:
                dst=b/'files'/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(t,dst)
        (b/'backup_manifest.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        for e in m['files']:
            rel=safe(e['target']); t=args.target_root/rel; t.parent.mkdir(parents=True,exist_ok=True); t.write_bytes(z.read(e['payload_path'])); log(args,'[APPLY] wrote '+str(t))
        code=verify(args)
        if code: log(args,'[APPLY] verify failed, rollback'); rollback(args); return code
        print('APPLY OK',PACKAGE_ID); return 0
    except Exception as exc:
        log(args,'[APPLY:ERROR] '+str(exc)); rollback(args); raise
    finally: z.close()
def parse(argv=None):
    p=argparse.ArgumentParser(description='Install '+PACKAGE_ID)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run',action='store_true'); g.add_argument('--apply',action='store_true'); g.add_argument('--verify',action='store_true'); g.add_argument('--rollback',action='store_true')
    p.add_argument('--target-root',default=DEFAULT_TARGET_ROOT); p.add_argument('--zip-path'); p.add_argument('--log-root',default=DEFAULT_LOG_ROOT)
    a=p.parse_args(argv); here=Path(__file__).resolve().parent; a.zip_path=Path(a.zip_path) if a.zip_path else here/ZIP_FILE_NAME; a.target_root=Path(a.target_root); a.log_root=Path(a.log_root); a.log_file=a.log_root/f'prisma_app_mobile_{LOG_SLUG}_int_{datetime.now().strftime("%y%m%d_%H%M")}.log'; return a
def main(argv=None):
    a=parse(argv)
    try:
        if a.dry_run: return dry(a)
        if a.apply: return apply(a)
        if a.verify: return verify(a)
        if a.rollback: return rollback(a)
        return 2
    except Exception as e:
        print('ERROR',e,file=sys.stderr)
        try: log(a,'[ERROR] '+str(e))
        except Exception: pass
        return 1
if __name__=='__main__': raise SystemExit(main())
