import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const dispatcher = fs.readFileSync(path.join(root, "products/tablet/app/src/server/sync/dispatcher.ts"), "utf8");
const schema = fs.readFileSync(path.join(root, "products/tablet/app/prisma/schema.prisma"), "utf8");
const failures = [];

for (const token of ["function isAck", "projected", "reconciled", "status: \"acked\"", "remoteLedgerId", "remoteLifecycleStatus", "ackedAt"]) {
  if (!dispatcher.includes(token) && !schema.includes(token)) failures.push(`ACK evidence missing token: ${token}`);
}
if (dispatcher.includes('status: "acked"') && !dispatcher.includes('projected') && !dispatcher.includes('reconciled')) failures.push("acked state is not tied to projected/reconciled lifecycle");
if (failures.length) {
  console.error("PRISMA_ACK_REQUIRED failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_ACK_REQUIRED passed");
