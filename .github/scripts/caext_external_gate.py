from __future__ import annotations
import csv, hashlib, json, os, shutil, subprocess, sys, tempfile, time, traceback, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PIN="6bd15cda5649a58c7bac806faff446c9074a2d94"
ROOT=Path(os.environ["CAEXT_HITECH_ROOT"]).resolve()
OUT=Path(os.environ["CAEXT_OUTPUT_ROOT"]).resolve()
WORKERS=18
REPOS=[
 {"id":"A","slug":"pallets/click","url":"https://github.com/pallets/click.git","sha":"8b44edfff7d9a6c895fa804148c16b3a0bc9efb5","tree":"a52cd0994280efa88a13aa9af244c4b809b89b13","stack":"Python library / CLI","target":"src/click/_termui_impl.py","other":"tests/test_termui.py","request":"Fix Windows temporary pager text handling without touching parser core or packaging.","domain":"runtime","hist":"8b44edfff7d9a6c895fa804148c16b3a0bc9efb5","hist_paths":["CHANGES.md","src/click/_termui_impl.py","tests/test_termui.py"]},
 {"id":"B","slug":"vitejs/vite","url":"https://github.com/vitejs/vite.git","sha":"dcf88bd2ad2b1a8845f9029587cc8c825e382d42","tree":"d2deca5bf3ec6b42068290ba4f97b52d93eb8b9d","stack":"TypeScript / Node monorepo","target":"packages/vite/src/node/plugins/define.ts","other":"packages/vite/src/node/__tests__/plugins/define.spec.ts","request":"Fix define-key matching for $-prefixed keys without touching unrelated build pipeline behavior.","domain":"runtime","hist":"dcf88bd2ad2b1a8845f9029587cc8c825e382d42","hist_paths":["packages/vite/src/node/plugins/define.ts","packages/vite/src/node/__tests__/plugins/define.spec.ts"]},
 {"id":"C","slug":"BurntSushi/ripgrep","url":"https://github.com/BurntSushi/ripgrep.git","sha":"3fce3b5bb0236da2df6d99672afb8a719642eca7","tree":"856ed9162d23416ee7dc5f4389975b54ca062f60","stack":"Rust CLI / workspace","target":"crates/ignore/src/gitignore.rs","other":"crates/ignore/src/types.rs","request":"Increase ignore matcher pool capacity without changing unrelated search behavior or release metadata.","domain":"runtime","hist":"020687a77d13146923333f0beb274eeabd54a270","hist_paths":["Cargo.lock","crates/globset/Cargo.toml","crates/ignore/Cargo.toml","crates/ignore/src/gitignore.rs","crates/ignore/src/types.rs"]},
]
HARD_LEAK=["PRISMA","hitech-os","terminal-de-venta-system","Factory Ledger","Authority Mesh","AutoMesh","Chart Lab","PRISMA_CTX","NDC"]
run_id="caext_"+datetime.now().astimezone().strftime("%d%m_%H%M%S")
tmp=Path(tempfile.mkdtemp(prefix=run_id+"_"))
stage=tmp/"package"; stage.mkdir(parents=True)
logfile=stage/"runner.log"

def iso(): return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
def log(s):
 print(s,flush=True)
 with logfile.open("a",encoding="utf-8") as f:f.write(s+"\n")
def sh(cmd,cwd=None,check=True,timeout=1800):
 p=subprocess.run(cmd,cwd=str(cwd) if cwd else None,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if p.stdout.strip(): log(p.stdout[-5000:])
 if p.stderr.strip(): log(p.stderr[-5000:])
 if check and p.returncode: raise RuntimeError(f"COMMAND_FAILED[{p.returncode}] {' '.join(cmd)}")
 return p
def git(repo,*a,check=True): return sh(["git","-C",str(repo),*a],check=check)
def jdump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def md(p,t): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t.rstrip()+"\n",encoding="utf-8")
def jload(p): return json.loads(p.read_text(encoding="utf-8"))
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def identity(repo):
 def q(*a):
  p=git(repo,*a,check=False); return p.stdout.strip() if p.returncode==0 else None
 st=q("status","--porcelain=v1","--untracked-files=all")
 return {"head":q("rev-parse","HEAD"),"tree":q("rev-parse","HEAD^{tree}"),"branch":q("branch","--show-current"),"remote":q("config","--get","remote.origin.url"),"dirty":bool(st) if st is not None else None,"status":st or ""}
