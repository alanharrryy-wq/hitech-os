(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const stateById = (registry, stateId) =>
    registry?.v2_internal_registries?.states?.items?.find(
      (item) => item.id === stateId
    ) || null;

  const variantById = (registry, variantId) =>
    registry?.v2_internal_registries?.variants?.items?.find(
      (item) => item.id === variantId
    ) || null;

  const resolve = (registry, stateId, variantId, explicitStates, explicitVariants) => {
    const state = stateById(registry, stateId);
    const variant = variantById(registry, variantId);
    return {
      stateId,
      variantId,
      stateProperties: {
        ...(state?.propertyOverrides || {}),
        ...(explicitStates?.[stateId] || {}),
      },
      variantProperties: {
        ...(variant?.propertyOverrides || {}),
        ...(explicitVariants?.[variantId] || {}),
      },
      subcomponentVisibility: state?.subcomponentVisibility || {},
      accessibilityImpact: state?.accessibilityImpact || "preserve",
      reducedMotionPolicy:
        state?.motionPolicy === "explicit" ? "remove-nonessential" : "preserve",
    };
  };

  const matrix = (registry, recipe) =>
    Object.fromEntries(
      (registry?.v2_internal_registries?.states?.items || []).map((state) => [
        state.id,
        {
          status: recipe?.requiredStates?.includes(state.id)
            ? "COMPLETE"
            : "NOT_REQUIRED",
          propertyOverrides: state.propertyOverrides,
          subcomponentVisibility: state.subcomponentVisibility,
          accessibilityImpact: state.accessibilityImpact,
        },
      ])
    );

  const variantMatrix = (registry) =>
    Object.fromEntries(
      (registry?.v2_internal_registries?.variants?.items || []).map((variant) => [
        variant.id,
        {
          status: "COMPLETE",
          kind: variant.kind,
          propertyOverrides: variant.propertyOverrides,
        },
      ])
    );

  modules["state-engine"] = Object.freeze({
    stateById,
    variantById,
    resolve,
    matrix,
    variantMatrix,
  });
})();
