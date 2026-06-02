/* PRISMA CC V77 - Origin State Lock - Fix3 stable
   Fix3 decision:
   - keep only deterministic interface routing/state parity;
   - no window scroll forcing;
   - no fixed global topbar;
   - no visual restyling.
*/
(function () {
  "use strict";

  var VERSION = "prisma-cc-v77-origin-state-lock-fix3";
  var STORE = "prisma-control-center-interface-v1";
  var VALID = ["operation", "quality", "license", "lifecycle", "prismo"];
  var SURFACES = {
    quality: "#qualityBaySurface",
    license: ".licenseOpsSurface",
    lifecycle: ".lifecycleSurface",
    prismo: "#prismoConsoleSurface"
  };

  window.PRISMA_CC_V77_ORIGIN_STATE_LOCK = {
    version: VERSION,
    applied: false,
    lastInterface: null,
    lastReason: null,
    errors: []
  };

  function qs(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function one(selector, root) {
    return (root || document).querySelector(selector);
  }

  function clean(value) {
    var raw = String(value || "").trim().replace(/^#/, "").replace(/^\/+/, "").replace(/\/+$/, "").toLowerCase();
    if (raw === "licencias") raw = "license";
    if (raw === "operacion" || raw === "operaciÃ³n") raw = "operation";
    if (raw === "data-lifecycle" || raw === "data_lifecycle" || raw === "data lifecycle") raw = "lifecycle";
    if (raw === "quality-bay" || raw === "quality bay") raw = "quality";
    return VALID.indexOf(raw) >= 0 ? raw : "";
  }

  function stored() {
    try { return clean(localStorage.getItem(STORE)); } catch (_) { return ""; }
  }

  function persist(name) {
    try { localStorage.setItem(STORE, name); } catch (_) {}
  }

  function hashInterface() {
    return clean(location.hash || "");
  }

  function pathInterface() {
    return clean(location.pathname || "");
  }

  function explicitInitial() {
    return hashInterface() || pathInterface() || stored() || "operation";
  }

  function setHidden(node, hidden) {
    if (!node) return;
    try {
      if (hidden) node.setAttribute("hidden", "");
      else node.removeAttribute("hidden");
    } catch (_) {}
  }

  function setButtonState(name) {
    qs("[data-prisma-interface-target]").forEach(function (button) {
      var target = clean(button.getAttribute("data-prisma-interface-target"));
      var active = target === name;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
  }

  function setSurfaceVisibility(name) {
    Object.keys(SURFACES).forEach(function (key) {
      qs(SURFACES[key]).forEach(function (node) {
        var active = key === name;
        setHidden(node, !active);
        if (active) {
          node.style.removeProperty("display");
          node.style.removeProperty("visibility");
          node.style.removeProperty("opacity");
        }
      });
    });

    if (name === "operation") {
      Object.keys(SURFACES).forEach(function (key) {
        qs(SURFACES[key]).forEach(function (node) { setHidden(node, true); });
      });
    }
  }

  function setHeaderFor(name) {
    var title = one(".titles h1");
    var subtitle = one("#subtitle");
    var chips = qs(".chips .chip");

    if (name === "prismo") {
      if (title) title.textContent = "PRISMO";
      if (subtitle) subtitle.textContent = "GEMINI COMMAND NEXUS";
      if (chips[0]) chips[0].innerHTML = '<span class="dot"></span>PRISMO ONLINE';
      if (chips[1]) chips[1].textContent = "Authority";
      if (chips[2]) chips[2].textContent = "No mutation";
    } else if (name === "operation") {
      if (title && !title.textContent.trim()) title.textContent = "CONTROL CENTER PRISMA";
      if (subtitle && !subtitle.textContent.trim()) subtitle.textContent = "CONTROL CENTER PRISMA";
    }
  }

  function activate(name, reason, options) {
    name = clean(name) || "operation";
    document.body.dataset.prismaInterface = name;
    document.body.dataset.prismaInterfaceLock = VERSION;
    persist(name);
    setButtonState(name);
    setSurfaceVisibility(name);
    setHeaderFor(name);

    window.PRISMA_CC_V77_ORIGIN_STATE_LOCK.applied = true;
    window.PRISMA_CC_V77_ORIGIN_STATE_LOCK.lastInterface = name;
    window.PRISMA_CC_V77_ORIGIN_STATE_LOCK.lastReason = reason || "unknown";

    if (options && options.hash) {
      try {
        history.replaceState({ prismaInterface: name, source: VERSION }, "", name === "operation" ? location.pathname : "#" + name);
      } catch (_) {}
    }
  }

  function bindClicks() {
    document.addEventListener("click", function (event) {
      var button = event.target && event.target.closest ? event.target.closest("[data-prisma-interface-target]") : null;
      if (!button) return;
      var target = clean(button.getAttribute("data-prisma-interface-target"));
      if (!target) return;
      event.preventDefault();
      event.stopPropagation();
      if (event.stopImmediatePropagation) event.stopImmediatePropagation();
      activate(target, "click", { hash: target !== "operation" });
    }, true);
  }

  function boot() {
    try {
      bindClicks();
      activate(explicitInitial(), "boot", { hash: false });
      window.addEventListener("hashchange", function () {
        var next = hashInterface();
        if (next) activate(next, "hashchange", { hash: false });
      });
      window.addEventListener("pageshow", function () {
        var next = hashInterface() || stored() || document.body.dataset.prismaInterface || "operation";
        activate(next, "pageshow", { hash: false });
      });
    } catch (err) {
      window.PRISMA_CC_V77_ORIGIN_STATE_LOCK.errors.push(String(err && err.stack || err));
      console.error("[PRISMA V77]", err);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();

  window.PRISMA_CC_V77_ORIGIN_STATE_LOCK.activate = activate;
})();
