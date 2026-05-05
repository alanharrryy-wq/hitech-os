from __future__ import annotations
import argparse, datetime as dt, hashlib, json
from pathlib import Path
PKG="PRISMA_VISUAL_OS_TREE_REORG_DOCTORS_VERIFIERS_SHIMS_00ZC_20260504_v01"
SYSTEM=Path("apps")/"terminal-de-venta-system"
VISUAL=SYSTEM/"tools"/"prisma-visual-os"
REQ=["doctors","launchers","verifiers","realtime","scoring","generators","gates","qa","docs","tree","_plans"]
DOCTORS=["ai_doctor_prisma_show_pos_00y.py","doctor_prisma_show_pos_scan_00u.py","doctor_prisma_show_pos_scan_00x.py"]
VERIFIERS=["verify_prisma_light_operational_pos_tokenization_00p.mjs","verify_prisma_show_pos_ai_doctor_00y.mjs","verify_prisma_show_pos_doctor_00u.mjs","verify_prisma_show_pos_doctor_00x.mjs","verify_prisma_visual_os_control_plane_00a.mjs","verify_prisma_visual_os_core_00d_00e.mjs","verify_prisma_visual_os_pos_live_binding_00t.mjs","verify_prisma_visual_os_readme_status_00w.mjs","verify_prisma_visual_os_studio_pro_qa_00r_00s.mjs","verify_prisma_visual_qa_release_gate_00l_00m_00n.mjs"]
PATS=["Path(__file__)","__file__","process.cwd","prisma-visual-os","tools/prisma-visual-os","tools\\prisma-visual-os","import.meta.url","__dirname","subprocess","child_process","127.0.0.1","localhost"]

def stamp(): return dt.datetime.now().strftime('%y%m%d_%H%M%S')
def jwrite(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def log(p,msg): p.parent.mkdir(parents=True,exist_ok=True); p.open('a',encoding='utf-8').write(msg+'\n')
def sha(p):
    if not p.exists() or not p.is_file(): return None
    h=hashlib.sha256();
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1048576),b''): h.update(c)
    return h.hexdigest()
def txt(p): return p.read_text(encoding='utf-8',errors='ignore') if p.exists() and p.is_file() else ''
def hits(p):
    out=[]
    for i,line in enumerate(txt(p).splitlines(),1):
        for pat in PATS:
            if pat in line:
                s=line.strip(); out.append({'line':i,'pattern':pat,'snippet':s[:180]}); break
    return out
def pyshim(n): return "from pathlib import Path\nimport runpy\nimport sys\n\n_TARGET = Path(__file__).resolve().parent / 'doctors' / '%s'\nif not _TARGET.exists():\n    raise SystemExit(f'PRISMA 00ZC shim target missing: {_TARGET}')\nsys.argv[0] = str(_TARGET)\nrunpy.run_path(str(_TARGET), run_name='__main__')\n"%n
def mshim(n): return "import './verifiers/%s';\n"%n
def action(cat,src,dst,shim,rh):
    srcx,dstx=src.exists(),dst.exists(); ishim=srcx and shim.strip() in txt(src); pats={x['pattern'] for x in rh}
    if dstx and ishim: return 'already_moved_with_shim','target exists and root shim points to it'
    if srcx and dstx and not ishim: return 'blocked_dual_copy','source and target both exist without compatible shim'
    if (not srcx) and dstx: return 'repair_root_shim_candidate','target exists but root shim is missing'
    if not srcx and not dstx: return 'missing','source and target missing'
    if cat=='doctors' and ({'Path(__file__)','__file__','subprocess'} & pats): return 'blocked_patch_required_before_move','doctor depends on script identity, root path, or subprocess behavior'
    if cat=='verifiers' and ({'import.meta.url','__dirname','child_process'} & pats): return 'blocked_patch_required_before_move','verifier has script-location or process assumptions'
    return ('planned_move_with_root_python_shim' if cat=='doctors' else 'planned_move_with_root_mjs_shim'),'candidate for later move with root shim; 00ZC does not move it'
def plan(root):
    v=root/VISUAL; items=[]
    for cat,folder,names in [('doctors','doctors',DOCTORS),('verifiers','verifiers',VERIFIERS)]:
        for n in names:
            src=v/n; dst=v/folder/n; shim=pyshim(n) if cat=='doctors' else mshim(n); rh=hits(src if src.exists() else dst); a,why=action(cat,src,dst,shim,rh)
            items.append({'name':n,'category':cat,'source':str(src),'target':str(dst),'sourceExists':src.exists(),'targetExists':dst.exists(),'sourceSha256':sha(src),'targetSha256':sha(dst),'riskHitCount':len(rh),'riskHits':rh[:40],'plannedRootShimPreview':shim,'action':a,'reason':why})
    summ={'totalCandidates':len(items),'byAction':{},'byCategory':{},'movesAppliedBy00ZC':0,'movementAllowedIn00ZCStage1':False}
    for it in items:
        summ['byAction'][it['action']]=summ['byAction'].get(it['action'],0)+1; summ['byCategory'][it['category']]=summ['byCategory'].get(it['category'],0)+1
    return {'package':PKG,'mode':'stage1_dry_run_plan_only','generatedAt':dt.datetime.now().isoformat(timespec='seconds'),'targetRoot':str(root),'visualRoot':str(v),'scope':{'runtimePosTouched':False,'tabletUiTouched':False,'cssTouched':False,'rootLaunchersMoved':False,'movesApplied':0},'requiredDirs':[{'name':d,'path':str(v/d),'exists':(v/d).exists()} for d in REQ],'summary':summ,'items':items,'nextRecommendedPackage':{'name':'PRISMA_VISUAL_OS_TREE_REORG_DOCTORS_VERIFIERS_MOVE_00ZD','preconditions':['review 00ZC plan','patch doctor self-check paths or defer doctors','run 00X/00Y/00T/04H before and after any future movement','confirm /pos, /visual-os/pro and realtime /health']}}
