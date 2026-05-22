(function(){
  "use strict";
  const STORE_INTERFACE = "prisma-control-center-interface-v1";
  const ACTION_LABELS = {
    "self-test":"Self-Test",
    "list":"Listar perfiles",
    "first-run":"Instalacion nueva",
    "client-readiness":"Cliente listo",
    "demo":"Demo segura",
    "support-pack":"Paquete soporte",
    "upgrade":"Upgrade check",
    "pilot":"Piloto cliente"
  };
  const $ = (selector, root=document) => root.querySelector(selector);
  const $$ = (selector, root=document) => Array.from(root.querySelectorAll(selector));
  function esc(value){return String(value ?? "").replace(/[&<>'"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[ch]));}
  function text(selector, value){const node=$(selector); if(node) node.textContent=String(value ?? "");}
  function tone(decision){const s=String(decision||"").toUpperCase(); if(["PASS","READY","READY_FOR_CUSTOMER_PROMOTION","OK","COMPLETED"].includes(s)) return "ok"; if(s.includes("WARN") || s.includes("FINDINGS") || s.includes("WATCH")) return "warn"; if(s.includes("BLOCK") || s.includes("FAIL") || s.includes("ERROR")) return "bad"; if(s.includes("RUN")) return "running"; return "";}
  function shortPath(path){if(!path || path==="<redacted>") return path || "-"; const raw=String(path); const slash=Math.max(raw.lastIndexOf("/"), raw.lastIndexOf("\\")); return slash>=0 ? raw.slice(slash+1) : raw;}
  function toast(message){if(typeof window.toast==="function") window.toast(message); else console.info("[PRISMA Quality Bay]", message);}
  async function fetchJson(url){const response=await fetch(url,{cache:"no-store",headers:{Accept:"application/json"}}); const payload=await response.json().catch(()=>({})); if(!response.ok){const err=new Error(payload.error || payload.reason || `${url} ${response.status}`); err.payload=payload; throw err;} return payload;}
  function setSurface(name){
    const surface = name === "quality" ? "quality" : name === "license" ? "license" : "operation";
    document.body.dataset.prismaInterface = surface;
    try{localStorage.setItem(STORE_INTERFACE, surface);}catch(_e){}
    const qSurface = $("#qualityBaySurface");
    if(qSurface) qSurface.hidden = surface !== "quality";
    const licenseSurface = $("#licenseOpsSurface");
    if(licenseSurface) licenseSurface.hidden = surface !== "license";
    $$('[data-prisma-interface-target]').forEach(button => {
      const active = button.dataset.prismaInterfaceTarget === surface;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    const title = $(".titles h1");
    const subtitle = $("#subtitle");
    const chips = $$(".chips .chip");
    if(surface === "quality"){
      if(title) title.textContent = "PRISMA Quality Bay";
      if(subtitle) subtitle.textContent = "Customer Assurance · instalacion, soporte, upgrade y evidencia.";
      if(chips[0]) chips[0].innerHTML = '<span class="dot"></span>Assurance';
      if(chips[1]) chips[1].textContent = "Evidencia local";
      if(chips[2]) chips[2].textContent = "Control audit-only";
      refreshQualityLatest();
    }else if(surface === "license"){
      if(title) title.textContent = "PRISMA License Ops";
      if(subtitle) subtitle.textContent = "Runtime, identidad, licencia local y evidencia de provisioning.";
      if(chips[0]) chips[0].innerHTML = '<span class="dot"></span>Local-first';
      if(chips[1]) chips[1].textContent = "ProgramData canonical";
      if(chips[2]) chips[2].textContent = "Tablet sola";
      window.PRISMA_LICENSE_OPS?.refresh?.();
    }else{
      if(title) title.textContent = "Cabina operativa premium";
      if(subtitle) subtitle.textContent = "Liquid Metal · reactor, rutas, señales, evidencia y auditoría.";
      if(chips[0]) chips[0].innerHTML = '<span class="dot"></span>Stable';
      if(chips[1]) chips[1].textContent = "Frescura 4 s";
      if(chips[2]) chips[2].textContent = "Confianza 97%";
    }
    window.scrollTo({top:0,behavior:"smooth"});
  }
  function renderInstalled(installed){
    const items = [
      ["Quality", installed && installed.qualityRoot],
      ["CLI", installed && installed.cli],
      ["Perfiles", installed && installed.profiles],
      ["Gates", installed && installed.gates]
    ];
    const html=items.map(([label,ok])=>`<div class="qualityInstallItem" data-ok="${!!ok}"><small>${esc(label)}</small><strong>${ok?"Presente":"Falta"}</strong></div>`).join("");
    const node=$("#qualityInstallStrip"); if(node) node.innerHTML=html;
  }
  function renderLedger(run){
    const node=$("#qualityLedger"); if(!node) return;
    if(!run || !run.available){node.innerHTML='<div class="qualityEmpty">Sin corridas todavía. El primer botón va a dejar evidencia visible aquí.</div>'; return;}
    const artifacts=run.artifacts || {};
    const rows=[
      ["Run", run.profile || "quality", run.decision || "UNKNOWN"],
      ["Decision", "QUALITY_DECISION.json", artifacts.decision && artifacts.decision.exists ? "listo" : "pendiente"],
      ["Summary", "QUALITY_MACHINE_SUMMARY.json", artifacts.summary && artifacts.summary.exists ? "listo" : "pendiente"],
      ["Ledger", "CUSTOMER_EVIDENCE_LEDGER.json", artifacts.ledger && artifacts.ledger.exists ? "listo" : "pendiente"]
    ];
    node.innerHTML=rows.map(row=>`<div class="qualityLedgerRow"><small>${esc(row[0])}</small><strong>${esc(row[1])}</strong><span class="qTag ${tone(row[2])}">${esc(row[2])}</span></div>`).join("");
  }
  function renderFindings(run){
    const node=$("#qualitySummaryList"); if(!node) return;
    if(!run || !run.available){node.innerHTML='<div class="qualityEmpty">Esperando una corrida de Quality.</div>'; return;}
    const findings=[...(run.topBlockers || []), ...(run.topWarnings || [])].slice(0,6);
    if(!findings.length){node.innerHTML='<div class="qualityEmpty">Sin blockers ni warnings en la última corrida.</div>'; return;}
    node.innerHTML=findings.map(f=>`<div class="qualityFinding"><b>${esc(f.id || f.title || "Finding")}</b><span>${esc(f.detail || f.recommendation || f.message || "Sin detalle")}</span></div>`).join("");
  }
  function renderLatest(payload){
    const run=payload && payload.latestRun;
    renderInstalled(payload && payload.installed);
    renderLedger(run);
    renderFindings(run);
    const decision = run && run.available ? (run.decision || "UNKNOWN") : "IDLE";
    const t = tone(decision);
    text("#qualityDecision", decision);
    const decisionNode=$("#qualityDecision"); if(decisionNode) decisionNode.className = `qTag ${t}`;
    text("#qualityGaugeNumber", run && run.available ? (run.blockerCount > 0 ? "B" : run.warningCount > 0 ? "W" : "OK") : "--");
    text("#qualityGaugeLabel", run && run.available ? (run.profile || "quality") : "sin corrida");
    text("#qualityGaugeSub", run && run.available ? `blockers ${run.blockerCount ?? 0} · warnings ${run.warningCount ?? 0}` : "listo para verificar");
    text("#qualityStatProfile", run && run.available ? run.profile || "-" : "-");
    text("#qualityStatBlockers", run && run.available ? run.blockerCount ?? 0 : "-");
    text("#qualityStatWarnings", run && run.available ? run.warningCount ?? 0 : "-");
    text("#qualityStatRun", run && run.available ? run.runId || "-" : "-");
    text("#qualityOutDir", payload && payload.outDir ? payload.outDir : "-");
  }
  async function refreshQualityLatest(){
    try{renderLatest(await fetchJson("/api/quality/latest"));}
    catch(error){
      text("#qualityDecision", "API ERROR");
      const node=$("#qualityDecision"); if(node) node.className="qTag bad";
      const result=$("#qualityResultText"); if(result) result.textContent = String(error.message || error);
    }
  }
  function renderRunResult(payload){
    const summary=payload && payload.summary;
    const label=payload.label || ACTION_LABELS[payload.action] || payload.action || "Quality";
    const decision=summary && summary.available ? summary.decision : payload.status;
    text("#qualityLastAction", label);
    const statusNode=$("#qualityRunStatus"); if(statusNode){statusNode.textContent=String(decision || "UNKNOWN"); statusNode.className=`qTag ${tone(decision)}`;}
    const lines=[];
    lines.push(`Accion: ${label}`);
    lines.push(`Status: ${payload.status || "-"}`);
    lines.push(`Return code: ${payload.returnCode ?? "-"}`);
    if(summary && summary.available){
      lines.push(`Decision: ${summary.decision || "-"}`);
      lines.push(`Profile: ${summary.profile || "-"}`);
      lines.push(`Blockers: ${summary.blockerCount ?? 0}`);
      lines.push(`Warnings: ${summary.warningCount ?? 0}`);
      const runDir=summary.artifacts && summary.artifacts.runDir && summary.artifacts.runDir.path;
      lines.push(`Run dir: ${runDir || "-"}`);
    }
    if(payload.log) lines.push(`Log: ${payload.log}`);
    lines.push("");
    lines.push("STDOUT");
    lines.push(payload.stdoutSample || "Sin salida stdout.");
    if(payload.stderrSample){lines.push(""); lines.push("STDERR"); lines.push(payload.stderrSample);}
    const result=$("#qualityResultText"); if(result) result.textContent=lines.join("\n");
    if(payload.latest) renderLatest(payload.latest);
    const button=$(`[data-quality-action="${payload.action}"]`);
    if(button){button.dataset.last = payload.ok ? (tone(decision)==="bad" ? "bad" : tone(decision)==="warn" ? "warn" : "ok") : "bad"; const st=$(".qActionStatus",button); if(st) st.textContent=payload.ok ? (decision || "done") : "error";}
  }
  async function runQuality(action, button){
    if(button && button.dataset.running==="true") return;
    const all=$$("[data-quality-action]");
    all.forEach(b=>b.disabled=true);
    if(button){button.dataset.running="true"; const st=$(".qActionStatus", button); if(st) st.textContent="running";}
    text("#qualityLastAction", ACTION_LABELS[action] || action);
    const statusNode=$("#qualityRunStatus"); if(statusNode){statusNode.textContent="RUNNING"; statusNode.className="qTag running";}
    const result=$("#qualityResultText"); if(result) result.textContent=`Ejecutando ${ACTION_LABELS[action] || action}...`;
    try{
      const payload=await fetchJson(`/api/quality/run/${encodeURIComponent(action)}`);
      renderRunResult(payload);
      toast(`Quality: ${payload.label || action} terminado`);
    }catch(error){
      const payload=error.payload || {ok:false,status:"ERROR",action,error:String(error.message || error)};
      renderRunResult(payload);
      toast(`Quality fallo: ${error.message || error}`);
    }finally{
      all.forEach(b=>b.disabled=false);
      if(button){button.dataset.running="false";}
    }
  }
  function wireQuality(){
    document.body.classList.add("quality-bay-ready");
    $$('[data-prisma-interface-target]').forEach(button=>button.addEventListener("click",()=>setSurface(button.dataset.prismaInterfaceTarget)));
    $$('[data-quality-action]').forEach(button=>{
      button.addEventListener("click",()=>runQuality(button.dataset.qualityAction, button));
      button.addEventListener("pointermove", event=>{
        const box=button.getBoundingClientRect();
        button.style.setProperty("--mx", `${((event.clientX-box.left)/box.width)*100}%`);
        button.style.setProperty("--my", `${((event.clientY-box.top)/box.height)*100}%`);
      }, {passive:true});
      button.addEventListener("pointerleave",()=>{button.style.setProperty("--mx","50%"); button.style.setProperty("--my","20%");});
    });
    const initial = (location.hash === "#quality" || location.hash === "#quality-bay") ? "quality" : (location.hash === "#license-ops" || location.hash === "#licencias") ? "license" : (localStorage.getItem(STORE_INTERFACE) || "operation");
    setSurface(initial);
    window.setInterval(()=>{if(document.body.dataset.prismaInterface==="quality") refreshQualityLatest();}, 15000);
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", wireQuality); else wireQuality();
  window.PRISMA_QUALITY_BAY={setSurface, refresh:refreshQualityLatest, run:runQuality};
})();
