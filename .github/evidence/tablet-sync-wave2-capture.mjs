import fs from "node:fs";
import path from "node:path";

const baseUrl = process.env.RUNTIME_URL || "http://127.0.0.1:3120";
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9223);
const evidenceDir = path.resolve(process.env.EVIDENCE_DIR || "evidence/tablet-sync-wave2-postmerge");
const screenshotDir = path.join(evidenceDir, "screenshots");
fs.mkdirSync(screenshotDir, { recursive: true });

const NOW = "2026-08-25T14:20:00.000Z";
const EARLIER = "2026-08-25T14:10:00.000Z";
const SENT = "2026-08-25T14:12:00.000Z";
const ACKED = "2026-08-25T14:13:00.000Z";

function baseItem(status, overrides = {}) {
  const delivery = {
    sentAt: status === "sent" || status === "acked" || status === "conflict" ? SENT : null,
    syncedAt: status === "acked" ? ACKED : null,
    ackedAt: status === "acked" ? ACKED : null,
    failedAt: status === "failed" ? EARLIER : null,
    conflictedAt: status === "conflict" ? EARLIER : null,
    lastAttemptAt: ["failed", "sent", "acked", "conflict"].includes(status) ? EARLIER : null,
    nextRetryAt: status === "failed" ? "2026-08-25T14:30:00.000Z" : null,
    remoteEventId: ["sent", "acked", "conflict"].includes(status) ? `remote-${status}-01` : null,
    remoteLedgerId: ["sent", "acked", "conflict"].includes(status) ? `ledger-${status}-01` : null,
    remoteLifecycleStatus: status === "acked" ? "reconciled" : status === "sent" ? "sent" : status === "conflict" ? "conflict" : status === "failed" ? "failed" : null,
    remoteConflictCode: status === "conflict" ? "stale_sequence" : null,
    remoteRejectedReason: status === "failed" ? "PC_TIMEOUT" : null,
  };
  return {
    id: `fixture-${status}-01`,
    eventId: `evt-${status}-01`,
    title: status === "conflict" ? "Venta por revisar" : "Venta registrada",
    description: status === "conflict"
      ? "Venta registrada en la Tablet. Requiere revisión; no se reintenta automáticamente."
      : status === "failed"
        ? "Venta registrada en la Tablet. Necesita revisión antes de volver a enviar."
        : "Venta registrada en la Tablet. Guardado localmente para continuidad de operación.",
    status,
    statusLabel: { pending: "Pendiente", failed: "Fallido", sent: "Enviado", acked: "Confirmado", conflict: "Revisión" }[status],
    risk: status === "failed" || status === "conflict" ? "danger" : status === "pending" || status === "sent" ? "warn" : "ok",
    attempts: status === "failed" ? 3 : status === "conflict" ? 2 : 1,
    createdAt: "2026-08-25T14:00:00.000Z",
    canRetry: status === "pending" || status === "failed",
    provenance: {
      source: "tablet-pos",
      businessId: "biz_hitech_default",
      storeId: "store-centro",
      terminalId: "terminal-tablet-01",
      deviceId: "device-tablet-01",
      actorId: "cashier-ana",
      aggregateId: "sale-20260825-001",
      originRecordId: "sale-20260825-001",
      idempotencyKey: "idem-wave2-001",
      correlationId: "corr-wave2-001",
      traceId: "trace-wave2-001",
    },
    delivery,
    resolutionOwner: status === "conflict" ? "pc_backoffice" : null,
    resolutionLabel: status === "conflict" ? "Revisión en PC / Backoffice" : null,
    ...overrides,
  };
}

function panelFor(state) {
  if (state === "clean" || state === "license-deny") {
    return {
      summary: { total: 0, pending: 0, failed: 0, sent: 0, acked: 0, conflict: 0, risk: "ok", headline: "Todo enviado", operatorMessage: "Sin pendientes.", offlineVisible: false, lastCheckedAt: NOW },
      items: [], diagnostics: ["Venta local disponible", "No hay pendientes visibles", "Última revisión ahora"]
    };
  }
  const status = state === "pc-offline" ? "pending" : state;
  const item = baseItem(status);
  const summary = { total: 1, pending: 0, failed: 0, sent: 0, acked: 0, conflict: 0, risk: item.risk, headline: "Operación visible", operatorMessage: "Revisar operación.", offlineVisible: state === "pc-offline", lastCheckedAt: NOW };
  summary[status] = 1;
  return { summary, items: [item], diagnostics: ["Venta local disponible", state === "pc-offline" ? "Hay trabajo local por enviar" : "Cola visible", "Última revisión ahora"] };
}

