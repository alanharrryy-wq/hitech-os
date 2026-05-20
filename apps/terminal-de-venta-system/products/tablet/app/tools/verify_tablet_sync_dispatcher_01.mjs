import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const dispatcherPath = path.join(root, "src/server/sync/dispatcher.ts");
const pcOriginPath = path.join(root, "src/server/sync/pc-origin.ts");
const schemaPath = path.join(root, "prisma/schema.prisma");
const dispatchRoutePath = path.join(root, "app/api/pos/sync/dispatch/route.ts");
const healthRoutePath = path.join(root, "app/api/pos/sync/health/pc/route.ts");

const failures = [];
function mustExist(file) { if (!fs.existsSync(file)) failures.push(`missing file: ${path.relative(root, file)}`); }
function read(file) { return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : ""; }
function mustContain(label, text, token) { if (!text.includes(token)) failures.push(`${label} missing token: ${token}`); }

[dispatcherPath, pcOriginPath, schemaPath, dispatchRoutePath, healthRoutePath].forEach(mustExist);
const dispatcher = read(dispatcherPath);
const pcOrigin = read(pcOriginPath);
const schema = read(schemaPath);

for (const token of ["dispatchTabletOutboxOnce", "loadPendingEvents", "nextRetryAt", "lastAttemptAt", "remoteLedgerId", "remoteLifecycleStatus", "remoteDiagnosticsJson", "backoffDate", "inFlight"]) {
  mustContain("dispatcher", dispatcher, token);
}
for (const token of ["PRISMA_TABLET_PC_SYNC_ENABLED", "PRISMA_TABLET_PC_ORIGIN", "PRISMA_TABLET_SYNC_AUTODISPATCH", "sanitizePcOrigin", "checkPrismaPcHealth"]) {
  mustContain("pc-origin", pcOrigin, token);
}
for (const token of ["lastAttemptAt", "nextRetryAt", "ackedAt", "remoteLedgerId", "remoteLifecycleStatus", "remoteDiagnosticsJson", "@@unique([businessId, idempotencyKey])"]) {
  mustContain("schema", schema, token);
}
if (!dispatcher.includes('result.status === "rejected"') || !dispatcher.includes('result.status === "conflict"')) failures.push("dispatcher does not explicitly handle rejected and conflict ACK results");
if (!dispatcher.includes('status: "acked"')) failures.push("dispatcher does not mark acked only after accepted remote lifecycle");
if (pcOrigin.includes('readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", true)')) failures.push("PC sync feature flag defaults on; it must default off");

if (failures.length) {
  console.error("PRISMA_TABLET_SYNC_DISPATCHER_01 failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_TABLET_SYNC_DISPATCHER_01 passed");
