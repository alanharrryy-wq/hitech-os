(function () {
  "use strict";

  const ACTION_LABELS = {
    "detect-runtime": "Detectar runtime",
    "provision-tablet-solo": "Provisionar Tablet Solo",
    "provision-tablet-solo-dry-run": "Dry run provisioning",
    "import-local-license": "Importar licencia local",
    "validate-runtime-config": "Validar runtime",
    "validate-provisioning": "Validar provisioning",
    "tablet-solo-smoke": "Tablet Solo smoke",
    "no-direct-db-in-ui": "No direct DB/licencia UI",
    "customer-smoke": "Customer smoke",
    "export-evidence-zip": "Exportar evidencia ZIP",
    "open-programdata": "Abrir ProgramData",
    "start-tablet-runtime-config": "Levantar Tablet runtime"
  };

  const ACTION_ORDER = [
    "detect-runtime",
    "provision-tablet-solo-dry-run",
    "provision-tablet-solo",
    "import-local-license",
    "validate-runtime-config",
    "validate-provisioning",
    "tablet-solo-smoke",
    "no-direct-db-in-ui",
    "customer-smoke",
    "export-evidence-zip",
    "open-programdata",
    "start-tablet-runtime-config"
  ];

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;"
    }[ch]));
  }

  function tone(value) {
    const raw = String(value || "").toUpperCase();
    if (["PASS", "OK", "READY", "IMPORTED", "EXPORTED", "OPENED", "STARTED", "RUNTIME_READY"].includes(raw)) return "ok";
    if (raw.includes("PENDING") || raw.includes("WARN") || raw.includes("MISSING")) return "warn";
    if (raw.includes("FAIL") || raw.includes("ERROR") || raw.includes("FORBIDDEN") || raw.includes("INVALID")) return "bad";
    if (raw.includes("RUN")) return "running";
    return "";
  }

  function shortPath(value) {
    if (!value || value === "<redacted>") return value || "-";
    const raw = String(value);
    const slash = Math.max(raw.lastIndexOf("/"), raw.lastIndexOf("\\"));
    return slash >= 0 ? raw.slice(slash + 1) : raw;
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || payload.reason || `${url} ${response.status}`);
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function setSurface(surface) {
    const next = surface === "license" ? "license" : surface === "quality" ? "quality" : "operation";
    if (window.PRISMA_QUALITY_BAY && typeof window.PRISMA_QUALITY_BAY.setSurface === "function") {
      window.PRISMA_QUALITY_BAY.setSurface(next);
      return;
    }
    document.body.dataset.prismaInterface = next;
    $$("[data-prisma-interface-target]").forEach((button) => {
      const active = button.dataset.prismaInterfaceTarget === next;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function statusFromLatest(payload) {
    const runtime = payload && payload.runtime;
    const summary = runtime && runtime.runtime;
    const mode = summary && summary.runtimeMode;
    const identityLoaded = runtime && runtime.deviceIdentityFile && runtime.deviceIdentityFile.exists;
    const licenseLoaded = runtime && runtime.licenseFile && runtime.licenseFile.exists;
    const runtimeLoaded = runtime && runtime.runtimeConfig && runtime.runtimeConfig.exists;
    if ((mode === "customer" || mode === "release") && identityLoaded && !licenseLoaded) return "LICENSE_CUSTOMER_PENDING";
    if (runtimeLoaded && identityLoaded && licenseLoaded) return "RUNTIME_READY";
    if (runtimeLoaded && mode === "dev" && !licenseLoaded) return "DEV_LICENSE_MISSING";
    if (!runtimeLoaded) return "RUNTIME_PENDING";
    return "REVIEW";
  }

  function pathRow(label, item) {
    const status = item && item.exists ? "PASS" : "MISSING";
    return `<div class="licenseOpsPathRow"><small>${esc(label)} · ${esc(status)}</small><strong title="${esc(item && item.path)}">${esc(shortPath(item && item.path))}</strong></div>`;
  }

  function ensureSurface() {
    const main = $("#main") || document.querySelector("main");
    if (!main) return;

    let switcher = $(".surfaceSwitch");
    if (switcher && !$('[data-prisma-interface-target="license"]', switcher)) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.prismaInterfaceTarget = "license";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "Licencias";
      switcher.appendChild(button);
      button.addEventListener("click", () => setSurface("license"));
    }

    if ($("#licenseOpsSurface")) return;
    const section = document.createElement("section");
    section.className = "licenseOpsSurface";
    section.id = "licenseOpsSurface";
    section.hidden = true;
    section.setAttribute("aria-label", "PRISMA License Ops Console");
    section.innerHTML = `
      <div class="licenseOps">
        <div class="licenseOpsHero">
          <div class="licenseOpsHeroGrid">
            <div>
              <p class="licenseOpsKicker">Runtime local-first</p>
              <h2>Licencias y Runtime</h2>
              <p>Cabina local para preparar Tablet Solo, validar runtime config, importar licencia firmada y exportar evidencia sin volver Tablet dependiente de PC, cloud o internet.</p>
            </div>
            <div class="licenseOpsSeal">
              <div class="licenseOpsSealCard"><small>Estado</small><strong id="licenseOpsStatus">Cargando</strong></div>
              <div class="licenseOpsSealCard"><small>Runtime</small><strong id="licenseOpsMode">-</strong></div>
              <div class="licenseOpsSealCard"><small>Origen</small><strong id="licenseOpsSource">-</strong></div>
            </div>
          </div>
        </div>

        <div class="licenseOpsGrid">
          <section class="licenseOpsPanel" aria-label="Estado runtime">
            <div class="licenseOpsPanelHead">
              <div>
                <h3>Contexto resuelto</h3>
                <p>Lectura local de runtime, identidad, licencia y rutas canonical.</p>
              </div>
              <span class="licenseOpsTag" id="licenseOpsStatusTag">IDLE</span>
            </div>
            <div class="licenseOpsPaths" id="licenseOpsPaths"></div>
          </section>

          <section class="licenseOpsPanel" aria-label="Acciones licencia">
            <div class="licenseOpsPanelHead">
              <div>
                <h3>Acciones seguras</h3>
                <p>Botones locales que llaman shared/runtime, shared/licensing, provisioning y verifiers.</p>
              </div>
              <span class="licenseOpsTag">LOCAL ONLY</span>
            </div>
            <div class="licenseOpsInputRow">
              <input id="licenseOpsLicensePath" placeholder="Ruta absoluta de licencia firmada para importar" />
              <button id="licenseOpsImportButton" type="button">Importar</button>
            </div>
            <div class="licenseOpsActions" id="licenseOpsActions"></div>
          </section>
        </div>

        <div class="licenseOpsGrid">
          <section class="licenseOpsPanel" aria-label="Runtime and Data Explorer">
            <div class="licenseOpsPanelHead">
              <div>
                <h3>Runtime and Data Explorer</h3>
                <p>Busqueda read-only por cliente, negocio, terminal, device, licencia, folio, venta, outbox o entitlement.</p>
              </div>
              <span class="licenseOpsTag">READ ONLY</span>
            </div>
            <div class="licenseOpsInputRow">
              <input id="licenseOpsExplorerInput" placeholder="clientId, businessId, deviceId, folio, saleId o clientRequestId" />
              <button id="licenseOpsExplorerButton" type="button">Buscar</button>
            </div>
            <div class="licenseOpsExplorerList" id="licenseOpsExplorerList"></div>
          </section>

          <section class="licenseOpsPanel" aria-label="Resultado License Ops">
            <div class="licenseOpsPanelHead">
              <div>
                <h3>Resultado</h3>
                <p id="licenseOpsLastAction">Esperando accion.</p>
              </div>
              <span class="licenseOpsTag" id="licenseOpsRunStatus">IDLE</span>
            </div>
            <pre class="licenseOpsResult" id="licenseOpsResult">Selecciona una accion o busca un ID.</pre>
          </section>
        </div>
      </div>`;
    const quality = $("#qualityBaySurface");
    if (quality) quality.insertAdjacentElement("afterend", section);
    else main.prepend(section);
  }

  function renderActions(actions) {
    const root = $("#licenseOpsActions");
    if (!root) return;
    const byId = new Map((actions || []).map((action) => [action.id, action]));
    root.innerHTML = ACTION_ORDER.map((id) => {
      const action = byId.get(id) || { id, label: ACTION_LABELS[id], description: "Accion local." };
      const hiddenImport = id === "import-local-license" ? " data-import-action=\"true\"" : "";
      return `<button class="licenseOpsCard" type="button" data-license-ops-action="${esc(id)}"${hiddenImport}><strong>${esc(action.label || ACTION_LABELS[id] || id)}</strong><small>${esc(action.description || "")}</small></button>`;
    }).join("");
    $$("[data-license-ops-action]").forEach((button) => {
      button.addEventListener("click", () => runAction(button.dataset.licenseOpsAction, button));
    });
  }

  function renderLatest(payload) {
    const runtime = payload && payload.runtime;
    const summary = runtime && runtime.runtime ? runtime.runtime : {};
    const status = statusFromLatest(payload);
    const statusNode = $("#licenseOpsStatus");
    const statusTag = $("#licenseOpsStatusTag");
    if (statusNode) statusNode.textContent = status;
    if (statusTag) {
      statusTag.textContent = status;
      statusTag.className = `licenseOpsTag ${tone(status)}`;
    }
    const mode = summary.runtimeMode || "sin runtime";
    const source = runtime && runtime.provenance ? runtime.provenance.runtimeConfig : "-";
    const modeNode = $("#licenseOpsMode");
    const sourceNode = $("#licenseOpsSource");
    if (modeNode) modeNode.textContent = mode;
    if (sourceNode) sourceNode.textContent = source || "-";
    const paths = $("#licenseOpsPaths");
    if (paths) {
      paths.innerHTML = [
        pathRow("Runtime config", runtime && runtime.runtimeConfig),
        pathRow("Config root", runtime && runtime.configRoot),
        pathRow("Device identity", runtime && runtime.deviceIdentityFile),
        pathRow("License file", runtime && runtime.licenseFile),
        pathRow("Current release", runtime && runtime.currentRelease),
        `<div class="licenseOpsPathRow"><small>Identidad</small><strong>${esc(summary.businessId || "-")} / ${esc(summary.storeId || "-")} / ${esc(summary.terminalId || "-")} / ${esc(summary.deviceId || "-")}</strong></div>`
      ].join("");
    }
    renderActions(payload && payload.actions);
  }

  function renderExplorer(payload) {
    const list = $("#licenseOpsExplorerList");
    if (!list) return;
    const parts = [];
    const data = payload && payload.tabletData ? payload.tabletData : {};
    const matches = data.matches || [];
    const latest = data.latestTickets || [];
    const outbox = data.outbox || [];
    parts.push(`<div class="licenseOpsExplorerRow"><small>Consulta</small><strong>${esc(payload.query || "-")}</strong></div>`);
    parts.push(`<div class="licenseOpsExplorerRow"><small>Tickets encontrados</small><strong>${esc(matches.length)}</strong></div>`);
    matches.slice(0, 5).forEach((row) => parts.push(`<div class="licenseOpsExplorerRow"><small>ticket ${esc(row.folio || row.id)}</small><strong>${esc(row.id)} · ${esc(row.clientRequestId || "-")} · ${esc(row.status || "-")}</strong></div>`));
    parts.push(`<div class="licenseOpsExplorerRow"><small>Outbox encontrado</small><strong>${esc(outbox.length)}</strong></div>`);
    outbox.slice(0, 5).forEach((row) => parts.push(`<div class="licenseOpsExplorerRow"><small>${esc(row.topic || "event")}</small><strong>${esc(row.aggregateId || row.id)} · ${esc(row.status || "-")}</strong></div>`));
    if (!matches.length && latest.length) {
      parts.push(`<div class="licenseOpsExplorerRow"><small>Ultimos 5 tickets</small><strong>${esc(latest.map((row) => row.folio || row.id).join(" / "))}</strong></div>`);
    }
    (payload.sources || []).forEach((source) => {
      const found = source.matches || [];
      parts.push(`<div class="licenseOpsExplorerRow"><small>${esc(source.source)} matches</small><strong>${esc(found.length)}</strong></div>`);
    });
    list.innerHTML = parts.join("");
  }

  async function refreshLatest() {
    ensureSurface();
    try {
      const payload = await fetchJson("/api/license-ops/latest");
      renderLatest(payload);
      const result = $("#licenseOpsResult");
      if (result && result.textContent === "Selecciona una accion o busca un ID.") {
        result.textContent = JSON.stringify(payload, null, 2);
      }
    } catch (error) {
      const statusNode = $("#licenseOpsStatus");
      if (statusNode) statusNode.textContent = "API ERROR";
      const result = $("#licenseOpsResult");
      if (result) result.textContent = String(error.message || error);
    }
  }

  async function runAction(action, button) {
    if (!action) return;
    const all = $$("[data-license-ops-action]");
    all.forEach((node) => { node.disabled = true; });
    const status = $("#licenseOpsRunStatus");
    const last = $("#licenseOpsLastAction");
    const result = $("#licenseOpsResult");
    if (status) {
      status.textContent = "RUNNING";
      status.className = "licenseOpsTag running";
    }
    if (last) last.textContent = ACTION_LABELS[action] || action;
    if (result) result.textContent = `Ejecutando ${ACTION_LABELS[action] || action}...`;
    try {
      let url = `/api/license-ops/run/${encodeURIComponent(action)}`;
      if (action === "import-local-license") {
        const raw = $("#licenseOpsLicensePath") && $("#licenseOpsLicensePath").value;
        if (raw) url += `?licenseFile=${encodeURIComponent(raw)}`;
      }
      const payload = await fetchJson(url);
      const decision = payload.status || (payload.ok ? "OK" : "ERROR");
      if (status) {
        status.textContent = decision;
        status.className = `licenseOpsTag ${tone(decision)}`;
      }
      if (result) result.textContent = JSON.stringify(payload, null, 2);
      if (payload.latest) renderLatest(payload.latest);
      else await refreshLatest();
    } catch (error) {
      const payload = error.payload || { ok: false, status: "ERROR", error: String(error.message || error) };
      if (status) {
        status.textContent = payload.status || "ERROR";
        status.className = "licenseOpsTag bad";
      }
      if (result) result.textContent = JSON.stringify(payload, null, 2);
    } finally {
      all.forEach((node) => { node.disabled = false; });
      if (button) button.disabled = false;
    }
  }

  async function runExplorer() {
    const input = $("#licenseOpsExplorerInput");
    const query = input ? input.value.trim() : "";
    const result = $("#licenseOpsResult");
    if (result) result.textContent = query ? `Buscando ${query}...` : "Escribe un identificador para buscar.";
    if (!query) return;
    try {
      const payload = await fetchJson(`/api/license-ops/explorer?query=${encodeURIComponent(query)}`);
      renderExplorer(payload);
      if (result) result.textContent = JSON.stringify(payload, null, 2);
    } catch (error) {
      if (result) result.textContent = String(error.message || error);
    }
  }

  function wire() {
    ensureSurface();
    $$('[data-prisma-interface-target="license"]').forEach((button) => {
      button.addEventListener("click", () => setSurface("license"));
    });
    $("#licenseOpsImportButton")?.addEventListener("click", () => runAction("import-local-license"));
    $("#licenseOpsExplorerButton")?.addEventListener("click", runExplorer);
    $("#licenseOpsExplorerInput")?.addEventListener("keydown", (event) => {
      if (event.key === "Enter") runExplorer();
    });
    if (location.hash === "#license-ops" || location.hash === "#licencias") {
      setSurface("license");
    }
    refreshLatest();
    window.setInterval(() => {
      if (document.body.dataset.prismaInterface === "license") refreshLatest();
    }, 15000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();

  window.PRISMA_LICENSE_OPS = {
    refresh: refreshLatest,
    run: runAction,
    explorer: runExplorer,
    setSurface
  };
})();
