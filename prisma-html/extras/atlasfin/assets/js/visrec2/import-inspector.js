(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const differences = (actual, proposed) =>
    modules["export-engine"].differences(actual || {}, proposed || {});

  const inspect = async (payload, context = {}) => {
    if (!payload || typeof payload !== "object") {
      return {
        schema: "PRISMA_VISUAL_IMPORT_INSPECTION_V1",
        version: "1.0.0",
        status: "BLOCKED",
        checksum: { ok: false, code: "JSON_INVALID" },
        applicationReadiness: "BLOCKED",
      };
    }
    const checksum = await modules["checksum-engine"].verify(payload);
    if (!checksum.ok) {
      return {
        schema: "PRISMA_VISUAL_IMPORT_INSPECTION_V1",
        version: "1.0.0",
        status: "BLOCKED_BY_INVALID_CHECKSUM",
        checksum,
        applicationReadiness: "BLOCKED",
      };
    }
    const migration = await modules["migration-engine"].migrate(payload);
    const candidate = migration.payload;
    const schemaValid =
      candidate.schema === "PRISMA_PORTABLE_VISUAL_TRANSFER_V2" &&
      candidate.schema_version === "2.0.0" &&
      candidate.instruction_only === true &&
      candidate.direct_target_mutation === false;
    const registry = context.registry || {};
    const currentValues = context.currentCanonicalValues || {};
    const proposedValues = candidate.recipe?.canonicalValues || {};
    const assetRegistry = new Map(
      (registry?.v2_internal_registries?.assets?.items || []).map((item) => [
        item.assetId,
        item,
      ])
    );
    const assets = (candidate.assets || []).map((asset) => ({
      assetId: asset.assetId,
      required: Boolean(asset.required),
      available: assetRegistry.has(asset.assetId),
      expectedHash: asset.expectedHash || null,
    }));
    const missingCapabilities = (candidate.capabilities || []).filter(
      (capability) =>
        ![
          "full-visual-stack",
          "state-matrix",
          "variant-matrix",
          "surface-adapters-v2",
          "portable-assets",
          "binding-requirements",
          "read-only-import",
          "migration-preview",
        ].includes(capability)
    );
    const compatibility = candidate.compatibility || {};
    const bindingStatus =
      candidate.binding_requirements?.status ||
      "BLOCKED_BY_MISSING_ELEMENT_BINDING";
    const coverageStatus = candidate.coverage?.status || "NOT_EVALUATED";
    const applicationReadiness =
      schemaValid &&
      bindingStatus === "RESOLVED" &&
      coverageStatus === "COMPLETE" &&
      compatibility.compatibilityStatus !== "INCOMPATIBLE"
        ? "PLAN_REQUIRED"
        : "BLOCKED";
    return {
      schema: "PRISMA_VISUAL_IMPORT_INSPECTION_V1",
      version: "1.0.0",
      status: schemaValid ? "INSPECTED_READ_ONLY" : "BLOCKED",
      readOnly: true,
      checksum,
      schemaValidation: {
        ok: schemaValid,
        schema: candidate.schema,
        schemaVersion: candidate.schema_version,
      },
      migrationPreview: migration.report,
      registryCompatibility: {
        ok: missingCapabilities.length === 0,
        missingCapabilities,
      },
      canonicalDiff: differences(currentValues, proposedValues),
      resolvedDiff: differences(
        context.currentResolvedValues || {},
        candidate.recipe?.resolvedValues || {}
      ),
      stateCoverage: candidate.state_matrix || {},
      variantCoverage: candidate.variant_matrix || {},
      assets,
      bindingRequirementSummary: candidate.binding_requirements || {},
      targetCompatibility: compatibility,
      recipeCoverageStatus: coverageStatus,
      bindingStatus,
      applicationReadiness,
      applicationReason:
        applicationReadiness === "PLAN_REQUIRED"
          ? "Requiere plan read-only y revisión humana."
          : "La importación nunca aplica; faltan gates de binding/cobertura/autoridad.",
      inspectedPayload: candidate,
    };
  };

  modules["import-inspector"] = Object.freeze({ inspect });
})();
