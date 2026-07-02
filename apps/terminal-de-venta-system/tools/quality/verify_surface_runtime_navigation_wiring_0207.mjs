#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const repo = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const appRoot = path.join(repo, "apps", "terminal-de-venta-system");
const failures = [];

function read(rel) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    failures.push(`missing ${rel}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}
function mustInclude(rel, needle) {
  const text = read(rel);
  if (!text.includes(needle)) failures.push(`missing ${needle} in ${rel}`);
}
function mustNotIncludeInSegment(rel, startNeedle, endNeedle, forbidden) {
  const text = read(rel);
  const start = text.indexOf(startNeedle);
  const end = text.indexOf(endNeedle, start + startNeedle.length);
  const segment = start >= 0 && end > start ? text.slice(start, end) : text;
  if (segment.includes(forbidden)) failures.push(`forbidden ${forbidden} in ${rel} segment ${startNeedle}`);
}

const tabletNav = "products/tablet/app/src/composition/navigation.ts";
const pcNav = "products/pc/app/src/composition/navigation.ts";
const tabletContracts = "products/tablet/app/src/navigation/tablet-page-contracts.ts";
const pcProduct = "products/pc/app/src/uiux/pc-product-navigation.ts";

mustInclude(tabletNav, "TABLET_FINAL_NAVIGATION");
mustInclude(tabletNav, "getTabletSecondaryNavigationForPath");
mustInclude(tabletNav, "contract.finalMenu");
mustInclude(tabletContracts, "export const TABLET_FINAL_NAVIGATION");

mustInclude(pcNav, "PC_FINAL_NAVIGATION");
mustInclude(pcNav, "PC_PRODUCT_NAV_PRESENTATION");
mustInclude(pcNav, '"/glosario"');
mustInclude(pcNav, "Lecturas ejecutivas y señales de negocio");
mustInclude(pcProduct, "export const PC_FINAL_NAVIGATION");

mustNotIncludeInSegment(pcNav, "const PC_PRODUCT_NAV_PRESENTATION", "export const PC_PRIMARY_NAVIGATION", "Chart Lab");
mustNotIncludeInSegment(pcNav, "const PC_PRODUCT_NAV_PRESENTATION", "export const PC_PRIMARY_NAVIGATION", "/laboratorio-pc");
mustNotIncludeInSegment(pcNav, "const PC_PRODUCT_NAV_PRESENTATION", "export const PC_PRIMARY_NAVIGATION", "/referencia-visual");

const forbiddenMenuRoutes = [
  "/visual-os",
  "/release-gate",
  "/screen-standard-preview",
  "/prisma-dark-pos-reference",
  "/prisma-visual-catalog",
  "/laboratorio-pc",
  "/referencia-visual",
  "/prisma-insights/chart-lab",
  "/gobierno",
  "/filtros-avanzados",
  "/filtros-fecha"
];

const pcPrimarySegment = (() => {
  const text = read(pcNav);
  const start = text.indexOf("const PC_PRODUCT_NAV_PRESENTATION");
  const end = text.indexOf("// Compatibility tokens", start);
  return start >= 0 && end > start ? text.slice(start, end) : text;
})();

for (const route of forbiddenMenuRoutes) {
  if (pcPrimarySegment.includes(route)) failures.push(`forbidden final PC primary route ${route}`);
}

if (failures.length) {
  console.error("BLOCKED SURFACE_RUNTIME_NAVIGATION_WIRING_0207");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS SURFACE_RUNTIME_NAVIGATION_WIRING_0207");
console.log("Tablet composition and PC primary navigation now consume surface-cleanup product contracts while hiding lab/internal/reference routes from final navigation.");
