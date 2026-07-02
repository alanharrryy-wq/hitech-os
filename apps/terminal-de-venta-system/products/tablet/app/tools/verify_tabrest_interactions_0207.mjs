#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const appRoot = fs.existsSync(path.join(cwd, "package.json")) && fs.existsSync(path.join(cwd, "components"))
  ? cwd
  : path.join(cwd, "apps", "terminal-de-venta-system", "products", "tablet", "app");
const checks = [];

function read(rel) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    checks.push({ name: `exists ${rel}`, ok: false });
    return "";
  }
  checks.push({ name: `exists ${rel}`, ok: true });
  return fs.readFileSync(file, "utf8");
}

function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail });
}

const home = read("components/tablet-home/tablet-home-screen.tsx");
const shift = read("components/shift/shift-cash-closure-screen.tsx");
const shiftCss = read("components/shift/shift-cash-closure.module.css");
const reports = read("components/reports/contextual-export-actions.tsx");
const offline = read("components/offline/offline-export-audit-screen.tsx");
const sync = read("components/sync/pending-offline-sync-panel-screen.tsx");
const salesDetail = read("components/sales/sales-ticket-detail-screen.tsx");

check("home removed runtime panel interaction", !home.includes("TabletRuntimePanel"));
check("home quick cards stay limited", (home.match(/title:/g) ?? []).length <= 8);
check("shift marks active panel by state", shift.includes('data-current={canOpen ? "true" : "false"}') && shift.includes('data-current={closePanelActive ? "true" : "false"}'));
check("shift inactive panel style exists", shiftCss.includes('.panel[data-current="false"]') && shiftCss.includes('.panel[data-current="true"]'));
check("contextual export opens by user action", reports.includes("<details") && reports.includes("<summary"));
check("offline export and support open by user action", (offline.match(/<details/g) ?? []).length >= 2);
check("sync secondary sections open by user action", (sync.match(/<details className={styles.supportDetails}>/g) ?? []).length >= 3);
check("sales ticket diagnostic is human-labelled", salesDetail.includes("Detalle para revisión") && !salesDetail.includes("Evidencia técnica"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_INTERACTIONS_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_INTERACTIONS_0207 PASS ${checks.length} checks`);
