import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const read = (rel) => fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), "utf8") : "";
const failures = [];
const projector = read("src/server/services/sync-projectors.service.ts");
for (const token of [
  "async function projectSupplier",
  "async function projectProductSupplier",
  "tx.supplier.upsert",
  "tx.productSupplier.upsert",
  "tx.productSupplier.updateMany",
  "supplier.created",
  "supplier.updated",
  "supplier.disabled",
  "product.supplier.linked",
  "product.supplier.unlinked",
  "product.supplier.updated",
  "PRODUCT_SUPPLIER_ALREADY_UNLINKED",
  "touchedModels: [\"ProductSupplier\", \"Product\", \"Supplier\"]"
]) if (!projector.includes(token)) failures.push(`projector missing ${token}`);
if (failures.length) { console.error("SUPPLIER_PROJECTORS failed"); console.error(JSON.stringify({ failures }, null, 2)); process.exit(1); }
console.log("SUPPLIER_PROJECTORS passed");
