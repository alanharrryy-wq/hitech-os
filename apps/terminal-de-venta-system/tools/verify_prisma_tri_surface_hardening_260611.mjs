import fs from "node:fs";
import path from "node:path";

const repo = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const checks = [];
function read(rel) {
  const full = path.join(repo, rel);
  return fs.existsSync(full) ? fs.readFileSync(full, "utf8") : null;
}
function check(name, ok, detail = {}) {
  checks.push({ name, ok: Boolean(ok), detail });
}

const requiredFiles = [
  "products/pc/app/app/api/backoffice/branches/route.ts",
  "products/pc/app/app/api/backoffice/inventory/route.ts",
  "products/pc/app/app/api/backoffice/purchases/route.ts",
  "products/pc/app/app/api/backoffice/suppliers/route.ts",
  "products/pc/app/app/api/backoffice/reorder/route.ts",
  "products/pc/app/app/api/proveedores/route.ts",
  "products/mobile/app/app/api/incidents/route.ts",
  "products/mobile/app/app/api/incidents/timeline/route.ts",
  "products/mobile/app/app/api/reports/route.ts",
  "products/tablet/app/app/api/backoffice/route.ts",
  "docs/ops/PRISMA_TRI_SURFACE_HARDENING_260611.md"
];
for (const rel of requiredFiles) check(`exists:${rel}`, fs.existsSync(path.join(repo, rel)), { rel });

const markerChecks = {
  "products/tablet/app/components/prisma-dark-pos/prisma-cart-panel.tsx": ["prisma:pos-cart-action", "data-prisma-hardening=\"cart-actions-260611\""],
  "products/tablet/app/components/prisma-dark-pos/prisma-category-rail.tsx": ["prisma:pos-category-action", "aria-pressed"],
  "products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-shell.tsx": ["prisma:pos-product-page", "aria-current"],
  "products/tablet/app/components/prisma-dark-pos/prisma-product-card.tsx": ["prisma:pos-product-action", "toggle-favorite"],
  "products/tablet/app/components/prisma-dark-pos/prisma-search-row.tsx": ["prisma:pos-search-action", "onKeyDown"],
  "products/tablet/app/components/prisma-dark-pos/prisma-top-action-bar.tsx": ["prisma:pos-top-action", "profile"],
  "products/tablet/app/app/prisma-pulse/PrismaTabletPulsePanel.tsx": ["tablet-pulse-filters-260611", "aria-pressed"],
  "products/pc/app/components/prisma-glass-capsule/prisma-glass-capsule.tsx": ["prisma:glass-action", "glass-actions-260611"],
  "products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx": ["pc-insights-filters-260611", "selectedFilters"],
  "products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx": ["mobile-command-filters-260611", "MOBILE_FILTERS"],
  "products/mobile/app/src/components/prisma-app/PrismaMobileCrystalCommand.tsx": ["mobile-inventory-ranking-260611", "mobile-timeline-actions-260611"],
  "products/mobile/app/src/lib/prisma-app/mobile-data-plane/endpoints.ts": ["preferExternal", "/api/mobile/alerts"]
};
for (const [rel, markers] of Object.entries(markerChecks)) {
  const text = read(rel);
  check(`markers:${rel}`, text && markers.every((marker) => text.includes(marker)), { rel, markers });
}

const unresolvedCritical = [
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/backoffice/inventory", "products/pc/app/app/api/backoffice/inventory/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/backoffice/purchases", "products/pc/app/app/api/backoffice/purchases/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/backoffice/suppliers", "products/pc/app/app/api/backoffice/suppliers/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/backoffice/reorder", "products/pc/app/app/api/backoffice/reorder/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/incidents", "products/mobile/app/app/api/incidents/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/incidents/timeline", "products/mobile/app/app/api/incidents/timeline/route.ts"],
  ["products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts", "/api/reports", "products/mobile/app/app/api/reports/route.ts"]
];
for (const [source, literal, route] of unresolvedCritical) {
  const sourceText = read(source);
  check(`route-contract:${literal}`, Boolean(sourceText?.includes(literal) && fs.existsSync(path.join(repo, route))), { source, route });
}

const failed = checks.filter((item) => !item.ok);
const result = {
  ok: failed.length === 0,
  generatedAt: new Date().toISOString(),
  repo,
  total: checks.length,
  failed: failed.length,
  checks
};
console.log(JSON.stringify(result, null, 2));
process.exit(failed.length === 0 ? 0 : 1);
