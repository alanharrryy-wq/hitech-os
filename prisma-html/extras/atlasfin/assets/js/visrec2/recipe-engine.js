(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const clone = (value) => structuredClone(value);

  const recipeByKind = (registry, kind) => {
    const recipes = registry?.v2_internal_registries?.recipes?.items || [];
    return (
      recipes.find((item) => item.familyKind === kind) ||
      recipes.find((item) => item.familyKind === "component") ||
      null
    );
  };

  const presetByFamily = (registry, familyId) =>
    registry?.v2_internal_registries?.presets?.items?.find(
      (item) => item.familyId === familyId
    ) || null;

  const profile = (registry, identityProfileId) =>
    registry?.v2_internal_registries?.profiles?.items?.find(
      (item) => item.identityProfileId === identityProfileId
    ) || null;

  const evaluateCoverage = (recipe, visualStack, assets = []) => {
    const partRows = Object.entries(visualStack || {}).map(([partId, part]) => ({
      partId,
      required: Boolean(part.required),
      status:
        !part.required || part.coverageStatus === "COMPLETE"
          ? "COMPLETE"
          : "PARTIAL",
    }));
    const requiredParts = partRows.filter((row) => row.required);
    const missingParts = requiredParts.filter((row) => row.status !== "COMPLETE");
    const requiredStates = recipe?.requiredStates || [];
    const requiredAssets = (assets || []).filter((asset) => asset.required);
    const missingAssets = requiredAssets.filter((asset) => !asset.expectedHash);
    const pseudoRows = partRows.filter((row) =>
      ["pseudo_before", "pseudo_after"].includes(row.partId)
    );
    const matrix = {
      Base: missingParts.length ? "PARTIAL" : "COMPLETE",
      Hover: requiredStates.includes("hover") ? "COMPLETE" : "PARTIAL",
      Focus:
        requiredStates.includes("focus-visible") &&
        visualStack?.focus_ring?.coverageStatus === "COMPLETE"
          ? "COMPLETE"
          : "PARTIAL",
      Disabled: requiredStates.includes("disabled") ? "COMPLETE" : "PARTIAL",
      Loading:
        requiredStates.includes("loading") &&
        visualStack?.spinner?.coverageStatus !== "PARTIAL"
          ? "COMPLETE"
          : "PARTIAL",
      Icon: visualStack?.icon?.required
        ? visualStack.icon.coverageStatus
        : "COMPLETE",
      Pseudo: pseudoRows.every((row) => row.status === "COMPLETE")
        ? "COMPLETE"
        : "PARTIAL",
      Assets: missingAssets.length ? "PARTIAL" : "COMPLETE",
    };
    const status = Object.values(matrix).every((value) => value === "COMPLETE")
      ? "COMPLETE"
      : "PARTIAL";
    const blockingIssues = [];
    missingParts.forEach((row) =>
      blockingIssues.push({
        code: "BLOCKED_BY_UNGOVERNED_SUBCOMPONENT",
        partId: row.partId,
      })
    );
    missingAssets.forEach((asset) =>
      blockingIssues.push({
        code: "BLOCKED_BY_UNGOVERNED_ASSET",
        assetId: asset.assetId,
      })
    );
    return {
      schema: "PRISMA_VISUAL_RECIPE_COVERAGE_V1",
      version: "1.0.0",
      status,
      matrix,
      parts: partRows,
      stateCount: requiredStates.length,
      blockingIssues,
    };
  };

  const bindingRequirements = (identity, targetSurface, recipe) => ({
    schema: "PRISMA_VISUAL_BINDING_REQUIREMENTS_V1",
    version: "1.0.0",
    status: "BLOCKED_BY_MISSING_ELEMENT_BINDING",
    requiredTargetSurface: targetSurface,
    requiredNeutralMeaningId:
      identity.neutralMeaningId || identity.semantic_id || null,
    requiredRole: recipe?.familyKind || identity.type || "component",
    requiredStates: recipe?.requiredStates || [],
    requiredSubcomponents: recipe?.requiredSubcomponents || [],
    requiredCapabilities: recipe?.requiredCapabilities || [],
    sourceFingerprint: {
      structuralFingerprint:
        identity.structuralFingerprint ||
        identity.structural_fingerprint ||
        null,
      semanticFingerprint: identity.semanticFingerprint || null,
    },
    candidateHints: {
      sourceComponentId: identity.componentId || identity.component_id || null,
      sourceComponentUiId:
        identity.componentUiId || identity.ui_id || null,
      sourceLayerId: identity.layerId || identity.layer_id || null,
    },
    forbiddenInferences: [
      "ownerId",
      "routeId",
      "regionId",
      "slotId",
      "componentId",
      "componentUiId",
      "layerId",
      "implementationFile",
      "implementationSelector",
    ],
  });

  const compile = ({
    registry,
    kind,
    familyId,
    visibleValues,
    stateId,
    variantId,
    stateOverrides,
    variantOverrides,
    identity,
    targetSurface,
    locks,
  }) => {
    const baseRecipe = recipeByKind(registry, kind);
    if (!baseRecipe)
      return {
        ok: false,
        status: "BLOCKED_BY_INCOMPLETE_RECIPE_COVERAGE",
        issues: [{ code: "RECIPE_MISSING", kind }],
      };
    const selectedPreset = presetByFamily(registry, familyId);
    const visualStack = clone(baseRecipe.visualStack);
    const normalizedVisible = modules["property-engine"].normalize(
      visibleValues,
      registry
    );
    const presetValues = selectedPreset?.canonicalValues || {};
    visualStack.root.properties = {
      ...visualStack.root.properties,
      ...presetValues,
      ...normalizedVisible,
    };
    const stateResolution = modules["state-engine"].resolve(
      registry,
      stateId,
      variantId,
      stateOverrides,
      variantOverrides
    );
    visualStack.root.stateOverrides[stateId] =
      stateResolution.stateProperties;
    visualStack.root.variantOverrides[variantId] =
      stateResolution.variantProperties;
    const assetRows = (baseRecipe.assets || []).map((asset) => ({ ...asset }));
    const coverage = evaluateCoverage(baseRecipe, visualStack, assetRows);
    const requirements = bindingRequirements(
      identity,
      targetSurface,
      baseRecipe
    );
    return {
      ok: true,
      status: "SOURCE_READY",
      identityProfile: profile(
        registry,
        selectedPreset?.identityProfileId || baseRecipe.identityProfileId
      ),
      familyId,
      preset: selectedPreset,
      recipe: clone(baseRecipe),
      visualStack,
      stateMatrix: modules["state-engine"].matrix(registry, baseRecipe),
      variantMatrix: modules["state-engine"].variantMatrix(registry),
      stateResolution,
      assets: assetRows,
      coverage,
      bindingRequirements: requirements,
      locks: {
        items: Array.from(locks || []).sort().map((propertyId) => ({
          propertyId,
          scope: "all-states",
          reason: "Bloqueada por decisión explícita del usuario.",
        })),
      },
      canonicalValues: visualStack.root.properties,
      lineage: {
        identityProfileId:
          selectedPreset?.identityProfileId || baseRecipe.identityProfileId,
        familyId,
        presetId: selectedPreset?.presetId || null,
        recipeId: baseRecipe.recipeId,
        stateSetId: baseRecipe.stateSetId,
        variantSetId: baseRecipe.variantSetId,
        schema: "PRISMA_PORTABLE_VISUAL_TRANSFER_V2",
        version: "2.0.0",
      },
    };
  };

  modules["recipe-engine"] = Object.freeze({
    recipeByKind,
    presetByFamily,
    profile,
    compile,
    evaluateCoverage,
    bindingRequirements,
  });
})();
