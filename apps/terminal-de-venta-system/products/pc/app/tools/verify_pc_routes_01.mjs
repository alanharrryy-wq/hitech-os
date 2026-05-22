#!/usr/bin/env node
import fs from "node:fs";import path from "node:path";import process from "node:process";
const args=process.argv.slice(2);const i=args.indexOf("--root");const root=path.resolve(i>=0&&args[i+1]?args[i+1]:process.cwd());
const routes=["/","/dashboard","/sales-control","/cash-sessions","/catalog","/stock","/movements","/counts","/purchasing","/receiving","/replenishment","/proveedores","/audit","/sync","/devices","/tablet-communication","/license-runtime","/data-quality","/settings"];
function page(route){return route==="/"?"app/page.tsx":`app${route}/page.tsx`;}
const checked=routes.map(route=>{const rel=page(route);const abs=path.join(root,rel);const exists=fs.existsSync(abs);const size=exists?fs.statSync(abs).size:0;return {route,rel,exists,size};});
const missing=checked.filter(x=>!x.exists).map(x=>x.route);const empty=checked.filter(x=>x.exists&&x.size<=0).map(x=>x.route);const ok=missing.length===0&&empty.length===0;
console.log(JSON.stringify({verifier:"pc_routes_01",phase:"I01",state:ok?"PASS":"FAIL",ok,root,checked,missing,empty,checkedAt:new Date().toISOString()},null,2));
process.exit(ok?0:1);
