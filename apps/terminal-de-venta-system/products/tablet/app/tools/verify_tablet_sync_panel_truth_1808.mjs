#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");
const checks = [];

function readApp(rel) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    checks.push({ name: `exists app/${rel}`, ok: false });
    return "";
  }
  checks.push({ name: `exists app/${rel}`, ok: true });
  return fs.readFileSync(file, "utf8");
}

function readTerminal(rel) {
  const file = path.join(terminalRoot, rel);
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

function functionBody(source, name, nextName) {
  const start = source.indexOf(`function ${name}`);
  const end = nextName ? source.indexOf(`function ${nextName}`, Math.max(0, start + 1)) : source.length;
  if (start < 0) return "";
  return source.slice(start, end < 0 ? source.length : end);
}

const route = readApp("app/api/pos/sync/panel/route.ts");
const screen = readApp("components/sync/pending-offline-sync-panel-screen.tsx");
const contract = readApp("src/lib/pending-offline-sync/sync-panel-contract.ts");
const outbox = readApp("src/server/pos-outbox/index.ts");
const operationalGate = readApp("src/lib/operational-gate/can-sell.ts");
const pcOrigin = readApp("src/server/sync/pc-origin.ts");
const dispatcher = readApp("src/server/sync/dispatcher.ts");
const licenseNormalizer = readTerminal("shared/licensing/license-normalizer.ts");
const licenseResolver = readTerminal("shared/licensing/feature-resolver.ts");

check(
  "cache key is based on normalized content-affecting query",
  route.includes("prismaTabboom1QueryKey(input)") &&
    route.includes("businessId: input.businessId") &&
    route.includes("limit: input.limit") &&
    route.includes('status: input.status?.trim().toLowerCase() ?? ""')
);
check(
  "cache and inflight are partitioned by query key",
  route.includes("states: Map<string, PrismaTabboom1State>") &&
    route.includes("store.states.get(cacheKey)") &&
    route.includes("prismaTabboom1State(cacheKey)")
);
check("query-state store is bounded", route.includes("PRISMA_TABBOOM1_MAX_QUERY_STATES") && route.includes("prismaTabboom1PruneStore"));

const timeoutBody = functionBody(route, "prismaTabboom1UnverifiedTimeout", "prismaTabboom1OriginalBounded");
check(
  "timeout fails closed as unverified",
  timeoutBody.includes('"SYNC_PANEL_UNVERIFIED"') &&
    timeoutBody.includes("503") &&
    timeoutBody.includes('reason: "bounded_timeout"') &&
    timeoutBody.includes("localSalesBlocked: false")
);
check("timeout never returns stale cache as current truth", timeoutBody.length > 0 && !timeoutBody.includes("prismaTabboom1Clone"));
check("timeout cannot manufacture unknown success payload", !route.includes('risk: "unknown"') && !route.includes("summary: { total: 0, pending: 0"));
check("timeout response is not cached", route.includes("if (response.status < 500 && body.length > 0)") && timeoutBody.includes('"cache-control", "no-store"'));
check("route preserves POS API error translation", route.includes("catch (error)") && route.includes("return toPosApiError(error)"));

check(
  "UI tracks panel verification independently from action errors",
  screen.includes("const [panelUnverified, setPanelUnverified] = useState(true)") &&
    screen.includes("setPanelUnverified(false)") &&
    screen.includes("setPanelUnverified(true)") &&
    screen.includes("const panelConfirmed = Boolean(panel && !panelUnverified && actionMode === null)")
);
check(
  "UI unknown or unconfirmed state is neutral, never implicit ok",
  screen.includes('summaryRisk === "ok" ? "ok"') &&
    screen.includes(': "neutral"') &&
    screen.includes("Estado de pendientes sin confirmar") &&
    screen.includes("panelUnverified && actionMode === null")
);
check(
  "UI does not fabricate zero queue counts while unconfirmed",
  screen.includes("Cola sin confirmar") &&
    screen.includes('panelConfirmed && typeof value === "number" ? value : "—"') &&
    !screen.includes("panel?.summary.total ?? 0") &&
    !screen.includes("panel?.summary.pending ?? 0") &&
    !screen.includes("panel?.summary.failed ?? 0") &&
    !screen.includes("panel?.summary.conflict ?? 0") &&
    !screen.includes("panel?.summary.acked ?? 0")
);
check(
  "empty queue copy is only definitive when confirmed",
  screen.includes("emptyQueueMessage(filter: FilterMode, confirmed: boolean)") &&
    screen.includes("if (!confirmed) return \"Estado de cola sin confirmar") &&
    screen.includes("emptyQueueMessage(filter, panelConfirmed)")
);

check(
  "SyncRisk contract remains governed ok-warn-danger only",
  contract.includes('export type SyncRisk="ok"|"warn"|"danger"') && !contract.includes('"unknown"')
);
for (const state of ["PENDING", "SENT", "FAILED", "ACKED", "CONFLICT"]) {
  check(`Outbox preserves ${state.toLowerCase()} state`, outbox.includes(`OUTBOX_STATUS_${state}`));
}
check("Outbox preserves business scoping", outbox.includes("businessId: input.businessId"));
check("Outbox preserves idempotency key", outbox.includes("idempotencyKey"));

check(
  "license deny semantics remain present",
  operationalGate.includes("LICENSE_BLOCKED") && operationalGate.includes("buildLicenseBlockedDecision")
);
check(
  "license allow semantics remain local-POS capability based",
  operationalGate.includes("license.canUseLocalPos") && licenseResolver.includes('status.state === "missing"')
);
check(
  "missing license remains explicit instead of invented assignment",
  licenseNormalizer.includes("LICENSE_CUSTOMER_PENDING") && licenseNormalizer.includes('assignmentState: "unknown"')
);
check(
  "Tablet sale stays local-first when PC sync is unavailable",
  screen.includes("Venta local disponible aunque PC no responda") &&
    pcOrigin.includes("PRISMA_TABLET_PC_SYNC_ENABLED") &&
    !pcOrigin.includes('readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", true)')
);
check(
  "sync remains user initiated and idempotent dispatcher truth is preserved",
  !screen.includes('source: "sync-panel-open"') &&
    dispatcher.includes("idempotencyKey") &&
    dispatcher.includes('result.status === "conflict"') &&
    dispatcher.includes('status: "acked"')
);
check("fix does not introduce !important", !route.includes("!important") && !screen.includes("!important"));

const failed = checks.filter((item) => !item.ok);
for (const item of checks) {
  console.log(`${item.ok ? "PASS" : "FAIL"} ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
}
if (failed.length) {
  console.error(`BLOCKED TABLET_SYNC_PANEL_TRUTH_1808 ${failed.length}/${checks.length} failed`);
  process.exit(1);
}
console.log(`PASS TABLET_SYNC_PANEL_TRUTH_1808 ${checks.length}/${checks.length}`);
