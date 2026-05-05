#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
const args=process.argv.slice(2);
const i=args.indexOf("--root");
const root=path.resolve(i>=0&&args[i+1]?args[i+1]:process.cwd());
const verifier="pc_dashboard_kpi_alerts_05";
const phase="I05_DOWNSTREAM";
const required=["app/dashboard/page.tsx", "app/page.tsx", "src/server/services/kpi-formulas.ts"];
const routes=["/", "/dashboard"];
const files=required.map(rel=>{const abs=path.join(root,rel);const exists=fs.existsSync(abs);const size=exists?fs.statSync(abs).size:0;return {rel,exists,size};});
const missing=files.filter(x=>!x.exists).map(x=>x.rel);
const empty=files.filter(x=>x.exists&&x.size<=0).map(x=>x.rel);
const findings=[];
function read(rel){return fs.readFileSync(path.join(root,rel),"utf8");}
if(missing.length>0)findings.push({severity:"DOWNSTREAM",code:"DASHBOARD_INCOMPLETE",message:"Queda para I04/I05; no bloquea I01."});
const ok=missing.length===0&&empty.length===0&&findings.every(f=>f.severity!=="BLOCKER");
console.log(JSON.stringify({verifier,phase,state:ok?"PASS":"FAIL",ok,root,routes,files,missing,empty,findings,checkedAt:new Date().toISOString()},null,2));
process.exit(ok?0:1);
