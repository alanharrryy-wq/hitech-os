(function () {
  "use strict";

  const VIEWS = [
    ["overview", "Cloud SaaS"],
    ["licenses", "Licencias"],
    ["tenants", "Tenants"],
    ["devices", "Devices"],
    ["snapshots", "Snapshots"],
    ["notes", "Notes"],
    ["receipts", "Receipts"],
    ["contract", "LICFLOW3"],
    ["health", "Health"],
    ["commercial", "Commercial"]
  ];
  const FIRST_CUSTOMER_NAME = "Prisma Original Customer";
  const FIRST_TENANT_SLUG = "prisma-original-customer";

  let state = { root: null, data: null, license: null, view: "overview", busy: false };

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;"
    }[ch]));
  }

  function json(value) {
    return esc(JSON.stringify(value ?? {}, null, 2));
  }

  async function api(path, options) {
    const response = await fetch(path, {
      cache: "no-store",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      ...(options || {})
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || payload.reason || `${path} ${response.status}`);
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function tone(value) {
    const raw = String(value || "").toUpperCase();
    if (raw.includes("LIVE") || raw.includes("FULL") || raw.includes("READY") || raw === "ACTIVE" || raw === "OK" || raw === "PASS") return "cloudSaasOk";
    if (raw.includes("READ_ONLY") || raw.includes("PARTIAL") || raw.includes("PENDING") || raw.includes("MISSING") || raw.includes("WARN")) return "cloudSaasWarn";
    if (raw.includes("FAIL") || raw.includes("ERROR") || raw.includes("OFFLINE") || raw.includes("FORBIDDEN")) return "cloudSaasBad";
    return "";
  }

  function card(kicker, title, body, tag) {
    return `<section class="cloudSaasCard">
      <div class="cloudSaasCardHead"><div><span>${esc(kicker)}</span><h3>${esc(title)}</h3></div>${tag ? `<b class="${tone(tag)}">${esc(tag)}</b>` : ""}</div>
      ${body}
    </section>`;
  }

  function row(label, value) {
    return `<div class="cloudSaasRow"><small>${esc(label)}</small><strong>${esc(value ?? "-")}</strong></div>`;
  }

  function rows(items) {
    return `<div class="cloudSaasRows">${items.map(([label, value]) => row(label, value)).join("")}</div>`;
  }

  function listRows(items, emptyLabel) {
    const list = Array.isArray(items) ? items : [];
    if (!list.length) return rows([["Estado", emptyLabel || "Sin datos disponibles"]]);
    return `<div class="cloudSaasRows">${list.slice(0, 16).map((item, index) => {
      const title = item && typeof item === "object" ? (item.name || item.displayName || item.id || item.slug || item.receiptId || item.deviceId || `Item ${index + 1}`) : item;
      const detail = item && typeof item === "object" ? (item.status || item.kind || item.createdAt || item.updatedAt || item.plan || "") : "";
      return row(title, detail || JSON.stringify(item).slice(0, 140));
    }).join("")}</div>`;
  }

  function renderHero() {
    const data = state.data || {};
    const derived = data.derived || {};
    const admin = data.admin || {};
    return `<section class="cloudSaasHero">
      <div>
        <h2>Prisma Cloud Ctr</h2>
        <p>${esc(derived.service || "PRISMA Cloud Semilla")} · ${esc(derived.version || "-")} · ${esc(data.cloud?.baseUrl || "https://app.hitechrts.com")}</p>
      </div>
      <div class="cloudSaasMode">
        ${row("Modo", data.mode || "READ_ONLY")}
        ${row("adminTokenPresent", admin.adminTokenPresent ? "true" : "false")}
      </div>
    </section>`;
  }

  function renderTabs() {
    return `<nav class="cloudSaasTabs" aria-label="Cloud SaaS views">${VIEWS.map(([id, label]) => `<button type="button" class="${state.view === id ? "active" : ""}" data-cloud-saas-view="${esc(id)}">${esc(label)}</button>`).join("")}</nav>`;
  }

  function endpointCard(name, label) {
    const endpoint = state.data?.endpoints?.[name] || {};
    return card(label, endpoint.ok ? "OK" : (endpoint.status || endpoint.statusCode || "REVIEW"), rows([
      ["HTTP", endpoint.statusCode ?? "-"],
      ["Latencia", endpoint.latencyMs != null ? `${endpoint.latencyMs} ms` : "-"],
      ["Ruta", endpoint.url || "-"]
    ]), endpoint.ok ? "PASS" : (endpoint.status || "WARN"));
  }

  function overview() {
    const derived = state.data?.derived || {};
    const counts = derived.counts || {};
    return `<div class="cloudSaasGrid">
      ${card("Cloud", derived.service || "PRISMA Cloud Semilla", rows([["Version", derived.version || "-"], ["Tenant", derived.tenant?.slug || FIRST_TENANT_SLUG], ["DB", derived.dbHealth ? JSON.stringify(derived.dbHealth).slice(0, 90) : "-"]]), state.data?.mode)}
      ${card("Counts", "Resumen vivo", rows([["Tenants", counts.tenants ?? "-"], ["Devices", counts.devices ?? "-"], ["Licencias activas", counts.activeLicenses ?? "-"], ["Activation codes", counts.activeActivationCodes ?? "-"]]), "LIVE")}
      ${card("Tenant", derived.tenant?.displayName || derived.tenant?.slug || FIRST_CUSTOMER_NAME, rows([["Status", derived.tenant?.status || "-"], ["Plan", derived.tenant?.plan || "-"], ["License", derived.license?.status || "-"]]), derived.tenant?.status || "REVIEW")}
      ${card("LICFLOW3", state.data?.licflow3Contract?.claim || "routes_live", rows([["Estado", state.data?.licflow3Contract?.hostedCloudEvidenceStatus || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE"], ["Worker", state.data?.licflow3Contract?.worker || "prisma-cloud-semilla"], ["D1", state.data?.licflow3Contract?.d1 || "prisma_cloud_semilla"]]), state.data?.licflow3Contract?.hostedCloudEvidenceStatus || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE")}
      ${endpointCard("health", "Health")}
      ${endpointCard("capabilities", "Capabilities")}
      ${endpointCard("tenantStatus", "Tenant Status")}
    </div>`;
  }

  function licenses() {
    const derived = state.data?.derived || {};
    const licenseRoot = `<div id="cloudLicenseOpsMount"></div>`;
    return `<div class="cloudSaasGrid two">
      ${card("Cloud license", derived.license?.status || "REVIEW", rows([["Plan", derived.license?.plan || "-"], ["Allowed", derived.license?.allowed ?? "-"], ["Max devices", derived.license?.maxDevices ?? "-"], ["Expires", derived.license?.expiresAt || "-"]]), derived.license?.status || "REVIEW")}
      ${card("Local license ops", "3150 adapter", licenseRoot, state.license?.status || "READ_ONLY")}
    </div>`;
  }

  function tenants() {
    const derived = state.data?.derived || {};
    return `<div class="cloudSaasGrid two">
      ${card(`Tenant ${FIRST_CUSTOMER_NAME}`, derived.tenant?.displayName || derived.tenant?.slug || FIRST_CUSTOMER_NAME, rows([["Slug", derived.tenant?.slug || FIRST_TENANT_SLUG], ["Status", derived.tenant?.status || "-"], ["Plan", derived.tenant?.plan || "-"]]), derived.tenant?.status || "REVIEW")}
      ${card("Public contract", "Contrato cliente", `<pre class="cloudSaasJson">${json(derived.publicContract)}</pre>`, "READ")}
    </div>`;
  }

  function devices() {
    const enabled = !!state.data?.admin?.enabled;
    return `<div class="cloudSaasGrid two">
      ${card("Devices", "Registrados", listRows(state.data?.derived?.devices, "Snapshot admin no disponible"), "SNAPSHOT")}
      <section class="cloudSaasAction">
        <div class="cloudSaasCardHead"><div><span>SMOKE</span><h3>Device register</h3></div><b class="${enabled ? "cloudSaasOk" : "cloudSaasWarn"}">${enabled ? "LOCAL_FULL" : "READ_ONLY"}</b></div>
        <button type="button" data-cloud-action="device-register-smoke" ${enabled ? "" : "disabled"}>Mandar device smoke</button>
        <pre class="cloudSaasJson" id="cloudActionResult">-</pre>
      </section>
    </div>`;
  }

  function snapshots() {
    return `<div class="cloudSaasGrid two">
      ${endpointCard("tenantSnapshot", "Tenant Snapshot")}
      ${card("Snapshot JSON", FIRST_CUSTOMER_NAME, `<pre class="cloudSaasJson">${json(state.data?.derived?.snapshot)}</pre>`, "READ")}
    </div>`;
  }

  function notes() {
    const enabled = !!state.data?.admin?.enabled;
    return `<div class="cloudSaasGrid two">
      ${card("Notes", "Ultimas notas", listRows(state.data?.derived?.notes, "Sin notas o snapshot admin no disponible"), "SNAPSHOT")}
      <section class="cloudSaasAction">
        <div class="cloudSaasCardHead"><div><span>ADMIN</span><h3>Crear nota ${FIRST_CUSTOMER_NAME}</h3></div><b class="${enabled ? "cloudSaasOk" : "cloudSaasWarn"}">${enabled ? "LOCAL_FULL" : "READ_ONLY"}</b></div>
        <textarea id="cloudNoteText" ${enabled ? "" : "disabled"} placeholder="Nota interna para ${FIRST_CUSTOMER_NAME}"></textarea>
        <button type="button" data-cloud-action="notes" ${enabled ? "" : "disabled"}>Crear nota</button>
        <pre class="cloudSaasJson" id="cloudActionResult">-</pre>
      </section>
    </div>`;
  }

  function receipts() {
    const enabled = !!state.data?.admin?.enabled;
    return `<div class="cloudSaasGrid two">
      ${card("Receipts", "Ultimos recibos", listRows(state.data?.derived?.receipts, "Sin recibos o snapshot admin no disponible"), "SNAPSHOT")}
      <section class="cloudSaasAction">
        <div class="cloudSaasCardHead"><div><span>SMOKE</span><h3>Integration receipt</h3></div><b class="${enabled ? "cloudSaasOk" : "cloudSaasWarn"}">${enabled ? "LOCAL_FULL" : "READ_ONLY"}</b></div>
        <button type="button" data-cloud-action="receipt-smoke" ${enabled ? "" : "disabled"}>Mandar receipt smoke</button>
        <pre class="cloudSaasJson" id="cloudActionResult">-</pre>
      </section>
    </div>`;
  }

  function health() {
    return `<div class="cloudSaasGrid">
      ${endpointCard("health", "Health")}
      ${endpointCard("capabilities", "Capabilities")}
      ${endpointCard("adminSelftest", "Admin Selftest")}
      ${endpointCard("tenantStatus", "Tenant Status")}
      ${endpointCard("clientContract", "Client Contract")}
      ${endpointCard("supportDiagnostics", "Support Diagnostics")}
      ${card("Eventos", "Cloud snapshot", listRows(state.data?.derived?.events, "Sin eventos o snapshot admin no disponible"), "READ")}
    </div>`;
  }

  function contract() {
    const licflow3 = state.data?.licflow3Contract || {};
    const endpoints = Array.isArray(licflow3.endpoints) ? licflow3.endpoints : [];
    return `<div class="cloudSaasGrid two">
      ${card("LICFLOW3", licflow3.claim || "contract_incomplete", rows([
        ["Base", licflow3.configuredBaseUrl || state.data?.cloud?.baseUrl || "-"],
        ["Tenant", licflow3.tenantSlug || state.data?.cloud?.tenantSlug || FIRST_TENANT_SLUG],
        ["Faltantes", (licflow3.missing || []).join(", ") || "0"],
        ["Estado", licflow3.hostedCloudEvidenceStatus || licflow3.status || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE"],
        ["Worker", licflow3.worker || "prisma-cloud-semilla"],
        ["D1", licflow3.d1 || "prisma_cloud_semilla"],
        ["Smoke sin token", "401 protected-route response"]
      ]), licflow3.hostedCloudEvidenceStatus || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE")}
      ${card("Endpoints", "Contrato configurado", listRows(endpoints.map((item) => ({ name: item.key, status: `${item.configured ? "CONFIGURADO" : "FALTA"} ${item.method} ${item.configuredPath || item.path} · ${(item.routeTags || []).join(", ") || "sin-clasificacion"}` })), "Sin contrato LICFLOW3"), "CONTRACT")}
    </div>`;
  }

  function commercial() {
    return `<div class="cloudSaasGrid two">
      ${endpointCard("commercialSummary", "Commercial Summary")}
      ${card("Commercial JSON", "Resumen", `<pre class="cloudSaasJson">${json(state.data?.derived?.commercialSummary)}</pre>`, "ADMIN")}
    </div>`;
  }

  function content() {
    if (!state.data) return '<section class="cloudSaasCard"><h3>Cargando Cloud SaaS...</h3></section>';
    const views = { overview, licenses, tenants, devices, snapshots, notes, receipts, contract, health, commercial };
    const view = views[state.view] || overview;
    return view();
  }

  function wire() {
    state.root.querySelectorAll("[data-cloud-saas-view]").forEach((button) => {
      button.addEventListener("click", () => setView(button.dataset.cloudSaasView));
    });
    state.root.querySelectorAll("[data-cloud-action]").forEach((button) => {
      button.addEventListener("click", () => runAction(button.dataset.cloudAction));
    });
    const licenseMount = state.root.querySelector("#cloudLicenseOpsMount");
    if (licenseMount && window.PRISMA_LICENSE_OPS_LAB) {
      window.PRISMA_LICENSE_OPS_LAB.mount(licenseMount);
    }
  }

  function render() {
    if (!state.root) return;
    state.root.innerHTML = `<div class="cloudSaasCockpit">${renderHero()}${renderTabs()}${content()}</div>`;
    wire();
  }

  async function refresh() {
    if (!state.root || state.busy) return;
    state.busy = true;
    try {
      const [cloud, license] = await Promise.all([
        api("/api/cloud-saas/summary"),
        api("/api/license-ops/latest").catch(() => null)
      ]);
      state.data = cloud;
      state.license = license;
    } catch (error) {
      state.data = { mode: "ERROR", derived: { service: "PRISMA Cloud Semilla" }, admin: {}, cloud: {}, endpoints: {}, error: error.message || String(error) };
    } finally {
      state.busy = false;
      render();
    }
  }

  async function runAction(action) {
    const result = state.root && state.root.querySelector("#cloudActionResult");
    if (result) result.textContent = `Ejecutando ${action}...`;
    try {
      const body = action === "notes" ? { text: state.root.querySelector("#cloudNoteText")?.value || "" } : {};
      const payload = await api(`/api/cloud-saas/${encodeURIComponent(action)}`, { method: "POST", body: JSON.stringify(body) });
      if (result) result.textContent = JSON.stringify(payload, null, 2);
      await refresh();
    } catch (error) {
      if (result) result.textContent = JSON.stringify(error.payload || { ok: false, error: error.message || String(error) }, null, 2);
    }
  }

  function setView(view) {
    if (!VIEWS.some(([id]) => id === view)) return;
    state.view = view;
    render();
  }

  function mount(root, options) {
    state.root = typeof root === "string" ? document.getElementById(root) : root;
    if (!state.root) return;
    if (options && options.view) state.view = options.view;
    render();
    refresh();
  }

  window.PRISMA_CLOUD_SAAS = { mount, refresh, setView };
})();
