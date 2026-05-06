import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] || process.cwd();
const checks = [];
function ok(name) { checks.push(name); console.log(`OK ${name}`); }
function fail(name) { console.error(`FAIL ${name}`); process.exit(1); }
function read(rel) {
  const path = join(root, rel);
  if (!existsSync(path)) fail(`missing ${rel}`);
  return readFileSync(path, "utf8");
}

const bridge = read("src/lib/suppliers/inventory-bridge.ts");
if (!bridge.includes("loadSupplierInventoryBridge")) fail("inventory bridge loader missing");
ok("inventory bridge loader");
if (!bridge.includes("prisma.stockSnapshot.findMany")) fail("stock snapshot query missing");
ok("stock snapshot query");
if (!bridge.includes("replenishmentSignal.findMany")) fail("replenishment signal query missing");
ok("replenishment signal query");
if (!bridge.includes("datos_de_proveedores")) fail("fallback source missing");
ok("fallback source declared");

const server = read("src/lib/suppliers/server.ts");
if (!server.includes("mergeSupplierProductLinksWithInventory")) fail("server does not merge inventory into supplier links");
ok("server merges inventory");
if (!server.includes("getSupplierInventoryBridgeSnapshot")) fail("server endpoint helper missing");
ok("server inventory helper");

const page = read("app/proveedores/page.tsx");
if (!page.includes("inventoryBridge={snapshot.inventoryBridge}")) fail("page does not pass inventory bridge");
ok("page passes inventory bridge");

const workbench = read("components/suppliers/smart-purchase-workbench.tsx");
if (!workbench.includes("Inventario conectado")) fail("visible inventory section missing");
ok("visible inventory section");
if (!workbench.includes("inventory-item-card-v11")) fail("inventory cards missing");
ok("inventory cards");
for (const bad of ["POST /api", "/api/proveedores", "order_cutoff", "payment_due", "expected_receiving", "backoffice", "ingest"]) {
  if (workbench.includes(bad)) fail(`visible technical residue ${bad}`);
}
ok("no visible technical residue in workbench");

const css = read("app/suppliers-ux-v08.css");
if (!css.includes("inventory-bridge-v11")) fail("inventory CSS missing");
ok("inventory CSS");

const route = read("app/api/proveedores/inventario/route.ts");
if (!route.includes("getSupplierInventoryBridgeSnapshot")) fail("inventory API route not wired");
ok("inventory API route");

console.log(`NODE READY suppliers inventory bridge v11 ${checks.length} checks`);