function catalogStatus() {
  return {
    ok: true,
    data: {
      stream: "catalog",
      targetBusinessId: "biz_hitech_default",
      terminalId: "terminal-tablet-01",
      pc: { enabled: true, origin: "http://pc.local", exportPath: "/api/catalog/export" },
      checkpoint: null,
      tableCounts: { Product: 12, PriceListItem: 12 }
    }
  };
}

function licenseResponse(state) {
  const denied = state === "license-deny";
  return {
    ok: true,
    data: {
      status: {
        state: denied ? "revoked" : "active",
        plan: "PRISMA Operación",
        assignmentState: denied ? "unassigned" : "assigned",
        operationalDecision: denied ? "deny" : "allow"
      }
    }
  };
}

function pcHealth(state) {
  if (state === "pc-offline") return { ok: false, enabled: true, status: "offline", url: "http://pc.local", error: "PC sin respuesta" };
  return { ok: true, enabled: true, status: "online", url: "http://pc.local", error: null };
}

let currentState = "clean";
const runtimeErrors = [];
const consoleErrors = [];
const requestLog = [];

class CDP {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.pending = new Map();
    this.handlers = new Map();
  }
  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("CDP websocket timeout")), 10000);
      this.ws.addEventListener("open", () => { clearTimeout(timer); resolve(); }, { once: true });
      this.ws.addEventListener("error", (event) => { clearTimeout(timer); reject(new Error(`CDP websocket error: ${event.message || "unknown"}`)); }, { once: true });
    });
    this.ws.addEventListener("message", async (event) => {
      let raw;
      if (typeof event.data === "string") raw = event.data;
      else if (event.data?.arrayBuffer) raw = Buffer.from(await event.data.arrayBuffer()).toString("utf8");
      else raw = Buffer.from(event.data).toString("utf8");
      const msg = JSON.parse(raw);
      if (msg.id) {
        const waiter = this.pending.get(msg.id);
        if (!waiter) return;
        this.pending.delete(msg.id);
        if (msg.error) waiter.reject(new Error(`${waiter.method}: ${JSON.stringify(msg.error)}`));
        else waiter.resolve(msg.result || {});
        return;
      }
      const fns = this.handlers.get(msg.method) || [];
      for (const fn of fns) Promise.resolve(fn(msg.params || {})).catch((error) => runtimeErrors.push(`handler ${msg.method}: ${error.stack || error}`));
    });
  }
  on(method, fn) {
    const arr = this.handlers.get(method) || [];
    arr.push(fn);
    this.handlers.set(method, arr);
  }
  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject, method });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
}

function responseBody(obj) {
  return Buffer.from(JSON.stringify(obj), "utf8").toString("base64");
}

async function waitFor(predicateExpression, label, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const result = await cdp.send("Runtime.evaluate", { expression: `Boolean(${predicateExpression})`, returnByValue: true });
    if (result.result?.value === true) return;
    await new Promise((r) => setTimeout(r, 180));
  }
  throw new Error(`WAIT_TIMEOUT:${label}`);
}

async function bodyText() {
  const r = await cdp.send("Runtime.evaluate", { expression: "document.body ? document.body.innerText : ''", returnByValue: true });
  return String(r.result?.value || "");
}

async function clickButton(label) {
  const expr = `(() => { const b=[...document.querySelectorAll('button')].find(x=>x.textContent.trim()===${JSON.stringify(label)}); if(!b) return false; b.click(); return true; })()`;
  const r = await cdp.send("Runtime.evaluate", { expression: expr, returnByValue: true });
  if (!r.result?.value) throw new Error(`BUTTON_NOT_FOUND:${label}`);
  await new Promise((r2) => setTimeout(r2, 450));
}

async function openDetails() {
  await cdp.send("Runtime.evaluate", { expression: "document.querySelectorAll('details').forEach(d=>d.open=true); true", returnByValue: true });
  await new Promise((r) => setTimeout(r, 250));
}

