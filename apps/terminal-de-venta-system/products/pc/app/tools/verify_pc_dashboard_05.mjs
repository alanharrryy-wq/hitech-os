#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["app/dashboard/page.tsx", "app/page.tsx", "src/server/services/kpi-formulas.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'dashboard_kpi_alerts_05',routes:["/", "/dashboard"],ok},null,2)); process.exit(ok?0:1);
