(function () {
  "use strict";

  var VERSION = "PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE";
  var COPY_TEXT = "Pregunta. PRISMO responderá.";
  var REQUIRED_IDS = [
    "prismoConsoleSurface",
    "prismo-console",
    "prismoComposer",
    "prismoPrompt",
    "prismoSendButton",
    "prismoClearButton",
    "prismoBridgeStatus",
    "prismoAuthorityStatus",
    "prismoSafetyStatus",
    "prismoHtmlStatus"
  ];

  window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE = {
    version: VERSION,
    started: false,
    movedButtons: 0,
    duplicateBarsTagged: 0,
    hiddenCopy: 0,
    missing: [],
    warnings: [],
    errors: []
  };

  function norm(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function byId(id) {
    return document.getElementById(id);
  }

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, { once: true });
    else fn();
  }

  function verifyRequired() {
    var missing = [];
    REQUIRED_IDS.forEach(function (id) {
      if (!byId(id)) missing.push(id);
    });
    window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.missing = missing;
    return missing.length === 0;
  }

  function suppressV56DuplicateActionBars() {
    var bars = Array.prototype.slice.call(document.querySelectorAll("#prismoComposer .prisma-v56-action-bar"));
    bars.forEach(function (bar) {
      bar.setAttribute("data-prisma-v59-suppressed", "true");
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.duplicateBarsTagged += 1;
    });
  }

  function moveExactButtonsOnly() {
    var form = byId("prismoComposer");
    var prompt = byId("prismoPrompt");
    var send = byId("prismoSendButton");
    var clear = byId("prismoClearButton");
    if (!form || !prompt || !send || !clear) return false;

    if (send.tagName !== "BUTTON" || clear.tagName !== "BUTTON") {
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.warnings.push("Send/Clear are not button nodes. No move applied.");
      return false;
    }

    if (norm(send.textContent) !== "Consultar PRISMO" || norm(clear.textContent) !== "Limpiar") {
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.warnings.push("Button text mismatch. No move applied.");
      return false;
    }

    var dock = byId("prismaV59PrimaryActions");
    if (!dock) {
      dock = document.createElement("div");
      dock.id = "prismaV59PrimaryActions";
      dock.className = "prismo-actions-row prisma-v59-primary-actions";
      dock.setAttribute("data-prisma-v59", "primary-actions-dock");
      prompt.insertAdjacentElement("afterend", dock);
    }

    if (send.parentElement !== dock) {
      dock.appendChild(send);
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.movedButtons += 1;
    }
    if (clear.parentElement !== dock) {
      dock.appendChild(clear);
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.movedButtons += 1;
    }
    return true;
  }

  function neutralizeExactStatusCopy() {
    var nodes = Array.prototype.slice.call(document.querySelectorAll("#prismoResponseStream .prismo-answer.prisma-v56-status-copy"));
    nodes.forEach(function (node) {
      if (norm(node.textContent) === COPY_TEXT) {
        node.setAttribute("data-prisma-v59-copy-neutralized", "true");
        window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.hiddenCopy += 1;
      }
    });
  }

  function tagRoot() {
    document.documentElement.setAttribute("data-prisma-cc-v59", "selector-safe-frost-evidence");
    var root = byId("prismo-console");
    if (root) root.classList.add("prisma-v59-ready");
  }

  function apply() {
    try {
      tagRoot();
      verifyRequired();
      suppressV56DuplicateActionBars();
      moveExactButtonsOnly();
      neutralizeExactStatusCopy();
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.started = true;
    } catch (err) {
      window.PRISMA_CC_V59_SELECTOR_SAFE_FROST_EVIDENCE.errors.push(err && (err.stack || err.message) || String(err));
      console.error("[" + VERSION + "]", err);
    }
  }

  ready(function () {
    apply();
    setTimeout(apply, 250);
    setTimeout(apply, 950);
    setTimeout(apply, 1800);

    var root = byId("prismoComposer") || document.body;
    if (root && window.MutationObserver) {
      var pending = false;
      var observer = new MutationObserver(function () {
        if (pending) return;
        pending = true;
        setTimeout(function () {
          pending = false;
          apply();
        }, 80);
      });
      observer.observe(root, { childList: true, subtree: true });
      setTimeout(function () { try { observer.disconnect(); } catch (_) {} }, 7000);
    }
  });
})();
