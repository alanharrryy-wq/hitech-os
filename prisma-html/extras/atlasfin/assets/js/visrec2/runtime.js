(() => {
  "use strict";

  const current = document.currentScript;
  const baseUrl = new URL(".", current?.src || window.location.href);
  const moduleNames = [
    "checksum-engine",
    "fingerprint-engine",
    "selection-engine",
    "property-engine",
    "state-engine",
    "adapter-engine",
    "compatibility-engine",
    "recipe-engine",
    "preview-engine",
    "export-engine",
    "migration-engine",
    "import-inspector",
    "console-engine",
  ];
  let loading = null;

  const loadScript = (name) =>
    new Promise((resolve, reject) => {
      if (window.__PRISMA_VISREC2_MODULES__?.[name]) {
        resolve();
        return;
      }
      const script = document.createElement("script");
      script.src = new URL(`${name}.js`, baseUrl).href;
      script.async = false;
      script.dataset.visrec2InternalModule = name;
      script.addEventListener("load", resolve, { once: true });
      script.addEventListener(
        "error",
        () => reject(new Error(`No fue posible cargar el módulo interno ${name}.`)),
        { once: true }
      );
      document.head.appendChild(script);
    });

  const load = () => {
    if (!loading) {
      loading = moduleNames
        .reduce((promise, name) => promise.then(() => loadScript(name)), Promise.resolve())
        .then(() => {
          const modules = window.__PRISMA_VISREC2_MODULES__ || {};
          const missing = moduleNames.filter((name) => !modules[name]);
          if (missing.length) {
            throw new Error(`Módulos VISREC2 incompletos: ${missing.join(", ")}.`);
          }
          return modules;
        });
    }
    return loading;
  };

  const api = {
    version: "2.0.0",
    schema: "PRISMA_VISREC2_PUBLIC_RUNTIME_V2",
    publicRuntimeCount: 1,
    visibleControlPolicy: "PRESERVE_EXACT_VISIBLE_CONTROL_SET",
    load,
    async init(bridge) {
      const modules = await load();
      return modules["console-engine"].init(bridge, modules);
    },
    async inspect(payload, context = {}) {
      const modules = await load();
      return modules["import-inspector"].inspect(payload, context, modules);
    },
    async migrate(payload) {
      const modules = await load();
      return modules["migration-engine"].migrate(payload, modules);
    },
  };

  Object.defineProperty(window, "PRISMA_VISREC2_RUNTIME_V2", {
    configurable: false,
    enumerable: true,
    value: Object.freeze(api),
    writable: false,
  });
})();
