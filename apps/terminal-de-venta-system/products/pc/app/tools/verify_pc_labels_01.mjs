#!/usr/bin/env node
import fs from "node:fs";import path from "node:path";import process from "node:process";
const args=process.argv.slice(2);const i=args.indexOf("--root");const root=path.resolve(i>=0&&args[i+1]?args[i+1]:process.cwd());
const files=["src/lib/i18n/messages/es.ts","src/composition/module-registry.ts","src/composition/navigation.ts","app/layout.tsx"];
const expected=["Panel administrativo de inventario","Catálogo","Existencias","Conteos","Compras","Recepción","Reabasto","Auditoría","Sincronización","Ajustes"];
const checked=[];const findings=[];
for(const rel of files){const abs=path.join(root,rel);const exists=fs.existsSync(abs);checked.push({rel,exists});if(!exists)findings.push({severity:"BLOCKER",code:"LABEL_FILE_MISSING",rel});}
const haystack=files.filter(rel=>fs.existsSync(path.join(root,rel))).map(rel=>fs.readFileSync(path.join(root,rel),"utf8")).join("\n");
for(const label of expected){if(!haystack.includes(label))findings.push({severity:"WARN",code:"EXPECTED_ESMX_LABEL_NOT_FOUND",label});}
const ok=findings.every(f=>f.severity!=="BLOCKER");
console.log(JSON.stringify({verifier:"pc_labels_es_mx_01",phase:"I01",state:ok?"PASS":"FAIL",ok,root,checked,findings,checkedAt:new Date().toISOString()},null,2));
process.exit(ok?0:1);
