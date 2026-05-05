#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, tempfile, zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
PACKAGE_ID='PRISMA_PC_CATALOG_SKU_BARCODE_02'; VERSION='20260504_v01'; PREFIX='apps/terminal-de-venta-system/products/pc/app/'
DEFAULT_TARGET_ROOT=r"F:\repos\hitech-os"; DEFAULT_LOG_DIR=r"F:\descargasf"
def stamp(): return datetime.now().strftime('%y%m%d_%H%M')
def ts(): return datetime.now().isoformat(timespec='seconds')
def norm(x):
 s=str(x).replace('\\','/').strip().lstrip('/'); parts=PurePosixPath(s).parts
 if any(p=='..' for p in parts): raise ValueError('ruta insegura '+str(x))
 return '/'.join(parts)
def targ(root,rel):
 r=norm(rel)
 if not r.startswith(PREFIX): raise ValueError('target fuera PC '+r)
 return Path(root).resolve()/Path(*PurePosixPath(r).parts)
def sha(p):
 d=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): d.update(b)
 return d.hexdigest()
def log(lp,msg): lp.parent.mkdir(parents=True,exist_ok=True); lp.open('a',encoding='utf-8').write('['+ts()+'] '+msg+'\n')
def root_here():
 here=Path(__file__).resolve()
 if (here.parent/'manifest.json').exists(): return here.parent.parent
 if (here.parent/'automation'/'manifest.json').exists(): return here.parent
 return None
def load(args):
 root=root_here(); tmp=None
 if root is None:
  zp=Path(args.zip_path).resolve() if args.zip_path else Path(__file__).with_name(PACKAGE_ID+'_'+VERSION+'.zip')
  if not zp.exists(): raise FileNotFoundError('ZIP no existe '+str(zp))
  tmp=Path(tempfile.mkdtemp(prefix=PACKAGE_ID+'_'))
  with zipfile.ZipFile(zp) as z: z.extractall(tmp)
  ds=[p for p in tmp.iterdir() if p.is_dir()]; root=ds[0] if len(ds)==1 else tmp
 man=json.loads((root/'automation'/'manifest.json').read_text(encoding='utf-8'))
 sums={}
 for line in (root/'automation'/'checksums.sha256').read_text(encoding='utf-8').splitlines():
  if line.strip():
   d,rel=line.split(None,1); sums[norm(rel)]=d.lower()
 return root,man,sums
def pay(root,rel):
 p=root/Path(*PurePosixPath(norm(rel)).parts)
 if not p.exists(): raise FileNotFoundError('payload no existe '+norm(rel))
 return p
def validate(root,man,sums):
 err=[]
 if man.get('package_id')!=PACKAGE_ID: err.append('package_id incorrecto')
 if man.get('version')!=VERSION: err.append('version incorrecta')
 if man.get('app')!='pc': err.append('app debe ser pc')
 if man.get('writes_outside_pc_app'): err.append('write outside bloqueado')
 for c in man.get('changes',[]):
  src=norm(c['source']); dst=norm(c['target'])
  if not src.startswith('payload/'): err.append('source fuera payload '+src)
  if not dst.startswith(PREFIX): err.append('target fuera PC '+dst)
  if src not in sums: err.append('falta checksum '+src)
  try:
   if sha(pay(root,src))!=sums.get(src): err.append('checksum invalido '+src)
  except Exception as e: err.append(str(e))
 return err
def bdir(root): return Path(root).resolve()/'apps'/'terminal-de-venta-system'/'.prisma_backups'/PACKAGE_ID
def state(root):
 base=bdir(root)
 if not base.exists(): return None
 xs=sorted(base.glob('*/rollback_state.json'), key=lambda p:p.stat().st_mtime, reverse=True)
 return xs[0] if xs else None
def dry(args,root,man,sums,lp):
 log(lp,'[START] dry-run'); err=validate(root,man,sums)
 for e in err: log(lp,'ERROR '+e)
 if err: return 10
 for c in man['changes']: log(lp,('REPLACE ' if targ(args.target_root,c['target']).exists() else 'CREATE ')+c['target'])
 log(lp,'[END] dry-run ok'); return 0
def verify(args,root,man,sums,lp):
 log(lp,'[START] verify'); err=validate(root,man,sums); ok=not err
 for e in err: log(lp,'ERROR '+e)
 for c in man.get('changes',[]):
  dst=targ(args.target_root,c['target']); src=pay(root,c['source'])
  if not dst.exists() or sha(dst)!=sha(src): log(lp,'VERIFY FAIL '+str(dst)); ok=False
  else: log(lp,'VERIFY OK '+str(dst))
 log(lp,'[END] verify '+('ok' if ok else 'failed')); return 0 if ok else 10
def apply(args,root,man,sums,lp):
 log(lp,'[START] apply'); err=validate(root,man,sums)
 for e in err: log(lp,'ERROR '+e)
 if err: return 10
 backup=bdir(args.target_root)/stamp(); files=backup/'files'; files.mkdir(parents=True,exist_ok=True); st=[]
 for c in man['changes']:
  dst=targ(args.target_root,c['target']); src=pay(root,c['source']); item={'target':norm(c['target']),'existed':dst.exists()}
  if dst.exists():
   bp=files/Path(*PurePosixPath(norm(c['target'])).parts); bp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,bp); item['backup']=str(bp)
  dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); st.append(item); log(lp,'APPLY '+str(dst))
 (backup/'rollback_state.json').write_text(json.dumps({'package_id':PACKAGE_ID,'files':st},ensure_ascii=False,indent=2),encoding='utf-8')
 log(lp,'[END] apply ok'); return 0
def rollback(args,lp):
 log(lp,'[START] rollback'); sp=state(args.target_root)
 if not sp: log(lp,'ROLLBACK nada que restaurar'); return 0
 data=json.loads(sp.read_text(encoding='utf-8'))
 for it in reversed(data.get('files',[])):
  dst=targ(args.target_root,it['target'])
  if it.get('existed') and it.get('backup'): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(it['backup'],dst); log(lp,'RESTORE '+str(dst))
  elif dst.exists(): dst.unlink(); log(lp,'REMOVE '+str(dst))
 log(lp,'[END] rollback ok'); return 0
def main(argv=None):
 p=argparse.ArgumentParser(); g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--dry-run',action='store_true'); g.add_argument('--apply',action='store_true'); g.add_argument('--verify',action='store_true'); g.add_argument('--rollback',action='store_true')
 p.add_argument('--target-root',default=DEFAULT_TARGET_ROOT); p.add_argument('--zip-path'); p.add_argument('--log-dir',default=DEFAULT_LOG_DIR); p.add_argument('--force',action='store_true')
 a=p.parse_args(argv); lp=Path(a.log_dir)/('prisma_pc_int_'+stamp()+'.log')
 if a.rollback: return rollback(a,lp)
 root,man,sums=load(a)
 if a.dry_run: return dry(a,root,man,sums,lp)
 if a.apply: return apply(a,root,man,sums,lp)
 if a.verify: return verify(a,root,man,sums,lp)
 return 2
if __name__=='__main__': sys.exit(main())
