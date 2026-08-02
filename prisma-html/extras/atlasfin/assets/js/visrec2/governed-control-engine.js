(function governedControlEngine() {
  "use strict";

  const openButton = document.querySelector("[data-atlas-control-open]");
  const panel = document.querySelector("[data-atlas-control-panel]");
  if (!openButton || !panel) return;

  const closeButton = panel.querySelector("[data-atlas-control-close]");
  const content = panel.querySelector("[data-atlas-control-content]");
  const dataSource = "assets/data/visual-control.cobrar.pilot.js";
  const applicationSource = "assets/data/visual-application.cobrar.current.js";
  let payload = null;
  let applicationPayload = null;
  let loading = null;
  let page = 0;
  let query = "";

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const statusClass = (status) => {
    const value = String(status || "").toLowerCase();
    if (value.includes("pass") || value.includes("ready") || value.includes("resolved")) {
      return "atlas-control-status--pass";
    }
    if (value.includes("blocked") || value.includes("disabled") || value.includes("missing")) {
      return "atlas-control-status--blocked";
    }
    return "atlas-control-status--neutral";
  };

  function loadScript(source, dataKey) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = source;
      script.async = true;
      script.dataset.atlasControlData = dataKey;
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener("error", () => reject(new Error(`No se pudo cargar ${dataKey}.`)), { once: true });
      document.head.append(script);
    });
  }

  function loadPayload() {
    if (payload && applicationPayload) return Promise.resolve(payload);
    if (loading) return loading;
    loading = Promise.all([
      window.PRISMA_ATLASFIN_VISUAL_CONTROL ? Promise.resolve() : loadScript(dataSource, "cobrar-pilot"),
      window.PRISMA_ATLASFIN_VISUAL_APPLICATION ? Promise.resolve() : loadScript(applicationSource, "cobrar-application"),
    ]).then(() => {
      payload = window.PRISMA_ATLASFIN_VISUAL_CONTROL;
      applicationPayload = window.PRISMA_ATLASFIN_VISUAL_APPLICATION;
      if (!payload || !applicationPayload) throw new Error("Los payloads gobernados no declararon sus contratos.");
      return payload;
    });
    return loading;
  }

  function requestTemplate() {
    return {
      schema: "PRISMA_ATLASFIN_VISUAL_APPLICATION_REQUEST_V1",
      schemaVersion: "1.0.0",
      taskId: applicationPayload.taskId,
      controlId: applicationPayload.controlId,
      transactionId: applicationPayload.transactionId,
      componentUiId: payload.pilot.componentUiId,
      recipeId: payload.recipe.recipeId,
      visualStackId: payload.recipe.visualStackId,
      bindingId: payload.pilot.bindingId,
      adapterId: payload.plan.adapterId,
      layerId: payload.pilot.layerId,
      implementationLayerId: payload.pilot.implementationLayerId,
      planId: "BRPLAN.ca4eebf8f3a79d3ec6944488",
      planChecksum: "cce8fd8567744602264cf386902ad2e8e1f78042919a4b9365d158c351f83153",
      authorization: "EXPLICIT_USER_AUTHORIZATION_ATLASFIN_COBRAR_V1",
      maxProductFileCount: 1,
      productFiles: applicationPayload.productFiles,
      selectors: applicationPayload.selectors,
      before: applicationPayload.after,
      beforeEvidence: {
        phase: "BEFORE",
        status: "PASS",
        selector: ".cobrarReferenceButton",
        path: "SELECT_LOCAL_BEFORE_EVIDENCE_FILE_IN_RUNNER",
        sha256: applicationPayload.preview.evidenceBundle.beforeEvidenceSha256,
      },
      note: "Atlasfin exports this portable request. The runner must bind the local BEFORE evidence path and revalidate every hash before writing.",
    };
  }

  function downloadJson(filename, value) {
    const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function hierarchyMarkup(pilot) {
    const rows = [
      ["Surface", pilot.surfaceId],
      ["Route", `${pilot.routeId} · ${pilot.routePath}`],
      ["Owner", pilot.ownerId],
      ["Region", pilot.regionId],
      ["Slot", pilot.slotId],
      ["Component", pilot.componentUiId],
      ["Selector", pilot.selector],
      ["Layer", pilot.layerId],
      ["Implementation", pilot.implementationLayerId],
      ["Binding", pilot.bindingId],
    ];
    return rows.map(([label, value]) => `
      <li><span>${escapeHtml(label)}</span><code>${escapeHtml(value)}</code></li>
    `).join("");
  }

  function gatesMarkup(gates) {
    return gates.map((gate) => `
      <li>
        <code>${escapeHtml(gate.gateId)}</code>
        <strong class="${statusClass(gate.status)}">${escapeHtml(gate.status)}</strong>
      </li>
    `).join("");
  }

  function operationsMarkup(operations, pageSize) {
    const filtered = query
      ? operations.filter((operation) => String(operation.searchText || "").includes(query))
      : operations;
    const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, pageCount - 1);
    const start = page * pageSize;
    const visible = filtered.slice(start, start + pageSize);
    const cards = visible.length
      ? visible.map((operation) => {
        const properties = operation.propertyChanges.map((change) => change.property).join(", ");
        return `
          <article class="atlas-control-operation">
            <header>
              <div><span>${escapeHtml(operation.kind)}</span><h4>${escapeHtml(operation.unitId)}</h4></div>
              <strong>${escapeHtml(operation.propertyCount)} propiedades</strong>
            </header>
            <code>${escapeHtml(operation.selector)}</code>
            <p>${escapeHtml(properties)}</p>
            <small class="${statusClass(operation.targetResolutionStatus)}">${escapeHtml(operation.targetResolutionStatus)}</small>
          </article>
        `;
      }).join("")
      : '<p class="atlas-control-empty">Sin operaciones para este filtro.</p>';
    return {
      markup: cards,
      count: filtered.length,
      pageCount,
      label: `${page + 1} / ${pageCount}`,
    };
  }

  function render() {
    const pageSize = payload.rendering.operationPageSize;
    const operations = operationsMarkup(payload.plan.operations, pageSize);
    const source = payload.evidence.source;
    const mamastrophic = payload.evidence.mamastrophic;
    const protectedFiles = payload.rollback.protectedFiles;
    const application = applicationPayload;
    const evidence = application.preview.evidenceBundle;
    content.innerHTML = `
      <div class="atlas-control-summary">
        <div><span>Planeación</span><strong class="atlas-control-status--pass">${escapeHtml(payload.status)}</strong></div>
        <div><span>Aplicación actual</span><strong class="atlas-control-status--pass">${escapeHtml(application.status)}</strong></div>
        <div><span>Plan UI Bridge</span><code>${escapeHtml(payload.plan.planId)}</code></div>
        <div><span>Post-plan</span><strong class="atlas-control-status--pass">${escapeHtml(application.preview.postApplicationPlan.status)}</strong></div>
      </div>

      <div class="atlas-control-layout">
        <section class="atlas-control-card">
          <p class="atlas-eyebrow">Jerarquía canónica</p>
          <h3>Tablet POS → Cobrar</h3>
          <ol class="atlas-control-hierarchy">${hierarchyMarkup(payload.pilot)}</ol>
        </section>

        <section class="atlas-control-card">
          <p class="atlas-eyebrow">Receta compatible</p>
          <label class="atlas-control-field">
            <span>Receta certificada</span>
            <select data-atlas-control-recipe disabled>
              <option>${escapeHtml(payload.recipe.recipeId)}</option>
            </select>
          </label>
          <div class="atlas-control-coverage">
            <div><strong>${escapeHtml(payload.recipe.plannedPropertyCount)}</strong><span>propiedades planeadas</span></div>
            <div><strong>${escapeHtml(payload.recipe.missingPropertyCount)}</strong><span>propiedades conocidas sin cubrir</span></div>
            <div><strong>${escapeHtml(payload.recipe.unitCount)}</strong><span>unidades paginadas</span></div>
          </div>
          <p class="atlas-control-note">La cobertura está fresca y el resultado actual está certificado por UIMAP, UI Bridge y evidencia Mamastrophic BEFORE/AFTER. El piloto V1 conserva intactos sus guards source-only históricos.</p>
        </section>
      </div>

      <section class="atlas-control-card atlas-control-plan">
        <header class="atlas-control-plan__header">
          <div><p class="atlas-eyebrow">Plan determinístico</p><h3>${escapeHtml(payload.plan.operationCount)} operaciones · cero escritura</h3></div>
          <label class="atlas-control-search"><span>Filtrar operación</span><input type="search" value="${escapeHtml(query)}" placeholder="hover, border, disabled…" data-atlas-control-search></label>
        </header>
        <div class="atlas-control-operations">${operations.markup}</div>
        <footer class="atlas-control-pagination">
          <span>${escapeHtml(operations.count)} resultados · página ${escapeHtml(operations.label)}</span>
          <div>
            <button class="atlas-button" type="button" data-atlas-control-prev ${page === 0 ? "disabled" : ""}>Anterior</button>
            <button class="atlas-button" type="button" data-atlas-control-next ${page + 1 >= operations.pageCount ? "disabled" : ""}>Siguiente</button>
          </div>
        </footer>
      </section>

      <div class="atlas-control-layout">
        <section class="atlas-control-card">
          <p class="atlas-eyebrow">Evidencia y gates</p>
          <h3>Estado honesto</h3>
          <ul class="atlas-control-gates">${gatesMarkup(payload.gates)}</ul>
          <dl class="atlas-control-evidence">
            <div><dt>CSS actual</dt><dd><code>${escapeHtml(source.styleSha256)}</code></dd></div>
            <div><dt>CSS en cobertura</dt><dd><code>${escapeHtml(source.declaredCoverageStyleSha256)}</code></dd></div>
            <div><dt>Mamastrophic</dt><dd class="${statusClass(mamastrophic.status)}">${escapeHtml(mamastrophic.status)}</dd></div>
          </dl>
        </section>

        <section class="atlas-control-card">
          <p class="atlas-eyebrow">Transacción exacta y rollback</p>
          <h3>Cobrar aplicado y verificable</h3>
          <p class="atlas-control-note">El navegador sólo prepara/exporta solicitudes y lee evidencia. La escritura pertenece al runner exacto de UI Bridge.</p>
          <div class="atlas-control-actions" role="group" aria-label="Evidencia de aplicación">
            <button class="atlas-button atlas-button--primary" type="button" data-atlas-application-action="request">Preparar solicitud</button>
            <button class="atlas-button" type="button" data-atlas-application-action="before">Ver BEFORE</button>
            <button class="atlas-button" type="button" data-atlas-application-action="patch">Ver patch</button>
            <button class="atlas-button" type="button" data-atlas-application-action="gates">Ver gates</button>
            <button class="atlas-button" type="button" data-atlas-application-action="rollback">Ver rollback</button>
            <button class="atlas-button" type="button" data-atlas-application-action="result">Ver resultado</button>
            <button class="atlas-button" type="button" data-atlas-application-action="after">Ver AFTER</button>
          </div>
          <pre class="atlas-control-inspector" data-atlas-application-inspector tabindex="0">${escapeHtml(JSON.stringify({ status: application.status, batchId: application.preview.uimap.batchId, evidenceSha256: evidence.sha256 }, null, 2))}</pre>
          <ul class="atlas-control-files">${protectedFiles.map((file) => `<li><code>${escapeHtml(file)}</code></li>`).join("")}</ul>
        </section>
      </div>
    `;

    const search = content.querySelector("[data-atlas-control-search]");
    search.addEventListener("input", (event) => {
      query = event.currentTarget.value.trim().toLowerCase();
      page = 0;
      render();
      content.querySelector("[data-atlas-control-search]").focus();
    });
    content.querySelector("[data-atlas-control-prev]").addEventListener("click", () => {
      page = Math.max(0, page - 1);
      render();
    });
    content.querySelector("[data-atlas-control-next]").addEventListener("click", () => {
      page += 1;
      render();
    });
    const inspector = content.querySelector("[data-atlas-application-inspector]");
    content.querySelectorAll("[data-atlas-application-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.atlasApplicationAction;
        if (action === "request") {
          downloadJson("atlasfin-cobrar-application-request.json", requestTemplate());
          inspector.textContent = "Solicitud portable exportada. No se escribió ningún archivo de producto.";
          return;
        }
        const views = {
          before: { source: application.before, evidenceSha256: evidence.beforeEvidenceSha256, screenshotSha256: evidence.beforeScreenshotSha256 },
          patch: { changedLineCount: application.preview.changedLineCount, patchSha256: application.preview.patchSha256, portableArtifact: application.preview.portableArtifact, postApplicationPlan: application.preview.postApplicationPlan },
          gates: { runtimeStatus: application.status, comparison: evidence.comparison, states: evidence.states, console: evidence.console, network: evidence.network },
          rollback: application.rollback,
          result: application,
          after: { source: application.after, evidenceSha256: evidence.afterEvidenceSha256, screenshotSha256: evidence.afterScreenshotSha256 },
        };
        inspector.textContent = JSON.stringify(views[action], null, 2);
        inspector.focus();
      });
    });
  }

  async function openControl() {
    panel.hidden = false;
    openButton.setAttribute("aria-expanded", "true");
    content.innerHTML = '<p class="atlas-control-loading" role="status">Cargando autoridad UIMAP, RIFAT y el plan UI Bridge…</p>';
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
    try {
      await loadPayload();
      render();
    } catch (error) {
      content.innerHTML = `<p class="atlas-control-error" role="alert">FAIL explícito: ${escapeHtml(error.message)}</p>`;
    }
  }

  function closeControl() {
    panel.hidden = true;
    openButton.setAttribute("aria-expanded", "false");
    openButton.focus();
  }

  openButton.addEventListener("click", openControl);
  closeButton?.addEventListener("click", closeControl);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) closeControl();
  });
}());
