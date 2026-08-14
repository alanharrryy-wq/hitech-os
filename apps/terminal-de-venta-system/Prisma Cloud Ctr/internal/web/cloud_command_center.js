(function () {
  "use strict";

  const SURFACES = [
    ["command", "Inicio", "¿Qué quieres hacer?", "Acciones claras: nuevo cliente, licencia, dispositivo, baja, clientes activos y soporte sin leer JSON."],
    ["customers", "Clientes", "Clientes activos", "Busca, clasifica y prepara clientes con giros homologados, IDs automáticos y fichas claras."],
    ["entitlements", "Licencias", "Tipos y asignación", "Catálogo de planes, módulos permitidos, vigencia, límites e IDs de licencia generados solos."],
    ["fleet", "Dispositivos", "Agregar y administrar", "Tipos de dispositivo homologados, códigos de registro automáticos y acciones de vinculación."],
    ["provisioning", "Altas", "Alta guiada", "Wizard de alta: datos mínimos, vertical, plan, dispositivo y paquete preparado para activar."],
    ["customer-setup", "Prisma Customer Setup", "Setup multi-dispositivo", "Setup Link, Setup Code, Setup QR y Device Slots para Tablet POS, PC Admin y Mobile Companion."],
    ["contracts", "Contracts & Config", "Contrato y configuración", "Contrato actual, capacidades, diferencias visibles y resumen copiable."],
    ["operations", "Reportes", "Clientes activos y operación", "Conteos de clientes, licencias, dispositivos, pendientes y actividad preparada."],
    ["support", "Support", "Soporte", "Paquete de diagnóstico humano con cliente, licencia, contrato, dispositivos y siguiente acción."],
    ["security", "Bajas", "Baja segura", "Suspender, desactivar o preparar baja con motivo homologado, impacto visible y folio automático."],
    ["tablet-lab", "TABLET LAB", "Laboratorio visual Tablet", "Cápsula portable basada en Entitlements para preparar Tablet Light Cloudglass sin tocar Tablet real."],
    ["system", "System", "Cuarto de máquinas", "Runtime, endpoint matrix, selftest, diagnostics y evidencia técnica encerrada aquí."]
  ];
  const FIRST_CUSTOMER_NAME = "Prisma Original Customer";
  const FIRST_TENANT_SLUG = "prisma-original-customer";

  const SUPPORT_IDENTITY_CONTEXT = {
    businessId: "biz_prisma_rey_lineage_seed",
    customerId: "cust_demo",
    customer: {
      displayName: "Prisma Original Customer",
      customerId: "cust_prisma_original_customer",
      tenantId: "tenant_prisma_original_customer",
      licenseId: "lic_prisma_original_customer_001",
      planLabel: "Tablet + PC Managed",
      businessId: "biz_78b3c840796a4a4dad",
      storeId: "store_00728649f3804a9e82",
      storeName: "Sucursal principal",
      tabletTerminalId: "term_49103c7382d84663a3",
      tabletTerminalName: "Tablet Caja 1",
      secondaryTabletTerminalId: "term_064de66650df46e0b2",
      pcDeviceId: "pc_prisma_original_customer_001",
      tabletDeviceId: "tablet_prisma_original_customer_001",
      mobileDeviceId: "mobile_prisma_original_customer_001"
    },
    runtime: {
      businessId: "biz_prisma_rey_lineage_seed",
      storeId: "store_prisma_rey_centro",
      terminalId: "term_tablet_pos_001",
      deviceId: "tablet-pos-source-ready"
    },
    license: {
      businessId: "biz_demo",
      customerId: "cust_demo",
      licenseId: "lic_demo_tablet_pro",
      plan: "TABLET_PRO",
      state: "active"
    },
    technicalSources: ["PC/Admin diagnostic", "runtime.json", "license.json", "POS local DB", "signed activation package"]
  };

  const ADVANCED_SURFACES = new Set(["system"]);
  const state = {
    surface: "command",
    data: null,
    license: null,
    bridge: null,
    health: null,
    runtime: null,
    contract: null,
    busy: false,
    lastResult: null,
    lastLoadedAt: null,
    commandCenter: null,
    supportCatalog: null,
    supportSearch: null,
    supportDiagnosis: null,
    supportSimulation: null,
    flow: {},
    openPicker: null
  };

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
    if (Array.isArray(value)) return `${value.length} items`;
    if (typeof value === "object") return JSON.stringify(value).slice(0, 120);
    return String(value);
  }

  function formatStatusLabel(value) {
    return String(value || "")
      .replace(/[_-]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function tone(value) {
    const raw = String(value || "").toUpperCase();
    if (raw.includes("PASS") || raw.includes("OK") || raw.includes("READY") || raw.includes("LIVE") || raw.includes("ACTIVE") || raw.includes("FULL") || raw.includes("SAFE") || raw.includes("CLEAN")) return "ok";
    if (raw.includes("WARN") || raw.includes("READ_ONLY") || raw.includes("PARTIAL") || raw.includes("PENDING") || raw.includes("MISSING") || raw.includes("REVIEW") || raw.includes("CHECK")) return "warn";
    if (raw.includes("FAIL") || raw.includes("ERROR") || raw.includes("OFFLINE") || raw.includes("FORBIDDEN") || raw.includes("BLOCKED") || raw.includes("RISK")) return "bad";
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
    const classes = ["cc-panel", `cc-span-${span}`, opts?.className || ""].filter(Boolean).join(" ");
    return `<article class="${classes}">
      <div class="cc-panel-head"><div><h3>${esc(title)}</h3>${summary ? `<p>${esc(summary)}</p>` : ""}</div>${tag}</div>
      ${body || ""}
    </article>`;
  }

  function list(items, emptyLabel) {
    const rows = Array.isArray(items) ? items : [];
    if (!rows.length) return `<div class="cc-empty">${esc(emptyLabel || "No hay datos todavía")}</div>`;
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

  function details(label, value, open) {
    return `<details class="cc-details" ${open ? "open" : ""}><summary>${esc(label)}</summary>${jsonBlock(value)}</details>`;
  }

  function actionButton(action, label, variant) {
    const cls = ["cc-action", variant || ""].filter(Boolean).join(" ");
    return `<button class="${cls}" type="button" data-action="${esc(action)}">${esc(label)}</button>`;
  }

  function surfaceButton(surface, label) {
    return `<button class="cc-action ghost" type="button" data-go="${esc(surface)}">${esc(label)}</button>`;
  }

  function actions(items) {
    return `<div class="cc-actions">${items.join("")}</div>`;
  }

  function table(headers, rows, emptyLabel) {
    const safeRows = Array.isArray(rows) ? rows : [];
    if (!safeRows.length) return `<div class="cc-empty">${esc(emptyLabel || "Sin filas")}</div>`;
    return `<div class="cc-table-wrap"><table class="cc-support-table"><thead><tr>${headers.map((header) => `<th>${esc(header)}</th>`).join("")}</tr></thead><tbody>${safeRows.map((row) => `<tr>${headers.map((header) => `<td>${esc(compact(row[header] ?? row[header.replace(/\s+/g, "")] ?? row[header.toLowerCase()] ?? ""))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  }

  function derived() {
    return state.data?.derived || {};
  }

  function endpoints() {
    return state.data?.endpoints || {};
  }

  function endpointState(name) {
    const endpoint = endpoints()[name] || {};
    const code = endpoint.statusCode || endpoint.status || (endpoint.ok ? "OK" : "CHECK");
    const ms = endpoint.latencyMs != null ? `${endpoint.latencyMs} ms` : "-";
    return { code, ms, ok: !!endpoint.ok, raw: endpoint };
  }

  function contractEndpoint(name) {
    return (state.data?.licflow3Contract?.endpoints || []).find((item) => item.key === name) || null;
  }

  const LICFLOW3_ENDPOINT_MATRIX = ["health", "capabilities", "tenantStatus", "adminSelftest", "commercialSummary", "tenantSnapshot", "clientContract", "supportDiagnostics", "licenseActivate", "licenseRefresh", "licenseRevoke", "deviceRegister", "integrationReceipt", "customerSetupCreate", "customerSetupResolve", "customerDeviceClaim", "customerLicenseStatus"];

  function licflow3LiveStatus() {
    return state.data?.licflow3Contract?.statusDisplay || state.data?.licflow3Contract?.hostedCloudEvidenceStatus || state.data?.licflow3Contract?.status || "Cloud License Gateway: Live";
  }

  function adminTokenPresent() {
    return !!state.data?.admin?.adminTokenPresent;
  }

  function licflow4Bridge() {
    return state.bridge || {};
  }

  function endpointRows(names) {
    const labels = {
      health: "Salud cloud",
      capabilities: "Capacidades públicas",
      tenantStatus: "Estado público del cliente",
      adminSelftest: "Diagnóstico administrativo",
      commercialSummary: "Resumen comercial",
      tenantSnapshot: "Estado completo del cliente",
      clientContract: "Contrato cliente",
      supportDiagnostics: "Diagnóstico soporte",
      licenseActivate: "Activar licencia",
      licenseRefresh: "Refrescar licencia",
      licenseRevoke: "Revocar licencia",
      deviceRegister: "Registrar dispositivo",
      integrationReceipt: "Recibo integración",
      customerSetupCreate: "Crear Prisma Customer Setup",
      customerSetupResolve: "Resolver Setup Code",
      customerDeviceClaim: "Device Claim cliente",
      customerLicenseStatus: "Estado licencia cliente"
    };
    return names.map((name) => {
      const item = endpointState(name);
      const contract = contractEndpoint(name);
      if (!item.raw?.name && contract) {
        const status = contract.configured ? "CONFIGURADO" : "FALTA";
        const guard = contract.mutatesCloud ? "sin autocall" : (contract.safeSummaryCall ? "summary" : "manual");
        return [labels[name] || name, `${status} · ${contract.method} ${contract.configuredPath || contract.path} · ${guard}`];
      }
      return [labels[name] || name, `${item.code} · ${item.ms}`];
    });
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

  async function safePost(path, body) {
    try {
      return await api(path, { method: "POST", body: JSON.stringify(body || {}) });
    } catch (error) {
      return { ok: false, path, error: String(error.message || error), payload: error.payload || null, secretsExposed: false };
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

  function setResult(title, message, payload, opts) {
    state.lastResult = {
      surface: opts?.surface || state.surface,
      title,
      message,
      payload: payload || {},
      kind: opts?.kind || (payload?.ok === false ? "warn" : "ok"),
      time: new Date().toLocaleString()
    };
  }

  function resultPanel() {
    const result = state.lastResult;
    if (!result || result.surface !== state.surface) return "";
    const body = `<div class="cc-result-card ${tone(result.kind)}"><strong>${esc(result.message)}</strong><small>${esc(result.time)}</small></div>${details("Ver evidencia técnica", result.payload, ADVANCED_SURFACES.has(state.surface))}`;
    return panel(result.title || "Último resultado", "Resultado claro de la última acción en esta superficie.", body, { span: 12, tag: result.kind || "OK" });
  }

  function safeCount(value) {
    return Array.isArray(value) ? value.length : 0;
  }

  function mainStatus() {
    const d = derived();
    const admin = state.data?.admin || {};
    const problems = collectProblems();
    if (!state.data) return "Cargando";
    if (problems.some((p) => p.level === "bad")) return "Riesgo";
    if (!admin.enabled) return "Lectura segura";
    if (state.data.ok) return "Operable";
    return "Revisión";
  }

  function collectProblems() {
    const data = state.data || {};
    const d = derived();
    const admin = data.admin || {};
    const found = [];
    if (!data.ok) found.push({ level: "warn", title: "Cloud requiere revisión", detail: data.error || data.status || "No hay PASS completo en resumen." });
    if (!endpointState("health").ok) found.push({ level: "bad", title: "Salud cloud no confirmó OK", detail: "Revisar System para detalle técnico." });
    if (!endpointState("tenantStatus").ok) found.push({ level: "warn", title: "Estado público del cliente incompleto", detail: `No se pudo confirmar status público de ${FIRST_CUSTOMER_NAME}.` });
    if (data.licflow3Contract?.missing?.length) found.push({ level: "warn", title: "Cloud License Gateway contract incomplete", detail: `Faltan endpoints: ${data.licflow3Contract.missing.join(", ")}.` });
    if (!d.license && !state.license?.runtime?.license) found.push({ level: "warn", title: "Licencia sin ficha clara", detail: "Falta estado de licencia legible para operación." });
    if (!safeCount(d.devices)) found.push({ level: "warn", title: "Sin dispositivos visibles", detail: "El snapshot no devolvió dispositivos." });
    return found;
  }

  function problemsHtml() {
    const problems = collectProblems();
    if (!problems.length) return `<div class="cc-empty">Sin problemas graves detectados. La cabina se ve operable.</div>`;
    return `<div class="cc-list cc-problem-list">${problems.map((p) => `<div class="cc-row cc-problem ${esc(p.level)}"><span>${esc(p.title)}<small>${esc(p.detail)}</small></span><strong>${esc(p.level === "bad" ? "Atender" : "Revisar")}</strong></div>`).join("")}</div>`;
  }

  function executiveSummary() {
    const d = derived();
    const license = state.license?.runtime?.license || d.license || {};
    const problems = collectProblems();
    return [
      "Prisma Cloud Center",
      `Estado general: ${mainStatus()}`,
      `Cloud: ${state.data?.ok ? "en línea" : "revisar"}`,
      `Cliente: ${d.tenant?.displayName || d.tenant?.slug || state.data?.cloud?.tenantSlug || FIRST_CUSTOMER_NAME}`,
      `Licencia: ${license.status || d.license?.status || state.license?.status || "revisar"}`,
      `Plan: ${license.plan || d.license?.plan || "-"}`,
      `Cloud License Gateway: ${state.data?.licflow3Contract?.claim || "contract_incomplete"}`,
      `Cloud License Gateway status: ${licflow3LiveStatus()}`,
      `Worker: ${state.data?.licflow3Contract?.worker || "prisma-cloud-semilla"}`,
      `D1: ${state.data?.licflow3Contract?.d1 || "prisma_cloud_semilla"}`,
      `Admin Token Status: ${adminTokenPresent() ? "presence-only" : "missing"}`,
      `Dispositivos: ${safeCount(d.devices)}`,
      `Receipts: ${safeCount(d.receipts)}`,
      `Notas: ${safeCount(d.notes)}`,
      `Problemas: ${problems.length ? problems.map((p) => p.title).join("; ") : "sin bloqueadores visibles"}`,
      `Siguiente acción: ${problems.length ? "abrir Ver problemas y atender el primer punto" : "seguir monitoreando / operar normal"}`
    ].join("\n");
  }

  function customerSummary() {
    const d = derived();
    const commercial = d.commercialSummary || {};
    return [
      `Cliente: ${d.tenant?.displayName || d.tenant?.slug || FIRST_CUSTOMER_NAME}`,
      `Estado: ${d.tenant?.status || "revisar"}`,
      `Plan: ${d.tenant?.plan || d.license?.plan || "-"}`,
      `Licencia: ${d.license?.status || state.license?.runtime?.license?.status || "revisar"}`,
      `Notas: ${safeCount(d.notes)}`,
      `Receipts: ${safeCount(d.receipts)}`,
      `Eventos: ${safeCount(d.events)}`,
      `Resumen comercial: ${compact(commercial.status || commercial.summary || commercial.total || "disponible en detalle técnico")}`
    ].join("\n");
  }

  function supportPacket() {
    const d = derived();
    const license = state.license?.runtime?.license || d.license || {};
    const contract = d.publicContract || {};
    const problems = collectProblems();
    const issue = state.supportDiagnosis?.primaryIssueCode || state.supportSearch?.events?.[0]?.issue || "sin codigo principal";
    return [
      "PAQUETE DE SOPORTE PRISMA",
      `Cliente: ${d.tenant?.displayName || d.tenant?.slug || FIRST_CUSTOMER_NAME}`,
      `Estado cliente: ${d.tenant?.status || "revisar"}`,
      `Licencia: ${license.status || "revisar"}`,
      `Plan: ${license.plan || d.license?.plan || "-"}`,
      `Contrato: ${contract.status || contract.plan || endpointState("clientContract").code}`,
      `Cloud License Gateway: ${state.data?.licflow3Contract?.claim || "contract_incomplete"}`,
      `Cloud License Gateway status: ${licflow3LiveStatus()}`,
      `Admin Token Status: ${adminTokenPresent() ? "presence-only" : "missing"}`,
      `Soporte cloud: ${endpointState("supportDiagnostics").code}`,
      `Issue principal: ${issue}`,
      `Dispositivos: ${safeCount(d.devices)}`,
      `Receipts: ${safeCount(d.receipts)}`,
      `Notas: ${safeCount(d.notes)}`,
      `Problemas detectados: ${problems.length ? problems.map((p) => p.title).join("; ") : "sin bloqueadores visibles"}`,
      `Siguiente acción sugerida: ${problems.length ? problems[0].detail : "confirmar operación normal con cliente"}`
    ].join("\n");
  }

  async function copyText(text, label) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
      }
      setResult("Copiado", `${label || "Texto"} copiado al portapapeles.`, { ok: true, text }, { kind: "ok" });
      toast(`${label || "Texto"} copiado`);
    } catch (error) {
      setResult("Copia manual", "No se pudo usar el portapapeles; copia desde la evidencia técnica.", { ok: false, text, error: String(error.message || error) }, { kind: "warn" });
      toast("Copia manual requerida");
    }
    render();
  }

  function updateChrome() {
    const data = state.data || {};
    const d = derived();
    const admin = data.admin || {};
    $("ccMode").textContent = formatStatusLabel(data.mode || "Lectura segura");
    $("ccMode").className = `cc-chip ${tone(data.mode)}`;
    $("ccCloud").textContent = data.ok ? "Cloud en línea" : "Cloud a revisar";
    $("ccCloud").className = `cc-chip ${data.ok ? "ok" : "warn"}`;
    $("ccAdmin").textContent = admin.enabled ? "Acciones activas" : "Sólo lectura";
    $("ccAdmin").className = `cc-chip ${admin.enabled ? "ok" : "warn"}`;
    $("metricHealth").textContent = endpointState("health").code || data.status || (data.ok ? "OK" : "CHECK");
    $("metricTenant").textContent = d.tenant?.slug || d.tenant?.id || data.cloud?.tenantSlug || FIRST_TENANT_SLUG;
    $("metricLicense").textContent = d.license?.status || state.license?.runtime?.license?.status || state.license?.status || "Revisar";
    $("metricEvidence").textContent = `${safeCount(d.notes)} notas / ${safeCount(d.receipts)} receipts`;
  }

  function updateSurfaceHeader() {
    const spec = SURFACES.find(([id]) => id === state.surface) || SURFACES[0];
    $("surfaceKicker").textContent = spec[1];
    $("surfaceTitle").textContent = spec[2];
    $("surfaceSummary").textContent = spec[3];
    $("surfacePrimary").textContent = derived().tenant?.slug || state.data?.cloud?.tenantSlug || FIRST_TENANT_SLUG;
    $("surfaceScore").textContent = mainStatus();
    $$(".cc-nav button").forEach((button) => button.classList.toggle("active", button.dataset.surface === state.surface));
  }


  // C C L A B 6 O P T: guarded catalog fallback + normalization.
  // C C L A B 7 S E L: visible catalog chips, default selection and cache-bust trace.
  // If /api/command-center/bootstrap is unavailable, dropdowns still show governed options.
  const FALLBACK_CATALOGS = {
    vertical: { code: "vertical", label: "Giro / vertical", allowOther: true, options: [
      { code: "retail", label: "Retail", metadata: { suggestedPlan: "starter", modules: ["pos","inventory","tickets","cash_cuts"] } },
      { code: "abarrotes", label: "Abarrotes / minisuper", metadata: { suggestedPlan: "starter", modules: ["pos","inventory","tickets","cash_cuts"] } },
      { code: "restaurant", label: "Restaurante / food service", metadata: { suggestedPlan: "business", modules: ["pos","tables","tickets","cash_cuts"] } },
      { code: "bar", label: "Bar", metadata: { suggestedPlan: "business", modules: ["pos","tables","tickets","cash_cuts"] } },
      { code: "pharmacy", label: "Farmacia", metadata: { suggestedPlan: "business", modules: ["pos","inventory","batch_tracking","tickets"] } },
      { code: "hardware", label: "Ferretería", metadata: { suggestedPlan: "business", modules: ["pos","inventory","quotes","tickets"] } },
      { code: "fashion", label: "Moda / boutique", metadata: { suggestedPlan: "starter", modules: ["pos","inventory","tickets"] } },
      { code: "butcher", label: "Carnicería", metadata: { suggestedPlan: "business", modules: ["pos","scale_support","inventory","tickets"] } },
      { code: "tortilla", label: "Tortillería", metadata: { suggestedPlan: "starter", modules: ["pos","tickets","cash_cuts"] } },
      { code: "services", label: "Servicios", metadata: { suggestedPlan: "starter", modules: ["pos","tickets","appointments"] } },
      { code: "multi_branch", label: "Multi-sucursal", metadata: { suggestedPlan: "enterprise", modules: ["pos","inventory","multi_branch","reports"] } },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] },
    subvertical: { code: "subvertical", label: "Subvertical", allowOther: true, options: [
      { code: "minisuper", label: "Minisuper", metadata: {} },
      { code: "specialty_store", label: "Tienda especializada", metadata: {} },
      { code: "restaurant_tables", label: "Restaurante con mesas", metadata: {} },
      { code: "quick_service", label: "Comida rápida", metadata: {} },
      { code: "coffee_shop", label: "Cafetería", metadata: {} },
      { code: "workshop", label: "Taller", metadata: {} },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] },
    business_size: { code: "business_size", label: "Tamaño", allowOther: false, options: [
      { code: "small", label: "Pequeño", metadata: { maxBranches: 1 } },
      { code: "medium", label: "Mediano", metadata: { maxBranches: 3 } },
      { code: "multi_branch", label: "Multi-sucursal", metadata: { maxBranches: 99 } }
    ] },
    operation_mode: { code: "operation_mode", label: "Tipo de operación", allowOther: true, options: [
      { code: "counter", label: "Mostrador", metadata: {} },
      { code: "inventory", label: "Mostrador + inventario", metadata: {} },
      { code: "tables", label: "Mesas", metadata: {} },
      { code: "services", label: "Servicios / citas", metadata: {} },
      { code: "mixed", label: "Mixto", metadata: {} },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] },
    license_plan: { code: "license_plan", label: "Tipo de licencia", allowOther: false, options: [
      { code: "TABLET_SOLO", label: "Tablet Solo", metadata: { maxDevices: 1, maxBranches: 1, modules: ["pos.open","pos.sale.complete","report.today.view"], source: "shared/licensing/plan-catalog.canonical.json" } },
      { code: "TABLET_PRO", label: "Tablet Pro", metadata: { maxDevices: 2, maxBranches: 1, modules: ["pos.open","pos.sale.complete","event.outbox.view","export.advanced"], source: "shared/licensing/plan-catalog.canonical.json" } },
      { code: "TABLET_PC_MANAGED", label: "Tablet + PC Managed", metadata: { maxDevices: 4, maxBranches: 1, modules: ["pos.open","event.outbox.view","pc.open","sync.managed"], source: "shared/licensing/plan-catalog.canonical.json" } }
    ] },
    device_type: { code: "device_type", label: "Tipo de dispositivo", allowOther: true, options: [
      { code: "tablet_pos", label: "Tablet POS", metadata: {} },
      { code: "pc_register", label: "Caja PC", metadata: {} },
      { code: "mobile", label: "Terminal móvil", metadata: {} },
      { code: "backoffice", label: "Backoffice", metadata: {} },
      { code: "kiosk", label: "Kiosko", metadata: {} },
      { code: "printer", label: "Impresora / periférico", metadata: {} },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] },
    deactivation_reason: { code: "deactivation_reason", label: "Motivo de baja", allowOther: true, options: [
      { code: "cancelation", label: "Cancelación", metadata: {} },
      { code: "non_payment", label: "Falta de pago", metadata: {} },
      { code: "demo_finished", label: "Fin de piloto", metadata: {} },
      { code: "device_replacement", label: "Cambio de dispositivo", metadata: {} },
      { code: "duplicate_client", label: "Cliente duplicado", metadata: {} },
      { code: "migration", label: "Migración", metadata: {} },
      { code: "support", label: "Soporte técnico", metadata: {} },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] },
    city_zone: { code: "city_zone", label: "Ciudad / zona", allowOther: true, options: [
      { code: "local", label: "Local / misma ciudad", metadata: {} },
      { code: "regional", label: "Regional", metadata: {} },
      { code: "remote", label: "Remoto", metadata: {} },
      { code: "other", label: "Otro", metadata: { requiresManualText: true } }
    ] }
  };

  function ccStore(){ return state.commandCenter || {}; }
  function normalizeCatalogOption(item){
    const code = String(item?.code ?? item?.value ?? item?.optionCode ?? item?.id ?? "").trim();
    if (!code) return null;
    const label = String(item?.label ?? item?.name ?? item?.optionLabel ?? code).trim() || code;
    let metadata = item?.metadata || {};
    if (typeof metadata === "string") {
      try { metadata = JSON.parse(metadata); } catch (_) { metadata = {}; }
    }
    return { ...item, code, label, metadata, active: item?.active !== false };
  }
  function normalizeCatalog(cat, fallback){
    const base = fallback || {};
    const rawOptions = Array.isArray(cat?.options) ? cat.options : [];
    const normalizedOptions = rawOptions.map(normalizeCatalogOption).filter(Boolean);
    const options = normalizedOptions.length ? normalizedOptions : (base.options || []);
    return {
      ...base,
      ...cat,
      code: cat?.code || base.code,
      label: cat?.label || cat?.name || base.label || cat?.code || base.code,
      allowOther: Boolean(cat?.allowOther ?? base.allowOther),
      options
    };
  }
  function catalogs(){
    const raw = ccStore().catalogs || {};
    const merged = {};
    Object.keys(FALLBACK_CATALOGS).forEach((code) => {
      merged[code] = normalizeCatalog(raw[code], FALLBACK_CATALOGS[code]);
    });
    Object.keys(raw).forEach((code) => {
      if (!merged[code]) merged[code] = normalizeCatalog(raw[code], { code, label: code, allowOther: false, options: [] });
    });
    return merged;
  }
  function catalogOptions(code){ return (catalogs()[code]?.options || []).filter((item)=>item.active !== false); }
  function catalogLabel(code,value){ return catalogOptions(code).find((opt)=>opt.code===value)?.label || value || "-"; }
  function flowValue(key,fallback){ return state.flow[key] || fallback || ""; }
  function planMeta(code){ return catalogOptions("license_plan").find((item)=>item.code===code)?.metadata || {}; }
const BILLING_PERIOD_LABELS = { monthly: "Mensual", quarterly: "Trimestral", semiannual: "Semestral", annual: "Anual" };
function moneyMxn(value){ const n=Number(value); if(!Number.isFinite(n)) return "-"; return new Intl.NumberFormat("es-MX",{style:"currency",currency:"MXN",maximumFractionDigits:0}).format(n); }
function planCommercial(code){ const meta=planMeta(code); return meta.commercial || (ccStore().licensePlans||[]).find((item)=>item.code===code)?.commercial || {}; }
function planCommercialPolicy(code){ const meta=planMeta(code); return meta.commercialPolicy || (ccStore().licensePlans||[]).find((item)=>item.code===code)?.commercialPolicy || {}; }
function planListPrice(code,period){ return planCommercial(code)?.listPriceMxn?.[period] ?? null; }
function billingPeriodField(){ const selected=flowValue("billingPeriod","monthly"); return `<label class="cc-field"><span>Periodicidad</span><select data-flow-field="billingPeriod">${Object.entries(BILLING_PERIOD_LABELS).map(([code,label])=>`<option value="${esc(code)}" ${selected===code?"selected":""}>${esc(label)}</option>`).join("")}</select></label>`; }
function priceTreatmentField(){ const selected=flowValue("priceTreatment","canonical_list"); const opts=[["canonical_list","Precio de lista"],["signed_contract_override","Precio firmado excepcional"],["grandfathered_contract","Contrato anterior / grandfathered"]]; return `<label class="cc-field"><span>Tratamiento del precio</span><select data-flow-field="priceTreatment">${opts.map(([code,label])=>`<option value="${esc(code)}" ${selected===code?"selected":""}>${esc(label)}</option>`).join("")}</select></label>`; }
  function catalogMetaSummary(item){
    const meta = item?.metadata || {};
    const parts = [];
    if (meta.category) parts.push(meta.category);
    if (meta.family) parts.push(meta.family);
    if (meta.suggestedPlan) parts.push(`Plan ${catalogLabel("license_plan", meta.suggestedPlan)}`);
    if (Array.isArray(meta.modules) && meta.modules.length) parts.push(`${meta.modules.length} módulos`);
    if (meta.maxDevices) parts.push(`${meta.maxDevices} disp.`);
    if (meta.maxBranches) parts.push(`${meta.maxBranches} suc.`);
    if (item?.code === "other") parts.push("Manual");
    return parts.slice(0,3).join(" · ") || "Homologado";
  }
  function catalogTableRows(fieldId,catalogCode,effectiveSelected){
    const options = catalogOptions(catalogCode);
    if (!options.length) return `<div class="cc-catalog-empty">Sin opciones cargadas. La cabina usará fallback local cuando esté disponible.</div>`;
    return options.map((item)=>{
      const selected = item.code === effectiveSelected;
      const search = `${item.label} ${item.code} ${catalogMetaSummary(item)}`.toLowerCase();
      return `<button type="button" class="cc-catalog-row ${selected?"active":""}" data-pick-flow="${esc(fieldId)}" data-value="${esc(item.code)}" data-picker-search="${esc(search)}"><span class="cc-catalog-name">${esc(item.label)}</span><span class="cc-catalog-meta">${esc(catalogMetaSummary(item))}</span><span class="cc-catalog-code">${esc(item.code)}</span></button>`;
    }).join("");
  }
  function selectField(id,label,catalogCode,selected,opts){
    const options=catalogOptions(catalogCode);
    const allowOther=!!catalogs()[catalogCode]?.allowOther;
    const effectiveSelected=selected || opts?.defaultValue || options[0]?.code || "";
    const selectedLabel=catalogLabel(catalogCode,effectiveSelected) || "Selecciona";
    const rows=[`<option value="">Selecciona...</option>`].concat(options.map((item)=>`<option value="${esc(item.code)}" ${item.code===effectiveSelected?"selected":""}>${esc(item.label)}</option>`));
    if(allowOther && !options.some((item)=>item.code==="other")) rows.push(`<option value="other" ${effectiveSelected==="other"?"selected":""}>Otro</option>`);
    const otherOpen=effectiveSelected==="other";
    const stateLabel=options.length?`${options.length} opciones homologadas`:`Sin catálogo cargado: usando fallback pendiente`;
    const open=state.openPicker===id;
    return `<label class="cc-field cc-field-select ${open?"picker-open":""}"><span>${esc(label)}</span><button type="button" class="cc-picker-button" data-picker-toggle="${esc(id)}" data-catalog="${esc(catalogCode)}" aria-expanded="${open?"true":"false"}"><strong>${esc(selectedLabel)}</strong><small>${esc(stateLabel)}</small></button><select class="cc-native-select" data-flow-field="${esc(id)}" data-catalog="${esc(catalogCode)}" data-options-count="${options.length}" tabindex="-1" aria-hidden="true" ${opts?.required?"required":""}>${rows.join("")}</select><div class="cc-catalog-state">${esc(stateLabel)}</div><div class="cc-catalog-table ${open?"show":""}" data-picker-panel="${esc(id)}"><div class="cc-catalog-toolbar"><input type="search" data-picker-filter="${esc(id)}" placeholder="Buscar opción homologada..." autocomplete="off" /><span>${esc(catalogs()[catalogCode]?.label || label)}</span></div><div class="cc-catalog-head"><span>Opción</span><span>Regla</span><span>Código</span></div><div class="cc-catalog-rows">${catalogTableRows(id,catalogCode,effectiveSelected)}</div></div><input class="cc-other-input ${otherOpen?"show":""}" data-other-for="${esc(id)}" placeholder="Especificar otro" value="${esc(state.flow[id+"Other"]||"")}" /></label>`;
  }
  function textField(id,label,value,opts){ return `<label class="cc-field"><span>${esc(label)}</span><input data-flow-field="${esc(id)}" value="${esc(value||"")}" placeholder="${esc(opts?.placeholder||"")}" ${opts?.required?"required":""} /></label>`; }
  function currentRecommendation(){ const vertical=flowValue("vertical","abarrotes"); const op=flowValue("operationMode","counter"); const size=flowValue("businessSize","small"); const meta=catalogOptions("vertical").find((item)=>item.code===vertical)?.metadata || {}; const validPlans=new Set(catalogOptions("license_plan").map((item)=>item.code)); let plan=meta.suggestedPlan || "TABLET_PC_MANAGED"; if(!validPlans.has(plan)) plan="TABLET_PC_MANAGED"; const modules=new Set(meta.modules || ["pos.open","pos.sale.complete","event.outbox.view"]); if(op==="inventory") modules.add("inventory.local.adjust"); if(size==="enterprise"||size==="multi_branch"){ plan="TABLET_PC_MANAGED"; modules.add("sync.managed"); } const device=op==="tables"?"pc_register":"tablet_pos"; return { plan, modules:Array.from(modules), device }; }
  function generatedPreview(){ const c=ccStore().counts || {}; return list([["Clientes preparados",c.clients||0],["Licencias preparadas",c.licenses||0],["Dispositivos preparados",c.devices||0],["Bajas preparadas",c.deactivations||0],["Borradores",c.preparedDrafts||0],["Otros por revisar",c.othersPending||0],["IDs generados",c.identities||0]]); }
  function flowSummary(){ const r=currentRecommendation(); return kvGrid([["Vertical",catalogLabel("vertical",flowValue("vertical","abarrotes"))],["Operación",catalogLabel("operation_mode",flowValue("operationMode","counter"))],["Plan sugerido",catalogLabel("license_plan",flowValue("plan",r.plan))],["Dispositivo sugerido",catalogLabel("device_type",flowValue("deviceType",r.device))]]); }
  function clientWizard(){ const r=currentRecommendation(); return `<div class="cc-flow-grid">${textField("displayName","Nombre comercial",flowValue("displayName"),{required:true,placeholder:"Ej. Abarrotes Don Pepe"})}${textField("contactName","Contacto",flowValue("contactName"),{placeholder:"Nombre de contacto"})}${textField("phone","Teléfono",flowValue("phone"),{})}${textField("email","Correo",flowValue("email"),{})}${selectField("vertical","Giro / vertical","vertical",flowValue("vertical","abarrotes"),{required:true})}${selectField("subvertical","Subvertical","subvertical",flowValue("subvertical"),{})}${selectField("businessSize","Tamaño","business_size",flowValue("businessSize","small"),{})}${selectField("operationMode","Tipo de operación","operation_mode",flowValue("operationMode","counter"),{})}${selectField("cityZone","Ciudad / zona","city_zone",flowValue("cityZone"),{})}${selectField("plan","Plan sugerido","license_plan",flowValue("plan",r.plan),{})}</div>${actions([actionButton("prepare-client","Preparar alta con IDs","primary"),actionButton("save-other-values","Guardar otros pendientes"),surfaceButton("entitlements","Ver planes"),surfaceButton("fleet","Agregar dispositivo")])}`; }
  function deviceWizard(){ const r=currentRecommendation(); return `<div class="cc-flow-grid">${selectField("clientCode","Cliente destino","client",flowValue("clientCode"),{})}${selectField("deviceType","Tipo de dispositivo","device_type",flowValue("deviceType",r.device),{required:true})}${selectField("operationMode","Uso principal","operation_mode",flowValue("operationMode","counter"),{})}${textField("deviceAlias","Alias visible",flowValue("deviceAlias"),{placeholder:"Ej. Caja principal"})}${selectField("cityZone","Sucursal / zona","city_zone",flowValue("cityZone"),{})}</div>${actions([actionButton("prepare-device","Generar dispositivo + código","primary"),actionButton("device-smoke","Registrar prueba cloud"),actionButton("receipt-smoke","Enviar receipt de prueba"),actionButton("save-other-values","Guardar otros pendientes")])}${details("Dispositivos preparados", { devices: localRows("devices") }, false)}`; }
function licenseWizard(){
  const r=currentRecommendation();
  const plan=flowValue("plan",r.plan);
  const m=planMeta(plan);
  const period=flowValue("billingPeriod","monthly");
  const listPrice=planListPrice(plan,period);
  const agreedRaw=flowValue("agreedPriceMxn","");
  const agreedDisplay=agreedRaw || listPrice;
  const policy=planCommercialPolicy(plan);
  return `<div class="cc-flow-grid">${selectField("clientCode","Cliente destino","client",flowValue("clientCode"),{})}${selectField("plan","Tipo de licencia","license_plan",plan,{required:true})}${billingPeriodField()}${priceTreatmentField()}${textField("agreedPriceMxn","Precio acordado MXN",agreedRaw,{placeholder:listPrice!=null?String(listPrice):"precio antes de IVA"})}${textField("priceEvidenceRef","Contrato / recibo / evidencia",flowValue("priceEvidenceRef"),{placeholder:"Obligatorio si el precio difiere del canon"})}${textField("validFrom","Inicio YYYY-MM-DD",flowValue("validFrom"),{placeholder:"Vacío = hoy"})}${textField("commercialNote","Nota comercial",flowValue("commercialNote"),{placeholder:"Opcional"})}</div>${kvGrid([["Precio lista",listPrice!=null?`${moneyMxn(listPrice)} + IVA`:"sin precio canonico"],["Precio a preparar",agreedDisplay!=null&&agreedDisplay!==""?`${moneyMxn(agreedDisplay)} + IVA`:"precio de lista"],["Versión",m.commercial?.priceVersion||"-"],["Periodicidad",BILLING_PERIOD_LABELS[period]||period],["Impuesto",policy.taxTreatment==="PLUS_APPLICABLE_IVA"?"+ IVA aplicable":policy.taxTreatment||"según contrato"],["Máximo dispositivos",m.maxDevices||"según contrato"],["Máximo sucursales",m.maxBranches||"según contrato"],["Módulos",(m.modules||r.modules).join(", ")]])}${actions([actionButton("prepare-license","Preparar licencia + contrato","primary"),actionButton("compare-license-contract","Comparar con contrato"),surfaceButton("customers","Ver cliente")])}${details("Licencias preparadas", { licenses: localRows("licenses"), contracts: localRows("contracts") }, false)}`;
}
  function deactivationWizard(){ return `<div class="cc-flow-grid"><label class="cc-field"><span>Qué se dará de baja</span><select data-flow-field="targetKind"><option value="client" ${flowValue("targetKind","client")==="client"?"selected":""}>Cliente</option><option value="license" ${flowValue("targetKind")==="license"?"selected":""}>Licencia</option><option value="device" ${flowValue("targetKind")==="device"?"selected":""}>Dispositivo</option></select></label>${selectField("clientCode","Cliente / referencia local","client",flowValue("clientCode"),{})}${textField("targetCode","Folio / referencia manual",flowValue("targetCode"),{placeholder:"Opcional si eliges cliente"})}${selectField("reason","Motivo","deactivation_reason",flowValue("reason","cancellation"),{required:true})}</div><div class="cc-impact"><strong>Impacto antes de confirmar</strong><span>Historial se conserva · cloud no se toca todavía · se genera folio de baja local</span></div>${actions([actionButton("prepare-deactivation","Preparar baja segura","primary"),actionButton("save-other-values","Guardar otros pendientes"),surfaceButton("system","Ver técnico")])}${details("Bajas preparadas", { deactivations: localRows("deactivations") }, false)}`; }


  function jsonValue(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback || null;
    if (typeof value === "object") return value;
    try { return JSON.parse(value); } catch (_) { return fallback || value; }
  }

  function localRows(kind){
    const local = ccStore().local || {};
    return Array.isArray(local[kind]) ? local[kind] : [];
  }
  function shortLocal(row){ return row?.humanCode || row?.entityCode || row?.id || "-"; }
  function clientLabel(row){ return row ? `${row.displayName || row.clientName || "Cliente"} · ${row.humanCode || row.clientCode || "-"}` : "-"; }
  function statusText(value){
    const raw = String(value || "prepared");
    const map = {
      pending_cloud_activation: "Pendiente cloud",
      pending_registration: "Pendiente registro",
      pending_catalog_review: "Pendiente catálogo",
      prepared: "Preparado",
      active: "Activo",
      suspended: "Suspendido"
    };
    return map[raw] || raw.replace(/_/g, " ");
  }
  function prettyDate(value){
    if (!value) return "-";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value).slice(0, 16);
    return d.toLocaleString([], { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" });
  }
  function localCounts(){ return ccStore().counts || {}; }
  function localDeskCells(kind, row){
    if (kind === "clients") return [
      row.humanCode || "-",
      row.displayName || "Cliente preparado",
      catalogLabel("vertical", row.verticalCode) || row.verticalCode || "Sin vertical",
      statusText(row.status),
      prettyDate(row.createdAt)
    ];
    if (kind === "licenses") return [
      row.humanCode || "-",
      row.clientName || row.clientCode || "Sin cliente",
      row.planLabel || catalogLabel("license_plan", row.planCode) || row.planCode || "Plan",
      statusText(row.status),
      prettyDate(row.createdAt)
    ];
    if (kind === "contracts") return [
      row.humanCode || "-",
      row.clientName || row.clientCode || "Sin cliente",
      `${row.planCode || "Plan"} · ${BILLING_PERIOD_LABELS[row.billingPeriod] || row.billingPeriod || "periodo"}`,
      row.agreedPriceMxn != null ? `${moneyMxn(row.agreedPriceMxn)} + IVA` : "-",
      row.renewalOn || statusText(row.status)
    ];
    if (kind === "devices") return [
      row.humanCode || "-",
      row.clientName || row.clientCode || "Sin cliente",
      catalogLabel("device_type", row.deviceType) || row.deviceType || "Dispositivo",
      row.registerCode || "Sin código",
      statusText(row.status)
    ];
    if (kind === "deactivations") return [
      row.humanCode || "-",
      `${row.targetKind || "target"} ${row.targetCode || ""}`.trim(),
      catalogLabel("deactivation_reason", row.reasonCode) || row.reasonCode || "Motivo",
      statusText(row.status),
      prettyDate(row.createdAt)
    ];
    if (kind === "drafts") return [
      row.humanCode || "-",
      row.kind || "draft",
      statusText(row.status),
      row.clientId ? String(row.clientId).slice(0, 8) : "-",
      prettyDate(row.createdAt)
    ];
    if (kind === "othersPending") return [
      row.catalogLabel || row.catalogKey || "Catálogo",
      row.manualText || "-",
      statusText(row.status),
      prettyDate(row.createdAt),
      "Revisión"
    ];
    if (kind === "events") return [
      row.entityCode || row.entityKind || "Evento",
      row.eventType || "audit",
      row.summary || "-",
      prettyDate(row.createdAt),
      row.entityKind || "-"
    ];
    return [shortLocal(row), row.status || row.summary || "local", prettyDate(row.createdAt), "-", "-"];
  }
  function localDeskHeaders(kind){
    return {
      clients: ["Folio", "Cliente", "Vertical", "Estado", "Fecha"],
      licenses: ["Folio", "Cliente", "Plan", "Estado", "Fecha"],
      contracts: ["Contrato", "Cliente", "Plan / periodo", "Precio", "Renovación"],
      devices: ["Folio", "Cliente", "Tipo", "Registro", "Estado"],
      deactivations: ["Folio", "Objetivo", "Motivo", "Estado", "Fecha"],
      drafts: ["Folio", "Tipo", "Estado", "Cliente", "Fecha"],
      othersPending: ["Catálogo", "Texto manual", "Estado", "Fecha", "Acción"],
      events: ["Entidad", "Evento", "Resumen", "Fecha", "Tipo"]
    }[kind] || ["Código", "Estado", "Fecha", "Dato", "Dato"];
  }
  function localDeskTitle(kind){
    return {
      clients: "Clientes locales",
      licenses: "Licencias preparadas",
      contracts: "Contratos comerciales",
      devices: "Dispositivos preparados",
      deactivations: "Bajas preparadas",
      drafts: "Borradores de operación",
      othersPending: "Otros pendientes de catálogo",
      events: "Auditoría local"
    }[kind] || "Registros locales";
  }
  function localPlainSummary(kind, row){
    const headers = localDeskHeaders(kind);
    const cells = localDeskCells(kind, row);
    return headers.map((h, i) => `${h}: ${compact(cells[i])}`).join("\n");
  }
  function localDesk(kind, empty){
    const rows = localRows(kind);
    const headers = localDeskHeaders(kind);
    if (!rows.length) return `<div class="cc-desk-empty"><strong>${esc(empty || "Sin registros todavía")}</strong><span>Cuando prepares datos desde los flujos, aparecerán aquí con folio, estado y siguiente acción.</span></div>`;
    return `<div class="cc-desk" data-kind="${esc(kind)}"><div class="cc-desk-grid cc-desk-headline">${headers.map((h)=>`<span>${esc(h)}</span>`).join("")}</div>${rows.slice(0, 30).map((row, index)=>`<button type="button" class="cc-desk-grid cc-desk-rowline" data-desk-kind="${esc(kind)}" data-desk-index="${index}">${localDeskCells(kind,row).map((cell)=>`<span>${esc(compact(cell))}</span>`).join("")}</button>`).join("")}</div>`;
  }
  function localList(kind, empty){ return localDesk(kind, empty); }
  function localDashboard(){
    const c = localCounts();
    return `<div class="cc-desk-dashboard">${[
      ["Clientes", c.clients || 0, "Preparados"],
      ["Licencias", c.licenses || 0, "Listas"],
      ["Contratos", c.contracts || 0, "Comerciales"],
      ["Dispositivos", c.devices || 0, "Pendientes"],
      ["Bajas", c.deactivations || 0, "Seguras"],
      ["Otros", c.othersPending || 0, "Catálogo"],
      ["Auditoría", c.auditEvents || 0, "Eventos"]
    ].map(([a,b,cx])=>`<div class="cc-desk-metric"><small>${esc(a)}</small><strong>${esc(b)}</strong><span>${esc(cx)}</span></div>`).join("")}</div>`;
  }
function planCatalogDesk(){
  const plans = ccStore().licensePlans || [];
  if (!plans.length) return `<div class="cc-desk-empty"><strong>Sin planes cargados</strong><span>El catálogo local o fallback todavía no devolvió planes.</span></div>`;
  return `<div class="cc-plan-grid">${plans.map((p)=>{ const prices=p.commercial?.listPriceMxn || p.rules?.commercial?.listPriceMxn || {}; const priceLine=Object.entries(BILLING_PERIOD_LABELS).map(([period,label])=>`${label}: ${prices[period]!=null?moneyMxn(prices[period]):"-"}`).join(" · "); return `<article class="cc-plan-card"><div><strong>${esc(p.label || p.code)}</strong><small>${esc(p.code || "plan")}</small></div><p>${esc(priceLine)} · + IVA</p><p>${esc((p.modules || []).join(" · ") || "Módulos pendientes")}</p><footer>${chip("READY", `${p.maxDevices || "N"} disp.`)}${chip("READY", `${p.maxBranches || "N"} suc.`)}</footer></article>`; }).join("")}</div>`;
}
  function localSummaryText(){
    const c = localCounts();
    const last = localRows("events").slice(0, 8).map((e)=>`- ${e.createdAt || ""} ${e.entityCode || e.entityKind || "evento"}: ${e.summary || e.eventType || ""}`).join("\n") || "- Sin eventos locales.";
    return [
      "Prisma Cloud Center - escritorio local",
      `Clientes: ${c.clients || 0}`,
      `Licencias: ${c.licenses || 0}`,
      `Contratos comerciales: ${c.contracts || 0}`,
      `Dispositivos: ${c.devices || 0}`,
      `Bajas: ${c.deactivations || 0}`,
      `Borradores preparados: ${c.preparedDrafts || 0}`,
      `Otros pendientes: ${c.othersPending || 0}`,
      `Audit events: ${c.auditEvents || 0}`,
      "",
      "Últimos eventos:",
      last
    ].join("\n");
  }
  function deskIntro(kind){
    const count = localRows(kind).length;
    return `${count} registro(s) locales. Click en una fila para ver/copy-pastear detalle sin abrir raw JSON.`;
  }
  function dbStatusPanel(){
    const s = ccStore();
    const c = localCounts();
    return kvGrid([
      ["Modo", s.workflowMode || s.mode || "local"],
      ["DB", s.dbPath ? "prisma-command-center.db" : "sin ruta"],
      ["Schema", s.schemaVersion || "-"],
      ["Catálogos", Object.keys(catalogs()).length],
      ["Opciones", Object.values(catalogs()).reduce((n, cat)=>n + ((cat.options || []).length), 0)],
      ["IDs", c.identities || 0]
    ]);
  }

  function renderCommand() {
    const d=derived(); const p=collectProblems(); const c=localCounts();
    return [
      panel("Acciones principales","Elige la tarea. La cabina genera IDs y usa catálogos; tú no escribes folios.",actions([surfaceButton("provisioning","+ Nuevo cliente"),surfaceButton("customer-setup","Prisma Customer Setup"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo"),surfaceButton("security","Dar de baja"),surfaceButton("operations","Ver escritorio local"),surfaceButton("support","Resolver soporte")]),{span:7,tag:"TAREAS"}),
      panel("Escritorio local","Lo que ya existe en la DB del cockpit: clientes, licencias, dispositivos, bajas, otros y auditoría.",localDashboard(),{span:5,tag:`${c.preparedDrafts||0} drafts`}),
      panel("Resumen actual","Lo que está pasando sin tocar acciones admin.",kvGrid([["Cloud",state.data?.ok?"En línea":"Revisar"],["Cloud License Gateway",licflow3LiveStatus()],["Cliente",d.tenant?.displayName||d.tenant?.slug||FIRST_CUSTOMER_NAME],["Admin Token Status",adminTokenPresent()?"presence-only":"missing"],["Problemas",p.length?`${p.length} por revisar`:"Sin bloqueadores"]]),{span:5,tag:mainStatus()}),
      panel("Operar escritorio","Copiar digest, abrir clientes o ir a System sin mirar raw técnico.",actions([actionButton("refresh","Actualizar todo","primary"),actionButton("copy-local-desk","Copiar escritorio local"),surfaceButton("customers","Clientes"),surfaceButton("operations","Reportes"),surfaceButton("system","System")]),{span:7,tag:"DESK"}),
      panel("Problemas detectados","Si algo bloquea, aparece aquí en humano.",problemsHtml(),{span:12,tag:p.length?"REVIEW":"OK"}),
      resultPanel()
    ].join("");
  }
  function renderCustomers() { const d=derived(); const c=localCounts(); return [
    panel("Clientes activos","Clientes preparados localmente + cliente observado en cloud.",kvGrid([["Clientes preparados",c.clients||0],["Activos/preparados",c.activeClients||0],["Cliente cloud",d.tenant?.displayName||d.tenant?.slug||FIRST_CUSTOMER_NAME],["Otros por revisar",c.othersPending||0]]),{span:5,tag:"CLIENTES"}),
    panel("Acciones","Operación centrada en cliente, no en módulos técnicos.",actions([surfaceButton("provisioning","+ Nuevo cliente"),actionButton("copy-clients-local","Copiar clientes locales"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo"),surfaceButton("security","Dar baja")]),{span:7,tag:"ACCIONES"}),
    panel("Mesa de clientes","Abrir filas, revisar vertical/estado y decidir siguiente acción.",localDesk("clients","Todavía no hay clientes preparados."),{span:12,tag:`${c.clients||0} local`}),
    panel("Auditoría del cliente","Últimos eventos del motor de catálogos/IDs.",localDesk("events","Todavía no hay eventos locales."),{span:12,tag:"AUDIT"}),
    resultPanel()
  ].join(""); }
  function bridgePayload(action, dryRun) {
    const root = document.querySelector(`[data-bridge-form="${action}"]`);
    const value = (name) => root?.querySelector(`[data-bridge-field="${name}"]`)?.value || "";
    return {
      confirmAdminLicenseAction: !!root?.querySelector(`[data-bridge-confirm]`)?.checked,
      confirmRevoke: value("confirmRevoke"),
      licenseId: value("licenseId") || value("licenseKey"),
      licenseKey: value("licenseKey") || value("licenseId"),
      deviceId: value("deviceId"),
      tenantId: value("tenantId") || FIRST_TENANT_SLUG,
      operatorNote: value("operatorNote"),
      reason: value("reason"),
      dryRun
    };
  }

  function bridgeForm(action, label, danger) {
    const revoke = action === "revoke";
    return `<div class="cc-bridge-form" data-bridge-form="${esc(action)}">
      <h4>${esc(label)}</h4>
      <div class="cc-flow-grid">
        <label class="cc-field"><span>License ID / key</span><input data-bridge-field="licenseId" autocomplete="off" placeholder="license-id" /></label>
        <label class="cc-field"><span>Device ID</span><input data-bridge-field="deviceId" autocomplete="off" placeholder="device-id" /></label>
        <label class="cc-field"><span>Tenant</span><input data-bridge-field="tenantId" autocomplete="off" value="${esc(FIRST_TENANT_SLUG)}" /></label>
        <label class="cc-field"><span>${revoke ? "Reason" : "Operator note"}</span><input data-bridge-field="${revoke ? "reason" : "operatorNote"}" autocomplete="off" placeholder="${revoke ? "Motivo requerido" : "Nota opcional"}" /></label>
        ${revoke ? `<label class="cc-field" for="bridge-phrase-revoke"><span>Confirm revoke</span><input id="bridge-phrase-revoke" data-bridge-field="confirmRevoke" autocomplete="off" placeholder="REVOKE_LICENSE" /></label>` : ""}
      </div>
      <label class="cc-impact" for="bridge-confirm-${esc(action)}"><input id="bridge-confirm-${esc(action)}" type="checkbox" data-bridge-confirm /> Confirmo operación de licencia admin para ${esc(label)}<span>El token vive sólo en backend; el browser no lo recibe.</span></label>
      ${actions([
        actionButton(`licflow4-dryrun-${action}`, `Run Simulation ${label}`, "secondary"),
        actionButton(`licflow4-run-${action}`, danger ? `Execute Confirmed Operation ${label}` : `Execute Confirmed Operation ${label}`, danger ? "danger" : "primary")
      ])}
    </div>`;
  }

  function bridgePanel() {
    const bridge = licflow4Bridge();
    const checklist = Array.isArray(bridge.operatorChecklist) ? bridge.operatorChecklist.map((item) => [item.label || item.id, item.done ? "ready" : "operator step"]) : [
      ["Admin Token Status: presence-only", "ready"],
      ["Run Simulation (Dry Run) first", "operator step"],
      ["Review sanitized payload", "operator step"],
      ["Confirm before Confirmed License Operation", "operator step"],
      ["For revoke, type REVOKE_LICENSE", "operator step"]
    ];
    return [
      kvGrid([
        ["bridgeAvailable", bridge.bridgeAvailable ? "true" : "false"],
        ["Admin Token Status", bridge.adminTokenPresent ? "presence-only" : "missing"],
        ["Token Mode", bridge.tokenMode || "presence-only"],
        ["Mutation Mode", bridge.mutationMode || "admin-token-missing"],
        ["Simulation", bridge.simulationLabel || "Simulation (Dry Run)"],
        ["Confirmed Operation", bridge.confirmedOperationLabel || "Confirmed License Operation"],
        ["Worker", bridge.worker || "prisma-cloud-semilla"],
        ["Cloud License Database", bridge.d1 || "prisma_cloud_semilla"],
        ["Activate", bridge.routes?.activate || "/api/licenses/activate"],
        ["Refresh", bridge.routes?.refresh || "/api/licenses/refresh"],
        ["Revoke", bridge.routes?.revoke || "/api/licenses/revoke"],
        ["Last result", bridge.lastResultCode || "-"],
        ["safeToMutate", bridge.safeToMutate ? "true" : "false"]
      ]),
      `<div class="cc-empty">License Admin Bridge never asks for credencial privilegiada server-side in the browser. Simulation validates fields first; Confirmed License Operation requires server-side token and explicit confirmation.</div>`,
      `<div class="cc-empty"><strong>Operator checklist</strong></div>`,
      list(checklist),
      `<div class="cc-empty"><strong>License Operation Audit</strong></div>`,
      list((bridge.audit?.latest || []).map((event) => [`${event.mode || (event.dryRun ? "simulation" : "confirmed-operation")} ${event.action}`, `${event.resultCode || "REVIEW"} · ${event.requestId || "-"}`]), "No License Operation Audit events yet."),
      bridgeForm("activate", "Activate", false),
      bridgeForm("refresh", "Refresh", false),
      bridgeForm("revoke", "Revoke", true)
    ].join("");
  }

  function renderEntitlements() { const c=localCounts(); return [
    panel("Asignar licencia","Elige cliente y plan desde catálogo. Límites y módulos vienen gobernados.",licenseWizard(),{span:8,tag:"LICENCIA"}),
    panel("Catálogo de planes","Tipos disponibles, límites y módulos incluidos.",planCatalogDesk(),{span:4,tag:`${(ccStore().licensePlans||[]).length} planes`}),
    panel("License Admin Bridge","Puente local seguro para activate, refresh y revoke sin exponer credencial privilegiada server-side al frontend.",bridgePanel(),{span:12,tag:licflow4Bridge().bridgeAvailable ? "BRIDGE" : "REVIEW"}),
    panel("Mesa de licencias","Asignaciones preparadas con folio LIC vinculadas a contrato comercial.",localDesk("licenses","Todavía no hay licencias preparadas."),{span:12,tag:`${c.licenses||0} local`}),
    panel("Contratos comerciales","Cada CTR conserva plan, periodicidad, precio de lista, precio acordado, versión, IVA, vigencia, renovación y evidencia cuando existe excepción.",localDesk("contracts","Todavía no hay contratos comerciales preparados."),{span:12,tag:`${c.contracts||0} CTR`}),
    panel("Reglas","Las licencias locales quedan preparadas; activate/refresh/revoke sólo pasan por License Admin Bridge con confirmación.",list([["Estado","pending_cloud_activation / prepared"],["Folio","LIC-YYYY-000001"],["Contrato","CTR-YYYY-000001"],["Cloud","Confirmed License Operation protected by bridge"],["Revoke","requiere REVOKE_LICENSE"]]),{span:12,tag:"REGLAS"}),
    resultPanel()
  ].join(""); }

    // PRISMA TABLET LAB CAPSULE START: dependency-free, portable-first surface capsule.
  function renderTabletLab() {
    const escapeLab = (value) => String(value ?? "").replace(/[&<>"']/g, (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch]));
    const cards = [
      {k:"01", tag:"LICENCIA", title:"Asignar licencia", body:"Elige cliente y plan desde catálogo. Límites y módulos vienen gobernados.", items:["Cliente", "Plan", "Módulos", "Confirmación"]},
      {k:"02", tag:"PLANES", title:"Catálogo de planes", body:"Tipos disponibles, límites y módulos incluidos para validar el flujo visual antes de tocar Tablet real.", items:["Starter", "Pro", "Enterprise", "Governed"]},
      {k:"03", tag:"BRIDGE", title:"License Admin Bridge", body:"Puente conceptual para activate, refresh y revoke sin exponer credenciales ni acoplar UI a dependencias externas.", items:["Activate", "Refresh", "Revoke", "Audit"]},
      {k:"04", tag:"MESA", title:"Mesa de licencias", body:"Asignaciones preparadas con folio LIC y contrato CTR en una maqueta portable de laboratorio.", items:["LIC-YYYY-000001", "CTR-YYYY-000001", "Prepared", "Cloud-ready"]},
      {k:"05", tag:"REGLAS", title:"Reglas", body:"La cápsula viaja como HTML, CSS namespaced y JS vanilla. Sin npm nuevo, sin CDN y sin lockfiles.", items:["Dependency-free", "Namespaced", "Rollbackable", "Tablet-safe"]},
      {k:"06", tag:"SALIDA", title:"Resultado", body:"Superficie aislada para ensayar Tablet Light Cloudglass antes de migrar una piel a la Tablet real.", items:["Lab first", "Mesh first", "Port once", "No fake green"]}
    ];
    const cardHtml = cards.map((card) => `
      <article class="tablet-lab-card" data-tablet-lab-card="${escapeLab(card.k)}">
        <div class="tablet-lab-card-topline"><span>${escapeLab(card.k)}</span><strong>${escapeLab(card.tag)}</strong></div>
        <h3>${escapeLab(card.title)}</h3>
        <p>${escapeLab(card.body)}</p>
        <div class="tablet-lab-chip-row">${card.items.map((item) => `<span>${escapeLab(item)}</span>`).join("")}</div>
      </article>`).join("");
    return `
      <section class="tablet-lab-capsule" data-tablet-lab-capsule="true" aria-label="PRISMA TABLET LAB Capsule">
        <div class="tablet-lab-hero">
          <span class="tablet-lab-kicker">TABLET LAB</span>
          <h2>Cápsula portable basada en Entitlements</h2>
          <p>Laboratorio visual aislado para preparar una piel clara Tablet Light Cloudglass sin tocar Tablet real, dependencias, lockfiles, puertos ni Prisma.</p>
          <div class="tablet-lab-hero-rail"><span>HTML portable</span><span>CSS namespaced</span><span>JS vanilla</span><span>Rollback listo</span></div>
        </div>
        <div class="tablet-lab-grid">${cardHtml}</div>
        <div class="tablet-lab-portability-sentinel" data-portability="cloud-to-tablet-ready">
          <strong>Portability Gate</strong>
          <span>Esta surface no depende de Entitlements renderer, npm, CDN ni assets obligatorios raros.</span>
        </div>
      </section>`;
  }
  // PRISMA TABLET LAB CAPSULE END

  function renderFleet() { const d=derived(); const c=localCounts(); return [
    panel("Agregar dispositivo","Selecciona cliente, tipo y uso. El motor genera ID, folio y código de registro.",deviceWizard(),{span:8,tag:"DEVICE"}),
    panel("Dispositivos cloud","Lo que el cloud/snapshot ya reporta.",list(d.devices,"El snapshot no devolvió dispositivos."),{span:4,tag:`${safeCount(d.devices)} cloud`}),
    panel("Mesa de dispositivos","Dispositivos preparados con folio DEV y código REG.",localDesk("devices","Todavía no hay dispositivos preparados."),{span:12,tag:`${c.devices||0} local`}),
    panel("Reglas","Sin IDs manuales y sin texto libre salvo Otro controlado.",list([["ID interno","se genera solo"],["Folio","DEV-YYYY-000001"],["Registro","REG-XXXXXX-XXXXXX"],["Cloud","no registrado hasta endpoint real"]]),{span:12,tag:"HOMOLOGADO"}),
    resultPanel()
  ].join(""); }
  function provisioningChecklist() {
    const d = derived();
    return [
      ["Cliente cargado", !!d.tenant],
      ["Licencia visible", !!(d.license || state.license?.runtime?.license)],
      ["Contrato visible", !!d.publicContract || endpointState("clientContract").ok],
      ["Capacidades visibles", !!d.capabilities || endpointState("capabilities").ok],
      ["Dispositivo registrado", safeCount(d.devices) > 0],
      ["Receipt disponible", safeCount(d.receipts) > 0],
      ["Nota inicial", safeCount(d.notes) > 0]
    ];
  }

  function renderProvisioning() { return [panel("Alta de nuevo cliente","Texto mínimo + catálogos. IDs, folios, contrato y alta se preparan solos.",clientWizard(),{span:8,tag:"WIZARD"}), panel("Resumen automático","La cabina recomienda plan, módulos y dispositivo según vertical/operación.",flowSummary(),{span:4,tag:"REGLAS"}), panel("Qué se va a generar","Nada se activa en cloud todavía si el endpoint no existe. Queda preparado y auditado.",list([["Cliente","CLI-YYYY-000001"],["Contrato","CTR-YYYY-000001"],["Alta","ALT-YYYY-000001"],["Estado","prepared / pending_cloud_activation"]]),{span:12,tag:"AUTO-ID"}), resultPanel()].join(""); }

  function customerSetupPass() {
    return {
      setupCode: "PRISMA-SETUP-STARTER",
      setupLink: "https://app.hitechrts.com/setup/PRISMA-SETUP-STARTER",
      setupQr: "prisma://setup/PRISMA-SETUP-STARTER",
      packageLabel: "Tablet POS + PC Admin + Mobile Companion",
      status: "source ready; deploy not executed",
      slots: [
        ["Tablet POS Slot", "tablet", "0 / 1 claimed"],
        ["PC Admin Slot", "pc", "0 / 1 claimed"],
        ["Mobile Companion Slot", "mobile", "0 / 1 claimed"]
      ]
    };
  }

  function renderCustomerSetup() {
    const setup = customerSetupPass();
    return [
      panel("Prisma Customer Setup", "Cliente compra Tablet + PC + Mobile; el operador genera Setup Link, Setup Code y Setup QR.", kvGrid([
        ["Package", setup.packageLabel],
        ["Setup Code", setup.setupCode],
        ["Setup Link", setup.setupLink],
        ["Setup QR", setup.setupQr],
        ["Estado", setup.status],
        ["secretsExposed", "false"]
      ]), { span: 6, tag: "SETUP" }),
      panel("Device Slots", "Cada app reclama sólo su slot correcto, sin credencial privilegiada en navegador y sin duplicar subsistemas.", list(setup.slots.map(([label, surface, claim]) => [label, `${surface} · ${claim}`])), { span: 6, tag: "SLOTS" }),
      panel("Customer-safe endpoints", "Cloud License Gateway source now contains customer setup routes. Live customer use still needs deploy/D1 authorization.", list([
        ["Admin create", "POST /api/admin/customer-setups/create"],
        ["Resolve setup", "GET /api/customer/setup/:setupCode"],
        ["Device Claim", "POST /api/customer/devices/claim"],
        ["License status", "GET /api/customer/license/status?setupCode=...&deviceId=..."],
        ["License refresh", "POST /api/customer/license/refresh"],
        ["Portal", "GET /api/customer/portal?setupCode=..."],
        ["Magic link", "GET /api/customer/magic-link?setupCode=..."],
        ["Replacement request", "POST /api/customer/devices/replacement/request"],
        ["Replacement approve", "POST /api/admin/customer-devices/replacement/approve"]
      ]), { span: 12, tag: "SOURCE READY" }),
      panel("Operator boundary", "Customer Setup is onboarding. License Admin Bridge remains separate for activate, refresh and revoke.", list([
        ["Customer Setup", "Setup Link, Setup Code, Setup QR, Device Slots"],
        ["License Admin Bridge", "Simulation (Dry Run) and Confirmed License Operation"],
        ["Admin Token Status", "presence-only, server-side only"],
        ["Cloud state", "source ready; deploy not executed"]
      ]), { span: 12, tag: "NO TOKEN" }),
      resultPanel()
    ].join("");
  }

  function renderContracts() {
    const d = derived();
    const contract = d.publicContract || {};
    const licflow3 = state.data?.licflow3Contract || {};
    const routeRows = Array.isArray(licflow3.endpoints) ? licflow3.endpoints.map((item) => [
      item.label || item.key,
      `${item.method} ${item.configuredPath || item.path} -> ${(item.routeTags || []).join(", ") || (item.adminRequired ? "admin-token-required" : "read-only")}`
    ]) : [];
    return [
      panel("Contrato actual", "Estado contractual resumido para operar.", kvGrid([
        ["Estado", contract.status || endpointState("clientContract").code],
        ["Plan", contract.plan || derived().license?.plan || "-"],
        ["Cliente", contract.tenant || contract.tenantSlug || d.tenant?.slug || FIRST_CUSTOMER_NAME],
        ["Capacidades", endpointState("capabilities").code]
      ]), { span: 5, tag: endpointState("clientContract").ok ? "CONTRATO" : "REVISAR" }),
      panel("Cloud License Routes", "Cloudflare routes are deployed and protected; unauthenticated POST smoke expects 401 protected-route response.", kvGrid([
        ["Estado", licflow3.statusDisplay || licflow3.hostedCloudEvidenceStatus || licflow3.status || "Cloud License Gateway: Live"],
        ["Worker", licflow3.worker || "prisma-cloud-semilla"],
        ["Cloud License Database", licflow3.d1 || "prisma_cloud_semilla"],
        ["Base", licflow3.configuredBaseUrl || state.data?.cloud?.baseUrl || "-"],
        ["Activate", "POST /api/licenses/activate -> admin-token-required, dry-run-safe"],
        ["Refresh", "POST /api/licenses/refresh -> admin-token-required, dry-run-safe"],
        ["Revoke", "POST /api/licenses/revoke -> admin-token-required, dry-run-safe, REVOKE_LICENSE"],
        ["Admin Token Status", adminTokenPresent() ? "presence-only" : "missing"]
      ]), { span: 7, tag: licflow3LiveStatus() }),
      panel("License Route Map", "Operator-safe classification mirrors the Worker source; mutating routes are not auto-called.", list(routeRows, "Route map not loaded yet."), { span: 12, tag: "ROUTE MAP" }),
      panel("Acciones de configuración", "Comparar, copiar y saltar a licencias sin ver endpoints.", actions([
        actionButton("refresh", "Actualizar contrato", "primary"),
        actionButton("compare-contract", "Comparar contrato vs capacidades"),
        actionButton("copy-contract", "Copiar configuración"),
        surfaceButton("entitlements", "Ver licencias"),
        surfaceButton("system", "Detalle técnico")
      ]), { span: 7, tag: "CONFIG" }),
      panel("Capacidades públicas", "Resumen legible de lo que el cliente puede usar.", list(Object.entries(d.capabilities || {}).slice(0, 14), "No hay capacidades legibles todavía."), { span: 12, tag: endpointState("capabilities").code }),
      resultPanel()
    ].join("");
  }

  function renderOperations() { const c=localCounts(); const d=derived(); return [
    panel("Escritorio operativo","Clientes, licencias, dispositivos, bajas e identidades del cockpit local.",localDashboard(),{span:12,tag:"DESK"}),
    panel("Borradores locales","Alta/licencia/dispositivo/baja preparados para activación futura.",localDesk("drafts","Todavía no hay borradores preparados."),{span:6,tag:`${c.preparedDrafts||0} drafts`}),
    panel("Otros pendientes","Valores manuales capturados como pending_catalog_review.",localDesk("othersPending","No hay valores Otro pendientes."),{span:6,tag:`${c.othersPending||0} review`}),
    panel("Cloud observado","Lo que existe hoy en app.hitechrts.com sin tocar semilla.",list([["Cliente",d.tenant?.displayName||d.tenant?.slug||FIRST_CUSTOMER_NAME],["Dispositivos cloud",safeCount(d.devices)],["Receipts",safeCount(d.receipts)],["Notas",safeCount(d.notes)]]),{span:6,tag:"CLOUD"}),
    panel("Acciones","Reportes y auditoría listos para copiar.",actions([actionButton("refresh","Actualizar","primary"),actionButton("copy-local-desk","Copiar escritorio"),actionButton("copy-ops","Copiar digest operativo"),surfaceButton("customers","Ver clientes"),surfaceButton("system","System")]),{span:6,tag:"REPORTES"}),
    panel("Auditoría local","Eventos recientes del motor local.",localDesk("events","Sin eventos locales."),{span:12,tag:`${c.auditEvents||0} audit`}),
    resultPanel()
  ].join(""); }
  function supportCatalog() {
    return state.supportCatalog || { codes: [], actions: [] };
  }

  function selectedSupportCode() {
    return flowValue("supportCode", state.supportDiagnosis?.primaryIssueCode || state.supportSearch?.events?.[0]?.issue || "CROSS_SOURCE_IDENTITY_SPLIT");
  }

  function supportCodeSelector() {
    const codes = supportCatalog().codes || [];
    const selected = selectedSupportCode();
    const options = codes.map((item) => `<option value="${esc(item.code)}" ${item.code === selected ? "selected" : ""}>${esc(item.category)} · ${esc(item.code)}</option>`).join("");
    return `<label class="cc-field"><span>Código</span><select data-flow-field="supportCode">${options}</select></label>`;
  }


  function selectedSupportAuthority() {
    return flowValue("supportAuthority", state.supportSimulation?.reconciliation?.recommendedAuthority || state.supportSearch?.reconciliation?.recommendedAuthority || "setup_claim_or_refresh");
  }

  function supportAuthoritySelector() {
    const rec = state.supportSimulation?.reconciliation || state.supportSearch?.reconciliation || {};
    const choices = rec.authorityChoices || [
      { id: "setup_claim_or_refresh", label: "Setup Code / License Refresh" },
      { id: "use_pos_local_seed", label: "DB POS local seed" },
      { id: "use_signed_activation_package", label: "Paquete firmado externo" }
    ];
    const selected = selectedSupportAuthority();
    const options = choices.map((item) => `<option value="${esc(item.id)}" ${item.id === selected ? "selected" : ""}>${esc(item.label || item.id)}</option>`).join("");
    return `<label class="cc-field"><span>Autoridad</span><select data-flow-field="supportAuthority">${options}</select></label>`;
  }




  function supportSetupCodeField() {
    const setupCode = flowValue("supportSetupCode", "");
    return `<label class="cc-field"><span>Setup Code</span><input data-flow-field="supportSetupCode" value="${esc(setupCode)}" placeholder="pegar setup code para preflight" autocomplete="off" /></label>`;
  }

  function supportRequestPayload(extra = {}) {
    const selectedAuthority = selectedSupportAuthority();
    return {
      ...SUPPORT_IDENTITY_CONTEXT,
      query: flowValue("supportQuery", FIRST_CUSTOMER_NAME),
      code: selectedSupportCode(),
      surface: "tablet",
      authority: selectedAuthority,
      selectedAuthority,
      authorityStrategy: selectedAuthority,
      identityReconciliationRequested: true,
      setupCode: flowValue("supportSetupCode", "").trim(),
      ...extra
    };
  }

  function supportFallbackReconciliation() {
    return {
      ok: true,
      splitDetected: true,
      primaryIssueCode: "CROSS_SOURCE_IDENTITY_SPLIT",
      worlds: [
        { id: "pc_admin_customer", label: "Prisma Original Customer", source: "pc-admin-diagnostic", authorityAction: "setup_claim_or_refresh", customerId: "cust_prisma_original_customer", businessId: "biz_78b3c840796a4a4dad", storeId: "store_00728649f3804a9e82", terminalId: "term_49103c7382d84663a3", tabletDeviceId: "tablet_prisma_original_customer_001" },
        { id: "runtime_local", label: "Runtime local", source: "runtime.json/device-identity", authorityAction: "use_runtime_local_only_after_license_match", businessId: "biz_prisma_rey_lineage_seed", storeId: "store_prisma_rey_centro", terminalId: "term_tablet_pos_001", deviceId: "tablet-pos-source-ready" },
        { id: "installed_license", label: "Licencia local instalada", source: "license.json", authorityAction: "license_claim_or_refresh_required", customerId: "cust_demo", businessId: "biz_demo", licenseId: "lic_demo_tablet_pro" }
      ],
      businessIds: ["biz_78b3c840796a4a4dad", "biz_demo", "biz_prisma_rey_lineage_seed"],
      customerIds: ["cust_demo", "cust_prisma_original_customer"],
      licenseIds: ["lic_demo_tablet_pro", "lic_prisma_original_customer_001"],
      authorityChoices: [
        { id: "setup_claim_or_refresh", label: "Usar Setup Code / License Refresh", safeToApply: false, recommended: true, reason: "Ruta producto: reclama slot/refresca licencia sin editar license.json." },
        { id: "use_pos_local_seed", label: "Usar DB POS local seed", safeToApply: false, recommended: false, reason: "Requiere licencia/setup compatible con biz_prisma_rey_lineage_seed." },
        { id: "use_signed_activation_package", label: "Usar paquete firmado externo", safeToApply: false, recommended: false, reason: "Requiere provisionar POS local al mundo firmado." }
      ],
      selectedAuthority: selectedSupportAuthority(),
      recommendedAuthority: "setup_claim_or_refresh",
      message: "Hay más de una identidad candidata; elige autoridad antes de mutar.",
      secretsExposed: false
    };
  }

  function normalizeSupportSimulation(result) {
    const selectedAuthority = selectedSupportAuthority();
    if (result?.resultCode === "IDENTITY_RECONCILIATION_REQUIRED" || result?.primaryIssueCode === "CROSS_SOURCE_IDENTITY_SPLIT") return result;
    const diagnosis = result?.diagnosis || state.supportDiagnosis || {};
    const issueCodes = (diagnosis.issues || []).map((item) => item.code);
    const looksLikeSplit = issueCodes.includes("LICENSE_ASSIGNMENT_WRONG_BUSINESS") || issueCodes.includes("RUNTIME_IDENTITY_DEMO_MODE") || selectedSupportCode() === "CROSS_SOURCE_IDENTITY_SPLIT";
    if (!looksLikeSplit) return result;
    const reconciliation = state.supportSearch?.reconciliation || diagnosis.issues?.find((item) => item.reconciliation)?.reconciliation || supportFallbackReconciliation();
    return {
      ...result,
      ok: true,
      resultCode: "IDENTITY_RECONCILIATION_REQUIRED",
      primaryIssueCode: "CROSS_SOURCE_IDENTITY_SPLIT",
      dryRun: true,
      wouldMutate: false,
      safeToApply: false,
      safeToApplyReason: "Apply remains blocked because multiple authority candidates exist. Choose Setup Code/Refresh, POS local seed, or signed activation package first.",
      wouldChange: [],
      touches: [],
      authorityChoices: reconciliation.authorityChoices || [],
      selectedAuthority,
      recommendedAuthority: reconciliation.recommendedAuthority || "setup_claim_or_refresh",
      candidateWorlds: reconciliation.worlds || [],
      identityReconciliation: reconciliation,
      reconciliation,
      diagnosis: { ...diagnosis, resultCode: "CROSS_SOURCE_IDENTITY_SPLIT", primaryIssueCode: "CROSS_SOURCE_IDENTITY_SPLIT" },
      clientSideStaleBridge: result?.resultCode === "SIMULATION_READY",
      secretsExposed: false
    };
  }

  function supportCodeDetail() {
    const selected = selectedSupportCode();
    const item = (supportCatalog().codes || []).find((code) => code.code === selected) || {};
    return list([
      ["Código", item.code || selected],
      ["Categoría", item.category || "-"],
      ["Severidad", item.severity || "-"],
      ["Cliente", item.customerExplanation || "-"],
      ["Técnico", item.technicalExplanation || "-"],
      ["Evidencia", (item.requiredEvidence || []).join(", ") || "-"],
      ["Resolución", item.suggestedResolution || "-"],
      ["Remoto", item.remoteResolvable ? "sí" : "no"],
      ["Setup Code", item.requiresSetupCode ? "sí" : "no"],
      ["Admin token", item.requiresAdminToken ? "presence-only/server-side" : "no"],
      ["Codex", item.requiresCodex ? "sí" : "no"],
      ["Presencial", item.requiresOnsite ? "sí" : "no"]
    ]);
  }

  function supportSearchControls() {
    const query = flowValue("supportQuery", FIRST_CUSTOMER_NAME);
    return `<div class="cc-flow-grid">
      <label class="cc-field"><span>Buscar</span><input data-flow-field="supportQuery" value="${esc(query)}" placeholder="cliente, licencia, device, terminal, setup, código" /></label>
      ${supportCodeSelector()}
      ${supportAuthoritySelector()}
      ${supportSetupCodeField()}
    </div>${actions([
      actionButton("support-search", "Buscar", "primary"),
      actionButton("support-diagnose", "Diagnosticar"),
      actionButton("support-simulate", "Simular resolución"),
      actionButton("support-export-case", "Exportar evidencia"),
      actionButton("copy-support", "Copiar resumen")
    ])}`;
  }

  function supportResultsTables() {
    const result = state.supportSearch || {};
    const clients = (result.customers || []).map((row) => ({ Cliente: row.customer, Empresa: row.business, Email: row.email, Teléfono: row.phone, Licencias: row.licenses, Dispositivos: row.devices, Estado: row.status, Issue: row.primaryIssue, Acción: row.action }));
    const licenses = (result.licenses || []).map((row) => ({ "License ID": row.licenseId, Cliente: row.customer, Negocio: row.business, Plan: row.plan, Estado: row.status, Vigencia: row.validUntil, Assignment: row.assignment, Issue: row.primaryIssue, Acción: row.action }));
    const devices = (result.devices || []).map((row) => ({ "Device ID": row.deviceId, Surface: row.surface, Slot: row.slot, Estado: row.status, Cliente: row.customer, Negocio: row.business, Store: row.store, Terminal: row.terminal, "Último visto": row.lastSeenAt, Issue: row.primaryIssue, Acción: row.action }));
    const terminals = (result.terminals || []).map((row) => ({ "Terminal ID": row.terminalId, Nombre: row.name, Sucursal: row.store, Activa: row.active ? "sí" : "no", Device: row.assignedDevice, Caja: row.cashOpen === true ? "abierta" : row.cashOpen === false ? "cerrada" : "sin dato", "Última venta": row.lastSale, Issue: row.issue, Acción: row.action }));
    const events = (result.events || []).map((row) => ({ Fecha: row.date, Evento: row.event, Cliente: row.customer, Device: row.device, Resultado: row.result, Issue: row.issue, Evidencia: row.evidence }));
    return [
      panel("Clientes", "Resultados humanos y técnicos.", table(["Cliente", "Empresa", "Email", "Teléfono", "Licencias", "Dispositivos", "Estado", "Issue", "Acción"], clients, "Ejecuta búsqueda."), { span: 12, tag: result.sourceMode || "SEARCH" }),
      panel("Licencias", "Asignación, plan y vigencia.", table(["License ID", "Cliente", "Negocio", "Plan", "Estado", "Vigencia", "Assignment", "Issue", "Acción"], licenses, "Sin licencias."), { span: 12, tag: `${licenses.length} filas` }),
      panel("Dispositivos", "Slots, surface y último estado.", table(["Device ID", "Surface", "Slot", "Estado", "Cliente", "Negocio", "Store", "Terminal", "Último visto", "Issue", "Acción"], devices, "Sin dispositivos."), { span: 12, tag: `${devices.length} filas` }),
      panel("Terminales y caja", "Terminal local y estado de caja.", table(["Terminal ID", "Nombre", "Sucursal", "Activa", "Device", "Caja", "Última venta", "Issue", "Acción"], terminals, "Sin terminales."), { span: 12, tag: `${terminals.length} filas` }),
      panel("Auditoría y eventos", "Eventos sanitizados para caso.", table(["Fecha", "Evento", "Cliente", "Device", "Resultado", "Issue", "Evidencia"], events, "Sin eventos."), { span: 12, tag: "AUDIT" })
    ].join("");
  }

  function support360Panels() {
    const result = state.supportSearch || {};
    const customer = result.customers?.[0] || {};
    const device = result.devices?.[0] || {};
    const diagnosis = state.supportDiagnosis || {};
    const status = diagnosis.surfaceStatus?.[0] || {};
    return [
      panel("Customer 360", "Cliente, licencia, slots y acciones disponibles.", list([
        ["Cliente", customer.customer || FIRST_CUSTOMER_NAME],
        ["Empresa", customer.business || "Prisma Rey"],
        ["Licencias", customer.licenses ?? "-"],
        ["Dispositivos", customer.devices ?? "-"],
        ["Setup Codes", "redacted-present"],
        ["Issue principal", diagnosis.primaryIssueCode || customer.primaryIssue || "CROSS_SOURCE_IDENTITY_SPLIT"],
        ["Siguiente acción", diagnosis.recommendedAction || "Elegir autoridad y simular antes de mutar"]
      ]), { span: 6, tag: "360" }),
      panel("Device 360", "Surface, slot, runtime, licencia e issues activos.", list([
        ["Device ID", device.deviceId || "tablet-pos-source-ready"],
        ["Surface", device.surface || "tablet"],
        ["Slot", device.slot || "Tablet POS Slot"],
        ["Cliente", device.customer || "cust_demo"],
        ["Negocio", device.business || "biz_demo"],
        ["Store", device.store || "store_prisma_rey_centro"],
        ["Terminal", device.terminal || "term_tablet_pos_001"],
        ["Operación", status.operationStatus || "blocked"],
        ["Issue principal", status.primaryIssueCode || customer.primaryIssue || "CROSS_SOURCE_IDENTITY_SPLIT"]
      ]), { span: 6, tag: status.operationStatus || "STATUS" })
    ].join("");
  }

  function supportReconciliationPanel() {
    const rec = state.supportSimulation?.reconciliation || state.supportSearch?.reconciliation || state.supportDiagnosis?.issues?.[0]?.reconciliation || {};
    const worlds = (rec.worlds || []).map((row) => ({
      Fuente: row.label || row.id,
      Cliente: row.customerId || "-",
      Negocio: row.businessId || "-",
      Store: row.storeId || "-",
      Terminal: row.terminalId || "-",
      Device: row.deviceId || row.tabletDeviceId || "-",
      Acción: row.authorityAction || "review"
    }));
    const choices = (rec.authorityChoices || []).map((row) => `${row.recommended ? "★ " : ""}${row.label || row.id}: ${row.reason || "revisar"}`);
    return panel("Reconciliación de identidad", "PC/Admin, runtime, licencia, DB POS y activación firmada como fuentes técnicas; ninguna se copia como segunda verdad.", [
      table(["Fuente", "Cliente", "Negocio", "Store", "Terminal", "Device", "Acción"], worlds, "Ejecuta búsqueda o simulación para ver mundos candidatos."),
      list([
        ["Split detectado", rec.splitDetected ? "sí" : "pendiente"],
        ["Autoridad seleccionada", selectedSupportAuthority()],
        ["Recomendación", rec.recommendedAuthority || "setup_claim_or_refresh"],
        ["Opciones", choices.join(" | ") || "Setup Code / Refresh, DB POS local seed, paquete firmado externo"]
      ])
    ].join(""), { span: 12, tag: rec.primaryIssueCode || "IDENTITY" });
  }



  function supportApplyPlanPanel() {
    const apply = state.supportApplyPlan || {};
    const sim = state.supportSimulation || {};
    const guide = apply.guidedResolution || sim.guidedResolution || {};
    const plan = apply.applyPlan || {};
    const required = plan.requiredBeforeMutation || guide.blockedUntil || [];
    const writes = plan.localWritePlan || [];
    return panel("Apply seguro / preflight", "Setup Code / License Refresh no escribe hasta licencia firmada, backup y rollback.", [
      list([
        ["Resultado", apply.resultCode || guide.resultCode || "pendiente"],
        ["Setup Code", plan.setupCodePresent ? "presente" : "requerido"],
        ["Mutación", apply.mutationPerformed === true ? "sí" : "no"],
        ["SafeToApply", apply.safeToApply === true ? "sí" : "no"],
        ["Rollback", plan.rollbackAvailable || apply.rollbackAvailable ? "disponible" : "pendiente"],
        ["Siguiente backend", apply.nextBackendAction || guide.futureApplyAction || "setup_claim_or_refresh_apply_with_backup_rollback"]
      ]),
      table(["Path", "Fuente", "Operación"], writes.map((row) => ({ Path: row.path, Fuente: row.source, Operación: row.operation })), "Simula o presiona Resolver problema para generar plan."),
      `<div class="cc-muted"><strong>Bloqueado hasta:</strong><br>${(required || []).map((x) => esc(String(x))).join("<br>") || "setupCode, licencia firmada, backup y rollback"}</div>`
    ].join(""), { span: 12, tag: apply.resultCode || "PREFLIGHT" });
  }

  function renderSupport() {
    const d = derived();
    const notes = d.notes || [];
    const diagnosis = state.supportDiagnosis || {};
    return [
      panel("Prisma Support Resolver Center", "Buscar, diagnosticar, simular y exportar casos sin exponer secretos.", supportSearchControls(), { span: 7, tag: diagnosis.primaryIssueCode || "CENTER" }),
      panel("Selector de códigos", "Explicación humana, técnica, evidencia y acción recomendada.", supportCodeDetail(), { span: 5, tag: selectedSupportCode() }),
      support360Panels(),
      supportReconciliationPanel(),
      supportApplyPlanPanel(),
      supportResultsTables(),
      panel("Acciones resolutivas", "Resolver problema permanece bloqueado hasta simulación segura, confirmación y rollback.", actions([
        actionButton("support-diagnose", "Diagnosticar", "primary"),
        actionButton("support-simulate", "Simular resolución"),
        actionButton("support-apply", "Resolver problema"),
        actionButton("support-export-case", "Exportar evidencia"),
        actionButton("copy-support", "Copiar resumen para soporte"),
        actionButton("create-note", "Agregar nota interna")
      ]), { span: 7, tag: state.supportSimulation?.safeToApply ? "READY" : "GUARDED" }),
      panel("Notas recientes", "Contexto rápido del caso.", list(notes, "Sin notas visibles todavía."), { span: 5, tag: `${notes.length} notas` }),
      resultPanel()
    ].join("");
  }

  function renderSecurity() { const c=localCounts(); return [
    panel("Preparar baja","Baja segura por catálogo: objetivo, motivo, impacto y folio automático.",deactivationWizard(),{span:8,tag:"BAJA"}),
    panel("Impacto","La baja queda preparada, auditada y sin tocar cloud real.",list([["Cloud","no tocado"],["Historial","se conserva"],["Confirmación","local prepared"],["Motivo Otro","requiere texto"]]),{span:4,tag:"SAFE"}),
    panel("Mesa de bajas","Constancias preparadas para revisión.",localDesk("deactivations","Todavía no hay bajas preparadas."),{span:12,tag:`${c.deactivations||0} local`}),
    panel("Otros de baja","Motivos manuales enviados a revisión de catálogo.",localDesk("othersPending","No hay valores Otro pendientes."),{span:12,tag:"CATÁLOGO"}),
    resultPanel()
  ].join(""); }
  function renderSystem() {
    const modules = state.contract?.modules || [];
    const events = state.runtime?.events || [];
    return [
      panel("DB del cockpit", "Estado local Prisma/SQLite del Command Center.", dbStatusPanel(), { span: 4, tag: "DB LOCAL" }),
      panel("Herramientas técnicas", "License Diagnostics, runtime y raw evidence para soporte técnico.", actions([actionButton("export-diagnostics", "Exportar diagnóstico", "primary"),actionButton("refresh", "Actualizar sistema"),actionButton("copy-endpoint-matrix", "Copiar endpoint matrix"),actionButton("copy-local-desk", "Copiar escritorio local")]), { span: 4, tag: state.health?.overall || state.health?.status || "SYSTEM" }),
      panel("Runtime", "Mensajes locales recientes.", list(events.slice(-12).reverse().map((item) => [item.time || item.ts || "evento", item.message || item.kind || JSON.stringify(item).slice(0, 120)]), "Sin eventos runtime."), { span: 4, tag: `${events.length} eventos` }),
      panel("Auditoría local", "Eventos generados por altas, licencias, dispositivos, bajas y Otros.", localDesk("events", "Sin auditoría local."), { span: 12, tag: "AUDIT" }),
      panel("License Route Map", "Detalle técnico permitido sólo en System.", list(endpointRows(LICFLOW3_ENDPOINT_MATRIX)), { span: 12, tag: "MATRIX" }),
      panel("Contrato de módulos", "Legado técnico retenido sólo como evidencia.", list(modules.map((m) => [m.name || m.id, `${m.statusLabel || "-"} · ${m.port || "-"}`])), { span: 6, tag: `${modules.length} módulos` }),
      panel("Raw técnico", "Payloads redacted para diagnóstico.", details("Abrir raw system", { health: state.health, runtime: state.runtime, contract: state.contract, licflow3Contract: state.data?.licflow3Contract, licflow4Bridge: state.bridge, commandCenter: ccStore() }, false), { span: 6, tag: "RAW" }),
      resultPanel()
    ].join("");
  }
  const renderers = {
    command: renderCommand,
    customers: renderCustomers,
    entitlements: renderEntitlements,
    fleet: renderFleet,
    provisioning: renderProvisioning,
    "customer-setup": renderCustomerSetup,
    contracts: renderContracts,
    operations: renderOperations,
    support: renderSupport,
    security: renderSecurity,
    "tablet-lab": renderTabletLab,
    system: renderSystem
  };

  function render() {
    updateChrome();
    updateSurfaceHeader();
    const renderer = renderers[state.surface] || renderCommand;
    $("surfaceRoot").innerHTML = renderer();
  }

  async function loadAll() {
    const [data, license, health, runtime, contract, commandCenter, bridge, supportCatalogPayload, supportSearchPayload] = await Promise.all([
      safeApi("/api/cloud-saas/summary"),
      safeApi("/api/license-ops/latest"),
      safeApi("/api/health"),
      safeApi("/api/runtime"),
      safeApi("/api/contract"),
      safeApi("/api/command-center/bootstrap"),
      safeApi("/api/licflow4/bridge/status"),
      safeApi("/api/support/catalog"),
      safePost("/api/support/search", { query: flowValue("supportQuery", FIRST_CUSTOMER_NAME) })
    ]);
    state.data = data;
    state.license = license;
    state.health = health;
    state.runtime = runtime;
    state.contract = contract;
    state.commandCenter = commandCenter;
    state.bridge = bridge;
    state.supportCatalog = supportCatalogPayload;
    state.supportSearch = supportSearchPayload;
    state.lastLoadedAt = new Date().toLocaleString();
    render();
  }

  async function postAction(path, body) {
    return api(path, { method: "POST", body: JSON.stringify(body || {}) });
  }

  function go(surface) {
    const next = SURFACES.some(([id]) => id === surface) ? surface : "command";
    state.surface = next;
    const hash = `#${next}`;
    if (window.location.hash !== hash) window.location.hash = hash;
    render();
  }

  function readHashSurface() {
    const raw = (window.location.hash || "#command").replace(/^#\/?/, "").trim();
    return SURFACES.some(([id]) => id === raw) ? raw : "command";
  }


  function collectOtherValues(){ const out={}; Object.keys(state.flow||{}).forEach((key)=>{ if(!key.endsWith("Other")) return; const base=key.replace(/Other$/,""); if(state.flow[base]==="other" && String(state.flow[key]||"").trim()) out[base]=String(state.flow[key]).trim(); }); return out; }
  async function saveOtherValues(){ const map={vertical:"vertical",subvertical:"subvertical",operationMode:"operation_mode",deviceType:"device_type",reason:"deactivation_reason",cityZone:"city_zone"}; const other=collectOtherValues(); const saved=[]; for(const [field,manualText] of Object.entries(other)){ const catalog=map[field]; if(!catalog) continue; saved.push(await postAction("/api/command-center/other",{catalog,manualText,context:{field,surface:state.surface}})); } return {ok:saved.every((x)=>x.ok), saved:saved.length, items:saved}; }

  async function handleAction(action, button) {
    if (state.busy) return;
    state.busy = true;
    if (button) button.disabled = true;
    try {
      let result;
      if (action === "refresh") {
        await loadAll();
        setResult("Actualización", "Datos actualizados desde el bridge local.", { ok: true, loadedAt: state.lastLoadedAt }, { kind: "ok" });
        toast("Datos actualizados");
      } else if (action.startsWith("licflow4-dryrun-") || action.startsWith("licflow4-run-")) {
        const dryRun = action.startsWith("licflow4-dryrun-");
        const bridgeAction = action.replace(/^licflow4-(dryrun|run)-/, "");
        const payload = bridgePayload(bridgeAction, dryRun);
        try {
          result = await postAction(`/api/licflow4/bridge/${bridgeAction}`, payload);
        } catch (error) {
          result = error.payload || { ok: false, code: "BRIDGE_REQUEST_FAILED", error: String(error.message || error), secretsExposed: false };
        }
        setResult(
          `License Admin Bridge ${bridgeAction}`,
          result.ok ? `${dryRun ? "Simulation (Dry Run)" : "Confirmed License Operation"} ${bridgeAction} procesada por backend.` : `${bridgeAction} bloqueado: ${result.code || "REVIEW"}`,
          result,
          { kind: result.ok ? "ok" : "warn" }
        );
        toast(result.ok ? `License Admin Bridge ${bridgeAction} OK` : `License Admin Bridge ${bridgeAction} bloqueado`);
        await loadAll();
      } else if (action === "show-problems") {
        const problems = collectProblems();
        setResult("Problemas", problems.length ? `${problems.length} punto(s) para revisar.` : "Sin bloqueadores visibles.", { ok: !problems.length, problems }, { kind: problems.length ? "warn" : "ok" });
        toast(problems.length ? "Hay puntos por revisar" : "Sin bloqueadores visibles");
      } else if (action === "support-search") {
        result = await safePost("/api/support/search", supportRequestPayload());
        state.supportSearch = result;
        setResult("Búsqueda de soporte", result.ok ? "Resultados de soporte actualizados." : "La búsqueda quedó clasificada para revisión.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Búsqueda lista" : "Búsqueda a revisar");
      } else if (action === "support-diagnose") {
        result = await safePost("/api/support/diagnose", supportRequestPayload());
        state.supportDiagnosis = result;
        setResult("Diagnóstico", result.ok ? `Issue principal: ${result.primaryIssueCode || "OK"}` : "Diagnóstico bloqueado.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Diagnóstico listo" : "Diagnóstico a revisar");
      } else if (action === "support-simulate") {
        result = normalizeSupportSimulation(await safePost("/api/support/resolve/simulate", supportRequestPayload()));
        state.supportSimulation = result;
        state.supportDiagnosis = result.diagnosis || state.supportDiagnosis;
        const simMessage = result.resultCode === "SETUP_CLAIM_OR_REFRESH_GUIDED"
          ? "Setup Code / License Refresh guiado: input requerido; no se mutó nada."
          : (result.resultCode === "IDENTITY_RECONCILIATION_REQUIRED" ? "Reconciliación requerida: hay varias identidades candidatas; no se mutó nada." : (result.ok ? "Dry-run completado sin mutación." : "Simulación bloqueada."));
        setResult("Simulación", simMessage, result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Simulación lista" : "Simulación a revisar");
      } else if (action === "support-apply") {
        result = await safePost("/api/support/resolve/apply", supportRequestPayload({ confirmResolutionAction: true, operatorConfirmation: true }));
        state.supportApplyPlan = result;
        const noMutation = result?.mutationPerformed === false;
        const preflightReady = result?.resultCode === "SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY";
        const inputRequired = result?.resultCode === "SETUP_CLAIM_OR_REFRESH_INPUT_REQUIRED";
        const applyMessage = preflightReady
          ? "Preflight listo; no se mutó nada. Falta claim/refresh real y licencia firmada verificada."
          : inputRequired
            ? "Setup Code requerido; no se mutó nada."
            : (result.ok && !noMutation ? "Acción aplicada." : `${result.resultCode || "APPLY_BLOCKED"}: no se mutó nada.`);
        setResult("Resolver problema", applyMessage, result, { kind: preflightReady ? "ok" : "warn" });
        toast(preflightReady ? "Preflight listo" : (inputRequired ? "Setup Code requerido" : "Resolución bloqueada"));
      } else if (action === "support-export-case") {
        result = await safePost("/api/support/export-case", supportRequestPayload());
        setResult("Exportar evidencia", result.ok ? "Caso de soporte preparado con redacción." : "Exportación bloqueada.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Evidencia lista" : "Evidencia a revisar");
      } else if (action === "copy-exec") {
        await copyText(executiveSummary(), "Resumen ejecutivo");
      } else if (action === "copy-customer") {
        await copyText(customerSummary(), "Resumen del cliente");
      } else if (action === "copy-license") {
        const license = state.license?.runtime?.license || derived().license || {};
        await copyText(["FICHA DE LICENCIA", `Estado: ${license.status || state.license?.status || "revisar"}`, `Plan: ${license.plan || "-"}`, `Vigencia: ${license.validUntil || "-"}`, `Cliente: ${license.assignment?.clientId || FIRST_CUSTOMER_NAME}`].join("\n"), "Ficha de licencia");
      } else if (action === "copy-fleet") {
        await copyText(`Fleet ${FIRST_CUSTOMER_NAME}\nDispositivos: ${safeCount(derived().devices)}\nReceipts: ${safeCount(derived().receipts)}\nEventos: ${safeCount(derived().events)}\nEstado: ${mainStatus()}`, "Estado de fleet");
      } else if (action === "copy-provisioning") {
        await copyText(provisioningChecklist().map(([label, ok]) => `${ok ? "[x]" : "[ ]"} ${label}`).join("\n"), "Checklist de alta");
      } else if (action === "copy-contract") {
        await copyText(`Contrato ${FIRST_CUSTOMER_NAME}\nEstado: ${derived().publicContract?.status || endpointState("clientContract").code}\nCapacidades: ${endpointState("capabilities").code}\nLicencia: ${state.license?.runtime?.license?.status || derived().license?.status || "revisar"}`, "Resumen de contrato");
      } else if (action === "copy-ops") {
        await copyText(executiveSummary(), "Digest operativo");
      } else if (action === "copy-support") {
        await copyText(supportPacket(), "Paquete de soporte");
      } else if (action === "copy-security") {
        const admin = state.data?.admin || {};
        const bridge = licflow4Bridge();
        await copyText(`Seguridad Prisma Cloud Center\nModo: ${admin.enabled ? "confirmed operations backend" : "lectura segura"}\nLicense Admin Bridge: ${bridge.ok ? "disponible" : "revisar"}\nAdmin Token Status: ${bridge.adminTokenPresent === true ? "presence-only" : "missing"}\nValor de token leido en frontend: false\nConfirmed License Operation: solo por /api/licflow4/bridge con confirmación explícita\nEstado: ${mainStatus()}`, "Resumen de seguridad");
      } else if (action === "copy-endpoint-matrix") {
        await copyText(endpointRows(LICFLOW3_ENDPOINT_MATRIX).map(([a, b]) => `${a}: ${b}`).join("\n"), "License Route Map");
      } else if (action === "compare-license-contract" || action === "compare-contract") {
        const license = state.license?.runtime?.license || derived().license || {};
        const contract = derived().publicContract || {};
        const comparison = {
          ok: true,
          licenseStatus: license.status || "review",
          licensePlan: license.plan || null,
          contractStatus: contract.status || endpointState("clientContract").code,
          contractPlan: contract.plan || null,
          recommendation: (license.plan && contract.plan && license.plan !== contract.plan) ? "Revisar diferencia de plan." : "Sin diferencia obvia de plan."
        };
        setResult("Comparación", comparison.recommendation, comparison, { kind: comparison.recommendation.startsWith("Revisar") ? "warn" : "ok" });
        toast("Comparación lista");
      } else if (action === "security-check") {
        const keys = Object.keys(window.localStorage || {}).filter((key) => /token|secret|auth/i.test(key));
        setResult("Seguridad", keys.length ? "Hay llaves sospechosas en localStorage." : "Browser limpio: no se detectaron llaves token/secret/auth en localStorage.", { ok: !keys.length, suspiciousLocalStorageKeys: keys }, { kind: keys.length ? "warn" : "ok" });
        toast(keys.length ? "Revisar localStorage" : "Browser limpio");
      } else if (action === "clear-cache") {
        ["prisma-cloud-ctr-cache", "cc-last-surface"].forEach((key) => localStorage.removeItem(key));
        setResult("Cache", "Cache local visual limpiada sin tocar token ni datos server-side.", { ok: true }, { kind: "ok" });
        toast("Cache local limpiada");
      } else if (action === "create-note") {
        const text = $("supportNoteText")?.value || "Nota interna desde Prisma Cloud Center.";
        result = await postAction("/api/cloud-saas/notes", { text });
        setResult("Nota interna", result.ok ? `Nota creada en ${FIRST_CUSTOMER_NAME}.` : "La nota no se confirmó; revisar evidencia.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Nota creada" : "Nota a revisar");
        await loadAll();
      } else if (action === "receipt-smoke") {
        result = await postAction("/api/cloud-saas/receipt-smoke", {});
        setResult("Receipt de prueba", result.ok ? "Receipt de prueba enviado." : "Receipt de prueba bloqueado o no confirmado.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Receipt enviado" : "Receipt bloqueado");
        await loadAll();
      } else if (action === "device-smoke") {
        result = await postAction("/api/cloud-saas/device-register-smoke", {});
        setResult("Dispositivo de prueba", result.ok ? "Registro de prueba enviado." : "Registro bloqueado o no confirmado.", result, { kind: result.ok ? "ok" : "warn" });
        toast(result.ok ? "Dispositivo registrado" : "Registro bloqueado");
        await loadAll();
      } else if (action === "prepare-client") { result = await postAction("/api/command-center/draft-client", { ...state.flow, other: collectOtherValues() }); setResult("Alta preparada", result.message || "Cliente preparado localmente.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.ok ? "Alta preparada" : "Alta a revisar"); await loadAll();
      } else if (action === "prepare-device") { result = await postAction("/api/command-center/draft-device", { ...state.flow, other: collectOtherValues() }); setResult("Dispositivo preparado", result.message || "Dispositivo preparado localmente.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.ok ? "Dispositivo preparado" : "Dispositivo a revisar"); await loadAll();
      } else if (action === "prepare-license") { result = await postAction("/api/command-center/draft-license", { ...state.flow, other: collectOtherValues() }); setResult("Licencia preparada", result.message || "Licencia preparada localmente.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.ok ? "Licencia preparada" : "Licencia a revisar"); await loadAll();
      } else if (action === "prepare-deactivation") { result = await postAction("/api/command-center/draft-deactivation", { ...state.flow, other: collectOtherValues() }); setResult("Baja preparada", result.message || "Baja preparada localmente.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.ok ? "Baja preparada" : "Baja a revisar"); await loadAll();
      } else if (action === "save-other-values") { result = await saveOtherValues(); setResult("Otros pendientes", result.saved ? `${result.saved} valor(es) enviados a revisión de catálogo.` : "No hay valores Otro para guardar.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.saved ? "Otros guardados" : "Sin otros nuevos"); await loadAll();
      } else if (action === "copy-local-desk") {
        await copyText(localSummaryText(), "Escritorio local");
      } else if (action === "copy-clients-local") {
        await copyText(localRows("clients").map((r)=>localPlainSummary("clients", r)).join("\n\n") || "Sin clientes locales.", "Clientes locales");
      } else if (action === "copy-licenses-local") {
        await copyText(localRows("licenses").map((r)=>localPlainSummary("licenses", r)).join("\n\n") || "Sin licencias locales.", "Licencias locales");
      } else if (action === "copy-devices-local") {
        await copyText(localRows("devices").map((r)=>localPlainSummary("devices", r)).join("\n\n") || "Sin dispositivos locales.", "Dispositivos locales");
      } else if (action === "export-diagnostics") {
        result = await postAction("/api/export-diagnostics", {});
        setResult("Diagnóstico", "Diagnóstico exportado por Prisma Cloud Center.", result, { kind: result.ok === false ? "warn" : "ok", surface: "system" });
        toast("Diagnóstico exportado");
      }
      render();
    } catch (error) {
      const payload = error.payload || { ok: false, error: String(error.message || error) };
      setResult("Error", String(error.message || error), payload, { kind: "bad" });
      toast(String(error.message || error));
      render();
    } finally {
      state.busy = false;
      if (button) button.disabled = false;
    }
  }

  function boot() {
    state.surface = readHashSurface();
    $$(".cc-nav button").forEach((button) => {
      button.addEventListener("click", () => go(button.dataset.surface || "command"));
    });
    window.addEventListener("hashchange", () => {
      state.surface = readHashSurface();
      render();
    });
    document.addEventListener("input", (event) => {
      const filter = event.target.closest("[data-picker-filter]");
      if (filter) {
        const panel = filter.closest("[data-picker-panel]");
        const q = String(filter.value || "").trim().toLowerCase();
        if (panel) panel.querySelectorAll("[data-picker-search]").forEach((row) => { row.hidden = q && !String(row.dataset.pickerSearch || "").includes(q); });
        return;
      }
      const field=event.target.closest("[data-flow-field]");
      if(field){ state.flow[field.dataset.flowField]=field.value; render(); return; }
      const other=event.target.closest("[data-other-for]");
      if(other){ state.flow[other.dataset.otherFor+"Other"]=other.value; }
    });
    document.addEventListener("change", (event) => { const field=event.target.closest("[data-flow-field]"); if(field){ state.flow[field.dataset.flowField]=field.value; render(); } });
    document.addEventListener("click", (event) => {
      const pickerToggleNode = event.target.closest("[data-picker-toggle]");
      if (pickerToggleNode) {
        const pickerId = pickerToggleNode.dataset.pickerToggle || "";
        state.openPicker = state.openPicker === pickerId ? null : pickerId;
        render();
        return;
      }
      const actionButtonNode = event.target.closest("[data-action]");
      if (actionButtonNode) {
        handleAction(actionButtonNode.dataset.action, actionButtonNode);
        return;
      }
      const pickNode = event.target.closest("[data-pick-flow]");
      if (pickNode) {
        const field = pickNode.dataset.pickFlow;
        const value = pickNode.dataset.value || "";
        if (field) {
          state.flow[field] = value;
          state.openPicker = null;
          render();
        }
        return;
      }
      const deskRowNode = event.target.closest("[data-desk-kind][data-desk-index]");
      if (deskRowNode) {
        const kind = deskRowNode.dataset.deskKind;
        const index = Number(deskRowNode.dataset.deskIndex || "-1");
        const row = localRows(kind)[index];
        if (row) {
          setResult(localDeskTitle(kind), "Detalle local listo para copiar o revisar.", { ok: true, kind, row, text: localPlainSummary(kind, row) }, { kind: "ok" });
          render();
        }
        return;
      }
      const goButtonNode = event.target.closest("[data-go]");
      if (goButtonNode) {
        go(goButtonNode.dataset.go || "command");
      }
    });
    loadAll();
    setInterval(loadAll, 30000);
  }

  window.addEventListener("DOMContentLoaded", boot);
})();

// === PRISMA RECON4 SETUP CLAIM OR REFRESH GUIDE UI START ===

(function prismaRecon4SetupGuideUi(){
  if (typeof window === "undefined" || window.__PRISMA_RECON4_SETUP_GUIDE_UI__) return;
  window.__PRISMA_RECON4_SETUP_GUIDE_UI__ = true;
  function compact(value){ return value === null || value === undefined || value === "" ? "sin dato" : String(value); }
  function findGuide(value){
    if (!value || typeof value !== "object") return null;
    if (value.guidedResolution && value.guidedResolution.id === "setup_claim_or_refresh") return value.guidedResolution;
    if (value.simulation && value.simulation.guidedResolution) return value.simulation.guidedResolution;
    if (value.payload) return findGuide(value.payload);
    return null;
  }
  function findJsonGuideFromDom(){
    var nodes = Array.prototype.slice.call(document.querySelectorAll("pre, code, textarea"));
    for (var i = 0; i < nodes.length; i++) {
      var text = nodes[i].value || nodes[i].textContent || "";
      if (text.indexOf("setup_claim_or_refresh") === -1 || text.indexOf("guidedResolution") === -1) continue;
      try { var parsed = JSON.parse(text); var guide = findGuide(parsed); if (guide) return guide; } catch (_) {}
    }
    return null;
  }
  function renderGuide(guide){
    if (!guide || guide.id !== "setup_claim_or_refresh") return;
    var root = document.querySelector("#support") || document.querySelector("[data-section='support']") || document.body;
    if (!root) return;
    var card = document.getElementById("prisma-recon4-setup-guide");
    if (!card) {
      card = document.createElement("section");
      card.id = "prisma-recon4-setup-guide";
      card.className = "cc-card support-recon4-guide";
      card.style.marginTop = "16px";
      card.style.padding = "14px";
      card.style.border = "1px solid rgba(148,163,184,.28)";
      card.style.borderRadius = "18px";
      card.style.background = "rgba(255,255,255,.72)";
      root.appendChild(card);
    }
    var auth = guide.candidateAuthority || {};
    var installed = guide.currentlyInstalled || {};
    card.innerHTML = "" +
      "<div style='display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap'>" +
      "<div><strong>Setup Code / License Refresh guiado</strong><p style='margin:.25rem 0 0'>" + compact(guide.humanExplanation) + "</p></div>" +
      "<span style='font-size:12px;padding:4px 8px;border-radius:999px;border:1px solid rgba(148,163,184,.35)'>" + compact(guide.stage) + "</span>" +
      "</div>" +
      "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:12px'>" +
      "<div><small>Autoridad candidata</small><br><strong>" + compact(auth.customerId) + "</strong><br><span>" + compact(auth.businessId) + "</span></div>" +
      "<div><small>Licencia instalada</small><br><strong>" + compact(installed.customerId) + "</strong><br><span>" + compact(installed.businessId) + "</span></div>" +
      "<div><small>Terminal destino</small><br><strong>" + compact(auth.terminalId) + "</strong><br><span>" + compact(auth.tabletDeviceId) + "</span></div>" +
      "</div>" +
      "<div style='margin-top:12px'><strong>Bloqueado hasta</strong><ul>" + (guide.blockedUntil || []).map(function(x){ return "<li>" + compact(x) + "</li>"; }).join("") + "</ul></div>" +
      "<div style='margin-top:10px'><strong>Checks previos</strong><ul>" + (guide.preflightChecks || []).map(function(x){ return "<li>" + compact(x) + "</li>"; }).join("") + "</ul></div>";
  }
  window.PRISMA_RECON4_RENDER_SETUP_GUIDE = renderGuide;
  document.addEventListener("click", function(){ setTimeout(function(){ var guide = findJsonGuideFromDom(); if (guide) renderGuide(guide); }, 650); }, true);
  setInterval(function(){ var guide = findJsonGuideFromDom(); if (guide) renderGuide(guide); }, 2000);
})();
// === PRISMA RECON4 SETUP CLAIM OR REFRESH GUIDE UI END ===

// === PRISMA RECON5 SETUP CLAIM APPLY PREFLIGHT UI START ===
// recon5: core Support UI functions patched in-place above.
// Expected runtime markers: supportSetupCodeField, supportApplyPlanPanel, SETUP_CLAIM_OR_REFRESH_PREFLIGHT_READY.
// === PRISMA RECON5 SETUP CLAIM APPLY PREFLIGHT UI END ===
