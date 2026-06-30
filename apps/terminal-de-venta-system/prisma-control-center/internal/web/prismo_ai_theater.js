/* PRISMO Adaptive Intelligence Theater */
(function () {
  "use strict";

  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const PIPELINE = [
    ["question", "Question", "Pregunta capturada", "free text first"],
    ["interpretation", "Interpretation", "Interpretación editable", "intent + area + lens"],
    ["protocol", "Protocol", "Protocolo rankeado", "memoria procedural"],
    ["evidence", "Evidence", "Evidencia preparada", "fuentes clasificables"],
    ["result", "Result", "Resultado renderizado", "Auto Render Ensemble"],
    ["feedback", "Feedback", "Aprendizaje de respuesta", "adapter seguro"]
  ];
  const SAFE_QUESTIONS = [
    "¿Qué evidencia reciente explica el estado de PRISMO?",
    "¿Qué memoria procedural ayuda a reparar esta señal?",
    "¿Dónde está el mayor riesgo operativo ahora?",
    "¿Qué acción preparada conviene revisar?",
    "¿Qué bloque visual debe renderizar PRISMO automáticamente?",
    "¿Cómo se compara esta evidencia contra la autoridad vigente?"
  ];

  let renderingPipeline = false;

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = (value) => String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;"
  }[ch]));

  function setText(node, value) {
    if (node && node.textContent !== value) node.textContent = value;
  }

  function setHtml(node, value) {
    if (node && node.innerHTML !== value) node.innerHTML = value;
  }

  function isPrismoActive() {
    return document.body && document.body.dataset.prismaInterface === "prismo";
  }

  function setHeaderForPrismo() {
    if (!isPrismoActive()) return;
    const title = $(".topbar .titles h1");
    const subtitle = $("#subtitle");
    const chips = $$(".chips .chip");
    setText(title, "PRISMO");
    setText(subtitle, "Operational AI Core · solo lectura · evidencia y decisión");
    setHtml(chips[0], '<span class="dot"></span>IA operacional');
    setText(chips[1], "Gemini server-side");
    setText(chips[2], "Gobernanza activa");
  }

  function normalizeStatusCopy() {
    const bridge = $("#prismoBridgeStatus");
    const authority = $("#prismoAuthorityStatus");
    const safety = $("#prismoSafetyStatus");
    const html = $("#prismoHtmlStatus");
    if (bridge) setText(bridge, bridge.dataset.state === "blocked" ? "Gemini protegido" : "Gemini server-side");
    setText(authority, "Authority Brain");
    if (safety) {
      setText(safety, "Gobernanza activa");
      safety.dataset.state = "online";
    }
    if (html) {
      setText(html, "Acciones preparadas");
      html.dataset.state = "online";
    }
    const ui = $("#prismoUiState");
    if (ui && ["booting", "idle", "no_api_key", "demo_mode", "Adaptador local"].includes(ui.textContent.trim())) {
      setText(ui, "Inteligencia activa");
      ui.dataset.state = "ok";
    }
  }

  function renderSafeQuestions() {
    const root = $("#prismoSuggestionRow");
    if (!root || root.children.length) return;
    SAFE_QUESTIONS.forEach((text) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "prismo-suggestion-chip";
      button.textContent = text;
      button.addEventListener("click", () => {
        const prompt = $("#prismoPrompt");
        if (prompt) {
          prompt.value = text;
          prompt.dispatchEvent(new Event("input", { bubbles: true }));
          prompt.focus();
        }
      });
      root.appendChild(button);
    });
  }

  function pipelineFromResponse(response) {
    const chain = response && response.response_memory_chain ? response.response_memory_chain : {};
    if (Array.isArray(chain.stages) && chain.stages.length) {
      return chain.stages.slice(0, 6).map((stage) => [
        stage.id || stage.type || "stage",
        stage.label || stage.id || "Stage",
        stage.title || "PRISMO",
        stage.summary || stage.status || ""
      ]);
    }
    return PIPELINE;
  }

  function renderPipeline(payload) {
    const root = $("#prismoBottomRail");
    if (!root || renderingPipeline) return;
    const response = payload || (window.PRISMO_COMMAND_NEXUS && window.PRISMO_COMMAND_NEXUS.state && window.PRISMO_COMMAND_NEXUS.state.lastResponse) || {};
    const labels = pipelineFromResponse(response);
    renderingPipeline = true;
    root.classList.add("prismo-decision-pipeline");
    root.innerHTML = labels.map(([id, stage, title, detail]) => `
      <div class="prismo-pipeline-card" data-stage="${esc(String(id).toLowerCase().replaceAll(" ", "-"))}">
        <small>${esc(stage)}</small>
        <strong>${esc(title)}</strong>
        <span>${esc(detail)}</span>
      </div>`).join("");
    renderingPipeline = false;
  }

  function preservePipeline() {
    const root = $("#prismoBottomRail");
    if (!root || root.dataset.prismoObserver === "true") return;
    root.dataset.prismoObserver = "true";
    const observer = new MutationObserver(() => {
      if (renderingPipeline) return;
      if (!root.querySelector(".prismo-pipeline-card") || root.children.length < 6) {
        renderPipeline();
      }
    });
    observer.observe(root, { childList: true });
    renderPipeline();
  }

  function normalizeLicenseCopy() {
    const surface = $("#licenseOpsSurface");
    if (!surface) return;
    const walker = document.createTreeWalker(surface, NodeFilter.SHOW_TEXT);
    const replacements = [];
    while (walker.nextNode()) replacements.push(walker.currentNode);
    replacements.forEach((node) => {
      node.nodeValue = node.nodeValue
        .replace(/\bRuntime and Data Explorer\b/g, "Explorador de Entorno y Datos")
        .replace(/\bRuntime local-first\b/g, "Entorno local-first")
        .replace(/\bLicencias y Runtime\b/g, "Licencias y Entorno Local")
        .replace(/\bEstado runtime\b/g, "Estado del entorno")
        .replace(/\bRuntime config\b/g, "Config local")
        .replace(/RUNTIME/g, "ENTORNO")
        .replace(/\bRuntime\b/g, "Entorno local")
        .replace(/\bruntime\b/g, "entorno local");
    });
    if (document.body.dataset.prismaInterface === "license") {
      const subtitle = $("#subtitle");
      setText(subtitle, "Identidad, licencia local y evidencia de provisioning.");
    }
  }

  function watchSurfaceCopy() {
    const main = $("#main") || document.body;
    if (!main || main.dataset.prismoAiTheaterWatch === "true") return;
    main.dataset.prismoAiTheaterWatch = "true";
    const observer = new MutationObserver(() => {
      normalizeLicenseCopy();
      normalizeStatusCopy();
      setHeaderForPrismo();
    });
    observer.observe(main, { childList: true, subtree: true });
  }

  function wrapRefreshStatus() {
    const api = window.PRISMO_COMMAND_NEXUS;
    if (!api || api.__aiTheaterWrapped || typeof api.refreshStatus !== "function") return;
    const original = api.refreshStatus.bind(api);
    api.refreshStatus = async function refreshStatusWithAiTheater() {
      const result = await original();
      normalizeStatusCopy();
      return result;
    };
    api.__aiTheaterWrapped = true;
  }

  function renderNeuralBlock(block) {
    const data = block && block.data ? block.data : {};
    const nodes = Array.isArray(data.nodes) && data.nodes.length ? data.nodes.slice(0, 8) : [
      { label: "Control Center", status: "reads evidence" },
      { label: "Gemini Bridge", status: "server-side AI" },
      { label: "Evidence Vault", status: "traceability" },
      { label: "Governance Canon", status: "governs action" },
      { label: "Static Visual Checks", status: "validates layers" },
      { label: "Dependency Atlas", status: "maps dependency" },
      { label: "PC · Tablet · Mobile", status: "multisurface impact" },
      { label: "Chart Lab", status: "visual intelligence" }
    ];
    const zones = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"];
    const article = document.createElement("article");
    article.className = "prismo-render-card";
    article.dataset.type = "flow_diagram";
    article.dataset.layout = "full";
    article.innerHTML = `
      <h4>${esc(block && block.title || "Neural Operations Graph")}</h4>
      <div class="prismo-neural-graph" aria-label="Neural Operations Graph render">
        <div class="prismo-graph-core"><small>Neural Operations Graph</small><strong>PRISMO Core</strong><span>decisión guiada</span></div>
        ${nodes.map((node, index) => `
          <div class="prismo-graph-node" data-zone="${zones[index] || zones[zones.length - 1]}">
            <strong>${esc(node.label || node.id || "Nodo")}</strong>
            <small>${esc(node.status || node.edge || node.summary || "")}</small>
          </div>`).join("")}
      </div>`;
    return article;
  }

  function wrapRenderers() {
    const renderers = window.PRISMO_RENDERERS;
    if (!renderers || renderers.__aiTheaterWrapped || typeof renderers.renderBlock !== "function") return;
    const original = renderers.renderBlock.bind(renderers);
    renderers.renderBlock = function renderBlockWithAiTheater(block) {
      const variant = block && block.data && block.data.variant;
      if (block && block.type === "flow_diagram" && variant === "neural_operations_graph") {
        return renderNeuralBlock(block);
      }
      return original(block);
    };
    renderers.__aiTheaterWrapped = true;
  }

  function exposeSurfaceFix() {
    window.PRISMO_AI_THEATER = {
      version: "prismo-theater-task2-20260601",
      get interpretation() {
        const state = window.PRISMO_COMMAND_NEXUS && window.PRISMO_COMMAND_NEXUS.state;
        return state ? { guidance: state.guidance, chips: state.chips } : {};
      },
      renderPipeline,
      normalizeStatusCopy,
      normalizeLicenseCopy
    };
    document.addEventListener("click", (event) => {
      const button = event.target && event.target.closest ? event.target.closest("[data-prisma-interface-target]") : null;
      if (!button) return;
      window.setTimeout(() => {
        setHeaderForPrismo();
        normalizeStatusCopy();
        normalizeLicenseCopy();
      }, 20);
      try { localStorage.setItem(STORE_INTERFACE, button.dataset.prismaInterfaceTarget || "operation"); } catch (_err) {}
    }, true);
  }

  function boot() {
    renderSafeQuestions();
    // PRISMO UI1: bottom rail was retired; preservePipeline no-ops when absent.
    preservePipeline();
    wrapRefreshStatus();
    wrapRenderers();
    watchSurfaceCopy();
    exposeSurfaceFix();
    normalizeStatusCopy();
    normalizeLicenseCopy();
    setHeaderForPrismo();
    window.setTimeout(() => {
      renderSafeQuestions();
      normalizeStatusCopy();
      normalizeLicenseCopy();
      setHeaderForPrismo();
      wrapRenderers();
    }, 80);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
