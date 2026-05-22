import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (rel) => fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), "utf8") : "";
const failures = [];
const topics = ["supplier.created", "supplier.updated", "supplier.disabled", "product.supplier.linked", "product.supplier.unlinked", "product.supplier.updated"];
const files = {
  contract: "shared/contracts/sync-event-contract.v1.json",
  shared: "shared/twin-kernel/src/sync/events.ts",
  tabletEvents: "products/tablet/app/src/server/sync/events.ts",
  pcEvents: "products/pc/app/src/server/sync/events.ts",
  pcValidator: "products/pc/app/src/server/validators/sync-event-contract.ts",
  pcProjector: "products/pc/app/src/server/services/sync-projectors.service.ts",
  tabletConstants: "products/tablet/app/src/server/pos-engine/constants.ts",
  tabletMutations: "products/tablet/app/src/server/pos-api/supplier-mutations.prisma.ts",
  pcIngest: "products/pc/app/src/server/services/sync-ingest.service.ts"
};
for (const [label, rel] of Object.entries(files)) if (!read(rel)) failures.push(`${label} missing: ${rel}`);
for (const [label, rel] of Object.entries(files)) {
  const source = read(rel);
  if (!source || label === "pcIngest") continue;
  for (const topic of topics) if (!source.includes(topic)) failures.push(`${label} missing topic ${topic}`);
}
const ingest = read(files.pcIngest);
for (const token of ["pick(payload.productSupplierId)", "pick(payload.linkId)", "pick(payload.supplierId)", "validation.conflicts.some((item) => item.severity === \"rejected\")"]) {
  if (!ingest.includes(token)) failures.push(`pc ingest missing ${token}`);
}
const projector = read(files.pcProjector);
for (const token of ["function supplierPayload", "async function projectSupplier", "function productSupplierPayload", "async function projectProductSupplier", "tx.supplier.upsert", "tx.productSupplier.upsert", "PRODUCT_SUPPLIER_PRODUCT_MISSING", "SUPPLIER_NAME_COLLISION"]) {
  if (!projector.includes(token)) failures.push(`projector missing real logic token ${token}`);
}
const mutations = read(files.tabletMutations);
for (const token of ["createOutboxEvent", "createTabletSupplier", "updateTabletSupplier", "disableTabletSupplier", "linkTabletProductSupplier", "updateTabletProductSupplier", "unlinkTabletProductSupplier", "schemaVersion: POS_EVENT_SCHEMA_VERSION", "idempotencyKey"]) {
  if (!mutations.includes(token)) failures.push(`tablet mutation missing ${token}`);
}
for (const route of [
  "products/tablet/app/app/api/pos/suppliers/create/route.ts",
  "products/tablet/app/app/api/pos/suppliers/update/route.ts",
  "products/tablet/app/app/api/pos/suppliers/disable/route.ts",
  "products/tablet/app/app/api/pos/suppliers/product-link/link/route.ts",
  "products/tablet/app/app/api/pos/suppliers/product-link/update/route.ts",
  "products/tablet/app/app/api/pos/suppliers/product-link/unlink/route.ts"
]) if (!read(route).includes("supplierMutationErrorToResponse")) failures.push(`tablet route incomplete ${route}`);
if (failures.length) {
  console.error("SUPPLIER_PRODUCT_SUPPLIER_SYNC_CLOSURE failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}
console.log("SUPPLIER_PRODUCT_SUPPLIER_SYNC_CLOSURE passed");
console.log(JSON.stringify({ topics, checkedAt: new Date().toISOString() }, null, 2));
