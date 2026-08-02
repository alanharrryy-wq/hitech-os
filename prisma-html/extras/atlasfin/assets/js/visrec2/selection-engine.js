(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});
  const candidateSelector = [
    "[data-visual-component-id]",
    "[data-atlas-item]",
    "[data-demo-id]",
    "button",
    "a.atlas-button",
    "input",
    "select",
    "textarea",
    "table",
    ".atlas-card",
    ".atlas-demo",
    ".atlas-section",
    ".atlas-panel",
    ".atlas-topbar",
    ".atlas-sidebar",
    ".atlas-tabs",
    ".atlas-alert",
    ".atlas-toast",
    ".atlas-dialog",
    ".atlas-drawer",
    ".atlas-nav",
    "nav",
    "form",
  ].join(",");

  const owns = (node) => Boolean(node?.closest?.("[data-visrec2-console]"));

  const classify = (element) => {
    if (!element) return "component";
    const tag = element.tagName?.toLowerCase();
    const role = element.getAttribute?.("role");
    const classes = Array.from(element.classList || []).join(" ").toLowerCase();
    if (tag === "button" || classes.includes("button")) return "button";
    if (
      ["input", "textarea", "select"].includes(tag) ||
      classes.includes("input") ||
      classes.includes("field")
    )
      return "input";
    if (tag === "table" || classes.includes("table")) return "table";
    if (
      tag === "nav" ||
      role === "navigation" ||
      classes.includes("nav") ||
      classes.includes("sidebar") ||
      classes.includes("topbar")
    )
      return "navigation";
    if (
      classes.includes("dialog") ||
      classes.includes("drawer") ||
      classes.includes("overlay") ||
      role === "dialog"
    )
      return "overlay";
    if (classes.includes("card") || classes.includes("demo")) return "card";
    if (classes.includes("section") || classes.includes("panel")) return "panel";
    return "component";
  };

  const selectableFrom = (node) => {
    if (!node || owns(node)) return null;
    const candidate = node.closest?.(candidateSelector);
    return candidate && !owns(candidate) ? candidate : null;
  };

  const inventory = (limit = 500) =>
    Array.from(document.querySelectorAll(candidateSelector))
      .filter((element) => !owns(element) && element.getClientRects().length > 0)
      .slice(0, limit);

  const scopeTarget = (selected, scope, root, body) => {
    if (!selected) return body;
    if (scope === "element") return selected;
    if (scope === "group")
      return (
        selected.closest(
          "[data-atlas-group], .atlas-card, .atlas-demo, form, fieldset"
        ) || selected
      );
    if (scope === "region")
      return (
        selected.closest(
          "[data-visual-recipe-region], .atlas-section, main, section"
        ) || selected
      );
    if (scope === "page")
      return (
        document.querySelector(".atlas-main") ||
        document.querySelector("main") ||
        body
      );
    return root;
  };

  modules["selection-engine"] = Object.freeze({
    candidateSelector,
    owns,
    classify,
    selectableFrom,
    inventory,
    scopeTarget,
  });
})();
