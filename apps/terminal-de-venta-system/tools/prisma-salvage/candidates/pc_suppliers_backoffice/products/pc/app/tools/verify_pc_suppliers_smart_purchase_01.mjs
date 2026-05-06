import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? process.cwd();
const required = [
  "app/proveedores/page.tsx",
  "app/api/proveedores/compra-inteligente/route.ts",
  "components/suppliers/smart-purchase-workbench.tsx",
  "src/lib/suppliers/types.ts",
  "src/lib/suppliers/fixtures.ts",
  "src/lib/suppliers/smart-purchase-engine.ts",
  "src/lib/suppliers/server.ts",
  "src/modules/suppliers/module.manifest.ts"
];

const missing = required.filter((rel) => !existsSync(join(root, rel)));
if (missing.length) {
  console.error("MISSING", missing.join("\n"));
  process.exit(1);
}

const registry = readFileSync(join(root, "src/composition/module-registry.ts"), "utf8");
const page = readFileSync(join(root, "app/proveedores/page.tsx"), "utf8");
const engine = readFileSync(join(root, "src/lib/suppliers/smart-purchase-engine.ts"), "utf8");
const component = readFileSync(join(root, "components/suppliers/smart-purchase-workbench.tsx"), "utf8");

const checks = [
  [registry.includes("SuppliersModule"), "registry includes SuppliersModule"],
  [page.includes("getSupplierDashboardSnapshot"), "page consumes supplier snapshot"],
  [engine.includes("simulatePurchase"), "engine exposes purchase simulation"],
  [engine.includes("buildSmartPurchaseOutput"), "engine exposes recommendation builder"],
  [component.includes("Compra Inteligente"), "UI contains visible Compra Inteligente"],
  [component.includes("Tablet vende"), "UI preserves Tablet boundary"],
  [component.includes("Crear pedido sugerido"), "UI connects recommendation to order action"]
];

const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  for (const [, label] of failed) console.error("FAILED", label);
  process.exit(1);
}

console.log("OK PRISMA PC Proveedores + Compra Inteligente package verified");
