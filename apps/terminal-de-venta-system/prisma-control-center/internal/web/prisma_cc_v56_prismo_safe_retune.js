(function () {
  "use strict";

  var VERSION = "v5.6-prismo-safe-retune";
  var TARGET_COPY = "Pregunta. PRISMO responderá.";
  var OLD_COPY = /PRISMO\s+est[áa]\s+listo[\s\S]*?(?:generar\s+un\s+brief\.?|brief\.?)/i;
  var PROMPT_TITLE = /¿Qué\s+quieres\s+entender,\s*revisar\s+o\s+mejorar\?/i;
  var STATUS_WORDS = ["read-only", "backend bridge", "no mutation", "success", "gemini bridge online", "authority loaded", "html preview off", "live", "online"];
  var SIDE_HEADERS = ["authority map", "evidence deck", "impact map", "runtime signals", "context pack", "ledger"];
  var INTERFACE_LABELS = ["operación", "quality bay", "licencias", "data lifecycle", "prismo"];
  var HIDE_ACTIONS = [
    "ask", "inspect", "improve", "evidence", "brief",
    "revisar contradicción de sync", "generar improvement brief", "detectar stubs peligrosos",
    "comparar current vs legacy", "crear mapa de impacto", "explicar ruta real pc → tablet",
    "explicar ruta real pc -> tablet", "revisar contradiccion de sync"
  ];

  window.PRISMA_CC_V56_SAFE_RETUNE = {
    version: VERSION,
    started: false,
    oldAtmosphereRemoved: 0,
    copyUpdated: 0,
    hiddenActions: 0,
    ledsTagged: 0,
    errors: []
  };

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function norm(s) {
    return (s || "").replace(/\s+/g, " ").trim();
  }

  function normLower(s) {
    return norm(s).toLowerCase();
  }

  function visible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    var r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  }

  function textOf(el) {
    return norm(el && el.textContent || "");
  }

  function safeClosestSurface(el) {
    if (!el) return null;
    return el.closest(".card,.panel,.glass,.commandPanel,.prismo-shell,section,article,form") || el.parentElement;
  }

  function removeOldAtmosphere() {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(
      "#prisma-atmosphere-v55-root,#prisma-atmosphere-v55-scrim,#prisma-atmosphere-v54-root,#prisma-atmosphere-v54-scrim,#prisma-atmosphere-v53-root,#prisma-atmosphere-v53-badge,#prisma-atmosphere-v53-canvas,[id*='atmosphere-v55'],[id*='atmosphere-v54'],[id*='atmosphere-v53']"
    ));
    nodes.forEach(function (node) {
      if (!node || node.id === "prisma-atmosphere-v56-root" || node.id === "prisma-atmosphere-v56-canvas" || node.id === "prisma-atmosphere-v56-scrim") return;
      node.classList.add("prisma-v56-old-atmosphere-hidden");
      node.style.display = "none";
      node.style.visibility = "hidden";
      node.style.opacity = "0";
      window.PRISMA_CC_V56_SAFE_RETUNE.oldAtmosphereRemoved += 1;
    });
  }

  function startAtmosphere() {
    removeOldAtmosphere();

    var old = document.getElementById("prisma-atmosphere-v56-root");
    if (old) old.remove();
    var oldScrim = document.getElementById("prisma-atmosphere-v56-scrim");
    if (oldScrim) oldScrim.remove();

    var root = document.createElement("div");
    root.id = "prisma-atmosphere-v56-root";
    var canvas = document.createElement("canvas");
    canvas.id = "prisma-atmosphere-v56-canvas";
    canvas.setAttribute("data-prisma-atmosphere", "v56-safe-slow-mist");
    root.appendChild(canvas);

    var scrim = document.createElement("div");
    scrim.id = "prisma-atmosphere-v56-scrim";

    document.body.prepend(scrim);
    document.body.prepend(root);

    var ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    var w = 0;
    var h = 0;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var reduced = false;
    try {
      reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (_) {}

    function resize() {
      w = window.innerWidth || document.documentElement.clientWidth || 1280;
      h = window.innerHeight || document.documentElement.clientHeight || 720;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.floor(w * dpr));
      canvas.height = Math.max(1, Math.floor(h * dpr));
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    resize();
    window.addEventListener("resize", resize, { passive: true });

    var mist = [];
    var dust = [];
    var mistCount = reduced ? 3 : 6;
    var dustCount = reduced ? 4 : 10;

    for (var i = 0; i < mistCount; i++) {
      mist.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 260 + Math.random() * 460,
        vx: (-0.007 + Math.random() * 0.014),
        vy: (-0.005 + Math.random() * 0.010),
        a: 0.012 + Math.random() * 0.018,
        phase: Math.random() * Math.PI * 2
      });
    }

    for (var j = 0; j < dustCount; j++) {
      dust.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.7 + Math.random() * 1.5,
        vx: (-0.004 + Math.random() * 0.008),
        vy: (-0.006 + Math.random() * 0.006),
        a: 0.025 + Math.random() * 0.050
      });
    }

    var t0 = performance.now();
    var last = 0;

    function draw(now) {
      var elapsed = (now - t0) / 1000;
      var dt = Math.min(32, now - last || 16) / 16.67;
      last = now;
      ctx.clearRect(0, 0, w, h);

      for (var i = 0; i < mist.length; i++) {
        var m = mist[i];
        if (!reduced) {
          m.x += m.vx * dt;
          m.y += m.vy * dt;
          if (m.x < -m.r) m.x = w + m.r;
          if (m.x > w + m.r) m.x = -m.r;
          if (m.y < -m.r) m.y = h + m.r;
          if (m.y > h + m.r) m.y = -m.r;
        }
        var pulse = 0.86 + Math.sin(elapsed * 0.045 + m.phase) * 0.14;
        var a = m.a * pulse;
        var rx = m.x + Math.sin(elapsed * 0.025 + i) * 8;
        var ry = m.y + Math.cos(elapsed * 0.022 + i) * 6;
        var g = ctx.createRadialGradient(rx, ry, 0, rx, ry, m.r);
        g.addColorStop(0, "rgba(198, 232, 255," + a + ")");
        g.addColorStop(0.40, "rgba(116, 176, 218," + (a * 0.28) + ")");
        g.addColorStop(1, "rgba(116, 176, 218,0)");
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(rx, ry, m.r, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.save();
      ctx.globalCompositeOperation = "screen";
      for (var k = 0; k < dust.length; k++) {
        var p = dust[k];
        if (!reduced) {
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          if (p.x < -8) p.x = w + 8;
          if (p.x > w + 8) p.x = -8;
          if (p.y < -8) p.y = h + 8;
          if (p.y > h + 8) p.y = -8;
        }
        ctx.globalAlpha = p.a * (0.82 + Math.sin(elapsed * 0.07 + k) * 0.14);
        ctx.fillStyle = k % 2 ? "rgba(198,229,255,.62)" : "rgba(148,223,255,.74)";
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      if (!reduced) requestAnimationFrame(draw);
    }

    requestAnimationFrame(draw);
  }

  function walkTextNodes(fn) {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node || !node.nodeValue || !norm(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        var parent = node.parentElement;
        if (!parent || parent.closest("script,style,noscript,svg")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(fn);
  }

  function replaceCopyAndMarkTitle() {
    walkTextNodes(function (node) {
      var value = node.nodeValue;
      var parent = node.parentElement;
      if (!parent) return;

      if (OLD_COPY.test(value) || /Autoridad\s+cargada|Modo\s+seguro\s+activo|Puedes\s+preguntar/i.test(value)) {
        node.nodeValue = TARGET_COPY;
        parent.classList.add("prisma-v56-status-copy");
        window.PRISMA_CC_V56_SAFE_RETUNE.copyUpdated += 1;
        var surface = safeClosestSurface(parent);
        if (surface) surface.classList.add("prisma-v56-status-surface");
        if (parent.children.length === 0) parent.classList.add("prisma-v56-status-flat");
      }

      if (PROMPT_TITLE.test(value)) {
        parent.classList.add("prisma-v56-prompt-title");
      }
    });
  }

  function findComposer() {
    var fields = Array.prototype.slice.call(document.querySelectorAll("textarea,input[type='text'],[contenteditable='true']")).filter(visible);
    if (!fields.length) return null;
    fields.sort(function (a, b) {
      var ar = a.getBoundingClientRect();
      var br = b.getBoundingClientRect();
      return (br.width * br.height) - (ar.width * ar.height);
    });
    var input = fields[0];
    var container = input.closest("form,[class*='composer'],[class*='Composer'],[class*='command'],[class*='Command'],[class*='prompt'],[class*='Prompt']") || input.parentElement;
    if (!container) container = input.parentElement;
    if (container) container.classList.add("prisma-v56-composer");
    return { input: input, container: container };
  }

  function valueOfInput(input) {
    if (!input) return "";
    if (input.matches && input.matches("[contenteditable='true']")) return input.textContent || "";
    return input.value || "";
  }

  function clearInput(input) {
    if (!input) return;
    if (input.matches && input.matches("[contenteditable='true']")) input.textContent = "";
    else input.value = "";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function findButtonByText(root, wanted) {
    var needle = normLower(wanted);
    var buttons = Array.prototype.slice.call((root || document).querySelectorAll("button,a,[role='button']"));
    return buttons.find(function (b) { return normLower(textOf(b)) === needle && !b.classList.contains("prisma-v56-action"); }) || null;
  }

  function hideOldComposerActions(composer) {
    if (!composer || !composer.container) return;
    var buttons = Array.prototype.slice.call(composer.container.querySelectorAll("button,a,[role='button']"));
    buttons.forEach(function (btn) {
      var txt = normLower(textOf(btn));
      if (!txt || txt === "consultar prismo" || txt === "limpiar") return;
      if (HIDE_ACTIONS.indexOf(txt) >= 0) {
        btn.classList.add("prisma-v56-hidden-front-action");
        window.PRISMA_CC_V56_SAFE_RETUNE.hiddenActions += 1;
      }
    });
  }

  function injectActions(composer) {
    if (!composer || !composer.container || !composer.input) return;
    if (composer.container.querySelector(".prisma-v56-action-bar")) return;

    var bar = document.createElement("div");
    bar.className = "prisma-v56-action-bar";

    var consult = document.createElement("button");
    consult.type = "button";
    consult.className = "prisma-v56-action prisma-v56-action-consult";
    consult.textContent = "Consultar PRISMO";
    consult.addEventListener("click", function () {
      var existing = findButtonByText(document, "Consultar PRISMO");
      if (existing) existing.click();
      else {
        var form = composer.input.closest("form");
        if (form && form.requestSubmit) form.requestSubmit();
        else composer.input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true, ctrlKey: true }));
      }
    });

    var clear = document.createElement("button");
    clear.type = "button";
    clear.className = "prisma-v56-action prisma-v56-action-clear";
    clear.textContent = "Limpiar";
    clear.addEventListener("click", function () {
      var existing = findButtonByText(document, "Limpiar");
      if (existing) existing.click();
      clearInput(composer.input);
      composer.input.focus && composer.input.focus();
    });

    bar.appendChild(consult);
    bar.appendChild(clear);

    var field = composer.input;
    var target = field.closest("label,div") || field;
    if (target && target.parentNode) target.parentNode.insertBefore(bar, target.nextSibling);
    else composer.container.appendChild(bar);

    function syncTyping() {
      var has = norm(valueOfInput(composer.input)).length > 0;
      composer.container.classList.toggle("prisma-v56-typing", has || document.activeElement === composer.input);
    }

    composer.input.addEventListener("input", syncTyping, { passive: true });
    composer.input.addEventListener("focus", syncTyping, { passive: true });
    composer.input.addEventListener("blur", function () { setTimeout(syncTyping, 120); }, { passive: true });
    syncTyping();
  }

  function tagLeds() {
    var candidates = Array.prototype.slice.call(document.querySelectorAll("body *")).filter(function (el) {
      if (!el || el.children.length > 6 || !visible(el)) return false;
      var t = normLower(textOf(el));
      if (!t || t.length > 80) return false;
      return STATUS_WORDS.some(function (word) { return t.indexOf(word) >= 0; });
    });

    candidates.forEach(function (el) {
      if (el.classList.contains("prisma-v56-led-chip")) return;
      el.classList.add("prisma-v56-led-chip");
      var t = normLower(textOf(el));
      var dot = document.createElement("span");
      dot.className = "prisma-v56-led-dot " + ((t.indexOf("backend") >= 0 || t.indexOf("no mutation") >= 0 || t.indexOf("html preview") >= 0) ? "is-blue" : "is-green");
      dot.setAttribute("aria-hidden", "true");
      el.insertBefore(dot, el.firstChild);
      window.PRISMA_CC_V56_SAFE_RETUNE.ledsTagged += 1;
    });
  }

  function commonAncestor(nodes) {
    if (!nodes.length) return null;
    var path = [];
    var n = nodes[0];
    while (n) { path.push(n); n = n.parentElement; }
    for (var i = 0; i < path.length; i++) {
      var candidate = path[i];
      if (nodes.every(function (node) { return candidate.contains(node); })) return candidate;
    }
    return null;
  }

  function tagInterfaceSelector() {
    var controls = Array.prototype.slice.call(document.querySelectorAll("button,a,[role='button']")).filter(function (el) {
      var t = normLower(textOf(el));
      return INTERFACE_LABELS.indexOf(t) >= 0;
    });
    if (controls.length < 3) return;
    controls.forEach(function (el) { el.classList.add("prisma-v56-interface-pill"); });
    var ancestor = commonAncestor(controls);
    if (ancestor && ancestor !== document.body) ancestor.classList.add("prisma-v56-interface-selector");
  }

  function tagSidePanels() {
    walkTextNodes(function (node) {
      var txt = normLower(node.nodeValue);
      if (SIDE_HEADERS.indexOf(txt) < 0) return;
      var surface = safeClosestSurface(node.parentElement);
      if (surface) surface.classList.add("prisma-v56-sidepanel");
    });
  }

  function applyRetune() {
    try {
      document.body.classList.add("prisma-v56-active");
      removeOldAtmosphere();
      startAtmosphere();
      replaceCopyAndMarkTitle();
      var composer = findComposer();
      hideOldComposerActions(composer);
      injectActions(composer);
      tagLeds();
      tagInterfaceSelector();
      tagSidePanels();
      window.PRISMA_CC_V56_SAFE_RETUNE.started = true;
    } catch (err) {
      window.PRISMA_CC_V56_SAFE_RETUNE.errors.push(err && (err.stack || err.message) || String(err));
      console.error("[PRISMA V5.6 Safe Retune]", err);
    }

    // One gentle second pass after UI hydration, without creating duplicates.
    setTimeout(function () {
      try {
        removeOldAtmosphere();
        replaceCopyAndMarkTitle();
        var composer = findComposer();
        hideOldComposerActions(composer);
        injectActions(composer);
        tagLeds();
        tagInterfaceSelector();
        tagSidePanels();
      } catch (err) {
        window.PRISMA_CC_V56_SAFE_RETUNE.errors.push(err && (err.stack || err.message) || String(err));
      }
    }, 900);
  }

  ready(applyRetune);
})();
