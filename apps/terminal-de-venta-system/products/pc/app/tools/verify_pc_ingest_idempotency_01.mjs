import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const servicePath = path.join(root, "src/server/services/sync-ingest.service.ts");
const projectorPath = path.join(root, "src/server/services/sync-projectors.service.ts");
const failures = [];
const read = (file) => fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
const service = read(servicePath);
const projector = read(projectorPath);

for (const token of ["findExistingEvent", "duplicateResult", "idempotencyKey", "idempotencyKey aparece repetido", "persistRejected", "persistConflict", "persistAndProjectEvent"]) {
  if (!service.includes(token)) failures.push(`sync ingest missing token: ${token}`);
}
for (const token of ["recognized_not_projected", "RECOGNIZED_NOT_PROJECTED", "sale.completed", "stock.decremented", "cash.session.opened", "inventory.low_stock_detected"]) {
  if (!projector.includes(token)) failures.push(`projector missing token: ${token}`);
}
if (projector.includes('status: "dead_letter"') && projector.includes("UNSUPPORTED_PROJECTOR")) failures.push("unsupported recognized topics still dead-letter silently");

if (failures.length) {
  console.error("PRISMA_PC_INGEST_IDEMPOTENCY_01 failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("PRISMA_PC_INGEST_IDEMPOTENCY_01 passed");
