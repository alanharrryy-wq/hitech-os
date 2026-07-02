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

const sync = read("components/sync/pending-offline-sync-panel-screen.tsx");
const shell = read("components/tablet-shell/prisma-tablet-shell.tsx");
const shellCss = read("components/tablet-shell/prisma-tablet-shell.module.css");
const touch = read("components/tablet-pos/touch-pos-ui.tsx");
const css = read("components/sync/pending-offline-sync-panel.module.css");
const kpiIndex = sync.indexOf("<section className={styles.kpis}>");
const accountDetailsIndex = sync.indexOf("<summary>Cuenta y equipos</summary>");
const catalogDetailsIndex = sync.indexOf("<summary>Actualizar catálogo</summary>");

check("sync headline uses pending language", sync.includes("Pendientes por enviar") && sync.includes("Pendientes al día"));
check("sync hero avoids support-tool phrasing", !sync.includes("herramientas de soporte"));
check("dispatch result uses pending language", sync.includes("pendiente(s) mandado(s)") && !sync.includes("evento(s) mandado"));
check("account context moved after pending KPIs", kpiIndex >= 0 && accountDetailsIndex > kpiIndex, `${kpiIndex} ${accountDetailsIndex}`);
check("catalog pull moved into secondary details", catalogDetailsIndex > kpiIndex && sync.includes("<CatalogPullPanel />"));
check("support details renamed", sync.includes("<summary>Detalle adicional</summary>"));
check("sync surface limits initial queue", sync.includes("QUEUE_PREVIEW_LIMIT = 8") && sync.includes("visibleItems.map"));
check("sync surface exposes show-all control", sync.includes("Ver todos") && sync.includes("setShowAll(false)"));
check("sync surface has per-action busy state", sync.includes('type ActionMode = "loading" | "refreshing" | "sending" | "retrying" | null') && sync.includes('actionMode === "sending"'));
check("sync surface announces dispatch status", sync.includes('aria-live="polite"') && sync.includes("activeStatusMessage"));
check("sync surface shows PC connection in hero", sync.includes("pcConnectionTone") && sync.includes("PC disponible") && sync.includes("heroMeta"));
check("sync dock is inline to avoid overlay", sync.includes('dockMode="inline"') && shell.includes('dockMode?: "sticky" | "inline"') && shellCss.includes(".bottomDockInline"));
check("sync partial dispatch is a visible warning", sync.includes('"partial"') && sync.includes("PC recibió") && sync.includes("respondió con avisos"));
check("legacy ACK copy removed from outbox route", !touch.includes("ACK") && touch.includes("Confirmados"));
check("legacy events copy removed from outbox route", !touch.includes("Eventos locales") && touch.includes("Movimientos guardados"));
check("sync details styling exists", css.includes(".supportDetails") && css.includes(".accountGrid"));
check("sync queue preview styling exists", css.includes(".queuePanel") && css.includes(".showMoreButton") && css.includes(".metaPill_ok"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_SYNC_HUMAN_PENDING_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_SYNC_HUMAN_PENDING_0207 PASS ${checks.length} checks`);
