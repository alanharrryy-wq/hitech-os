#!/usr/bin/env node
const fs=require('fs'); const path=require('path'); const required=["app/sync/page.tsx", "app/api/sync/ingest/route.ts", "src/server/validators/sync-event-contract.ts"]; let ok=true;
for (const rel of required){ if(!fs.existsSync(path.join(process.cwd(),rel))){ console.error('MISSING',rel); ok=false;} else console.log('OK',rel); }
console.log(JSON.stringify({verifier:'sync_ingest_conflicts_release_06',routes:["/sync", "/api/sync/ingest"],ok},null,2)); process.exit(ok?0:1);
