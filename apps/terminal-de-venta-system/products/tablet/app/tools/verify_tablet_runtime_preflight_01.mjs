#!/usr/bin/env node
import {existsSync,readFileSync} from "node:fs";const pkg=JSON.parse(readFileSync("package.json","utf8"));const req=["dev","typecheck","db:tablet:init"];const miss=req.filter(s=>!pkg.scripts?.[s]);console.log(JSON.stringify({ok:miss.length===0,node:process.version,missingScripts:miss},null,2));if(miss.length)process.exit(1);
