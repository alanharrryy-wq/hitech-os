import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const adapterPath = path.join(root, "src/lib/prisma-app/mobile-data-plane/outbox-adapter.ts");
const text = fs.existsSync(adapterPath) ? fs.readFileSync(adapterPath, "utf8") : "";
const failures = [];

if (!text) failures.push("missing mobile outbox adapter");
if (text.includes('status === "sent"') || text.includes('status === "synced"')) failures.push("Mobile adapter counts sent/synced as acknowledged; fake green risk");
if (text.includes('["acked", "sent", "ackedCount"]')) failures.push("Mobile summary accepts sent alias as acked");
if (!text.includes('status === "acked"')) failures.push("Mobile adapter no longer detects acked state explicitly");

if (failures.length) {
  console.error("PRISMA_MOBILE_SYNC_VISIBILITY_01 failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_MOBILE_SYNC_VISIBILITY_01 passed");
