#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, zipfile
from datetime import datetime
from pathlib import Path
PACKAGE_ID="PRISMA_TABLET_RUNTIME_GATES_BASE_01_20260504_v01"; ZIP_NAME="PRISMA_TABLET_RUNTIME_GATES_BASE_01_20260504_v01.zip"; SLUG="runtime_gates_base_01"
TARGET_DEFAULT=r"F:\repos\hitech-os\apps\terminal-de-venta-system"; LOG_DEFAULT=r"F:\descargasf"
def hfile(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1048576),b''): h.update(c)
 return h.hexdigest()
def hbytes(b): return hashlib.sha256(b).hexdigest()
def relsafe(s):
 if not s or ':' in s or s.startswith('/') or s.startswith('\\'): raise SystemExit(4)
 p=Path(s.replace('\\','/'))
 if any(x in ('..','') for x in p.parts): raise SystemExit(4)
 return p
def log(msg, lines): print(msg); lines.append(str(msg))
def read_pkg(zip_path):
 with zipfile.ZipFile(zip_path) as z:
  man=json.loads(z.read('automation/manifest.json').decode('utf-8'))
  sums={}
  for line in z.read('automation/checksums.sha256').decode('utf-8').splitlines():
   if not line.strip() or line.startswith('#'): continue
   d,n=line.split('  ',1); sums[n]=d
  for n,d in sums.items():
   if n=='automation/checksums.sha256': continue
   if hbytes(z.read(n))!=d: raise SystemExit(3)
 return man,sums
def plan(man,target):
 allowed=(target/'products/tablet/app').resolve(strict=False); out=[]
 for f in man['files']:
  src=str(relsafe(f['source'])).replace('\','/')
  tr=relsafe(f['target']); dest=(target/tr).resolve(strict=False)
  if os.path.commonpath([str(allowed),str(dest)])!=str(allowed): raise SystemExit(4)
  out.append((src,tr,dest))
 return out
def verify(pl,sums,lines):
 ok=True
 for src,tr,dest in pl:
  if not dest.exists(): log(f'FAIL missing {tr}',lines); ok=False; continue
  actual=hfile(dest); exp=sums.get(src)
  if exp and exp!=actual: log(f'FAIL hash {tr}',lines); ok=False
  else: log(f'OK {tr} {actual}',lines)
 return ok
def backup(pl,target,lines):
 stamp=datetime.now().strftime('%Y%m%d_%H%M%S'); root=target/'.prisma_backups'/PACKAGE_ID/stamp; state=[]
 for src,tr,dest in pl:
  bp=root/'files'/tr
  if dest.exists(): bp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dest,bp); existed=True
  else: existed=False
  state.append({'target':str(tr).replace('\','/'),'backup':str(bp.relative_to(root)).replace('\','/'),'existed':existed}); log(f'backup {tr} existed={existed}',lines)
 root.mkdir(parents=True,exist_ok=True); (root/'rollback_state.json').write_text(json.dumps({'files':state},indent=2),encoding='utf-8')
 last=target/'.prisma_backups'/PACKAGE_ID/'last_rollback_state.json'; last.parent.mkdir(parents=True,exist_ok=True); last.write_text(json.dumps({'state':str(root/'rollback_state.json')}),encoding='utf-8')
def rollback(target,lines):
 marker=target/'.prisma_backups'/PACKAGE_ID/'last_rollback_state.json'
 if not marker.exists(): raise SystemExit(5)
 state_path=Path(json.loads(marker.read_text(encoding='utf-8'))['state']); st=json.loads(state_path.read_text(encoding='utf-8')); root=state_path.parent
 for f in reversed(st['files']):
  dest=target/relsafe(f['target'])
  if f['existed']:
   bp=root/relsafe(f['backup']); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(bp,dest); log(f'restored {f["target"]}',lines)
  elif dest.exists(): dest.unlink(); log(f'removed {f["target"]}',lines)
def main():
 ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True)
 for m in ['dry-run','apply','verify','rollback']: g.add_argument('--'+m, action='store_true')
 ap.add_argument('--zip-path',default=''); ap.add_argument('--target-root',default=TARGET_DEFAULT); ap.add_argument('--log-root',default=LOG_DEFAULT); ap.add_argument('--run-commands',action='store_true'); args=ap.parse_args()
 mode='dry-run' if args.dry_run else 'apply' if args.apply else 'verify' if args.verify else 'rollback'
 lines=[f'package={PACKAGE_ID}',f'mode={mode}',f'started={datetime.now().isoformat()}']
 try:
  target=Path(args.target_root).resolve(strict=False); zp=Path(args.zip_path or (Path(__file__).parent/ZIP_NAME)).resolve(strict=False)
  log(f'targetRoot={target}',lines)
  if args.rollback: rollback(target,lines); code=0
  else:
   man,sums=read_pkg(zp); pl=plan(man,target); log(f'plannedFiles={len(pl)}',lines)
   for src,tr,dest in pl: log(f'plan {src} -> {tr}',lines)
   if args.dry_run: code=0
   elif args.apply:
    backup(pl,target,lines)
    with zipfile.ZipFile(zp) as z:
     for src,tr,dest in pl: dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(z.read(src)); log(f'installed {tr}',lines)
    code=0 if verify(pl,sums,lines) else 2
   else: code=0 if verify(pl,sums,lines) else 2
   if code==0 and args.run_commands:
    for c in man.get('verifyCommands',[]):
     log('command> '+c,lines); r=subprocess.run(c,cwd=target,shell=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); log(r.stdout[-4000:],lines); code=max(code,r.returncode)
 except SystemExit as e: code=int(e.code)
 except Exception as e: log('ERROR '+repr(e),lines); code=2
 Path(args.log_root).mkdir(parents=True,exist_ok=True); log_path=Path(args.log_root)/f'prisma_tablet_{SLUG}_int_{datetime.now().strftime("%y%m%d_%H%M%S")}.log'; log_path.write_text('
'.join(lines)+'
',encoding='utf-8'); print('log='+str(log_path)); sys.exit(code)
if __name__=='__main__': main()
