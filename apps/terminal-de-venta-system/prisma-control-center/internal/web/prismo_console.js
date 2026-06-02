(function () {
  "use strict";

  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const FILE_PREVIEW_LIMIT = 180000;
  const SUGGESTIONS = [
    "¿Qué evidencia reciente explica el estado de PRISMO?",
    "¿Qué protocolo debería rankear primero y por qué?",
    "¿Dónde está el mayor riesgo operativo ahora?",
    "¿Qué memoria procedural ayuda a reparar esta señal?",
    "¿Qué bloque visual debe renderizar PRISMO automáticamente?",
    "¿Qué acción preparada conviene revisar?"
  ];
  const MODES = ["ASK", "INSPECT", "IMPROVE", "EVIDENCE"];
  const GUIDANCE = {
    intent: {
      diagnose: "Diagnose",
      explain: "Explain",
      recommend: "Recommend",
      compare: "Compare",
      audit: "Audit",
      prepare_action: "Prepare action",
      summarize: "Summarize",
      investigate: "Investigate"
    },
    area: {
      learning: "Learning",
      sync: "Sync",
      pc_ui: "PC UI",
      tablet: "Tablet",
      pos: "POS",
      chart_lab: "Chart Lab",
      governance: "Governance",
      evidence_vault: "Evidence Vault",
      protocols: "Protocols",
      visual_theater: "Visual/Theater"
    },
    lens: {
      recent_evidence: "Recent evidence",
      detected_patterns: "Detected patterns",
      suggested_protocols: "Suggested protocols",
      procedural_memory: "Procedural memory",
      runtime_state: "Runtime state",
      governance_canon: "Governance canon",
      visual_memory: "Visual memory",
      operational_memory: "Operational memory"
    }
  };
  const STATE = {
    mode: "ASK",
    guidance: { intent: "", area: "", lens: "" },
    chips: { intent: "", area: "", lens: "" },
    busy: false,
    status: "booting",
    evidenceFiles: [],
    lastResponse: null,
    bridge: null,
    feedbackState: "pending"
  };

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = (value) => window.PRISMO_RENDERERS ? window.PRISMO_RENDERERS.esc(value) : String(value ?? "");

  function toast(message) {
    if (typeof window.toast === "function") window.toast(message);
    else console.info("[PRISMO]", message);
  }

  function setState(next) {
    STATE.status = next;
    document.body.dataset.prismoState = next;
    const chip = $("#prismoUiState");
    if (chip) {
      const labels = {
        booting: "Inicializando",
        idle: "Inteligencia activa",
        no_api_key: "Adaptador local",
        demo_mode: "Adaptador local",
        offline: "Origen no disponible",
        submitting: "Enviando",
        thinking: "Interpretando",
        rendering: "Renderizando",
        success: "Respuesta lista",
        partial: "Respuesta parcial",
        blocked: "Bloqueado",
        error: "Error"
      };
      chip.textContent = labels[next] || next.replaceAll("_", " ");
      chip.dataset.state = next === "blocked" || next === "error" ? "bad" : next === "demo_mode" || next === "no_api_key" ? "warn" : "ok";
    }
  }

  function setSurface(name) {
    const next = name === "prismo" ? "prismo" : name;
    document.body.dataset.prismaInterface = next;
    try { localStorage.setItem(STORE_INTERFACE, next); } catch (_err) {}
    $$("[data-prisma-interface-target]").forEach((button) => {
      const active = button.dataset.prismaInterfaceTarget === next;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    const surface = $("#prismoConsoleSurface");
    if (surface) surface.hidden = next !== "prismo";
    if (next === "prismo") {
      const title = $(".titles h1");
      const subtitle = $("#subtitle");
      const chips = $$(".chips .chip");
      if (title) title.textContent = "PRISMO";
      if (subtitle) subtitle.textContent = "Operational AI Core · solo lectura · evidencia y decisión.";
      if (chips[0]) chips[0].innerHTML = '<span class="dot"></span>IA operacional';
      if (chips[1]) chips[1].textContent = "Gemini server-side";
      if (chips[2]) chips[2].textContent = "Gobernanza activa";
      window.scrollTo({ top: 0, behavior: "smooth" });
      refreshStatus();
    }
  }

  function bindSurfaceCapture() {
    if (window.__PRISMO_SURFACE_CAPTURE_BOUND__) return;
    window.__PRISMO_SURFACE_CAPTURE_BOUND__ = true;
    document.addEventListener("click", (event) => {
      const button = event.target && event.target.closest ? event.target.closest('[data-prisma-interface-target="prismo"]') : null;
      if (!button) return;
      event.preventDefault();
      event.stopPropagation();
      if (typeof event.stopImmediatePropagation === "function") event.stopImmediatePropagation();
      setSurface("prismo");
    }, true);
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json", ...(options && options.headers ? options.headers : {}) },
      ...options
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(payload.direct_answer || payload.error || payload.status || `${url} ${response.status}`);
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function renderStatus(payload) {
    STATE.bridge = payload || {};
    const bridge = $("#prismoBridgeStatus");
    const authority = $("#prismoAuthorityStatus");
    const safety = $("#prismoSafetyStatus");
    const html = $("#prismoHtmlStatus");
    if (bridge) {
      bridge.textContent = payload.demo_mode ? "Gemini server-side" : payload.ai_enabled ? "Gemini server-side" : "Gemini protegido";
      bridge.dataset.state = payload.demo_mode ? "demo" : payload.ai_enabled ? "online" : "blocked";
    }
    if (authority) {
      authority.textContent = "Authority Brain";
      authority.dataset.state = payload.authority && payload.authority.currentStateLoaded ? "online" : "demo";
    }
    if (safety) {
      safety.textContent = payload.mutation_allowed ? "Revisión requerida" : "Gobernanza activa";
      safety.dataset.state = payload.mutation_allowed ? "blocked" : "online";
    }
    if (html) {
      html.textContent = payload.html_preview_allowed ? "Vista gobernada" : "Acciones preparadas";
      html.dataset.state = payload.html_preview_allowed ? "demo" : "online";
    }
    if (payload.demo_mode) setState(payload.gemini_configured ? "demo_mode" : "no_api_key");
    else setState("idle");
  }

  async function refreshStatus() {
    try {
      renderStatus(await fetchJson("/api/prismo/status"));
    } catch (_error) {
      setState("offline");
      renderStatus({ demo_mode: true, ai_enabled: false, gemini_configured: false, html_preview_allowed: false, mutation_allowed: false, authority: {} });
    }
  }

  function wireModes() {
    $$(".prismo-mode-chip").forEach((button) => {
      button.addEventListener("click", () => {
        STATE.mode = button.dataset.prismoMode || "ASK";
        $$(".prismo-mode-chip").forEach((item) => item.setAttribute("aria-pressed", item === button ? "true" : "false"));
      });
    });
  }

  function normalizeGuidanceOption(option) {
    if (!option) return { value: "", label: "" };
    if (typeof option === "string") return { value: option, label: option };
    if (typeof option === "object") return { value: String(option.value || option.id || option.label || ""), label: String(option.label || option.value || option.id || "") };
    return { value: String(option), label: String(option) };
  }

  function guidanceLabel(key, value) {
    const normalized = normalizeGuidanceOption(value);
    return (GUIDANCE[key] && GUIDANCE[key][normalized.value]) || normalized.label || "PRISMO inferred";
  }

  function inferChipValues() {
    const query = ($("#prismoPrompt")?.value || "").toLowerCase();
    const pick = (key, fallback) => STATE.guidance[key] || STATE.chips[key] || fallback;
    const intent =
      query.includes("compar") ? "compare" :
      query.includes("audit") || query.includes("verifica") ? "audit" :
      query.includes("recom") || query.includes("siguiente") ? "recommend" :
      query.includes("resume") || query.includes("brief") ? "summarize" :
      query.includes("explica") || query.includes("why") ? "explain" :
      "diagnose";
    const area =
      query.includes("sync") ? "sync" :
      query.includes("tablet") ? "tablet" :
      query.includes("pc") ? "pc_ui" :
      query.includes("chart") ? "chart_lab" :
      query.includes("govern") ? "governance" :
      query.includes("visual") || query.includes("theater") || query.includes("glass") ? "visual_theater" :
      "learning";
    const lens =
      query.includes("runtime") || query.includes("estado") ? "runtime_state" :
      query.includes("pattern") || query.includes("patron") ? "detected_patterns" :
      query.includes("evidencia") || query.includes("evidence") ? "recent_evidence" :
      query.includes("visual") || query.includes("glass") ? "visual_memory" :
      query.includes("govern") ? "governance_canon" :
      "procedural_memory";
    STATE.chips.intent = pick("intent", intent);
    STATE.chips.area = pick("area", area);
    STATE.chips.lens = pick("lens", lens);
  }

  function renderInterpretationChips(chips) {
    const root = $("#prismoInterpretationChips");
    if (!root) return;
    const fromResponse = Array.isArray(chips) && chips.length ? chips : null;
    if (!fromResponse) inferChipValues();
    const rows = fromResponse || ["intent", "area", "lens"].map((key) => ({
      key,
      value: STATE.chips[key],
      label: guidanceLabel(key, STATE.chips[key]),
      source: STATE.guidance[key] ? "user" : "inferred",
      editable: true
    }));
    root.innerHTML = rows.map((chip) => `
      <button type="button" class="prismo-inferred-chip" data-chip-key="${esc(chip.key)}" data-source="${esc(chip.source || "inferred")}">
        <small>${esc(chip.key)}</small>
        <span contenteditable="true" spellcheck="false">${esc(chip.label || chip.value || "")}</span>
      </button>`).join("");
    $$(".prismo-inferred-chip", root).forEach((button) => {
      const span = $("span", button);
      const key = button.dataset.chipKey;
      if (!span || !key) return;
      span.addEventListener("input", () => {
        STATE.chips[key] = span.textContent.trim();
        button.dataset.source = "mixed";
      });
    });
  }

  function wireGuidance() {
    $$("[data-prismo-guidance]").forEach((select) => {
      select.addEventListener("change", () => {
        const key = select.dataset.prismoGuidance;
        if (!key) return;
        STATE.guidance[key] = select.value || "";
        STATE.chips[key] = select.value || "";
        renderInterpretationChips();
      });
    });
    $("#prismoPrompt")?.addEventListener("input", () => renderInterpretationChips());
    renderInterpretationChips();
  }

  function renderSuggestions() {
    const root = $("#prismoSuggestionRow");
    if (!root) return;
    root.innerHTML = "";
    SUGGESTIONS.forEach((label) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "prismo-suggestion-chip";
      button.textContent = label;
      button.addEventListener("click", () => {
        const input = $("#prismoPrompt");
        if (input) input.value = label;
        selectMode(label.includes("evidencia") || label.includes("evidence") ? "EVIDENCE" : label.includes("acción") ? "IMPROVE" : "ASK");
        renderInterpretationChips();
      });
      root.appendChild(button);
    });
  }

  function selectMode(mode) {
    if (!MODES.includes(mode)) return;
    STATE.mode = mode;
    $$(".prismo-mode-chip").forEach((button) => button.setAttribute("aria-pressed", button.dataset.prismoMode === mode ? "true" : "false"));
  }

  async function readEvidenceFiles(input) {
    STATE.evidenceFiles = [];
    const files = Array.from(input.files || []).slice(0, 8);
    for (const file of files) {
      const item = {
        name: file.name,
        mime: file.type || "application/octet-stream",
        size: file.size,
        textPreview: ""
      };
      if (/\.zip$/i.test(file.name)) {
        item.textPreview = "ZIP uploaded as metadata only. Use an evidence input pack or backend ingestion.";
      } else if (/\.(txt|md|json|jsonc|log|csv|html|xml|ya?ml)$/i.test(file.name) || file.type.startsWith("text/")) {
        item.textPreview = await file.slice(0, FILE_PREVIEW_LIMIT).text();
      } else {
        item.textPreview = "Unsupported binary preview. File registered as temporal evidence metadata only.";
      }
      STATE.evidenceFiles.push(item);
    }
    const note = $("#prismoFileNote");
    if (note) note.textContent = STATE.evidenceFiles.length ? `${STATE.evidenceFiles.length} archivo(s) listos como evidencia temporal.` : "Sin archivos adjuntos.";
  }

  function collectPayload() {
    const prompt = $("#prismoPrompt");
    const evidence = $("#prismoEvidenceText");
    const context = $("#prismoContextText");
    inferChipValues();
    return {
      mode: STATE.mode,
      intent: STATE.guidance.intent || null,
      area: STATE.guidance.area || null,
      lens: STATE.guidance.lens || null,
      chips: { ...STATE.chips },
      selection_source: {
        intent: STATE.guidance.intent ? "user" : "inferred",
        area: STATE.guidance.area ? "user" : "inferred",
        lens: STATE.guidance.lens ? "user" : "inferred"
      },
      message: prompt ? prompt.value.trim() : "",
      query: prompt ? prompt.value.trim() : "",
      context: context ? context.value.trim() : "",
      attachments: STATE.evidenceFiles,
      evidenceText: evidence ? evidence.value.trim() : "",
      client_context: {
        surface: "control_center",
        route: "/prismo",
        adapter: "/api/prismo/theater/query",
        composer: "free_text_first_three_guidance"
      }
    };
  }

  function renderLoading() {
    const stream = $("#prismoResponseStream");
    if (!stream) return;
    stream.innerHTML = `
      <div class="prismo-response-card">
        <div class="prismo-response-meta">
          <span class="prismo-tag" data-state="warn">Reading memory</span>
          <span class="prismo-tag">Checking evidence</span>
          <span class="prismo-tag">Building render plan</span>
        </div>
        <p class="prismo-answer">PRISMO está interpretando la pregunta, rankeando protocolos y preparando Auto Render Ensemble.</p>
      </div>`;
  }

  function renderResponse(payload) {
    STATE.lastResponse = payload;
    setState(payload.status === "blocked" ? "blocked" : payload.status === "error" ? "error" : payload.status === "partial" ? "partial" : "success");
    const stream = $("#prismoResponseStream");
    if (stream) {
      const certainty = payload.certainty_level || "NO_CONFIRMADO";
      const risk = payload.risk || {};
      stream.innerHTML = `
        <div class="prismo-response-card">
          <div class="prismo-response-meta">
            <span class="prismo-tag" data-state="${payload.status === "blocked" ? "bad" : "ok"}">${esc(payload.status || "success")}</span>
            <span class="prismo-tag">${esc((payload.interpretation && payload.interpretation.intent) || payload.mode || STATE.mode)}</span>
            <span class="prismo-tag" data-state="${payload.demo_mode ? "warn" : "ok"}">${payload.demo_mode ? "deterministic adapter" : "live bridge"}</span>
            <span class="prismo-tag">${esc(certainty)}</span>
          </div>
          <p class="prismo-answer">${esc(payload.direct_answer || "")}</p>
          <div class="prismo-risk-summary"><strong>Riesgo</strong><br>${esc(risk.summary || risk.level || "sin riesgo reportado")}</div>
          <div class="prismo-safe-step"><strong>Siguiente paso seguro</strong><br>${esc(payload.safe_next_step || "Reunir evidencia current.")}</div>
        </div>`;
    }
    if (payload.interpretation) renderInterpretationChips(payload.interpretation.chips || []);
    renderAuthority(payload.authority || {});
    renderEvidence(payload.evidence || []);
    renderBlocks(payload.blocks || payload.render_blocks || []);
    renderBottomRail(payload);
    renderTechnicalDrawer(payload);
    renderFeedbackDock(payload);
  }

  function renderAuthority(authority) {
    const root = $("#prismoAuthorityList");
    if (!root) return;
    const precedence = Array.isArray(authority.precedence_applied) ? authority.precedence_applied : [];
    root.innerHTML = `
      <div class="prismo-authority-row"><strong>${esc(authority.winning_source || "NO_CONFIRMADO")}</strong><small>${esc(authority.notes || "Sin fuente ganadora confirmada.")}</small></div>
      ${precedence.map((item, index) => `<div class="prismo-authority-row"><strong>${index + 1}. ${esc(item)}</strong><small>${index === 0 ? "mayor autoridad" : "precedencia inferior"}</small></div>`).join("")}`;
  }

  function renderEvidence(items) {
    const root = $("#prismoEvidenceList");
    if (!root) return;
    root.innerHTML = items.length ? items.map((item) => `
      <div class="prismo-evidence-row">
        <strong>${esc(item.title || item.id || "Evidencia")}</strong>
        <small>${esc(item.source_type || "unknown")} · ${esc(item.freshness || "unknown")} · ${esc(item.confidence || "low")}</small>
        <small>${esc(item.summary || item.quote || "")}</small>
      </div>`).join("") : `
      <div class="prismo-evidence-row"><strong>Evidencia local</strong><small>Lectura segura · preparada para clasificar · alta prioridad</small></div>
      <div class="prismo-evidence-row"><strong>Estado visual</strong><small>Rutas, capas y regresiones integrables.</small></div>
      <div class="prismo-evidence-row"><strong>Gobernanza</strong><small>Reglas, permisos y límites de mutación visibles.</small></div>`;
  }

  function renderBlocks(blocks) {
    const root = $("#prismoRenderGrid");
    if (!root) return;
    root.innerHTML = "";
    if (!window.PRISMO_RENDERERS) {
      root.innerHTML = `<div class="prismo-empty">Renderer PRISMO no disponible.</div>`;
      return;
    }
    blocks.forEach((block) => root.appendChild(window.PRISMO_RENDERERS.renderBlock(block)));
  }

  function renderBottomRail(payload) {
    const root = $("#prismoBottomRail");
    if (!root) return;
    const chain = payload.response_memory_chain || {};
    const stages = Array.isArray(chain.stages) && chain.stages.length ? chain.stages : [
      { id: "question", title: "Pregunta capturada", summary: payload.query || payload.message || "free text first" },
      { id: "interpretation", title: "Interpretación editable", summary: `${(payload.interpretation && payload.interpretation.intent) || "intent"} + ${(payload.interpretation && payload.interpretation.area) || "area"} + ${(payload.interpretation && payload.interpretation.lens) || "lens"}` },
      { id: "protocol", title: "Protocolo rankeado", summary: "memoria procedural" },
      { id: "evidence", title: "Evidencia preparada", summary: `${(payload.evidence || []).length} evidencia(s)` },
      { id: "result", title: "Resultado renderizado", summary: payload.certainty_level || "contextual" },
      { id: "feedback", title: "Aprendizaje de respuesta", summary: STATE.feedbackState || "pending" }
    ];
    root.innerHTML = stages.slice(0, 6).map((stage) => `
      <div class="prismo-pipeline-card" data-stage="${esc(stage.id || stage.type || "stage")}">
        <small>${esc(stage.label || stage.id || "stage")}</small>
        <strong>${esc(stage.title || "PRISMO")}</strong>
        <span>${esc(stage.summary || stage.status || "")}</span>
      </div>`).join("");
  }

  function renderTechnicalDrawer(payload) {
    const trace = $("#prismoTechnicalTrace");
    if (!trace) return;
    const view = {
      request_id: payload.request_id || "",
      interpretation: payload.interpretation || {},
      render_plan: payload.render_plan || {},
      response_memory_chain: payload.response_memory_chain || {},
      memory_used: payload.memory_used || [],
      technical_trace: payload.technical_trace || {},
      safety: payload.safety || { read_only: payload.read_only, mutation_allowed: payload.mutation_allowed },
      warnings: payload.warnings || [],
      errors: payload.errors || []
    };
    trace.textContent = JSON.stringify(view, null, 2);
  }

  function openTechnicalDrawer() {
    const drawer = $("#prismoTechnicalDrawer");
    const button = $("#prismoCommandButton");
    if (!drawer) return;
    drawer.hidden = false;
    drawer.dataset.open = "true";
    if (button) button.setAttribute("aria-expanded", "true");
  }

  function closeTechnicalDrawer() {
    const drawer = $("#prismoTechnicalDrawer");
    const button = $("#prismoCommandButton");
    if (!drawer) return;
    drawer.hidden = true;
    drawer.dataset.open = "false";
    if (button) button.setAttribute("aria-expanded", "false");
  }

  function renderFeedbackDock(payload) {
    const root = $("#prismoFeedbackDock");
    const state = $("#prismoFeedbackState");
    if (!root) return;
    root.dataset.requestId = payload.request_id || "";
    root.dataset.status = STATE.feedbackState || "pending";
    if (state) state.textContent = (STATE.feedbackState || "pending").replaceAll("_", " ");
    $$("[data-prismo-feedback]", root).forEach((button) => {
      const active = button.dataset.prismoFeedback === STATE.feedbackState;
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  async function sendFeedback(outcome) {
    STATE.feedbackState = outcome || "pending";
    renderFeedbackDock(STATE.lastResponse || {});
    const payload = {
      rating: outcome,
      request_id: STATE.lastResponse && STATE.lastResponse.request_id,
      summary: STATE.lastResponse && STATE.lastResponse.direct_answer,
      interpretation: STATE.lastResponse && STATE.lastResponse.interpretation,
      surface: "prismo_theater"
    };
    try {
      const response = await fetchJson("/api/prismo/learning/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const state = $("#prismoFeedbackState");
      if (state) state.textContent = response.status === "recorded" ? "recorded" : STATE.feedbackState.replaceAll("_", " ");
    } catch (_error) {
      const state = $("#prismoFeedbackState");
      if (state) state.textContent = "queued locally";
    }
  }

  function wireCommandPalette() {
    const button = $("#prismoCommandButton");
    const palette = $("#prismoCommandPalette");
    if (button && palette) {
      button.addEventListener("click", () => {
        const next = palette.hidden;
        palette.hidden = !next;
        button.setAttribute("aria-expanded", next ? "true" : "false");
      });
    }
    $$("[data-prismo-command]").forEach((command) => {
      command.addEventListener("click", () => {
        const action = command.dataset.prismoCommand;
        if (action === "focus_query") $("#prismoPrompt")?.focus();
        if (action === "open_technical") openTechnicalDrawer();
        if (action === "prepare_action") {
          STATE.guidance.intent = "prepare_action";
          const select = $("#prismoIntentSelect");
          if (select) select.value = "prepare_action";
          renderInterpretationChips();
        }
        if (palette) palette.hidden = true;
      });
    });
    $("#prismoTechnicalClose")?.addEventListener("click", closeTechnicalDrawer);
  }

  function wireFeedback() {
    $$("#prismoFeedbackDock [data-prismo-feedback]").forEach((button) => {
      button.addEventListener("click", () => sendFeedback(button.dataset.prismoFeedback || "pending"));
    });
  }

  async function submit(event) {
    event.preventDefault();
    if (STATE.busy) return;
    const payload = collectPayload();
    if (!payload.message && !payload.evidenceText && !payload.attachments.length) {
      toast("Escribe una pregunta o pega evidencia.");
      return;
    }
    STATE.busy = true;
    const send = $("#prismoSendButton");
    if (send) send.disabled = true;
    setState("submitting");
    renderLoading();
    try {
      setState("thinking");
      const response = await fetchJson("/api/prismo/theater/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      setState("rendering");
      renderResponse(response);
    } catch (error) {
      setState("error");
      renderResponse(error.payload || {
        ok: false,
        status: "error",
        mode: STATE.mode,
        demo_mode: true,
        direct_answer: "No se pudo consultar PRISMO. No se ejecutó ninguna acción.",
        certainty_level: "NO_CONFIRMADO",
        risk: { level: "medium", summary: String(error.message || error) },
        safe_next_step: "Revisa el reporte técnico o intenta con menos evidencia.",
        evidence: [],
        render_blocks: [],
        meta: { provider: "demo" }
      });
    } finally {
      STATE.busy = false;
      if (send) send.disabled = false;
    }
  }

  function clearComposer() {
    const prompt = $("#prismoPrompt");
    const evidence = $("#prismoEvidenceText");
    const context = $("#prismoContextText");
    const file = $("#prismoEvidenceFile");
    if (prompt) prompt.value = "";
    if (evidence) evidence.value = "";
    if (context) context.value = "";
    if (file) file.value = "";
    $$("[data-prismo-guidance]").forEach((select) => { select.value = ""; });
    STATE.guidance = { intent: "", area: "", lens: "" };
    STATE.chips = { intent: "", area: "", lens: "" };
    STATE.feedbackState = "pending";
    STATE.evidenceFiles = [];
    const note = $("#prismoFileNote");
    if (note) note.textContent = "Sin archivos adjuntos.";
    renderInterpretationChips();
    renderFeedbackDock(STATE.lastResponse || {});
  }

  function boot() {
    bindSurfaceCapture();
    wireModes();
    wireGuidance();
    wireCommandPalette();
    wireFeedback();
    renderSuggestions();
    $("#prismoComposer")?.addEventListener("submit", submit);
    $("#prismoClearButton")?.addEventListener("click", clearComposer);
    $("#prismoEvidenceFile")?.addEventListener("change", (event) => readEvidenceFiles(event.currentTarget));
    const initial = (location.hash || "").toLowerCase();
    const pathName = (location.pathname || "").toLowerCase().replace(/\/+$/, "");
    let stored = "";
    try { stored = localStorage.getItem(STORE_INTERFACE) || ""; } catch (_err) {}
    if (initial === "#prismo" || pathName === "/prismo" || stored === "prismo") {
      window.setTimeout(() => setSurface("prismo"), 40);
    }
    refreshStatus();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  window.PRISMO_COMMAND_NEXUS = {
    state: STATE,
    setSurface,
    refreshStatus,
    submit: () => $("#prismoComposer")?.requestSubmit()
  };
})();
