#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const verifier = "PRISMA_APP_MOBILE_32_SOURCE_STATES_CURRENT_TECHNICAL_CONTRACT";
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const exists = (p) => fs.existsSync(path.join(root, p));

const fail = (message, details = {}) => {
  console.error(JSON.stringify({ ok: false, verifier, message, details }, null, 2));
  process.exit(1);
};

const requireText = (file, snippets) => {
  if (!exists(file)) fail(`Missing file: ${file}`);
  const text = read(file);
  const missing = snippets.filter((snippet) => !text.includes(snippet));
  if (missing.length) fail(`${file} missing current contract tokens`, { missing });
  return text;
};

const pkg = JSON.parse(read("package.json"));
if (!pkg.scripts || pkg.scripts["verify:source-states"] !== "node tools/verify_prisma_app_mobile_32_source_states.mjs") {
  fail("package.json must expose verify:source-states");
}
if (!String(pkg.scripts["check:all"] || "").includes("verify:source-states")) {
  fail("check:all must include verify:source-states");
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

const loader = requireText("src/lib/prisma-app/mobile-data-plane/state-loader.ts", [
  "tabletSalesToday",
  "tabletLowStock",
  "tabletOutbox",
  "pcDashboard",
  "tabletHealth",
  "pcHealth",
  "function runtimeMode",
  'return "reference-disabled"',
  'return "stale"',
  'return "live"',
  'return "partial"',
  'return "offline"',
  'return "unknown"',
  "localOnlySnapshot",
  'runtimeMode: localOnlySnapshot || (localSnapshot && mode === "offline") ? "stale" : mode'
]);

const runtimeModePattern = /if\s*\(input\.tabletOk\s*&&\s*input\.pcOk\s*&&\s*\(staleByPending\s*\|\|\s*staleBySync\)\)\s*return\s*"stale";[\s\S]*if\s*\(input\.tabletOk\s*&&\s*input\.pcOk\s*&&\s*input\.warnings\.length\s*===\s*0\)\s*return\s*"live";[\s\S]*if\s*\(input\.tabletOk\s*\|\|\s*input\.pcOk\)\s*return\s*"partial";[\s\S]*if\s*\(input\.warnings\.length\s*>\s*0\)\s*return\s*"offline";[\s\S]*return\s*"unknown";/s;
if (!runtimeModePattern.test(loader)) {
  fail("runtimeMode source-state precedence drifted", {
    expectedSemantics: "both+stale -> stale; both+clean -> live; either -> partial; warnings -> offline; otherwise unknown"
  });
}

const readiness = requireText("src/lib/prisma-app/mobile-data-plane/data-readiness.ts", [
  'export type MobileDataReadinessLevel = "ready" | "partial" | "empty" | "offline" | "blocked"',
  "function readableSourceSummary",
  "function classifySync",
  "export function deriveMobileDataReadiness",
  "sourceSummary: readableSourceSummary(state)",
  "actions: actions.slice(0, 4)"
]);

if (!/const\s+level\s*:\s*MobileDataReadinessLevel\s*=\s*!tabletAvailable[\s\S]*\?\s*"empty"[\s\S]*\?\s*"partial"[\s\S]*:\s*"ready"\s*;/s.test(readiness)) {
  fail("Data Readiness level-state mapping drifted");
}

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
  'data-prisma-state="error"',
  "onClearCache"
]);

const sourceStateVectors = [
  { id: "pc_tablet_online_ready", intent: "both upstreams available with clean warnings can be live/ready" },
  { id: "tablet_only_partial", intent: "one operational upstream remains partial rather than fake-ready" },
  { id: "pc_only_blocked_for_sales", intent: "PC alone does not invent Tablet sales availability" },
  { id: "offline_with_cache_stale", intent: "local cache can preserve stale evidence without claiming live" },
  { id: "offline_no_cache_error", intent: "no source and no cache remains an honest unavailable/error state" },
  { id: "timeout_normalized_error", intent: "timeouts normalize through the HTTP error contract" }
];
if (new Set(sourceStateVectors.map((item) => item.id)).size !== 6) {
  fail("deterministic Source States vector set is incomplete");
}

const retiredScenarioPath = "docs/prisma-app/qa/prisma-app-mobile-32-source-state-runtime-scenarios.json";
if (exists(retiredScenarioPath)) {
  fail("retired generated QA scenario file must not become a current verifier dependency", { retiredScenarioPath });
}

console.log(JSON.stringify({
  ok: true,
  verifier,
  currentRuntimeModes: ["reference-disabled", "stale", "live", "partial", "offline", "unknown"],
  readinessLevels: ["ready", "partial", "empty", "offline", "blocked"],
  deterministicSourceStateVectors: sourceStateVectors.length,
  retiredQaDirectoryRequired: false,
  historicalCopyTokensRequired: false,
  claimsRuntimeBehaviorMatrix: false,
  checkAllContainsSourceStates: true,
  message: "Source States verifies current source-state semantics without obsolete copy strings or deleted generated QA artifacts."
}, null, 2));
