#!/usr/bin/env node
import {existsSync,readFileSync} from "node:fs";import {join,resolve} from "node:path";const root=resolve(process.cwd());const req=JSON.parse(process.argv[2]||"[]");const miss=req.filter(r=>!existsSync(join(root,r)));console.log(JSON.stringify({ok:miss.length===0,missing:miss},null,2));if(miss.length)process.exit(1);
