#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const checks = [
  {
    id: "history_route",
    file: "app/api/pos/sales/history/route.ts",
    must: ["HISTORY_RANGE_TOO_LARGE", "readSalesHistoryInput", "getSalesHistorySummary"]
  },
  {
    id: "history_screen",
    file: "components/sales/sales-history-screen.tsx",
    must: ["preset", "custom", "60 días", "/api/pos/sales/history", "basePath=\"/sales/history\""]
  },
  {
    id: "history_detail_route",
    file: "app/sales/history/[saleId]/page.tsx",
    must: ["SalesTicketDetailScreen", "currentPath=\"/sales/history\"", "backHref=\"/sales/history\""]
  },
  {
    id: "ticket_id_guard",
    file: "components/sales/sales-ticket-list.tsx",
    must: ["ticket.saleId !== \"undefined\"", "basePath"]
  },
  {
    id: "cashier_diagnostics_locked",
    file: "components/sales/sales-ticket-detail-screen.tsx",
    must: ["Bloqueado para caja", "details", "No se muestran IDs internos"]
  },
  {
    id: "safe_reset_api",
    file: "app/api/pos/admin/sales-reset/route.ts",
    must: ["configure_security", "RESET_SECURITY_NOT_CONFIGURED", "destructiveAction", "preservesLicenseConfig"]
  },
  {
    id: "safe_reset_service",
    file: "src/server/pos-api/sales-reset.prisma.ts",
    must: ["TabletLocalSecuritySecret", "tablet.sales.reset", "support_reset", "local_support_outbox", "preservesLicenseConfig"]
  },
  {
    id: "safe_reset_ui",
    file: "components/settings/sales-reset-panel.tsx",
    must: ["Herramienta bloqueada", "Pregunta de seguridad", "PIN admin", "No toca licencia"]
  },
  ];

const results = checks.map((check) => {
  const abs = path.join(root, check.file);
  const text = fs.existsSync(abs) ? fs.readFileSync(abs, "utf8") : "";
  const missing = check.must.filter((needle) => !text.includes(needle));
  return { ...check, abs, exists: Boolean(text), missing, ok: text.length > 0 && missing.length === 0 };
});

const ok = results.every((item) => item.ok);
console.log(JSON.stringify({
  verifier: "verify_tablet_sales_history_reset_01",
  state: ok ? "PASS" : "FAIL",
  ok,
  results,
  checkedAt: new Date().toISOString()
}, null, 2));
process.exit(ok ? 0 : 1);
