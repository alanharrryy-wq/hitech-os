#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path
PKG="PRISMA_VISUAL_OS_FINAL_STABILIZATION_00ZF_20260505_v01"
DEFAULT_OUT=Path(r"F:\descargasf")
HARD=[
 ("00T POS live binding",["node","tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs"]),
 ("00X doctor",["node","tools/prisma-visual-os/verify_prisma_show_pos_doctor_00x.mjs"]),
 ("00Y AI doctor",["node","tools/prisma-visual-os/verify_prisma_show_pos_ai_doctor_00y.mjs"]),
 ("00U doctor",["node","tools/prisma-visual-os/verify_prisma_show_pos_doctor_00u.mjs"]),
 ("00W README",["node","tools/prisma-visual-os/verify_prisma_visual_os_readme_status_00w.mjs"]),
 ("00N release gate",["node","tools/prisma-visual-os/gate_prisma_visual_release_00n.mjs"]),
 ("01H reference visual",["node","tools/visual/verify_prisma_reference_visual_scope_01h.mjs"]),
]
DIRS=["tools/prisma-visual-os/doctors","tools/prisma-visual-os/verifiers","tools/prisma-visual-os/gates","tools/prisma-visual-os/generators","tools/prisma-visual-os/realtime","tools/prisma-visual-os/scoring","tools/prisma-visual-os/qa","tools/prisma-visual-os/tree","tools/prisma-visual-os/launchers","tools/prisma-visual-os/docs","tools/prisma-visual-os/_plans","tools/visual","tools/prisma-pos-visual-control"]
FILES=["products/tablet/app/components/pos/pos-screen.tsx","products/tablet/app/components/pos/pos-live-binding.tsx","products/tablet/app/components/pos/pos.module.css","tools/prisma-visual-os/tree/prisma_visual_os_tree_reorg_close_00ze.py","tools/prisma-visual-os/tree/prisma_visual_os_final_stabilization_00zf.py","tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZF_INDEX.md","tools/prisma-visual-os/docs/README_PRISMA_VISUAL_OS_FINAL_00ZF.md","tools/prisma-visual-os/_plans/PRISMA_VISUAL_OS_FINAL_STABILIZATION_00ZF.md","tools/prisma-visual-os/launchers/run_prisma_visual_os_final_stabilization_00zf.cmd","tools/prisma-visual-os/run_prisma_visual_os_final_stabilization_00zf.cmd","docs/design/PRISMA_VISUAL_OS_FINAL_STABILIZATION_00ZF.md","docs/qa/PRISMA_VISUAL_OS_FINAL_STABILIZATION_00ZF_ACCEPTANCE.md","config/prisma-visual-os/final-stabilization-00zf.json"]
def system_root(t:Path)->Path:
    r=t.resolve()
    if r.name=='terminal-de-venta-system': return r
    for p in [r,*r.parents]:
        if p.name=='terminal-de-venta-system': return p
    c=r/'apps'/'terminal-de-venta-system'
    return c.resolve() if c.exists() else c
def tail(s,n=1600): return s if len(s)<=n else s[-n:]
def run(root,name,cmd):
    try:
        p=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=120)
        return {'name':name,'command':cmd,'ok':p.returncode==0,'returncode':p.returncode,'stdoutTail':tail(p.stdout),'stderrTail':tail(p.stderr)}
    except Exception as e:
        return {'name':name,'command':cmd,'ok':False,'returncode':127,'error':str(e)}
def verify(target:Path,out:Path):
    root=system_root(target); out.mkdir(parents=True,exist_ok=True); checks=[]
    checks.append({'name':'system root exists','ok':root.exists(),'path':str(root)})
    for d in DIRS: checks.append({'name':'dir '+d,'ok':(root/d).is_dir(),'path':str(root/d)})
    for f in FILES: checks.append({'name':'file '+f,'ok':(root/f).is_file(),'path':str(root/f)})
    pos=(root/'products/tablet/app/components/pos/pos-screen.tsx').read_text(encoding='utf-8',errors='replace') if root.exists() else ''
    checks += [
      {'name':'PosScreen imports PosLiveBinding','ok':'import { PosLiveBinding } from "./pos-live-binding";' in pos},
      {'name':'PosScreen renders PosLiveBinding','ok':'<PosLiveBinding />' in pos},
      {'name':'PosScreen declares 00T hook','ok':'data-prisma-pos-live="00T"' in pos},
    ]
    results=[run(root,n,c) for n,c in HARD] if root.exists() else []
    ok=all(c['ok'] for c in checks) and all(r['ok'] for r in results)
    data={'package':PKG,'status':'ready' if ok else 'blocked','systemRoot':str(root),'checks':checks,'hardCommandResults':results,'legacyDisposition':{'tools/prisma-pos-visual-control':'legacy compatibility archive kept','tools/visual':'reference visual scope kept','root shims':'kept intentionally'}}
    report=out/("prisma_visual_os_final_stabilization_00zf_"+dt.datetime.now().strftime('%y%m%d_%H%M')+".json")
    report.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8'); data['report']=str(report)
    return (0 if ok else 4),data
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--target-root',default='.'); ap.add_argument('--out-dir',default=str(DEFAULT_OUT)); ap.add_argument('--verify',action='store_true')
    a=ap.parse_args(); rc,data=verify(Path(a.target_root),Path(a.out_dir)); print(json.dumps(data,indent=2,ensure_ascii=False)); return rc
if __name__=='__main__': raise SystemExit(main())
