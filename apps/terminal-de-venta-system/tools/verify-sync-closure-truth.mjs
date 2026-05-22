import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "products/tablet/app/src/server/sync/dispatcher.ts",
  "products/tablet/app/src/server/sync/pc-origin.ts",
  "products/tablet/app/app/api/pos/sync/dispatch/route.ts",
  "products/tablet/app/app/api/pos/sync/health/pc/route.ts",
  "products/tablet/app/tools/verify_tablet_sync_dispatcher_01.mjs",
  "products/pc/app/tools/verify_pc_ingest_idempotency_01.mjs",
  "products/mobile/app/tools/verify_mobile_sync_visibility_01.mjs",
  "tools/verify-ack-required.mjs",
  "tools/verify-no-fake-green.mjs",
  "docs/prisma/PRISMA_SYNC_CLOSURE_PATCH_20260518.md"
];
const failures = [];
for (const rel of required) if (!fs.existsSync(path.join(root, rel))) failures.push(`missing ${rel}`);
const pcOrigin = fs.existsSync(path.join(root, required[1])) ? fs.readFileSync(path.join(root, required[1]), "utf8") : "";
if (pcOrigin.includes('readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", true)')) failures.push("PC sync flag defaults on");
if (!pcOrigin.includes('readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", false)')) failures.push("PC sync flag default-off evidence missing");
if (failures.length) {
  console.error("PRISMA_SYNC_CLOSURE_TRUTH failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_SYNC_CLOSURE_TRUTH passed");
