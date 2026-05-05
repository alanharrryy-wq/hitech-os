#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["app/purchasing/page.tsx", "app/receiving/page.tsx", "app/replenishment/page.tsx", "src/server/validators/procurement-integrity.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'purchasing_receiving_replenishment_04',routes:["/purchasing", "/receiving", "/replenishment"],ok},null,2)); process.exit(ok?0:1);
