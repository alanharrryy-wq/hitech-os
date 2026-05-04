import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
function exists(rel){ return fs.existsSync(path.join(root, rel)); }
function must(rel){ if(!exists(rel)) throw new Error(`Missing ${rel}`); }
function readJson(rel){ return JSON.parse(fs.readFileSync(path.join(root, rel), "utf8")); }
function versionAtLeast(actual, min){
  const a=String(actual).split(".").map(Number); const b=String(min).split(".").map(Number);
  for(let i=0;i<3;i++){ if((a[i]||0)>(b[i]||0)) return true; if((a[i]||0)<(b[i]||0)) return false; }
  return true;
}
const pkg=readJson("products/mobile/app/package.json");
if(!versionAtLeast(pkg.version, "0.7.0")) throw new Error(`unsupported package version: ${pkg.version}`);
for (const rel of [
  "products/mobile/app/app/api/mobile/snapshot/route.ts",
  "products/mobile/app/app/prisma-app/page.tsx",
  "products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx",
  "products/mobile/app/src/lib/prisma-app/prisma-mobile-api-client.ts",
  "products/mobile/app/src/lib/prisma-app/prisma-mobile-cache.ts",
  "products/mobile/app/src/lib/prisma-app/prisma-mobile-snapshot-contract.ts",
  "products/mobile/app/src/lib/prisma-app/prisma-mobile-snapshot-source.ts",
  "products/mobile/app/src/lib/prisma-app/prisma-mobile-view-model.ts"
]) must(rel);
console.log(`[UI BINDING OK] PRISMA_APP_MOBILE_07_API_CLIENT_UI_BINDING client, snapshot route, offline cache, and connected dashboard are installed. root=${root}`);
