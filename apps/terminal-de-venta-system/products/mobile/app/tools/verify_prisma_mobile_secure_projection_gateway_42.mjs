#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");
const exists = (relative) => fs.existsSync(path.join(root, relative));
const failures = [];

function requireFile(relative) {
  if (!exists(relative)) failures.push(`Missing required file: ${relative}`);
}

function requireText(relative, snippets) {
  requireFile(relative);
  if (!exists(relative)) return;
  const text = read(relative);
  for (const snippet of snippets) {
    if (!text.includes(snippet)) failures.push(`${relative} lacks: ${snippet}`);
  }
}

function forbidText(relative, snippets) {
  requireFile(relative);
  if (!exists(relative)) return;
  const text = read(relative);
  for (const snippet of snippets) {
    if (text.includes(snippet)) failures.push(`${relative} contains forbidden marker: ${snippet}`);
  }
}

const context = "src/lib/prisma-app/mobile-security/context.ts";
const cache = "src/lib/prisma-app/prisma-mobile-cache.ts";
const snapshotRoute = "app/api/mobile/snapshot/route.ts";
const endpointHandlers = "src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts";
const projectionEnvelope = "src/lib/prisma-app/mobile-security/projection-envelope.ts";
const packageJson = "package.json";

requireText(context, [
  "createHmac",
  "timingSafeEqual",
  "PRISMA_MOBILE_SESSION_SECRET",
  'process.env.NODE_ENV === "production"',
  "ERR.AUTH.REQUIRED",
  "ERR.PERMISSION.DENIED",
  "development-loopback",
  "mobileContextToConfigOverrides"
]);

requireText(cache, [
  'LEGACY_PRISMA_MOBILE_CACHE_KEY = "prisma.mobile.snapshot.v18"',
  "memorySnapshot",
  "localStorage.removeItem"
]);

forbidText(cache, [
  "localStorage.setItem",
  "MAX_CACHE_AGE_MS = 1000 * 60 * 30"
]);

requireText(snapshotRoute, [
  "mobileDataPlaneSnapshotJson(request)"
]);

forbidText(snapshotRoute, [
  'params.get("businessId")',
  'params.get("terminalId")',
  "readScopedOverrides"
]);

requireText(endpointHandlers, [
  "loadAuthorizedMobileState",
  "guarded.safeProbes",
  "Authorization, Cookie"
]);

requireText(projectionEnvelope, [
  "contractVersion",
  "schemaVersion",
  "sourceSystem",
  "sourceRuntime",
  "sourceOwner",
  "tenantId",
  "businessId",
  "branchId",
  "terminalId",
  "deviceId",
  "licenseId",
  "actorId",
  "capturedAt",
  "observedAt",
  "generatedAt",
  "expiresAt",
  "freshnessState",
  "dataQuality",
  "privacyClass",
  "permissionScope",
  "traceId",
  "sourceEventIds",
  "nextCursor",
  "warnings",
  "errors"
]);

const requiredReadModelRoutes = [
  "system-summary",
  "data-readiness",
  "sync-source-health",
  "executive-summary",
  "sales-summary"
];

for (const route of requiredReadModelRoutes) {
  requireText(`app/api/mobile/v1/read-models/${route}/route.ts`, [
    "mobileProjectionJson(request"
  ]);
}

const legacyRoutes = [
  "action-inbox",
  "alerts",
  "branches",
  "cash/current",
  "command-center",
  "daily-brief",
  "data-quality",
  "decision-ledger",
  "health",
  "health-radar",
  "inventory/watchlist",
  "pulse-timeline",
  "reports/daily",
  "sales/today",
  "snapshot",
  "summary"
];

for (const route of legacyRoutes) {
  const relative = `app/api/mobile/${route}/route.ts`;
  requireFile(relative);
  if (!exists(relative)) continue;
  const text = read(relative);
  const guarded =
    text.includes("mobileDataPlaneJson(request") ||
    text.includes("mobileDataPlaneSnapshotJson(request") ||
    text.includes("loadAuthorizedMobileState(request");
  if (!guarded) failures.push(`${relative} is not guarded`);
}

requireText(packageJson, [
  '"version": "0.42.0"',
  '"verify:secure-projection-gateway"',
  '"prismaMobileSecureProjectionGatewayVersion": "0.42.0"'
]);

const allChangedSources = [
  context,
  cache,
  snapshotRoute,
  endpointHandlers,
  projectionEnvelope,
  "src/lib/prisma-app/mobile-security/phase1-read-models.ts",
  "src/lib/prisma-app/mobile-security/projection-route.ts",
  "src/lib/prisma-app/mobile-security/route-guard.ts",
  "src/lib/prisma-app/mobile-security/sanitize.ts"
];

for (const relative of allChangedSources) {
  if (exists(relative) && read(relative).includes("!important")) {
    failures.push(`${relative} introduces !important`);
  }
}

if (failures.length) {
  console.error("PRISMA Mobile Secure Projection Gateway 42: FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA Mobile Secure Projection Gateway 42: PASS");
console.log(JSON.stringify({
  contract: "MOBPROJ1_SECURE_PROJECTION_GATEWAY_PHASE1",
  classification: "VERIFY",
  status: "LOCAL_VERIFIED_PENDING_RUNTIME_SESSION_E2E",
  phase: "read-only",
  guardedLegacyRoutes: legacyRoutes.length,
  phase1ReadModels: requiredReadModelRoutes.length,
  persistentOperationalCache: false,
  commandPathsEnabled: false,
  runtimeOrDeployProven: false
}, null, 2));
