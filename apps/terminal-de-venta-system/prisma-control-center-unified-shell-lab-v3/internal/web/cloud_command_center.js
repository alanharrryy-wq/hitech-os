(function () {
  "use strict";

  const SURFACES = [
    ["command", "Command", "Cloud command surface", "Live PRISMA Cloud Semilla signals, tenant state, licenses, fleet and evidence."],
    ["customers", "Customers", "Customer operations", "Tenants, commercial summary and demo-prisma snapshot context."],
    ["entitlements", "Entitlements", "Licensing authority", "License Ops from Control Center 3150 adapted into the private 3160 cockpit."],
    ["fleet", "Fleet", "Fleet and devices", "Registered devices, recent activity and local non-customer device smoke."],
    ["provisioning", "Provisioning", "Provisioning lane", "Capabilities, activation posture and smoke actions against the SaaS contract."],
    ["contracts", "Contracts & Config", "Contracts and config", "Public contract, client integration receipt and runtime commercial contract evidence."],
    ["operations", "Operations", "Operations health", "Cloud health, admin selftest, tenant snapshot and commercial summary status."],
    ["support", "Support", "Support notes", "Create a demo-prisma operator note when the local admin token is available."],
    ["security", "Security & Audit", "Security and audit", "Local admin-token posture, audit events and redacted endpoint telemetry."],
    ["system", "System", "System diagnostics", "Local diagnostics, runtime events and legacy technical observability moved out of the main face."]
  ];

  const state = { surface: "command", data: null, license: null, health: null, runtime: null, contract: null, busy: false };
  const $ = (id) => document.getElementById(id);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;"
    }[ch]));
  }

  function compact(value, fallback = "-") {
    if (value === null || value === undefined || value === "") return fallback;
    if (typeof value === "object") return JSON.stringify(value).slice(0, 140);
    return String(value);
  }

  function tone(value) {
    const raw = String(value || "").toUpperCase();
    if (raw.includes("PASS") || raw.includes("OK") || raw.includes("READY") || raw.includes("LIVE") || raw.includes("ACTIVE") || raw.includes("FULL")) return "ok";
    if (raw.includes("WARN") || raw.includes("READ_ONLY") || raw.includes("PARTIAL") || raw.includes("PENDING") || raw.includes("MISSING") || raw.includes("REVIEW")) return "warn";
    if (raw.includes("FAIL") || raw.includes("ERROR") || raw.includes("OFFLINE") || raw.includes("FORBIDDEN") || raw.includes("BLOCKED")) return "bad";
    return "";
  }

  function chip(value, label) {
    const text = compact(label ?? value);
    return `<span class="cc-tone ${tone(value)}">${esc(text)}</span>`;
  }

  function kv(label, value) {
    return `<div class="cc-kv"><small>${esc(label)}</small><strong title="${esc(compact(value))}">${esc(compact(value))}</strong></div>`;
  }

  function kvGrid(items) {
    return `<div class="cc-kv-grid">${items.map(([label, value]) => kv(label, value)).join("")}</div>`;
  }

  function panel(title, summary, body, opts) {
    const span = opts?.span || 6;
    const tag = opts?.tag ? chip(opts.tag, opts.tagLabel || opts.tag) : "";
    return `<article class="cc-panel cc-span-${span}">
      <div class="cc-panel-head"><div><h3>${esc(title)}</h3>${summary ? `<p>${esc(summary)}</p>` : ""}</div>${tag}</div>
      ${body || ""}
    </article>`;
  }

  function list(items, emptyLabel) {
    const rows = Array.isArray(items) ? items : [];
    if (!rows.length) return `<div class="cc-empty">${esc(emptyLabel || "No data available")}</div>`;
    return `<div class="cc-list">${rows.slice(0, 18).map((item, index) => {
      if (Array.isArray(item)) return `<div class="cc-row"><span>${esc(item[0])}</span><strong>${esc(compact(item[1]))}</strong></div>`;
      const title = item && typeof item === "object" ? (item.displayName || item.name || item.slug || item.id || item.deviceId || item.receiptId || `Item ${index + 1}`) : item;
      const detail = item && typeof item === "object" ? (item.status || item.state || item.kind || item.plan || item.createdAt || item.updatedAt || "") : "";
      return `<div class="cc-row"><span>${esc(title)}</span><strong>${esc(compact(detail))}</strong></div>`;
    }).join("")}</div>`;
  }

  function jsonBlock(value) {
    return `<pre class="cc-result">${esc(JSON.stringify(value ?? {}, null, 2))}</pre>`;
  }

  async function api(path, options) {
    const response = await fetch(path, {
      cache: "no-store",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      ...(options || {})
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || payload.reason || payload.status || `${path} ${response.status}`);
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  async function safeApi(path) {
    try {
      return await api(path);
    } catch (error) {
      return { ok: false, path, error: String(error.message || error), payload: error.payload || null };
    }
  }

  function toast(message) {
    const node = $("ccToast");
    if (!node) return;
    node.textContent = message;
    node.classList.add("show");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => node.classList.remove("show"), 2600);
  }

  function derived() {
    return state.data?.derived || {};
  }

  function endpoints() {
    return state.data?.endpoints || {};
  }

  function endpointRows(names) {
    return names.map((name) => {
      const endpoint = endpoints()[name] || {};
      const status = endpoint.status || endpoint.statusCode || (endpoint.ok ? "OK" : "CHECK");
      return [name, `${status} ${endpoint.latencyMs != null ? endpoint.latencyMs + " ms" : ""}`.trim()];
    });
  }

  function updateChrome() {
    const data = state.data || {};
    const d = derived();
    const admin = data.admin || {};
    $("ccMode").textContent = data.mode || "READ_ONLY";
    $("ccMode").className = `cc-chip ${tone(data.mode)}`;
    $("ccCloud").textContent = data.ok ? "Cloud online" : "Cloud review";
    $("ccCloud").className = `cc-chip ${data.ok ? "ok" : "warn"}`;
    $("ccAdmin").textContent = admin.enabled ? "Admin local active" : (admin.tokenAvailable ? "Admin token local" : "No admin token");
    $("ccAdmin").className = `cc-chip ${admin.enabled ? "ok" : "warn"}`;
    $("metricHealth").textContent = endpoints().health?.statusCode || data.status || (data.ok ? "OK" : "CHECK");
    $("metricTenant").textContent = d.tenant?.slug || d.tenant?.id || data.cloud?.tenantSlug || "demo-prisma";
    $("metricLicense").textContent = d.license?.status || state.license?.status || "Review";
    $("metricEvidence").textContent = `${(d.notes || []).length} notes / ${(d.receipts || []).length} receipts`;
  }

  function updateSurfaceHeader() {
    const spec = SURFACES.find(([id]) => id === state.surface) || SURFACES[0];
    $("surfaceKicker").textContent = spec[1];
    $("surfaceTitle").textContent = spec[2];
    $("surfaceSummary").textContent = spec[3];
    $("surfacePrimary").textContent = derived().tenant?.slug || state.data?.cloud?.tenantSlug || "demo-prisma";
    $("surfaceScore").textContent = state.data?.ok ? "LIVE" : "CHECK";
    $$(".cc-nav button").forEach((button) => button.classList.toggle("active", button.dataset.surface === state.surface));
  }

  function renderCommand() {
    const d = derived();
    return [
      panel("Cloud signal", "Health, capabilities and tenant status from app.hitechrts.com.", kvGrid([
        ["Service", d.service || "PRISMA Cloud Semilla"],
        ["Version", d.version || "-"],
        ["Base URL", state.data?.cloud?.baseUrl || "https://app.hitechrts.com"],
        ["Mode", state.data?.mode || "READ_ONLY"]
      ]), { span: 5, tag: state.data?.ok ? "LIVE" : "REVIEW" }),
      panel("Endpoint runway", "Public and admin checks stay behind the local 3160 bridge.", list(endpointRows(["health", "capabilities", "tenantStatus", "adminSelftest", "commercialSummary", "tenantSnapshot"])), { span: 7, tag: endpoints().health?.ok ? "PASS" : "WARN" }),
      panel("Command lanes", "Primary operational surfaces are first-class tabs, not embeds.", list(SURFACES.map(([, label, title]) => [label, title])), { span: 12 })
    ].join("");
  }

  function renderCustomers() {
    const d = derived();
    const commercial = d.commercialSummary || {};
    return [
      panel("Tenant demo-prisma", "Customer identity, plan and live status.", kvGrid([
        ["Tenant", d.tenant?.displayName || d.tenant?.slug || "demo-prisma"],
        ["Status", d.tenant?.status || "-"],
        ["Plan", d.tenant?.plan || d.license?.plan || "-"],
        ["License", d.license?.status || "-"]
      ]), { span: 5, tag: d.tenant?.status || "REVIEW" }),
      panel("Commercial summary", "Admin commercial signal, redacted by the local bridge.", jsonBlock(commercial), { span: 7, tag: endpoints().commercialSummary?.ok ? "PASS" : endpoints().commercialSummary?.status || "WARN" }),
      panel("Recent customer evidence", "Notes, receipts and audit events from tenant snapshot.", list([
        ["Notes", (d.notes || []).length],
        ["Receipts", (d.receipts || []).length],
        ["Events", (d.events || []).length],
        ["Devices", (d.devices || []).length]
      ]), { span: 12 })
    ].join("");
  }

  function renderEntitlements() {
    const runtime = state.license?.runtime || {};
    const license = runtime.license || {};
    const identity = runtime.identity || {};
    return [
      panel("License Ops", "3150 license operations adapted as read-only 3160 telemetry.", kvGrid([
        ["Adapter status", state.license?.status || "-"],
        ["Safety", state.license?.safetyMode || "LOCAL_READ_ONLY"],
        ["Read only", state.license?.readOnly ? "yes" : "review"],
        ["Source", state.license?.source || "-"]
      ]), { span: 4, tag: state.license?.status || "REVIEW" }),
      panel("Entitlement record", "License file summary and assignment without exposing local paths.", kvGrid([
        ["License ID", license.licenseId || "-"],
        ["Plan", license.plan || derived().license?.plan || "-"],
        ["Status", license.status || derived().license?.status || "-"],
        ["Valid until", license.validUntil || "-"]
      ]), { span: 4, tag: license.status || derived().license?.status || "REVIEW" }),
      panel("Identity binding", "Device identity and tenant assignment.", kvGrid([
        ["Client", license.assignment?.clientId || identity.clientId || "-"],
        ["Business", license.assignment?.businessId || identity.businessId || "-"],
        ["Store", license.assignment?.storeId || identity.storeId || "-"],
        ["Device", license.assignment?.deviceId || identity.deviceId || "-"]
      ]), { span: 4, tag: license.signaturePresent ? "SIGNED" : "REVIEW" }),
      panel("License raw evidence", "Public-redacted latest payload.", jsonBlock(state.license), { span: 12 })
    ].join("");
  }

  function renderFleet() {
    const d = derived();
    return [
      panel("Registered devices", "Devices observed in tenant snapshot.", list(d.devices, "No devices returned by snapshot."), { span: 7, tag: `${(d.devices || []).length} devices` }),
      panel("Device smoke", "Local non-customer POST /api/devices/register through the SaaS bridge.", `<p>Runs only from local 3160 and uses the admin token when available.</p><div class="cc-actions"><button class="cc-action" data-action="device-smoke">Register lab device</button></div><div id="deviceSmokeResult"></div>`, { span: 5, tag: state.data?.admin?.enabled ? "READY" : "TOKEN_MISSING" }),
      panel("Fleet snapshot", "Recent receipts and events tied to fleet operations.", list([["Receipts", (d.receipts || []).length], ["Events", (d.events || []).length], ["Admin snapshot", endpoints().tenantSnapshot?.statusCode || endpoints().tenantSnapshot?.status || "-"]]), { span: 12 })
    ].join("");
  }

  function renderProvisioning() {
    const caps = derived().capabilities || {};
    return [
      panel("Capabilities", "Public capabilities endpoint.", jsonBlock(caps), { span: 7, tag: endpoints().capabilities?.ok ? "PASS" : "WARN" }),
      panel("Provisioning actions", "Smoke actions are local-only and non-customer.", `<div class="cc-actions"><button class="cc-action" data-action="receipt-smoke">Send receipt smoke</button><button class="cc-action" data-action="device-smoke">Register lab device</button></div><div id="provisioningResult"></div>`, { span: 5, tag: state.data?.admin?.enabled ? "READY" : "READ_ONLY" }),
      panel("Provisioning contract", "Client contract and tenant public status.", list(endpointRows(["clientContract", "tenantStatus", "tenantSnapshot"])), { span: 12 })
    ].join("");
  }

  function renderContracts() {
    const d = derived();
    return [
      panel("Public contract", "GET /api/client/contract for demo-prisma.", jsonBlock(d.publicContract || {}), { span: 6, tag: endpoints().clientContract?.ok ? "PASS" : "WARN" }),
      panel("Cloud configuration", "Local bridge configuration, redacted by backend.", jsonBlock({
        baseUrl: state.data?.cloud?.baseUrl,
        tenantSlug: state.data?.cloud?.tenantSlug,
        admin: state.data?.admin,
        source: state.data?.source
      }), { span: 6, tag: "LOCAL" }),
      panel("Integration receipt", "POST /api/client/integration-receipt smoke path.", `<div class="cc-actions"><button class="cc-action" data-action="receipt-smoke">Send receipt smoke</button></div><div id="contractReceiptResult"></div>`, { span: 12, tag: state.data?.admin?.enabled ? "READY" : "TOKEN_MISSING" })
    ].join("");
  }

  function renderOperations() {
    return [
      panel("Health endpoints", "Operations status across public and admin endpoints.", list(endpointRows(["health", "capabilities", "adminSelftest", "commercialSummary", "tenantSnapshot"])), { span: 6, tag: endpoints().health?.ok ? "PASS" : "WARN" }),
      panel("Selftest payload", "Admin selftest response if local admin token is available.", jsonBlock(endpoints().adminSelftest || {}), { span: 6, tag: endpoints().adminSelftest?.ok ? "PASS" : endpoints().adminSelftest?.status || "WARN" }),
      panel("Commercial operations", "Summary and tenant snapshot details.", jsonBlock({ commercialSummary: endpoints().commercialSummary, tenantSnapshot: endpoints().tenantSnapshot }), { span: 12 })
    ].join("");
  }

  function renderSupport() {
    const notes = derived().notes || [];
    return [
      panel("Create demo-prisma note", "POST /api/admin/tenants/demo-prisma/notes via local token bridge.", `<textarea id="supportNoteText" class="cc-textarea" spellcheck="true">Operator note from PRISMA Cloud Command Center.</textarea><div class="cc-actions"><button class="cc-action" data-action="create-note">Create support note</button></div><div id="supportNoteResult"></div>`, { span: 6, tag: state.data?.admin?.enabled ? "READY" : "TOKEN_MISSING" }),
      panel("Recent support notes", "Tenant notes from the admin snapshot.", list(notes, "No notes returned by snapshot."), { span: 6, tag: `${notes.length} notes` }),
      panel("Support evidence", "Receipts and events can support customer investigation.", list([["Receipts", (derived().receipts || []).length], ["Events", (derived().events || []).length], ["Snapshot", endpoints().tenantSnapshot?.statusCode || endpoints().tenantSnapshot?.status || "-"]]), { span: 12 })
    ].join("");
  }

  function renderSecurity() {
    const admin = state.data?.admin || {};
    return [
      panel("Local admin posture", "Token status is metadata only; token value is never exposed.", kvGrid([
        ["Local host allowed", admin.localHostAllowed ? "yes" : "no"],
        ["Token available", admin.tokenAvailable ? "yes" : "no"],
        ["Token source", admin.tokenSourceName || "-"],
        ["Token length", admin.tokenLength || 0]
      ]), { span: 5, tag: admin.enabled ? "LOCAL_FULL" : "READ_ONLY" }),
      panel("Audit events", "Recent audit-style tenant events from snapshot.", list(derived().events, "No events returned by snapshot."), { span: 7, tag: `${(derived().events || []).length} events` }),
      panel("Endpoint redaction", "Backend responses are redacted before they reach the browser.", jsonBlock({ mode: state.data?.mode, admin, source: state.data?.source, endpointNames: Object.keys(endpoints()) }), { span: 12 })
    ].join("");
  }

  function renderSystem() {
    const modules = state.contract?.modules || [];
    const events = state.runtime?.events || [];
    return [
      panel("Diagnostics", "Technical diagnostics live here, away from the main command face.", `<div class="cc-actions"><button class="cc-action" data-action="export-diagnostics">Export diagnostics</button><button class="cc-action" data-action="refresh">Refresh</button></div><div id="diagnosticsResult"></div>`, { span: 4, tag: state.health?.overall || state.health?.status || "SYSTEM" }),
      panel("Runtime events", "Latest local runtime messages.", list(events.slice(-12).reverse().map((item) => [item.time || item.ts || "event", item.message || item.kind || JSON.stringify(item).slice(0, 120)]), "No runtime events."), { span: 4, tag: `${events.length} events` }),
      panel("Module contract", "Legacy module contract retained as technical evidence only.", list(modules.map((m) => [m.name || m.id, `${m.statusLabel || "-"} · ${m.port || "-"}`])), { span: 4, tag: `${modules.length} modules` }),
      panel("System raw", "Redacted runtime and health payloads.", jsonBlock({ health: state.health, runtime: state.runtime, contract: state.contract }), { span: 12 })
    ].join("");
  }

  const renderers = {
    command: renderCommand,
    customers: renderCustomers,
    entitlements: renderEntitlements,
    fleet: renderFleet,
    provisioning: renderProvisioning,
    contracts: renderContracts,
    operations: renderOperations,
    support: renderSupport,
    security: renderSecurity,
    system: renderSystem
  };

  function render() {
    updateChrome();
    updateSurfaceHeader();
    const renderer = renderers[state.surface] || renderCommand;
    $("surfaceRoot").innerHTML = renderer();
  }

  async function loadAll() {
    const [data, license, health, runtime, contract] = await Promise.all([
      safeApi("/api/cloud-saas/summary"),
      safeApi("/api/license-ops/latest"),
      safeApi("/api/health"),
      safeApi("/api/runtime"),
      safeApi("/api/contract")
    ]);
    state.data = data;
    state.license = license;
    state.health = health;
    state.runtime = runtime;
    state.contract = contract;
    render();
  }

  async function postAction(path, body) {
    return api(path, { method: "POST", body: JSON.stringify(body || {}) });
  }

  async function handleAction(action, button) {
    if (state.busy) return;
    state.busy = true;
    if (button) button.disabled = true;
    try {
      let result;
      if (action === "refresh") {
        await loadAll();
        toast("Command Center refreshed");
        return;
      }
      if (action === "create-note") {
        const text = $("supportNoteText")?.value || "Operator note from PRISMA Cloud Command Center.";
        result = await postAction("/api/cloud-saas/notes", { text });
        $("supportNoteResult").innerHTML = jsonBlock(result);
        toast(result.ok ? "Support note created" : "Support note reviewed");
      } else if (action === "receipt-smoke") {
        result = await postAction("/api/cloud-saas/receipt-smoke", {});
        ["provisioningResult", "contractReceiptResult"].forEach((id) => { if ($(id)) $(id).innerHTML = jsonBlock(result); });
        toast(result.ok ? "Receipt smoke sent" : "Receipt smoke blocked");
      } else if (action === "device-smoke") {
        result = await postAction("/api/cloud-saas/device-register-smoke", {});
        ["deviceSmokeResult", "provisioningResult"].forEach((id) => { if ($(id)) $(id).innerHTML = jsonBlock(result); });
        toast(result.ok ? "Device smoke sent" : "Device smoke blocked");
      } else if (action === "export-diagnostics") {
        result = await postAction("/api/export-diagnostics", {});
        $("diagnosticsResult").innerHTML = jsonBlock(result);
        toast("Diagnostics exported");
      }
      await loadAll();
    } catch (error) {
      toast(String(error.message || error));
      const payload = error.payload || { ok: false, error: String(error.message || error) };
      ["supportNoteResult", "provisioningResult", "contractReceiptResult", "deviceSmokeResult", "diagnosticsResult"].forEach((id) => {
        if ($(id)) $(id).innerHTML = jsonBlock(payload);
      });
    } finally {
      state.busy = false;
      if (button) button.disabled = false;
    }
  }

  function boot() {
    $$(".cc-nav button").forEach((button) => {
      button.addEventListener("click", () => {
        state.surface = button.dataset.surface || "command";
        render();
      });
    });
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-action]");
      if (!button) return;
      handleAction(button.dataset.action, button);
    });
    loadAll();
    setInterval(loadAll, 30000);
  }

  window.addEventListener("DOMContentLoaded", boot);
})();