async function screenshot(name) {
  const shot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, fromSurface: true });
  fs.writeFileSync(path.join(screenshotDir, name), Buffer.from(shot.data, "base64"));
}

const target = await (async () => {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(baseUrl + "/sync")}`, { method: "PUT" });
      if (r.ok) return await r.json();
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("CHROME_DEBUG_TARGET_UNAVAILABLE");
})();

const cdp = new CDP(target.webSocketDebuggerUrl);
await cdp.connect();
await cdp.send("Page.enable");
await cdp.send("Runtime.enable");
await cdp.send("Log.enable");
await cdp.send("Network.enable");
await cdp.send("Emulation.setDeviceMetricsOverride", { width: 1365, height: 900, deviceScaleFactor: 1, mobile: false });
await cdp.send("Fetch.enable", { patterns: [{ urlPattern: `${baseUrl}/api/*`, requestStage: "Request" }] });

cdp.on("Runtime.exceptionThrown", ({ exceptionDetails }) => runtimeErrors.push(`exception:${exceptionDetails?.text || "unknown"}`));
cdp.on("Runtime.consoleAPICalled", ({ type, args }) => {
  if (type === "error") consoleErrors.push(args?.map((x) => x.value ?? x.description ?? "").join(" ") || "console.error");
});
cdp.on("Log.entryAdded", ({ entry }) => {
  if (entry?.level === "error" && !String(entry?.text || "").includes("favicon")) consoleErrors.push(`log:${entry.text}`);
});

cdp.on("Fetch.requestPaused", async ({ requestId, request }) => {
  const url = new URL(request.url);
  requestLog.push(`${currentState} ${request.method} ${url.pathname}`);
  let status = 200;
  let payload;
  if (url.pathname === "/api/pos/sync/panel") {
    if (currentState === "unconfirmed") {
      status = 503;
      payload = { ok: false, error: "SYNC_PANEL_UNVERIFIED", message: "Estado de pendientes sin confirmar." };
    } else payload = { ok: true, data: panelFor(currentState) };
  } else if (url.pathname === "/api/license/status") {
    payload = licenseResponse(currentState);
  } else if (url.pathname === "/api/pos/sync/health/pc") {
    payload = pcHealth(currentState);
  } else if (url.pathname === "/api/pos/sync/pull") {
    payload = request.method === "GET" ? catalogStatus() : { ok: true, reason: "empty", mode: "delta", sourceBusinessId: "biz_hitech_default", targetBusinessId: "biz_hitech_default", terminalId: "terminal-tablet-01", cursorBefore: null, cursorAfter: null, checkpoint: null, counts: { received: 0, applied: 0, rejected: 0, conflict: 0, duplicate: 0, byEntity: {} }, findings: [], errors: [], health: { enabled: true, origin: "http://pc.local", url: "http://pc.local", status: "online", httpStatus: 200 } };
  } else if (url.pathname === "/api/pos/sync/retry") {
    payload = { ok: true, data: { scope: "all_failed", requested: null, eligible: 1, updated: 1, skipped: null, eligibleIds: [], skippedIds: [], message: "Preparadas 1 operación(es) fallida(s). Se enviarán cuando haya conexión." } };
  } else if (url.pathname === "/api/pos/sync/dispatch") {
    payload = { ok: false, reason: "pc_unavailable", dispatched: 0, forced: true, health: { ok: false, enabled: true, status: "offline", url: "http://pc.local", error: "PC sin respuesta" } };
  } else {
    payload = { ok: true, data: {} };
  }
  await cdp.send("Fetch.fulfillRequest", {
    requestId,
    responseCode: status,
    responseHeaders: [{ name: "content-type", value: "application/json; charset=utf-8" }, { name: "cache-control", value: "no-store" }],
    body: responseBody(payload)
  });
});

const states = [
  ["clean", null, ["Pendientes al día", "No hay pendientes para enviar."]],
  ["pending", "Pendientes", ["Detalles de operación", "Tienda: store-centro", "Reintento disponible"]],
  ["failed", "Fallidos", ["Último rechazo: PC_TIMEOUT", "Reintento disponible", "Último intento:"]],
  ["sent", "Enviados", ["Estado PC: sent", "Ledger: ledger-sent-01", "Sin acción requerida"]],
  ["acked", "Confirmados", ["Estado PC: reconciled", "Confirmado:", "Sin acción requerida"]],
  ["conflict", "Revisión", ["Revisión en PC / Backoffice.", "Motivo de conflicto: stale_sequence", "Revisión requerida"]],
  ["pc-offline", "Pendientes", ["PC sin respuesta", "Venta local disponible aunque PC no responda", "Tienda: store-centro"]],
  ["license-deny", null, ["Licencia detenida", "Tablet pendiente", "Pendientes al día"]],
  ["unconfirmed", null, ["Cola sin confirmar", "Estado de pendientes sin confirmar", "—"]]
];

const manifest = [];
for (const [state, filter, expectedTexts] of states) {
  currentState = state;
  const beforeExceptions = runtimeErrors.length;
  const beforeConsole = consoleErrors.length;
  await cdp.send("Page.navigate", { url: `${baseUrl}/sync?wave2Evidence=${encodeURIComponent(state)}&t=${Date.now()}` });
  await waitFor("document.readyState === 'complete' && document.body && document.body.innerText.includes('Pendientes y conexión')", `${state}:page-ready`, 25000);
  await new Promise((r) => setTimeout(r, 650));
  if (filter) await clickButton(filter);
  await openDetails();
  const text = await bodyText();
  for (const expected of expectedTexts) {
    if (!text.includes(expected)) throw new Error(`ASSERT_TEXT_MISSING:${state}:${expected}`);
  }
  if (state === "conflict" && text.includes("Reintento disponible")) throw new Error("CONFLICT_ADVERTISED_RETRY");
  if (["sent", "acked", "conflict"].includes(state) && text.includes(`evt-${state}-01`)) throw new Error(`RAW_EVENT_ID_VISIBLE:${state}`);
  if (runtimeErrors.length !== beforeExceptions) throw new Error(`RUNTIME_EXCEPTION:${state}:${runtimeErrors.slice(beforeExceptions).join(" | ")}`);
  if (consoleErrors.length !== beforeConsole) throw new Error(`CONSOLE_ERROR:${state}:${consoleErrors.slice(beforeConsole).join(" | ")}`);
  const name = `${String(manifest.length + 1).padStart(2, "0")}-${state}.png`;
  await screenshot(name);
  manifest.push({ state, screenshot: name, assertions: expectedTexts });

  if (state === "failed") {
    await clickButton("Reintentar fallidos");
    await waitFor("document.body && document.body.innerText.includes('Reintento: 1 operación(es) preparadas.')", "failed:retry-result", 15000);
    await openDetails();
    const retryText = await bodyText();
    if (!retryText.includes("PC no disponible") && !retryText.includes("PC no respondio") && !retryText.includes("PC no disponible")) {
      if (!retryText.includes("PC no disponible") && !retryText.includes("PC no disponible.")) throw new Error("RETRY_PC_UNAVAILABLE_COPY_MISSING");
    }
    const retryName = `${String(manifest.length + 1).padStart(2, "0")}-failed-retry-result.png`;
    await screenshot(retryName);
    manifest.push({ state: "failed-retry-result", screenshot: retryName, assertions: ["Reintento: 1 operación(es) preparadas."] });
  }
}

fs.writeFileSync(path.join(evidenceDir, "screenshot-manifest.json"), JSON.stringify({ targetSha: process.env.TARGET_SHA, viewport: "1365x900", screenshots: manifest }, null, 2) + "\n");
fs.writeFileSync(path.join(evidenceDir, "browser-runtime-errors.json"), JSON.stringify({ runtimeErrors, consoleErrors }, null, 2) + "\n");
fs.writeFileSync(path.join(evidenceDir, "browser-api-requests.log"), requestLog.join("\n") + "\n");
if (runtimeErrors.length || consoleErrors.length) throw new Error(`BROWSER_ANOMALIES runtime=${runtimeErrors.length} console=${consoleErrors.length}`);
console.log(`PASS_TABLET_SYNC_WAVE2_BROWSER_SCREENSHOTS ${manifest.length}/${manifest.length}`);
cdp.ws.close();
