#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
const args=process.argv.slice(2);
const i=args.indexOf("--root");
const root=path.resolve(i>=0&&args[i+1]?args[i+1]:process.cwd());
const verifier="pc_runtime_governance_gates_01";
const phase="I01";
const required=["src/lib/core/product-identity.ts", "src/lib/core/route-contracts.ts", "src/composition/navigation.ts", "app/layout.tsx", "app/page.tsx"];
const routes=["/", "/catalog", "/stock", "/counts", "/purchasing", "/receiving", "/replenishment", "/audit", "/sync", "/settings"];
const files=required.map(rel=>{const abs=path.join(root,rel);const exists=fs.existsSync(abs);const size=exists?fs.statSync(abs).size:0;return {rel,exists,size};});
const missing=files.filter(x=>!x.exists).map(x=>x.rel);
const empty=files.filter(x=>x.exists&&x.size<=0).map(x=>x.rel);
const findings=[];
function read(rel){return fs.readFileSync(path.join(root,rel),"utf8");}
try{const identity=read("src/lib/core/product-identity.ts");if(!identity.includes("Panel administrativo de inventario"))findings.push({severity:"BLOCKER",code:"PC_IDENTITY_MISSING"});const layout=read("app/layout.tsx");if(!identity.includes("pc-backoffice")&&!identity.includes("backoffice")&&!layout.includes("pc-backoffice"))findings.push({severity:"BLOCKER",code:"PC_ROLE_MISSING"});const rc=read("src/lib/core/route-contracts.ts");for(const route of routes){if(route!=="/dashboard"&&!rc.includes(`"${route}"`))findings.push({severity:"BLOCKER",code:"ROUTE_CONTRACT_GAP",route});}if(!layout.includes("es-MX"))findings.push({severity:"BLOCKER",code:"LOCALE_MISSING"});}catch(e){findings.push({severity:"BLOCKER",code:"RUNTIME_READ_ERROR",message:String(e?.message??e)});}
const ok=missing.length===0&&empty.length===0&&findings.every(f=>f.severity!=="BLOCKER");
console.log(JSON.stringify({verifier,phase,state:ok?"PASS":"FAIL",ok,root,routes,files,missing,empty,findings,checkedAt:new Date().toISOString()},null,2));
process.exit(ok?0:1);
