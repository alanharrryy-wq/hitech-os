(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});
  const dimensionNames = [
    "propertySupport",
    "stateSupport",
    "variantSupport",
    "layoutCompatibility",
    "interactionCompatibility",
    "accessibilityCompatibility",
    "performanceCompatibility",
    "assetCompatibility",
    "bindingReadiness",
    "recipeCoverage",
  ];

  const evaluate = ({
    registry,
    values,
    recipe,
    coverage,
    targetSurface,
    transferMode,
    bindingRequirements,
    activeState,
  }) => {
    const adapter = modules["adapter-engine"].get(registry, targetSurface);
    const adapted = modules["adapter-engine"].adapt(
      values,
      adapter,
      transferMode
    );
    const warnings = [];
    if (adapter?.pointerMode === "touch" && activeState === "hover") {
      warnings.push({
        code: "HOVER_NOT_PRIMARY_ON_TOUCH",
        message: "Hover se conserva como opcional; pressed es el feedback táctil.",
      });
      adapted.adaptations.push({
        propertyId: "state.hover",
        from: "hover",
        to: "pressed",
        reason: "touch-substitution",
      });
    }
    const requiredAssets = (recipe?.assets || []).filter((asset) => asset.required);
    const dimensions = {
      propertySupport: adapted.blockingIssues.length ? 55 : 100,
      stateSupport: recipe?.requiredStates?.length ? 100 : 60,
      variantSupport: recipe?.variantSetId ? 100 : 70,
      layoutCompatibility:
        adapter?.authorityLimits?.writeRuntime === false ? 100 : 60,
      interactionCompatibility:
        adapter?.pointerMode === "touch" && activeState === "hover" ? 82 : 100,
      accessibilityCompatibility:
        adapter?.focusPolicy === "focus-visible-required" ? 100 : 65,
      performanceCompatibility:
        adapted.adaptations.some((row) => row.propertyId === "material.blur")
          ? 84
          : 100,
      assetCompatibility: requiredAssets.length ? 85 : 100,
      bindingReadiness:
        bindingRequirements?.status === "RESOLVED" ? 100 : 0,
      recipeCoverage: coverage?.status === "COMPLETE" ? 100 : 55,
    };
    const compatibilityDimensions = Object.fromEntries(
      dimensionNames
        .filter((name) => !["bindingReadiness", "recipeCoverage"].includes(name))
        .map((name) => [name, dimensions[name]])
    );
    const score = Math.round(
      Object.values(compatibilityDimensions).reduce(
        (sum, value) => sum + value,
        0
      ) / Object.keys(compatibilityDimensions).length
    );
    const compatibilityStatus = adapted.blockingIssues.length
      ? "INCOMPATIBLE"
      : adapted.adaptations.length || warnings.length
      ? "COMPATIBLE_WITH_ADAPTATIONS"
      : "COMPATIBLE";
    const bindingStatus =
      bindingRequirements?.status || "BLOCKED_BY_MISSING_ELEMENT_BINDING";
    const recipeCoverageStatus = coverage?.status || "NOT_EVALUATED";
    const applicationReadiness =
      bindingStatus === "RESOLVED" &&
      recipeCoverageStatus === "COMPLETE" &&
      compatibilityStatus !== "INCOMPATIBLE"
        ? "PLAN_REQUIRED"
        : "BLOCKED";
    return {
      compatibilityStatus,
      score,
      dimensions,
      adaptations: adapted.adaptations,
      warnings,
      blockingIssues: adapted.blockingIssues,
      bindingStatus,
      recipeCoverageStatus,
      applicationReadiness,
      adapterId: adapter?.id || null,
      resolvedValues: adapted.resolvedValues,
    };
  };

  modules["compatibility-engine"] = Object.freeze({
    dimensionNames,
    evaluate,
  });
})();
