#!/usr/bin/env node
import fs from "node:fs";import path from "node:path";import process from "node:process";import http from "node:http";import https from "node:https";
const args=process.argv.slice(2);function val(flag,fallback){const i=args.indexOf(flag);return i>=0&&args[i+1]?args[i+1]:fallback;}
const mode=val("--mode","source");const root=path.resolve(val("--root",process.cwd()));const baseUrl=val("--base-url","http://127.0.0.1:3130").replace(/\/$/,"");
const routes=["/","/dashboard","/catalog","/stock","/counts","/purchasing","/receiving","/replenishment","/audit","/sync","/settings"];
function page(route){return route==="/"?"app/page.tsx":`app${route}/page.tsx`;}
function source(){return routes.map(route=>{const rel=page(route);const abs=path.join(root,rel);if(!fs.existsSync(abs))return {route,rel,status:"FAIL",reason:"page file missing"};const text=fs.readFileSync(abs,"utf8");const render=/export\s+default\s+(async\s+)?function|redirect\(/.test(text);return {route,rel,status:render?"PASS":"FAIL",reason:render?"route source has default export or redirect":"missing route export"};});}
function req(route){return new Promise(resolve=>{const url=new URL(route,baseUrl);const client=url.protocol==="https:"?https:http;const r=client.get(url,{timeout:12000},res=>{let body="";res.setEncoding("utf8");res.on("data",c=>body+=c.slice(0,500));res.on("end",()=>resolve({route,url:String(url),statusCode:res.statusCode,ok:res.statusCode>=200&&res.statusCode<400,bodySample:body.slice(0,300)}));});r.on("timeout",()=>r.destroy(new Error("timeout")));r.on("error",e=>resolve({route,url:String(url),statusCode:null,ok:false,error:String(e.message??e)}));});}
const results=mode==="http"?await Promise.all(routes.slice(0,6).map(req)):source();const ok=results.every(x=>x.ok===true||x.status==="PASS");
console.log(JSON.stringify({smoke:"pc_i01_routes",mode,state:ok?"PASS":"FAIL",ok,root,baseUrl,results,checkedAt:new Date().toISOString()},null,2));process.exit(ok?0:1);
