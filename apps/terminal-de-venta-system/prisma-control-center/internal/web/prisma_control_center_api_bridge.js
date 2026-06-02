// PRISMA Control Center API Bridge v2
// Purpose: keep every Control Center surface wired to the local 3150 API when UI scripts run from a nested/dev/alternate origin.
// Scope: /api/* only. It does not mutate DB, does not run Quality actions by itself, and does not hide server-side 500s.
(function prismaControlCenterApiBridge(){
  "use strict";
  if (window.__PRISMA_CONTROL_CENTER_API_BRIDGE_V2__) return;
  window.__PRISMA_CONTROL_CENTER_API_BRIDGE_V2__ = true;

  const originalFetch = window.fetch ? window.fetch.bind(window) : null;
  const API_PORT = "3150";
  const MAX_HISTORY = 80;
  const state = { version: "motores-fix2-20260601", enabled: true, apiPort: API_PORT, retries: 0, lastError: null, history: [], origins: [] };

  function push(event){
    state.history.push({ at: new Date().toISOString(), ...event });
    if (state.history.length > MAX_HISTORY) state.history.splice(0, state.history.length - MAX_HISTORY);
  }
  function currentOrigin(){
    try { return window.location.origin && window.location.origin !== "null" ? window.location.origin : ""; } catch (_e) { return ""; }
  }
  function apiPathFrom(input){
    try {
      const raw = typeof input === "string" ? input : (input && input.url ? input.url : String(input || ""));
      if (!raw) return null;
      if (raw.startsWith("/api/")) return raw;
      const url = new URL(raw, currentOrigin() || "http://127.0.0.1:3150");
      if (url.pathname.startsWith("/api/")) return url.pathname + url.search + url.hash;
    } catch (_e) {}
    return null;
  }
  function isApi(input){ return !!apiPathFrom(input); }
  function makeFallbackOrigins(){
    const origins = [];
    const cur = currentOrigin();
    if (cur) origins.push(cur);
    origins.push("http://127.0.0.1:" + API_PORT);
    origins.push("http://localhost:" + API_PORT);
    try {
      const host = window.location.hostname;
      if (host && !["127.0.0.1", "localhost"].includes(host)) origins.push(window.location.protocol + "//" + host + ":" + API_PORT);
    } catch (_e) {}
    return Array.from(new Set(origins.filter(Boolean)));
  }
  function targetFor(path, origin){ return origin ? origin.replace(/\/$/, "") + path : path; }
  function isRetryableResponse(response, attemptedUrl){
    if (!response) return true;
    if ((response.status === 404 || response.status === 405) && !String(attemptedUrl).includes(":" + API_PORT + "/api/")) return true;
    return false;
  }
  function cloneOptions(init){
    if (!init) return init;
    const copy = { ...init };
    if (init.headers) copy.headers = init.headers;
    return copy;
  }
  async function bridgedFetch(input, init){
    if (!originalFetch || !state.enabled || !isApi(input)) return originalFetch(input, init);
    const path = apiPathFrom(input);
    const origins = makeFallbackOrigins();
    state.origins = origins;
    const attempts = [];
    attempts.push({ input, urlText: typeof input === "string" ? input : (input && input.url ? input.url : String(input)) });
    for (const origin of origins) {
      const url = targetFor(path, origin);
      if (!attempts.some(a => a.urlText === url)) attempts.push({ input: url, urlText: url });
    }
    let lastError = null;
    let lastResponse = null;
    for (let i = 0; i < attempts.length; i += 1) {
      const attempt = attempts[i];
      const started = performance.now ? performance.now() : Date.now();
      try {
        const response = await originalFetch(attempt.input, cloneOptions(init));
        const ms = Math.round((performance.now ? performance.now() : Date.now()) - started);
        push({ type: "fetch", apiPath: path, url: attempt.urlText, status: response.status, ok: response.ok, ms });
        if (!isRetryableResponse(response, attempt.urlText) || i === attempts.length - 1) return response;
        lastResponse = response;
        state.retries += 1;
      } catch (error) {
        const ms = Math.round((performance.now ? performance.now() : Date.now()) - started);
        lastError = error;
        state.lastError = String(error && (error.message || error));
        push({ type: "fetch-error", apiPath: path, url: attempt.urlText, error: state.lastError, ms });
        if (i === attempts.length - 1) throw error;
        state.retries += 1;
      }
    }
    if (lastResponse) return lastResponse;
    throw lastError || new TypeError("PRISMA API bridge could not reach Control Center API");
  }
  window.fetch = bridgedFetch;
  window.PRISMA_API_BRIDGE = { state, status(){ return JSON.parse(JSON.stringify(state)); }, enable(){ state.enabled = true; }, disable(){ state.enabled = false; }, apiPathFrom };
  push({ type: "boot", origin: currentOrigin(), apiPort: API_PORT });
})();
