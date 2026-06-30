(function () {
  "use strict";

  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const STORE_HISTORY = "prismo-chat-history-v1";
  const MAX_HISTORY_ITEMS = 28;
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
    feedbackState: "pending",
    history: [],
    appLiveContext: null
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



  function clampText(value, max = 460) {
    const text = String(value ?? "");
    return text.length > max ? `${text.slice(0, max - 1)}…` : text;
  }

  function loadHistory() {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORE_HISTORY) || "[]");
      STATE.history = Array.isArray(parsed) ? parsed.slice(0, MAX_HISTORY_ITEMS) : [];
    } catch (_err) {
      STATE.history = [];
    }
  }

  function saveHistory() {
    try { localStorage.setItem(STORE_HISTORY, JSON.stringify(STATE.history.slice(0, MAX_HISTORY_ITEMS))); } catch (_err) {}
  }

  function compactResponseForHistory(response) {
    const payload = response || {};
    return {
      ok: payload.ok !== false,
      status: payload.status || "success",
      request_id: payload.request_id || "",
      mode: payload.mode || STATE.mode,
      demo_mode: Boolean(payload.demo_mode),
      direct_answer: clampText(payload.direct_answer || "", 1600),
      certainty_level: payload.certainty_level || "contextual",
      risk: payload.risk || {},
      safe_next_step: payload.safe_next_step || "",
      interpretation: payload.interpretation || {},
      authority: payload.authority || {},
      evidence: Array.isArray(payload.evidence) ? payload.evidence.slice(0, 8) : [],
      render_plan: payload.render_plan || {},
      render_blocks: selectDisplayBlocks(payload.render_blocks || payload.blocks || [], payload).slice(0, 3),
      blocks: selectDisplayBlocks(payload.render_blocks || payload.blocks || [], payload).slice(0, 3),
      response_memory_chain: payload.response_memory_chain || {},
      memory_used: Array.isArray(payload.memory_used) ? payload.memory_used.slice(0, 8) : [],
      technical_trace: payload.technical_trace ? { adapter_path: payload.technical_trace.adapter_path, missing_sources: payload.technical_trace.missing_sources || [] } : {},
      meta: payload.meta || {}
    };
  }

  function renderHistory() {
    const root = $("#prismoHistoryList");
    const count = $("#prismoHistoryCount");
    if (count) count.textContent = String(STATE.history.length);
    if (!root) return;
    if (!STATE.history.length) {
      root.innerHTML = `<div class="prismo-empty">Haz una consulta y PRISMO la guardará aquí como conversación recuperable.</div>`;
      return;
    }
    root.innerHTML = STATE.history.map((item, index) => `
      <button type="button" class="prismo-history-item" data-prismo-history-index="${index}">
        <span>${esc(item.query || "Consulta PRISMO")}</span>
        <small>${esc(item.renderType || item.status || "respuesta")} · ${esc(item.timeLabel || "reciente")}</small>
        <em>${esc(item.summary || "")}</em>
      </button>`).join("");
  }

  function addHistoryEntry(requestPayload, response) {
    const query = (requestPayload && (requestPayload.message || requestPayload.query)) || (response && (response.query || response.message)) || "";
    if (!query.trim()) return;
    const compact = compactResponseForHistory(response);
    const firstBlock = (compact.render_blocks || compact.blocks || [])[0] || {};
    const entry = {
      id: compact.request_id || `local_${Date.now()}`,
      ts: new Date().toISOString(),
      timeLabel: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      query: clampText(query, 260),
      summary: clampText(compact.direct_answer || compact.safe_next_step || "", 160),
      status: compact.status || "success",
      renderType: firstBlock.type || compact.certainty_level || "respuesta",
      response: compact
    };
    STATE.history = [entry, ...STATE.history.filter((item) => item.id !== entry.id)].slice(0, MAX_HISTORY_ITEMS);
    saveHistory();
    renderHistory();
  }

  function restoreHistoryEntry(index) {
    const entry = STATE.history[Number(index)];
    if (!entry || !entry.response) return;
    const prompt = $("#prismoPrompt");
    if (prompt) prompt.value = entry.query || "";
    renderResponse(entry.response, null, { fromHistory: true });
    if (prompt) prompt.focus();
  }

  function clearHistory() {
    STATE.history = [];
    saveHistory();
    renderHistory();
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

  function renderResponse(payload, requestPayload, options = {}) {
    STATE.lastResponse = payload;
    setState(payload.status === "blocked" ? "blocked" : payload.status === "error" ? "error" : payload.status === "partial" ? "partial" : "success");
    const stream = $("#prismoResponseStream");
    if (stream) {
      const certainty = payload.certainty_level || "NO_CONFIRMADO";
      const risk = payload.risk || {};
      const showRisk = ["high", "critical"].includes(String(risk.level || "").toLowerCase()) || payload.status === "blocked";
      const primaryType = (payload.render_plan && payload.render_plan.selection && payload.render_plan.selection.primary_block_type) || "visual";
      stream.innerHTML = `
        <div class="prismo-response-card prismo-chat-answer-card">
          <div class="prismo-response-meta">
            <span class="prismo-tag" data-state="${payload.status === "blocked" ? "bad" : "ok"}">${esc(payload.status || "success")}</span>
            <span class="prismo-tag">${esc((payload.interpretation && payload.interpretation.intent) || payload.mode || STATE.mode)}</span>
            <span class="prismo-tag" data-state="${payload.demo_mode ? "warn" : "ok"}">${payload.demo_mode ? "deterministic adapter" : "live bridge"}</span>
            <span class="prismo-tag">${esc(primaryType)}</span>
            <span class="prismo-tag">${esc(certainty)}</span>
          </div>
          <p class="prismo-answer">${esc(payload.direct_answer || "")}</p>
          <div class="prismo-safe-step"><strong>Siguiente paso</strong><br>${esc(payload.safe_next_step || "Reunir evidencia current.")}</div>
          ${showRisk ? `<div class="prismo-risk-summary"><strong>Riesgo visible</strong><br>${esc(risk.summary || risk.level || "sin riesgo reportado")}</div>` : ""}
        </div>`;
    }
    if (payload.interpretation) renderInterpretationChips(payload.interpretation.chips || []);
    renderAuthority(payload.authority || {});
    renderEvidence(payload.evidence || []);
    renderBlocks(payload.blocks || payload.render_blocks || [], payload);
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


  function inferPreferredRenderType(payload, blocks) {
    const query = String((payload && (payload.query || payload.message)) || "").toLowerCase();
    const interpretation = (payload && payload.interpretation) || {};
    const intent = String(interpretation.intent || "").toLowerCase();
    const lens = String(interpretation.lens || "").toLowerCase();
    const area = String(interpretation.area || "").toLowerCase();
    const has = (type) => blocks.some((block) => block && block.type === type);
    const pick = (types) => types.find((type) => has(type));
    if (/gr[aá]fic|chart|m[eé]tric|n[uú]mero|score|porcentaje/.test(query)) return pick(["chart_spec", "runtime_map", "impact_map"]);
    if (/graph|grafo|flujo|conect|depend|mapa|ruta|apps|app live|tiempo real|runtime/.test(query) || lens === "runtime_state") return pick(["runtime_map", "impact_map", "flow_diagram"]);
    if (/compar|diff|versus| vs /.test(query) || intent === "compare") return pick(["diff_view", "comparison_board"]);
    if (/timeline|l[ií]nea|cambi[oó]|hist[oó]rico|evoluci/.test(query)) return pick(["timeline"]);
    if (/riesgo|risk|bloque|blocker/.test(query) || intent === "audit") return pick(["risk_matrix", "checklist"]);
    if (/autoridad|govern|gobern|canon|preceden/.test(query) || area === "governance") return pick(["authority_map", "authority_strip"]);
    if (/evidencia|evidence|vault|logs?/.test(query) || lens === "recent_evidence") return pick(["evidence_board", "evidence_cards", "context_pack_explorer"]);
    if (/paso|siguiente|qu[eé] hago|accion|acci[oó]n|check/.test(query) || intent === "recommend" || intent === "prepare_action") return pick(["checklist", "next_best_action", "protocol_ladder"]);
    return pick(["flow_diagram", "runtime_map", "executive_brief", "checklist", "risk_matrix"]);
  }

  function selectDisplayBlocks(blocks, payload) {
    const source = Array.isArray(blocks) ? blocks.filter(Boolean) : [];
    if (!source.length) return [];
    const hiddenTypes = new Set(["technical_drawer", "action_bar", "feedback_dock", "memory_trace", "insight_chips"]);
    const visual = source.filter((block) => block && !hiddenTypes.has(block.type));
    if (visual.length <= 3) {
      return visual.map((block, index) => ({ ...block, layout: index === 0 ? "full" : (block.layout || "half") }));
    }
    const preferredType = (payload && payload.render_plan && payload.render_plan.selection && payload.render_plan.selection.primary_block_type) || inferPreferredRenderType(payload || {}, visual);
    const selected = [];
    const take = (predicate) => {
      const item = visual.find((block) => predicate(block) && !selected.some((picked) => picked.id === block.id));
      if (item) selected.push(item);
    };
    if (preferredType) take((block) => block.type === preferredType);
    take((block) => ["runtime_map", "impact_map", "flow_diagram", "chart_spec", "diff_view", "timeline", "risk_matrix", "checklist", "evidence_board", "authority_map"].includes(block.type));
    take((block) => ["next_best_action", "protocol_ladder", "executive_brief"].includes(block.type));
    visual.forEach((block) => { if (selected.length < 3 && !selected.some((picked) => picked.id === block.id)) selected.push(block); });
    return selected.slice(0, 3).map((block, index) => ({ ...block, layout: index === 0 ? "full" : (block.layout || "half") }));
  }

  function renderBlocks(blocks, payload) {
    const root = $("#prismoRenderGrid");
    if (!root) return;
    root.innerHTML = "";
    if (!window.PRISMO_RENDERERS) {
      root.innerHTML = `<div class="prismo-empty">Renderer PRISMO no disponible.</div>`;
      return;
    }
    selectDisplayBlocks(blocks, payload || STATE.lastResponse || {}).forEach((block) => root.appendChild(window.PRISMO_RENDERERS.renderBlock(block)));
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
    const memory = $("#prismoMemoryTrace");
    if (memory) memory.textContent = JSON.stringify({ memory_used: payload.memory_used || [], response_memory_chain: payload.response_memory_chain || {} }, null, 2);
  }



  function selectDrawerTab(name) {
    const next = name || "trace";
    $$("[data-prismo-drawer-tab]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.prismoDrawerTab === next ? "true" : "false");
    });
    $$("[data-prismo-drawer-section]").forEach((section) => {
      section.hidden = section.dataset.prismoDrawerSection !== next;
    });
  }

  function openTechnicalDrawer(tab = "trace") {
    const drawer = $("#prismoTechnicalDrawer");
    const button = $("#prismoCommandButton");
    if (!drawer) return;
    drawer.hidden = false;
    drawer.dataset.open = "true";
    if (button) button.setAttribute("aria-expanded", "true");
    selectDrawerTab(tab);
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
    $("#prismoOpenTechnical")?.addEventListener("click", () => openTechnicalDrawer("trace"));
    $$("[data-prismo-drawer-tab]").forEach((button) => button.addEventListener("click", () => selectDrawerTab(button.dataset.prismoDrawerTab || "trace")));
  }

  function wireFeedback() {
    $$("#prismoFeedbackDock [data-prismo-feedback]").forEach((button) => {
      button.addEventListener("click", () => sendFeedback(button.dataset.prismoFeedback || "pending"));
    });
  }



  function renderAppLiveContext(payload) {
    const root = $("#prismoAppLiveContext");
    const state = $("#prismoAppLiveState");
    if (!root) return;
    const data = payload && payload.ok ? payload : null;
    if (!data) {
      if (state) { state.textContent = "offline"; state.dataset.state = "warn"; }
      root.innerHTML = `<div class="prismo-mini-card"><strong>Índice no disponible</strong><small>El endpoint estará activo tras recargar el backend de PRISMO.</small></div>`;
      return;
    }
    STATE.appLiveContext = data;
    const apps = Array.isArray(data.apps) ? data.apps : [];
    const summary = data.summary || {};
    const evidence = data.evidence_library || {};
    const delta = data.delta_scanner || {};
    const memoryLayers = data.memory_layers || {};
    if (state) { state.textContent = data.cache_written ? "brain indexed" : "read-only"; state.dataset.state = "ok"; }
    const head = `
      <div class="prismo-mini-card">
        <strong>Project Brain</strong>
        <small>${esc(summary.file_count || 0)} files · ${esc(summary.route_count || 0)} routes · ${esc(summary.memory_layer_count || Object.keys(memoryLayers).length || 0)} memorias</small>
      </div>
      <div class="prismo-mini-card">
        <strong>Evidence Librarian</strong>
        <small>${esc(evidence.zip_count || 0)} ZIPs · fail=${esc(Boolean(evidence.latest_fail))} · result=${esc(Boolean(evidence.latest_result))}</small>
      </div>
      <div class="prismo-mini-card">
        <strong>Delta Scanner</strong>
        <small>${esc(delta.available ? "activo" : "primer índice")} · ${esc(delta.changed_count_sampled || 0)} changed · ${esc(delta.added_count_sampled || 0)} added</small>
      </div>`;
    const body = apps.slice(0, 5).map((app) => `
      <div class="prismo-live-app" data-status="${esc(app.exists ? "ready" : "missing")}">
        <strong>${esc(app.label || app.id)}</strong>
        <small>${esc(app.file_count || 0)} files · ${esc(app.route_count || 0)} routes · ${esc(app.component_count || 0)} comps · ${esc(app.css_count || 0)} css</small>
      </div>`).join("");
    root.innerHTML = head + (body || `<div class="prismo-mini-card"><strong>Sin apps detectadas</strong><small>Read-only scan completado sin superficies.</small></div>`);
  }

  async function refreshAppLiveContext(query = "") {
    try {
      const suffix = query ? `?q=${encodeURIComponent(query.slice(0, 280))}` : "";
      const payload = await fetchJson(`/api/prismo/app-live-context${suffix}`);
      renderAppLiveContext(payload);
      return payload;
    } catch (_error) {
      renderAppLiveContext(null);
      return null;
    }
  }

  function resetComposerAfterSuccess() {
    const prompt = $("#prismoPrompt");
    const evidence = $("#prismoEvidenceText");
    const context = $("#prismoContextText");
    const file = $("#prismoEvidenceFile");
    if (prompt) prompt.value = "";
    if (evidence) evidence.value = "";
    if (context) context.value = "";
    if (file) file.value = "";
    STATE.evidenceFiles = [];
    const note = $("#prismoFileNote");
    if (note) note.textContent = "Panel limpio. Puedes preguntar otra cosa.";
    renderInterpretationChips();
    if (prompt) window.setTimeout(() => prompt.focus(), 20);
  }

  function responseClearsComposer(response) {
    return response && response.ok !== false && !["error", "blocked"].includes(String(response.status || "success").toLowerCase());
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
      const liveContext = await refreshAppLiveContext(payload.message || payload.evidenceText || "");
      if (liveContext) payload.client_context.app_live_context = { generated_at: liveContext.generated_at, apps: (liveContext.apps || []).map((app) => ({ id: app.id, file_count: app.file_count, route_count: app.route_count, css_count: app.css_count })) };
      const response = await fetchJson("/api/prismo/theater/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      setState("rendering");
      renderResponse(response, payload);
      addHistoryEntry(payload, response);
      if (responseClearsComposer(response)) resetComposerAfterSuccess();
    } catch (error) {
      setState("error");
      const errorResponse = error.payload || {
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
      };
      renderResponse(errorResponse, payload);
      addHistoryEntry(payload, errorResponse);
      const prompt = $("#prismoPrompt");
      if (prompt) prompt.focus();
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
    loadHistory();
    renderHistory();
    wireModes();
    wireGuidance();
    wireCommandPalette();
    wireFeedback();
    renderSuggestions();
    $("#prismoComposer")?.addEventListener("submit", submit);
    $("#prismoPrompt")?.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        $("#prismoComposer")?.requestSubmit();
      }
    });
    $("#prismoClearButton")?.addEventListener("click", clearComposer);
    $("#prismoHistoryClear")?.addEventListener("click", clearHistory);
    $("#prismoHistoryList")?.addEventListener("click", (event) => {
      const item = event.target && event.target.closest ? event.target.closest("[data-prismo-history-index]") : null;
      if (item) restoreHistoryEntry(item.dataset.prismoHistoryIndex);
    });
    $("#prismoEvidenceFile")?.addEventListener("change", (event) => readEvidenceFiles(event.currentTarget));
    const initial = (location.hash || "").toLowerCase();
    const pathName = (location.pathname || "").toLowerCase().replace(/\/+$/, "");
    let stored = "";
    try { stored = localStorage.getItem(STORE_INTERFACE) || ""; } catch (_err) {}
    if (initial === "#prismo" || pathName === "/prismo" || stored === "prismo") {
      window.setTimeout(() => setSurface("prismo"), 40);
    }
    refreshStatus();
    refreshAppLiveContext();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  window.PRISMO_COMMAND_NEXUS = {
    state: STATE,
    setSurface,
    refreshStatus,
    submit: () => $("#prismoComposer")?.requestSubmit(),
    history: { render: renderHistory, clear: clearHistory },
    appLiveContext: () => STATE.appLiveContext
  };
})();
