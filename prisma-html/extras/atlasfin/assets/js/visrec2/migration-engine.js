(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const isV2 = (payload) =>
    payload?.schema === "PRISMA_PORTABLE_VISUAL_TRANSFER_V2" &&
    (payload?.schema_version === "2.0.0" || payload?.version === "2.0.0");

  const identityFrom = (payload) => {
    const source =
      payload.selection?.identity ||
      payload.identity ||
      payload.recipes?.[0]?.identity ||
      {};
    return {
      neutralMeaningId:
        source.neutralMeaningId || source.semantic_id || source.semanticId || null,
      sourceComponentId:
        source.componentId || source.component_id || null,
      sourceComponentUiId:
        source.componentUiId || source.ui_id || source.uiId || null,
      structuralFingerprint:
        source.structuralFingerprint ||
        source.structural_fingerprint ||
        null,
      semanticFingerprint: source.semanticFingerprint || null,
    };
  };

  const migrate = async (payload) => {
    if (isV2(payload)) {
      return {
        payload: structuredClone(payload),
        report: {
          schema: "PRISMA_VISUAL_MIGRATION_REPORT_V1",
          version: "1.0.0",
          status: "ALREADY_CURRENT",
          sourceSchema: payload.schema,
          targetSchema: payload.schema,
          inferredFields: [],
          nonInferableFields: [],
          inventedBindings: [],
          idempotent: true,
        },
      };
    }
    const sourceChecksum = payload?.checksum || payload?.integrity?.checksum || null;
    const selection = payload?.selection || payload?.recipes?.[0] || {};
    const identity = identityFrom(payload);
    const canonicalValues =
      selection.canonical_values ||
      selection.canonicalValues ||
      payload?.canonical_values ||
      {};
    const resolvedValues =
      selection.resolved_values ||
      selection.resolvedValues ||
      payload?.resolved_values ||
      {};
    const targetSurface =
      selection.target_intent ||
      payload.target_intent ||
      payload.surface_intent?.targetSurface ||
      "neutral";
    const migrated = {
      schema: "PRISMA_PORTABLE_VISUAL_TRANSFER_V2",
      version: "2.0.0",
      schema_version: "2.0.0",
      producer: {
        systemId: "VISREC2_MIGRATOR",
        runtimeVersion: "2.0.0",
        registryVersion: "unknown",
      },
      capabilities: ["migration-preview", "binding-requirements"],
      export_kind: ["selection", "page", "collection", "delta"].includes(
        payload.export_kind
      )
        ? payload.export_kind
        : "selection",
      export_id: payload.export_id || "PEX.MIGRATED.V1.V2",
      exported_at: payload.exported_at || null,
      instruction_only: true,
      direct_target_mutation: false,
      identity: {
        ...identity,
        identityProfileId: selection.identityProfileId || null,
        recipeId:
          selection.recipeId ||
          selection.recipe_id ||
          selection.recipePresetId ||
          null,
        familyId: selection.familyId || selection.family_id || null,
        presetId: selection.presetId || null,
      },
      source: payload.source || payload.page_context || {},
      recipe: {
        recipeId:
          selection.recipeId ||
          selection.recipe_id ||
          selection.recipePresetId ||
          null,
        familyId: selection.familyId || selection.family_id || null,
        presetId: selection.presetId || null,
        identityProfileId: selection.identityProfileId || null,
        canonicalValues,
        resolvedValues,
        transferMode:
          selection.transfer_mode || payload.transfer_mode || "adaptive",
        intention: selection.intention || payload.intention || "",
        version: selection.version || payload.schema_version || "1.0.0",
        artifactStatus: selection.frozen
          ? "FROZEN"
          : selection.golden
          ? "GOLDEN"
          : "MIGRATION_REQUIRED",
        noTouchRules:
          selection.no_touch_rules || payload.no_touch_rules || [],
      },
      visual_stack: {
        root: {
          partId: "PART.MIGRATED.ROOT",
          semanticRole: "root",
          required: true,
          properties: canonicalValues,
          stateOverrides: selection.state_overrides || {},
          variantOverrides: selection.variant_overrides || {},
          coverageStatus: "PARTIAL",
        },
      },
      state_matrix: selection.state_overrides || {},
      variant_matrix: selection.variant_overrides || {},
      surface_intent: {
        targetSurface,
        adapterId: null,
        bindingApplicationAllowed: false,
      },
      assets: [],
      locks: {
        items: (selection.locked_properties || []).map((propertyId) => ({
          propertyId,
          scope: "legacy",
          reason: "Migrated from V1 lock.",
        })),
      },
      compatibility: {
        compatibilityStatus: "UNKNOWN",
        score: null,
        dimensions: {},
        adaptations: [],
        warnings: ["Requiere reevaluación con registries V2."],
        blockingIssues: [],
        bindingStatus: "BLOCKED_BY_MISSING_ELEMENT_BINDING",
        recipeCoverageStatus: "PARTIAL",
        applicationReadiness: "BLOCKED",
      },
      binding_requirements: {
        schema: "PRISMA_VISUAL_BINDING_REQUIREMENTS_V1",
        version: "1.0.0",
        status: "BLOCKED_BY_MISSING_ELEMENT_BINDING",
        requiredTargetSurface: targetSurface,
        requiredNeutralMeaningId: identity.neutralMeaningId,
        requiredRole: null,
        requiredStates: Object.keys(selection.state_overrides || {}),
        requiredSubcomponents: [],
        requiredCapabilities: [],
        sourceFingerprint: {
          structuralFingerprint: identity.structuralFingerprint,
          semanticFingerprint: identity.semanticFingerprint,
        },
        candidateHints: {},
        forbiddenInferences: [
          "ownerId",
          "routeId",
          "regionId",
          "slotId",
          "componentId",
          "componentUiId",
          "layerId",
        ],
      },
      coverage: {
        schema: "PRISMA_VISUAL_RECIPE_COVERAGE_V1",
        version: "1.0.0",
        status: "PARTIAL",
        matrix: {
          Base: "PARTIAL",
          Hover: "PARTIAL",
          Focus: "PARTIAL",
          Disabled: "PARTIAL",
          Loading: "PARTIAL",
          Icon: "PARTIAL",
          Pseudo: "PARTIAL",
          Assets: "COMPLETE",
        },
        blockingIssues: [
          { code: "BLOCKED_BY_INCOMPLETE_RECIPE_COVERAGE" },
        ],
      },
      evidence: {
        status: "SOURCE_ONLY",
        runtimeProductEvidence: false,
      },
      migration: {
        migrated: true,
        lineage: [
          {
            sourceSchema: payload.schema || "UNKNOWN_V1",
            sourceChecksum,
          },
        ],
        inferredFields: [
          "instruction_only",
          "direct_target_mutation",
          "binding_requirements.status",
          "coverage.status",
        ],
        nonInferableFields: [
          "target ownerId",
          "target routeId",
          "target regionId",
          "target slotId",
          "target componentId",
          "target componentUiId",
          "target layerId",
          "complete visual stack",
        ],
      },
      integrity: { checksum: null },
    };
    const unsigned = structuredClone(migrated);
    delete unsigned.integrity.checksum;
    migrated.integrity.checksum =
      await modules["checksum-engine"].calculate(unsigned);
    return {
      payload: migrated,
      report: {
        schema: "PRISMA_VISUAL_MIGRATION_REPORT_V1",
        version: "1.0.0",
        status: "MIGRATED_PREVIEW",
        sourceSchema: payload.schema || "UNKNOWN_V1",
        targetSchema: "PRISMA_PORTABLE_VISUAL_TRANSFER_V2",
        originalChecksum: sourceChecksum,
        generatedChecksum: migrated.integrity.checksum,
        inferredFields: migrated.migration.inferredFields,
        nonInferableFields: migrated.migration.nonInferableFields,
        inventedBindings: [],
        idempotent: true,
      },
    };
  };

  modules["migration-engine"] = Object.freeze({ isV2, migrate });
})();
