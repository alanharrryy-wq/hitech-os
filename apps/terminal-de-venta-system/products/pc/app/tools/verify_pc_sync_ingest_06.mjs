#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
const args=process.argv.slice(2);
const i=args.indexOf("--root");
const root=path.resolve(i>=0&&args[i+1]?args[i+1]:process.cwd());
const verifier="pc_sync_ingest_conflicts_release_06";
const phase="I06_DOWNSTREAM";
const required=["app/sync/page.tsx", "app/api/sync/ingest/route.ts", "src/server/validators/sync-event-contract.ts"];
const routes=["/sync", "/api/sync/ingest"];
const files=required.map(rel=>{const abs=path.join(root,rel);const exists=fs.existsSync(abs);const size=exists?fs.statSync(abs).size:0;return {rel,exists,size};});
const missing=files.filter(x=>!x.exists).map(x=>x.rel);
const empty=files.filter(x=>x.exists&&x.size<=0).map(x=>x.rel);
const findings=[];
function read(rel){return fs.readFileSync(path.join(root,rel),"utf8");}
if(missing.length>0)findings.push({severity:"DOWNSTREAM",code:"SYNC_INCOMPLETE",message:"Queda para I05; no bloquea I01."});
const ok=missing.length===0&&empty.length===0&&findings.every(f=>f.severity!=="BLOCKER");
console.log(JSON.stringify({verifier,phase,state:ok?"PASS":"FAIL",ok,root,routes,files,missing,empty,findings,checkedAt:new Date().toISOString()},null,2));
process.exit(ok?0:1);