def clone(spec):
 d=tmp/f"repo_{spec['id']}"; sh(["git","init",str(d)]); git(d,"remote","add","origin",spec["url"]); git(d,"fetch","--depth=1","--no-tags","origin",spec["sha"]); git(d,"checkout","--detach","FETCH_HEAD")
 i=identity(d)
 if i["head"]!=spec["sha"] or i["tree"]!=spec["tree"] or i["dirty"]: raise RuntimeError(f"PIN_MISMATCH:{spec['slug']}:{i}")
 return d
def worktree(base,label):
 d=tmp/"wt"/label; d.parent.mkdir(exist_ok=True)
 git(base,"worktree","add","--detach","--force",str(d),"HEAD")
 return d
def rmwt(base,d):
 git(base,"worktree","remove","--force",str(d),check=False); shutil.rmtree(d,ignore_errors=True)
def mutate(p):
 suf=p.suffix.lower(); mark="\n# caext fixture\n" if suf in {".py",".sh",".yml",".yaml"} else ("\n<!-- caext fixture -->\n" if suf in {".md",".html"} else "\n// caext fixture\n")
 with p.open("a",encoding="utf-8",errors="replace") as f:f.write(mark)
def policy(rid,protected,strict=False,auth=None):
 return {"schemaVersion":"code_atlas_customer_policy.v1","policyId":f"caext-{rid}-{'strict' if strict else 'base'}","version":"1","protectedPaths":[protected] if protected else [],"requiredAuthorities":[auth] if auth else [],"requiredTests":["caext.required.check"] if strict else [],"requiredReviews":[],"forbiddenOperations":["push","deploy","database-mutation","dependency-install","process-kill","port-change"],"domainEvidenceRequirements":["caext.required.evidence"] if strict else [],"impactThresholds":{}}
def codes(r): return sorted({str(x.get("code")) for x in r.get("findings",[]) if isinstance(x,dict) and x.get("code")})
def negrow(name,report,accepted):
 d=str(report.get("decision") or "ERROR"); return {"scenario":name,"actual":d,"accepted":sorted(accepted),"behaviorPass":d in accepted,"findingCodes":codes(report)}
def stable(ctx):
 s=ctx.get("snapshot") or {}; a=ctx.get("authorities") or {}
 return {"repository":s.get("repository"),"profile":s.get("profile"),"scanner":s.get("scannerVersion"),"request":s.get("requestDigest"),"authorityHashes":s.get("authorityHashes"),"materialHashes":s.get("materialHashes"),"inventoryDigest":s.get("inventoryDigest"),"authorityDigest":s.get("authorityDigest"),"graphs":digest(ctx.get("graphs") or {}),"authorities":digest(a.get("candidates") or []),"coverage":digest(ctx.get("coverage") or {})}
def qa(inv,g,target):
 own=g.get("ownershipGraph") or {}; imp=g.get("changeImpact") or {}; tests=set(inv.get("testFiles") or [])
 oe=[e for e in own.get("edges",[]) if e.get("to")==target and e.get("owner")]; owners=sorted({e["owner"] for e in oe}); impacted=[p for p in imp.get("impacted",[]) if p!=target]
 return {
  "owner":{"support":"SUPPORTED" if owners else "UNKNOWN","answer":owners or None,"provenance":[e.get("evidence") for e in oe]},
  "dependsOnTarget":{"support":"INFERRED" if impacted else "UNKNOWN","answer":impacted,"provenance":["changeImpact"],"doesNotProve":imp.get("doesNotProve")},
  "relatedTests":{"support":"INFERRED" if set(impacted)&tests else "UNKNOWN","answer":sorted(set(impacted)&tests),"provenance":["testFiles","changeImpact"]},
  "documentationContradictions":{"support":"UNKNOWN","answer":None,"provenance":[],"nextEvidence":"semantic source-vs-doc reconciliation not instrumented"},
  "sensitivePaths":{"support":"SUPPORTED","answer":inv.get("sensitivePaths") or [],"provenance":["repository_inventory.sensitivePaths"]},
  "unclassifiedArchitectureFiles":{"support":"SUPPORTED","answer":sum(1 for x in (g.get("architectureLayerGraph") or {}).get("nodes",[]) if x.get("layer")=="unclassified"),"provenance":["architectureLayerGraph"]},
 }
