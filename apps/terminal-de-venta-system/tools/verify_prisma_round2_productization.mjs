#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const isWindows = process.platform === "win32";

const checks = [
  {
    id: "shared-sync-contract",
    cwd: root,
    bin: process.execPath,
    args: ["tools/verify_sync_contract_gate_01.mjs"],
    coverage: "Shared contract/event language remains coherent."
  },
  {
    id: "tablet-standalone-sale-core",
    cwd: path.join(root, "products/tablet/app"),
    bin: process.execPath,
    args: ["tools/verify_tablet_standalone_core_closeout_02.mjs"],
    coverage: "Tablet can sell locally, decrement stock, persist Sale/SaleLine/StockMovement, and leave outbox events without PC/Mobile."
  },
  {
    id: "tablet-catalog-stock-pos-routes",
    cwd: path.join(root, "products/tablet/app"),
    bin: process.execPath,
    args: ["tools/verify_tablet_catalog_stock_selling_assist_route_smokes_03j_03k.mjs", "--root", "."],
    coverage: "Tablet catalog, stock, and POS route smoke matrix is present."
  },
  {
    id: "tablet-offline-outbox-route",
    cwd: path.join(root, "products/tablet/app"),
    bin: process.execPath,
    args: ["tools/verify_tablet_pending_offline_sync_panel_route_smokes_03m.mjs", "--root", "."],
    coverage: "Tablet offline/outbox route smoke matrix is present."
  },
  {
    id: "tablet-shift-cash-return-audit-route",
    cwd: path.join(root, "products/tablet/app"),
    bin: process.execPath,
    args: ["tools/verify_tablet_shift_cash_closure_route_smokes_03l.mjs", "--root", "."],
    coverage: "Tablet shift/cash/closure route smoke matrix is present."
  },
  {
    id: "tablet-contextual-export-route",
    cwd: path.join(root, "products/tablet/app"),
    bin: process.execPath,
    args: ["tools/verify_tablet_contextual_export_reports_route_smokes_03n.mjs", "--root", "."],
    coverage: "Tablet contextual export reports route smoke matrix is present."
  },
  {
    id: "pc-backoffice-route-adder",
    cwd: path.join(root, "products/pc/app"),
    bin: process.execPath,
    args: ["tools/smoke_pc_i01_routes.mjs", "--mode", "source", "--root", "."],
    coverage: "PC backoffice/admin routes load as source-level adders."
  },
  {
    id: "mobile-supervisor-release-boundary",
    cwd: path.join(root, "products/mobile/app"),
    bin: "pnpm",
    args: ["run", "verify:release-hardening"],
    shell: isWindows,
    coverage: "Mobile remains a supervisor adder with light Dashboard and Premium Navigator ownership."
  }
];

function run(check) {
  const result = spawnSync(check.bin, check.args, {
    cwd: check.cwd,
    encoding: "utf8",
    shell: check.shell ?? false,
    env: {
      ...process.env,
      DATABASE_URL: process.env.DATABASE_URL ?? "file:./prisma-round2-local.db"
    }
  });
  return {
    id: check.id,
    coverage: check.coverage,
    cwd: check.cwd,
    command: [check.bin, ...check.args].join(" "),
    exitCode: typeof result.status === "number" ? result.status : 1,
    stdout: result.stdout?.trim() ?? "",
    stderr: result.stderr?.trim() ?? "",
    error: result.error?.message ?? null
  };
}

const results = checks.map(run);
const ok = results.every((item) => item.exitCode === 0);
const output = {
  status: ok ? "PASS" : "FAIL",
  verifier: "prisma_round2_productization",
  checkedAt: new Date().toISOString(),
  root,
  results
};

const outDir = path.join(root, "tools/codex/runs/prisma-round2-productization");
if (fs.existsSync(outDir)) {
  fs.writeFileSync(path.join(outDir, "round2_smoke_results.json"), JSON.stringify(output, null, 2) + "\n");
}

console.log(JSON.stringify(output, null, 2));
process.exit(ok ? 0 : 1);
