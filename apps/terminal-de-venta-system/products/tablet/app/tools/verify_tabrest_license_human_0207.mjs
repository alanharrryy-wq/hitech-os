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

const card = read("components/license/license-status-card.tsx");
const refresh = read("components/license/license-refresh-panel.tsx");

check("license card is readonly", card.includes('data-prisma-client-license-view="readonly"'));
check("refresh panel is readonly", refresh.includes('data-prisma-license-refresh-view="readonly"'));
check("license support detail remains collapsed", card.includes("<details className={styles.evidenceDisclosure}>"));
check("feature groups remain collapsed", card.includes("<details key={category} className={styles.featureGroup}>"));
check("refresh copy is human", !refresh.includes("Refresh remoto") && refresh.includes("Actualización no configurada"));
check("sync/outbox labels are translated", !card.includes("Sincronización y respaldos") && card.includes("Pendientes y respaldos"));
check("no license action buttons are exposed", !card.includes("<button") && !refresh.includes("<button"));
check("no activation/import workflow component appears", !card.includes("onClick") && !refresh.includes("onClick"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_LICENSE_HUMAN_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_LICENSE_HUMAN_0207 PASS ${checks.length} checks`);
