(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const get = (registry, surfaceId) =>
    registry?.v2_internal_registries?.adapters?.items?.find(
      (item) => item.surfaceId === surfaceId
    ) ||
    registry?.v2_internal_registries?.adapters?.items?.find(
      (item) => item.surfaceId === "neutral"
    ) ||
    null;

  const adapt = (values, adapter, mode = "adaptive") => {
    const resolved = structuredClone(values || {});
    const adaptations = [];
    const blockingIssues = [];
    const clamp = (propertyId, maximum) => {
      const value = Number(resolved[propertyId]);
      if (!Number.isFinite(value) || maximum === null || maximum === undefined)
        return;
      if (value <= maximum) return;
      if (mode === "exact") {
        blockingIssues.push({
          code: "EXACT_VALUE_UNSUPPORTED",
          propertyId,
          value,
          maximum,
        });
        return;
      }
      adaptations.push({
        propertyId,
        from: value,
        to: maximum,
        reason: "surface-adapter-limit",
      });
      resolved[propertyId] = maximum;
    };
    clamp("material.blur", adapter?.maximumBlur);
    if (
      adapter?.minimumTouchTarget &&
      Number(resolved["geometry.touchTarget"] || 0) <
        adapter.minimumTouchTarget
    ) {
      if (mode === "exact") {
        blockingIssues.push({
          code: "TOUCH_TARGET_BELOW_FLOOR",
          propertyId: "geometry.touchTarget",
          minimum: adapter.minimumTouchTarget,
        });
      } else {
        adaptations.push({
          propertyId: "geometry.touchTarget",
          from: resolved["geometry.touchTarget"] || null,
          to: adapter.minimumTouchTarget,
          reason: "accessibility-floor",
        });
        resolved["geometry.touchTarget"] = adapter.minimumTouchTarget;
      }
    }
    return { resolvedValues: resolved, adaptations, blockingIssues };
  };

  modules["adapter-engine"] = Object.freeze({ get, adapt });
})();
