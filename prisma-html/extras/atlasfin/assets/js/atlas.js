
(() => {
  const manifest = window.PRISMA_ATLAS_MANIFEST;
  const root = document.documentElement;
  const body = document.body;

  const accentById = Object.fromEntries(
    manifest.accent_roles.map((accent) => [accent.id, accent])
  );

  // PRISMA Atlas Chroma Balance 01.
  // Every page has a semantic palette. A manual choice remains available,
  // but page defaults are no longer written into storage as accidental graphite.
  const pagePaletteById = {
    INDEX: ["cyan", "violet", "amber"],
    A: ["cyan", "violet", "amber"],
    B: ["violet", "cyan", "pink"],
    C: ["emerald", "cyan", "amber"],
    D: ["cyan", "violet", "emerald"],
    E: ["amber", "violet", "cyan"],
    F: ["cyan", "magenta", "violet"],
    G: ["violet", "cyan", "pink"],
    H: ["navy", "cyan", "violet"],
    I: ["violet", "pink", "cyan"],
    J: ["cyan", "violet", "emerald"],
    K: ["emerald", "amber", "cyan"],
    L: ["violet", "cyan", "magenta"],
    M: ["magenta", "violet", "amber"],
    N: ["emerald", "cyan", "amber"],
    O: ["pink", "violet", "cyan"],
    P: ["cyan", "magenta", "violet"],
    Q: ["amber", "cyan", "emerald"],
    R: ["pink", "violet", "amber"],
    S: ["violet", "cyan", "magenta"],
    T: ["cyan", "pink", "violet"],
    U: ["amber", "pink", "cyan"],
    V: ["amber", "emerald", "magenta"],
    W: ["navy", "violet", "cyan"],
    X: ["magenta", "amber", "cyan"],
    Y: ["cyan", "pink", "amber"],
    Z: ["navy", "cyan", "violet"],
  };

  const pageId = body.dataset.atlasPage || "INDEX";
  const pagePalette = pagePaletteById[pageId] || pagePaletteById.INDEX;
  const userAccentKey = "prisma-atlas-accent-user-v1";
  const migrationKey = "prisma-atlas-chroma-migrated-v1";

  const role = (id, fallback) => accentById[id] || accentById[fallback] || accentById.cyan;
  const secondary = role(pagePalette[1], "violet");
  const tertiary = role(pagePalette[2], "amber");
  root.style.setProperty("--atlas-accent-2", secondary.rgb);
  root.style.setProperty("--atlas-accent-3", tertiary.rgb);
  root.dataset.atlasPage = pageId;

  if (!localStorage.getItem(migrationKey)) {
    // The old key was polluted because the previous initializer persisted graphite
    // even when the user never selected it. Keep only the new explicit-user key.
    localStorage.removeItem("prisma-atlas-accent-v4");
    localStorage.setItem(migrationKey, "done");
  }

  const setAccent = (id, { persist = false } = {}) => {
    const accent = role(id, pagePalette[0]);
    root.style.setProperty("--atlas-accent", accent.rgb);
    root.style.setProperty("--atlas-accent-hex", accent.value);
    root.dataset.accent = accent.id;
    body.dataset.accentMode = persist ? "manual" : "page";
    if (persist) localStorage.setItem(userAccentKey, accent.id);
    document.querySelectorAll("[data-accent-choice]").forEach((item) => {
      item.classList.toggle("is-active", item.dataset.accentChoice === accent.id);
    });
  };

  const usePageAccent = () => {
    localStorage.removeItem(userAccentKey);
    setAccent(body.dataset.defaultAccent || pagePalette[0]);
  };

  setAccent(localStorage.getItem(userAccentKey) || body.dataset.defaultAccent || pagePalette[0]);

  document.querySelectorAll("[data-accent-choice]").forEach((button) => {
    button.addEventListener("click", () => setAccent(button.dataset.accentChoice, { persist: true }));
  });

  const topActions = document.querySelector(".atlas-top-actions");
  if (topActions) {
    const autoAccent = document.createElement("button");
    autoAccent.type = "button";
    autoAccent.className = "atlas-icon-button atlas-auto-accent";
    autoAccent.textContent = "◈";
    autoAccent.title = "Usar la paleta semántica de esta hoja";
    autoAccent.setAttribute("aria-label", "Usar color automático de esta hoja");
    autoAccent.addEventListener("click", usePageAccent);
    topActions.prepend(autoAccent);
  }

  const revealObserver = "IntersectionObserver" in window
    ? new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              revealObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.08, rootMargin: "40px 0px -20px" }
      )
    : null;

  document.querySelectorAll(".atlas-reveal").forEach((node) => {
    if (revealObserver) revealObserver.observe(node);
    else node.classList.add("is-visible");
  });

  requestAnimationFrame(() => {
    requestAnimationFrame(() => body.classList.add("is-ready"));
  });

  const command = document.querySelector(".atlas-command");
  const commandInput = document.querySelector(".atlas-command__input");
  const results = document.querySelector(".atlas-command__results");

  const allItems = manifest.sections.flatMap((section) =>
    section.items.map((item) => ({
      ...item,
      sectionTitle: section.title,
      implemented: manifest.implemented_sections.includes(section.letter),
    }))
  );

  const pageMap = {
    A: "a-fundamentos.html",
    B: "b-materiales.html",
    C: "c-acciones.html",
    D: "d-entrada-texto.html",
    E: "e-seleccion-filtros.html",
    F: "f-navegacion.html",
    G: "g-tablas.html",
    M: "m-overlays.html",
    Z: "z-gobierno.html",
  };

  const renderResults = (query = "") => {
    const normalized = query.trim().toLowerCase();
    const filtered = allItems
      .filter((item) => {
        if (!normalized) return item.implemented;
        return [item.name, item.description, item.sectionTitle, item.id]
          .join(" ")
          .toLowerCase()
          .includes(normalized);
      })
      .slice(0, 40);

    results.innerHTML = filtered.length
      ? filtered
          .map(
            (item) => `
          <button class="atlas-search-result" type="button"
            data-result-section="${item.section}"
            data-result-slug="${item.slug}"
            data-result-implemented="${item.implemented}">
            <span class="atlas-search-result__section">${item.section}</span>
            <span class="atlas-search-result__copy">
              <strong>${escapeHtml(item.name)}</strong>
              <small>${escapeHtml(item.description)}</small>
            </span>
            <span class="atlas-search-result__status">
              ${item.implemented ? "Abrir" : "Lote futuro"}
            </span>
          </button>`
          )
          .join("")
      : `<div class="atlas-card"><strong>Sin resultados</strong><p>Prueba con tabla, smoke, modal, licencia, rosa o foco.</p></div>`;
  };

  const openCommand = () => {
    command?.classList.add("is-open");
    command?.setAttribute("aria-hidden", "false");
    renderResults(commandInput?.value || "");
    setTimeout(() => commandInput?.focus(), 20);
  };

  const closeCommand = () => {
    command?.classList.remove("is-open");
    command?.setAttribute("aria-hidden", "true");
  };

  document.querySelectorAll("[data-open-search]").forEach((button) => {
    button.addEventListener("click", openCommand);
  });

  document.querySelectorAll("[data-close-search]").forEach((button) => {
    button.addEventListener("click", closeCommand);
  });

  commandInput?.addEventListener("input", (event) => renderResults(event.target.value));

  results?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-result-section]");
    if (!button) return;
    if (button.dataset.resultImplemented !== "true") return;
    const page = pageMap[button.dataset.resultSection];
    const slug = button.dataset.resultSlug;
    window.location.href = `${page}#${slug}`;
  });

  document.addEventListener("keydown", (event) => {
    const isSearchShortcut =
      (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k";
    if (isSearchShortcut) {
      event.preventDefault();
      openCommand();
    }
    if (event.key === "Escape") {
      closeCommand();
      closeOverlay();
    }
  });

  const motionButton = document.querySelector("[data-motion-cycle]");
  const motionModes = ["normal", "reduced", "off"];
  const savedMotion = localStorage.getItem("prisma-atlas-motion") || "normal";
  root.dataset.motion = savedMotion;
  if (motionButton) motionButton.dataset.mode = savedMotion;

  motionButton?.addEventListener("click", () => {
    const current = root.dataset.motion || "normal";
    const next = motionModes[(motionModes.indexOf(current) + 1) % motionModes.length];
    root.dataset.motion = next;
    motionButton.dataset.mode = next;
    motionButton.setAttribute("aria-label", `Movimiento: ${next}`);
    localStorage.setItem("prisma-atlas-motion", next);
  });

  document.querySelectorAll("[data-replay-motion]").forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".atlas-motion-card");
      card.classList.remove("is-playing");
      void card.offsetWidth;
      card.classList.add("is-playing");
    });
  });

  const layerDefaults = {
    smoke: 8,
    chrome: 28,
    content: 20,
  };

  const layerVariables = {
    smoke: "--atlas-smoke",
    chrome: "--atlas-chrome-alpha",
    content: "--atlas-content-alpha",
  };

  const layerStorageKey = (name) => `prisma-atlas-layer-v4-${name}`;

  const applyLayer = (name, value, persist = true) => {
    const normalized = Math.max(0, Math.min(100, Number(value)));
    const variable = layerVariables[name];
    if (!variable) return;

    root.style.setProperty(variable, normalized / 100);
    const stateName = `atlasLayer${name.charAt(0).toUpperCase()}${name.slice(1)}`;
    root.dataset[stateName] = normalized === 0 ? "zero" : "active";

    document
      .querySelectorAll(`[data-layer-control="${name}"]`)
      .forEach((control) => {
        control.value = String(normalized);
      });

    document
      .querySelectorAll(`[data-layer-output="${name}"]`)
      .forEach((output) => {
        output.textContent = `${Math.round(normalized)}%`;
      });

    if (persist) {
      localStorage.setItem(layerStorageKey(name), String(normalized));
    }
  };

  Object.entries(layerDefaults).forEach(([name, fallback]) => {
    const raw = localStorage.getItem(layerStorageKey(name));
    const value = raw === null ? fallback : Number(raw);
    applyLayer(name, Number.isFinite(value) ? value : fallback, false);
  });

  document.querySelectorAll("[data-layer-control]").forEach((control) => {
    control.addEventListener("input", (event) => {
      applyLayer(control.dataset.layerControl, event.target.value);
    });
  });

  document.querySelector("[data-reset-layers]")?.addEventListener("click", () => {
    Object.entries(layerDefaults).forEach(([name, value]) => {
      applyLayer(name, value);
    });
    setAccent("graphite");
  });

  // Table lab.
  document.querySelectorAll("[data-atlas-table]").forEach((table) => {
    table.querySelectorAll("th[data-sort]").forEach((header) => {
      header.addEventListener("click", () => {
        const tbody = table.tBodies[0];
        const index = Array.from(header.parentElement.children).indexOf(header);
        const rows = Array.from(tbody.rows);
        const direction = header.dataset.direction === "asc" ? "desc" : "asc";
        header.dataset.direction = direction;
        rows.sort((a, b) => {
          const av = a.cells[index]?.innerText.trim() || "";
          const bv = b.cells[index]?.innerText.trim() || "";
          return direction === "asc"
            ? av.localeCompare(bv, "es", { numeric: true })
            : bv.localeCompare(av, "es", { numeric: true });
        });
        rows.forEach((row) => tbody.appendChild(row));
      });
    });

    table.querySelectorAll("tbody tr[data-selectable]").forEach((row) => {
      row.addEventListener("click", (event) => {
        if (event.target.closest("[contenteditable], button, a, input")) return;
        row.classList.toggle("is-selected");
      });
    });
  });

  // Overlay lab.
  let overlayRoot = null;
  let previousFocus = null;

  const overlayContent = (type, title) => {
    const body = {
      tooltip: "Ayuda breve, no interactiva y ligada al foco.",
      toggletip: "Ayuda interactiva con acciones secundarias.",
      popover: "Contenido contextual sin bloquear la tarea.",
      menu: "Lista temporal de acciones relacionadas.",
      context: "Acciones específicas del elemento seleccionado.",
      modal: "Decisión importante que bloquea el fondo.",
      confirm: "Confirma una acción antes de ejecutarla.",
      destructive: "Confirma una operación irreversible.",
      drawer: "Detalle secundario desde el borde derecho.",
      sheet: "Superficie temporal desde la parte inferior.",
      notification: "Notificaciones agrupadas con estado.",
      command: "Búsqueda global de acciones y componentes.",
      dismiss: "Cierra al tocar el fondo.",
      focus: "Mantiene el teclado dentro del overlay activo.",
    }[type] || "Componente temporal gobernado.";

    return `
      <button class="atlas-icon-button atlas-overlay-close" type="button" data-overlay-close aria-label="Cerrar">✕</button>
      <p class="atlas-eyebrow">${escapeHtml(type)}</p>
      <h2>${escapeHtml(title)}</h2>
      <p>${escapeHtml(body)}</p>
      <div class="atlas-contract">
        <div class="atlas-contract__row"><span class="atlas-contract__key">Material</span><span class="atlas-contract__value">Overlay smoke fuerte, un solo blur.</span></div>
        <div class="atlas-contract__row"><span class="atlas-contract__key">Foco</span><span class="atlas-contract__value">Borde sólido más halo, Escape cierra.</span></div>
        <div class="atlas-contract__row"><span class="atlas-contract__key">Capas</span><span class="atlas-contract__value">Una superficie temporal, sin paneles anidados.</span></div>
      </div>
      <div class="atlas-hero__meta">
        <button class="atlas-button atlas-button--primary" type="button" data-overlay-close>Entendido</button>
        <button class="atlas-button" type="button" data-overlay-close>Cancelar</button>
      </div>`;
  };

  const focusables = (rootNode) =>
    Array.from(
      rootNode.querySelectorAll(
        'button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])'
      )
    );

  const openOverlay = (type, title, trigger) => {
    closeOverlay();
    previousFocus = trigger || document.activeElement;
    overlayRoot = document.createElement("div");
    overlayRoot.className = "atlas-overlay-root";
    overlayRoot.innerHTML = `
      <div class="atlas-overlay-backdrop" data-overlay-close></div>
      <section class="atlas-overlay-panel" data-type="${escapeHtml(type)}" role="dialog" aria-modal="true" aria-label="${escapeHtml(title)}">
        ${overlayContent(type, title)}
      </section>`;
    document.body.appendChild(overlayRoot);

    overlayRoot.addEventListener("click", (event) => {
      if (event.target.closest("[data-overlay-close]")) closeOverlay();
    });

    overlayRoot.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      const items = focusables(overlayRoot);
      if (!items.length) return;
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

    setTimeout(() => focusables(overlayRoot)[0]?.focus(), 30);
  };

  function closeOverlay() {
    if (!overlayRoot) return;
    overlayRoot.remove();
    overlayRoot = null;
    previousFocus?.focus?.();
  }

  document.querySelectorAll("[data-overlay-demo]").forEach((button) => {
    button.addEventListener("click", () => {
      openOverlay(button.dataset.overlayDemo, button.dataset.overlayTitle, button);
    });
  });

  // Correct/anti-pattern toggles.
  document.querySelectorAll("[data-toggle-antipattern]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.querySelector(button.dataset.toggleAntipattern);
      target?.toggleAttribute("hidden");
    });
  });

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  // ---------------------------------------------------------------
  // Batch 2: Materials
  // ---------------------------------------------------------------
  const materialPresets = {
    shell: {
      name: "Shell Material",
      description: "Chrome global con saturación óptica y humo moderado.",
      alpha: 28,
      blur: 22,
      saturation: 182,
      scrim: 12,
    },
    navigation: {
      name: "Navigation Material",
      description: "Navegación persistente con lectura y difracción en bordes.",
      alpha: 24,
      blur: 20,
      saturation: 170,
      scrim: 10,
    },
    panel: {
      name: "Panel Material",
      description: "Contenedor funcional para información relacionada.",
      alpha: 34,
      blur: 18,
      saturation: 140,
      scrim: 15,
    },
    card: {
      name: "Card Material",
      description: "Pieza ligera dentro de una colección, sin blur propio.",
      alpha: 18,
      blur: 0,
      saturation: 110,
      scrim: 8,
    },
    control: {
      name: "Control Material",
      description: "Superficie compacta para inputs, selects y botones.",
      alpha: 26,
      blur: 0,
      saturation: 112,
      scrim: 8,
    },
    overlay: {
      name: "Overlay Material",
      description: "Superficie temporal con smoke fuerte y foco contenido.",
      alpha: 88,
      blur: 24,
      saturation: 132,
      scrim: 48,
    },
  };

  const materialSample = document.querySelector("[data-material-sample]");
  const materialStage = document.querySelector("[data-material-stage]");

  const applyMaterialValue = (name, value) => {
    if (!materialSample) return;
    const normalized = Number(value);
    if (name === "alpha") {
      materialSample.style.setProperty("--sample-alpha", normalized / 100);
      document.querySelector('[data-material-output="alpha"]')?.replaceChildren(`${normalized}%`);
    }
    if (name === "blur") {
      materialSample.style.setProperty("--sample-blur", `${normalized}px`);
      document.querySelector('[data-material-output="blur"]')?.replaceChildren(`${normalized} px`);
    }
    if (name === "saturation") {
      materialSample.style.setProperty("--sample-saturation", normalized / 100);
      document.querySelector('[data-material-output="saturation"]')?.replaceChildren(`${normalized}%`);
    }
  };

  const applyMaterialPreset = (id) => {
    const preset = materialPresets[id];
    if (!preset || !materialSample) return;
    document.querySelector("[data-material-name]")?.replaceChildren(preset.name);
    document.querySelector("[data-material-description]")?.replaceChildren(preset.description);
    if (materialStage) {
      materialStage.style.setProperty("--material-scrim", preset.scrim / 100);
    }
    ["alpha", "blur", "saturation"].forEach((name) => {
      const value = preset[name];
      document.querySelector(`[data-material-control="${name}"]`)?.setAttribute("value", String(value));
      const control = document.querySelector(`[data-material-control="${name}"]`);
      if (control) control.value = String(value);
      applyMaterialValue(name, value);
    });
    document.querySelectorAll("[data-material-preset]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.materialPreset === id);
    });
  };

  document.querySelectorAll("[data-material-preset]").forEach((button) => {
    button.addEventListener("click", () => applyMaterialPreset(button.dataset.materialPreset));
  });

  document.querySelectorAll("[data-material-control]").forEach((control) => {
    control.addEventListener("input", () => {
      applyMaterialValue(control.dataset.materialControl, control.value);
    });
  });

  if (materialSample) applyMaterialPreset("panel");

  // ---------------------------------------------------------------
  // Batch 2: Actions
  // ---------------------------------------------------------------
  document.querySelectorAll("[data-toggle-action]").forEach((button) => {
    button.addEventListener("click", () => {
      const pressed = button.getAttribute("aria-pressed") !== "true";
      button.setAttribute("aria-pressed", String(pressed));
      button.textContent = pressed ? "★ Favorito" : "☆ Favorito";
    });
  });

  document.querySelectorAll("[data-loading-action]").forEach((button) => {
    button.addEventListener("click", () => {
      if (button.classList.contains("is-loading")) return;
      const original = button.textContent;
      button.classList.add("is-loading");
      button.setAttribute("aria-busy", "true");
      setTimeout(() => {
        button.classList.remove("is-loading");
        button.removeAttribute("aria-busy");
        button.textContent = "Reporte listo ✓";
        setTimeout(() => {
          button.textContent = original;
        }, 1100);
      }, 1200);
    });
  });

  document.querySelectorAll("[data-menu-button]").forEach((button) => {
    const menu = button.parentElement?.querySelector("[data-action-menu]");
    button.addEventListener("click", () => {
      const open = !menu?.classList.contains("is-open");
      document.querySelectorAll("[data-action-menu].is-open").forEach((other) => {
        other.classList.remove("is-open");
      });
      menu?.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", String(open));
      if (open) menu?.querySelector('[role="menuitem"]')?.focus();
    });
  });

  // ---------------------------------------------------------------
  // Batch 2: Text fields
  // ---------------------------------------------------------------
  document.querySelectorAll("[data-clear-input]").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.closest(".prisma-field__control")?.querySelector("[data-clearable-input]");
      if (input) {
        input.value = "";
        input.focus();
      }
    });
  });

  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    const input = button.closest(".prisma-field__control")?.querySelector("[data-password-input]");
    button.addEventListener("click", () => {
      if (!input) return;
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.setAttribute("aria-label", reveal ? "Ocultar contraseña" : "Mostrar contraseña");
      button.textContent = reveal ? "◌" : "◉";
      input.focus();
    });
  });

  document.querySelectorAll("[data-counted-textarea]").forEach((textarea) => {
    const counter = textarea.closest(".prisma-field")?.querySelector("[data-text-counter]");
    const update = () => {
      if (counter) counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
    };
    textarea.addEventListener("input", update);
    update();
  });

  document.querySelectorAll("[data-otp]").forEach((group) => {
    const inputs = [...group.querySelectorAll("input")];
    inputs.forEach((input, index) => {
      input.addEventListener("input", () => {
        input.value = input.value.replace(/\D/g, "").slice(0, 1);
        if (input.value && inputs[index + 1]) inputs[index + 1].focus();
      });
      input.addEventListener("keydown", (event) => {
        if (event.key === "Backspace" && !input.value && inputs[index - 1]) {
          inputs[index - 1].focus();
        }
      });
    });
  });

  // ---------------------------------------------------------------
  // Batch 2: Selection
  // ---------------------------------------------------------------
  document.querySelectorAll(".prisma-choice input").forEach((input) => {
    input.addEventListener("change", () => {
      const groupName = input.type === "radio" ? input.name : null;
      if (groupName) {
        document.querySelectorAll(`input[type="radio"][name="${groupName}"]`).forEach((radio) => {
          radio.closest(".prisma-choice")?.classList.toggle("is-selected", radio.checked);
        });
      } else {
        input.closest(".prisma-choice")?.classList.toggle("is-selected", input.checked);
      }
    });
  });

  document.querySelectorAll("[data-toggle-switch]").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const checked = toggle.getAttribute("aria-checked") !== "true";
      toggle.setAttribute("aria-checked", String(checked));
    });
  });

  document.querySelectorAll("[data-segmented]").forEach((group) => {
    group.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        group.querySelectorAll("button").forEach((item) => {
          item.setAttribute("aria-pressed", String(item === button));
        });
      });
    });
  });

  document.querySelectorAll(".prisma-combobox").forEach((combo) => {
    const input = combo.querySelector("[data-combobox-input]");
    const list = combo.querySelector("[data-combobox-list]");
    const opener = combo.querySelector("[data-combobox-open]");
    const options = [...combo.querySelectorAll(".prisma-option")];

    const openList = (open = true) => {
      list?.classList.toggle("is-open", open);
      input?.setAttribute("aria-expanded", String(open));
    };

    opener?.addEventListener("click", () => {
      openList(!list?.classList.contains("is-open"));
      if (!list?.classList.contains("is-open")) input?.focus();
    });

    input?.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      options.forEach((option) => {
        option.hidden = !option.textContent.toLowerCase().includes(query);
      });
      openList(true);
    });

    options.forEach((option) => {
      option.addEventListener("click", () => {
        input.value = option.textContent.trim();
        options.forEach((item) => item.setAttribute("aria-selected", String(item === option)));
        openList(false);
        input.focus();
      });
    });
  });

  document.querySelectorAll("[data-tag-picker]").forEach((picker) => {
    const input = picker.querySelector("[data-tag-input]");

    const bindRemove = (tag) => {
      tag.querySelector("button")?.addEventListener("click", () => tag.remove());
    };

    picker.querySelectorAll(".prisma-tag").forEach(bindRemove);

    input?.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || !input.value.trim()) return;
      event.preventDefault();
      const tag = document.createElement("span");
      tag.className = "prisma-tag";
      tag.innerHTML = `${escapeHtml(input.value.trim())} <button type="button" aria-label="Quitar">✕</button>`;
      picker.insertBefore(tag, input);
      bindRemove(tag);
      input.value = "";
    });
  });

  // ---------------------------------------------------------------
  // Batch 2: Navigation
  // ---------------------------------------------------------------
  document.querySelectorAll("[data-tabs]").forEach((tablist) => {
    const tabs = [...tablist.querySelectorAll('[role="tab"]')];
    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => {
        const id = tab.dataset.tab;
        tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
        document.querySelectorAll("[data-tab-panel]").forEach((panel) => {
          panel.classList.toggle("is-active", panel.dataset.tabPanel === id);
        });
      });
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
        event.preventDefault();
        const direction = event.key === "ArrowRight" ? 1 : -1;
        const next = tabs[(index + direction + tabs.length) % tabs.length];
        next.focus();
        next.click();
      });
    });
  });

  document.querySelectorAll("[data-local-rail]").forEach((rail) => {
    rail.querySelectorAll(".prisma-rail-item").forEach((item) => {
      item.addEventListener("click", () => {
        rail.querySelectorAll(".prisma-rail-item").forEach((other) => {
          other.removeAttribute("aria-current");
        });
        item.setAttribute("aria-current", "page");
      });
    });
  });

  document.querySelectorAll("[data-demo-dock]").forEach((dock) => {
    dock.querySelectorAll(".prisma-dock-item").forEach((item) => {
      item.addEventListener("click", () => {
        dock.querySelectorAll(".prisma-dock-item").forEach((other) => {
          other.removeAttribute("aria-current");
        });
        item.setAttribute("aria-current", "page");
      });
    });
  });

  document.querySelectorAll("[data-pagination]").forEach((pagination) => {
    pagination.querySelectorAll(".prisma-page").forEach((button) => {
      button.addEventListener("click", () => {
        if (!/^\d+$/.test(button.textContent.trim())) return;
        pagination.querySelectorAll(".prisma-page").forEach((other) => {
          other.removeAttribute("aria-current");
        });
        button.setAttribute("aria-current", "page");
      });
    });
  });

  document.querySelectorAll("[data-next-step]").forEach((button) => {
    const stepper = button.closest(".atlas-section")?.querySelector("[data-stepper]");
    button.addEventListener("click", () => {
      if (!stepper) return;
      const steps = [...stepper.querySelectorAll(".prisma-step")];
      let activeIndex = steps.findIndex((step) => step.classList.contains("is-active"));
      if (activeIndex < 0) activeIndex = 0;
      steps[activeIndex].classList.remove("is-active");
      steps[activeIndex].classList.add("is-complete");
      const nextIndex = Math.min(activeIndex + 1, steps.length - 1);
      steps[nextIndex].classList.add("is-active");
      if (nextIndex === steps.length - 1) button.textContent = "Listo ✓";
    });
  });


  // PRISMA Atlas Polish Pass 1
  const premiumReactiveSelector = [
    ".atlas-button",
    ".atlas-icon-button",
    ".atlas-search-trigger",
    ".prisma-action",
    ".atlas-overlay-trigger",
  ].join(",");

  document.querySelectorAll(premiumReactiveSelector).forEach((node) => {
    node.classList.add("is-premium-reactive");

    node.addEventListener("pointermove", (event) => {
      const bounds = node.getBoundingClientRect();
      node.style.setProperty("--atlas-fx-x", `${event.clientX - bounds.left}px`);
      node.style.setProperty("--atlas-fx-y", `${event.clientY - bounds.top}px`);
    });

    node.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      node.classList.add("is-pointer-pressed");
    });

    const release = () => node.classList.remove("is-pointer-pressed");
    node.addEventListener("pointerup", release);
    node.addEventListener("pointercancel", release);
    node.addEventListener("pointerleave", release);
  });


  // ---------------------------------------------------------------
  // PRISMA Atlas Batch 3 · H-L
  // ---------------------------------------------------------------

  const setDisclosure = (button, expanded) => {
    const targetId = button.getAttribute("aria-controls");
    const panel = targetId ? document.getElementById(targetId) : null;
    button.setAttribute("aria-expanded", String(expanded));
    if (panel) panel.hidden = !expanded;

    const marker = button.querySelector(":scope > span:last-child");
    if (marker && ["+", "−", "▸", "▾"].includes(marker.textContent.trim())) {
      marker.textContent = expanded ? "−" : "+";
    }
  };

  document.querySelectorAll("[data-disclosure-button]").forEach((button) => {
    button.addEventListener("click", () => {
      setDisclosure(button, button.getAttribute("aria-expanded") !== "true");
    });
  });

  document.querySelectorAll("[data-accordion]").forEach((accordion) => {
    const buttons = [...accordion.querySelectorAll("[data-disclosure-button]")];

    buttons.forEach((button, index) => {
      button.addEventListener("keydown", (event) => {
        const keys = ["ArrowDown", "ArrowUp", "Home", "End"];
        if (!keys.includes(event.key)) return;
        event.preventDefault();

        let targetIndex = index;
        if (event.key === "ArrowDown") targetIndex = (index + 1) % buttons.length;
        if (event.key === "ArrowUp") targetIndex = (index - 1 + buttons.length) % buttons.length;
        if (event.key === "Home") targetIndex = 0;
        if (event.key === "End") targetIndex = buttons.length - 1;

        buttons[targetIndex]?.focus();
      });
    });
  });

  document.querySelectorAll("[data-tree-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") !== "true";
      const target = document.getElementById(button.getAttribute("aria-controls"));
      button.setAttribute("aria-expanded", String(expanded));
      button.textContent = button.textContent.replace(
        expanded ? "▸" : "▾",
        expanded ? "▾" : "▸"
      );
      if (target) target.hidden = !expanded;
      button.closest('[role="treeitem"]')?.setAttribute("aria-expanded", String(expanded));
    });
  });

  document.querySelectorAll("[data-selectable-list]").forEach((listbox) => {
    const options = [...listbox.querySelectorAll('[role="option"]')];

    const select = (option) => {
      options.forEach((item) => {
        const selected = item === option;
        item.classList.toggle("is-selected", selected);
        item.setAttribute("aria-selected", String(selected));
      });
    };

    options.forEach((option, index) => {
      option.addEventListener("click", () => select(option));
      option.addEventListener("keydown", (event) => {
        if (!["ArrowDown", "ArrowUp"].includes(event.key)) return;
        event.preventDefault();
        const direction = event.key === "ArrowDown" ? 1 : -1;
        const next = options[(index + direction + options.length) % options.length];
        next.focus();
        select(next);
      });
    });
  });

  document.querySelectorAll("[data-dismiss-notification]").forEach((button) => {
    button.addEventListener("click", () => {
      const notification = button.closest("[data-notification]");
      notification?.animate(
        [
          { opacity: 1, transform: "translateX(0)" },
          { opacity: 0, transform: "translateX(18px)" },
        ],
        { duration: 180, easing: "ease-out" }
      ).finished.then(() => notification.remove());
    });
  });

  document.querySelector("[data-feed-add]")?.addEventListener("click", () => {
    const feed = document.querySelector("[data-activity-feed]");
    if (!feed) return;

    const article = document.createElement("article");
    article.className = "atlas-feed__item";
    article.tabIndex = 0;
    article.innerHTML = `
      <span class="atlas-feed__dot"></span>
      <div>
        <strong>Evento añadido</strong>
        <p>Registro generado desde el laboratorio.</p>
        <time>Ahora</time>
      </div>
    `;
    feed.prepend(article);
    article.focus();
  });

  document.querySelectorAll("[data-selectable-card]").forEach((card) => {
    card.addEventListener("click", () => {
      const pressed = card.getAttribute("aria-pressed") !== "true";
      card.setAttribute("aria-pressed", String(pressed));
      card.classList.toggle("is-selected", pressed);
    });
  });

  document.querySelectorAll("[data-loading-tile]").forEach((tile) => {
    tile.addEventListener("click", () => {
      if (tile.dataset.loading === "true") return;
      tile.dataset.loading = "true";
      const label = tile.querySelector("small");
      if (label) label.textContent = "Cargando…";

      setTimeout(() => {
        tile.dataset.loading = "false";
        if (label) label.textContent = "Listo ✓";
      }, 1100);
    });
  });

  document.querySelector("[data-show-more]")?.addEventListener("click", (event) => {
    const button = event.currentTarget;
    const content = document.querySelector("[data-show-more-content]");
    const expanded = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(expanded));
    if (content) content.hidden = !expanded;
    button.textContent = expanded ? "Mostrar menos" : "Mostrar más";
  });

  document.querySelector("[data-progressive-toggle]")?.addEventListener("change", (event) => {
    const fields = document.querySelector("[data-progressive-fields]");
    if (fields) fields.hidden = !event.currentTarget.checked;
  });

  const stateDefinitions = {
    success: {
      eyebrow: "Estado saludable",
      title: "Operación confirmada",
      copy: "Los cambios fueron guardados y verificados.",
      action: "Ver detalle",
    },
    warning: {
      eyebrow: "Advertencia",
      title: "Revisión necesaria",
      copy: "Hay información que conviene confirmar antes de continuar.",
      action: "Revisar",
    },
    danger: {
      eyebrow: "Error crítico",
      title: "Operación detenida",
      copy: "El sistema evitó aplicar una operación incompatible.",
      action: "Diagnosticar",
    },
    offline: {
      eyebrow: "Continuidad local",
      title: "Sin conexión remota",
      copy: "La operación local continúa y los cambios quedan en cola.",
      action: "Ver cola",
    },
    readonly: {
      eyebrow: "Sólo lectura",
      title: "Contenido protegido",
      copy: "Puedes consultar esta información, pero no editarla.",
      action: "Entendido",
    },
    conflict: {
      eyebrow: "Conflicto",
      title: "Dos versiones requieren decisión",
      copy: "Compara origen, hora y responsable antes de resolver.",
      action: "Comparar",
    },
  };

  document.querySelectorAll("[data-state-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.stateChoice;
      const definition = stateDefinitions[id];
      const stage = document.querySelector("[data-state-stage]");
      if (!definition || !stage) return;

      stage.dataset.tone = id;
      stage.querySelector("[data-state-eyebrow]")?.replaceChildren(definition.eyebrow);
      stage.querySelector("[data-state-title]")?.replaceChildren(definition.title);
      stage.querySelector("[data-state-copy]")?.replaceChildren(definition.copy);
      stage.querySelector("[data-state-action]")?.replaceChildren(definition.action);
    });
  });

  document.querySelector("[data-retry-button]")?.addEventListener("click", (event) => {
    const button = event.currentTarget;
    const state = button.closest("[data-retry-state]");
    button.disabled = true;
    button.textContent = "Reintentando…";

    setTimeout(() => {
      state?.style.setProperty("--feedback-rgb", "102, 236, 177");
      state?.querySelector("strong")?.replaceChildren("Lectura recuperada");
      state?.querySelector("p")?.replaceChildren("La operación respondió correctamente.");
      button.textContent = "Listo ✓";
    }, 1200);
  });

  const toastRegion = document.querySelector("[data-toast-region]");

  const addTransientMessage = (kind) => {
    if (!toastRegion) return;

    const message = document.createElement("article");
    message.className = kind === "snackbar" ? "atlas-snackbar" : "atlas-toast";
    message.setAttribute("role", kind === "snackbar" ? "status" : "status");

    if (kind === "snackbar") {
      message.innerHTML = `
        <div><strong>Cambio guardado</strong><p>La configuración se actualizó.</p></div>
        <button class="atlas-button" type="button">Deshacer</button>
      `;
    } else {
      message.innerHTML = `
        <div><strong>Reporte listo</strong><p>El archivo está disponible para descarga.</p></div>
        <button class="atlas-icon-button" type="button" aria-label="Cerrar">×</button>
      `;
    }

    toastRegion.appendChild(message);

    const close = () => message.remove();
    message.querySelector("button")?.addEventListener("click", close);
    setTimeout(close, kind === "snackbar" ? 5200 : 3600);
  };

  document.querySelector("[data-toast-trigger]")?.addEventListener(
    "click",
    () => addTransientMessage("toast")
  );

  document.querySelector("[data-snackbar-trigger]")?.addEventListener(
    "click",
    () => addTransientMessage("snackbar")
  );

  const setProgress = (value) => {
    const normalized = Math.max(0, Math.min(100, Math.round(value)));
    const bar = document.querySelector("[data-progress-bar]");
    const circular = document.querySelector("[data-circular-progress]");

    if (bar) {
      bar.setAttribute("aria-valuenow", String(normalized));
      const fill = bar.querySelector("span");
      if (fill) fill.style.width = `${normalized}%`;
    }

    document.querySelector("[data-progress-output]")?.replaceChildren(`${normalized}%`);

    if (circular) {
      circular.setAttribute("aria-valuenow", String(normalized));
      circular.style.setProperty("--progress-value", normalized);
    }

    document.querySelector("[data-circular-output]")?.replaceChildren(`${normalized}%`);
  };

  document.querySelector("[data-progress-start]")?.addEventListener("click", (event) => {
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = "Procesando…";

    const started = performance.now();
    const duration = 2400;

    const tick = (now) => {
      const progress = Math.min(1, (now - started) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setProgress(eased * 100);

      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        button.disabled = false;
        button.textContent = "Repetir";
      }
    };

    setProgress(0);
    requestAnimationFrame(tick);
  });

  document.querySelector("[data-demo-loading-button]")?.addEventListener("click", (event) => {
    const button = event.currentTarget;
    if (button.getAttribute("aria-busy") === "true") return;

    button.setAttribute("aria-busy", "true");
    button.disabled = true;
    button.textContent = "Generando…";

    setTimeout(() => {
      button.removeAttribute("aria-busy");
      button.disabled = false;
      button.textContent = "Reporte listo ✓";
    }, 1200);
  });

  document.querySelector("[data-sync-toggle]")?.addEventListener("click", (event) => {
    const sync = document.querySelector("[data-background-sync]");
    const paused = !sync?.classList.contains("is-paused");
    sync?.classList.toggle("is-paused", paused);
    document.querySelector("[data-sync-label]")?.replaceChildren(paused ? "Pausado" : "Activo");
    event.currentTarget.textContent = paused
      ? "Reanudar sincronización"
      : "Pausar sincronización";
  });

  let queuedOperation = 4;

  document.querySelector("[data-queue-add]")?.addEventListener("click", () => {
    const queue = document.querySelector("[data-queue]");
    if (!queue) return;

    const item = document.createElement("article");
    item.className = "atlas-queue-item";
    item.dataset.status = "queued";
    item.innerHTML = `
      <span>${queuedOperation}</span>
      <div><strong>Operación #${queuedOperation}</strong><p>En cola</p></div>
      <time>Próximo</time>
    `;
    queuedOperation += 1;
    queue.appendChild(item);

    setTimeout(() => {
      item.dataset.status = "active";
      item.firstElementChild?.replaceWith(
        Object.assign(document.createElement("span"), {
          className: "atlas-spinner atlas-spinner--small",
        })
      );
      item.querySelector("p")?.replaceChildren("Procesando");
      item.querySelector("time")?.replaceChildren("Ahora");

      setTimeout(() => {
        item.dataset.status = "complete";
        item.firstElementChild?.replaceWith(
          Object.assign(document.createElement("span"), {
            textContent: "✓",
          })
        );
        item.querySelector("p")?.replaceChildren("Confirmada");
        item.querySelector("time")?.replaceChildren("Listo");
      }, 1200);
    }, 500);
  });


  // PRISMA Atlas Complete N-Y
  const selectSingle = (container, selector, attribute) => {
    if (!container) return;
    const items = [...container.querySelectorAll(selector)];
    items.forEach((item) => item.addEventListener("click", () => {
      items.forEach((other) => other.setAttribute(attribute, String(other === item)));
    }));
  };

  document.querySelectorAll("[data-single-choice]").forEach((group) =>
    selectSingle(group, "button", "aria-checked")
  );

  document.querySelector("[data-cash-input]")?.addEventListener("input", (event) => {
    const value = Math.max(0, Number(event.currentTarget.value || 0) - 188);
    document.querySelector("[data-change]")?.replaceChildren(
      new Intl.NumberFormat("es-MX",{style:"currency",currency:"MXN"}).format(value)
    );
  });

  document.querySelectorAll("[data-pattern-tabs] [data-pattern]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-pattern-tabs] [data-pattern]").forEach((item) =>
        item.setAttribute("aria-selected", String(item === button))
      );
      const stage=document.querySelector("[data-screen-demo]");
      if(stage) stage.dataset.pattern=button.dataset.pattern;
    });
  });

  document.querySelector("[data-motion-range]")?.addEventListener("input", (event) => {
    document.querySelector("[data-motion-lab]")?.style.setProperty(
      "--motion", Number(event.currentTarget.value)/100
    );
  });

  document.querySelectorAll("[data-width-tabs] [data-width]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-width-tabs] [data-width]").forEach((item) =>
        item.setAttribute("aria-pressed", String(item === button))
      );
      const frame=document.querySelector("[data-viewport-demo]");
      if(frame) frame.dataset.width=button.dataset.width;
    });
  });

  const toggle = (button) => {
    const checked=button.getAttribute("aria-checked")!=="true";
    button.setAttribute("aria-checked",String(checked));
    return checked;
  };

  document.querySelector("[data-motion-switch]")?.addEventListener("click",(event)=>{
    document.documentElement.dataset.motion=toggle(event.currentTarget)?"reduced":"normal";
  });
  document.querySelector("[data-alpha-switch]")?.addEventListener("click",(event)=>{
    document.documentElement.style.setProperty("--atlas-content-alpha",toggle(event.currentTarget)?".88":"");
  });

  document.querySelector("[data-copy-button]")?.addEventListener("click",async(event)=>{
    const text=document.querySelector("[data-copy-source]")?.textContent?.trim()||"";
    try { await navigator.clipboard.writeText(text); event.currentTarget.textContent="Copiado ✓"; }
    catch { event.currentTarget.textContent="Selecciona y copia"; }
  });

  document.querySelectorAll("[data-chart-point]").forEach((point)=>{
    const tip=document.querySelector("[data-chart-tip]");
    const show=()=>{ if(!tip)return; tip.hidden=false; tip.textContent=point.dataset.value; };
    point.addEventListener("mouseenter",show);
    point.addEventListener("focus",show);
    point.addEventListener("mouseleave",()=>{if(tip)tip.hidden=true;});
  });

  const drop=document.querySelector("[data-drop-zone]");
  const input=document.querySelector("[data-file-input]");
  const list=document.querySelector("[data-file-list]");
  const addFiles=(files)=>{
    if(!list)return;
    [...files].forEach((file)=>{
      const row=document.createElement("article");
      row.innerHTML=`<span>${escapeHtml((file.name.split(".").pop()||"FILE").toUpperCase().slice(0,4))}</span><div><strong>${escapeHtml(file.name)}</strong><small>${Math.max(1,Math.round(file.size/1024))} KB · listo</small></div><button class="atlas-icon-button" aria-label="Quitar">×</button>`;
      row.querySelector("button")?.addEventListener("click",()=>row.remove());
      list.appendChild(row);
      if(file.type.startsWith("image/")){
        const reader=new FileReader();
        reader.addEventListener("load",()=>{
          const preview=document.querySelector("[data-preview-demo]");
          if(preview){preview.style.background=`url(${reader.result}) center/cover`;preview.textContent="";}
        });
        reader.readAsDataURL(file);
      }
    });
  };
  input?.addEventListener("change",()=>addFiles(input.files||[]));
  ["dragenter","dragover"].forEach((name)=>drop?.addEventListener(name,(event)=>{event.preventDefault();drop.classList.add("is-dragging");}));
  ["dragleave","drop"].forEach((name)=>drop?.addEventListener(name,(event)=>{event.preventDefault();drop.classList.remove("is-dragging");}));
  drop?.addEventListener("drop",(event)=>addFiles(event.dataTransfer.files));
  document.querySelector("[data-export-demo]")?.addEventListener("click",(event)=>event.currentTarget.textContent="Exportación lista ✓");
  document.querySelectorAll("[data-print-demo]").forEach((button)=>button.addEventListener("click",()=>window.print()));

  document.querySelectorAll("[data-calendar-demo] button").forEach((button)=>{
    button.addEventListener("click",()=>{
      document.querySelectorAll("[data-calendar-demo] button").forEach((item)=>{
        item.classList.toggle("is-selected",item===button);
        item.setAttribute("aria-pressed",String(item===button));
      });
    });
  });
  selectSingle(document.querySelector("[data-time-slots]"),"button","aria-pressed");
  document.querySelector("[data-duration]")?.addEventListener("input",(event)=>{
    document.querySelector("[data-duration-output]")?.replaceChildren(`${event.currentTarget.value} min`);
  });

  let countdown=872;
  const countdownNode=document.querySelector("[data-countdown]");
  if(countdownNode) setInterval(()=>{
    countdown=Math.max(0,countdown-1);
    const h=Math.floor(countdown/3600),m=Math.floor((countdown%3600)/60),s=countdown%60;
    countdownNode.textContent=[h,m,s].map(x=>String(x).padStart(2,"0")).join(":");
  },1000);

  document.querySelector("[data-signin-form]")?.addEventListener("submit",(event)=>{
    event.preventDefault();event.currentTarget.querySelector('button[type="submit"]').textContent="Sesión verificada ✓";
  });
  document.querySelector("[data-passkey]")?.addEventListener("click",(event)=>event.currentTarget.textContent="Passkey disponible ✓");

  const otp=[...document.querySelectorAll("[data-mfa-otp] input")];
  otp.forEach((field,index)=>field.addEventListener("input",()=>{
    field.value=field.value.replace(/\D/g,"").slice(0,1);
    if(field.value)otp[index+1]?.focus();
  }));
  document.querySelector("[data-mfa-verify]")?.addEventListener("click",()=>{
    document.querySelector("[data-mfa-status]")?.replaceChildren(
      otp.every((field)=>field.value.length===1)?"Verificado":"Código incompleto"
    );
  });

  document.querySelector("[data-run-diagnostics]")?.addEventListener("click",(event)=>{
    const cards=[...document.querySelectorAll("[data-health-demo] article")];
    event.currentTarget.disabled=true;event.currentTarget.textContent="Diagnosticando…";
    cards.forEach((card,index)=>setTimeout(()=>{
      card.querySelector("small")?.replaceChildren("PASS");
      if(index===cards.length-1){event.currentTarget.disabled=false;event.currentTarget.textContent="Diagnóstico PASS";}
    },220*(index+1)));
  });

  document.querySelector("[data-log-search]")?.addEventListener("input",(event)=>{
    const q=event.currentTarget.value.toLowerCase();
    document.querySelectorAll("[data-log-viewer] code").forEach((line)=>line.hidden=!line.textContent.toLowerCase().includes(q));
  });

  const formatLocale=()=>{
    const locale=document.querySelector("[data-locale]")?.value||"es-MX";
    const currency=document.querySelector("[data-currency]")?.value||"MXN";
    const date=new Date("2026-07-18T08:42:00-06:00");
    document.querySelector("[data-format-currency]")?.replaceChildren(new Intl.NumberFormat(locale,{style:"currency",currency}).format(48420.75));
    document.querySelector("[data-format-number]")?.replaceChildren(new Intl.NumberFormat(locale).format(1234567.89));
    document.querySelector("[data-format-date]")?.replaceChildren(new Intl.DateTimeFormat(locale,{dateStyle:"medium",timeStyle:"short"}).format(date));
    document.querySelector("[data-format-plural]")?.replaceChildren(new Intl.PluralRules(locale).select(3)==="one"?"1 producto":"3 productos");
  };
  document.querySelector("[data-locale]")?.addEventListener("change",formatLocale);
  document.querySelector("[data-currency]")?.addEventListener("change",formatLocale);
  document.querySelector("[data-rtl]")?.addEventListener("click",(event)=>{
    const preview=document.querySelector("[data-locale-demo]");
    const rtl=preview?.getAttribute("dir")!=="rtl";
    preview?.setAttribute("dir",rtl?"rtl":"ltr");
    event.currentTarget.textContent=rtl?"Desactivar RTL":"Activar RTL";
  });
  document.querySelector("[data-reconnect]")?.addEventListener("click",(event)=>{
    event.currentTarget.disabled=true;event.currentTarget.textContent="Conectando…";
    setTimeout(()=>{event.currentTarget.disabled=false;event.currentTarget.textContent="Conectado ✓";document.querySelector("[data-freshness]")?.replaceChildren("Actualizado ahora");},900);
  });
  formatLocale();

  // ---------------------------------------------------------------
  // PRISMA Atlas Chroma Balance · Accessible Select 01
  // Native <select> remains the state/form authority. The visible listbox is
  // a single governed overlay surface so Windows never paints a pale popup.
  // ---------------------------------------------------------------
  const atlasSelectState = {
    current: null,
    sequence: 0,
  };

  const closeAtlasSelect = (restoreFocus = false) => {
    const current = atlasSelectState.current;
    if (!current) return;
    current.shell.classList.remove("is-open");
    current.trigger.setAttribute("aria-expanded", "false");
    current.panel.hidden = true;
    if (restoreFocus) current.trigger.focus();
    atlasSelectState.current = null;
  };

  const positionAtlasSelect = (instance) => {
    if (!instance || instance.panel.hidden) return;
    const rect = instance.trigger.getBoundingClientRect();
    const viewportWidth = document.documentElement.clientWidth;
    const viewportHeight = document.documentElement.clientHeight;
    const gutter = 10;
    const gap = 7;
    const minimumWidth = Math.min(280, viewportWidth - gutter * 2);
    const width = Math.min(Math.max(rect.width, minimumWidth), viewportWidth - gutter * 2);
    const left = Math.max(gutter, Math.min(rect.left, viewportWidth - width - gutter));
    const below = viewportHeight - rect.bottom - gutter;
    const above = rect.top - gutter;
    const useTop = below < 190 && above > below;

    instance.panel.style.width = `${width}px`;
    instance.panel.style.left = `${left}px`;
    instance.panel.style.right = "auto";
    instance.panel.style.top = "auto";
    instance.panel.style.bottom = "auto";
    instance.panel.dataset.placement = useTop ? "top" : "bottom";

    if (useTop) {
      instance.panel.style.bottom = `${Math.max(gutter, viewportHeight - rect.top + gap)}px`;
      instance.panel.style.maxHeight = `${Math.max(120, Math.min(320, above - gap))}px`;
    } else {
      instance.panel.style.top = `${Math.min(viewportHeight - gutter, rect.bottom + gap)}px`;
      instance.panel.style.maxHeight = `${Math.max(120, Math.min(320, below - gap))}px`;
    }
  };

  const focusAtlasOption = (instance, index) => {
    const enabled = instance.optionButtons.filter((button) => !button.disabled);
    if (!enabled.length) return;
    const target = enabled[Math.max(0, Math.min(index, enabled.length - 1))];
    target.focus();
    target.scrollIntoView({ block: "nearest" });
  };

  const selectAtlasOption = (instance, index) => {
    const option = instance.select.options[index];
    if (!option || option.disabled) return;
    instance.select.selectedIndex = index;
    instance.sync();
    instance.select.dispatchEvent(new Event("input", { bubbles: true }));
    instance.select.dispatchEvent(new Event("change", { bubbles: true }));
    closeAtlasSelect(true);
  };

  const openAtlasSelect = (instance, focusSelected = false) => {
    if (instance.select.disabled) return;
    if (atlasSelectState.current && atlasSelectState.current !== instance) {
      closeAtlasSelect(false);
    }
    atlasSelectState.current = instance;
    instance.shell.classList.add("is-open");
    instance.trigger.setAttribute("aria-expanded", "true");
    instance.panel.hidden = false;
    positionAtlasSelect(instance);
    if (focusSelected) {
      const selected = instance.optionButtons.findIndex((button) => button.getAttribute("aria-selected") === "true");
      requestAnimationFrame(() => focusAtlasOption(instance, Math.max(0, selected)));
    }
  };

  const enhanceAtlasSelect = (select) => {
    if (select.dataset.atlasEnhanced === "true") return;
    select.dataset.atlasEnhanced = "true";

    const id = `atlas-select-${++atlasSelectState.sequence}`;
    const shell = document.createElement("div");
    shell.className = "atlas-select-shell";
    select.parentNode.insertBefore(shell, select);
    shell.appendChild(select);
    select.classList.add("atlas-native-select");
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "atlas-select-trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-controls", `${id}-panel`);
    trigger.disabled = select.disabled;

    const valueNode = document.createElement("span");
    valueNode.className = "atlas-select-trigger__value";
    const metaNode = document.createElement("span");
    metaNode.className = "atlas-select-trigger__meta";
    metaNode.textContent = `${select.options.length} opciones`;
    trigger.append(valueNode, metaNode);
    shell.appendChild(trigger);

    const panel = document.createElement("div");
    panel.id = `${id}-panel`;
    panel.className = "atlas-select-panel";
    panel.setAttribute("role", "listbox");
    panel.hidden = true;
    document.body.appendChild(panel);

    const label = select.labels?.[0]?.textContent?.trim()
      || select.getAttribute("aria-label")
      || select.name
      || "Seleccionar opción";
    trigger.setAttribute("aria-label", label);
    panel.setAttribute("aria-label", label);

    const instance = {
      select,
      shell,
      trigger,
      panel,
      optionButtons: [],
      sync: null,
    };

    Array.from(select.options).forEach((option, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "atlas-select-option";
      button.setAttribute("role", "option");
      button.dataset.optionIndex = String(index);
      button.textContent = option.textContent;
      button.disabled = option.disabled;
      button.addEventListener("click", () => selectAtlasOption(instance, index));
      button.addEventListener("keydown", (event) => {
        const enabled = instance.optionButtons.filter((item) => !item.disabled);
        const currentIndex = enabled.indexOf(button);
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          event.preventDefault();
          const direction = event.key === "ArrowDown" ? 1 : -1;
          focusAtlasOption(instance, (currentIndex + direction + enabled.length) % enabled.length);
        } else if (event.key === "Home" || event.key === "End") {
          event.preventDefault();
          focusAtlasOption(instance, event.key === "Home" ? 0 : enabled.length - 1);
        } else if (event.key === "Escape") {
          event.preventDefault();
          closeAtlasSelect(true);
        } else if (event.key === "Tab") {
          closeAtlasSelect(false);
        }
      });
      instance.optionButtons.push(button);
      panel.appendChild(button);
    });

    instance.sync = () => {
      const selected = select.options[select.selectedIndex] || select.options[0];
      valueNode.textContent = selected?.textContent?.trim() || "Seleccionar";
      instance.optionButtons.forEach((button, index) => {
        button.setAttribute("aria-selected", String(index === select.selectedIndex));
      });
      trigger.disabled = select.disabled;
    };

    instance.sync();

    trigger.addEventListener("click", (event) => {
      if (atlasSelectState.current === instance) closeAtlasSelect(false);
      else openAtlasSelect(instance, event.detail === 0);
    });

    trigger.addEventListener("keydown", (event) => {
      if (["ArrowDown", "ArrowUp", " "].includes(event.key)) {
        event.preventDefault();
        openAtlasSelect(instance, true);
      }
    });

    select.addEventListener("change", instance.sync);
    select.labels?.forEach((labelNode) => {
      labelNode.addEventListener("click", (event) => {
        event.preventDefault();
        trigger.focus();
      });
    });
  };

  document.querySelectorAll("select").forEach(enhanceAtlasSelect);

  document.addEventListener("pointerdown", (event) => {
    const current = atlasSelectState.current;
    if (!current) return;
    if (current.shell.contains(event.target) || current.panel.contains(event.target)) return;
    closeAtlasSelect(false);
  });

  window.addEventListener("resize", () => positionAtlasSelect(atlasSelectState.current), { passive: true });
  window.addEventListener("scroll", () => positionAtlasSelect(atlasSelectState.current), { passive: true, capture: true });


})();
