import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, "..");
const repoRoot = path.resolve(appRoot, "../../../../..");
const tsxRel = "apps/terminal-de-venta-system/products/pc/app/components/inventory/inventory-workspace.tsx";
const cssRel = "apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css";
const read = (rel) => fs.readFileSync(path.join(repoRoot, rel), "utf8");
const tsx = read(tsxRel);
const css = read(cssRel);
const begin = "/* PRISMA_PC_STOCK_FICHA_TABLET_LICENSES_PILOT_V1_BEGIN */";
const end = "/* PRISMA_PC_STOCK_FICHA_TABLET_LICENSES_PILOT_V1_END */";
const checks = [];
const check = (name, ok, detail = "") => { checks.push({ name, ok, detail }); if (!ok) console.error(`FAIL ${name}: ${detail}`); };
const attrs = {
  "data-prisma-surface": "pc",
  "data-prisma-route": "/stock",
  "data-prisma-owner": "StockFicha",
  "data-prisma-region": "ZONE.pc.stock.detail",
  "data-prisma-slot": "SLOT.pc.stock.detail.primary",
  "data-prisma-component-ui-id": "PC-STOCK-FICHA-PANEL-01",
  "data-prisma-recipe": "REC.panel.operational.cloudglass",
  "data-prisma-visual-stack": "VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
  "data-prisma-binding": "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
  "data-prisma-adapter": "ADP.PC.DENSE.CLOUDGLASS.V1",
  "data-prisma-neutral-layer": "LYR.SURFACE.OPERATIONAL.DETAIL",
  "data-prisma-visual-pilot": "pc-stock-ficha-tablet-licenses-v1"
};
for (const [key, value] of Object.entries(attrs)) {
  const needle = `${key}="${value}"`;
  check(`${key} twice`, tsx.split(needle).length - 1 === 2, needle);
}
check("stock roots preserved", tsx.split('data-pcinv-product-ficha="stock"').length - 1 === 1 && tsx.split('data-pcinv-product-ficha="stock-empty"').length - 1 === 1);
check("CSS marker pair", css.includes(begin) && css.includes(end));
const block = css.slice(css.indexOf(begin), css.indexOf(end) + end.length);
check("no important", !block.includes("!important"));
check("exact scope", block.includes('.productFicha[data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1"]'));
check("real transparency", block.includes("rgba(") && block.includes("backdrop-filter"));
check("rows flattened", block.includes(".fichaRow") && block.includes("background: transparent"));
check("states", block.includes(":focus-within") && block.includes(":focus-visible") && block.includes("aria-disabled") && block.includes("prefers-reduced-motion"));
const changed = execFileSync("git", ["status", "--porcelain=v1", "-z", "--untracked-files=all"], { cwd: repoRoot, encoding: "utf8" })
  .split("\0").filter(Boolean)
  .map(record => record.slice(3).replaceAll("\\", "/"));
const allowed = new Set([
  tsxRel, cssRel,
  "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots/PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json",
  "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots/REC.panel.operational.cloudglass.pc-stock-ficha.v1.json",
  "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots/PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.coverage.json",
  "apps/terminal-de-venta-system/products/pc/app/tools/verify_pc_stock_ficha_tablet_licenses_visual_pilot.mjs",
  "apps/terminal-de-venta-system/products/pc/app/tools/verify_pc_stock_ficha_visual_layout_gate.mjs",
  "PRISMA Factory Ledger/addenda/PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.md"
]);
check("scope exact", changed.every(x => allowed.has(x)), changed.filter(x => !allowed.has(x)).join(", "));
check("no Tablet mutation", !changed.some(x => x.startsWith("apps/terminal-de-venta-system/products/tablet/")));
check("no Cobrar/RIFAT mutation", !changed.some(x => x.includes("pos.module.css") || x.includes("pos-ticket-panel") || x.startsWith("prisma-html/authority/rifat/")));
check("excluded metricas untouched", !changed.some(x => x.includes("metricas-dia")));
check("no dependencies", !changed.some(x => /(^|\/)package(-lock)?\.json$|pnpm-lock|yarn\.lock/.test(x)));
const failures = checks.filter(x => !x.ok);
const report = { schema: "prisma.pc-stock-ficha.validator.v1", status: failures.length ? "FAIL" : "PASS", checks, changed };
console.log(JSON.stringify(report, null, 2));
if (failures.length) process.exit(1);
