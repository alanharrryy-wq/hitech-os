(function () {
  "use strict";

  const SURFACES = [
    ["command", "Inicio", "¿Qué quieres hacer?", "Acciones claras: nuevo cliente, licencia, dispositivo, baja, clientes activos y soporte sin leer JSON."],
    ["customers", "Clientes", "Clientes activos", "Busca, clasifica y prepara clientes con giros homologados, IDs automáticos y fichas claras."],
    ["entitlements", "Licencias", "Tipos y asignación", "Catálogo de planes, módulos permitidos, vigencia, límites e IDs de licencia generados solos."],
    ["fleet", "Dispositivos", "Agregar y administrar", "Tipos de dispositivo homologados, códigos de registro automáticos y acciones de vinculación."],
    ["provisioning", "Altas", "Alta guiada", "Wizard de alta: datos mínimos, vertical, plan, dispositivo y paquete preparado para activar."],
    ["contracts", "Contracts & Config", "Contrato y configuración", "Contrato actual, capacidades, diferencias visibles y resumen copiable."],
    ["operations", "Reportes", "Clientes activos y operación", "Conteos de clientes, licencias, dispositivos, pendientes y actividad preparada."],
    ["support", "Support", "Soporte", "Paquete de diagnóstico humano con cliente, licencia, contrato, dispositivos y siguiente acción."],
    ["security", "Bajas", "Baja segura", "Suspender, desactivar o preparar baja con motivo homologado, impacto visible y folio automático."],
    ["system", "System", "Cuarto de máquinas", "Runtime, endpoint matrix, selftest, diagnostics y evidencia técnica encerrada aquí."]
  ];
  const FIRST_CUSTOMER_NAME = "Prisma Original Customer";
  const FIRST_TENANT_SLUG = "prisma-original-customer";

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

  const LICFLOW3_ENDPOINT_MATRIX = ["health", "capabilities", "tenantStatus", "adminSelftest", "commercialSummary", "tenantSnapshot", "clientContract", "supportDiagnostics", "licenseActivate", "licenseRefresh", "licenseRevoke", "deviceRegister", "integrationReceipt"];

  function licflow3LiveStatus() {
    return state.data?.licflow3Contract?.hostedCloudEvidenceStatus || state.data?.licflow3Contract?.status || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE";
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
      integrationReceipt: "Recibo integración"
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
    if (data.licflow3Contract?.missing?.length) found.push({ level: "warn", title: "Contrato LICFLOW3 incompleto", detail: `Faltan endpoints: ${data.licflow3Contract.missing.join(", ")}.` });
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
      "Prisma Cloud Ctr",
      `Estado general: ${mainStatus()}`,
      `Cloud: ${state.data?.ok ? "en línea" : "revisar"}`,
      `Cliente: ${d.tenant?.displayName || d.tenant?.slug || state.data?.cloud?.tenantSlug || FIRST_CUSTOMER_NAME}`,
      `Licencia: ${license.status || d.license?.status || state.license?.status || "revisar"}`,
      `Plan: ${license.plan || d.license?.plan || "-"}`,
      `LICFLOW3: ${state.data?.licflow3Contract?.claim || "contract_incomplete"}`,
      `LICFLOW3 live state: ${licflow3LiveStatus()}`,
      `Worker: ${state.data?.licflow3Contract?.worker || "prisma-cloud-semilla"}`,
      `D1: ${state.data?.licflow3Contract?.d1 || "prisma_cloud_semilla"}`,
      `adminTokenPresent: ${adminTokenPresent() ? "true" : "false"}`,
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
    return [
      "PAQUETE DE SOPORTE PRISMA",
      `Cliente: ${d.tenant?.displayName || d.tenant?.slug || FIRST_CUSTOMER_NAME}`,
      `Estado cliente: ${d.tenant?.status || "revisar"}`,
      `Licencia: ${license.status || "revisar"}`,
      `Plan: ${license.plan || d.license?.plan || "-"}`,
      `Contrato: ${contract.status || contract.plan || endpointState("clientContract").code}`,
      `LICFLOW3: ${state.data?.licflow3Contract?.claim || "contract_incomplete"}`,
      `LICFLOW3 live state: ${licflow3LiveStatus()}`,
      `adminTokenPresent: ${adminTokenPresent() ? "true" : "false"}`,
      `Soporte cloud: ${endpointState("supportDiagnostics").code}`,
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
    $("ccMode").textContent = data.mode || "Lectura segura";
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
  function licenseWizard(){ const r=currentRecommendation(); const plan=flowValue("plan",r.plan); const m=planMeta(plan); return `<div class="cc-flow-grid">${selectField("clientCode","Cliente destino","client",flowValue("clientCode"),{})}${selectField("plan","Tipo de licencia","license_plan",plan,{required:true})}${selectField("vertical","Vertical del cliente","vertical",flowValue("vertical","abarrotes"),{})}${selectField("businessSize","Tamaño","business_size",flowValue("businessSize","small"),{})}${selectField("operationMode","Operación","operation_mode",flowValue("operationMode","counter"),{})}</div>${kvGrid([["Máximo dispositivos",m.maxDevices||"según contrato"],["Máximo sucursales",m.maxBranches||"según contrato"],["Módulos",(m.modules||r.modules).join(", ")]])}${actions([actionButton("prepare-license","Preparar licencia + folio","primary"),actionButton("compare-license-contract","Comparar con contrato"),surfaceButton("customers","Ver cliente")])}${details("Licencias preparadas", { licenses: localRows("licenses") }, false)}`; }
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
      ["Dispositivos", c.devices || 0, "Pendientes"],
      ["Bajas", c.deactivations || 0, "Seguras"],
      ["Otros", c.othersPending || 0, "Catálogo"],
      ["Auditoría", c.auditEvents || 0, "Eventos"]
    ].map(([a,b,cx])=>`<div class="cc-desk-metric"><small>${esc(a)}</small><strong>${esc(b)}</strong><span>${esc(cx)}</span></div>`).join("")}</div>`;
  }
  function planCatalogDesk(){
    const plans = ccStore().licensePlans || [];
    if (!plans.length) return `<div class="cc-desk-empty"><strong>Sin planes cargados</strong><span>El catálogo local o fallback todavía no devolvió planes.</span></div>`;
    return `<div class="cc-plan-grid">${plans.map((p)=>`<article class="cc-plan-card"><div><strong>${esc(p.label || p.code)}</strong><small>${esc(p.code || "plan")}</small></div><p>${esc((p.modules || []).join(" · ") || "Módulos pendientes")}</p><footer>${chip("READY", `${p.maxDevices || "N"} disp.`)}${chip("READY", `${p.maxBranches || "N"} suc.`)}</footer></article>`).join("")}</div>`;
  }
  function localSummaryText(){
    const c = localCounts();
    const last = localRows("events").slice(0, 8).map((e)=>`- ${e.createdAt || ""} ${e.entityCode || e.entityKind || "evento"}: ${e.summary || e.eventType || ""}`).join("\n") || "- Sin eventos locales.";
    return [
      "Prisma Cloud Ctr - escritorio local",
      `Clientes: ${c.clients || 0}`,
      `Licencias: ${c.licenses || 0}`,
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
      panel("Acciones principales","Elige la tarea. La cabina genera IDs y usa catálogos; tú no escribes folios.",actions([surfaceButton("provisioning","+ Nuevo cliente"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo"),surfaceButton("security","Dar de baja"),surfaceButton("operations","Ver escritorio local"),surfaceButton("support","Resolver soporte")]),{span:7,tag:"TAREAS"}),
      panel("Escritorio local","Lo que ya existe en la DB del cockpit: clientes, licencias, dispositivos, bajas, otros y auditoría.",localDashboard(),{span:5,tag:`${c.preparedDrafts||0} drafts`}),
      panel("Resumen actual","Lo que está pasando sin tocar acciones admin.",kvGrid([["Cloud",state.data?.ok?"En línea":"Revisar"],["LICFLOW3",licflow3LiveStatus()],["Cliente",d.tenant?.displayName||d.tenant?.slug||FIRST_CUSTOMER_NAME],["adminTokenPresent",adminTokenPresent()?"true":"false"],["Problemas",p.length?`${p.length} por revisar`:"Sin bloqueadores"]]),{span:5,tag:mainStatus()}),
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
      licenseKey: value("licenseKey"),
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
        <label class="cc-field"><span>License key</span><input data-bridge-field="licenseKey" autocomplete="off" placeholder="LIC-..." /></label>
        <label class="cc-field"><span>Device ID</span><input data-bridge-field="deviceId" autocomplete="off" placeholder="device-id" /></label>
        <label class="cc-field"><span>Tenant</span><input data-bridge-field="tenantId" autocomplete="off" value="${esc(FIRST_TENANT_SLUG)}" /></label>
        <label class="cc-field"><span>${revoke ? "Reason" : "Operator note"}</span><input data-bridge-field="${revoke ? "reason" : "operatorNote"}" autocomplete="off" placeholder="${revoke ? "Motivo requerido" : "Nota opcional"}" /></label>
        ${revoke ? `<label class="cc-field" for="bridge-phrase-revoke"><span>Confirm revoke</span><input id="bridge-phrase-revoke" data-bridge-field="confirmRevoke" autocomplete="off" placeholder="REVOKE_LICENSE" /></label>` : ""}
      </div>
      <label class="cc-impact" for="bridge-confirm-${esc(action)}"><input id="bridge-confirm-${esc(action)}" type="checkbox" data-bridge-confirm /> Confirmo acción admin LICFLOW4 para ${esc(label)}<span>El token vive sólo en backend; el browser no lo recibe.</span></label>
      ${actions([
        actionButton(`licflow4-dryrun-${action}`, `Dry-run ${label}`, "secondary"),
        actionButton(`licflow4-run-${action}`, danger ? `Ejecutar ${label}` : `Enviar ${label}`, danger ? "danger" : "primary")
      ])}
    </div>`;
  }

  function bridgePanel() {
    const bridge = licflow4Bridge();
    return [
      kvGrid([
        ["bridgeAvailable", bridge.bridgeAvailable ? "true" : "false"],
        ["adminTokenPresent", bridge.adminTokenPresent ? "true" : "false"],
        ["Worker", bridge.worker || "prisma-cloud-semilla"],
        ["D1", bridge.d1 || "prisma_cloud_semilla"],
        ["Activate", bridge.routes?.activate || "/api/licenses/activate"],
        ["Refresh", bridge.routes?.refresh || "/api/licenses/refresh"],
        ["Revoke", bridge.routes?.revoke || "/api/licenses/revoke"],
        ["Confirmación", "confirmAdminLicenseAction"]
      ]),
      `<div class="cc-empty">LICFLOW4 nunca pide ADMIN_TOKEN en el browser. Las acciones reales requieren token local server-side y confirmación explícita.</div>`,
      bridgeForm("activate", "Activate", false),
      bridgeForm("refresh", "Refresh", false),
      bridgeForm("revoke", "Revoke", true)
    ].join("");
  }

  function renderEntitlements() { const c=localCounts(); return [
    panel("Asignar licencia","Elige cliente y plan desde catálogo. Límites y módulos vienen gobernados.",licenseWizard(),{span:8,tag:"LICENCIA"}),
    panel("Catálogo de planes","Tipos disponibles, límites y módulos incluidos.",planCatalogDesk(),{span:4,tag:`${(ccStore().licensePlans||[]).length} planes`}),
    panel("LICFLOW4 Admin Bridge","Puente local seguro para activate, refresh y revoke sin exponer ADMIN_TOKEN al frontend.",bridgePanel(),{span:12,tag:licflow4Bridge().bridgeAvailable ? "LICFLOW4" : "REVIEW"}),
    panel("Mesa de licencias","Asignaciones preparadas con folio LIC y contrato CTR.",localDesk("licenses","Todavía no hay licencias preparadas."),{span:12,tag:`${c.licenses||0} local`}),
    panel("Reglas","Las licencias locales quedan preparadas; activate/refresh/revoke sólo pasan por LICFLOW4 con confirmación.",list([["Estado","pending_cloud_activation / prepared"],["Folio","LIC-YYYY-000001"],["Contrato","CTR-YYYY-000001"],["Cloud","mutación protegida por bridge"],["Revoke","requiere REVOKE_LICENSE"]]),{span:12,tag:"REGLAS"}),
    resultPanel()
  ].join(""); }
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

  function renderContracts() {
    const d = derived();
    const contract = d.publicContract || {};
    const licflow3 = state.data?.licflow3Contract || {};
    return [
      panel("Contrato actual", "Estado contractual resumido para operar.", kvGrid([
        ["Estado", contract.status || endpointState("clientContract").code],
        ["Plan", contract.plan || derived().license?.plan || "-"],
        ["Cliente", contract.tenant || contract.tenantSlug || d.tenant?.slug || FIRST_CUSTOMER_NAME],
        ["Capacidades", endpointState("capabilities").code]
      ]), { span: 5, tag: endpointState("clientContract").ok ? "CONTRATO" : "REVISAR" }),
      panel("LICFLOW3 live routes", "Cloudflare routes are deployed and protected; unauthenticated POST smoke expects 401 ADMIN_TOKEN_REQUIRED.", kvGrid([
        ["Estado", licflow3.hostedCloudEvidenceStatus || licflow3.status || "LICFLOW3_CLOUDFLARE_ROUTES_LIVE"],
        ["Worker", licflow3.worker || "prisma-cloud-semilla"],
        ["D1", licflow3.d1 || "prisma_cloud_semilla"],
        ["Base", licflow3.configuredBaseUrl || state.data?.cloud?.baseUrl || "-"],
        ["Activate", "POST /api/licenses/activate -> 401 ADMIN_TOKEN_REQUIRED"],
        ["Refresh", "POST /api/licenses/refresh -> 401 ADMIN_TOKEN_REQUIRED"],
        ["Revoke", "POST /api/licenses/revoke -> 401 ADMIN_TOKEN_REQUIRED"],
        ["adminTokenPresent", adminTokenPresent() ? "true" : "false"]
      ]), { span: 7, tag: licflow3LiveStatus() }),
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
  function renderSupport() {
    const d = derived();
    const notes = d.notes || [];
    return [
      panel("Diagnóstico humano", "Lo necesario para entender el caso sin leer JSON.", list([
        ["Cliente", d.tenant?.displayName || d.tenant?.slug || FIRST_CUSTOMER_NAME],
        ["Estado", d.tenant?.status || "Revisar"],
        ["Licencia", d.license?.status || state.license?.runtime?.license?.status || "Revisar"],
        ["Problemas", collectProblems().length]
      ]), { span: 5, tag: "SOPORTE" }),
      panel("Acciones de soporte", "Crear nota y copiar paquete listo para seguimiento.", `<textarea id="supportNoteText" class="cc-textarea" spellcheck="true">Nota interna desde Prisma Cloud Ctr.</textarea>${actions([
        actionButton("create-note", "Agregar nota interna", "primary"),
        actionButton("copy-support", "Copiar paquete de soporte"),
        actionButton("show-problems", "Ver problemas"),
        surfaceButton("customers", "Ver cliente"),
        surfaceButton("system", "Ir a System")
      ])}`, { span: 7, tag: state.data?.admin?.enabled ? "LISTO" : "LECTURA" }),
      panel("Notas recientes", "Contexto rápido del caso.", list(notes, "Sin notas visibles todavía."), { span: 12, tag: `${notes.length} notas` }),
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
      panel("Herramientas técnicas", "Aquí sí vive el fierro: diagnostics, runtime y raw evidence.", actions([actionButton("export-diagnostics", "Exportar diagnóstico", "primary"),actionButton("refresh", "Actualizar sistema"),actionButton("copy-endpoint-matrix", "Copiar endpoint matrix"),actionButton("copy-local-desk", "Copiar escritorio local")]), { span: 4, tag: state.health?.overall || state.health?.status || "SYSTEM" }),
      panel("Runtime", "Mensajes locales recientes.", list(events.slice(-12).reverse().map((item) => [item.time || item.ts || "evento", item.message || item.kind || JSON.stringify(item).slice(0, 120)]), "Sin eventos runtime."), { span: 4, tag: `${events.length} eventos` }),
      panel("Auditoría local", "Eventos generados por altas, licencias, dispositivos, bajas y Otros.", localDesk("events", "Sin auditoría local."), { span: 12, tag: "AUDIT" }),
      panel("Endpoint matrix", "Detalle técnico permitido sólo en System.", list(endpointRows(LICFLOW3_ENDPOINT_MATRIX)), { span: 12, tag: "MATRIX" }),
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
    const [data, license, health, runtime, contract, commandCenter, bridge] = await Promise.all([
      safeApi("/api/cloud-saas/summary"),
      safeApi("/api/license-ops/latest"),
      safeApi("/api/health"),
      safeApi("/api/runtime"),
      safeApi("/api/contract"),
      safeApi("/api/command-center/bootstrap"),
      safeApi("/api/licflow4/bridge/status")
    ]);
    state.data = data;
    state.license = license;
    state.health = health;
    state.runtime = runtime;
    state.contract = contract;
    state.commandCenter = commandCenter;
    state.bridge = bridge;
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
          `LICFLOW4 ${bridgeAction}`,
          result.ok ? `${dryRun ? "Dry-run" : "Acción"} ${bridgeAction} procesada por backend.` : `${bridgeAction} bloqueado: ${result.code || "REVIEW"}`,
          result,
          { kind: result.ok ? "ok" : "warn" }
        );
        toast(result.ok ? `LICFLOW4 ${bridgeAction} OK` : `LICFLOW4 ${bridgeAction} bloqueado`);
        await loadAll();
      } else if (action === "show-problems") {
        const problems = collectProblems();
        setResult("Problemas", problems.length ? `${problems.length} punto(s) para revisar.` : "Sin bloqueadores visibles.", { ok: !problems.length, problems }, { kind: problems.length ? "warn" : "ok" });
        toast(problems.length ? "Hay puntos por revisar" : "Sin bloqueadores visibles");
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
        await copyText(`Seguridad Prisma Cloud Ctr\nModo: ${admin.enabled ? "acciones admin backend" : "lectura segura"}\nBridge LICFLOW4: ${bridge.ok ? "disponible" : "revisar"}\nadminTokenPresent: ${bridge.adminTokenPresent === true ? "true" : "false"}\nValor de token leido en frontend: false\nAcciones mutating: solo por /api/licflow4/bridge con confirmación explícita\nEstado: ${mainStatus()}`, "Resumen de seguridad");
      } else if (action === "copy-endpoint-matrix") {
        await copyText(endpointRows(LICFLOW3_ENDPOINT_MATRIX).map(([a, b]) => `${a}: ${b}`).join("\n"), "Endpoint matrix");
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
        const text = $("supportNoteText")?.value || "Nota interna desde Prisma Cloud Ctr.";
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
        setResult("Diagnóstico", "Diagnóstico exportado por Prisma Cloud Ctr.", result, { kind: result.ok === false ? "warn" : "ok", surface: "system" });
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
