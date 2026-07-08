#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const terminalRoot = path.resolve(appRoot, "..", "..", "..");

const failures = [];
function read(root, rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}
function mustInclude(root, rel, needle) {
  const text = read(root, rel);
  if (!text.includes(needle)) failures.push(`missing ${needle} in ${path.join(root, rel)}`);
}
function mustNotOperatorCopy(root, rel, pattern, label) {
  const text = read(root, rel);
  if (pattern.test(text)) failures.push(`operator-copy ${label} remains in ${path.join(root, rel)}`);
}

mustInclude(appRoot, "app/api/pos/sales/complete/route.ts", "ticketEvidence");
mustInclude(appRoot, "app/api/pos/sales/complete/route.ts", "canonicalTicketId: sale.saleId");
mustInclude(appRoot, "app/api/pos/sales/complete/route.ts", "guardTabletFeatureForApi(\"pos.sale.complete\")");
mustInclude(appRoot, "app/api/pos/products/search/route.ts", "guardTabletFeatureForApi(\"pos.product.search\")");
mustInclude(appRoot, "app/api/pos/products/resolve/route.ts", "guardTabletFeatureForApi(\"pos.product.search\")");
mustInclude(appRoot, "src/server/pos-api/sales-detail.prisma.ts", "SALE_AS_TICKET_EVIDENCE_V1");
mustInclude(appRoot, "src/server/pos-api/sales-detail.prisma.ts", "outboxEvidenceForSale");
mustInclude(appRoot, "components/sales/sales-ticket-detail-screen.tsx", "Reintentar lectura");
mustInclude(appRoot, "components/sales/sales-ticket-list.tsx", "encodeURIComponent(ticket.saleId)");

mustInclude(terminalRoot, "shared/licensing/license-governor.ts", "getLicenseGovernorSnapshot");
mustInclude(terminalRoot, "shared/licensing/license-types.ts", "LicenseAssignmentState");
mustInclude(terminalRoot, "shared/licensing/license-types.ts", "operationalDecision");
mustInclude(terminalRoot, "shared/licensing/license-refresh-state.ts", "refresh_disabled");
mustInclude(terminalRoot, "shared/licensing/license-refresh-client.ts", "La operación local continúa si la licencia local es válida");
mustInclude(appRoot, "src/lib/tablet-runtime-snapshot/shell-contract.ts", "TabletRuntimeLicense");
mustInclude(appRoot, "src/server/tablet-runtime-snapshot/build.ts", "getTabletLicenseGovernor");
mustInclude(appRoot, "src/lib/operational-gate/can-sell.ts", "LICENSE_BLOCKED");
mustInclude(appRoot, "app/api/license/status/route.ts", "getTabletLicenseGovernor");
mustInclude(appRoot, "components/license/license-status-card.tsx", "Equipo no asignado");
mustInclude(appRoot, "components/license/license-refresh-panel.tsx", "Refresh remoto no configurado");

const operatorFiles = [
  "components/license/license-status-card.tsx",
  "components/license/license-refresh-panel.tsx",
  "components/sales/sales-ticket-detail-screen.tsx",
  "components/pos/pos-sale-success.tsx",
  "components/pos/pos-screen.tsx",
  "components/pos/pos-live-binding.tsx",
  "app/visual-os/realtime/PrismaRealtimeBridgeClient.tsx",
  "src/lib/pos/pos-visible-errors.ts"
];

for (const rel of operatorFiles) {
  mustNotOperatorCopy(appRoot, rel, /sin receta/i, "sin receta");
  mustNotOperatorCopy(appRoot, rel, /OOT Live/i, "OOT Live");
  mustNotOperatorCopy(appRoot, rel, /ROOT Live/i, "ROOT Live");
  mustNotOperatorCopy(appRoot, rel, /BOOT Live/i, "BOOT Live");
}

if (failures.length) {
  console.error("FAIL PRISMA_TABLET_TICKET_LICENSE_BUNDLE_01");
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log("PASS PRISMA_TABLET_TICKET_LICENSE_BUNDLE_01");
console.log("Ticket evidence uses Sale-as-ticket; Tablet POS is guarded by license governor across runtime, lookup, resolve and sale completion.");