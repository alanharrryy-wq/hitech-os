(function () {
  "use strict";

  const api = async (path) => {
    const response = await fetch(path, { cache: "no-store", headers: { Accept: "application/json" } });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || payload.reason || `${path} ${response.status}`);
    return payload;
  };

  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (ch) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;"
    }[ch]));
  }

  function shortPath(item) {
    const value = item && item.path ? item.path : item && item.name ? item.name : "";
    if (!value || value === "<redacted>") return value || "-";
    const raw = String(value);
    const slash = Math.max(raw.lastIndexOf("/"), raw.lastIndexOf("\\"));
    return slash >= 0 ? raw.slice(slash + 1) : raw;
  }

  function row(label, item) {
    const status = item && item.exists ? "PASS" : "MISSING";
    return `<div class="cloudSaasRow"><small>${esc(label)} · ${esc(status)}</small><strong title="${esc(item && item.path)}">${esc(shortPath(item))}</strong></div>`;
  }

  function render(root, payload) {
    const runtime = payload && payload.runtime ? payload.runtime : {};
    const summary = runtime.runtime || {};
    root.innerHTML = `
      <div class="licenseOpsMiniGrid">
        <section class="cloudSaasCard">
          <div class="cloudSaasCardHead">
            <div><span>LOCAL LICENSE OPS</span><h3>${esc(payload.status || "REVIEW")}</h3></div>
            <b>${esc(payload.safetyMode || "LOCAL_READ_ONLY")}</b>
          </div>
          <div class="cloudSaasRows">
            ${row("Runtime config", runtime.runtimeConfig)}
            ${row("Device identity", runtime.deviceIdentityFile)}
            ${row("License file", runtime.licenseFile)}
            ${row("Current release", runtime.currentRelease)}
            <div class="cloudSaasRow"><small>Identidad</small><strong>${esc(summary.businessId || "-")} / ${esc(summary.storeId || "-")} / ${esc(summary.terminalId || "-")} / ${esc(summary.deviceId || "-")}</strong></div>
          </div>
        </section>
        <section class="cloudSaasCard">
          <div class="cloudSaasCardHead">
            <div><span>3150 ADAPTADO</span><h3>Read-only</h3></div>
            <b>NO PROCESS</b>
          </div>
          <pre class="licenseOpsResult">${esc(JSON.stringify(payload, null, 2))}</pre>
        </section>
      </div>`;
  }

  async function mount(root) {
    const target = typeof root === "string" ? document.getElementById(root) : root;
    if (!target) return;
    target.innerHTML = '<div class="cloudSaasCard"><h3>Cargando licencias...</h3></div>';
    try {
      const payload = await api("/api/license-ops/latest");
      render(target, payload);
    } catch (error) {
      target.innerHTML = `<div class="cloudSaasCard cloudSaasError"><h3>Licencias no disponibles</h3><pre>${esc(error.message || error)}</pre></div>`;
    }
  }

  window.PRISMA_LICENSE_OPS_LAB = { mount, refresh: mount };
})();