def leakscan(repo_stage,inventory_paths):
 findings=[]
 for p in list((repo_stage/"native_extracted").rglob("*.json"))+[repo_stage/"prep_base.json",repo_stage/"prep_strict.json"]:
  if not p.is_file(): continue
  txt=p.read_text(encoding="utf-8",errors="replace").lower()
  for term in HARD_LEAK:
   if term.lower() in txt: findings.append({"severity":"BUG_LEAKAGE","term":term,"file":p.relative_to(repo_stage).as_posix()})
 for term in ["Tablet","PC","Mobile"]:
  for p in (repo_stage/"native_extracted").rglob("*.json"):
   if p.is_file() and term.lower() in p.read_text(encoding="utf-8",errors="replace").lower():
    findings.append({"severity":"SOURCE_DERIVED_ALLOWED" if any(term.lower() in x.lower() for x in inventory_paths) else "REVIEW_CONTEXTUAL_TERM","term":term,"file":p.relative_to(repo_stage).as_posix()})
 return findings
def hist_validate(spec,base,resolve,Req):
 if spec["hist"]!=spec["sha"]: git(base,"fetch","--depth=1","--no-tags","origin",spec["hist"])
 w=worktree(base,f"hist_{spec['id']}")
 try:
  git(w,"checkout","--detach",spec["hist"])
  c=resolve(w,stage/f"repo_{spec['id']}"/"hist_out",request=Req(intent="VERIFY",domain=spec["domain"],changed_paths=(spec["target"],),semantic_query=spec["request"],workers=WORKERS))
  impacted=set(((c.get("graphs") or {}).get("changeImpact") or {}).get("impacted") or []); actual=set(spec["hist_paths"])
  return {"commit":spec["hist"],"actualChanged":sorted(actual),"impact":sorted(impacted),"missedHistorical":sorted(actual-impacted),"extraImpact":sorted(impacted-actual),"recallPct":round(100*len(actual&impacted)/max(1,len(actual)),2)}
 finally: rmwt(base,w)
def negatives(spec,base,pbase,pstrict,pauth,pol,pols,pola,protected,auth,verify,prepare,fresh):
 rows=[]; raw={}
 def do(name,wt,changed,prep,policy_,evidence=None,accepted={"BLOCKED"}):
  r=verify(prep,wt,changed_paths=changed,produced_evidence=evidence,policy=policy_,workers=WORKERS); raw[name]=r; rows.append(negrow(name,r,accepted)); return r
 w=worktree(base,f"{spec['id']}_allow")
 try: mutate(w/spec["target"]); do("allowed_in_scope",w,[spec["target"]],pbase,pol,accepted={"PASS"})
 finally: rmwt(base,w)
 w=worktree(base,f"{spec['id']}_out")
 try: mutate(w/spec["other"]); do("out_of_scope",w,[spec["other"]],pbase,pol)
 finally: rmwt(base,w)
 if protected:
  w=worktree(base,f"{spec['id']}_prot")
  try: mutate(w/protected); do("protected_path",w,[protected],pbase,pol)
  finally: rmwt(base,w)
 do("missing_required_evidence",base,[],pstrict,pols,evidence=[])
 if pauth and pauth.get("authorityPack") and auth:
  w=worktree(base,f"{spec['id']}_auth")
  try: mutate(w/auth); do("authority_drift",w,[],pauth,pola)
  finally: rmwt(base,w)
 else: rows.append({"scenario":"authority_drift","actual":"NOT_RUN","behaviorPass":False,"reason":"no authority-bearing pack"})
 evid=protected or auth
 if evid:
  w=worktree(base,f"{spec['id']}_evid")
  try: mutate(w/evid); do("evidence_drift",w,[],pbase,pol)
  finally: rmwt(base,w)
 w=worktree(base,f"{spec['id']}_stale")
 try:
  mutate(w/spec["target"]); git(w,"config","user.name","CAEXT"); git(w,"config","user.email","caext@example.invalid"); git(w,"add","--",spec["target"]); git(w,"commit","-m","caext disposable fixture"); do("stale_commit_tree",w,[spec["target"]],pbase,pol)
 finally: rmwt(base,w)
 r=prepare(base,change_request="Modify a target that does not exist; do not guess.",target_paths=["__missing__/never.exists"],output_root=stage/f"repo_{spec['id']}"/"missing_out",policy=pol,domain=spec["domain"],intent="VERIFY",workers=WORKERS); raw["unknown_target"]=r; rows.append(negrow("unknown_target",r,{"BLOCKED","UNKNOWN"}))
 w=worktree(base,f"{spec['id']}_new")
 try:
  rel="caext fixtures/área incómoda/new route.txt"; p=w/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text("fixture\n",encoding="utf-8"); do("new_unicode_space_path",w,[rel],pbase,pol)
 finally: rmwt(base,w)
 w=worktree(base,f"{spec['id']}_dirty")
 try:
  rel="caext hidden/ñ dirty outside scope.txt"; p=w/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text("fixture\n",encoding="utf-8")
  fr=fresh(pbase["portableSnapshot"],w); r=do("dirty_hidden_outside_manifest",w,[],pbase,pol); raw["dirty_hidden_freshness"]=fr; rows[-1]["freshnessPrimitive"]=fr
 finally: rmwt(base,w)
 return rows,raw

