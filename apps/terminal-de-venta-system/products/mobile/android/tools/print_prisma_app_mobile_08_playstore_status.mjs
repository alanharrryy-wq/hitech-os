#!/usr/bin/env node
import fs from "node:fs"; import path from "node:path";
const root=process.cwd().endsWith(path.join("products","mobile","app"))?path.resolve(process.cwd(),"..",".."):process.cwd(); const c=JSON.parse(fs.readFileSync(path.join(root,"products/mobile/android/prisma-playstore.config.json"),"utf8"));
for(const [k,v,ok] of [["Package ID",c.packageId,!String(c.packageId).includes("REPLACE_WITH")],["Launch URL",c.launchUrl,!String(c.launchUrl).includes("REPLACE_WITH")],["Target SDK",String(c.targetSdkVersion),Number(c.targetSdkVersion)>=35],["Signing SHA-256",c.releaseSigningSha256,!String(c.releaseSigningSha256).includes("REPLACE_WITH")]]) console.log(`${ok?"OK":"BLOCKED"} ${k}: ${v}`);
