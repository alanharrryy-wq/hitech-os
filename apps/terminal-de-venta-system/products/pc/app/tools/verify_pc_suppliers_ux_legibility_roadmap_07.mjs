import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? process.cwd();
const checks = [];
function check(name, condition) {
  checks.push({ name, condition });
  if (!condition) {
    console.error(`FAIL ${name}`);
    process.exitCode = 1;
  } else {
    console.log(`OK ${name}`);
  }
}
function read(rel) {
  const full = join(root, rel);
  if (!existsSync(full)) throw new Error(`Missing ${rel}`);
  return readFileSync(full, "utf8");
}

const workbench = read("components/suppliers/smart-purchase-workbench.tsx");
const css = read("app/suppliers.css");

check("v07 marker", workbench.includes("supplier-readable-v07"));
check("gold reason callout", workbench.includes("¿POR QUÉ PRISMA LO RECOMIENDA?") && css.includes("reason-callout-v07"));
check("product rows separated", workbench.includes("product-line-v07") && css.includes("product-lines-head-v07"));
check("trust checklist", workbench.includes("trust-checklist-v07") && css.includes("trust-card-v07"));
check("calendar timeline", workbench.includes("calendar-timeline-v07") && css.includes("calendar-day-v07"));
check("audit roadmap", workbench.includes("audit-roadmap-v07") && css.includes("audit-step-v07"));
check("no visible api routes", !workbench.includes("POST /api") && !workbench.includes("/api/proveedores"));
check("no raw blocked label in visible strings", !workbench.includes('"Bloqueada"') && !workbench.includes('"Compra bloqueada"'));
check("no raw order cutoff visible", !workbench.includes("order_cutoff") && !workbench.includes("expected_receiving") && !workbench.includes("payment_due"));
check("no translated import path", !workbench.includes("sincronización/module.manifest"));

if (process.exitCode) {
  console.error(`NODE BLOCKED suppliers ux roadmap v07 ${checks.length} checks`);
  process.exit(process.exitCode);
}
console.log(`NODE READY suppliers ux roadmap v07 ${checks.length} checks`);
