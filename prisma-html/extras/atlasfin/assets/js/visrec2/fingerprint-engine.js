(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const normalizedText = (element) =>
    String(
      element?.getAttribute?.("aria-label") ||
        element?.getAttribute?.("title") ||
        element?.innerText ||
        ""
    )
      .normalize("NFKC")
      .trim()
      .replace(/\s+/g, " ")
      .slice(0, 240);

  const stableClasses = (element) =>
    Array.from(element?.classList || [])
      .filter(
        (name) =>
          !name.startsWith("is-") &&
          !name.startsWith("has-") &&
          !name.startsWith("visrec2-")
      )
      .sort();

  const dataAttributes = (element) =>
    Object.fromEntries(
      Array.from(element?.attributes || [])
        .filter((attribute) => attribute.name.startsWith("data-"))
        .filter((attribute) => !attribute.name.startsWith("data-visrec2-"))
        .slice(0, 40)
        .map((attribute) => [attribute.name, attribute.value])
    );

  const ariaAttributes = (element) =>
    Object.fromEntries(
      Array.from(element?.attributes || [])
        .filter(
          (attribute) =>
            attribute.name.startsWith("aria-") ||
            ["role", "tabindex"].includes(attribute.name)
        )
        .slice(0, 30)
        .map((attribute) => [attribute.name, attribute.value])
    );

  const stableAncestors = (element) => {
    const rows = [];
    let current = element?.parentElement;
    while (current && rows.length < 6) {
      const token =
        current.id ||
        current.dataset?.visualComponentId ||
        current.dataset?.visualRegionId ||
        stableClasses(current)[0];
      if (token) rows.push(token);
      current = current.parentElement;
    }
    return rows;
  };

  const siblingPattern = (element) => {
    if (!element?.parentElement) return [];
    return Array.from(element.parentElement.children)
      .slice(0, 24)
      .map((node) => ({
        tag: node.tagName?.toLowerCase(),
        role: node.getAttribute?.("role") || null,
        semanticId: node.dataset?.visualSemanticId || null,
      }));
  };

  const domDepth = (element) => {
    let depth = 0;
    let current = element;
    while (current?.parentElement) {
      depth += 1;
      current = current.parentElement;
    }
    return depth;
  };

  const hash = (value, checksum) =>
    checksum.fnv(checksum.stableJson(value)).toUpperCase();

  const create = (element, context, classify, checksum) => {
    const style = window.getComputedStyle(element);
    const structural = {
      tag: element.tagName?.toLowerCase(),
      role: element.getAttribute?.("role") || null,
      type: classify(element),
      classes: stableClasses(element),
      dataAttributes: dataAttributes(element),
      childSemanticRoles: Array.from(element.children || [])
        .slice(0, 30)
        .map((child) => ({
          tag: child.tagName.toLowerCase(),
          role: child.getAttribute("role"),
          semanticId: child.dataset?.visualSemanticId || null,
        })),
      computedDisplayType: style.display,
      domDepth: domDepth(element),
      siblingPattern: siblingPattern(element),
      stableAncestorIds: stableAncestors(element),
      sourcePage: context.page_id || context.pageId || null,
      sourceVersion: context.version || "unknown",
      textNormalizationPolicy: "NFKC_TRIM_COLLAPSE_240",
    };
    const semantic = {
      neutralMeaningId:
        element.dataset?.neutralMeaningId ||
        element.dataset?.visualSemanticId ||
        null,
      accessibleName: normalizedText(element),
      ariaAttributes: ariaAttributes(element),
      role: element.getAttribute?.("role") || element.tagName?.toLowerCase(),
      relations: {
        labelledBy: element.getAttribute?.("aria-labelledby") || null,
        describedBy: element.getAttribute?.("aria-describedby") || null,
        controls: element.getAttribute?.("aria-controls") || null,
      },
      componentRole: classify(element),
      sourceSurfaceId:
        context.surface_instance_id ||
        context.surfaceId ||
        context.surface_id ||
        null,
    };
    return {
      structuralFingerprint: hash(structural, checksum),
      semanticFingerprint: hash(semantic, checksum),
      structural,
      semantic,
      resolutionAuthority: "CANDIDATE_ONLY",
      bindingStatus: "CANDIDATE",
    };
  };

  modules["fingerprint-engine"] = Object.freeze({
    create,
    normalizedText,
    stableClasses,
    dataAttributes,
    ariaAttributes,
  });
})();
