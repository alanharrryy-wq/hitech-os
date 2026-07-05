
(function () {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[ch]));
  }

  function tone(value) {
    const raw = String(value || "").toLowerCase();
    if (["pass", "ready", "ok", "clean"].includes(raw)) return "ok";
    if (["generated", "mixed", "warn", "pin_ready", "manual_or_real"].some(x => raw.includes(x))) return "warn";
    if (["fail", "error", "blocked", "invalid", "expired"].some(x => raw.includes(x))) return "bad";
    return "";
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.error || payload.status || `${url} ${response.status}`);
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function setSurface(surface) {
    const next = surface === "lifecycle" ? "lifecycle" : surface;
    document.body.dataset.prismaInterface = next;
    $$('[data-prisma-interface-target]').forEach((button) => {
      const active = button.dataset.prismaInterfaceTarget === next;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    const node = $("#lifecycleSurface");
    if (node) node.hidden = next !== "lifecycle";
    if (next === "lifecycle") refreshAll();
  }

  function ensureSurface() {
    const main = $("#main") || document.querySelector("main");
    if (!main) return;

    let switcher = $(".surfaceSwitch");
    if (switcher && !$('[data-prisma-interface-target="lifecycle"]', switcher)) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.prismaInterfaceTarget = "lifecycle";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "Data Lifecycle";
      switcher.appendChild(button);
      button.addEventListener("click", () => setSurface("lifecycle"));
    }

    if ($("#lifecycleSurface")) return;
    const section = document.createElement("section");
    section.className = "lifecycleSurface";
    section.id = "lifecycleSurface";
    section.hidden = true;
    section.setAttribute("aria-label", "PRISMA Data Lifecycle");
    section.innerHTML = `
      <div class="lifecycle">
        <div class="lifecycleHero">
          <div class="lifecycleHeroGrid">
            <div>
              <p class="lifecycleKicker">Internal only · Clean Room · v5 Golden</p>
              <h2>PRISMA Data Lifecycle</h2>
              <p>Alimenta datos coherentes, limpia lo generado por ledger y prepara PRISMA cristalino. UI de dos botones; maquinaria interna por dominios, backup, PIN, evidencia, auditoría y rollback.</p>
            </div>
            <div class="lifecycleSeal">
              <div class="lifecycleSealCard"><small>Estado</small><strong id="lifecycleStatus">Cargando</strong></div>
              <div class="lifecycleSealCard"><small>PIN</small><strong id="lifecyclePinState">-</strong></div>
              <div class="lifecycleSealCard"><small>Clear candidates</small><strong id="lifecycleOpenRecords">-</strong></div>
              <div class="lifecycleSealCard"><small>Ledger open</small><strong id="lifecycleLedgerOpenRecords">-</strong></div>
              <div class="lifecycleSealCard"><small>External signature</small><strong id="lifecycleExternalOpenRecords">-</strong></div>
              <div class="lifecycleSealCard"><small>DBs</small><strong id="lifecycleDbCount">-</strong></div>
            </div>
          </div>
        </div>

        <div class="lifecycleActionGrid">
          <section class="lifecyclePanel lifecycleInjectPanel" aria-label="Inyectar datos">
            <div class="lifecyclePanelHead">
              <div>
                <h3>Inyectar datos</h3>
                <p>Un modo alimenta todos los dominios internos: ventas, caja, inventario, proveedores, compras, sync, tablets, usuarios, auditoría y Chart Lab.</p>
              </div>
              <span class="lifecycleTag">SEED CENTER</span>
            </div>
            <div class="lifecycleControlRow">
              <label for="lifecycleMode">Modo</label>
              <select id="lifecycleMode">
                <option value="light">Ligera</option>
                <option value="heavy">Pesada</option>
                <option value="longaniza">Pasada de longaniza</option>
              </select>
              <button id="lifecycleInjectButton" type="button">Inyectar</button>
            </div>
            <div class="lifecyclePlan" id="lifecyclePlan">Selecciona un modo para ver el plan.</div>
          </section>

          <section class="lifecyclePanel lifecycleClearPanel" aria-label="Clear datos">
            <div class="lifecyclePanelHead">
              <div>
                <h3>Clear</h3>
                <p>Limpia lo generado por Data Lifecycle usando ledger + firma externa. Hace backup antes de borrar y pide PIN de 6 dígitos si está activo.</p>
              </div>
              <span class="lifecycleTag warn">BACKUP + PIN</span>
            </div>
            <div class="lifecyclePreview" id="lifecycleClearPreview">Calculando preview...</div>
            <div class="lifecycleClearFlow">
              <button id="lifecycleRequestPinButton" type="button">Enviar PIN</button>
              <input id="lifecyclePinInput" inputmode="numeric" maxlength="6" placeholder="PIN 6 dígitos" autocomplete="one-time-code" />
              <button id="lifecycleClearButton" type="button">Clear</button>
            </div>
            <div class="lifecyclePinNote" id="lifecyclePinNote">El PIN se enviará al correo configurado. Si SMTP no está listo, quedará evidencia local interna.</div>
          </section>
        </div>

        <section class="lifecyclePanel" aria-label="Dashboard por dominio">
          <div class="lifecyclePanelHead">
            <div>
              <h3>Dashboard por dominio</h3>
              <p>Cifras actuales por dominio: total, candidatos Clear por ledger/firma externa, manual/real estimado y estado.</p>
            </div>
            <button id="lifecycleRefreshButton" type="button" class="lifecycleGhostButton">Actualizar</button>
          </div>
          <div class="lifecycleDomainGrid" id="lifecycleDomainGrid"></div>
        </section>

        <section class="lifecyclePanel" aria-label="Preflight y evidencia">
          <div class="lifecyclePanelHead">
            <div>
              <h3>Preflight / Evidencia</h3>
              <p>Resumen técnico interno sin saturar la operación.</p>
            </div>
            <span class="lifecycleTag" id="lifecycleRunStatus">IDLE</span>
          </div>
          <div class="lifecycleEvidenceActions">
            <button id="lifecycleAuditButton" type="button" class="lifecycleGhostButton">Auditar ledger</button>
            <button id="lifecycleBackupButton" type="button" class="lifecycleGhostButton">Backup ahora</button>
          </div>
          <p id="lifecycleLastAction">Esperando acción.</p>
          <pre class="lifecycleResult" id="lifecycleResult">PRISMA Data Lifecycle listo.</pre>
        </section>
      </div>`;
    const license = $("#licenseOpsSurface");
    if (license) license.insertAdjacentElement("afterend", section);
    else main.appendChild(section);
  }

  function renderPlan(payload) {
    const node = $("#lifecyclePlan");
    if (!node) return;
    const p = payload.plan || payload;
    const est = p.estimated_total_records ? `<span>${esc(p.estimated_total_records)} registros estimados</span>` : "";
    node.innerHTML = `
      <div class="lifecyclePlanGrid">
        <span><b>${esc(p.label || p.mode)}</b></span>
        <span>${esc(p.days)} días</span>
        <span>${esc(p.products)} productos</span>
        <span>${esc(p.tablets)} tablets</span>
        <span>${esc(p.users)} usuarios</span>
        <span>${esc(p.sales_target)} ventas aprox.</span>
        ${est}
      </div>`;
  }

  function renderLatest(payload) {
    const status = $("#lifecycleStatus");
    if (status) status.textContent = payload.status || (payload.ok ? "READY" : "ERROR");
    const pin = $("#lifecyclePinState");
    if (pin) pin.textContent = payload.pin_required ? "Activo" : "Desactivado";
    const open = $("#lifecycleOpenRecords");
    if (open) open.textContent = String(payload.generated_records_open ?? "-");
    const ledgerOpen = $("#lifecycleLedgerOpenRecords");
    if (ledgerOpen) ledgerOpen.textContent = String(payload.ledger_records_open ?? payload.generated_records_open ?? "-");
    const externalOpen = $("#lifecycleExternalOpenRecords");
    if (externalOpen) externalOpen.textContent = String(payload.external_seed_records_open ?? "0");
    const dbCount = $("#lifecycleDbCount");
    if (dbCount) dbCount.textContent = String((payload.databases || []).length);
    const grid = $("#lifecycleDomainGrid");
    if (grid) {
      grid.innerHTML = (payload.domains || []).map((d) => `
        <article class="lifecycleDomainCard ${tone(d.state)}">
          <div class="lifecycleDomainTop"><strong>${esc(d.domain)}</strong><span>${esc(d.state)}</span></div>
          <div class="lifecycleDomainStats">
            <div><small>Total</small><b>${esc(d.total)}</b></div>
            <div><small>Generado</small><b>${esc(d.generated)}</b></div>
            <div><small>Manual/real</small><b>${esc(d.manual_or_real)}</b></div>
          </div>
        </article>`).join("") || `<div class="lifecycleEmpty">Sin dominios detectados.</div>`;
    }
  }

  function renderPreview(payload) {
    const node = $("#lifecycleClearPreview");
    if (!node) return;
    if (!payload || payload.status !== "CLEAR_PREVIEW_READY") {
      node.textContent = "Preview no disponible.";
      return;
    }
    const parts = Object.entries(payload.by_domain || {}).map(([k, v]) => `${esc(k)}: ${esc(v)}`).join(" · ");
    node.innerHTML = `<strong>${esc(payload.records_to_clear || 0)}</strong> registros generados pendientes de limpiar${parts ? `<br><small>${parts}</small>` : ""}`;
  }

  function setRunning(label) {
    const status = $("#lifecycleRunStatus");
    const last = $("#lifecycleLastAction");
    const result = $("#lifecycleResult");
    if (status) { status.textContent = "RUNNING"; status.className = "lifecycleTag running"; }
    if (last) last.textContent = label;
    if (result) result.textContent = `${label}...`;
  }

  function setResult(payload) {
    const status = $("#lifecycleRunStatus");
    const result = $("#lifecycleResult");
    if (status) { status.textContent = payload.status || (payload.ok ? "OK" : "ERROR"); status.className = `lifecycleTag ${tone(payload.status || (payload.ok ? "ok" : "bad"))}`; }
    if (result) result.textContent = JSON.stringify(payload, null, 2);
  }

  async function refreshLatest() {
    try { const payload = await fetchJson("/api/lifecycle/latest"); renderLatest(payload); return payload; }
    catch (error) { setResult(error.payload || { ok: false, status: "ERROR", error: String(error.message || error) }); }
  }
  async function refreshPlan() {
    const mode = $("#lifecycleMode")?.value || "light";
    try { renderPlan(await fetchJson(`/api/lifecycle/plan/${encodeURIComponent(mode)}`)); }
    catch (error) { const n = $("#lifecyclePlan"); if (n) n.textContent = String(error.message || error); }
  }
  async function refreshPreview() {
    try { renderPreview(await fetchJson("/api/lifecycle/clear/preview")); }
    catch (error) { renderPreview(null); }
  }
  async function refreshPreflight() {
    try { setResult(await fetchJson("/api/lifecycle/preflight")); }
    catch (error) { setResult(error.payload || { ok: false, status: "ERROR", error: String(error.message || error) }); }
  }
  async function refreshAll() { await refreshPlan(); await refreshLatest(); await refreshPreview(); }

  async function inject() {
    const mode = $("#lifecycleMode")?.value || "light";
    setRunning(`Inyectando ${mode}`);
    $$("#lifecycleInjectButton,#lifecycleClearButton,#lifecycleRequestPinButton").forEach(b => b.disabled = true);
    try { const payload = await fetchJson(`/api/lifecycle/inject/${encodeURIComponent(mode)}`); setResult(payload); await refreshAll(); }
    catch (error) { setResult(error.payload || { ok: false, status: "ERROR", error: String(error.message || error) }); }
    finally { $$("#lifecycleInjectButton,#lifecycleClearButton,#lifecycleRequestPinButton").forEach(b => b.disabled = false); }
  }

  async function requestPin() {
    setRunning("Solicitando PIN");
    try {
      const payload = await fetchJson("/api/lifecycle/clear/request-pin");
      const note = $("#lifecyclePinNote");
      if (note) note.textContent = payload.email && payload.email.ok ? `PIN enviado a ${payload.owner_email}` : `PIN listo. ${payload.email?.message || payload.email?.status || "Revisa evidencia local."}`;
      setResult(payload);
    } catch (error) { setResult(error.payload || { ok: false, status: "ERROR", error: String(error.message || error) }); }
  }

  async function clearData() {
    const pin = $("#lifecyclePinInput")?.value || "";
    setRunning("Ejecutando Clear");
    $$("#lifecycleInjectButton,#lifecycleClearButton,#lifecycleRequestPinButton").forEach(b => b.disabled = true);
    try { const payload = await fetchJson(`/api/lifecycle/clear/confirm?pin=${encodeURIComponent(pin)}`); setResult(payload); await refreshAll(); }
    catch (error) { setResult(error.payload || { ok: false, status: "ERROR", error: String(error.message || error) }); }
    finally { $$("#lifecycleInjectButton,#lifecycleClearButton,#lifecycleRequestPinButton").forEach(b => b.disabled = false); }
  }

  function bind() {
    document.addEventListener("click", (event) => {
      const t = event.target;
      if (!(t instanceof HTMLElement)) return;
      if (t.matches('[data-prisma-interface-target="lifecycle"]')) setSurface("lifecycle");
      if (t.id === "lifecycleInjectButton") inject();
      if (t.id === "lifecycleRequestPinButton") requestPin();
      if (t.id === "lifecycleClearButton") clearData();
      if (t.id === "lifecycleRefreshButton") refreshAll().then(refreshPreflight);
      if (t.id === "lifecycleAuditButton") { setRunning('Auditando ledger'); fetchJson('/api/lifecycle/audit').then(setResult).catch(error => setResult(error.payload || {ok:false,status:'ERROR',error:String(error.message||error)})); }
      if (t.id === "lifecycleBackupButton") { setRunning('Creando backup'); fetchJson('/api/lifecycle/backup/create?reason=manual_ui').then(setResult).then(refreshAll).catch(error => setResult(error.payload || {ok:false,status:'ERROR',error:String(error.message||error)})); }
    });
    document.addEventListener("change", (event) => { if (event.target && event.target.id === "lifecycleMode") refreshPlan(); });
  }

  function init() { ensureSurface(); bind(); refreshPlan(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

// ============================================================================
// PRISMA Data Lifecycle V4 Excelsior UI enhancement layer.
// Adds an internal tools rail without changing the main two-action contract.
// ============================================================================
(function lifecycleV4Excelsior(){
  "use strict";
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));
  const esc = (v) => String(v ?? "").replace(/[&<>'"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));
  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) { const e = new Error(payload.error || payload.status || `${url} ${response.status}`); e.payload = payload; throw e; }
    return payload;
  }
  function setResult(payload) {
    const result = $("#lifecycleResult");
    const status = $("#lifecycleRunStatus");
    if (status) { status.textContent = payload.status || (payload.ok ? "OK" : "ERROR"); status.className = "lifecycleTag " + (payload.ok ? "ok" : "bad"); }
    if (result) result.textContent = JSON.stringify(payload, null, 2);
  }
  function running(label) {
    const result = $("#lifecycleResult");
    const last = $("#lifecycleLastAction");
    const status = $("#lifecycleRunStatus");
    if (status) { status.textContent = "RUNNING"; status.className = "lifecycleTag running"; }
    if (last) last.textContent = label;
    if (result) result.textContent = label + "...";
  }
  async function action(label, url) {
    running(label);
    try { setResult(await fetchJson(url)); }
    catch (error) { setResult(error.payload || { ok:false, status:"ERROR", error:String(error.message || error) }); }
  }
  function ensureV4Panel(retries=0) {
    const base = $("#lifecycleSurface .lifecycle");
    if (!base) { if (retries < 30) setTimeout(() => ensureV4Panel(retries + 1), 120); return; }
    if ($("#lifecycleV4Tools")) return;
    const panel = document.createElement("section");
    panel.className = "lifecyclePanel lifecycleV4Tools";
    panel.id = "lifecycleV4Tools";
    panel.setAttribute("aria-label", "Herramientas internas V5 Golden");
    panel.innerHTML = `
      <div class="lifecyclePanelHead">
        <div>
          <h3>Herramientas internas V5 Golden</h3>
          <p>La UI principal sigue siendo Inyectar + Clear. Esta botonera pequeña es para auditoría, evidencia, dry-runs, release checks y diagnóstico sin tocar producción a lo tarugo.</p>
        </div>
        <span class="lifecycleTag">V5 · Golden RC</span>
      </div>
      <div class="lifecycleV4ButtonGrid">
        <button type="button" data-lifecycle-v4="doctor">Doctor</button>
        <button type="button" data-lifecycle-v4="dryInject">Dry-run inyección</button>
        <button type="button" data-lifecycle-v4="dryClear">Dry-run Clear</button>
        <button type="button" data-lifecycle-v4="schema">Schema</button>
        <button type="button" data-lifecycle-v4="quality">Quality</button>
        <button type="button" data-lifecycle-v4="history">History</button>
        <button type="button" data-lifecycle-v4="bundle">Evidence bundle</button>
        <button type="button" data-lifecycle-v4="snapshot">Snapshot</button>
        <button type="button" data-lifecycle-v4="diff">Diff</button>
        <button type="button" data-lifecycle-v4="features">+50 mejoras</button>
        <button type="button" data-lifecycle-v4="routes">Routes</button>
        <button type="button" data-lifecycle-v4="pin">PIN status</button>
        <button type="button" data-lifecycle-v4="smtp">SMTP</button>
        <button type="button" data-lifecycle-v4="retention">Retention</button>
        <button type="button" data-lifecycle-v4="exportMd">Reporte MD</button>
        <button type="button" data-lifecycle-v4="exportCsv">Dashboard CSV</button>
      </div>`;
    base.appendChild(panel);
    refreshV4Chips();
  }
  async function refreshV4Chips() {
    try {
      const payload = await fetchJson('/api/lifecycle/manifest');
      const status = $("#lifecycleStatus");
      if (status && payload.feature_count) status.textContent = `V4 · ${payload.feature_count} mejoras`;
    } catch {}
  }
  document.addEventListener("click", (event) => {
    const t = event.target;
    if (!(t instanceof HTMLElement)) return;
    const key = t.dataset.lifecycleV4;
    if (!key) return;
    const mode = $("#lifecycleMode")?.value || "light";
    const pin = $("#lifecyclePinInput")?.value || "";
    const routes = {
      doctor: ["Doctor V4", "/api/lifecycle/doctor"],
      dryInject: ["Dry-run inyección", `/api/lifecycle/plan/dry-run/${encodeURIComponent(mode)}`],
      dryClear: ["Dry-run Clear", "/api/lifecycle/clear/dry-run"],
      schema: ["Schema inventory", "/api/lifecycle/schema"],
      quality: ["Data quality", "/api/lifecycle/quality"],
      history: ["History", "/api/lifecycle/history"],
      bundle: ["Evidence bundle", "/api/lifecycle/evidence/bundle"],
      snapshot: ["Snapshot dashboard", "/api/lifecycle/snapshot/create?label=ui_v4"],
      diff: ["Dashboard diff", "/api/lifecycle/snapshot/diff"],
      features: ["Catálogo de mejoras", "/api/lifecycle/features"],
      routes: ["Lifecycle routes", "/api/lifecycle/routes"],
      pin: ["PIN status", "/api/lifecycle/pin/status"],
      smtp: ["SMTP diagnostics", "/api/lifecycle/smtp/diagnostics"],
      retention: ["Retention preview", "/api/lifecycle/retention/preview"],
      exportMd: ["Export reporte MD", "/api/lifecycle/export/report.md"],
      exportCsv: ["Export dashboard CSV", "/api/lifecycle/export/dashboard.csv"],
      prune: ["Retention prune", `/api/lifecycle/retention/prune?pin=${encodeURIComponent(pin)}`],
    };
    const spec = routes[key];
    if (spec) action(spec[0], spec[1]);
  });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => ensureV4Panel());
  else ensureV4Panel();
})();


