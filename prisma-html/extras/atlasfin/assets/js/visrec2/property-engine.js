(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const aliases = (registry) =>
    registry?.v2_internal_registries?.aliases?.propertyAliases || {};

  const canonicalId = (propertyId, registry) => {
    const map = aliases(registry);
    return (
      Object.entries(map).find(([, legacy]) => legacy.includes(propertyId))?.[0] ||
      propertyId
    );
  };

  const normalizeValue = (propertyId, value) => {
    if (
      propertyId === "material.opacity" &&
      typeof value === "number" &&
      value > 1
    )
      return Math.round(value) / 100;
    if (
      propertyId === "shadow.base" &&
      typeof value === "number"
    ) {
      if (value <= 0) return [];
      const alpha = Math.min(0.55, value / 180);
      return [
        {
          x: 0,
          y: Math.max(4, value / 3),
          blur: Math.max(12, value),
          spread: 0,
          color: `rgba(0,0,0,${alpha.toFixed(3)})`,
        },
      ];
    }
    return value;
  };

  const normalize = (values, registry) =>
    Object.fromEntries(
      Object.entries(values || {}).map(([propertyId, value]) => {
        const id = canonicalId(propertyId, registry);
        return [id, normalizeValue(id, value)];
      })
    );

  const propertyMap = (registry) =>
    new Map(
      (registry?.v2_internal_registries?.properties?.items || []).map((item) => [
        item.id,
        item,
      ])
    );

  const validate = (values, registry) => {
    const definitions = propertyMap(registry);
    const issues = [];
    Object.entries(values || {}).forEach(([id, value]) => {
      const definition = definitions.get(id);
      if (!definition) {
        issues.push({ code: "PROPERTY_UNKNOWN", propertyId: id });
        return;
      }
      if (
        typeof value === "number" &&
        definition.min !== null &&
        definition.min !== undefined &&
        value < definition.min
      )
        issues.push({
          code: "PROPERTY_BELOW_MIN",
          propertyId: id,
          value,
          min: definition.min,
        });
      if (
        typeof value === "number" &&
        definition.max !== null &&
        definition.max !== undefined &&
        value > definition.max
      )
        issues.push({
          code: "PROPERTY_ABOVE_MAX",
          propertyId: id,
          value,
          max: definition.max,
        });
    });
    return { ok: issues.length === 0, issues };
  };

  modules["property-engine"] = Object.freeze({
    canonicalId,
    normalize,
    propertyMap,
    validate,
  });
})();