def markdown(data):
    lines=['# PRISMA Visual OS Tree Reorg 00ZC - dry-run plan','',f"- Package: `{PKG}`",'- Stage 1 applies no doctors/verifiers moves.','',f"- Total candidates: `{data['summary']['totalCandidates']}`",f"- By action: `{json.dumps(data['summary']['byAction'],ensure_ascii=False)}`",'','## Candidates']
    for it in data['items']: lines.append(f"- `{it['name']}` -> `{it['target']}`: **{it['action']}**. {it['reason']}")
    return '\n'.join(lines)+'\n'
def dry(args):
    root=Path(args.target_root).resolve(); out=Path(args.out_dir).resolve(); out.mkdir(parents=True,exist_ok=True); s=stamp(); lg=out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.log'
    if not (root/VISUAL).exists():
        r={'status':'blocked','reason':'visual root missing','visualRoot':str(root/VISUAL),'log':str(lg)}; jwrite(out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.json',r); print(json.dumps(r,indent=2,ensure_ascii=False)); return 2
    data=plan(root); pj=out/f'prisma_visual_os_tree_reorg_00zc_plan_{s}.json'; pm=out/f'prisma_visual_os_tree_reorg_00zc_plan_{s}.md'; jwrite(pj,data); pm.write_text(markdown(data),encoding='utf-8'); log(lg,f'DRY-RUN {pj}'); log(lg,'NO MOVES APPLIED')
    r={'status':'ready_for_review','package':PKG,'planJson':str(pj),'planMarkdown':str(pm),'summary':data['summary'],'log':str(lg)}; jwrite(out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.json',r); print(json.dumps(r,indent=2,ensure_ascii=False)); return 0
def verify(args):
    root=Path(args.target_root).resolve(); out=Path(args.out_dir).resolve(); out.mkdir(parents=True,exist_ok=True); s=stamp(); v=root/VISUAL; lg=out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.log'
    checks=[{'name':'visual root','ok':v.exists(),'path':str(v)}]+[{'name':'dir '+d,'ok':(v/d).exists(),'path':str(v/d)} for d in REQ]+[{'name':'engine','ok':(v/'tree/prisma_visual_os_tree_reorg_00zc.py').exists(),'path':str(v/'tree/prisma_visual_os_tree_reorg_00zc.py')},{'name':'launcher','ok':(v/'run_prisma_visual_os_tree_reorg_00zc.cmd').exists(),'path':str(v/'run_prisma_visual_os_tree_reorg_00zc.cmd')}]
    ok=all(c['ok'] for c in checks); r={'package':PKG,'mode':'verify','status':'verified' if ok else 'blocked','checks':checks,'log':str(lg)}; jwrite(out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.json',r); log(lg,'VERIFY '+('OK' if ok else 'BLOCKED')); print(json.dumps(r,indent=2,ensure_ascii=False)); return 0 if ok else 4
def blocked(args,mode):
    out=Path(args.out_dir).resolve(); out.mkdir(parents=True,exist_ok=True); s=stamp(); lg=out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.log'; r={'package':PKG,'mode':mode,'status':'nothing_to_apply' if mode=='rollback' else 'blocked_by_design','reason':'00ZC engine is plan-only and never moves doctors/verifiers. Installer --apply only installs planner files.','log':str(lg)}; jwrite(out/f'prisma_visual_os_tree_reorg_00zc_int_{s}.json',r); log(lg,mode.upper()+' no movement'); print(json.dumps(r,indent=2,ensure_ascii=False)); return 0 if mode=='rollback' else 6
def main():
    p=argparse.ArgumentParser(description='PRISMA Visual OS 00ZC doctors/verifiers movement planner'); g=p.add_mutually_exclusive_group(required=True); [g.add_argument(x,action='store_true') for x in ['--dry-run','--apply','--verify','--rollback']]; p.add_argument('--target-root',default=r'F:\repos\hitech-os'); p.add_argument('--out-dir',default=r'F:\descargasf'); a=p.parse_args()
    if a.dry_run: return dry(a)
    if a.verify: return verify(a)
    if a.apply: return blocked(a,'apply')
    if a.rollback: return blocked(a,'rollback')
if __name__=='__main__': raise SystemExit(main())