// ============================================================================
// PRISMA Data Lifecycle V5 Golden UI polish.
// Keeps the main UI simple and adds compact release-readiness buttons.
// ============================================================================
(function lifecycleV5Golden(){
  "use strict";
  const $ = (s, r=document) => r.querySelector(s);
  const esc = (v) => String(v ?? "").replace(/[&<>'"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));
  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store", headers: { Accept: "application/json" } });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || payload.status || `${url} ${response.status}`);
    return payload;
  }
  function render(target, title, payload) {
    if (!target) return;
    const ok = payload && payload.ok;
    target.innerHTML = `<div class="lifecycleResult ${ok ? "ok" : "warn"}"><strong>${esc(title)} · ${esc(payload.status || "READY")}</strong><pre>${esc(JSON.stringify(payload, null, 2)).slice(0, 9000)}</pre></div>`;
  }
  function ensureV5Panel(){
    const surface = $("#lifecycleSurface .lifecycle");
    if (!surface || $("#lifecycleV5Panel")) return;
    const panel = document.createElement("section");
    panel.id = "lifecycleV5Panel";
    panel.className = "lifecyclePanel lifecycleV5Panel";
    panel.setAttribute("aria-label", "Release readiness V5 Golden");
    panel.innerHTML = `
      <div class="lifecyclePanelHead">
        <div>
          <h3>Release readiness V5 Golden</h3>
          <p>Último filtro antes de instalar: no-downgrade, checklist, crosscheck y safety polish. No agrega botones peligrosos.</p>
        </div>
        <span class="lifecycleTag ok">Golden RC</span>
      </div>
      <div class="lifecycleV4ButtonGrid lifecycleV5ButtonGrid">
        <button type="button" data-lifecycle-v5="manifest">Manifest</button>
        <button type="button" data-lifecycle-v5="checklist">Checklist</button>
        <button type="button" data-lifecycle-v5="nodowngrade">No downgrade</button>
        <button type="button" data-lifecycle-v5="crosscheck">Crosscheck</button>
        <button type="button" data-lifecycle-v5="safety">Safety</button>
        <button type="button" data-lifecycle-v5="evidence">Evidence final</button>
      </div>
      <div id="lifecycleV5Output" class="lifecycleToolOutput" aria-live="polite"></div>
    `;
    surface.appendChild(panel);
    const output = $("#lifecycleV5Output", panel);
    const routes = {
      manifest: "/api/lifecycle/release/manifest",
      checklist: "/api/lifecycle/release/checklist",
      nodowngrade: "/api/lifecycle/release/no-downgrade",
      crosscheck: "/api/lifecycle/release/crosscheck",
      safety: "/api/lifecycle/release/safety",
      evidence: "/api/lifecycle/release/evidence"
    };
    panel.addEventListener("click", async (ev) => {
      const btn = ev.target.closest("[data-lifecycle-v5]");
      if (!btn) return;
      const key = btn.dataset.lifecycleV5;
      btn.disabled = true;
      try {
        render(output, btn.textContent, await fetchJson(routes[key]));
      } catch (err) {
        render(output, btn.textContent, { ok:false, status:"V5_UI_ERROR", error:String(err.message || err) });
      } finally {
        btn.disabled = false;
      }
    });
  }
  const boot = () => { ensureV5Panel(); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();


// ============================================================================
// PRISMA Data Lifecycle V5.3 Visibility Hotfix
// Purpose: make the tab visible even when Control Center surface scripts or
// topbar CSS were still tuned for exactly 3 tabs. This is UI-only hardening.
// ============================================================================
(function lifecycleV53VisibilityHotfix(){
  "use strict";
  const PATCH_ID = "PRISMA_DATA_LIFECYCLE_V5_3_VISIBILITY_HOTFIX";
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  function ensureButton(){
    const switcher = $(".surfaceSwitch");
    if (!switcher) return false;
    let button = $('[data-prisma-interface-target="lifecycle"]', switcher);
    if (!button) {
      button = document.createElement("button");
      button.type = "button";
      button.dataset.prismaInterfaceTarget = "lifecycle";
      button.setAttribute("aria-pressed", "false");
      button.textContent = "Data Lifecycle";
      switcher.appendChild(button);
    }
    button.classList.add("lifecycleSwitchButton");
    return true;
  }

  function ensureSurfaceVisibleState(){
    const main = $("#main") || $("main");
    const surface = $("#lifecycleSurface");
    if (!main || !surface) return false;
    document.body.dataset.prismaInterface = "lifecycle";
    $$('[data-prisma-interface-target]').forEach((button) => {
      const active = button.dataset.prismaInterfaceTarget === "lifecycle";
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    $$(':scope > section', main).forEach((section) => {
      if (section.id === "lifecycleSurface") {
        section.hidden = false;
        section.style.display = "block";
      } else {
        section.hidden = true;
        section.style.display = "none";
      }
    });
    surface.hidden = false;
    surface.style.display = "block";
    try {
      if (window.PRISMA_DATA_LIFECYCLE && typeof window.PRISMA_DATA_LIFECYCLE.refresh === "function") {
        window.PRISMA_DATA_LIFECYCLE.refresh();
      }
    } catch (_err) {}
    return true;
  }

  function ensureNonLifecycleCanReturn(target){
    if (!target || target === "lifecycle") return;
    const main = $("#main") || $("main");
    document.body.dataset.prismaInterface = target;
    $$('[data-prisma-interface-target]').forEach((button) => {
      const active = button.dataset.prismaInterfaceTarget === target;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    const lifecycle = $("#lifecycleSurface");
    if (lifecycle) { lifecycle.hidden = true; lifecycle.style.display = "none"; }
    if (main) {
      $$(':scope > section', main).forEach((section) => {
        if (section.id !== "lifecycleSurface") section.style.display = "";
      });
    }
  }

  function bindCapture(){
    if (window.__PRISMA_DATA_LIFECYCLE_V53_CAPTURE_BOUND__) return;
    window.__PRISMA_DATA_LIFECYCLE_V53_CAPTURE_BOUND__ = true;
    document.addEventListener("click", (event) => {
      const button = event.target && event.target.closest ? event.target.closest('[data-prisma-interface-target]') : null;
      if (!button) return;
      const target = button.dataset.prismaInterfaceTarget;
      if (target === "lifecycle") {
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === "function") event.stopImmediatePropagation();
        ensureSurfaceVisibleState();
      } else if (document.body.dataset.prismaInterface === "lifecycle") {
        ensureNonLifecycleCanReturn(target);
      }
    }, true);
  }

  function boot(){
    ensureButton();
    bindCapture();
  }

  window.PRISMA_DATA_LIFECYCLE_V53_VISIBILITY = {
    patch: PATCH_ID,
    ensureButton,
    show: ensureSurfaceVisibleState,
    boot
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
  window.addEventListener("load", boot);
  setTimeout(boot, 250);
  setTimeout(boot, 1000);
  try {
    new MutationObserver(boot).observe(document.documentElement, { childList: true, subtree: true });
  } catch (_err) {}
})();