def main():
 start=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
 state={"schemaVersion":"caext.v1","classification":"VERIFY / EXTERNAL EVIDENCE","startedAt":iso(),"codeAtlasCommit":PIN,"workersConfigured":WORKERS,"workerPeak":"NOT_MEASURED","productionCertified":False,"repos":[],"failures":[]}
 try:
  if git(ROOT,"diff","--quiet",PIN,"--","tools/code-atlas",check=False).returncode!=0: raise RuntimeError("CODE_ATLAS_SOURCE_DIFF_FROM_PIN")
  export=tmp/"atlas.zip"; sh(["git","-C",str(ROOT),"archive","--format=zip",f"--output={export}",PIN,"tools/code-atlas"])
  srcroot=tmp/"atlas"; zipfile.ZipFile(export).extractall(srcroot); sys.path.insert(0,str(srcroot/"tools/code-atlas/src"))
  from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context
  from code_atlas.intelligence.engine import run_intelligence
  from code_atlas.intelligence.repository import discover_repository
  from code_atlas.intelligence.snapshot import assess_snapshot_freshness
  from code_atlas.change_intelligence import prepare_change, verify_prepared_change
  for spec in REPOS:
   rs=stage/f"repo_{spec['id']}"; rs.mkdir()
   t=time.perf_counter(); base=clone(spec); pre=identity(base); jdump(rs/"identity_pre.json",pre)
   t0=time.perf_counter(); probe=discover_repository(base,workers=WORKERS); discovery=time.perf_counter()-t0
   native=run_intelligence(base,rs/"native",request=IntelligenceRequest(intent="DISCOVER",domain=spec["domain"],semantic_query=spec["request"],workers=WORKERS))
   nz=Path(native["artifact"]); ex=rs/"native_extracted"; ex.mkdir(); zipfile.ZipFile(nz).extractall(ex)
   inv=jload(ex/"repository_inventory.json"); auths=jload(ex/"authority_discovery.json"); graphs=jload(ex/"system_graphs.json"); cov=jload(ex/"coverage.json")
   protected=next((x for x in ["README.md","SECURITY.md","CONTRIBUTING.md"] if (base/x).is_file()),None)
   auth=next((x for x in ["README.md","CONTRIBUTING.md","SECURITY.md",".github/CODEOWNERS","CODEOWNERS","pyproject.toml","package.json","Cargo.toml"] if (base/x).is_file()),None)
   pol=policy(spec["id"],protected); pols=policy(spec["id"],protected,True); pola=policy(spec["id"],protected,False,auth) if auth else None
   pbase=prepare_change(base,change_request=spec["request"],target_paths=[spec["target"]],output_root=rs/"prep_out",policy=pol,domain=spec["domain"],intent="VERIFY",workers=WORKERS)
   pstrict=prepare_change(base,change_request=spec["request"],target_paths=[spec["target"]],output_root=rs/"strict_out",policy=pols,domain=spec["domain"],intent="VERIFY",workers=WORKERS)
   pauth=prepare_change(base,change_request=spec["request"],target_paths=[spec["target"]],output_root=rs/"auth_out",policy=pola,domain=spec["domain"],intent="VERIFY",workers=WORKERS) if pola else None
   jdump(rs/"prep_base.json",pbase); jdump(rs/"prep_strict.json",pstrict); jdump(rs/"prep_authority.json",pauth)
   req=IntelligenceRequest(intent="DISCOVER",domain=spec["domain"],semantic_query=spec["request"],workers=WORKERS); c1=resolve_intelligence_context(base,rs/"repeat1",request=req); c2=resolve_intelligence_context(base,rs/"repeat2",request=req); f1,f2=stable(c1),stable(c2); repeat={"stable":f1==f2,"fingerprint1":digest(f1),"fingerprint2":digest(f2)}
   hist=hist_validate(spec,base,resolve_intelligence_context,IntelligenceRequest)
   neg,raw=negatives(spec,base,pbase,pstrict,pauth,pol,pols,pola,protected,auth,verify_prepared_change,prepare_change,assess_snapshot_freshness)
   questions=qa(inv,graphs,spec["target"]); paths={str(x.get("path")) for x in inv.get("files",[]) if x.get("path")}; leaks=leakscan(rs,paths)
   post=identity(base); unchanged=pre["head"]==post["head"] and pre["tree"]==post["tree"] and not post["dirty"]; jdump(rs/"identity_post.json",post)
   states=Counter(str(x.get("state")) for x in auths.get("candidates",[])); dg=graphs.get("dependencyGraph") or {}; og=graphs.get("ownershipGraph") or {}; eg=graphs.get("evidenceGraph") or {}; alg=graphs.get("architectureLayerGraph") or {}; impact=graphs.get("changeImpact") or {}
   hard=[x for x in leaks if x["severity"]=="BUG_LEAKAGE"]
   metrics={"repoId":spec["id"],"repository":spec["slug"],"stack":spec["stack"],"commit":spec["sha"],"tree":spec["tree"],"profile":"neutral/default","files":inv.get("fileCount"),"discoverySeconds":round(discovery,3),"totalSeconds":round(time.perf_counter()-t,3),"workersConfigured":WORKERS,"workerPeak":"NOT_MEASURED","authoritiesDiscovered":len(auths.get("candidates",[])),"AUTHORITATIVE":states["AUTHORITATIVE"],"SUPPORTED":states["SUPPORTED"],"CONFLICTED":states["CONFLICTED"],"MISSING":states["MISSING"],"UNKNOWN":sum(1 for x in neg if x.get("actual")=="UNKNOWN"),"dependencyNodes":len(dg.get("nodes") or []),"dependencyEdges":dg.get("edgeCount"),"ownershipEdges":og.get("edgeCount"),"evidenceEdges":eg.get("edgeCount"),"architectureNodes":len(alg.get("nodes") or []),"testCount":(graphs.get("testIntelligence") or {}).get("testCount"),"physicalCoverage":(cov.get("physical") or {}).get("percent"),"semanticCoverage":(cov.get("semantic") or {}).get("percent"),"changeImpactSize":len(impact.get("impacted") or []),"protectedScope":[protected] if protected else [],"requiredEvidence":["caext.required.check","caext.required.evidence"],"falsePositivesDetected":"NOT_MEASURED","falseNegativesDetectedManual":"NOT_MEASURED","neutralityLeakage":len(hard),"errors":0,"blockers":sum(1 for x in neg if x.get("actual")=="BLOCKED"),"negativePassed":sum(1 for x in neg if x.get("behaviorPass")),"negativeTotal":len(neg),"repeatability":repeat["stable"],"historicalRecallPct":hist["recallPct"],"historicalMissed":hist["missedHistorical"],"baselineCloneUnchanged":unchanged}
   jdump(rs/"repository_questions.json",questions); jdump(rs/"historical_validation.json",hist); jdump(rs/"negative_tests.json",neg); jdump(rs/"negative_tests_raw.json",raw); jdump(rs/"neutrality_leaks.json",leaks); jdump(rs/"metrics.json",metrics)
   state["repos"].append({"spec":spec,"metrics":metrics,"prep":pbase,"qa":questions,"hist":hist,"negative":neg,"leaks":leaks})
  rows=[x["metrics"] for x in state["repos"]]; jdump(stage/"02_REPO_MATRIX.json",rows)
  fields=sorted({k for r in rows for k in r})
  with (stage/"01_REPO_MATRIX.csv").open("w",newline="",encoding="utf-8-sig") as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
  hard=[(r["spec"]["id"],x) for r in state["repos"] for x in r["leaks"] if x["severity"]=="BUG_LEAKAGE"]; negs=[(r["spec"]["id"],x) for r in state["repos"] for x in r["negative"]]; bad=[(rid,x) for rid,x in negs if not x.get("behaviorPass")]
  rustgap=any(r["spec"]["id"]=="C" and int(r["metrics"].get("dependencyEdges") or 0)==0 for r in state["repos"])
  classification="FIX" if hard or bad else ("VERIFY / BLOCKED FOR STRONG UNIVERSAL CLAIM" if rustgap else "VERIFY")
  state["recommendedClassification"]=classification
  md(stage/"NEUTRALITY_LEAK_SCAN.md","# NEUTRALITY LEAK SCAN\n\nHard leakage: **%d**\n\n%s"%(len(hard),"\n".join(f"- Repo {rid}: {x}" for rid,x in hard) or "- No hard implicit product leakage detected."))
  md(stage/"NEGATIVE_TEST_RESULTS.md","# NEGATIVE TEST RESULTS\n\n"+"\n".join(f"- Repo {rid} {'PASS' if x.get('behaviorPass') else 'FAIL'} `{x.get('scenario')}` actual `{x.get('actual')}` findings `{','.join(x.get('findingCodes') or [])}`" for rid,x in negs))
  md(stage/"AUTHORITY_ACCURACY.md","# AUTHORITY ACCURACY\n\n"+"\n".join(f"- Repo {r['repoId']}: discovered {r['authoritiesDiscovered']}; AUTHORITATIVE {r['AUTHORITATIVE']}; SUPPORTED {r['SUPPORTED']}; CONFLICTED {r['CONFLICTED']}; MISSING {r['MISSING']}." for r in rows)+"\n\nKnown filenames are not promoted to AUTHORITATIVE without repository declarations.")
  md(stage/"CHANGE_INTELLIGENCE_RESULTS.md","# CHANGE INTELLIGENCE RESULTS\n\n"+"\n".join(f"- Repo {x['spec']['id']}: preparation **{x['prep'].get('decision')}**, target `{x['spec']['target']}`, impact size {x['metrics']['changeImpactSize']}, historical co-change recall {x['hist']['recallPct']}%, missed `{json.dumps(x['hist']['missedHistorical'])}`." for x in state["repos"]))
  md(stage/"PERFORMANCE.md","# PERFORMANCE\n\n"+"\n".join(f"- Repo {r['repoId']}: files {r['files']}; discovery {r['discoverySeconds']}s; total {r['totalSeconds']}s; workers configured 18; worker peak NOT_MEASURED." for r in rows))
  failures=[]
  if rustgap: failures.append("C. UNSUPPORTED TECHNOLOGY: ripgrep Rust dependency graph produced zero edges.")
  for rid,x in bad: failures.append(("G. CHANGE INTELLIGENCE BUG" if x.get("scenario")=="dirty_hidden_outside_manifest" else "J. TEST/HARNESS OR PRODUCT BEHAVIOR FAILURE")+f": Repo {rid} {x}")
  for x in state["repos"]:
   for k,v in x["qa"].items():
    if v.get("support")=="UNKNOWN": failures.append(f"UNKNOWN Repo {x['spec']['id']} {k}: evidence unavailable.")
  md(stage/"FAILURES_AND_UNKNOWNS.md","# FAILURES AND UNKNOWNS\n\n"+"\n".join("- "+x for x in failures) if failures else "# FAILURES AND UNKNOWNS\n\n- None recorded. This does not authorize production claims.")
  md(stage/"CROSS_REPO_FINDINGS.md","# CROSS-REPO FINDINGS\n\n"+"\n".join(f"- Repo {r['repoId']} {r['repository']}: deps {r['dependencyEdges']}, ownership {r['ownershipEdges']}, negatives {r['negativePassed']}/{r['negativeTotal']}, leaks {r['neutralityLeakage']}, repeatable {r['repeatability']}." for r in rows))
  nextgate="STOP. Generate a new task-exact Authority Mesh for the evidenced defect before any Code Atlas patch." if classification=="FIX" else "Repeat on additional unrelated repos/machines. Do not claim production, enterprise, or absolute universality."
  md(stage/"NEXT_GATE.md",f"# NEXT GATE\n\nRecommended classification: **{classification}**\n\n{nextgate}")
  md(stage/"CONTINUATION.md",f"# CONTINUATION\n\nCode Atlas pin `{PIN}`. Classification `{classification}`. {nextgate}")
  md(stage/"00_EXECUTIVE_SUMMARY.md",f"""# EXTERNAL EVIDENCE RESULT

Repos tested: **3**
Stacks: Python; TypeScript/Node monorepo; Rust
Read-only compliance: **{'PASS' if all(r['metrics']['baselineCloneUnchanged'] for r in state['repos']) else 'BLOCKED'}**
Neutrality leakage: **{len(hard)}**
Negative-test behavior: **{sum(1 for _,x in negs if x.get('behaviorPass'))}/{len(negs)}**
Repeatability: **{sum(1 for r in rows if r['repeatability'])}/3**
Critical failures: **{len(bad)}**
Recommended classification: **{classification}**

## What this evidence proves
- The pinned Code Atlas source was exercised against three unrelated real repositories in neutral mode.
- Repository identity, authority discovery, graphs, Change Intelligence, negative verification, repeatability and provenance outputs were captured.
- External repositories were modified only in disposable local worktrees/clones.

## What this evidence does NOT prove
- Production readiness.
- Enterprise readiness.
- Correctness across arbitrary repositories or all technology stacks.
- Runtime correctness beyond supplied evidence.
- Legal/privacy/IAM/hosted multi-tenant certification.
""")
 except Exception as e:
  state["failures"].append({"class":"I/J ENVIRONMENT OR HARNESS FAILURE","error":repr(e),"traceback":traceback.format_exc()}); state["recommendedClassification"]="BLOCKED"
  md(stage/"00_EXECUTIVE_SUMMARY.md","# EXTERNAL EVIDENCE RESULT\n\n**BLOCKED / INCOMPLETE.** See run_state.json and runner.log.")
  for name in ["CROSS_REPO_FINDINGS","AUTHORITY_ACCURACY","NEUTRALITY_LEAK_SCAN","CHANGE_INTELLIGENCE_RESULTS","NEGATIVE_TEST_RESULTS","PERFORMANCE","FAILURES_AND_UNKNOWNS","NEXT_GATE","CONTINUATION"]:
   p=stage/(name+".md")
   if not p.exists(): md(p,f"# {name.replace('_',' ')}\n\nRun incomplete.")
 finally:
  state["finishedAt"]=iso(); state["elapsedSeconds"]=round(time.perf_counter()-start,3); jdump(stage/"run_state.json",state)
  files=[]
  for p in sorted(stage.rglob("*")):
   if p.is_file() and p.name!="EVIDENCE_INDEX.json": files.append({"path":p.relative_to(stage).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
  jdump(stage/"EVIDENCE_INDEX.json",{"schemaVersion":"caext_evidence_index.v1","generatedAt":iso(),"codeAtlasCommit":PIN,"files":files})
  out=OUT/f"caext_{datetime.now().astimezone().strftime('%d%m_%H%M')}.zip"
  with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
   for p in sorted(stage.rglob("*")):
    if p.is_file(): z.write(p,p.relative_to(stage).as_posix())
  print("CAEXT_RESULT="+str(out)); print("CAEXT_CLASSIFICATION="+str(state.get("recommendedClassification")))
  shutil.rmtree(tmp,ignore_errors=True)
 return 2 if state.get("recommendedClassification")=="BLOCKED" else 0

if __name__=="__main__": raise SystemExit(main())
