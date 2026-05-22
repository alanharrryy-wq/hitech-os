import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const read = (rel) => fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), "utf8") : "";
const failures = [];
const validator = read("src/server/validators/sync-event-contract.ts");
const events = read("src/server/sync/events.ts");
const topics = ["supplier.created", "supplier.updated", "supplier.disabled", "product.supplier.linked", "product.supplier.unlinked", "product.supplier.updated"];
for (const topic of topics) {
  if (!validator.includes(topic)) failures.push(`validator missing ${topic}`);
  if (!events.includes(topic)) failures.push(`PC sync events missing ${topic}`);
}
for (const token of ["supplier.* requires supplierId", "product.supplier.* requires productId and supplierId", "RECOGNIZED_SYNC_TOPICS", "SUPPORTED_SYNC_SCHEMA_VERSIONS"]) if (!validator.includes(token)) failures.push(`validator missing token ${token}`);
if (failures.length) { console.error("SUPPLIER_SYNC_CONTRACT failed"); console.error(JSON.stringify({ failures }, null, 2)); process.exit(1); }
console.log("SUPPLIER_SYNC_CONTRACT passed");
