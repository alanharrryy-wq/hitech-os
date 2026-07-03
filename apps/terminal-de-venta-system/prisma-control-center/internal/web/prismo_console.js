(function () {
  "use strict";

  // PRISMO_TQFIX4_CLIENT_FALLBACK: Theater Query errors never replace a useful Project Brain answer.

  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const STORE_HISTORY = "prismo-chat-history-v1";
  const MAX_HISTORY_ITEMS = 28;
  const FILE_PREVIEW_LIMIT = 180000;
  const ANSWER_OVERFLOW_GUARD = { chars: 24000, lines: 320 };
  const MAX_VISUAL_BLOCKS = 12;
  const PRISMO_QUERY_FALLBACK_CONTRACT = "theater_query_never_blocks_project_brain_v1";
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

  async function fetchJson(url, options = {}) {
    const timeoutMs = Number(options.timeoutMs || 0);
    const fetchOptions = { ...(options || {}) };
    delete fetchOptions.timeoutMs;
    let controller = null;
    let timeoutHandle = null;
    if (timeoutMs > 0 && typeof AbortController !== "undefined") {
      controller = new AbortController();
      fetchOptions.signal = controller.signal;
      timeoutHandle = window.setTimeout(() => controller.abort(), timeoutMs);
    }
    try {
      const response = await fetch(url, {
        cache: "no-store",
        headers: { Accept: "application/json", ...(fetchOptions && fetchOptions.headers ? fetchOptions.headers : {}) },
        ...fetchOptions
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const error = new Error(payload.direct_answer || payload.error || payload.status || `${url} ${response.status}`);
        error.payload = payload;
        throw error;
      }
      return payload;
    } catch (error) {
      if (error && error.name === "AbortError") {
        const timeoutError = new Error(`timeout:${url}`);
        timeoutError.code = "PRISMO_CLIENT_TIMEOUT";
        throw timeoutError;
      }
      throw error;
    } finally {
      if (timeoutHandle) window.clearTimeout(timeoutHandle);
    }
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

  function reasonableAnswer(value) {
    const text = String(value ?? "").replace(/\r\n/g, "\n").trim();
    if (!text) return "PRISMO leyó el contexto disponible en modo read-only y preparó una respuesta trazable.";
    const normalized = text
      .split("\n")
      .map((line) => line.trimEnd())
      .join("\n")
      .replace(/\n{4,}/g, "\n\n\n")
      .trim();
    const lines = normalized.split("\n");
    let guarded = lines.length > ANSWER_OVERFLOW_GUARD.lines
      ? `${lines.slice(0, ANSWER_OVERFLOW_GUARD.lines).join("\n").trim()}\n\n…[respuesta abreviada solo por protección anti-desborde de UI]`
      : normalized;
    if (guarded.length > ANSWER_OVERFLOW_GUARD.chars) {
      guarded = `${guarded.slice(0, ANSWER_OVERFLOW_GUARD.chars - 72).trim()}\n\n…[respuesta abreviada solo por protección anti-desborde de UI]`;
    }
    return guarded;
  }

  function formatAnswerHtml(value) {
    const text = reasonableAnswer(value);
    const chunks = text.split(/\n{2,}/).map((part) => part.trim()).filter(Boolean);
    if (!chunks.length) return `<p>${esc(text)}</p>`;
    return chunks.map((part) => {
      const lines = part.split("\n").map((line) => line.trim()).filter(Boolean);
      if (lines.length > 1 && lines.every((line) => /^[-•*]\s+/.test(line))) {
        return `<ul>${lines.map((line) => `<li>${esc(line.replace(/^[-•*]\s+/, ""))}</li>`).join("")}</ul>`;
      }
      return `<p>${esc(part)}</p>`;
    }).join("");
  }

  function normalizeAnswerChannel(payload) {
    const channel = payload && payload.answer_channel ? payload.answer_channel : {};
    const full = String(channel.full_text || channel.expanded_text || payload.direct_answer || "");
    const main = channel.main_text || channel.short_text || payload.direct_answer || full;
    const mainText = reasonableAnswer(main);
    return {
      mainText,
      shortText: mainText,
      fullText: reasonableAnswer(full || main),
      primaryVisual: channel.primary_visual_type || (payload.visual_stage && payload.visual_stage.primary_block_type) || "visual",
      noVisualReason: channel.no_visual_reason || (payload.visual_stage && payload.visual_stage.no_visual_reason) || "",
      visualRequired: Boolean(channel.visual_stage_required || (payload.visual_stage && payload.visual_stage.required))
    };
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
      render_blocks: selectDisplayBlocks(mergeVisualFallbacks(payload.render_blocks || payload.blocks || [], payload), payload).slice(0, 3),
      blocks: selectDisplayBlocks(mergeVisualFallbacks(payload.render_blocks || payload.blocks || [], payload), payload).slice(0, 3),
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
        <p class="prismo-answer">PRISMO está leyendo Project Brain, hidratando datos y preparando un Visual Stage real, no puro texto.</p>
      </div>`;
  }


  function visualRowsFromLiveContext() {
    const data = STATE.appLiveContext || {};
    const apps = Array.isArray(data.apps) ? data.apps.filter((app) => app && app.exists !== false) : [];
    return apps.map((app) => ({
      id: String(app.id || app.label || "surface"),
      label: String(app.label || app.id || "Surface"),
      files: Number(app.file_count || 0),
      routes: Number(app.route_count || 0),
      components: Number(app.component_count || 0),
      css: Number(app.css_count || 0),
      docs: Number(app.doc_count || 0)
    })).filter((row) => row.files || row.routes || row.components || row.css || row.docs);
  }

  function queryTextFromPayload(payload) {
    return String(
      (payload && (payload._prismo_query || payload.query || payload.message || payload.direct_answer || payload.safe_next_step)) ||
      (STATE.lastResponse && (STATE.lastResponse.query || STATE.lastResponse.message)) ||
      ""
    ).toLowerCase();
  }

  function isProductionQuery(query) {
    const text = String(query || "").toLowerCase();
    return /producci[oó]n|produccion|production|prod|release|go live|salir|cerrar|terminar|qu[eé] falta|que falta|faltan|pendiente|listo|ready/.test(text);
  }

  function sumSurfaceRows(rows) {
    return rows.reduce((acc, row) => {
      acc.files += Number(row.files || 0);
      acc.routes += Number(row.routes || 0);
      acc.components += Number(row.components || 0);
      acc.css += Number(row.css || 0);
      acc.docs += Number(row.docs || 0);
      return acc;
    }, { files: 0, routes: 0, components: 0, css: 0, docs: 0 });
  }

  function productionWeightRows(rows) {
    return rows.map((row) => {
      const weight = Number(row.routes || 0) * 4 + Number(row.components || 0) * 3 + Number(row.css || 0) * 2 + Math.floor(Number(row.files || 0) / 100) + Math.floor(Number(row.docs || 0) / 80);
      return { ...row, weight, prodRisk: weight >= 850 ? "high" : weight >= 300 || Number(row.css || 0) >= 40 ? "medium" : "low" };
    }).sort((a, b) => Number(b.weight || 0) - Number(a.weight || 0));
  }

  function productionAnswerText(rows, requestPayload, error) {
    const totals = sumSurfaceRows(rows);
    const evidence = (STATE.appLiveContext && STATE.appLiveContext.evidence_library) || {};
    const delta = (STATE.appLiveContext && STATE.appLiveContext.delta_scanner) || {};
    const ranked = productionWeightRows(rows).slice(0, 4);
    const rankedText = ranked.length ? ranked.map((row) => `${row.label}: peso ${row.weight} (${row.routes} rutas, ${row.components} comps, ${row.css} CSS)`).join("; ") : "sin superficies ponderables";
    const parts = [
      `Para acercar PRISMA a producción, el punto no es sólo contar ${totals.routes} rutas y ${totals.files} archivos; falta convertir ese inventario en readiness verificable por superficie.`,
      "Faltantes principales: scorecard de producción por superficie; certificación runtime/QA de rutas críticas; evidencia fresca por scope; clasificación de bloqueadores vs deuda; cierre o registro de deuda visual/CSS; y un plan de release con gates claros.",
      `Prioridad read-only por peso: ${rankedText}. No significa que estén rotas; significa que ahí conviene empezar porque concentran más rutas, componentes o CSS.`,
      `Evidencia: ${Number(evidence.zip_count || 0)} ZIPs indexados; latest_result=${Boolean(evidence.latest_result)}; latest_fail=${Boolean(evidence.latest_fail)}. Sin evidencia fresca por superficie, la conclusión debe ser orientación, no green de producción.`,
      delta.available ? `Delta disponible: ${Number(delta.changed_count_sampled || 0)} changed / ${Number(delta.added_count_sampled || 0)} added. Úsalo para detectar deriva reciente antes de declarar estabilidad.` : "Delta no está fresco o está en baseline; PRISMO puede describir estado actual, pero no afirmar estabilidad histórica fuerte.",
      "Siguiente paso: pedir `readiness por superficie` empezando por la superficie de mayor peso. Para cada una: rutas críticas, evidencia reciente, riesgos, deuda visual y conclusión de producción. Todo sigue read-only."
    ];
    if (error) parts.push(`Nota técnica: el bridge live se degradó (${error.code || error.message || String(error)}), pero el análisis salió del Project Brain local ya cargado.`);
    return parts.join("\n\n");
  }

  function chartBlockFromRows(rows, payload) {
    const chartRows = rows.slice(0, 10).map((row) => ({
      surface: row.label,
      files: row.files,
      routes: row.routes,
      components: row.components,
      css: row.css,
      docs: row.docs
    }));
    return {
      id: "client_visual_project_surface_chart",
      type: "chart_spec",
      title: "Visual Stage · Superficies PRISMA",
      description: "Gráfico read-only generado desde Project Brain cuando hay datos estructurados disponibles.",
      priority: 1,
      layout: "full",
      visual_role: "primary",
      status: "ready",
      data: {
        chartType: "bar",
        meta: {
          title: "Superficies PRISMA por rutas, componentes y CSS",
          description: "Comparación del índice vivo read-only; no modifica apps, procesos ni Prisma.",
          footer: "Fuente: /api/prismo/app-live-context y Learning Store."
        },
        xKey: "surface",
        xAxis: { data: chartRows.map((row) => row.surface), label: "Superficie" },
        labels: chartRows.map((row) => row.surface),
        series: [
          { dataKey: "routes", name: "Rutas", label: "Rutas" },
          { dataKey: "components", name: "Componentes", label: "Componentes" },
          { dataKey: "css", name: "CSS", label: "CSS" }
        ],
        data: chartRows,
        rows: chartRows,
        source: "client_fallback_project_brain"
      }
    };
  }

  function matrixBlockFromRows(rows) {
    return {
      id: "client_visual_project_surface_matrix",
      type: "surface_matrix",
      title: "Surface matrix",
      description: "Tabla compacta de lo que Project Brain ve en modo solo lectura.",
      priority: 2,
      layout: "half",
      visual_role: "secondary",
      status: "ready",
      data: { rows: rows.slice(0, 12), columns: ["label", "files", "routes", "components", "css", "docs"] }
    };
  }

  function evidenceFallbackBlock() {
    const evidence = (STATE.appLiveContext && STATE.appLiveContext.evidence_library) || {};
    const rows = [
      { evidence: "ZIPs", count: Number(evidence.zip_count || 0) },
      { evidence: "Latest result", count: evidence.latest_result ? 1 : 0 },
      { evidence: "Latest fail", count: evidence.latest_fail ? 1 : 0 }
    ];
    if (!rows.some((row) => row.count)) return null;
    return {
      id: "client_visual_evidence_chart",
      type: "chart_spec",
      title: "Visual Stage · Evidencia",
      description: "Evidencia histórica detectada por PRISMO en F:\\descargasf.",
      priority: 3,
      layout: "half",
      visual_role: "secondary",
      status: "ready",
      data: {
        chartType: "bar",
        meta: { title: "Evidence Librarian", description: "Conteo de paquetes y señales result/fail recientes." },
        xKey: "evidence",
        labels: rows.map((row) => row.evidence),
        xAxis: { data: rows.map((row) => row.evidence), label: "Evidencia" },
        series: [{ dataKey: "count", name: "Conteo", label: "Conteo" }],
        data: rows
      }
    };
  }

  function deltaFallbackBlock() {
    const delta = (STATE.appLiveContext && STATE.appLiveContext.delta_scanner) || {};
    if (!delta.available) return null;
    return {
      id: "client_visual_delta_timeline",
      type: "timeline",
      title: "Delta timeline",
      description: "Cambios detectados por Project Brain contra el índice previo.",
      priority: 4,
      layout: "half",
      visual_role: "secondary",
      status: "ready",
      data: {
        events: [
          { time: "Previo", title: "Baseline disponible", status: "ready", summary: "Existe índice previo en Learning Store." },
          { time: "Ahora", title: `${Number(delta.changed_count_sampled || 0)} changed · ${Number(delta.added_count_sampled || 0)} added`, status: "read-only", summary: "Comparación sin modificar repo." }
        ].concat((Array.isArray(delta.changed_files_sample) ? delta.changed_files_sample : []).slice(0, 4).map((item) => ({
          time: "sample", title: item.rel || "archivo cambiado", status: "changed", summary: item.mtime || ""
        })))
      }
    };
  }

  function routeFallbackBlock(rows) {
    const apps = (STATE.appLiveContext && Array.isArray(STATE.appLiveContext.apps)) ? STATE.appLiveContext.apps : [];
    const nodes = [];
    apps.forEach((app) => {
      (Array.isArray(app.routes_sample) ? app.routes_sample : []).slice(0, 8).forEach((route) => {
        nodes.push({ id: route.route || route.rel || app.id, label: route.route || route.rel || "route", status: app.label || app.id, summary: route.rel || "" });
      });
    });
    if (!nodes.length && rows.length) {
      rows.slice(0, 8).forEach((row) => nodes.push({ id: row.id, label: row.label, status: `${row.routes} rutas`, summary: `${row.files} archivos · ${row.components} componentes` }));
    }
    if (!nodes.length) return null;
    return { id: "client_visual_route_map", type: "route_map", title: "Route map", description: "Rutas y superficies detectadas por Project Brain.", priority: 5, layout: "half", visual_role: "secondary", status: "ready", data: { nodes: nodes.slice(0, 40) } };
  }

  function layerFallbackBlock() {
    const apps = (STATE.appLiveContext && Array.isArray(STATE.appLiveContext.apps)) ? STATE.appLiveContext.apps : [];
    const rows = [];
    apps.forEach((app) => {
      (Array.isArray(app.layer_signals) ? app.layer_signals : []).slice(0, 8).forEach((sig) => rows.push({ surface: app.label || app.id, file: sig.file || "", selector: sig.selector || "", z_index: Array.isArray(sig.z_index) ? sig.z_index.join(", ") : "", important: sig.important_count || 0, backdrop: Boolean(sig.backdrop_filter) }));
    });
    if (!rows.length) return null;
    return { id: "client_visual_layer_table", type: "table_view", title: "Layer investigator", description: "Selectores, z-index y señales visuales, sin tocar CSS.", priority: 6, layout: "half", visual_role: "secondary", status: "ready", data: { rows: rows.slice(0, 28), columns: ["surface", "file", "selector", "z_index", "important", "backdrop"] } };
  }

  function memoryFallbackBlock() {
    const layers = (STATE.appLiveContext && STATE.appLiveContext.memory_layers) || {};
    const rows = Object.entries(layers).map(([key, value]) => ({ memory: key.replaceAll("_", " "), confidence: (value && value.confidence) || "medium", purpose: (value && value.purpose) || "" }));
    if (!rows.length) return null;
    return { id: "client_visual_memory_layers", type: "table_view", title: "Memorias chidas", description: "Capas de memoria activas para entender PRISMA.", priority: 7, layout: "half", visual_role: "secondary", status: "ready", data: { rows: rows.slice(0, 10), columns: ["memory", "confidence", "purpose"] } };
  }

  function capabilityFallbackBlock() {
    return { id: "client_visual_capability_checklist", type: "checklist", title: "Inteligencia read-only activa", description: "Capacidades locales que PRISMO puede usar sin modificar el proyecto.", priority: 8, layout: "half", visual_role: "secondary", status: "ready", data: { items: [
      { label: "Project Brain indexado", done: Boolean(STATE.appLiveContext && STATE.appLiveContext.ok), status: "apps/rutas/componentes/CSS" },
      { label: "Visual Stage automático", done: true, status: "chart/matrix/timeline/map" },
      { label: "Memoria semántica/procedural/episódica", done: true, status: "Learning Store" },
      { label: "Read-only contract", done: true, status: "sin mutación" },
      { label: "Fallback local si bridge falla", done: true, status: "cliente + Project Brain" }
    ] } };
  }


  function developmentReadinessBlock(rows) {
    const totals = rows.reduce((acc, row) => {
      acc.files += row.files || 0;
      acc.routes += row.routes || 0;
      acc.components += row.components || 0;
      acc.css += row.css || 0;
      return acc;
    }, { files: 0, routes: 0, components: 0, css: 0 });
    return {
      id: "client_visual_development_readiness",
      type: "checklist",
      title: "Readiness para desarrollar PRISMA",
      description: "Lectura read-only de si PRISMO tiene suficiente contexto para orientar desarrollo sin tocar apps.",
      priority: 5,
      layout: "half",
      visual_role: "secondary",
      status: "ready",
      data: { items: [
        { label: "Project Brain ve superficies", done: rows.length > 0, status: `${rows.length} superficies` },
        { label: "Rutas indexadas", done: totals.routes > 0, status: `${totals.routes} rutas` },
        { label: "Componentes indexados", done: totals.components > 0, status: `${totals.components} componentes` },
        { label: "CSS y capas visibles", done: totals.css > 0, status: `${totals.css} CSS` },
        { label: "Evidencia consultable", done: Boolean(STATE.appLiveContext && STATE.appLiveContext.evidence_library && STATE.appLiveContext.evidence_library.zip_count), status: `${(STATE.appLiveContext && STATE.appLiveContext.evidence_library && STATE.appLiveContext.evidence_library.zip_count) || 0} ZIPs` },
        { label: "Modo conocimiento seguro", done: true, status: "read-only / sin mutación" }
      ] }
    };
  }

  function riskFallbackBlock(rows) {
    const evidence = (STATE.appLiveContext && STATE.appLiveContext.evidence_library) || {};
    const delta = (STATE.appLiveContext && STATE.appLiveContext.delta_scanner) || {};
    const cssHeavy = rows.slice().sort((a, b) => (b.css || 0) - (a.css || 0))[0];
    const items = [
      { title: "Contexto fresco", risk: "Contexto fresco", level: rows.length ? "low" : "medium", summary: rows.length ? "Project Brain cargó superficies actuales." : "No hay superficies cargadas todavía.", mitigation: "Refrescar Project Brain antes de decisiones grandes." },
      { title: "Evidencia histórica", risk: "Evidencia histórica", level: evidence.zip_count ? "low" : "medium", summary: `${evidence.zip_count || 0} ZIPs indexados.`, mitigation: "Consultar result/fail ZIPs antes de asumir causa raíz." },
      { title: "Delta reciente", risk: "Delta reciente", level: delta.available ? "low" : "medium", summary: delta.available ? `${delta.changed_count_sampled || 0} changed / ${delta.added_count_sampled || 0} added.` : "Primer índice o baseline no disponible.", mitigation: "Comparar contra siguiente índice para detectar deriva real." }
    ];
    if (cssHeavy) items.push({ title: "Carga visual", risk: "Carga visual", level: (cssHeavy.css || 0) > 40 ? "medium" : "low", summary: `${cssHeavy.label}: ${cssHeavy.css || 0} CSS detectados.`, mitigation: "Usar Layer Investigator antes de cualquier cambio visual." });
    return { id: "client_visual_readonly_risk_matrix", type: "risk_matrix", title: "Riesgos read-only", description: "Riesgos de interpretación detectados sin tocar archivos.", priority: 6, layout: "half", visual_role: "secondary", status: "ready", data: { items } };
  }

  function productionReadinessBlock(rows) {
    const totals = sumSurfaceRows(rows);
    const evidence = (STATE.appLiveContext && STATE.appLiveContext.evidence_library) || {};
    const delta = (STATE.appLiveContext && STATE.appLiveContext.delta_scanner) || {};
    const ranked = productionWeightRows(rows);
    const top = ranked[0] || {};
    return { id: "client_visual_production_readiness", type: "checklist", title: "Production readiness scorecard", description: "Qué falta para acercar PRISMA a producción, no sólo qué puede leer PRISMO.", priority: 1, layout: "full", visual_role: "primary", status: "ready", data: { items: [
      { label: "Inventario read-only suficiente", done: Boolean(totals.files && totals.routes), status: `${totals.files} archivos · ${totals.routes} rutas` },
      { label: "Evidencia fresca por scope", done: Boolean(evidence.latest_result), status: evidence.latest_result ? "hay result reciente" : "falta confirmar result por superficie" },
      { label: "Runtime/QA de rutas críticas", done: false, status: "pendiente de evidencia certificada por superficie" },
      { label: "Bloqueadores vs deuda separados", done: false, status: "necesita scorecard por surface" },
      { label: "Deuda visual/CSS clasificada", done: false, status: `${totals.css} CSS; revisar capas críticas` },
      { label: "Delta reciente revisado", done: Boolean(delta.available), status: delta.available ? `${delta.changed_count_sampled || 0} changed / ${delta.added_count_sampled || 0} added` : "baseline no concluyente" },
      { label: "Superficie prioritaria calculada", done: Boolean(top.label), status: top.label ? `${top.label} · peso ${top.weight}` : "sin superficie top" },
      { label: "Contrato read-only respetado", done: true, status: "PRISMO orienta; no modifica" }
    ] } };
  }

  function productionSurfaceRiskBlock(rows) {
    const ranked = productionWeightRows(rows).slice(0, 8);
    const items = ranked.map((row) => ({
      risk: `${row.label} readiness`,
      title: `${row.label} readiness`,
      level: row.prodRisk,
      summary: `Peso ${row.weight}: ${row.routes} rutas, ${row.components} componentes, ${row.css} CSS.`,
      mitigation: "Pedir scorecard específico: rutas críticas, evidencia fresca, runtime QA, deuda visual y bloqueadores."
    }));
    return { id: "client_visual_production_surface_risk", type: "risk_matrix", title: "Riesgo por superficie para producción", description: "Priorización read-only por peso real de rutas, componentes y CSS.", priority: 2, layout: "full", visual_role: "primary", status: "ready", data: { items } };
  }

  function productionNextStepsBlock(rows) {
    const ranked = productionWeightRows(rows);
    const top = ranked[0] || {};
    const totals = sumSurfaceRows(rows);
    return { id: "client_visual_production_next_steps", type: "checklist", title: "Siguiente paso hacia producción", description: "Cómo convertir contexto en avance real sin tocar el proyecto desde PRISMO.", priority: 3, layout: "half", visual_role: "secondary", status: "ready", data: { items: [
      { label: "Readiness por superficie", done: false, status: top.label ? `empezar por ${top.label}` : "definir surface inicial" },
      { label: "Rutas críticas vs evidencia", done: false, status: `${totals.routes} rutas indexadas` },
      { label: "Separar bloqueadores, warnings y deuda", done: false, status: "evitar inventario gigante sin prioridad" },
      { label: "Confirmar evidence fresh", done: false, status: "usar result/fail ZIPs recientes" },
      { label: "Revisar delta reciente", done: Boolean(STATE.appLiveContext && STATE.appLiveContext.delta_scanner && STATE.appLiveContext.delta_scanner.available), status: "antes de declarar estabilidad" },
      { label: "Mantener modo conocimiento", done: true, status: "read-only" }
    ] } };
  }

  function intelligenceRouterBlock(payload) {
    const query = queryTextFromPayload(payload);
    const signals = [
      ["surfaces", /app|apps|superficie|surface|tablet|pc|mobile|chart/.test(query)],
      ["routes", /ruta|route|page|layout|endpoint/.test(query)],
      ["layers", /css|layer|selector|z-index|capa|visual/.test(query)],
      ["evidence", /evidencia|evidence|zip|fail|result|log/.test(query)],
      ["delta", /cambio|cambió|delta|desde|ayer|timeline|histórico|historico/.test(query)],
      ["memory", /memoria|memory|procedural|semant|episod|aprendiz/.test(query)],
      ["risk", /riesgo|risk|bloque|blocker|gate|gobern|autoridad/.test(query)],
      ["build", /terminar|desarroll|útil|util|mejora|arregl|funcion/.test(query)],
      ["graph", /grafo|graph|mapa|depend|conecta|flujo/.test(query)],
      ["chart", /graf|chart|métrica|metrica|número|numero|conteo|cuánt|cuant/.test(query)]
    ];
    return { id: "client_visual_intelligence_router", type: "table_view", title: "Router de inteligencia", description: "Señales detectadas para elegir texto, memoria y visuales.", priority: 9, layout: "half", visual_role: "secondary", status: "ready", data: { rows: signals.map(([signal, used]) => ({ signal, used: used ? "yes" : "available", source: "client query profiler" })), columns: ["signal", "used", "source"] } };
  }

  function buildClientVisualFallbacks(payload) {
    const rows = visualRowsFromLiveContext();
    if (!rows.length) return [];
    const query = queryTextFromPayload(payload);
    const wantsBroad = !query || /todo|completo|diagn[oó]stico|desarroll|terminar|prisma|proyecto|inteligencia|util|útil/.test(query);
    const out = [];
    const add = (block) => { if (block && !out.some((item) => item.id === block.id)) out.push(block); };

    if (isProductionQuery(query)) {
      add(productionReadinessBlock(rows));
      add(productionSurfaceRiskBlock(rows));
      add(productionNextStepsBlock(rows));
      add(evidenceFallbackBlock());
      add(deltaFallbackBlock());
      add(chartBlockFromRows(rows, payload));
      add(matrixBlockFromRows(rows));
      if (/ruta|route|endpoint|mapa/.test(query)) add(routeFallbackBlock(rows));
      if (/css|layer|selector|z-index|capa|visual/.test(query)) add(layerFallbackBlock());
      return out.slice(0, MAX_VISUAL_BLOCKS);
    }

    add(chartBlockFromRows(rows, payload));
    add(matrixBlockFromRows(rows));
    if (wantsBroad || /ruta|route|app|superficie|surface|mapa|grafo|graph|depend/.test(query)) add(routeFallbackBlock(rows));
    if (wantsBroad || /evidencia|evidence|zip|fail|result|historial/.test(query)) add(evidenceFallbackBlock());
    if (wantsBroad || /cambio|cambió|delta|desde|ayer|timeline|histórico|historico/.test(query)) add(deltaFallbackBlock());
    if (wantsBroad || /css|layer|selector|z-index|capa|visual/.test(query)) add(layerFallbackBlock());
    if (wantsBroad || /memoria|memory|procedural|semant|episod|aprendiz/.test(query)) add(memoryFallbackBlock());
    if (wantsBroad || /capacidad|inteligencia|util|usar|terminar|desarroll/.test(query)) add(capabilityFallbackBlock());
    if (wantsBroad || /riesgo|risk|gate|bloque|blocker|seguro/.test(query)) add(riskFallbackBlock(rows));
    if (wantsBroad || /router|por qu[eé]|elige|inteligencia/.test(query)) add(intelligenceRouterBlock(payload));
    if (wantsBroad || /terminar|desarroll|pendiente|listo|readiness/.test(query)) add(developmentReadinessBlock(rows));
    return out.slice(0, MAX_VISUAL_BLOCKS);
  }

  function mergeVisualFallbacks(blocks, payload) {
    const base = Array.isArray(blocks) ? blocks.slice() : [];
    const hasRealChart = base.some((block) => block && ["chart_spec", "surface_matrix", "timeline", "runtime_map", "route_map", "dependency_graph", "risk_matrix", "evidence_board", "table_view"].includes(block.type));
    const fallback = buildClientVisualFallbacks(payload || STATE.lastResponse || {});
    if (!fallback.length) return base;
    if (!hasRealChart) return fallback.concat(base);
    const ids = new Set(base.map((block) => block && block.id));
    fallback.forEach((block) => { if (!ids.has(block.id) && !base.some((item) => item && item.type === block.type && item.title === block.title)) base.push(block); });
    return base;
  }

  function renderResponse(payload, requestPayload, options = {}) {
    STATE.lastResponse = payload;
    setState(payload.status === "blocked" ? "blocked" : payload.status === "error" ? "error" : payload.status === "partial" ? "partial" : "success");
    const stream = $("#prismoResponseStream");
    if (stream) {
      const certainty = payload.certainty_level || "NO_CONFIRMADO";
      const risk = payload.risk || {};
      const showRisk = ["high", "critical"].includes(String(risk.level || "").toLowerCase()) || payload.status === "blocked";
      const answer = normalizeAnswerChannel(payload);
      const fullDetail = answer.fullText && answer.fullText !== answer.mainText ? answer.fullText : (payload.safe_next_step || "Detalle disponible en el drawer técnico.");
      stream.innerHTML = `
        <article class="prismo-response-card prismo-answer-channel" data-visual-required="${answer.visualRequired ? "true" : "false"}">
          <div class="prismo-response-meta">
            <span class="prismo-tag" data-state="${payload.status === "blocked" ? "bad" : "ok"}">${esc(payload.status || "success")}</span>
            <span class="prismo-tag" data-state="ok">Read-only</span>
            <span class="prismo-tag">Visual: ${esc(answer.primaryVisual)}</span>
            <span class="prismo-tag">${esc(certainty)}</span>
          </div>
          <h3>Respuesta PRISMO</h3>
          <div class="prismo-answer prismo-answer-main">${formatAnswerHtml(answer.mainText || answer.shortText)}</div>
          ${showRisk ? `<div class="prismo-risk-summary"><strong>Riesgo visible</strong><br>${esc(risk.summary || risk.level || "sin riesgo reportado")}</div>` : ""}
          <details class="prismo-collapsible-brief">
            <summary>Ver explicación completa y siguiente paso</summary>
            <div class="prismo-answer-detail">${formatAnswerHtml(fullDetail)}</div>
            <div class="prismo-safe-step"><strong>Siguiente paso</strong><br>${esc(payload.safe_next_step || "Seguir consultando en modo read-only con evidencia fresca.")}</div>
          </details>
        </article>`;
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
    if (/gr[aá]fic|chart|m[eé]tric|n[uú]mero|score|porcentaje/.test(query)) return pick(["chart_spec", "surface_matrix", "runtime_map", "impact_map"]);
    if (/graph|grafo|flujo|conect|depend|mapa|ruta|apps|app live|tiempo real|runtime/.test(query) || lens === "runtime_state") return pick(["runtime_map", "impact_map", "flow_diagram"]);
    if (/compar|diff|versus| vs /.test(query) || intent === "compare") return pick(["diff_view", "comparison_board"]);
    if (/timeline|l[ií]nea|cambi[oó]|hist[oó]rico|evoluci/.test(query)) return pick(["timeline"]);
    if (/riesgo|risk|bloque|blocker/.test(query) || intent === "audit") return pick(["risk_matrix", "checklist"]);
    if (/autoridad|govern|gobern|canon|preceden/.test(query) || area === "governance") return pick(["authority_map", "authority_strip"]);
    if (/evidencia|evidence|vault|logs?/.test(query) || lens === "recent_evidence") return pick(["evidence_board", "evidence_cards", "context_pack_explorer"]);
    if (/paso|siguiente|qu[eé] hago|accion|acci[oó]n|check/.test(query) || intent === "recommend" || intent === "prepare_action") return pick(["checklist", "next_best_action", "protocol_ladder"]);
    return pick(["chart_spec", "surface_matrix", "runtime_map", "flow_diagram", "table_view", "checklist", "risk_matrix"]);
  }

  function inferPreferredRenderType(payload, blocks) {
    const query = queryTextFromPayload(payload);
    const types = new Set((blocks || []).map((block) => block && block.type));
    const pick = (candidates) => candidates.find((type) => types.has(type));
    if (/gr[aá]fic|chart|m[eé]trica|n[uú]mero|conteo|cu[aá]nt/.test(query)) return pick(["chart_spec", "surface_matrix", "table_view"]);
    if (/ruta|route|app|apps|superficie|surface|componente|css|project brain/.test(query)) return pick(["chart_spec", "surface_matrix", "runtime_map", "route_map"]);
    if (/evidencia|evidence|zip|fail|result|historial/.test(query)) return pick(["evidence_board", "chart_spec", "timeline"]);
    if (/cambio|cambió|delta|desde|ayer|timeline|hist[oó]ric/.test(query)) return pick(["timeline", "chart_spec", "diff_view"]);
    if (/compar|diff|versus| vs /.test(query)) return pick(["diff_view", "chart_spec", "surface_matrix"]);
    if (/riesgo|risk|bloque|blocker|gate|gobern/.test(query)) return pick(["risk_matrix", "authority_map", "checklist"]);
    if (/depend|grafo|graph|flujo|conecta|mapa/.test(query)) return pick(["dependency_graph", "route_map", "flow_diagram", "runtime_map"]);
    return pick(["chart_spec", "surface_matrix", "runtime_map", "timeline", "risk_matrix", "checklist"]);
  }

  function selectDisplayBlocks(blocks, payload) {
    const all = Array.isArray(blocks) ? blocks.filter(Boolean) : [];
    const hidden = new Set(["hero_response", "executive_brief", "next_best_action", "protocol_ladder", "procedural_steps", "technical_drawer", "action_bar", "feedback_dock", "memory_trace", "insight_chips", "authority_strip"]);
    const visualTypes = new Set(["chart_spec", "surface_matrix", "runtime_map", "route_map", "dependency_graph", "impact_map", "flow_diagram", "diff_view", "timeline", "risk_matrix", "checklist", "evidence_board", "authority_map", "table_view", "context_pack_explorer"]);
    const visual = all.filter((block) => !hidden.has(block.type) && visualTypes.has(block.type));
    const preferredType = (payload && payload.render_plan && payload.render_plan.selection && payload.render_plan.selection.primary_block_type) || inferPreferredRenderType(payload || {}, visual);
    const selected = [];
    const take = (predicate) => {
      const item = visual.find((block) => predicate(block) && !selected.some((picked) => picked.id === block.id));
      if (item) selected.push(item);
    };
    if (preferredType) take((block) => block.type === preferredType);
    take((block) => block.type === "chart_spec");
    take((block) => block.type === "surface_matrix");
    take((block) => ["timeline", "runtime_map", "route_map", "dependency_graph", "risk_matrix", "evidence_board", "table_view", "checklist", "diff_view"].includes(block.type));
    visual.forEach((block) => { if (selected.length < MAX_VISUAL_BLOCKS && !selected.some((picked) => picked.id === block.id)) selected.push(block); });
    return selected.slice(0, MAX_VISUAL_BLOCKS).map((block, index) => ({ ...block, layout: index === 0 ? "full" : (block.layout || (index < 3 ? "half" : "third")), visual_role: index === 0 ? "primary" : "secondary" }));
  }

  function renderBlocks(blocks, payload) {
    const root = $("#prismoRenderGrid");
    if (!root) return;
    root.innerHTML = "";
    if (!window.PRISMO_RENDERERS) {
      root.innerHTML = `<div class="prismo-empty">Renderer PRISMO no disponible.</div>`;
      return;
    }
    const merged = mergeVisualFallbacks(blocks, payload || STATE.lastResponse || {});
    const selected = selectDisplayBlocks(merged, payload || STATE.lastResponse || {});
    if (!selected.length) {
      const reason = (payload && payload.visual_stage && payload.visual_stage.no_visual_reason) || "insufficient_structured_data";
      root.innerHTML = reason === "conversational_only" ? "" : `<article class="prismo-render-card prismo-compact-empty" data-type="no_visual_reason" data-layout="full"><h4>Visual no requerido</h4><small>${esc(reason)}</small></article>`;
      return;
    }
    selected.forEach((block) => {
      try {
        root.appendChild(window.PRISMO_RENDERERS.renderBlock(block));
      } catch (error) {
        const fallback = document.createElement("article");
        fallback.className = "prismo-render-card";
        fallback.dataset.type = "render_error";
        fallback.dataset.layout = "full";
        fallback.innerHTML = `<div class="prismo-render-title"><h4>${esc(block.title || "Visual Stage")}</h4><p>El renderer falló, pero PRISMO conservó la respuesta estructurada.</p></div><pre>${esc(error && (error.message || String(error)))}</pre>`;
        root.appendChild(fallback);
      }
    });
  }

  function renderBottomRail(payload) {
    const root = $("#prismoBottomRail");
    if (!root) return;
    const chain = payload.response_memory_chain || {};
    const stages = Array.isArray(chain.stages) && chain.stages.length ? chain.stages : [
      { id: "question", title: "Pregunta", summary: payload.query || payload.message || "capturada" },
      { id: "interpretation", title: "Interpretación", summary: `${(payload.interpretation && payload.interpretation.intent) || "intent"} / ${(payload.interpretation && payload.interpretation.area) || "area"}` },
      { id: "visual", title: "Visual Stage", summary: (payload.visual_stage && payload.visual_stage.primary_block_type) || "auto" },
      { id: "memory", title: "Memoria", summary: `${(payload.memory_used || []).length} capas` },
      { id: "safety", title: "Read-only", summary: payload.mutation_allowed ? "mutation?" : "sin mutación" }
    ];
    root.innerHTML = stages.slice(0, 5).map((stage) => `
      <div class="prismo-pipeline-card" data-stage="${esc(stage.id || stage.type || "stage")}">
        <small>${esc(stage.id || "stage")}</small>
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
      root.innerHTML = `<details class="prismo-context-accordion"><summary>Project Brain no disponible</summary><div class="prismo-mini-card"><strong>Índice no disponible</strong><small>El endpoint estará activo tras recargar el backend de PRISMO.</small></div></details>`;
      return;
    }
    STATE.appLiveContext = data;
    const apps = Array.isArray(data.apps) ? data.apps : [];
    const summary = data.summary || {};
    const evidence = data.evidence_library || {};
    const delta = data.delta_scanner || {};
    const memoryLayers = data.memory_layers || {};
    if (state) { state.textContent = data.cache_written ? "brain indexed" : "read-only"; state.dataset.state = "ok"; }
    const appRows = apps.slice(0, 8).map((app) => `
      <div class="prismo-live-app" data-status="${esc(app.exists ? "ready" : "missing")}">
        <strong>${esc(app.label || app.id)}</strong>
        <small>${esc(app.file_count || 0)} files · ${esc(app.route_count || 0)} rutas · ${esc(app.component_count || 0)} comps · ${esc(app.css_count || 0)} css</small>
      </div>`).join("");
    const memoryRows = Object.entries(memoryLayers).slice(0, 8).map(([key, value]) => `
      <div class="prismo-mini-card"><strong>${esc(key.replaceAll("_", " "))}</strong><small>${esc((value && value.confidence) || "medium")}</small></div>`).join("");
    root.innerHTML = `
      <details class="prismo-context-accordion">
        <summary>Project Brain · ${esc(summary.file_count || 0)} files · ${esc(summary.route_count || 0)} rutas</summary>
        <div class="prismo-mini-grid">
          <div class="prismo-mini-card"><strong>Evidence Librarian</strong><small>${esc(evidence.zip_count || 0)} ZIPs · fail=${esc(Boolean(evidence.latest_fail))} · result=${esc(Boolean(evidence.latest_result))}</small></div>
          <div class="prismo-mini-card"><strong>Delta Scanner</strong><small>${esc(delta.available ? "activo" : "primer índice")} · ${esc(delta.changed_count_sampled || 0)} changed · ${esc(delta.added_count_sampled || 0)} added</small></div>
        </div>
      </details>
      <details class="prismo-context-accordion">
        <summary>Superficies indexadas</summary>
        <div class="prismo-live-context-list">${appRows || `<div class="prismo-mini-card"><strong>Sin apps detectadas</strong><small>Read-only scan sin superficies.</small></div>`}</div>
      </details>
      <details class="prismo-context-accordion">
        <summary>Memorias chidas</summary>
        <div class="prismo-mini-grid">${memoryRows || `<div class="prismo-mini-card"><strong>Memoria pendiente</strong><small>Learning Store se llenará al consultar.</small></div>`}</div>
      </details>`;
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


  function buildClientOnlyResponse(requestPayload, error) {
    const rows = visualRowsFromLiveContext();
    const summary = rows.reduce((acc, row) => {
      acc.files += row.files || 0;
      acc.routes += row.routes || 0;
      acc.components += row.components || 0;
      acc.css += row.css || 0;
      return acc;
    }, { files: 0, routes: 0, components: 0, css: 0 });
    const blocks = buildClientVisualFallbacks(requestPayload);
    const reason = error && (error.code || error.message || String(error));
    const query = queryTextFromPayload(requestPayload);
    const prodQuery = isProductionQuery(query);
    const shortText = rows.length
      ? (prodQuery ? productionAnswerText(rows, requestPayload, error) : `PRISMO usó Project Brain en modo local read-only. Detecté ${rows.length} superficies, ${summary.files} archivos, ${summary.routes} rutas, ${summary.components} componentes y ${summary.css} CSS. Con eso puedo comparar superficies, revisar rutas, capas, evidencia, delta y memoria sin modificar el proyecto.`)
      : "PRISMO no pudo consultar el bridge y tampoco encontró Project Brain cargado; conviene refrescar contexto antes de concluir.";
    return {
      ok: Boolean(rows.length),
      status: rows.length ? "partial" : "error",
      request_id: `client_project_brain_${Date.now()}`,
      mode: STATE.mode,
      demo_mode: true,
      read_only: true,
      mutation_allowed: false,
      direct_answer: shortText,
      certainty_level: rows.length ? "CONFIRMADO_POR_INDICE_LOCAL" : "NO_CONFIRMADO",
      answer_channel: {
        contract: "prismo.answer_channel.v3.client_local",
        short_text: shortText,
        full_text: rows.length
          ? (prodQuery ? shortText : `${shortText} El bridge de consulta no respondió a tiempo, así que PRISMO usó el índice local ya cargado.`)
          : `No hubo respuesta del bridge y no se encontró Project Brain cargado. Motivo técnico: ${reason || "unknown"}.`,
        overflow_guard: "no_artificial_answer_cap_client_local",
        visual_stage_required: Boolean(rows.length),
        primary_visual_type: rows.length ? (prodQuery ? "production_readiness" : "chart_spec") : "no_visual_reason",
        no_visual_reason: rows.length ? "" : "project_brain_unavailable"
      },
      visual_stage: {
        required: Boolean(rows.length),
        source: "client_project_brain_fallback",
        primary_block_type: rows.length ? (prodQuery ? "production_readiness" : "chart_spec") : "no_visual_reason",
        no_visual_reason: rows.length ? "" : "project_brain_unavailable"
      },
      authority: {
        winning_source: "Project Brain client cache",
        winning_source_type: "runtime_readonly_index",
        precedence_applied: ["current app-live-context", "client fallback", "read-only contract"],
        notes: "Fallback local activado porque el endpoint de consulta no respondió correctamente."
      },
      evidence: [],
      risk: {
        level: rows.length ? "low" : "medium",
        summary: rows.length ? "Bridge de consulta degradado; Visual Stage local disponible." : "Bridge y Visual Stage local no disponibles.",
        reasons: reason ? [reason] : [],
        mitigations: ["Mantener modo read-only.", "Revisar endpoint de consulta en diagnóstico técnico."]
      },
      safe_next_step: rows.length ? "Usar el Visual Stage local y revisar el detalle técnico del bridge cuando convenga." : "Recargar Project Brain o revisar runtime.",
      render_blocks: blocks,
      blocks,
      warnings: ["PRISMO_CLIENT_PROJECT_BRAIN_FALLBACK"],
      errors: reason ? [{ code: "PRISMO_QUERY_BRIDGE_DEGRADED", message: String(reason), safe_message: "Consulta local degradada con Visual Stage disponible.", recoverable: true }] : [],
      meta: { provider: "client_project_brain", schema_version: "prodreadiness_client_v1", render_block_count: blocks.length }
    };
  }


  function isTheaterQueryDegraded(payload, error) {
    const status = String((payload && payload.status) || "").toLowerCase();
    const blob = [
      status,
      payload && payload.ok === false ? "ok_false" : "",
      payload && payload.direct_answer,
      payload && payload.error,
      payload && payload.safe_next_step,
      payload && payload.block_reason,
      payload && payload.certainty_level,
      payload && JSON.stringify(payload.errors || []),
      payload && JSON.stringify(payload.warnings || []),
      error && error.message,
      error && error.code
    ].filter(Boolean).join(" ");
    return Boolean(
      /PRISMO Theater adapter unavailable|PRISMO_THEATER_QUERY_SERVER_FALLBACK|PRISMO_THEATER_QUERY_IMPL_DEGRADED|PRISMO_QUERY_BRIDGE_DEGRADED|timeout:\/api\/prismo\/theater\/query|Theater Query|adapter unavailable|returned null|NO_CONFIRMADO/i.test(blob) &&
      (status === "error" || status === "blocked" || /fallback|degrad|timeout|validar|adapter|returned null/i.test(blob))
    );
  }

  function compactServerError(payload, error) {
    const errors = Array.isArray(payload && payload.errors) ? payload.errors.slice(0, 6) : [];
    const warnings = Array.isArray(payload && payload.warnings) ? payload.warnings.slice(0, 10) : [];
    return {
      server_status: payload && payload.status,
      server_request_id: payload && payload.request_id,
      server_error: payload && (payload.error || payload.direct_answer),
      client_error: error && (error.message || String(error)),
      client_code: error && error.code,
      warnings,
      errors
    };
  }

  function responseForDisplay(response, requestPayload, error) {
    const serverPayload = response && typeof response === "object" ? response : null;
    const degraded = isTheaterQueryDegraded(serverPayload, error);
    if (degraded || (!serverPayload && error)) {
      const fallback = buildClientOnlyResponse(requestPayload, error || { message: serverPayload && (serverPayload.error || serverPayload.direct_answer) || "theater_query_degraded" });
      if (fallback && fallback.ok) {
        const serverDetail = compactServerError(serverPayload || {}, error || {});
        fallback.status = "partial";
        fallback.ok = true;
        fallback.certainty_level = "CONFIRMADO_POR_INDICE_LOCAL";
        fallback.warnings = Array.from(new Set([...(fallback.warnings || []), "PRISMO_THEATER_QUERY_DEGRADED_HIDDEN_FROM_USER", ...(serverDetail.warnings || [])]));
        fallback.errors = [
          ...(Array.isArray(fallback.errors) ? fallback.errors : []),
          {
            code: "PRISMO_THEATER_QUERY_DEGRADED_HIDDEN_FROM_USER",
            message: "Theater Query no validó en backend, pero Project Brain client-side respondió en modo read-only.",
            safe_message: "PRISMO usó Project Brain local; el detalle técnico conserva la falla del bridge.",
            recoverable: true,
            server_detail: serverDetail
          }
        ];
        fallback.technical_trace = {
          ...(fallback.technical_trace || {}),
          adapter_path: "client::responseForDisplay",
          degraded_server_payload: serverDetail,
          fallback_source: "Project Brain client cache",
          policy: "Never show Theater Query validation failure as the main user answer when local Project Brain is available."
        };
        fallback.meta = { ...(fallback.meta || {}), bridge_degraded_hidden: true, schema_version: "prodreadiness_client_v2" };
        return fallback;
      }
    }
    return serverPayload || buildClientOnlyResponse(requestPayload, error);
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
        body: JSON.stringify(payload),
        timeoutMs: 9000
      });
      const displayResponse = responseForDisplay(response, payload, null);
      setState(displayResponse.status === "error" ? "error" : "rendering");
      renderResponse(displayResponse, payload);
      addHistoryEntry(payload, displayResponse);
      if (responseClearsComposer(displayResponse)) resetComposerAfterSuccess();
    } catch (error) {
      const displayResponse = responseForDisplay(error.payload || null, payload, error);
      setState(displayResponse.status === "error" ? "error" : "rendering");
      renderResponse(displayResponse, payload);
      addHistoryEntry(payload, displayResponse);
      if (responseClearsComposer(displayResponse)) resetComposerAfterSuccess();
      else {
        const prompt = $("#prismoPrompt");
        if (prompt) prompt.focus();
      }
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
