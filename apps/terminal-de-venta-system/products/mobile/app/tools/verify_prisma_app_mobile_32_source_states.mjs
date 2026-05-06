#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const exists = (p) => fs.existsSync(path.join(root, p));
const fail = (message) => {
  console.error(JSON.stringify({ ok: false, verifier: "PRISMA_APP_MOBILE_32_SOURCE_STATES", message }, null, 2));
  process.exit(1);
};
const requireText = (file, snippets) => {
  if (!exists(file)) fail(`Missing file: ${file}`);
  const text = read(file);
  const missing = snippets.filter((snippet) => !text.includes(snippet));
  if (missing.length) fail(`${file} missing: ${missing.join(", ")}`);
  return text;
};

const pkg = JSON.parse(read("package.json"));
if (!pkg.scripts || pkg.scripts["verify:source-states"] !== "node tools/verify_prisma_app_mobile_32_source_states.mjs") {
  fail("package.json must expose verify:source-states.");
}
if (!String(pkg.scripts["check:all"] || "").includes("verify:source-states")) {
  fail("check:all must include verify:source-states.");
}

requireText("src/lib/prisma-app/mobile-data-plane/config.ts", [
  "PRISMA_MOBILE_TABLET_ORIGIN",
  "PRISMA_MOBILE_PC_ORIGIN",
  "PRISMA_MOBILE_SOURCE_TIMEOUT_MS",
  "requestTimeoutMs",
  "staleAfterMs"
]);
requireText("src/lib/prisma-app/mobile-data-plane/http.ts", [
  "timeout",
  "http_error",
  "parse_error",
  "network_error",
  "fetchJsonWithRetry"
]);
requireText("src/lib/prisma-app/mobile-data-plane/state-loader.ts", [
  "tabletSalesToday",
  "tabletLowStock",
  "tabletOutbox",
  "pcDashboard",
  "tabletHealth",
  "pcHealth",
  "runtimeMode"
]);
requireText("src/lib/prisma-app/mobile-data-plane/data-readiness.ts", [
  "ready",
  "partial",
  "empty",
  "offline",
  "blocked",
  "Tablet conectada",
  "PC sin respuesta",
  "sourceSummary",
  "actions"
]);
requireText("src/lib/prisma-app/prisma-mobile-api-client.ts", [
  "loadSnapshotEndpoint",
  "loadParallelEndpoints",
  "readCachedPrismaMobileSnapshot",
  "local-cache",
  "No se pudo cargar PRISMA App con fuentes conectadas"
]);
requireText("src/components/prisma-app/PrismaMobileDashboard.tsx", [
  "data-prisma-readiness",
  "data-prisma-source",
  "data-prisma-stale",
  "data-prisma-state=\"error\"",
  "onClearCache"
]);

const scenariosPath = "docs/prisma-app/qa/prisma-app-mobile-32-source-state-runtime-scenarios.json";
if (!exists(scenariosPath)) fail(`Missing ${scenariosPath}`);
const scenarios = JSON.parse(read(scenariosPath));
const ids = new Set((scenarios.states || []).map((s) => s.id));
for (const id of [
  "pc_tablet_online_ready",
  "tablet_only_partial",
  "pc_only_blocked_for_sales",
  "offline_with_cache_stale",
  "offline_no_cache_error",
  "timeout_normalized_error"
]) {
  if (!ids.has(id)) fail(`Missing scenario: ${id}`);
}

console.log(JSON.stringify({
  ok: true,
  verifier: "PRISMA_APP_MOBILE_32_SOURCE_STATES",
  scenarios: scenarios.states.length,
  checkAllContainsSourceStates: true
}, null, 2));
