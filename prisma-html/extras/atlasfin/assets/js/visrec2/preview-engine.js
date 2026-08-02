(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});
  const snapshots = new WeakMap();
  let sequence = 0;

  const shadowList = (value) =>
    Array.isArray(value)
      ? value
          .map(
            (row) =>
              `${row.inset ? "inset " : ""}${row.x || 0}px ${row.y || 0}px ${
                row.blur || 0
              }px ${row.spread || 0}px ${row.color || "rgba(0,0,0,.25)"}`
          )
          .join(", ")
      : value || "none";

  const list = (value) =>
    Array.isArray(value)
      ? value
          .map((row) => (typeof row === "string" ? row : row.value || ""))
          .filter(Boolean)
          .join(" ")
      : value || "";

  const cssValue = (value, unit = "") =>
    typeof value === "number" ? `${value}${unit}` : value;

  const propertiesToCss = (properties) => {
    const css = {};
    const mapping = {
      "color.background": ["background-color", ""],
      "color.foreground": ["color", ""],
      "color.border": ["border-color", ""],
      "border.color": ["border-color", ""],
      "border.width": ["border-width", "px"],
      "border.style": ["border-style", ""],
      "border.radius": ["border-radius", "px"],
      "typography.size": ["font-size", "px"],
      "typography.weight": ["font-weight", ""],
      "typography.lineHeight": ["line-height", ""],
      "typography.letterSpacing": ["letter-spacing", "em"],
      "spacing.paddingInline": ["padding-inline", "px"],
      "spacing.paddingBlock": ["padding-block", "px"],
      "spacing.gap": ["gap", "px"],
      "motion.duration": ["transition-duration", "ms"],
      "motion.delay": ["transition-delay", "ms"],
      "motion.easing": ["transition-timing-function", ""],
      "interaction.cursor": ["cursor", ""],
      "interaction.pointerEvents": ["pointer-events", ""],
      "interaction.userSelect": ["user-select", ""],
      "interaction.touchAction": ["touch-action", ""],
    };
    Object.entries(mapping).forEach(([id, [cssName, unit]]) => {
      if (properties[id] !== undefined)
        css[cssName] = cssValue(properties[id], unit);
    });
    if (properties["material.opacity"] !== undefined)
      css.opacity = String(properties["material.opacity"]);
    if (properties["material.blur"] !== undefined) {
      css["backdrop-filter"] = `blur(${properties["material.blur"]}px)`;
      css["-webkit-backdrop-filter"] = `blur(${properties["material.blur"]}px)`;
    }
    if (properties["shadow.base"] !== undefined)
      css["box-shadow"] = shadowList(properties["shadow.base"]);
    if (properties["filter.base"] !== undefined)
      css.filter = list(properties["filter.base"]);
    if (properties["motion.transform"] !== undefined)
      css.transform = list(properties["motion.transform"]);
    return css;
  };

  const apply = (target, compiled, stateId, variantId, locks = new Set()) => {
    if (!target || !compiled?.ok) return;
    clear(target);
    const styleBefore = target.getAttribute("style");
    snapshots.set(target, styleBefore);
    const root = compiled.visualStack.root;
    const properties = {
      ...root.properties,
      ...(root.variantOverrides?.[variantId] || {}),
      ...(root.stateOverrides?.[stateId] || {}),
    };
    const css = propertiesToCss(properties);
    Object.entries(css).forEach(([property, value]) => {
      const canonical = Object.entries(
        compiled.visualStack.root.properties || {}
      ).find(([id]) => modules["property-engine"].canonicalId(id, {}) === id)?.[0];
      if (!locks.has(canonical || property))
        target.style.setProperty(property, String(value));
    });
    sequence += 1;
    target.dataset.visrec2PreviewKey = String(sequence);
    target.dataset.visrec2PreviewState = stateId;
    target.dataset.visrec2Variant = variantId;
    target.classList.add("visrec2-preview-target");
  };

  const clear = (target) => {
    if (!target || !snapshots.has(target)) return;
    const previous = snapshots.get(target);
    if (previous === null) target.removeAttribute("style");
    else target.setAttribute("style", previous);
    snapshots.delete(target);
    target.classList.remove("visrec2-preview-target");
    delete target.dataset.visrec2PreviewKey;
    delete target.dataset.visrec2PreviewState;
    delete target.dataset.visrec2Variant;
  };

  modules["preview-engine"] = Object.freeze({
    apply,
    clear,
    propertiesToCss,
    shadowList,
  });
})();
