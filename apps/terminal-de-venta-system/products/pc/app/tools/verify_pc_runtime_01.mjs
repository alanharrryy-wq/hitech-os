#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["src/lib/core/product-identity.ts", "src/lib/core/route-contracts.ts", "src/composition/navigation.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'runtime_governance_gates_01',routes:["/", "/catalog", "/stock", "/counts", "/purchasing", "/receiving", "/replenishment", "/audit", "/sync", "/settings"],ok},null,2)); process.exit(ok?0:1);
