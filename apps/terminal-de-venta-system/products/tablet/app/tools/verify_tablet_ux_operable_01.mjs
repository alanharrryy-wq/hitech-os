import fs from "node:fs";
import path from "node:path";

const appRoot = path.resolve(process.cwd());
const required = [
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/tablet-shell/prisma-tablet-shell.module.css",
  "components/tablet-shell/tablet-nav.ts",
  "src/lib/i18n/tablet-visible-labels.ts",
  "docs/qa/ux-operable-01/acceptance.md",
  "docs/qa/ux-operable-01/visual-checklist.md"
];
const visibleFiles = [
  "app/page.tsx",
  "app/pos/page.tsx",
  "app/checkout/page.tsx",
  "app/catalog/page.tsx",
  "app/returns/page.tsx",
  "app/sales/page.tsx",
  "app/sales/today/page.tsx",
  "app/stock/page.tsx",
  "app/shift/page.tsx",
  "app/sync/page.tsx",
  "app/events/outbox/page.tsx",
  "app/settings/export/page.tsx",
  "components/tablet-pos/touch-pos-ui.tsx",
  "components/prisma-dark-pos/prisma-route-ui.tsx",
  "src/lib/i18n/messages/es.ts"
];
const banned = [/Dark POS/i, /SaleReturn/i, /amountCents/i, /Guardrails/i, /Lookup/i, /Restock/i, /\bStock\b/g, /\bSync\b/g, /\bRuntime\b/g, /\bOutbox\b/g];
function read(rel) { return fs.readFileSync(path.join(appRoot, rel), "utf8"); }
function extractLikelyVisibleStrings(source) {
  const matches = [];
  const re = /(["'`])((?:\\.|(?!\1)[\s\S])*?)\1/g;
  let match;
  while ((match = re.exec(source))) {
    const value = match[2];
    if (!value.trim()) continue;
    if (value.startsWith("/") || value.includes("@/") || value.includes("@components") || value.includes("api/")) continue;
    if (/^[a-z0-9_./:-]+$/i.test(value) && !/\s/.test(value)) continue;
    matches.push(value);
  }
  return matches;
}
const failures = [];
for (const rel of required) {
  if (!fs.existsSync(path.join(appRoot, rel))) failures.push(`Falta archivo requerido: ${rel}`);
}
for (const rel of visibleFiles) {
  const abs = path.join(appRoot, rel);
  if (!fs.existsSync(abs)) continue;
  for (const value of extractLikelyVisibleStrings(read(rel))) {
    for (const pattern of banned) {
      pattern.lastIndex = 0;
      if (pattern.test(value)) failures.push(`Texto técnico visible en ${rel}: ${value}`);
    }
  }
}
const navSource = read("components/tablet-shell/tablet-nav.ts");
for (const label of ["Vender", "Cobro", "Catálogo", "Ventas de hoy", "Existencias", "Devoluciones", "Turno", "Sincronización", "Exportar"]) {
  if (!navSource.includes(label)) failures.push(`Falta label de navegación: ${label}`);
}
if (failures.length) {
  console.error("UX Operable 01: BLOCKED");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("UX Operable 01: PASS");
console.log(`Revisados ${visibleFiles.length} archivos visibles y ${required.length} archivos requeridos.`);
