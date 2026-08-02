(() => {
  "use strict";
  const modules = (window.__PRISMA_VISREC2_MODULES__ ||= {});

  const init = async (bridge, engines) => {
    const registry = bridge.registry;
    const transfer = registry?.transfer_console;
    if (!transfer) throw new Error("Falta transfer_console en el registry.");

    const expectedCounts = {
      properties: 12,
      states: 12,
      variants: 8,
      targets: 4,
      transferModes: 3,
    };
    const visibleContract = transfer.visible_control_contract || {};
    if (
      engines["checksum-engine"].stableJson(visibleContract.counts) !==
        engines["checksum-engine"].stableJson(expectedCounts) ||
      visibleContract.additionalControlCount !== 0
    ) {
      throw new Error(
        "El contrato de controles visibles cambió; VISREC2 bloqueó el runtime."
      );
    }

    document.querySelector("[data-recipe-dock]")?.remove();
    document.querySelector("[data-open-recipe-dock]")?.remove();
    document.querySelector("[data-visrec2-console]")?.remove();
    document.querySelector("[data-open-visrec2]")?.remove();

    const selectionEngine = engines["selection-engine"];
    const fingerprintEngine = engines["fingerprint-engine"];
    const recipeEngine = engines["recipe-engine"];
    const previewEngine = engines["preview-engine"];
    const exportEngine = engines["export-engine"];
    const importInspector = engines["import-inspector"];
    const checksumEngine = engines["checksum-engine"];

    const state = {
      open: false,
      selecting: false,
      selected: null,
      deltaA: null,
      deltaB: null,
      scope: "element",
      transferMode: "adaptive",
      target: "neutral",
      activeState: "default",
      activeVariant: "base",
      familyId: "",
      locks: new Set(),
      canonicalValues: {},
      stateOverrides: {},
      variantOverrides: {},
      intent: "",
      noTouch: new Set([
        "logic",
        "content",
        "accessibility",
        "primary-action",
      ]),
      version: "2.0.0",
      golden: false,
      frozen: false,
      collection: [],
      imported: null,
      inventory: [],
      compiled: null,
      highlight: null,
      returnFocus: null,
    };

    const escapeHtml = (value) =>
      String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

    const slug = (value) =>
      String(value || "UNKNOWN")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-zA-Z0-9]+/g, ".")
        .replace(/^\.+|\.+$/g, "")
        .toUpperCase() || "UNKNOWN";

    const pageContext = () => bridge.pageContext();

    const elementIndex = (element, type) => {
      const candidates = selectionEngine
        .inventory()
        .filter((candidate) => selectionEngine.classify(candidate) === type);
      return Math.max(1, candidates.indexOf(element) + 1);
    };

    const identify = (element) => {
      const context = pageContext();
      const type = selectionEngine.classify(element);
      const fingerprints = fingerprintEngine.create(
        element,
        context,
        selectionEngine.classify,
        checksumEngine
      );
      const pageToken = slug(context.page_id || bridge.pageId);
      const typeToken = slug(type);
      const explicit = element.dataset?.visualComponentId || element.id || null;
      const region = element.closest?.(
        "[data-visual-recipe-region], [id], .atlas-section, .atlas-demo, .atlas-card"
      );
      const regionToken =
        region?.dataset?.visualRecipeRegion ||
        region?.id ||
        Array.from(region?.classList || [])[0] ||
        "PAGE";
      const structuralFingerprint = fingerprints.structuralFingerprint;
      const componentId = explicit
        ? slug(explicit)
        : `ATL.${pageToken}.${typeToken}.${structuralFingerprint}`;
      return {
        neutralMeaningId:
          element.dataset?.neutralMeaningId ||
          element.dataset?.visualSemanticId ||
          `VIS.${typeToken}.GENERIC`,
        sourceSurfaceId:
          context.surface_instance_id || `SURF.HTML.ATLASFIN.${pageToken}`,
        sourceOwnerId:
          element.dataset?.visualOwnerId ||
          `OWN.ATLASFIN.${pageToken}.${typeToken}`,
        sourceRouteId:
          context.route_id || `ROUTE.ATLASFIN.${pageToken}`,
        sourceRegionId:
          element.dataset?.visualRegionId ||
          `REG.ATLASFIN.${pageToken}.${slug(regionToken)}`,
        sourceSlotId:
          element.dataset?.visualSlotId ||
          `SLOT.${typeToken}.${String(elementIndex(element, type)).padStart(
            2,
            "0"
          )}`,
        componentId,
        componentUiId: explicit
          ? `${slug(explicit)}.UI`
          : `${componentId}.UI`,
        layerId:
          element.dataset?.visualLayerId ||
          `LYR.ATLAS.${pageToken}.${typeToken}.${structuralFingerprint}`,
        implementationLayerId: null,
        type,
        structuralFingerprint,
        semanticFingerprint: fingerprints.semanticFingerprint,
        fingerprints: {
          structural: fingerprints.structural,
          semantic: fingerprints.semantic,
        },
        bindingStatus: "CANDIDATE",
        resolutionAuthority: "CANDIDATE_ONLY",
      };
    };

    const parseDuration = (value) => {
      const first = String(value || "0s").split(",")[0].trim();
      if (first.endsWith("ms")) return Number.parseFloat(first) || 0;
      return (Number.parseFloat(first) || 0) * 1000;
    };

    const computedValueMap = (element) => {
      const computed = window.getComputedStyle(element || bridge.body);
      const blur = Number.parseFloat(
        (
          computed.backdropFilter ||
          computed.webkitBackdropFilter ||
          ""
        ).match(/blur\(([-\d.]+)px\)/)?.[1] || "0"
      );
      return {
        "material.opacity": Math.round(
          Number.parseFloat(computed.opacity || "1") * 100
        ),
        "material.blur": blur,
        "material.radius": Number.parseFloat(computed.borderRadius || "0") || 0,
        "material.border.width":
          Number.parseFloat(computed.borderTopWidth || "0") || 0,
        "material.shadow": computed.boxShadow === "none" ? 0 : 45,
        "color.accent":
          getComputedStyle(bridge.root)
            .getPropertyValue("--atlas-accent-hex")
            .trim() || "#7c5cff",
        "color.background": computed.backgroundColor,
        "color.foreground": computed.color,
        "typography.size": Number.parseFloat(computed.fontSize || "16") || 16,
        "typography.weight": String(computed.fontWeight || "600"),
        "layout.spacing": Number.parseFloat(computed.paddingTop || "0") || 0,
        "motion.duration": parseDuration(computed.transitionDuration),
      };
    };

    const resolvedValueMap = (element) => {
      const computed = window.getComputedStyle(element || bridge.body);
      const names = transfer.resolved_properties || [
        "background-color",
        "color",
        "border-radius",
        "border-width",
        "box-shadow",
        "font-size",
        "font-weight",
        "padding",
        "transition-duration",
      ];
      return Object.fromEntries(
        names.map((property) => [
          property,
          computed.getPropertyValue(property).trim(),
        ])
      );
    };

    const familyOptions = (type) =>
      transfer.component_families?.[type] || [];

    const scopeTarget = () =>
      selectionEngine.scopeTarget(
        state.selected,
        state.scope,
        bridge.root,
        bridge.body
      );

    const compile = () => {
      const target = state.selected || bridge.body;
      const identity = identify(target);
      state.compiled = recipeEngine.compile({
        registry,
        kind: selectionEngine.classify(target),
        familyId: state.familyId,
        visibleValues: state.canonicalValues,
        stateId: state.activeState,
        variantId: state.activeVariant,
        stateOverrides: state.stateOverrides,
        variantOverrides: state.variantOverrides,
        identity,
        targetSurface: state.target,
        locks: state.locks,
      });
      return state.compiled;
    };

    const compatibility = () => {
      const compiled = state.compiled?.ok ? state.compiled : compile();
      return engines["compatibility-engine"].evaluate({
        registry,
        values: compiled?.canonicalValues || {},
        recipe: compiled?.recipe,
        coverage: compiled?.coverage,
        targetSurface: state.target,
        transferMode: state.transferMode,
        bindingRequirements: compiled?.bindingRequirements,
        activeState: state.activeState,
      });
    };

    const applyPreview = () => {
      if (state.frozen) return;
      const target = scopeTarget();
      if (!target) return;
      const compiled = compile();
      previewEngine.apply(
        target,
        compiled,
        state.activeState,
        state.activeVariant,
        state.locks
      );
      renderGovernance();
    };

    const clearPreview = () => {
      const target = scopeTarget();
      if (target) previewEngine.clear(target);
    };

    const labelFor = (element) =>
      String(
        element.getAttribute("aria-label") ||
          element.innerText ||
          element.id ||
          Array.from(element.classList || [])[0] ||
          element.tagName
      )
        .trim()
        .replace(/\s+/g, " ")
        .slice(0, 90);

    const buildInventory = () => {
      state.inventory = selectionEngine.inventory().map((element) => ({
        element,
        type: selectionEngine.classify(element),
        identity: identify(element),
        label: labelFor(element),
      }));
      renderInventory();
      renderInventorySummary();
    };

    const setSelected = (element) => {
      clearPreview();
      if (state.selected && state.selected !== element)
        state.selected.classList.remove("visrec2-selected-source");
      state.selected = element;
      state.selected?.classList.add("visrec2-selected-source");
      state.canonicalValues = computedValueMap(element || bridge.body);
      state.familyId =
        familyOptions(selectionEngine.classify(element))[0]?.id || "";
      compile();
      renderSelection();
      renderFamilyControls();
      renderPropertyControls();
      renderIds();
      renderGovernance();
    };

    const highlight = (element) => {
      const overlay = state.highlight;
      if (!overlay) return;
      if (!element) {
        overlay.hidden = true;
        return;
      }
      const rect = element.getBoundingClientRect();
      overlay.hidden = false;
      overlay.style.left = `${rect.left + window.scrollX}px`;
      overlay.style.top = `${rect.top + window.scrollY}px`;
      overlay.style.width = `${rect.width}px`;
      overlay.style.height = `${rect.height}px`;
      overlay.dataset.type = selectionEngine.classify(element);
      overlay.querySelector("span").textContent = `${selectionEngine.classify(
        element
      )} · ${labelFor(element)}`;
    };

    const startSelecting = () => {
      state.selecting = true;
      bridge.body.classList.add("is-visrec2-selecting");
      bridge.toast("Selecciona un objeto de la página.");
    };

    const stopSelecting = () => {
      state.selecting = false;
      bridge.body.classList.remove("is-visrec2-selecting");
      highlight(null);
    };

    const captureSnapshot = () => {
      if (!state.selected) return null;
      const compiled = compile();
      const identity = identify(state.selected);
      return {
        identity,
        canonicalValues: compiled.canonicalValues,
        resolvedValues: resolvedValueMap(state.selected),
        visualStack: compiled.visualStack,
        stateMatrix: compiled.stateMatrix,
        variantMatrix: compiled.variantMatrix,
        assets: compiled.assets,
        coverage: compiled.coverage,
        bindingRequirements: compiled.bindingRequirements,
        lineage: compiled.lineage,
      };
    };

    const captureDelta = (side) => {
      const snapshot = captureSnapshot();
      if (!snapshot) {
        bridge.toast("Selecciona un objeto primero.");
        return;
      }
      if (side === "A") state.deltaA = snapshot;
      else state.deltaB = snapshot;
      renderDelta();
      bridge.toast(`Captura ${side} guardada.`);
    };

    const artifactStatus = () =>
      state.frozen ? "FROZEN" : state.golden ? "GOLDEN" : "SOURCE_READY";

    const exportPayload = async (kind) => {
      const visibleKinds = ["selection", "page", "collection", "delta"];
      const internalKinds = transfer.export_kinds_internal || visibleKinds;
      if (!internalKinds.includes(kind))
        throw new Error(`Export kind no gobernado: ${kind}`);
      if (!state.selected && !["page", "theme", "adapter"].includes(kind)) {
        bridge.toast("Selecciona un objeto primero.");
        return null;
      }
      const target = state.selected || bridge.body;
      const identity = identify(target);
      const compiled = compile();
      const compat = compatibility();
      const allNoTouch = Array.from(
        new Set([
          ...(compiled.recipe?.noTouchRules || []),
          ...Array.from(state.noTouch),
        ])
      ).sort();
      const extras = {};
      if (kind === "collection") extras.collection = state.collection;
      if (kind === "page")
        extras.page_inventory = bridge.capturePageInventory();
      if (kind === "delta") {
        if (!state.deltaA || !state.deltaB) {
          bridge.toast("Captura A y B antes de exportar delta.");
          return null;
        }
        extras.delta = exportEngine.delta(state.deltaA, state.deltaB);
      }
      if (
        ["profile", "recipe", "family", "preset", "state-set", "adapter", "asset-pack"].includes(
          kind
        )
      ) {
        extras.registry_entity = {
          profile: compiled.identityProfile,
          recipe: compiled.recipe,
          familyId: compiled.familyId,
          preset: compiled.preset,
          stateSet: registry.v2_internal_registries?.states,
          adapter:
            registry.v2_internal_registries?.adapters?.items?.find(
              (item) => item.surfaceId === state.target
            ) || null,
          assetPack: compiled.assets,
        };
      }
      const raw = exportEngine.build({
        kind,
        exportId: `PEX.VISREC2.${slug(bridge.pageId)}.${slug(
          kind
        )}.${bridge.fileStamp()}`,
        exportedAt: bridge.timestamp(),
        source: pageContext(),
        identity,
        compiled,
        targetSurface: state.target,
        transferMode: state.transferMode,
        compatibility: compat,
        resolvedValues: resolvedValueMap(target),
        noTouchRules: allNoTouch,
        intention: state.intent,
        version: state.version,
        artifactStatus: artifactStatus(),
        evidence: {
          status: "PREVIEW_ONLY",
          sourcePage: pageContext().page_file,
          runtimeProductEvidence: false,
          visualReview: "NOT_CAPTURED",
        },
        extras,
      });
      const finalized = await exportEngine.finalize(raw);
      const filename = bridge.sanitizeFilename(
        `visrec2_${bridge.pageId}_${kind}_${bridge.fileStamp()}.prisma-visual.json`
      );
      bridge.download(filename, finalized);
      storeHistory(finalized);
      bridge.toast(`Exportación ${kind} V2 lista.`);
      return finalized;
    };

    const addCollection = () => {
      const snapshot = captureSnapshot();
      if (!snapshot) {
        bridge.toast("Selecciona un objeto primero.");
        return;
      }
      state.collection.push(snapshot);
      renderCollection();
      bridge.toast("Objeto añadido a la colección.");
    };

    const historyKey = `prisma-visrec2-v2-history-${bridge.pageId}`;
    const storeHistory = (payload) => {
      const current = JSON.parse(localStorage.getItem(historyKey) || "[]");
      current.unshift({
        exportId: payload.export_id,
        exportKind: payload.export_kind,
        exportedAt: payload.exported_at,
        componentId: payload.identity?.sourceComponentId,
        version: payload.recipe?.version,
        artifactStatus: payload.recipe?.artifactStatus,
        checksum: payload.integrity?.checksum?.value,
      });
      localStorage.setItem(historyKey, JSON.stringify(current.slice(0, 30)));
      renderHistory();
    };

    const inputForProperty = (property, value) => {
      if (property.type === "select") {
        return `<select data-visrec2-property="${escapeHtml(
          property.id
        )}">${(property.options || [])
          .map(
            (option) =>
              `<option value="${escapeHtml(option)}" ${
                String(value) === String(option) ? "selected" : ""
              }>${escapeHtml(option)}</option>`
          )
          .join("")}</select>`;
      }
      if (property.type === "color") {
        const color = /^#[0-9a-f]{6}$/i.test(String(value))
          ? value
          : property.default || "#7c5cff";
        return `<input type="color" value="${color}" data-visrec2-property="${escapeHtml(
          property.id
        )}">`;
      }
      return `<span class="visrec2-range"><input type="range" min="${
        property.min ?? 0
      }" max="${property.max ?? 100}" step="${property.step ?? 1}" value="${Number(
        value ?? property.default ?? 0
      )}" data-visrec2-property="${escapeHtml(
        property.id
      )}"><output>${escapeHtml(value ?? property.default ?? 0)}${escapeHtml(
        property.unit || ""
      )}</output></span>`;
    };

    let shell;

    const renderPropertyControls = () => {
      const host = shell.querySelector("[data-property-controls]");
      if (!host) return;
      host.innerHTML = (transfer.properties || [])
        .map((property) => {
          const value =
            state.canonicalValues[property.id] ?? property.default;
          return `<label class="visrec2-property-row" data-category="${escapeHtml(
            property.category
          )}">
            <span><strong>${escapeHtml(
              property.label
            )}</strong><small>${escapeHtml(property.id)}</small></span>
            ${inputForProperty(property, value)}
            <input type="checkbox" data-lock-property="${escapeHtml(
              property.id
            )}" ${
            state.locks.has(property.id) ? "checked" : ""
          } aria-label="Bloquear ${escapeHtml(property.label)}">
          </label>`;
        })
        .join("");
      host
        .querySelectorAll("[data-visrec2-property]")
        .forEach((input) => {
          input.addEventListener("input", () => {
            const property = transfer.properties.find(
              (item) => item.id === input.dataset.visrec2Property
            );
            const value =
              property?.type === "range" || input.type === "range"
                ? Number(input.value)
                : input.value;
            state.canonicalValues[input.dataset.visrec2Property] = value;
            input
              .closest(".visrec2-property-row")
              ?.querySelector("output")
              ?.replaceChildren(`${value}${property?.unit || ""}`);
            applyPreview();
          });
        });
      host.querySelectorAll("[data-lock-property]").forEach((input) => {
        input.addEventListener("change", () => {
          if (input.checked) state.locks.add(input.dataset.lockProperty);
          else state.locks.delete(input.dataset.lockProperty);
          compile();
          renderGovernance();
        });
      });
    };

    const renderFamilyControls = () => {
      const host = shell.querySelector("[data-family-control]");
      if (!host) return;
      if (!state.selected) {
        host.innerHTML =
          '<p class="visrec2-empty">Selecciona un objeto para resolver su familia.</p>';
        return;
      }
      const type = selectionEngine.classify(state.selected);
      const families = familyOptions(type);
      if (!families.length) {
        host.innerHTML = `<p class="visrec2-empty">No se muestra un control muerto: ${escapeHtml(
          type
        )} usa la receta genérica interna.</p>`;
        return;
      }
      host.innerHTML = `<label><span>Familia ${escapeHtml(
        type
      )}</span><select data-family-select>${families
        .map(
          (family) =>
            `<option value="${escapeHtml(family.id)}" ${
              family.id === state.familyId ? "selected" : ""
            }>${escapeHtml(family.label)}</option>`
        )
        .join("")}</select></label>`;
      host.querySelector("[data-family-select]")?.addEventListener(
        "change",
        (event) => {
          state.familyId = event.target.value;
          const family = families.find((item) => item.id === state.familyId);
          Object.assign(state.canonicalValues, family?.values || {});
          renderPropertyControls();
          applyPreview();
        }
      );
    };

    const renderSelection = () => {
      const host = shell.querySelector("[data-selection-summary]");
      if (!host) return;
      if (!state.selected) {
        host.innerHTML =
          '<p class="visrec2-empty">Aún no hay objeto seleccionado.</p>';
        return;
      }
      const identity = identify(state.selected);
      host.innerHTML = `<strong>${escapeHtml(
        labelFor(state.selected)
      )}</strong><span>${escapeHtml(identity.type)} · ${escapeHtml(
        state.scope
      )}</span><code>${escapeHtml(identity.componentId)}</code>`;
    };

    const renderIds = () => {
      const host = shell.querySelector("[data-identity-table]");
      if (!host) return;
      if (!state.selected) {
        host.innerHTML =
          '<p class="visrec2-empty">Los IDs aparecerán al seleccionar un objeto.</p>';
        return;
      }
      const identity = identify(state.selected);
      const keys = [
        "neutralMeaningId",
        "sourceSurfaceId",
        "sourceOwnerId",
        "sourceRouteId",
        "sourceRegionId",
        "sourceSlotId",
        "componentId",
        "componentUiId",
        "layerId",
        "implementationLayerId",
        "structuralFingerprint",
        "semanticFingerprint",
        "bindingStatus",
      ];
      host.innerHTML = keys
        .map(
          (key) =>
            `<div><span>${escapeHtml(key)}</span><code>${escapeHtml(
              identity[key] ?? "UNRESOLVED"
            )}</code></div>`
        )
        .join("");
    };

    const renderInventorySummary = () => {
      const host = shell.querySelector("[data-inventory-summary]");
      if (!host) return;
      const counts = state.inventory.reduce((result, item) => {
        result[item.type] = (result[item.type] || 0) + 1;
        return result;
      }, {});
      host.innerHTML = Object.entries(counts)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(
          ([type, count]) =>
            `<span><strong>${count}</strong>${escapeHtml(type)}</span>`
        )
        .join("");
    };

    const renderInventory = () => {
      const host = shell.querySelector("[data-inventory-list]");
      if (!host) return;
      host.innerHTML = state.inventory
        .slice(0, 160)
        .map(
          (item, index) =>
            `<button type="button" data-inventory-index="${index}"><span>${escapeHtml(
              item.type
            )}</span><strong>${escapeHtml(item.label)}</strong><code>${escapeHtml(
              item.identity.componentId
            )}</code></button>`
        )
        .join("");
      host.querySelectorAll("[data-inventory-index]").forEach((button) => {
        button.addEventListener("click", () => {
          const item = state.inventory[Number(button.dataset.inventoryIndex)];
          if (!item) return;
          setSelected(item.element);
          item.element.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        });
      });
    };

    const renderCollection = () => {
      const host = shell.querySelector("[data-collection-list]");
      if (!host) return;
      host.innerHTML = state.collection.length
        ? state.collection
            .map(
              (item, index) =>
                `<li><span>${escapeHtml(
                  item.identity.componentId
                )}</span><button type="button" data-remove-collection="${index}">✕</button></li>`
            )
            .join("")
        : '<li class="visrec2-empty">Colección vacía.</li>';
      host.querySelectorAll("[data-remove-collection]").forEach((button) => {
        button.addEventListener("click", () => {
          state.collection.splice(
            Number(button.dataset.removeCollection),
            1
          );
          renderCollection();
        });
      });
    };

    const renderDelta = () => {
      const host = shell.querySelector("[data-delta-summary]");
      if (!host) return;
      host.innerHTML =
        state.deltaA && state.deltaB
          ? `<strong>Delta listo</strong><span>${escapeHtml(
              state.deltaA.identity.componentId
            )} → ${escapeHtml(state.deltaB.identity.componentId)}</span>`
          : `<strong>Delta incompleto</strong><span>A: ${
              state.deltaA ? "✓" : "pendiente"
            } · B: ${state.deltaB ? "✓" : "pendiente"}</span>`;
    };

    const renderHistory = () => {
      const host = shell.querySelector("[data-history-list]");
      if (!host) return;
      const current = JSON.parse(localStorage.getItem(historyKey) || "[]");
      host.innerHTML = current.length
        ? current
            .map(
              (item) =>
                `<li><span>${
                  item.artifactStatus === "GOLDEN" ? "★ " : ""
                }${escapeHtml(item.exportKind)}</span><strong>${escapeHtml(
                  item.componentId || bridge.pageId
                )}</strong><small>${escapeHtml(
                  item.version || ""
                )} · ${escapeHtml(item.exportedAt)}</small></li>`
            )
            .join("")
        : '<li class="visrec2-empty">Sin exportaciones todavía.</li>';
    };

    const statusClass = (value) =>
      value === "COMPLETE" ||
      value === "COMPATIBLE" ||
      value === "SOURCE_READY"
        ? "visrec2-status--complete"
        : value === "INVALID_CHECKSUM" || value === "INCOMPATIBLE"
        ? "visrec2-status--invalid"
        : value === "BLOCKED" || String(value).startsWith("BLOCKED_")
        ? "visrec2-status--blocked"
        : "visrec2-status--partial";

    const renderGovernance = () => {
      const host = shell.querySelector("[data-governance-readouts]");
      if (!host) return;
      const compiled = state.compiled?.ok ? state.compiled : compile();
      const compat = compatibility();
      const coverage = compiled.coverage;
      const lineage = compiled.lineage;
      const locks = compiled.locks?.items || [];
      const unresolved = [
        "ownerId",
        "routeId",
        "regionId",
        "slotId",
        "componentId",
        "componentUiId",
        "layerId",
        "implementationFile",
        "implementationSelector",
      ];
      host.innerHTML = `
        <section class="visrec2-readout" aria-label="Cobertura de receta">
          <header><strong>Cobertura</strong><span class="${statusClass(
            coverage.status
          )}">${escapeHtml(coverage.status)}</span></header>
          <ul>${Object.entries(coverage.matrix)
            .map(
              ([name, value]) =>
                `<li><span>${escapeHtml(name)}</span><strong class="${statusClass(
                  value
                )}">${escapeHtml(value)}</strong></li>`
            )
            .join("")}</ul>
        </section>
        <section class="visrec2-readout" aria-label="Destino y readiness">
          <header><strong>Destino</strong><code>${escapeHtml(
            state.target
          )}</code></header>
          <ul>
            <li><span>Compatibilidad</span><strong class="${statusClass(
              compat.compatibilityStatus
            )}">${escapeHtml(compat.compatibilityStatus)}</strong></li>
            <li><span>Binding</span><strong class="${statusClass(
              compat.bindingStatus
            )}">${escapeHtml(compat.bindingStatus)}</strong></li>
            <li><span>Receta</span><strong class="${statusClass(
              compat.recipeCoverageStatus
            )}">${escapeHtml(compat.recipeCoverageStatus)}</strong></li>
            <li><span>Aplicación</span><strong class="${statusClass(
              compat.applicationReadiness
            )}">${escapeHtml(compat.applicationReadiness)}</strong></li>
          </ul>
        </section>
        <section class="visrec2-readout" aria-label="Lineage">
          <header><strong>Lineage</strong><code>V2</code></header>
          <ul>
            <li><span>Perfil</span><code>${escapeHtml(
              lineage.identityProfileId
            )}</code></li>
            <li><span>Familia</span><code>${escapeHtml(
              lineage.familyId || "AUTO"
            )}</code></li>
            <li><span>Preset</span><code>${escapeHtml(
              lineage.presetId || "DEFAULT"
            )}</code></li>
            <li><span>Receta</span><code>${escapeHtml(
              lineage.recipeId
            )}</code></li>
            <li><span>Adaptador</span><code>${escapeHtml(
              compat.adapterId
            )}</code></li>
          </ul>
        </section>
        <section class="visrec2-readout" aria-label="Locks">
          <header><strong>Locks</strong><span>${locks.length}</span></header>
          <ul>${
            locks.length
              ? locks
                  .map(
                    (lock) =>
                      `<li><span>${escapeHtml(
                        lock.propertyId
                      )}<small class="visrec2-lock-reason">${escapeHtml(
                        lock.reason
                      )}</small></span><strong>LOCKED</strong></li>`
                  )
                  .join("")
              : "<li><span>Sin locks explícitos</span><strong>—</strong></li>"
          }</ul>
        </section>
        <section class="visrec2-readout" aria-label="Faltantes de binding">
          <header><strong>Unresolved</strong><span>${unresolved.length}</span></header>
          <ul>${unresolved
            .map(
              (field) =>
                `<li><span>${escapeHtml(
                  field
                )}</span><strong class="visrec2-status--blocked">MISSING</strong></li>`
            )
            .join("")}</ul>
        </section>`;

      const score = shell.querySelector("[data-compatibility-score]");
      const list = shell.querySelector("[data-compatibility-list]");
      if (score) score.textContent = `${compat.score}%`;
      if (list)
        list.innerHTML = [
          ...compat.warnings.map(
            (item) =>
              `<li class="is-warning">⚠ ${escapeHtml(
                item.message || item.code
              )}</li>`
          ),
          ...compat.adaptations.map(
            (item) =>
              `<li>↪ ${escapeHtml(item.propertyId)}: ${escapeHtml(
                item.from ?? ""
              )} → ${escapeHtml(item.to ?? "")}</li>`
          ),
          ...(compat.warnings.length || compat.adaptations.length
            ? []
            : [
                '<li class="is-pass">✓ Compatible sin adaptación obligatoria.</li>',
              ]),
        ].join("");
    };

    const renderImportInspection = (inspection) => {
      const host = shell.querySelector("[data-import-comparison]");
      if (!host) return;
      const canonicalRows = Object.entries(
        inspection.canonicalDiff || {}
      ).map(([key, row]) => ({ key, ...row }));
      host.innerHTML = `
        <section class="visrec2-readout">
          <header><strong>${escapeHtml(
            inspection.status
          )}</strong><span class="${statusClass(
        inspection.applicationReadiness
      )}">${escapeHtml(inspection.applicationReadiness)}</span></header>
          <ul>
            <li><span>Checksum</span><strong>${escapeHtml(
              inspection.checksum?.code || "UNKNOWN"
            )}</strong></li>
            <li><span>Migración</span><strong>${escapeHtml(
              inspection.migrationPreview?.status || "NOT_EVALUATED"
            )}</strong></li>
            <li><span>Binding</span><strong>${escapeHtml(
              inspection.bindingStatus || "UNRESOLVED"
            )}</strong></li>
            <li><span>Cobertura</span><strong>${escapeHtml(
              inspection.recipeCoverageStatus || "NOT_EVALUATED"
            )}</strong></li>
          </ul>
          <p>${escapeHtml(inspection.applicationReason || "")}</p>
        </section>
        ${
          canonicalRows.length
            ? `<table><thead><tr><th>Propiedad</th><th>Actual</th><th>Receta</th></tr></thead><tbody>${canonicalRows
                .map(
                  (row) =>
                    `<tr><td>${escapeHtml(row.key)}</td><td>${escapeHtml(
                      typeof row.from === "object"
                        ? JSON.stringify(row.from)
                        : row.from
                    )}</td><td>${escapeHtml(
                      typeof row.to === "object"
                        ? JSON.stringify(row.to)
                        : row.to
                    )}</td></tr>`
                )
                .join("")}</tbody></table>`
            : '<p class="is-pass">Sin diferencias canónicas.</p>'
        }`;
    };

    const taskTableHtml = () => `
      <table class="visrec2-task-table">
        <thead><tr><th>ID</th><th>Capacidad</th><th>Estado</th></tr></thead>
        <tbody>${(transfer.tasks || [])
          .map(
            (task) =>
              `<tr><td><code>${escapeHtml(task.id)}</code></td><td>${escapeHtml(
                task.label || task.name
              )}</td><td><span class="is-pass">${escapeHtml(
                task.status
              )}</span></td></tr>`
          )
          .join("")}</tbody>
      </table>`;

    const buildShell = () => {
      const topActions = document.querySelector(".atlas-top-actions");
      const trigger = document.createElement("button");
      trigger.type = "button";
      trigger.className =
        "atlas-button atlas-recipe-dock-trigger visrec2-trigger";
      trigger.dataset.openVisrec2 = "";
      trigger.setAttribute("aria-controls", "visrec2-console");
      trigger.setAttribute("aria-expanded", "false");
      trigger.innerHTML =
        '<span aria-hidden="true">💾</span><span>Recetas</span>';
      const indexLink = Array.from(
        topActions?.querySelectorAll("a") || []
      ).find((link) => link.getAttribute("href") === "index.html");
      topActions?.insertBefore(trigger, indexLink || null);

      const wrapper = document.createElement("div");
      wrapper.className = "visrec2-shell";
      wrapper.dataset.visrec2Console = "";
      wrapper.setAttribute("aria-hidden", "true");
      wrapper.innerHTML = `
        <button class="visrec2-backdrop" type="button" data-visrec2-close aria-label="Cerrar consola"></button>
        <aside class="visrec2-console" id="visrec2-console" role="dialog" aria-modal="true" aria-labelledby="visrec2-title" tabindex="-1">
          <header class="visrec2-header">
            <div><p class="atlas-eyebrow">PRISMA Visual Transfer Console</p><h2 id="visrec2-title">Receta precisa y portátil</h2><p>${escapeHtml(
              bridge.pageLabel()
            )}</p></div>
            <button class="atlas-icon-button" type="button" data-visrec2-close aria-label="Cerrar">✕</button>
          </header>
          <nav class="visrec2-tabs" aria-label="Secciones de Recetas">
            ${[
              ["select", "Seleccionar"],
              ["design", "Diseño"],
              ["states", "Estados"],
              ["transfer", "Transferir"],
              ["import", "Importar"],
              ["tasks", "20 tasks"],
            ]
              .map(
                ([id, label], index) =>
                  `<button type="button" data-visrec2-tab="${id}" class="${
                    index === 0 ? "is-active" : ""
                  }">${label}</button>`
              )
              .join("")}
          </nav>
          <div class="visrec2-body">
            <section class="visrec2-pane is-active" data-visrec2-pane="select">
              <div class="visrec2-actions"><button class="atlas-button atlas-button--accent" type="button" data-start-select>◎ Seleccionar objeto</button><button class="atlas-button" type="button" data-refresh-inventory>Actualizar inventario</button></div>
              <div class="visrec2-selection" data-selection-summary></div>
              <fieldset class="visrec2-segment"><legend>Alcance exacto</legend>${transfer.scopes
                .map(
                  (scope) =>
                    `<label><input type="radio" name="visrec2-scope" value="${escapeHtml(
                      scope.id
                    )}" ${
                      scope.id === "element" ? "checked" : ""
                    }><span>${escapeHtml(scope.label)}</span></label>`
                )
                .join("")}</fieldset>
              <div class="visrec2-inventory-summary" data-inventory-summary></div>
              <div class="visrec2-inventory" data-inventory-list></div>
              <section><h3>IDs y huellas</h3><div class="visrec2-identity" data-identity-table></div></section>
            </section>
            <section class="visrec2-pane" data-visrec2-pane="design">
              <div data-family-control></div>
              <div class="visrec2-property-controls" data-property-controls></div>
              <div class="visrec2-layer-block">
                <h3>Capas globales de esta superficie</h3>
                ${Object.entries(bridge.layerDefaults)
                  .map(
                    ([name, value]) =>
                      `<label><span>${escapeHtml(
                        name
                      )}</span><span class="visrec2-range"><input type="range" min="0" max="100" step="1" value="${value}" data-visrec2-layer="${escapeHtml(
                        name
                      )}"><output>${value}%</output></span></label>`
                  )
                  .join("")}
                <div class="visrec2-accent-grid">${(
                  bridge.manifest.accent_roles || []
                )
                  .map(
                    (accent) =>
                      `<button type="button" data-visrec2-accent="${escapeHtml(
                        accent.id
                      )}" style="--visrec2-accent:${escapeHtml(
                        accent.rgb
                      )}" title="${escapeHtml(
                        accent.purpose
                      )}"><span></span>${escapeHtml(accent.name)}</button>`
                  )
                  .join("")}</div>
              </div>
              <div class="visrec2-actions"><button class="atlas-button" type="button" data-reset-graphite>Restaurar grafito</button><button class="atlas-button" type="button" data-clear-preview>Limpiar preview</button></div>
            </section>
            <section class="visrec2-pane" data-visrec2-pane="states">
              <fieldset class="visrec2-segment"><legend>Estado</legend>${transfer.states
                .map(
                  (item) =>
                    `<label><input type="radio" name="visrec2-state" value="${escapeHtml(
                      item.id
                    )}" ${
                      item.id === "default" ? "checked" : ""
                    }><span>${escapeHtml(item.label)}</span></label>`
                )
                .join("")}</fieldset>
              <fieldset class="visrec2-segment"><legend>Variante</legend>${transfer.variants
                .map(
                  (item) =>
                    `<label><input type="radio" name="visrec2-variant" value="${escapeHtml(
                      item.id
                    )}" ${
                      item.id === "base" ? "checked" : ""
                    }><span>${escapeHtml(item.label)}</span></label>`
                )
                .join("")}</fieldset>
              <label class="visrec2-field"><span>Versión</span><input type="text" value="2.0.0" data-version></label>
              <div class="visrec2-checks"><label><input type="checkbox" data-golden>★ Golden Recipe</label><label><input type="checkbox" data-frozen>❄ Congelada</label></div>
              <label class="visrec2-field"><span>Intención visual</span><textarea rows="4" data-intent placeholder="Debe sentirse táctil, luminoso y premium…"></textarea></label>
              <fieldset class="visrec2-checks"><legend>Reglas No tocar</legend>${transfer.no_touch_rules
                .map(
                  (item) =>
                    `<label><input type="checkbox" value="${escapeHtml(
                      item.id
                    )}" data-no-touch ${
                      state.noTouch.has(item.id) ? "checked" : ""
                    }>${escapeHtml(item.label)}</label>`
                )
                .join("")}</fieldset>
            </section>
            <section class="visrec2-pane" data-visrec2-pane="transfer">
              <fieldset class="visrec2-segment"><legend>Modo de traslado</legend>${transfer.transfer_modes
                .map(
                  (item) =>
                    `<label><input type="radio" name="visrec2-mode" value="${escapeHtml(
                      item.id
                    )}" ${
                      item.id === "adaptive" ? "checked" : ""
                    }><span>${escapeHtml(item.label)}</span></label>`
                )
                .join("")}</fieldset>
              <fieldset class="visrec2-segment"><legend>Destino deseado</legend>${transfer.targets
                .map(
                  (item) =>
                    `<label><input type="radio" name="visrec2-target" value="${escapeHtml(
                      item.id
                    )}" ${
                      item.id === "neutral" ? "checked" : ""
                    }><span>${escapeHtml(item.label)}</span></label>`
                )
                .join("")}</fieldset>
              <section class="visrec2-compatibility"><header><span>Compatibilidad</span><strong data-compatibility-score>100%</strong></header><ul data-compatibility-list></ul></section>
              <div class="visrec2-governance-grid" data-governance-readouts></div>
              <div class="visrec2-actions"><button class="atlas-button" type="button" data-add-collection>Añadir selección</button><button class="atlas-button" type="button" data-export-selection>Exportar selección</button><button class="atlas-button" type="button" data-export-page>Guardar página</button><button class="atlas-button atlas-button--accent" type="button" data-export-collection>Guardar colección</button></div>
              <ul class="visrec2-collection" data-collection-list></ul>
              <section class="visrec2-delta"><h3>Delta entre dos elementos</h3><div class="visrec2-actions"><button class="atlas-button" type="button" data-capture-a>Capturar A</button><button class="atlas-button" type="button" data-capture-b>Capturar B</button><button class="atlas-button" type="button" data-export-delta>Exportar delta</button></div><div data-delta-summary></div></section>
              <h3>Historial local</h3><ul class="visrec2-history" data-history-list></ul>
            </section>
            <section class="visrec2-pane" data-visrec2-pane="import">
              <label class="visrec2-import"><span>Importar receta en modo lectura</span><input type="file" accept=".json,.prisma-visual.json,application/json" data-import-transfer></label>
              <div class="visrec2-import-comparison" data-import-comparison><p>Selecciona un archivo para validar checksum, migración y cobertura.</p></div>
            </section>
            <section class="visrec2-pane" data-visrec2-pane="tasks">${taskTableHtml()}</section>
          </div>
        </aside>
        <div class="visrec2-highlight" data-visrec2-highlight hidden><span></span></div>`;
      document.querySelector(".atlas-shell")?.appendChild(wrapper);
      return { wrapper, trigger };
    };

    const built = buildShell();
    shell = built.wrapper;
    const trigger = built.trigger;
    const panel = shell.querySelector(".visrec2-console");
    state.highlight = shell.querySelector("[data-visrec2-highlight]");

    const activateTab = (tabId) => {
      shell
        .querySelectorAll("[data-visrec2-tab]")
        .forEach((item) =>
          item.classList.toggle("is-active", item.dataset.visrec2Tab === tabId)
        );
      shell
        .querySelectorAll("[data-visrec2-pane]")
        .forEach((pane) =>
          pane.classList.toggle("is-active", pane.dataset.visrec2Pane === tabId)
        );
    };

    const focusables = () =>
      Array.from(
        panel.querySelectorAll(
          'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'
        )
      ).filter((element) => element.getClientRects().length > 0);

    const openConsole = (open) => {
      state.open = Boolean(open);
      if (state.open) state.returnFocus = document.activeElement;
      shell.dataset.open = String(state.open);
      shell.setAttribute("aria-hidden", String(!state.open));
      trigger.setAttribute("aria-expanded", String(state.open));
      bridge.body.classList.toggle("is-visrec2-open", state.open);
      if (state.open) {
        buildInventory();
        requestAnimationFrame(() => panel.focus());
      } else {
        stopSelecting();
        state.returnFocus?.focus?.();
        state.returnFocus = null;
      }
    };

    trigger.addEventListener("click", () => openConsole(!state.open));
    shell
      .querySelectorAll("[data-visrec2-close]")
      .forEach((button) =>
        button.addEventListener("click", () => openConsole(false))
      );
    shell.querySelectorAll("[data-visrec2-tab]").forEach((button) => {
      button.addEventListener("click", () => {
        activateTab(button.dataset.visrec2Tab);
      });
    });
    shell
      .querySelector("[data-start-select]")
      ?.addEventListener("click", startSelecting);
    shell
      .querySelector("[data-refresh-inventory]")
      ?.addEventListener("click", buildInventory);
    shell
      .querySelectorAll('input[name="visrec2-scope"]')
      .forEach((input) =>
        input.addEventListener("change", () => {
          state.scope = input.value;
          renderSelection();
          applyPreview();
        })
      );
    shell
      .querySelectorAll('input[name="visrec2-state"]')
      .forEach((input) =>
        input.addEventListener("change", () => {
          state.activeState = input.value;
          applyPreview();
        })
      );
    shell
      .querySelectorAll('input[name="visrec2-variant"]')
      .forEach((input) =>
        input.addEventListener("change", () => {
          state.activeVariant = input.value;
          applyPreview();
        })
      );
    shell
      .querySelectorAll('input[name="visrec2-mode"]')
      .forEach((input) =>
        input.addEventListener("change", () => {
          state.transferMode = input.value;
          renderGovernance();
        })
      );
    shell
      .querySelectorAll('input[name="visrec2-target"]')
      .forEach((input) =>
        input.addEventListener("change", () => {
          state.target = input.value;
          compile();
          renderGovernance();
        })
      );
    shell
      .querySelector("[data-version]")
      ?.addEventListener("input", (event) => {
        state.version = event.target.value || "2.0.0";
      });
    shell
      .querySelector("[data-golden]")
      ?.addEventListener("change", (event) => {
        state.golden = event.target.checked;
      });
    shell
      .querySelector("[data-frozen]")
      ?.addEventListener("change", (event) => {
        state.frozen = event.target.checked;
        panel.classList.toggle("is-frozen", state.frozen);
      });
    shell
      .querySelector("[data-intent]")
      ?.addEventListener("input", (event) => {
        state.intent = event.target.value;
      });
    shell.querySelectorAll("[data-no-touch]").forEach((input) => {
      input.addEventListener("change", () => {
        if (input.checked) state.noTouch.add(input.value);
        else state.noTouch.delete(input.value);
      });
    });
    shell.querySelectorAll("[data-visrec2-layer]").forEach((input) => {
      input.addEventListener("input", () => {
        bridge.applyLayer(input.dataset.visrec2Layer, input.value);
        input
          .closest(".visrec2-range")
          ?.querySelector("output")
          ?.replaceChildren(`${input.value}%`);
      });
    });
    shell.querySelectorAll("[data-visrec2-accent]").forEach((button) => {
      button.addEventListener("click", () =>
        bridge.setAccent(button.dataset.visrec2Accent, { persist: true })
      );
    });
    shell
      .querySelector("[data-reset-graphite]")
      ?.addEventListener("click", () => {
        Object.entries(bridge.layerDefaults).forEach(([name, value]) =>
          bridge.applyLayer(name, value)
        );
        bridge.setAccent("graphite", { persist: true });
        clearPreview();
      });
    shell
      .querySelector("[data-clear-preview]")
      ?.addEventListener("click", clearPreview);
    shell
      .querySelector("[data-add-collection]")
      ?.addEventListener("click", addCollection);
    shell
      .querySelector("[data-export-selection]")
      ?.addEventListener("click", () => exportPayload("selection"));
    shell
      .querySelector("[data-export-page]")
      ?.addEventListener("click", () => exportPayload("page"));
    shell
      .querySelector("[data-export-collection]")
      ?.addEventListener("click", () => exportPayload("collection"));
    shell
      .querySelector("[data-capture-a]")
      ?.addEventListener("click", () => captureDelta("A"));
    shell
      .querySelector("[data-capture-b]")
      ?.addEventListener("click", () => captureDelta("B"));
    shell
      .querySelector("[data-export-delta]")
      ?.addEventListener("click", () => exportPayload("delta"));
    shell
      .querySelector("[data-import-transfer]")
      ?.addEventListener("change", async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;
        try {
          const payload = JSON.parse(await file.text());
          const inspection = await importInspector.inspect(payload, {
            registry,
            currentCanonicalValues: state.compiled?.canonicalValues || {},
            currentResolvedValues: resolvedValueMap(
              state.selected || bridge.body
            ),
          });
          state.imported =
            inspection.status === "INSPECTED_READ_ONLY"
              ? inspection.inspectedPayload
              : null;
          renderImportInspection(inspection);
          bridge.toast(
            inspection.checksum?.ok
              ? "Importación inspeccionada en modo lectura."
              : "Importación bloqueada por checksum."
          );
        } catch (error) {
          renderImportInspection({
            status: "BLOCKED",
            applicationReadiness: "BLOCKED",
            checksum: { code: "JSON_INVALID" },
            applicationReason: `Archivo inválido: ${error.message}`,
          });
        } finally {
          event.target.value = "";
        }
      });

    document.addEventListener(
      "pointermove",
      (event) => {
        if (state.selecting)
          highlight(selectionEngine.selectableFrom(event.target));
      },
      true
    );
    document.addEventListener(
      "click",
      (event) => {
        if (!state.selecting) return;
        const element = selectionEngine.selectableFrom(event.target);
        if (!element) return;
        event.preventDefault();
        event.stopPropagation();
        stopSelecting();
        setSelected(element);
        openConsole(true);
      },
      true
    );
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && state.selecting) {
        event.preventDefault();
        stopSelecting();
        return;
      }
      if (event.key === "Escape" && state.open) {
        event.preventDefault();
        openConsole(false);
        return;
      }
      if (event.key !== "Tab" || !state.open) return;
      const items = focusables();
      if (!items.length) {
        event.preventDefault();
        panel.focus();
        return;
      }
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
    window.addEventListener(
      "scroll",
      () => {
        if (state.selecting) highlight(null);
      },
      { passive: true, capture: true }
    );

    renderSelection();
    renderFamilyControls();
    renderPropertyControls();
    renderIds();
    renderCollection();
    renderDelta();
    renderHistory();
    compile();
    renderGovernance();
    buildInventory();

    const query = new URLSearchParams(window.location.search);
    if (
      query.get("recipeDock") === "open" ||
      query.get("visrec2") === "open"
    ) {
      openConsole(true);
    }
    const qaMode = query.get("visrec2Qa");
    if (qaMode) {
      const candidate =
        state.inventory.find((item) => item.type === "button") ||
        state.inventory[0];
      if (candidate) setSelected(candidate.element);
      if (qaMode === "coverage") activateTab("transfer");
      if (qaMode === "selector" && candidate) {
        activateTab("select");
        startSelecting();
        highlight(candidate.element);
      }
      if (qaMode === "state") {
        activateTab("states");
        state.activeState = "hover";
        shell.querySelector(
          'input[name="visrec2-state"][value="hover"]'
        ).checked = true;
        applyPreview();
      }
      if (qaMode === "import") activateTab("import");
      if (qaMode === "scroll") {
        activateTab("transfer");
        requestAnimationFrame(() => {
          const body = shell.querySelector(".visrec2-body");
          if (body) body.scrollTop = body.scrollHeight;
        });
      }
      if (qaMode === "focus") {
        activateTab("transfer");
        requestAnimationFrame(() =>
          shell.querySelector("[data-export-selection]")?.focus()
        );
      }
    }

    const publicApi = {
      version: transfer.version,
      schema: transfer.schema,
      tasks: transfer.tasks,
      visibleControlContract: visibleContract,
      open: () => openConsole(true),
      close: () => openConsole(false),
      select: startSelecting,
      exportSelection: () => exportPayload("selection"),
      exportKind: (kind) => exportPayload(kind),
      inspect: (payload) =>
        importInspector.inspect(payload, {
          registry,
          currentCanonicalValues: state.compiled?.canonicalValues || {},
          currentResolvedValues: resolvedValueMap(
            state.selected || bridge.body
          ),
        }),
      setInternalTarget: (surfaceId) => {
        const known =
          registry.v2_internal_registries?.adapters?.items?.some(
            (item) => item.surfaceId === surfaceId
          );
        if (!known) throw new Error(`Adaptador desconocido: ${surfaceId}`);
        state.target = surfaceId;
        compile();
        renderGovernance();
      },
      applicationAllowed: false,
      productMutationAllowed: false,
    };
    Object.defineProperty(window, "PRISMA_VISREC2", {
      configurable: true,
      enumerable: true,
      value: Object.freeze(publicApi),
      writable: false,
    });
    return publicApi;
  };

  modules["console-engine"] = Object.freeze({ init });
})();
