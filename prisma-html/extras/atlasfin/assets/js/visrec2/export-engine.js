(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const differences = (from, to) => {
    const keys = new Set([...Object.keys(from || {}), ...Object.keys(to || {})]);
    return Object.fromEntries(
      Array.from(keys)
        .sort()
        .filter(
          (key) =>
            modules["checksum-engine"].stableJson(from?.[key]) !==
            modules["checksum-engine"].stableJson(to?.[key])
        )
        .map((key) => [key, { from: from?.[key], to: to?.[key] }])
    );
  };

  const delta = (a, b) => ({
    schema: "PRISMA_VISUAL_DELTA_V2",
    version: "2.0.0",
    canonicalDifferences: differences(a?.canonicalValues, b?.canonicalValues),
    resolvedDifferences: differences(a?.resolvedValues, b?.resolvedValues),
    structuralDifferences: differences(
      a?.identity?.fingerprints?.structural,
      b?.identity?.fingerprints?.structural
    ),
    semanticDifferences: differences(
      a?.identity?.fingerprints?.semantic,
      b?.identity?.fingerprints?.semantic
    ),
    stateDifferences: differences(a?.stateMatrix, b?.stateMatrix),
    variantDifferences: differences(a?.variantMatrix, b?.variantMatrix),
    assetDifferences: differences(
      Object.fromEntries((a?.assets || []).map((row) => [row.assetId, row])),
      Object.fromEntries((b?.assets || []).map((row) => [row.assetId, row]))
    ),
    deltaIntent: "instruction-only visual comparison",
    deltaPatchHints: [],
    deltaBindingRequirements: {
      from: a?.bindingRequirements || null,
      to: b?.bindingRequirements || null,
    },
    instructionOnly: true,
  });

  const build = ({
    kind,
    exportId,
    exportedAt,
    source,
    identity,
    compiled,
    targetSurface,
    transferMode,
    compatibility,
    resolvedValues,
    noTouchRules,
    intention,
    version,
    artifactStatus,
    evidence,
    extras,
  }) => ({
    schema: "PRISMA_PORTABLE_VISUAL_TRANSFER_V2",
    version: "2.0.0",
    schema_version: "2.0.0",
    producer: {
      systemId: "VISREC2",
      runtimeVersion: "2.0.0",
      registryVersion: "4.0.0",
    },
    capabilities: [
      "full-visual-stack",
      "state-matrix",
      "variant-matrix",
      "surface-adapters-v2",
      "portable-assets",
      "binding-requirements",
      "read-only-import",
    ],
    export_kind: kind,
    export_id: exportId,
    exported_at: exportedAt,
    instruction_only: true,
    direct_target_mutation: false,
    identity: {
      neutralMeaningId: identity.neutralMeaningId,
      identityProfileId: compiled.lineage.identityProfileId,
      recipeId: compiled.lineage.recipeId,
      familyId: compiled.lineage.familyId,
      presetId: compiled.lineage.presetId,
      sourceComponentId: identity.componentId,
      sourceComponentUiId: identity.componentUiId,
      fingerprints: {
        structuralFingerprint: identity.structuralFingerprint,
        semanticFingerprint: identity.semanticFingerprint,
        structural: identity.fingerprints?.structural || {},
        semantic: identity.fingerprints?.semantic || {},
      },
    },
    source,
    recipe: {
      recipeId: compiled.lineage.recipeId,
      familyId: compiled.lineage.familyId,
      presetId: compiled.lineage.presetId,
      identityProfileId: compiled.lineage.identityProfileId,
      canonicalValues: compiled.canonicalValues,
      resolvedValues,
      transferMode,
      intention,
      version,
      artifactStatus,
      noTouchRules,
    },
    visual_stack: compiled.visualStack,
    state_matrix: compiled.stateMatrix,
    variant_matrix: compiled.variantMatrix,
    surface_intent: {
      targetSurface,
      adapterId: compatibility.adapterId,
      bindingApplicationAllowed: false,
    },
    assets: compiled.assets,
    locks: compiled.locks,
    compatibility,
    binding_requirements: compiled.bindingRequirements,
    coverage: compiled.coverage,
    evidence: evidence || {
      status: "PREVIEW_ONLY",
      runtimeProductEvidence: false,
    },
    migration: {
      migrated: false,
      lineage: [],
      inferredFields: [],
      nonInferableFields: [],
    },
    integrity: {
      checksum: null,
    },
    ...extras,
  });

  const finalize = async (payload) => {
    const unsigned = structuredClone(payload);
    delete unsigned.integrity.checksum;
    unsigned.integrity.checksum =
      await modules["checksum-engine"].calculate(unsigned);
    return unsigned;
  };

  modules["export-engine"] = Object.freeze({
    differences,
    delta,
    build,
    finalize,
  });
})();
