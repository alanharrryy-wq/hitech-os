#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["app/stock/page.tsx", "app/counts/page.tsx", "app/audit/page.tsx", "src/server/validators/inventory-integrity.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'stock_counts_audit_03',routes:["/stock", "/counts", "/audit"],ok},null,2)); process.exit(ok?0:1);
