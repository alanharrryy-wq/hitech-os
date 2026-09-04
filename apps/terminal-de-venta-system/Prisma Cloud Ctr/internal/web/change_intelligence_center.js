(function () {
  "use strict";

  const CONFIG_PATH = "/internal/config/change_intelligence_cloud.json";
  const HOST_HEALTH_PATH = "/api/health";

  const VIEW_META = {
    overview: {
      kicker: "CHANGE ASSURANCE",
      title: "Know the system. Control the change. Prove the result.",
      summary: "A governed, read-only product console over the existing Code Atlas Engine and shared PRISMA Cloud Center owners. Nothing becomes green merely because a UI can render it."
    },
    repositories: {
      kicker: "REPOSITORY CONTROL PLANE",
      title: "Repositories",
      summary: "Authorized repository registrations belong here once a read-only registry adapter is bound. V1 does not invent repositories or pretend a customer source connection exists."
    },
    runs: {
      kicker: "ANALYSIS EXECUTION",
      title: "Analysis Runs",
      summary: "Real run manifests, provenance and PASS/BLOCKED/UNKNOWN outcomes will project here. A missing run backend is shown as NOT_CONNECTED, never as an empty healthy system."
    },
    discover: {
      kicker: "DISCOVER",
      title: "See the truth before you touch the code.",
      summary: "Repository reality, architecture, dependencies, authority candidates, ownership, evidence relationships, critical gaps and explicit unknowns."
    },
    guard: {
      kicker: "GUARD",
      title: "Know the blast radius before it becomes an incident.",
      summary: "Change readiness, impact radius, explicit scope, protected boundaries and required evidence. Impact Radius informs; it never authorizes an edit."
    },
    control: {
      kicker: "CONTROL",
      title: "Give AI agents authority, not just context.",
      summary: "Bind task, target, allowed scope, protected scope, required evidence and compatibility locks before a human or agent can legitimately call a change done."
    },
    authority: {
      kicker: "AUTHORITY PACKS",
      title: "Portable change authority",
      summary: "Authority Packs are the handoff contract between repository evidence and the human or agent performing work. This console does not create fake packs when the engine adapter is not connected."
    },
    evidence: {
      kicker: "EVIDENCE",
      title: "Provenance before confidence",
      summary: "Evidence Reports, sanitized references and source boundaries make every material claim reviewable. Retrieval and derived indexes remain evidence locators, not truth."
    },
    roi: {
      kicker: "ROI",
      title: "Justify price with engineering time first.",
      summary: "ROI is input-driven. The console keeps the governing formulas visible but refuses to manufacture customer savings without measured inputs."
    },
    entitlements: {
      kicker: "SHARED PLATFORM OWNER",
      title: "Entitlements",
      summary: "Change Assurance should reuse PRISMA licensing and commercial owners through explicit adapters. It does not create a second licensing universe."
    }
  };

  const state = {
    config: null,
    hostHealth: null,
    configError: null,
    view: "overview"
  };

  const $ = (id) => document.getElementById(id);
  const $$ = (selector) => Array.from(document.querySelectorAll(selector));

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));
  }

  function compact(value, fallback = "-") {
    if (value === null || value === undefined || value === "") return fallback;
    if (Array.isArray(value)) return `${value.length} item${value.length === 1 ? "" : "s"}`;
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
  }

  function tone(value) {
    const text = String(value || "").toUpperCase();
    if (text.includes("BLOCK") || text.includes("FAIL") || text.includes("ERROR")) return "bad";
    if (text.includes("UNKNOWN") || text.includes("NOT_CONNECTED") || text.includes("NOT_MEASURED") || text.includes("PENDING") || text.includes("NOT_CERTIFIED") || text.includes("NOT_CLAIMED")) return "unknown";
    if (text.includes("LOCAL_VERIFIED") || text.includes("RUNTIME_VERIFIED") || text.includes("PASS") || text.includes("SOURCE_AVAILABLE") || text.includes("READY")) return "ok";
    if (text.includes("VERIFY") || text.includes("ADAPT") || text.includes("SHARED") || text.includes("REVIEW") || text.includes("BOUNDED")) return "warn";
    return "unknown";
  }

  function chip(value, label) {
    return `<span class="pci-mini-chip" data-tone="${esc(tone(value))}">${esc(label || value || "UNKNOWN")}</span>`;
  }

  function card(title, summary, body, options = {}) {
    const span = options.span || 6;
    const tag = options.tag ? chip(options.tag, options.tagLabel || options.tag) : "";
    const cardTone = options.tone ? ` data-tone="${esc(options.tone)}"` : "";
    return `<article class="pci-card" data-span="${esc(span)}"${cardTone}>
      <div class="pci-card-head">
        <div><h2>${esc(title)}</h2>${summary ? `<p>${esc(summary)}</p>` : ""}</div>
        ${tag}
      </div>
      ${body || ""}
    </article>`;
  }

  function list(rows) {
    const safeRows = Array.isArray(rows) ? rows : [];
    if (!safeRows.length) return empty("No source-backed rows", "The console will not manufacture rows to make the product look populated.");
    return `<div class="pci-list">${safeRows.map((row) => `<div class="pci-list-row"><span>${esc(row[0])}</span><strong>${esc(compact(row[1]))}</strong></div>`).join("")}</div>`;
  }

  function kpis(rows) {
    return `<div class="pci-kpi-grid">${rows.map((row) => `<div class="pci-kpi"><small>${esc(row[0])}</small><strong>${esc(compact(row[1]))}</strong>${row[2] ? `<span>${esc(row[2])}</span>` : ""}</div>`).join("")}</div>`;
  }

  function empty(title, detail) {
    return `<div class="pci-empty"><div><strong>${esc(title)}</strong><p>${esc(detail)}</p></div></div>`;
  }

  function code(value) {
    return `<pre class="pci-code">${esc(typeof value === "string" ? value : JSON.stringify(value, null, 2))}</pre>`;
  }

  function actions(items) {
    return `<div class="pci-action-row">${items.map((item) => `<a class="pci-action-link" href="${esc(item[0])}">${esc(item[1])}</a>`).join("")}</div>`;
  }

  function table(headers, rows) {
    if (!rows.length) return empty("No connected data", "The adapter for this dataset is not connected in V1.");
    return `<div class="pci-table-wrap"><table class="pci-table"><thead><tr>${headers.map((header) => `<th>${esc(header)}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${headers.map((header) => `<td>${esc(compact(row[header]))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
  }

  function config() {
    return state.config || {};
  }

  function controlPlane(key) {
    return config().controlPlane?.[key] || { status: "UNKNOWN", items: [] };
  }

  function product(id) {
    return (config().products || []).find((item) => item.id === id) || { id, name: id, status: "UNKNOWN", outputs: [] };
  }

  function sharedOwner(id) {
    return (config().sharedOwners || []).find((item) => item.id === id) || { id, maturity: "UNKNOWN", reuseMode: "UNKNOWN", boundary: "No owner mapping found." };
  }

  function updateChrome() {
    const maturity = config().maturity || {};
    const maturityChip = $("pciMaturityChip");
    const runtimeChip = $("pciRuntimeChip");

    if (maturityChip) {
      maturityChip.textContent = `Engine · ${compact(maturity.engineStatus, "UNKNOWN")}`;
      maturityChip.dataset.tone = tone(maturity.engineStatus);
    }

    if (runtimeChip) {
      const hostReachable = state.hostHealth?.ok === true || String(state.hostHealth?.status || "").toUpperCase().includes("PASS");
      runtimeChip.textContent = hostReachable ? "Cloud Center host · reachable" : "Cloud Center host · UNKNOWN";
      runtimeChip.dataset.tone = hostReachable ? "ok" : "unknown";
    }
  }

  function updateHeader() {
    const meta = VIEW_META[state.view] || VIEW_META.overview;
    $("pciViewKicker").textContent = meta.kicker;
    $("pciViewTitle").textContent = meta.title;
    $("pciViewSummary").textContent = meta.summary;
    $$("[data-pci-view]").forEach((node) => node.classList.toggle("active", node.dataset.pciView === state.view));

    const maturity = config().maturity || {};
    $("pciSealLabel").textContent = state.view === "overview" ? "ENGINE MATURITY" : meta.kicker;
    $("pciSealValue").textContent = state.view === "overview" ? compact(maturity.engineStatus, "UNKNOWN") : "READ-ONLY";
    $("pciSealDetail").textContent = state.view === "overview" ? `certifiable=${String(maturity.certifiable === true)}` : "No mutation from this console V1";
  }

  function updateAlert() {
    const alert = $("pciAlert");
    if (!alert) return;

    if (state.configError) {
      alert.dataset.tone = "bad";
      alert.innerHTML = `<strong>BLOCKED_CONFIG_UNAVAILABLE</strong><span>${esc(state.configError)}</span>`;
      return;
    }

    const maturity = config().maturity || {};
    if (maturity.productionCertified === true || maturity.certifiable === true) {
      alert.dataset.tone = "bad";
      alert.innerHTML = "<strong>CONTRACT_CONFLICT</strong><span>This V1 surface expected conservative maturity flags but received a certification claim. Review source authority before proceeding.</span>";
      return;
    }

    alert.dataset.tone = "warn";
    alert.innerHTML = `<strong>${esc(compact(maturity.engineStatus, "UNKNOWN"))}</strong><span>Source/local verification is not production certification. Human usefulness remains ${esc(compact(maturity.humanUsefulness, "UNKNOWN"))}; independent evaluator is ${esc(compact(maturity.independentEvaluator, "UNKNOWN"))}.</span>`;
  }

  function renderOverview() {
    const cfg = config();
    const maturity = cfg.maturity || {};
    const repo = controlPlane("repositories");
    const runs = controlPlane("analysisRuns");
    const entitlements = controlPlane("usageEntitlements");

    return [
      card("Product state", "What is proven now, without inflating the evidence ceiling.", kpis([
        ["Engine", maturity.engineStatus, maturity.engineClassification],
        ["Repositories", repo.status, `${repo.items?.length || 0} source-backed registrations`],
        ["Analysis runs", runs.status, `${runs.items?.length || 0} projected runs`],
        ["Entitlements", entitlements.status, "Shared owner contract"],
        ["Human usefulness", maturity.humanUsefulness, "External human study gate"],
        ["Production", maturity.productionCertified ? "CERTIFIED" : "NOT CERTIFIED", "Explicit evidence boundary"]
      ]), { span: 8, tag: maturity.engineStatus, tone: "accent" }),
      card("Authority", "Fresh task-exact Mesh behind this surface.", list([
        ["Mesh run", cfg.generatedFrom?.authorityMesh?.runId],
        ["Artifact", cfg.generatedFrom?.authorityMesh?.artifactId],
        ["Profile", cfg.generatedFrom?.authorityMesh?.profile],
        ["Authority coverage", cfg.generatedFrom?.authorityMesh?.requiredAuthorityCoverage],
        ["Layer Map", cfg.generatedFrom?.authorityMesh?.layerMapPresent ? "PRESENT" : "MISSING"],
        ["Base HEAD", cfg.generatedFrom?.baseHead]
      ]), { span: 4, tag: cfg.generatedFrom?.authorityMesh?.result || "UNKNOWN" }),
      card("Discover · Guard · Control", "Commercial products over one internal engine, not three duplicated codebases.", `<div class="pci-kpi-grid">${(cfg.products || []).map((item) => `<div class="pci-kpi"><small>${esc(item.name)}</small><strong>${esc(item.question)}</strong><span>${esc(item.promise)}</span></div>`).join("")}</div>`, { span: 12, tag: "PRODUCTS" }),
      card("Shared platform reuse", "Existing Cloud Center owners remain owners. Change Assurance consumes contracts instead of rebuilding them.", table(
        ["Owner", "Maturity", "Reuse", "Boundary"],
        (cfg.sharedOwners || []).map((item) => ({ Owner: item.id, Maturity: item.maturity, Reuse: item.reuseMode, Boundary: item.boundary }))
      ), { span: 12, tag: "NO REBUILD" }),
      card("V1 control-plane boundary", "The first slice is deliberately source-ready and read-only.", list([
        ["Organization context", controlPlane("organizationContext").status],
        ["Repository registry", repo.status],
        ["Run projection", runs.status],
        ["Authority Packs", controlPlane("authorityPacks").status],
        ["Evidence references", controlPlane("evidenceReferences").status],
        ["Usage / entitlements", entitlements.status]
      ]), { span: 6, tag: "FAIL CLOSED" }),
      card("Next allowed gates", "Advance by evidence, not by decorative confidence.", list([
        ["1", "Bind read-only repository registry adapter"],
        ["2", "Project real Code Atlas analysis manifests"],
        ["3", "Bind Authority Pack and Evidence references"],
        ["4", "Map Change Assurance entitlements to existing licensing owner"],
        ["5", "Measure ROI with customer inputs"],
        ["6", "Collect human and independent-agent usefulness evidence"]
      ]), { span: 6, tag: "NEXT" })
    ].join("");
  }

  function renderRepositories() {
    const repo = controlPlane("repositories");
    const rental = sharedOwner("private-repository-rental");
    return [
      card("Repository Registry", "No fake tenants, no fake repos.", repo.items?.length ? table(["Repository", "Status", "Mode"], repo.items) : empty(repo.status, repo.nextGate || "A read-only registry adapter is required."), { span: 8, tag: repo.status, tone: repo.status === "NOT_CONNECTED" ? "blocked" : "accent" }),
      card("Rental boundary", "Private-repository handling already has a hardened source owner from PR #299.", list([
        ["Reuse", rental.reuseMode],
        ["Maturity", rental.maturity],
        ["Read-only", "required"],
        ["Source egress", "DENIED BY DEFAULT"],
        ["Retention", "EPHEMERAL / BOUNDED"],
        ["Cleanup evidence", "required"]
      ]), { span: 4, tag: rental.maturity }),
      card("Repository lifecycle", "Target contract for the next adapter gate.", `<div class="pci-flow">${[
        ["REGISTER", "authorized repository ref"],
        ["RENT", "bounded workspace"],
        ["DISCOVER", "read-only intelligence"],
        ["PREPARE", "change model"],
        ["VERIFY", "evidence-backed result"],
        ["SANITIZE", "approved egress only"],
        ["CLEANUP", "lifecycle evidence"],
        ["EXPIRE", "retention boundary"],
        ["CONTINUE", "portable handoff"]
      ].map((step) => `<div class="pci-flow-step"><strong>${esc(step[0])}</strong><span>${esc(step[1])}</span></div>`).join("")}</div>`, { span: 12, tag: "CONTRACT" })
    ].join("");
  }

  function renderRuns() {
    const runs = controlPlane("analysisRuns");
    return [
      card("Run history", "Only engine-backed runs belong here.", runs.items?.length ? table(["Run", "Repository", "Intent", "Status"], runs.items) : empty(runs.status, runs.nextGate || "Bind real analysis-run manifests."), { span: 8, tag: runs.status, tone: "blocked" }),
      card("Result semantics", "A missing check cannot silently become green.", list([
        ["PASS", "All mandatory obligations represented by the evaluated contract are satisfied."],
        ["BLOCKED", "A required obligation failed or a protected boundary was violated."],
        ["UNKNOWN", "There is not enough evidence to make the requested claim."],
        ["NOT_EVALUATED", "The requested gate did not run or is outside the supported evidence envelope."]
      ]), { span: 4, tag: "NO FAKE GREEN" }),
      card("Run provenance", "Minimum information the future adapter must project.", list([
        ["Repository identity", "repository + commit/tree"],
        ["Intent", "DISCOVER / AUDIT / VERIFY / FIX / BUILD / CERTIFY when supported"],
        ["Authority", "explicit required authorities and state"],
        ["Target", "evidence-supported target only"],
        ["Inputs", "profile / policy / evidence digests"],
        ["Outputs", "manifest + result + evidence references"],
        ["Drift", "freshness / compatibility state"],
        ["Failure", "visible and fail-closed"]
      ]), { span: 12, tag: "PROVENANCE" })
    ].join("");
  }

  function renderProduct(id) {
    const item = product(id);
    const isGuard = id === "guard";
    const isControl = id === "control";
    const extras = isGuard ? [
      ["Impact Radius", "Evidence-backed affected-path model. It is not edit authorization."],
      ["Historical evidence", item.evidenceBoundary || "Bounded"],
      ["Protected scope", "Wins over widened scope."],
      ["Missing evidence", "BLOCKED or UNKNOWN, never green."]
    ] : isControl ? [
      ["Task", "normalized request"],
      ["Authority", "repository-evidence-backed authority"],
      ["Target", "explicit, not guessed"],
      ["Allowed scope", "explicit only"],
      ["Protected", "cannot be widened by Impact Radius"],
      ["Required evidence", "contract obligations"],
      ["Verify", "actual paths + evidence + compatibility"],
      ["Result", "PASS / BLOCKED / UNKNOWN"]
    ] : [
      ["Repository inventory", "technology-aware discovery"],
      ["Authority discovery", "candidate does not equal authority"],
      ["Graphs", "dependency, ownership, evidence, architecture"],
      ["Retrieval", "locates evidence, does not establish truth"],
      ["Snapshots", "portable identity and freshness"],
      ["Unknowns", "preserved explicitly"]
    ];

    return [
      card(item.name, item.promise, kpis([
        ["Status", item.status, item.question],
        ["Engine", config().product?.internalEngine, "Internal technology"],
        ["Mutation", "NONE FROM CLOUD V1", "Read-only projection"],
        ["Certification", "NOT CLAIMED", "Evidence ceiling preserved"]
      ]), { span: 7, tag: item.status, tone: "accent" }),
      card("Outputs", "Canonical outcome classes already owned by the engine.", list((item.outputs || []).map((output, index) => [`${index + 1}`, output])), { span: 5, tag: "REUSE AS IS" }),
      card("Operating contract", "What this product means in the governed pipeline.", list(extras), { span: 12, tag: "EVIDENCE FIRST" })
    ].join("");
  }

  function renderAuthority() {
    const packs = controlPlane("authorityPacks");
    return [
      card("Authority Packs", "Portable authority contracts are engine-owned; the Cloud console will only project real pack references.", packs.items?.length ? table(["Pack", "Repository", "Target", "Status"], packs.items) : empty(packs.status, "Connect the engine adapter before showing customer Authority Packs."), { span: 7, tag: packs.status, tone: "blocked" }),
      card("Pack invariants", "The safety properties the UI must not dilute.", list([
        ["Repository lock", "repository + commit/tree identity"],
        ["Target", "explicit and evidence-supported"],
        ["Allowed scope", "explicit only"],
        ["Protected scope", "wins over broad impact"],
        ["Policy/evidence digests", "compatibility locked"],
        ["Outside-scope drift", "BLOCKED"],
        ["Semantic retrieval", "not authority"]
      ]), { span: 5, tag: "LOCKED" }),
      card("Change loop", "The product-level handshake between preparation and verification.", `<div class="pci-flow">${[
        ["TASK", "request"],
        ["AUTHORITY", "facts"],
        ["TARGET", "exact"],
        ["BOUNDARY", "allowed"],
        ["PROTECTED", "do not touch"],
        ["IMPACT", "informs"],
        ["EVIDENCE", "required"],
        ["VERIFY", "actual result"],
        ["CONTINUE", "handoff"]
      ].map((step) => `<div class="pci-flow-step"><strong>${esc(step[0])}</strong><span>${esc(step[1])}</span></div>`).join("")}</div>`, { span: 12, tag: "CONTROL" })
    ].join("");
  }

  function renderEvidence() {
    const refs = controlPlane("evidenceReferences");
    const safety = config().safety || {};
    return [
      card("Evidence references", "No evidence bundle or report is represented as connected until an adapter supplies real references.", refs.items?.length ? table(["Evidence", "Type", "Status", "Provenance"], refs.items) : empty(refs.status, "Bind sanitized engine evidence references in a later gate."), { span: 7, tag: refs.status, tone: "blocked" }),
      card("Evidence laws", "Non-negotiable semantics inherited from Code Atlas.", list([
        ["Retrieval is proof", safety.retrievalIsNotProof ? "FALSE" : "UNKNOWN"],
        ["Derived index is authority", safety.derivedIndexIsNotAuthority ? "FALSE" : "UNKNOWN"],
        ["Impact Radius authorizes edits", safety.impactRadiusIsNotAuthorization ? "FALSE" : "UNKNOWN"],
        ["Unknown becomes green", safety.unknownRemainsUnknown ? "FALSE" : "UNKNOWN"],
        ["Source-code egress by default", safety.sourceCodeEgressDefault ? "TRUE - REVIEW" : "FALSE"],
        ["Frontend secrets", safety.noFrontendSecrets ? "FORBIDDEN" : "UNKNOWN"]
      ]), { span: 5, tag: "FAIL CLOSED" }),
      card("Canonical sources", "Source references behind this projection.", code(config().sourceRefs || []), { span: 12, tag: "PROVENANCE" })
    ].join("");
  }

  function renderRoi() {
    const roi = controlPlane("roi");
    const commercial = config().commercialReference || {};
    return [
      card("ROI Engine", "Engineering time is the hard-ROI foundation; risk reduction is optional and customer-supplied.", `<div class="pci-formula">
        <code>Measured Monthly Benefit = Discovery + Rework + Agent Supervision + Release/Evidence</code>
        <code>Net Monthly Value = Measured Monthly Benefit - Price</code>
        <code>ROI % = (Measured Monthly Benefit - Price) / Price × 100</code>
      </div>`, { span: 8, tag: roi.status, tone: "accent" }),
      card("Inputs required", "No savings number is emitted until these values exist.", list((roi.requiredCustomerInputs || []).map((item, index) => [`${index + 1}`, item])), { span: 4, tag: "NO ESTIMATE" }),
      card("Commercial reference", "Current documented founding terms and later targets, with evidence discipline preserved.", kpis([
        ["Founding Pilot", `$${compact(commercial.foundingPilotMxn)} MXN + IVA`, "first external validation cohort"],
        ["Founding Guard", `$${compact(commercial.foundingGuardMonthlyMxn)} MXN/mo + IVA`, `${compact(commercial.foundingGuardMonths)}-month validation period`],
        ["Standard Guard target", `$${compact(commercial.standardGuardTargetMonthlyMxn)} MXN/mo + IVA`, "only after recurring measured ROI"],
        ["Mature Pilot target", `$${compact(commercial.maturePilotTargetMxn)} MXN + IVA`, "not proven launch willingness-to-pay"],
        ["Control Design Partner", `$${(commercial.controlDesignPartnerMonthlyRangeMxn || []).join("–")} MXN/mo + IVA`, "after its own readiness evidence"]
      ]), { span: 12, tag: "REFERENCE" }),
      card("Pricing evidence rule", "Price follows external evidence, not internal enthusiasm.", list([
        ["Rule", commercial.pricingEvidenceRule],
        ["Current ROI state", roi.status],
        ["Customer savings shown", "NONE UNTIL INPUTS EXIST"]
      ]), { span: 12, tag: "DISCIPLINE" })
    ].join("");
  }

  function renderEntitlements() {
    const entitlements = controlPlane("usageEntitlements");
    const licensing = sharedOwner("licensing-contract-alignment");
    const registration = sharedOwner("customer-registration");
    const billing = sharedOwner("commercial-billing");
    return [
      card("Shared-owner status", "This vertical reuses PRISMA platform ownership instead of forking it.", kpis([
        ["Customer / tenant", registration.maturity, registration.reuseMode],
        ["Licensing", licensing.maturity, licensing.reuseMode],
        ["Commercial billing", billing.maturity, billing.reuseMode],
        ["CI entitlements", entitlements.status, "Adapter contract still pending"]
      ]), { span: 8, tag: "SHARED PLATFORM", tone: "accent" }),
      card("Boundary", "What this first slice is allowed to do.", list([
        ["Read entitlements", "future adapter, read-only"],
        ["Activate license", "EXISTING OWNER ONLY"],
        ["Refresh license", "EXISTING OWNER ONLY"],
        ["Revoke license", "EXISTING OWNER ONLY"],
        ["Create billing records", "EXISTING OWNER ONLY"],
        ["Create second licensing subsystem", "FORBIDDEN"]
      ]), { span: 4, tag: "DO NOT REBUILD" }),
      card("Next entitlement contract", "The missing seam is mapping product access, not reconstructing license mechanics.", list([
        ["Product", "change_intelligence"],
        ["Capabilities", "discover / guard / control"],
        ["Repository limit", "customer contract input"],
        ["Run or Guard-pack limit", "customer contract input"],
        ["Control enabled", "explicit entitlement"],
        ["Status", entitlements.status],
        ["Next gate", entitlements.nextGate]
      ]), { span: 12, tag: "ADAPTER" })
    ].join("");
  }

  function renderView() {
    if (state.configError) {
      $("pciContent").innerHTML = card("BLOCKED_CONFIG_UNAVAILABLE", "The governed source contract could not be loaded.", code({ error: state.configError, configPath: CONFIG_PATH }), { span: 12, tag: "BLOCKED", tone: "blocked" });
      return;
    }

    const renderers = {
      overview: renderOverview,
      repositories: renderRepositories,
      runs: renderRuns,
      discover: () => renderProduct("discover"),
      guard: () => renderProduct("guard"),
      control: () => renderProduct("control"),
      authority: renderAuthority,
      evidence: renderEvidence,
      roi: renderRoi,
      entitlements: renderEntitlements
    };

    const renderer = renderers[state.view] || renderOverview;
    $("pciContent").innerHTML = renderer();
  }

  function readView() {
    const raw = String(window.location.hash || "#overview").replace(/^#\/?/, "").trim();
    return Object.prototype.hasOwnProperty.call(VIEW_META, raw) ? raw : "overview";
  }

  async function getJson(path) {
    const response = await fetch(path, {
      cache: "no-store",
      headers: { Accept: "application/json" }
    });
    if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`);
    return response.json();
  }

  async function boot() {
    state.view = readView();

    try {
      state.config = await getJson(CONFIG_PATH);
      document.documentElement.dataset.pciState = "contract-loaded";
    } catch (error) {
      state.configError = String(error?.message || error);
      document.documentElement.dataset.pciState = "blocked";
    }

    try {
      state.hostHealth = await getJson(HOST_HEALTH_PATH);
    } catch (_) {
      state.hostHealth = { ok: false, status: "UNKNOWN" };
    }

    updateChrome();
    updateHeader();
    updateAlert();
    renderView();
  }

  window.addEventListener("hashchange", () => {
    state.view = readView();
    updateHeader();
    renderView();
  });

  window.addEventListener("DOMContentLoaded", boot);
})();
