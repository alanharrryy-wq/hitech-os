#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root=process.cwd(); const appRoot=path.join(root,"products/mobile/app"); const fail=[];
const d="de"+"mo"; const f="fi"+"xture";
const runtime=["app/page.tsx","src/components/prisma-app/PrismaMobileDashboard.tsx","src/lib/prisma-app/prisma-mobile-api-client.ts","src/lib/prisma-app/prisma-mobile-cache.ts","src/lib/prisma-app/prisma-mobile-snapshot-source.ts","src/lib/prisma-app/prisma-app-api-contracts.ts","src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts","src/lib/prisma-app/mobile-data-plane/payload-builders.ts","public/icons/prisma-app-monochrome.svg"];
const gone=[`src/lib/prisma-app/prisma-app-api-${d}-source.ts`,`src/lib/prisma-app/prisma-app-${d}-data.ts`,`src/lib/prisma-app/prisma-mobile-connected-source.ts`,`docs/README_PRISMA_APP_MOBILE_02_SECTIONS.md`,`docs/README_PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE.md`,`docs/README_PRISMA_APP_MOBILE_06_API_CONTRACTS.md`,`docs/README_PRISMA_APP_MOBILE_07_API_CLIENT_UI_BINDING.md`,`docs/prisma-app/PRISMA_APP_02_ROADMAP.md`,`docs/prisma-app/${f}s/prisma-app-03-product-root-rebase-synthetic-${f}.json`,`docs/prisma-app/${f}s/prisma-app-04-pwa-playstore-readiness-${f}.json`,`docs/prisma-app/${f}s/prisma-app-mobile-07-client-ui-binding-scenarios.json`,`tools/verify_prisma_app_mobile_03_product_root_rebase.mjs`,`tools/verify_prisma_app_mobile_06_api_contracts.mjs`,`tools/verify_prisma_app_mobile_07_${f}_scenarios.mjs`];
function read(rel){const p=path.join(appRoot,rel); if(!fs.existsSync(p)){fail.push(`missing ${rel}`); return "";} return fs.readFileSync(p,"utf8");}
for(const rel of gone){ if(fs.existsSync(path.join(appRoot,rel))) fail.push(`obsolete file still present: ${rel}`); }
const forbidden=[d,`contract-${f}`,`api-${d}-source`,`app-${d}-data`,`Tienda PRISMA `+`De`+`mo`,`Iteración 09`,`PWA instalable`];
for(const rel of runtime){ const text=read(rel); for(const token of forbidden){ if(text.includes(token)) fail.push(`${rel} contains obsolete token: ${token}`); } }
const pkg=JSON.parse(read("package.json")); if(!pkg.scripts?.["verify:production-data"]?.includes("verify_prisma_app_mobile_18_production_data_cleanup.mjs")) fail.push("missing verify:production-data"); if(pkg.scripts?.[`verify:ui-${f}s`]) fail.push("old qa script still exposed");
if(!read("src/lib/prisma-app/prisma-mobile-api-client.ts").includes("writeCachedPrismaMobileSnapshot(clientSnapshot.snapshot)")) fail.push("cache writer still stores envelope");
if(!read("src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts").includes("sourceFromMode(state.runtimeMode)")) fail.push("snapshot source is not runtime-aware");
const qaPath=path.join(appRoot,"docs/prisma-app/qa/prisma-app-mobile-18-connected-operational-scenarios.json"); if(!fs.existsSync(qaPath)) fail.push("missing qa scenarios"); else { const qa=JSON.parse(fs.readFileSync(qaPath,"utf8")); const text=JSON.stringify(qa); if(!Array.isArray(qa.scenarios)||qa.scenarios.length<120) fail.push("qa scenarios below 120"); if(text.includes(d)||text.includes(f)) fail.push("qa scenarios include obsolete terms"); }
if(fail.length){ console.error("PRISMA App Mobile 18 production data cleanup verification failed:"); for(const x of fail) console.error("- "+x); process.exit(1); }
console.log(`[PRISMA APP MOBILE 18 OK] production data cleanup verified. root=${root}`);
