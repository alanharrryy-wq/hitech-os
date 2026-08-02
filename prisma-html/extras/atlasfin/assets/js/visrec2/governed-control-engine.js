(function governedControlEngine() {
  "use strict";

  const openButton = document.querySelector("[data-atlas-control-open]");
  const panel = document.querySelector("[data-atlas-control-panel]");
  if (!openButton || !panel) return;

  const closeButton = panel.querySelector("[data-atlas-control-close]");
  const content = panel.querySelector("[data-atlas-control-content]");
  const dataSource = "assets/data/visual-control.cobrar.pilot.js";
  let payload = null;
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

  function loadPayload() {
    if (payload) return Promise.resolve(payload);
    if (loading) return loading;
    loading = new Promise((resolve, reject) => {
      const existing = window.PRISMA_ATLASFIN_VISUAL_CONTROL;
      if (existing) {
        payload = existing;
        resolve(payload);
        return;
      }
      const script = document.createElement("script");
      script.src = dataSource;
      script.async = true;
      script.dataset.atlasControlData = "cobrar-pilot";
      script.addEventListener("load", () => {
        if (!window.PRISMA_ATLASFIN_VISUAL_CONTROL) {
          reject(new Error("El payload gobernado no declaró su contrato."));
          return;
        }
        payload = window.PRISMA_ATLASFIN_VISUAL_CONTROL;
        resolve(payload);
      }, { once: true });
      script.addEventListener("error", () => reject(new Error("No se pudo cargar el payload gobernado.")), { once: true });
      document.head.append(script);
    });
    return loading;
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
    content.innerHTML = `
      <div class="atlas-control-summary">
        <div><span>Planeación</span><strong class="atlas-control-status--pass">${escapeHtml(payload.status)}</strong></div>
        <div><span>Aplicación</span><strong class="atlas-control-status--blocked">${escapeHtml(payload.applicationReadiness)}</strong></div>
        <div><span>Plan UI Bridge</span><code>${escapeHtml(payload.plan.planId)}</code></div>
        <div><span>Mutación</span><strong>Desactivada</strong></div>
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
          <p class="atlas-control-note">La cobertura declarada es completa, pero su hash CSS está obsoleto. Eso bloquea certificación runtime y aplicación; no bloquea revisar el plan source-only.</p>
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
          <p class="atlas-eyebrow">Ciclo futuro y rollback</p>
          <h3>Aplicar sigue bloqueado</h3>
          <ol class="atlas-control-workflow">${payload.workflow.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>
          <p class="atlas-control-note">${escapeHtml(payload.rollback.currentPlan)}</p>
          <ol class="atlas-control-history">${payload.history.map((entry) => `<li><strong>${escapeHtml(entry.event)}</strong><small>${escapeHtml(entry.batchId || entry.planId || entry.reason)}</small></li>`).join("")}</ol>
          <ul class="atlas-control-files">${protectedFiles.map((file) => `<li><code>${escapeHtml(file)}</code></li>`).join("")}</ul>
          <button class="atlas-button atlas-button--primary" type="button" disabled aria-disabled="true">Aplicar receta · bloqueado por contrato</button>
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
