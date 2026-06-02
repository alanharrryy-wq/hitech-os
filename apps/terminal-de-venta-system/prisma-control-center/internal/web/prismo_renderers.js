(function () {
  "use strict";

  const BLOCKED_TEXT = "Bloque visual bloqueado porque no cumplió las reglas de seguridad.";
  const ALLOWED = new Set([
    "hero_response",
    "executive_brief",
    "next_best_action",
    "protocol_ladder",
    "procedural_steps",
    "procedural_recipe",
    "evidence_board",
    "evidence_cards",
    "risk_matrix",
    "timeline",
    "flow_diagram",
    "comparison_board",
    "memory_trace",
    "authority_strip",
    "context_cards",
    "insight_chips",
    "technical_drawer",
    "action_bar",
    "error_recovery",
    "loading_state",
    "feedback_dock",
    "direct_answer_card",
    "authority_map",
    "impact_map",
    "runtime_map",
    "improvement_brief_board",
    "context_pack_explorer",
    "diff_view",
    "checklist",
    "chart_spec"
  ]);
  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;"
    }[ch]));
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function card(block, body) {
    const node = document.createElement("article");
    node.className = "prismo-render-card";
    node.dataset.type = block.type || "blocked";
    node.dataset.layout = block.layout || "half";
    node.innerHTML = `<h4>${esc(block.title || "PRISMO")}</h4>`;
    if (typeof body === "string") node.insertAdjacentHTML("beforeend", body);
    else if (body) node.appendChild(body);
    return node;
  }

  function blockedCard() {
    return card({ title: "Bloque visual bloqueado", type: "direct_answer_card", layout: "full" }, `<p>${BLOCKED_TEXT}</p>`);
  }

  function renderDirect(block) {
    const data = block.data || {};
    return card(block, `<p class="prismo-answer">${esc(data.answer || block.description || "")}</p>`);
  }

  function renderHero(block) {
    const data = block.data || {};
    const interpretation = data.interpretation || {};
    const chips = asArray(interpretation.chips).map((chip) => `
      <span class="prismo-theater-chip" data-source="${esc(chip.source || "inferred")}">${esc(chip.label || chip.value || "")}</span>`).join("");
    return card(block, `
      <p class="prismo-answer">${esc(data.answer || block.summary || block.message || "")}</p>
      <div class="prismo-response-meta">${chips}</div>`);
  }

  function renderNextAction(block) {
    const data = block.data || {};
    return card(block, `
      <div class="prismo-safe-step"><strong>${esc(data.action || block.title || "Next action")}</strong><br>${esc(block.summary || data.impact || "")}</div>
      <div class="prismo-response-meta">
        <span class="prismo-tag" data-state="ok">review impact</span>
        <span class="prismo-tag">prepare action</span>
      </div>`);
  }

  function renderProtocolLadder(block) {
    const protocols = asArray((block.data || {}).protocols);
    return card(block, `<div class="prismo-ranked-ladder">${protocols.map((item, index) => `
      <div class="prismo-ladder-step">
        <small>${esc(String(Math.round(Number(item.score || 0) * 100)))}%</small>
        <strong>${esc(item.label || item.id || `Protocol ${index + 1}`)}</strong>
        <p>${esc(item.reason || "")}</p>
      </div>`).join("") || `<div class="prismo-empty">Sin protocolo rankeado.</div>`}</div>`);
  }

  function renderProcedural(block) {
    const steps = asArray((block.data || {}).steps || (block.data || {}).items);
    return card(block, `<div class="prismo-checklist">${steps.map((item, index) => `
      <div class="prismo-check-item" data-done="${esc(item.status || "ready")}">
        <strong>${index + 1}. ${esc(item.label || item.title || item)}</strong>
        <small>${esc(item.status || "ready")}</small>
      </div>`).join("") || `<div class="prismo-empty">Sin pasos procedurales.</div>`}</div>`);
  }

  function renderEvidenceBoard(block) {
    const items = asArray((block.data || {}).items);
    const html = `<div class="prismo-evidence-board">${items.map((item) => `
      <div class="prismo-mini-card" data-relevance="${esc(item.relevance || "supporting")}">
        <strong>${esc(item.title || item.id || "Evidencia")}</strong>
        <small>${esc(item.source_type || "runtime")} · ${esc(item.freshness || "current")} · ${esc(item.confidence || "medium")}</small>
        <p>${esc(item.summary || "")}</p>
      </div>`).join("") || `<div class="prismo-empty">Sin evidencia renderizable.</div>`}</div>`;
    return card(block, html);
  }

  function renderMemoryTrace(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-memory-trace">${items.map((item) => `
      <div class="prismo-mini-card">
        <strong>${esc(String(item.type || "memory").replaceAll("_", " "))}</strong>
        <small>${esc(item.confidence || "contextual")}</small>
        <p>${esc(item.summary || "")}</p>
      </div>`).join("")}</div>`);
  }

  function renderAuthorityStrip(block) {
    const data = block.data || {};
    const precedence = asArray(data.precedence);
    return card(block, `<div class="prismo-response-meta">
      <span class="prismo-tag" data-state="ok">${esc(data.winning_source || "PRISMO runtime")}</span>
      ${precedence.slice(0, 4).map((item) => `<span class="prismo-tag">${esc(item)}</span>`).join("")}
    </div><p>${esc(block.summary || "")}</p>`);
  }

  function renderInsightChips(block) {
    const chips = asArray((block.data || {}).chips);
    return card(block, `<div class="prismo-response-meta">${chips.map((chip) => `
      <span class="prismo-theater-chip" data-source="${esc(chip.source || "inferred")}">
        <small>${esc(chip.key || "chip")}</small>${esc(chip.label || chip.value || "")}
      </span>`).join("")}</div>`);
  }

  function renderActionBar(block) {
    const actions = asArray((block.data || {}).actions);
    return card(block, `<div class="prismo-actions-row">${actions.map((action) => `
      <button type="button" class="prismo-secondary-action" data-prismo-action="${esc(action)}">${esc(String(action).replaceAll("_", " "))}</button>`).join("")}</div>`);
  }

  function renderFeedbackDock(block) {
    const states = asArray((block.data || {}).states);
    return card(block, `<div class="prismo-feedback-inline">${states.slice(1).map((state) => `
      <span class="prismo-theater-chip">${esc(String(state).replaceAll("_", " "))}</span>`).join("")}</div>`);
  }

  function renderEvidence(block) {
    const items = asArray((block.data || {}).items);
    const html = `<div class="prismo-mini-grid">${items.map((item) => `
      <div class="prismo-mini-card">
        <strong>${esc(item.title || item.id || "Evidencia")}</strong>
        <small>${esc(item.source_type || item.freshness || "unknown")}</small>
        <p>${esc(item.summary || item.quote || "")}</p>
      </div>`).join("") || `<div class="prismo-empty">Sin evidencia renderizable.</div>`}</div>`;
    return card(block, html);
  }

  function renderAuthority(block) {
    const data = block.data || {};
    const rows = asArray(data.precedence).map((item, index) => `
      <div class="prismo-authority-row">
        <strong>${index + 1}. ${esc(item)}</strong>
        <small>${index === 0 ? "Fuente que manda" : "Precedencia inferior"}</small>
      </div>`).join("");
    const warnings = asArray(data.warnings).map((item) => `<div class="prismo-tag" data-state="warn">${esc(item)}</div>`).join("");
    return card(block, `<div class="prismo-authority-list"><div class="prismo-authority-row"><strong>${esc(data.winning_source || "Authority")}</strong><small>${esc(data.notes || "")}</small></div>${rows}</div><div class="prismo-response-meta">${warnings}</div>`);
  }

  function renderFlow(block) {
    const data = block.data || {};
    if (data.variant === "neural_operations_graph") return renderNeuralGraph(block);
    const nodes = asArray(data.nodes);
    const html = `<div class="prismo-flow">${nodes.map((node, index) => {
      const next = index < nodes.length - 1 ? `<div class="prismo-flow-arrow">→</div>` : "";
      return `<div class="prismo-flow-node" data-status="${esc(node.status || "unknown")}"><strong>${esc(node.label || node.id)}</strong><small>${esc(node.status || "")}</small></div>${next}`;
    }).join("") || `<div class="prismo-empty">Sin nodos.</div>`}</div>`;
    return card(block, html);
  }

  function renderNeuralGraph(block) {
    const data = block.data || {};
    const nodes = asArray(data.nodes).slice(0, 8);
    const zones = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"];
    const html = `<div class="prismo-neural-graph" aria-label="Neural Operations Graph render">
      <div class="prismo-graph-core"><small>Neural Operations Graph</small><strong>PRISMO Core</strong><span>decisión guiada</span></div>
      ${nodes.map((node, index) => `
        <div class="prismo-graph-node" data-zone="${esc(zones[index] || "north")}">
          <strong>${esc(node.label || node.id || "Nodo")}</strong>
          <small>${esc(node.status || node.edge || node.summary || "")}</small>
        </div>`).join("")}
    </div>`;
    return card(block, html);
  }

  function renderImpact(block) {
    const groups = asArray((block.data || {}).groups);
    return card(block, `<div class="prismo-impact-grid">${groups.map((group) => `
      <div class="prismo-impact-node" data-risk="${esc(group.risk || "unknown")}">
        <strong>${esc(group.label || "Nodo")}</strong>
        <small>${esc(group.risk || "unknown")}</small>
        <p>${esc(asArray(group.items).join(" · "))}</p>
      </div>`).join("") || `<div class="prismo-empty">Sin mapa de impacto.</div>`}</div>`);
  }

  function renderRuntime(block) {
    const signals = asArray((block.data || {}).signals);
    return card(block, `<div class="prismo-mini-grid">${signals.map((signal) => `
      <div class="prismo-runtime-signal">
        <strong>${esc(signal.label || "Signal")}</strong>
        <small>${esc(signal.status || "unknown")}</small>
      </div>`).join("")}</div>`);
  }

  function renderTimeline(block) {
    const events = asArray((block.data || {}).events);
    return card(block, `<div class="prismo-timeline">${events.map((event) => `
      <div class="prismo-timeline-row">
        <div class="prismo-timeline-time">${esc(event.time || event.date || "now")}</div>
        <div class="prismo-mini-card"><strong>${esc(event.title || "Evento")}</strong><small>${esc(event.status || event.source || "")}</small><p>${esc(event.summary || "")}</p></div>
      </div>`).join("") || `<div class="prismo-empty">Sin timeline.</div>`}</div>`);
  }

  function renderBrief(block) {
    const sections = asArray((block.data || {}).sections);
    const html = `<div class="prismo-brief-board">${sections.map((section) => `
      <section class="prismo-brief-section">
        <strong>${esc(section.title || "Sección")}</strong>
        <ul>${asArray(section.items).map((item) => `<li>${esc(item)}</li>`).join("")}</ul>
      </section>`).join("") || `<div class="prismo-empty">Sin brief.</div>`}</div>`;
    return card(block, html);
  }

  function renderContext(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-context-grid">${items.map((item) => `
      <div class="prismo-context-item"><strong>${esc(item.label || item.path || "Contexto")}</strong><small>${esc(item.status || item.kind || "")}</small></div>`).join("")}</div>`);
  }

  function renderDiff(block) {
    const columns = asArray((block.data || {}).columns);
    return card(block, `<div class="prismo-mini-grid">${columns.map((col) => `
      <div class="prismo-diff-col"><strong>${esc(col.title || "Columna")}</strong><ul>${asArray(col.items).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></div>`).join("")}</div>`);
  }

  function renderRisk(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-risk-grid">${items.map((item) => `
      <div class="prismo-risk-node" data-level="${esc(item.level || "medium")}"><strong>${esc(item.risk || item.title || "Riesgo")}</strong><small>${esc(item.level || "")}</small><p>${esc(item.mitigation || item.summary || "")}</p></div>`).join("")}</div>`);
  }

  function renderChecklist(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-checklist">${items.map((item) => `
      <div class="prismo-check-item" data-done="${item.done ? "true" : "false"}"><strong>${item.done ? "✓" : "•"} ${esc(item.label || item)}</strong><small>${esc(item.status || "")}</small></div>`).join("")}</div>`);
  }

  function renderChart(block) {
    const spec = block.data || {};
    const labels = (spec.xAxis && spec.xAxis.data) || asArray(spec.labels);
    const series = asArray(spec.series);
    const values = series[0] && Array.isArray(series[0].data) ? series[0].data.map(Number).filter(Number.isFinite) : [];
    const max = Math.max(1, ...values);
    const html = `<div class="prismo-chart-bars">${values.map((value, index) => `
      <div class="prismo-chart-row">
        <small>${esc(labels[index] || `Item ${index + 1}`)}</small>
        <div class="prismo-chart-track"><span style="--w:${Math.max(4, Math.round((value / max) * 100))}%"></span></div>
        <strong>${esc(value)}</strong>
      </div>`).join("") || `<div class="prismo-empty">Chart spec sin serie simple renderizable.</div>`}</div>`;
    return card(block, html);
  }

  function renderBlock(block) {
    if (!block || !ALLOWED.has(block.type)) return blockedCard();
    switch (block.type) {
      case "hero_response": return renderHero(block);
      case "executive_brief": return renderBrief({ ...block, data: { sections: ((block.data || {}).sections || []) } });
      case "next_best_action": return renderNextAction(block);
      case "protocol_ladder": return renderProtocolLadder(block);
      case "procedural_steps":
      case "procedural_recipe": return renderProcedural(block);
      case "evidence_board": return renderEvidenceBoard(block);
      case "comparison_board": return renderDiff({ ...block, data: { columns: ((block.data || {}).columns || []) } });
      case "memory_trace": return renderMemoryTrace(block);
      case "authority_strip": return renderAuthorityStrip(block);
      case "context_cards": return renderContext({ ...block, data: { items: ((block.data || {}).items || []) } });
      case "insight_chips": return renderInsightChips(block);
      case "technical_drawer": return card(block, `<p>${esc(block.summary || "Open technical detail for full trace.")}</p>`);
      case "action_bar": return renderActionBar(block);
      case "error_recovery": return renderDirect({ ...block, data: { answer: block.summary || block.message || "" } });
      case "loading_state": return card(block, `<p>${esc(block.summary || "Reading memory, checking evidence, building render plan.")}</p>`);
      case "feedback_dock": return renderFeedbackDock(block);
      case "direct_answer_card": return renderDirect(block);
      case "evidence_cards": return renderEvidence(block);
      case "authority_map": return renderAuthority(block);
      case "flow_diagram": return renderFlow(block);
      case "impact_map": return renderImpact(block);
      case "runtime_map": return renderRuntime(block);
      case "timeline": return renderTimeline(block);
      case "improvement_brief_board": return renderBrief(block);
      case "context_pack_explorer": return renderContext(block);
      case "diff_view": return renderDiff(block);
      case "risk_matrix": return renderRisk(block);
      case "checklist": return renderChecklist(block);
      case "chart_spec": return renderChart(block);
      default: return blockedCard();
    }
  }

  window.PRISMO_RENDERERS = {
    esc,
    renderBlock,
    blockedCard
  };
})();
