#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["app/catalog/page.tsx", "src/modules/catalog/types.ts", "src/server/validators/catalog-quality.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'catalog_sku_barcode_02',routes:["/catalog"],ok},null,2)); process.exit(ok?0:1);
