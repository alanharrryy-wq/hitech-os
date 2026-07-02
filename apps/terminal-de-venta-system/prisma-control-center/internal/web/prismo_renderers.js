(function () {
  "use strict";

  const BLOCKED_TEXT = "Bloque visual bloqueado porque no cumplió las reglas de seguridad.";
  const ALLOWED = new Set([
    "hero_response", "executive_brief", "next_best_action", "protocol_ladder",
    "procedural_steps", "procedural_recipe", "evidence_board", "evidence_cards",
    "risk_matrix", "timeline", "flow_diagram", "comparison_board", "memory_trace",
    "authority_strip", "context_cards", "insight_chips", "technical_drawer",
    "action_bar", "error_recovery", "loading_state", "feedback_dock",
    "direct_answer_card", "authority_map", "impact_map", "runtime_map",
    "improvement_brief_board", "context_pack_explorer", "diff_view", "checklist",
    "chart_spec", "surface_matrix", "table_view", "route_map", "dependency_graph", "layer_map"
  ]);

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
    }[ch]));
  }

  function asArray(value) { return Array.isArray(value) ? value : []; }
  function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  function num(value) { const n = Number(value); return Number.isFinite(n) ? n : 0; }

  function card(block, body, extraClass = "") {
    const node = document.createElement("article");
    node.className = `prismo-render-card ${extraClass}`.trim();
    node.dataset.type = block.type || "blocked";
    node.dataset.layout = block.layout || "half";
    node.dataset.visualRole = block.visual_role || block.visualRole || "support";
    node.innerHTML = `<div class="prismo-render-title"><h4>${esc(block.title || "PRISMO")}</h4>${block.description ? `<p>${esc(block.description)}</p>` : ""}</div>`;
    if (typeof body === "string") node.insertAdjacentHTML("beforeend", body);
    else if (body) node.appendChild(body);
    return node;
  }

  function blockedCard() {
    return card({ title: "Bloque visual bloqueado", type: "direct_answer_card", layout: "full" }, `<p>${BLOCKED_TEXT}</p>`);
  }

  function renderDirect(block) {
    const data = block.data || {};
    return card(block, `<p class="prismo-answer">${esc(data.answer || block.summary || block.description || "")}</p>`);
  }

  function renderHero(block) {
    const data = block.data || {};
    const interpretation = data.interpretation || {};
    const chips = asArray(interpretation.chips).map((chip) => `
      <span class="prismo-theater-chip" data-source="${esc(chip.source || "inferred")}">${esc(chip.label || chip.value || "")}</span>`).join("");
    return card(block, `<p class="prismo-answer">${esc(data.answer || block.summary || block.message || "")}</p><div class="prismo-response-meta">${chips}</div>`);
  }

  function renderNextAction(block) {
    const data = block.data || {};
    return card(block, `
      <div class="prismo-safe-step"><strong>${esc(data.action || block.title || "Next action")}</strong><br>${esc(block.summary || data.impact || "")}</div>
      <div class="prismo-response-meta"><span class="prismo-tag" data-state="ok">review impact</span><span class="prismo-tag">read-only</span></div>`);
  }

  function renderProtocolLadder(block) {
    const protocols = asArray((block.data || {}).protocols);
    return card(block, `<div class="prismo-ranked-ladder">${protocols.map((item, index) => `
      <div class="prismo-ladder-step"><small>${esc(String(Math.round(Number(item.score || 0) * 100)))}%</small><strong>${esc(item.label || item.id || `Protocol ${index + 1}`)}</strong><p>${esc(item.reason || "")}</p></div>`).join("") || `<div class="prismo-empty">Sin protocolo rankeado.</div>`}</div>`);
  }

  function renderProcedural(block) {
    const steps = asArray((block.data || {}).steps || (block.data || {}).items);
    return card(block, `<div class="prismo-checklist">${steps.map((item, index) => `
      <div class="prismo-check-item" data-done="${esc(item.status || "ready")}"><strong>${index + 1}. ${esc(item.label || item.title || item)}</strong><small>${esc(item.status || "ready")}</small></div>`).join("") || `<div class="prismo-empty">Sin pasos procedurales.</div>`}</div>`);
  }

  function renderEvidenceBoard(block) {
    const items = asArray((block.data || {}).items);
    const html = `<div class="prismo-evidence-board">${items.map((item) => `
      <div class="prismo-mini-card" data-relevance="${esc(item.relevance || "supporting")}"><strong>${esc(item.title || item.id || "Evidencia")}</strong><small>${esc(item.source_type || "runtime")} · ${esc(item.freshness || "current")} · ${esc(item.confidence || "medium")}</small><p>${esc(item.summary || "")}</p></div>`).join("") || `<div class="prismo-empty">Sin evidencia renderizable.</div>`}</div>`;
    return card(block, html);
  }

  function renderMemoryTrace(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-memory-trace">${items.map((item) => `
      <div class="prismo-mini-card"><strong>${esc(String(item.type || "memory").replaceAll("_", " "))}</strong><small>${esc(item.confidence || "contextual")}</small><p>${esc(item.summary || "")}</p></div>`).join("")}</div>`);
  }

  function renderAuthorityStrip(block) {
    const data = block.data || {};
    const precedence = asArray(data.precedence);
    return card(block, `<div class="prismo-response-meta"><span class="prismo-tag" data-state="ok">${esc(data.winning_source || "PRISMO runtime")}</span>${precedence.slice(0, 4).map((item) => `<span class="prismo-tag">${esc(item)}</span>`).join("")}</div><p>${esc(block.summary || "")}</p>`);
  }

  function renderInsightChips(block) {
    const chips = asArray((block.data || {}).chips);
    return card(block, `<div class="prismo-response-meta">${chips.map((chip) => `<span class="prismo-theater-chip" data-source="${esc(chip.source || "inferred")}"><small>${esc(chip.key || "chip")}</small>${esc(chip.label || chip.value || "")}</span>`).join("")}</div>`);
  }

  function renderActionBar(block) {
    const actions = asArray((block.data || {}).actions);
    return card(block, `<div class="prismo-actions-row">${actions.map((action) => `<button type="button" class="prismo-secondary-action" data-prismo-action="${esc(action)}">${esc(String(action).replaceAll("_", " "))}</button>`).join("")}</div>`);
  }

  function renderFeedbackDock(block) {
    const states = asArray((block.data || {}).states);
    return card(block, `<div class="prismo-feedback-inline">${states.slice(1).map((state) => `<span class="prismo-theater-chip">${esc(String(state).replaceAll("_", " "))}</span>`).join("")}</div>`);
  }

  function renderEvidence(block) {
    const items = asArray((block.data || {}).items);
    const html = `<div class="prismo-mini-grid">${items.map((item) => `<div class="prismo-mini-card"><strong>${esc(item.title || item.id || "Evidencia")}</strong><small>${esc(item.source_type || item.freshness || "unknown")}</small><p>${esc(item.summary || item.quote || "")}</p></div>`).join("") || `<div class="prismo-empty">Sin evidencia renderizable.</div>`}</div>`;
    return card(block, html);
  }

  function renderAuthority(block) {
    const data = block.data || {};
    const rows = asArray(data.precedence).map((item, index) => `<div class="prismo-authority-row"><strong>${index + 1}. ${esc(item)}</strong><small>${index === 0 ? "Fuente que manda" : "Precedencia inferior"}</small></div>`).join("");
    const warnings = asArray(data.warnings).map((item) => `<div class="prismo-tag" data-state="warn">${esc(item)}</div>`).join("");
    return card(block, `<div class="prismo-authority-list"><div class="prismo-authority-row"><strong>${esc(data.winning_source || "Authority")}</strong><small>${esc(data.notes || "")}</small></div>${rows}</div><div class="prismo-response-meta">${warnings}</div>`);
  }

  function renderFlow(block) {
    const data = block.data || {};
    if (data.variant === "neural_operations_graph") return renderNeuralGraph(block);
    const nodes = asArray(data.nodes || data.items || data.rows);
    const html = `<div class="prismo-flow">${nodes.map((node, index) => {
      const next = index < nodes.length - 1 ? `<div class="prismo-flow-arrow">→</div>` : "";
      return `<div class="prismo-flow-node" data-status="${esc(node.status || "unknown")}"><strong>${esc(node.label || node.id || node.path || "Nodo")}</strong><small>${esc(node.summary || node.status || node.kind || "")}</small></div>${next}`;
    }).join("") || `<div class="prismo-empty">Sin nodos.</div>`}</div>`;
    return card(block, html);
  }

  function renderNeuralGraph(block) {
    const data = block.data || {};
    const nodes = asArray(data.nodes).slice(0, 8);
    const zones = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"];
    const html = `<div class="prismo-neural-graph prismo-neural-graph-card"><div class="prismo-graph-core"><small>${esc(data.core_label || "PRISMO")}</small><strong>${esc(data.core_title || "Core")}</strong><span>${esc(data.core_state || "read-only")}</span></div>${nodes.map((node, index) => `<div class="prismo-graph-node" data-zone="${zones[index % zones.length]}"><strong>${esc(node.label || node.id)}</strong><small>${esc(node.status || node.kind || "")}</small></div>`).join("")}</div>`;
    return card(block, html);
  }

  function renderImpact(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-impact-map">${items.map((item) => `<div class="prismo-impact-node" data-impact="${esc(item.impact || "medium")}"><strong>${esc(item.surface || item.label || "Surface")}</strong><small>${esc(item.impact || "medium")}</small><p>${esc(item.reason || item.summary || "")}</p></div>`).join("") || `<div class="prismo-empty">Sin impacto calculado.</div>`}</div>`);
  }

  function renderRuntime(block) {
    const signals = asArray((block.data || {}).signals);
    return card(block, `<div class="prismo-mini-grid">${signals.map((signal) => `<div class="prismo-runtime-signal"><strong>${esc(signal.label || "Signal")}</strong><small>${esc(signal.status || "unknown")}</small></div>`).join("")}</div>`);
  }

  function renderTimeline(block) {
    const events = asArray((block.data || {}).events);
    return card(block, `<div class="prismo-timeline">${events.map((event) => `<div class="prismo-timeline-row"><div class="prismo-timeline-time">${esc(event.time || event.date || "now")}</div><div class="prismo-mini-card"><strong>${esc(event.title || "Evento")}</strong><small>${esc(event.status || event.source || "")}</small><p>${esc(event.summary || "")}</p></div></div>`).join("") || `<div class="prismo-empty">Sin timeline.</div>`}</div>`);
  }

  function renderBrief(block) {
    const sections = asArray((block.data || {}).sections);
    const html = `<div class="prismo-brief-board">${sections.map((section) => `<section class="prismo-brief-section"><strong>${esc(section.title || "Sección")}</strong><ul>${asArray(section.items).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></section>`).join("") || `<div class="prismo-empty">Sin brief.</div>`}</div>`;
    return card(block, html);
  }

  function renderContext(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-context-grid">${items.map((item) => `<div class="prismo-context-item"><strong>${esc(item.label || item.path || item.entry || "Contexto")}</strong><small>${esc(item.status || item.kind || item.summary || "")}</small></div>`).join("")}</div>`);
  }

  function renderDiff(block) {
    const columns = asArray((block.data || {}).columns);
    return card(block, `<div class="prismo-mini-grid">${columns.map((col) => `<div class="prismo-diff-col"><strong>${esc(col.title || "Columna")}</strong><ul>${asArray(col.items).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></div>`).join("")}</div>`);
  }

  function renderRisk(block) {
    const items = asArray((block.data || {}).items);
    return card(block, `<div class="prismo-risk-grid">${items.map((item) => `<div class="prismo-risk-node" data-level="${esc(item.level || "medium")}"><strong>${esc(item.risk || item.title || "Riesgo")}</strong><small>${esc(item.level || "")}</small><p>${esc(item.mitigation || item.summary || "")}</p></div>`).join("")}</div>`);
  }

  function renderChecklist(block) {
    const items = asArray((block.data || {}).items || (block.data || {}).steps);
    return card(block, `<div class="prismo-checklist">${items.map((item) => `<div class="prismo-check-item" data-done="${item.done ? "true" : "false"}"><strong>${item.done ? "✓" : "•"} ${esc(item.label || item.title || item)}</strong><small>${esc(item.status || "")}</small></div>`).join("")}</div>`);
  }

  function normalizeChartSpec(spec) {
    spec = spec && typeof spec === "object" ? spec : {};
    const meta = spec.meta || {};
    const sourceData = asArray(spec.data);
    const xKey = spec.xKey || (spec.xAxis && spec.xAxis.key) || spec.nameKey || "label";
    let rawLabels = [];
    if (spec.xAxis && Array.isArray(spec.xAxis.data)) rawLabels = spec.xAxis.data;
    else if (Array.isArray(spec.labels)) rawLabels = spec.labels;
    else if (sourceData.length && xKey) rawLabels = sourceData.map((row, index) => row && row[xKey] !== undefined ? row[xKey] : `Item ${index + 1}`);

    const series = asArray(spec.series).map((item, idx) => {
      const dataKey = item.dataKey || item.key || item.name || `series_${idx + 1}`;
      const values = Array.isArray(item.data)
        ? item.data.map(num)
        : sourceData.map((row) => num(row && row[dataKey]));
      return {
        label: item.label || item.name || dataKey,
        dataKey,
        values,
        valuePrefix: item.valuePrefix || "",
        valueSuffix: item.valueSuffix || ""
      };
    }).filter((item) => item.values.length);

    const labels = rawLabels.length
      ? rawLabels.map((x, i) => String(x || `Item ${i + 1}`))
      : (series[0] ? series[0].values.map((_v, i) => `Item ${i + 1}`) : []);

    return {
      chartType: String(spec.chartType || spec.type || "bar").toLowerCase(),
      title: meta.title || spec.title || "Gráfico PRISMO",
      description: meta.description || spec.description || "Datos estructurados renderizados por PRISMO.",
      footer: meta.footer || spec.footer || "",
      labels,
      series,
      layout: spec.layout || "",
      nameKey: spec.nameKey,
      valueKey: spec.valueKey,
      data: sourceData
    };
  }

  function renderSvgBars(chart) {
    const labels = chart.labels.slice(0, 10);
    const series = chart.series.slice(0, 4);
    if (!labels.length || !series.length) return "";
    const width = 920;
    const rowH = 48;
    const top = 30;
    const left = 150;
    const right = 46;
    const barGap = 4;
    const innerW = width - left - right;
    const height = top + labels.length * rowH + 40;
    const max = Math.max(1, ...series.flatMap((s) => s.values.slice(0, labels.length)));
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => Math.round(max * t));
    const grid = ticks.map((value) => {
      const x = left + (value / max) * innerW;
      return `<line x1="${x}" x2="${x}" y1="${top - 10}" y2="${height - 28}" class="prismo-svg-grid"/><text x="${x}" y="${height - 10}" class="prismo-svg-tick">${esc(value)}</text>`;
    }).join("");
    const rows = labels.map((label, idx) => {
      const yBase = top + idx * rowH;
      const barH = Math.max(8, (rowH - 12) / Math.max(1, series.length));
      const bars = series.map((s, sidx) => {
        const value = num(s.values[idx]);
        const w = clamp((value / max) * innerW, value > 0 ? 3 : 0, innerW);
        const y = yBase + 7 + sidx * (barH + barGap);
        return `<rect x="${left}" y="${y}" width="${w}" height="${barH}" rx="7" class="prismo-svg-bar prismo-svg-series-${sidx}"/><text x="${left + w + 8}" y="${y + barH - 2}" class="prismo-svg-value">${esc(`${s.valuePrefix}${value}${s.valueSuffix}`)}</text>`;
      }).join("");
      return `<g><text x="18" y="${yBase + rowH / 2 + 5}" class="prismo-svg-label">${esc(label)}</text>${bars}</g>`;
    }).join("");
    const legend = series.map((s, idx) => `<span><i class="prismo-legend-dot prismo-svg-series-${idx}"></i>${esc(s.label)}</span>`).join("");
    return `<div class="prismo-svg-chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(chart.title)}">${grid}${rows}</svg><div class="prismo-chart-legend">${legend}</div></div>`;
  }

  function renderSvgLine(chart) {
    const labels = chart.labels.slice(0, 14);
    const series = chart.series.slice(0, 3);
    if (!labels.length || !series.length) return "";
    const width = 920, height = 340, left = 68, right = 28, top = 28, bottom = 52;
    const innerW = width - left - right, innerH = height - top - bottom;
    const values = series.flatMap((s) => s.values.slice(0, labels.length));
    const max = Math.max(1, ...values), min = Math.min(0, ...values);
    const xFor = (i) => left + (labels.length <= 1 ? 0 : (i / (labels.length - 1)) * innerW);
    const yFor = (v) => top + innerH - ((v - min) / Math.max(1, max - min)) * innerH;
    const grid = [0, .25, .5, .75, 1].map((t) => {
      const y = top + innerH * t;
      const val = Math.round(max - (max - min) * t);
      return `<line x1="${left}" x2="${width - right}" y1="${y}" y2="${y}" class="prismo-svg-grid"/><text x="18" y="${y + 4}" class="prismo-svg-tick">${esc(val)}</text>`;
    }).join("");
    const lines = series.map((s, sidx) => {
      const points = s.values.slice(0, labels.length).map((v, i) => `${xFor(i)},${yFor(num(v))}`).join(" ");
      const dots = s.values.slice(0, labels.length).map((v, i) => `<circle cx="${xFor(i)}" cy="${yFor(num(v))}" r="4" class="prismo-svg-dot prismo-svg-series-${sidx}"/>`).join("");
      return `<polyline points="${points}" class="prismo-svg-line prismo-svg-series-${sidx}"/>${dots}`;
    }).join("");
    const axis = labels.map((label, i) => `<text x="${xFor(i)}" y="${height - 18}" class="prismo-svg-tick prismo-svg-x">${esc(label)}</text>`).join("");
    const legend = series.map((s, idx) => `<span><i class="prismo-legend-dot prismo-svg-series-${idx}"></i>${esc(s.label)}</span>`).join("");
    return `<div class="prismo-svg-chart"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(chart.title)}">${grid}${lines}${axis}</svg><div class="prismo-chart-legend">${legend}</div></div>`;
  }

  function renderChart(block) {
    const chart = normalizeChartSpec(block.data || {});
    let visual = "";
    if (chart.chartType === "line") visual = renderSvgLine(chart);
    else visual = renderSvgBars(chart);
    if (!visual) {
      visual = `<div class="prismo-empty">Chart spec sin datos renderizables.</div>`;
    }
    const footer = chart.footer ? `<p class="prismo-chart-footer">${esc(chart.footer)}</p>` : "";
    return card(block, `<div class="prismo-chart-shell"><div class="prismo-chart-copy"><strong>${esc(chart.title)}</strong><small>${esc(chart.description)}</small></div>${visual}${footer}</div>`, "prismo-chart-card");
  }

  function renderTable(block) {
    const data = block.data || {};
    const rows = asArray(data.rows);
    const columns = asArray(data.columns).length ? asArray(data.columns) : Object.keys(rows[0] || {});
    const header = columns.map((col) => `<th>${esc(String(col).replaceAll("_", " "))}</th>`).join("");
    const body = rows.map((row) => `<tr>${columns.map((col) => `<td>${esc(row && row[col] !== undefined ? row[col] : "")}</td>`).join("")}</tr>`).join("");
    return card(block, `<div class="prismo-table-scroll"><table class="prismo-data-table"><thead><tr>${header}</tr></thead><tbody>${body || `<tr><td>Sin filas renderizables.</td></tr>`}</tbody></table></div>`);
  }

  function renderSurfaceMatrix(block) {
    const rows = asArray((block.data || {}).rows);
    const html = `<div class="prismo-surface-matrix">${rows.map((row) => `<div class="prismo-surface-row"><strong>${esc(row.label || row.id || "Surface")}</strong><span><b>${esc(row.routes || 0)}</b> rutas</span><span><b>${esc(row.components || 0)}</b> comps</span><span><b>${esc(row.css || 0)}</b> css</span><small>${esc(row.files || 0)} files</small></div>`).join("") || `<div class="prismo-empty">Sin superficies.</div>`}</div>`;
    return card(block, html);
  }

  function renderGraphLike(block) { return renderFlow(block); }

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
      case "table_view": return renderTable(block);
      case "surface_matrix": return renderSurfaceMatrix(block);
      case "route_map":
      case "dependency_graph":
      case "layer_map": return renderGraphLike(block);
      default: return blockedCard();
    }
  }

  window.PRISMO_RENDERERS = { esc, renderBlock, blockedCard };
})();
