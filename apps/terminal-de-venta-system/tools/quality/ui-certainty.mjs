#!/usr/bin/env node
/* PRISMA UI Certainty Supreme Mesh - repo-native gate */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const cwd = process.cwd();
function exists(p){ try { return fs.existsSync(p); } catch { return false; } }
function readJson(p){ return JSON.parse(fs.readFileSync(p,'utf8')); }
function writeJson(p,obj){ fs.mkdirSync(path.dirname(p),{recursive:true}); fs.writeFileSync(p, JSON.stringify(obj,null,2),'utf8'); }
function writeText(p,s){ fs.mkdirSync(path.dirname(p),{recursive:true}); fs.writeFileSync(p,s,'utf8'); }
function walk(dir, opts={}, out=[]){
  if(!exists(dir)) return out;
  const skip = new Set(['.git','node_modules','.next','dist','build','coverage','.turbo','.cache','out','__pycache__','.prisma','generated']);
  for(const e of fs.readdirSync(dir,{withFileTypes:true})){
    const p = path.join(dir,e.name);
    if(e.isDirectory()) { if(!skip.has(e.name)) walk(p,opts,out); }
    else out.push(p);
  }
  return out;
}
function rel(p){ return path.relative(cwd,p).replace(/\\/g,'/'); }
function parseArgs(){
  const args=process.argv.slice(2); const cmd=args.shift()||'work'; const flags={_:[]};
  for(let i=0;i<args.length;i++){ const a=args[i]; if(a.startsWith('--')){ const k=a.slice(2); const v=(i+1<args.length && !args[i+1].startsWith('--'))?args[++i]:true; flags[k]=v;} else flags._.push(a); }
  return {cmd,flags};
}
function load(){
  const root = path.join(cwd,'.prisma-ui');
  const registryPath=path.join(root,'registry.json');
  const surfacesPath=path.join(root,'surfaces.json');
  const panelDir=path.join(root,'panels');
  const registry=exists(registryPath)?readJson(registryPath):null;
  const surfaces=exists(surfacesPath)?readJson(surfacesPath):null;
  const panels=[];
  if(exists(panelDir)) for(const f of fs.readdirSync(panelDir).filter(x=>x.endsWith('.json')).sort()) panels.push(readJson(path.join(panelDir,f)));
  return {root,registryPath,surfacesPath,panelDir,registry,surfaces,panels};
}
function findAnchors(files){
  const anchors=[];
  const rx=/data-prisma-panel\s*=\s*['"`]([^'"`]+)['"`]/g;
  for(const f of files){
    if(!/\.(tsx|jsx|ts|js|html|mdx)$/i.test(f)) continue;
    let txt=''; try{ if(fs.statSync(f).size>2500000) continue; txt=fs.readFileSync(f,'utf8'); }catch{ continue; }
    let m; while((m=rx.exec(txt))) anchors.push({panel_id:m[1], file:rel(f), index:m.index});
  }
  return anchors;
}
function textSearch(files, terms){
  const hits=[];
  for(const f of files){
    if(!/\.(tsx|jsx|ts|js|css|scss|md|json|mjs|cjs)$/i.test(f)) continue;
    let txt=''; try{ if(fs.statSync(f).size>2500000) continue; txt=fs.readFileSync(f,'utf8'); }catch{ continue; }
    for(const t of terms||[]){ if(t && txt.includes(t)) hits.push({term:t,file:rel(f)}); }
  }
  return hits;
}
function selectorExists(selector, files){
  if(!selector || selector.startsWith('[')) return null;
  let key = selector.replace(/::?.*$/,'').trim();
  if(key.startsWith('.')) key = key.slice(1);
  if(!key) return null;
  for(const f of files){
    if(!/\.(css|scss|module\.css)$/i.test(f)) continue;
    try{ if(fs.statSync(f).size>2500000) continue; const txt=fs.readFileSync(f,'utf8'); if(txt.includes(key)) return rel(f); }catch{}
  }
  return false;
}
function gitChanged(){
  try{
    const out=execFileSync('git',['diff','--name-only'],{cwd,encoding:'utf8',stdio:['ignore','pipe','ignore']});
    const out2=execFileSync('git',['diff','--name-only','--cached'],{cwd,encoding:'utf8',stdio:['ignore','pipe','ignore']});
    return Array.from(new Set((out+'\n'+out2).split(/\r?\n/).map(x=>x.trim()).filter(Boolean)));
  }catch{return []}
}
function globishMatch(file, pattern){
  pattern=(pattern||'').replace(/\\/g,'/'); file=file.replace(/\\/g,'/');
  if(pattern.endsWith('/**')) return file.startsWith(pattern.slice(0,-3));
  if(pattern.includes('**')) return file.startsWith(pattern.split('**')[0]);
  return file===pattern || file.endsWith(pattern);
}
function zeroImportant(files){
  const hits=[];
  for(const f of files){
    if(!/\.(css|scss|tsx|ts|jsx|js)$/i.test(f)) continue;
    try{ if(fs.statSync(f).size>2500000) continue; const lines=fs.readFileSync(f,'utf8').split(/\r?\n/); lines.forEach((line,i)=>{ if(line.includes('!important')) hits.push({file:rel(f),line:i+1,text:line.trim().slice(0,260)}); }); }catch{}
  }
  return hits;
}
function certify(flags={}){
  const data=load(); const scanRoots=['products','app','src','components','styles','tools','docs','.prisma-ui'].map(x=>path.join(cwd,x)).filter(exists);
  const files=[]; scanRoots.forEach(r=>walk(r,{},files));
  const anchors=findAnchors(files);
  const cssFiles=files.filter(f=>/\.(css|scss|module\.css)$/i.test(f));
  const reports=[]; const conflicts={};
  for(const a of anchors) (conflicts[a.panel_id]||(conflicts[a.panel_id]=[])).push(a.file);
  const wantedPanel=flags.panel;
  const panels=data.panels.filter(p=>!wantedPanel || p.panel_id===wantedPanel);
  for(const p of panels){
    const anchorHits=anchors.filter(a=>a.panel_id===p.panel_id);
    const termHits=textSearch(files,p.target_strings||[]);
    const selectorChecks=(p.canonical_selectors||[]).map(sel=>({selector:sel, foundIn:selectorExists(sel,cssFiles)}));
    const ownerComponent=p.owner_component?exists(path.join(cwd,p.owner_component)):null;
    const ownerCss=p.owner_css_module?exists(path.join(cwd,p.owner_css_module)):null;
    let status='EVIDENCE_READY_UNCERTIFIED';
    const blockers=[];
    if(anchorHits.length===0) blockers.push('missing data-prisma-panel anchor');
    const missingSelectors=selectorChecks.filter(x=>x.foundIn===false).map(x=>x.selector);
    if(missingSelectors.length) blockers.push('missing canonical selectors: '+missingSelectors.join(', '));
    if(ownerComponent===false) blockers.push('owner_component missing');
    if(ownerCss===false) blockers.push('owner_css_module missing');
    if(blockers.length) status='BLOCKED'; else if((p.status||'').includes('CERTIFIED') && anchorHits.length) status='CERTIFIED';
    reports.push({panel_id:p.panel_id,surface:p.surface,route:p.route,status,blockers,anchorHits,termHits:termHits.slice(0,80),selectorChecks,ownerComponent,ownerCss,allowed_files:p.allowed_files||[],forbidden_surfaces:p.forbidden_surfaces||[]});
  }
  const zi=zeroImportant(files);
  const changed=gitChanged();
  const scope=[];
  for(const f of changed){
    const owners=reports.filter(r=>(r.allowed_files||[]).some(p=>globishMatch(f,p)));
    scope.push({file:f,allowedBy:owners.map(o=>o.panel_id),status:owners.length?'MAPPED':'UNMAPPED'});
  }
  const summary={
    schema:'prisma.ui.cert.report.v1', createdAt:new Date().toISOString(), command:'certify', cwd,
    status: reports.some(r=>r.status==='BLOCKED')?'BLOCKED':(reports.some(r=>r.status==='EVIDENCE_READY_UNCERTIFIED')?'EVIDENCE_READY_UNCERTIFIED':'CERTIFIED'),
    registryExists:!!data.registry, surfacesExists:!!data.surfaces, panelCount:data.panels.length, anchorCount:anchors.length,
    changedCount:changed.length, unmappedChanged:scope.filter(x=>x.status==='UNMAPPED'), zeroImportantCount:zi.length,
    panels:reports, anchors, scope, zeroImportant:zi.slice(0,500)
  };
  writeJson(path.join(cwd,'.prisma-ui','current','UI_CERT_REPORT.json'),summary);
  const md=['# UI Certainty Report','',`- status: \`${summary.status}\``,`- panels: \`${summary.panelCount}\``,`- anchors: \`${summary.anchorCount}\``,`- zero-important hits: \`${summary.zeroImportantCount}\``, '', '## Panels', ...reports.map(r=>`- ${r.status} · ${r.panel_id} · blockers: ${r.blockers.join('; ')||'none'}`),''];
  writeText(path.join(cwd,'.prisma-ui','current','UI_CERT_REPORT.md'),md.join('\n'));
  return summary;
}
function work(flags={}){
  const report=certify(flags);
  const panel=flags.panel?report.panels.find(p=>p.panel_id===flags.panel):null;
  if(panel){ console.log(JSON.stringify({status:panel.status,panel:panel.panel_id,allowed_files:panel.allowed_files,blockers:panel.blockers},null,2)); }
  else console.log(JSON.stringify({status:report.status,panelCount:report.panelCount,anchorCount:report.anchorCount,zeroImportantCount:report.zeroImportantCount},null,2));
  return report;
}
function selftest(){
  const data=load(); const problems=[];
  if(!data.registry) problems.push('missing .prisma-ui/registry.json');
  if(!data.surfaces) problems.push('missing .prisma-ui/surfaces.json');
  if(!data.panels.length) problems.push('missing panel contracts');
  const r={status:problems.length?'FAIL':'PASS',problems,panelCount:data.panels.length,createdAt:new Date().toISOString()};
  writeJson(path.join(cwd,'.prisma-ui','current','UI_CERT_SELFTEST.json'),r);
  console.log(JSON.stringify(r,null,2));
  return r;
}
function scope(){
  const report=certify({});
  const blocked=report.unmappedChanged||[];
  console.log(JSON.stringify({status:blocked.length?'BLOCKED':'PASS',unmappedChanged:blocked},null,2));
  return {status:blocked.length?'BLOCKED':'PASS'};
}
function zero(){
  const files=[]; ['products','app','src','components','styles'].map(x=>path.join(cwd,x)).filter(exists).forEach(r=>walk(r,{},files));
  const hits=zeroImportant(files); const r={status:hits.length?'BLOCKED':'PASS',count:hits.length,hits:hits.slice(0,500)};
  writeJson(path.join(cwd,'.prisma-ui','current','ZERO_IMPORTANT_REPORT.json'),r); console.log(JSON.stringify(r,null,2)); return r;
}
const {cmd,flags}=parseArgs(); let result;
if(cmd==='self-test') result=selftest();
else if(cmd==='certify') result=certify(flags), console.log(JSON.stringify({status:result.status,panelCount:result.panelCount,anchorCount:result.anchorCount},null,2));
else if(cmd==='scope') result=scope();
else if(cmd==='zero-important') result=zero();
else if(cmd==='work') result=work(flags);
else if(cmd==='supreme') result=work(flags);
else { console.error('Unknown command '+cmd); process.exit(2); }
if(flags.strict && result && ['FAIL','BLOCKED'].includes(result.status)) process.exit(1);
