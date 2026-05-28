(function () {
  "use strict";

  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const FILE_PREVIEW_LIMIT = 180000;
  const SUGGESTIONS = [
    "Revisar contradicción de sync",
    "Generar Improvement Brief",
    "Detectar stubs peligrosos",
    "Comparar current vs legacy",
    "Crear mapa de impacto",
    "Explicar ruta real PC → Tablet"
  ];
  const MODES = ["ASK", "INSPECT", "IMPROVE", "EVIDENCE"];
  const STATE = {
    mode: "ASK",
    busy: false,
    status: "booting",
    evidenceFiles: [],
    lastResponse: null,
    bridge: null
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
      chip.textContent = next.replaceAll("_", " ");
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
      if (title) title.textContent = "PRISMO · Gemini Command Nexus";
      if (subtitle) subtitle.textContent = "Inteligencia interna read-only con autoridad, evidencia y safety.";
      if (chips[0]) chips[0].innerHTML = '<span class="dot"></span>Read-only v1';
      if (chips[1]) chips[1].textContent = STATE.bridge && STATE.bridge.demo_mode ? "Bridge demo" : "Gemini Bridge";
      if (chips[2]) chips[2].textContent = "No mutation";
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
      bridge.textContent = payload.demo_mode ? "Gemini Bridge demo" : payload.ai_enabled ? "Gemini Bridge online" : "Gemini Bridge offline";
      bridge.dataset.state = payload.demo_mode ? "demo" : payload.ai_enabled ? "online" : "blocked";
    }
    if (authority) {
      authority.textContent = payload.authority && payload.authority.currentStateLoaded ? "Authority loaded" : "Authority demo";
      authority.dataset.state = payload.authority && payload.authority.currentStateLoaded ? "online" : "demo";
    }
    if (safety) {
      safety.textContent = payload.mutation_allowed ? "Mutation allowed" : "No mutation";
      safety.dataset.state = payload.mutation_allowed ? "blocked" : "online";
    }
    if (html) {
      html.textContent = payload.html_preview_allowed ? "HTML sandbox on" : "HTML preview off";
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
        if (label.includes("Brief")) selectMode("IMPROVE");
        else if (label.includes("stubs") || label.includes("contradicción") || label.includes("Comparar")) selectMode("INSPECT");
        else selectMode("ASK");
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
        item.textPreview = "ZIP uploaded as metadata only in v1. Use an evidence input pack or future backend ingestion.";
      } else if (/\.(txt|md|json|jsonc|log|csv|html|xml|ya?ml)$/i.test(file.name) || file.type.startsWith("text/")) {
        item.textPreview = await file.slice(0, FILE_PREVIEW_LIMIT).text();
      } else {
        item.textPreview = "Unsupported binary preview in v1. File registered as temporal evidence metadata only.";
      }
      STATE.evidenceFiles.push(item);
    }
    const note = $("#prismoFileNote");
    if (note) note.textContent = STATE.evidenceFiles.length ? `${STATE.evidenceFiles.length} archivo(s) listos como evidencia temporal.` : "Sin archivos adjuntos.";
  }

  function collectPayload() {
    const prompt = $("#prismoPrompt");
    const evidence = $("#prismoEvidenceText");
    return {
      mode: STATE.mode,
      message: prompt ? prompt.value.trim() : "",
      attachments: STATE.evidenceFiles,
      requested_output: ["direct_answer", "diagram", "evidence_cards"],
      evidenceText: evidence ? evidence.value.trim() : "",
      client_context: {
        surface: "control_center",
        route: "/prismo"
      }
    };
  }

  function renderLoading() {
    const stream = $("#prismoResponseStream");
    if (!stream) return;
    stream.innerHTML = `
      <div class="prismo-response-card">
        <div class="prismo-response-meta">
          <span class="prismo-tag" data-state="warn">thinking</span>
          <span class="prismo-tag">read-only</span>
          <span class="prismo-tag">safety firewall</span>
        </div>
        <p class="prismo-answer">PRISMO está clasificando intención, autoridad y evidencia temporal.</p>
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
            <span class="prismo-tag">${esc(payload.mode || STATE.mode)}</span>
            <span class="prismo-tag" data-state="${payload.demo_mode ? "warn" : "ok"}">${payload.demo_mode ? "demo mode" : "live bridge"}</span>
            <span class="prismo-tag">${esc(certainty)}</span>
          </div>
          <p class="prismo-answer">${esc(payload.direct_answer || "")}</p>
          <div class="prismo-risk-summary"><strong>Riesgo</strong><br>${esc(risk.summary || risk.level || "sin riesgo reportado")}</div>
          <div class="prismo-safe-step"><strong>Siguiente paso seguro</strong><br>${esc(payload.safe_next_step || "Reunir evidencia current.")}</div>
        </div>`;
    }
    renderAuthority(payload.authority || {});
    renderEvidence(payload.evidence || []);
    renderBlocks(payload.render_blocks || []);
    renderBottomRail(payload);
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
      </div>`).join("") : `<div class="prismo-empty">Sin evidencia confirmada todavía.</div>`;
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
    const risk = payload.risk || {};
    const meta = payload.meta || {};
    root.innerHTML = `
      <div class="prismo-bottom-card"><small>Impact Map</small><strong>${esc(risk.level || "low")}</strong></div>
      <div class="prismo-bottom-card"><small>Runtime Signals</small><strong>${payload.demo_mode ? "demo" : "live"}</strong></div>
      <div class="prismo-bottom-card"><small>Context Pack</small><strong>${esc((payload.evidence || []).length)} evidencias</strong></div>
      <div class="prismo-bottom-card"><small>Ledger</small><strong>${esc(meta.provider || "demo")} · ${esc(payload.request_id || "-")}</strong></div>`;
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
      const response = await fetchJson("/api/prismo/query", {
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
    const file = $("#prismoEvidenceFile");
    if (prompt) prompt.value = "";
    if (evidence) evidence.value = "";
    if (file) file.value = "";
    STATE.evidenceFiles = [];
    const note = $("#prismoFileNote");
    if (note) note.textContent = "Sin archivos adjuntos.";
  }

  function boot() {
    bindSurfaceCapture();
    wireModes();
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
