#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const checks = [
  {
    id: "navigation_groups",
    file: "src/composition/navigation.ts",
    must: ["Sales Control", "Devices", "Runtime", "Settings", "searchKeywords"]
  },
  {
    id: "shell_search",
    file: "components/layout/app-shell.tsx",
    must: ["action=\"/sales-control\"", "Buscar folio", "groupedNavigation", "Tablet opera independiente"]
  },
  {
    id: "command_service",
    file: "src/server/services/pc-command-center.service.ts",
    must: [
      "getPcSalesControl",
      "getPcCashSessions",
      "getPcDeviceFleet",
      "getPcSyncCommandCenter",
      "getPcDataQuality",
      "getPcLicenseRuntimeControl",
      "getPcTabletCommunication",
      "recordTabletGovernanceCommand",
      "MAX_CUSTOM_RANGE_DAYS"
    ]
  },
  {
    id: "command_page_component",
    file: "components/control/pc-command-center-page.tsx",
    must: ["Diagnostico admin sanitizado", "DataTable", "Tablet opera independiente"]
  },
  {
    id: "sales_route",
    file: "app/sales-control/page.tsx",
    must: ["getPcSalesControl", "PcCommandCenterPage"]
  },
  {
    id: "cash_route",
    file: "app/cash-sessions/page.tsx",
    must: ["getPcCashSessions", "PcCommandCenterPage"]
  },
  {
    id: "devices_route",
    file: "app/devices/page.tsx",
    must: ["getPcDeviceFleet", "PcCommandCenterPage"]
  },
  {
    id: "sync_route",
    file: "app/sync/page.tsx",
    must: ["getPcSyncCommandCenter", "PcCommandCenterPage"]
  },
  {
    id: "license_runtime_route",
    file: "app/license-runtime/page.tsx",
    must: ["getPcLicenseRuntimeControl", "PcCommandCenterPage"]
  },
  {
    id: "communication_route",
    file: "app/tablet-communication/page.tsx",
    must: ["getPcTabletCommunication", "PcCommandCenterPage"]
  },
  {
    id: "data_quality_route",
    file: "app/data-quality/page.tsx",
    must: ["getPcDataQuality", "PcCommandCenterPage"]
  },
  {
    id: "apis",
    file: "app/api/backoffice/tablet-communication/governance-command/route.ts",
    must: ["catalog.release", "license.refresh", "recordTabletGovernanceCommand"]
  },
  {
    id: "contract",
    file: "../../../shared/contracts/pc-tablet-governance-command.v1.json",
    must: ["safeToContinueSelling", "queued_for_pickup", "license.refresh"]
  },
  {
    id: "docs_status",
    file: "docs/PC_UIUX_300_STATUS_TABLE.md",
    must: ["PC-UIUX-001", "PC-UIUX-300", "DONE", "VERIFIED_EXISTING"]
  },
  {
    id: "no_downgrade_doc",
    file: "docs/PC_NO_DOWNGRADE_REVIEW.md",
    must: ["Tablet operates independently", "PC governs if present", "No fake success states"]
  }
];

const results = checks.map((check) => {
  const abs = path.resolve(root, check.file);
  const text = fs.existsSync(abs) ? fs.readFileSync(abs, "utf8") : "";
  const missing = check.must.filter((needle) => !text.includes(needle));
  return { ...check, abs, exists: Boolean(text), missing, ok: text.length > 0 && missing.length === 0 };
});

const ok = results.every((item) => item.ok);
console.log(JSON.stringify({
  verifier: "verify_pc_uiux_300_addendum",
  state: ok ? "PASS" : "FAIL",
  ok,
  results,
  checkedAt: new Date().toISOString()
}, null, 2));
process.exit(ok ? 0 : 1);
