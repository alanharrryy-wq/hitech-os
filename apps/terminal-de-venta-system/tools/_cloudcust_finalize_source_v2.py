#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot structural finalizer for PR #254.

Temporary CI helper. It is intentionally plain UTF-8 source, never base64/zip,
and must be removed by the successful finalization workflow.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

APP = Path("apps/terminal-de-venta-system")
STORE = APP / "Prisma Cloud Ctr/internal/py/command_center_store.py"
JS = APP / "Prisma Cloud Ctr/internal/web/cloud_command_center.js"
HTML = APP / "Prisma Cloud Ctr/internal/web/cloud_command_center.html"
EVIDENCE = Path(".cloudcust-evidence")
EVIDENCE.mkdir(exist_ok=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"ANCHOR_COUNT_{label}:{count}")
    return text.replace(old, new, 1)


def replace_between(text: str, start: str, end: str, replacement: str, label: str) -> str:
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"ANCHOR_START_{label}_MISSING")
    b = text.find(end, a + len(start))
    if b < 0:
        raise SystemExit(f"ANCHOR_END_{label}_MISSING")
    second = text.find(start, a + len(start), b)
    if second >= 0:
        raise SystemExit(f"ANCHOR_{label}_AMBIGUOUS")
    return text[:a] + replacement + text[b:]


def regex_once(text: str, pattern: str, replacement: str, label: str, flags: int = 0) -> str:
    out, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"REGEX_COUNT_{label}:{count}")
    return out


before = {str(p): sha256(p) for p in (STORE, JS, HTML)}

# ---------------------------------------------------------------------------
# Store: tiny seam only. Runtime behavior lives in customer_registration_runtime.py.
# ---------------------------------------------------------------------------
store = STORE.read_text(encoding="utf-8")
store = replace_once(store, "import json\nimport hashlib\n", "import json\nimport hashlib\nimport os\n", "STORE_IMPORT_OS")
store = replace_once(
    store,
    'DB_PATH = DATA_DIR / "prisma-command-center.db"',
    'DB_PATH = Path(os.environ.get("PRISMA_COMMAND_CENTER_DB_PATH") or (DATA_DIR / "prisma-command-center.db"))',
    "STORE_DB_OVERRIDE",
)
hook = '''# Governed customer-registration runtime adapter. Installed last so unrelated\n# billing/support/licensing behavior remains owned by the original store.\nfrom customer_registration_runtime import install_runtime as _install_customer_registration_runtime\n_install_customer_registration_runtime(globals())\n\n'''
store = replace_once(store, 'if __name__ == "__main__":\n', hook + 'if __name__ == "__main__":\n', "STORE_RUNTIME_HOOK")
STORE.write_text(store, encoding="utf-8")

# ---------------------------------------------------------------------------
# Browser operator ergonomics and governed registration workflow.
# ---------------------------------------------------------------------------
js = JS.read_text(encoding="utf-8")

# The previous finalizer failed here because it cared about whitespace/comma style.
# This structural expression accepts either style but still requires exactly one state tail.
if "refreshRenderPending" not in js:
    js = regex_once(
        js,
        r"(\n\s*openPicker\s*:\s*null)(,?)(\s*\n\s*};)",
        r"\1,\n    refreshRenderPending: false\3",
        "JS_REFRESH_STATE",
    )

# Required/selects may opt out of an implicit first-option default. Manual facts should
# not silently become the first catalog entry just because the list is non-empty.
js = replace_once(
    js,
    '    const effectiveSelected=selected || opts?.defaultValue || options[0]?.code || "";',
    '    const effectiveSelected=selected || opts?.defaultValue || (opts?.noDefault ? "" : (options[0]?.code || ""));',
    "JS_SELECT_NO_DEFAULT",
)

js = replace_once(
    js,
    '  function catalogOptions(code){ return (catalogs()[code]?.options || []).filter((item)=>item.active !== false); }',
    '''  function catalogOptions(code){\n    let options = (catalogs()[code]?.options || []).filter((item)=>item.active !== false);\n    if (code === "subvertical") {\n      const vertical = flowValue("vertical", "");\n      options = options.filter((item) => { const parents=(item.metadata||{}).parentVerticals||[]; return item.code==="other" || !parents.length || !vertical || parents.includes(vertical); });\n    }\n    if (code === "device_role") {\n      const type = flowValue("deviceType", "");\n      options = options.filter((item) => { const types=(item.metadata||{}).deviceTypes||[]; return !types.length || !type || types.includes(type); });\n    }\n    if (code === "state_mx" && flowValue("country", "") !== "MX") return [];\n    return options;\n  }''',
    "JS_DEPENDENT_CATALOGS",
)

client_wizard = '''  function clientWizard(){\n    const r=currentRecommendation();\n    const country=flowValue("country","");\n    const requestId=flowValue("clientRequestId","");\n    return `<div class="cc-flow-grid" data-customer-registration-form="v2">\n      ${textField("displayName","Nombre comercial",flowValue("displayName"),{required:true,placeholder:"Ej. Abarrotes Don Pepe"})}\n      ${textField("legalName","Razón social",flowValue("legalName"),{placeholder:"Opcional; no se infiere"})}\n      ${textField("contactName","Contacto",flowValue("contactName"),{placeholder:"Nombre de contacto"})}\n      ${selectField("contactRole","Rol del contacto","contact_role",flowValue("contactRole"),{noDefault:true})}\n      ${textField("phone","Teléfono",flowValue("phone"),{placeholder:"Teléfono o correo obligatorio"})}\n      ${textField("email","Correo",flowValue("email"),{placeholder:"correo@negocio.mx"})}\n      ${selectField("vertical","Giro / vertical","vertical",flowValue("vertical"),{required:true,noDefault:true})}\n      ${selectField("subvertical","Subvertical","subvertical",flowValue("subvertical"),{noDefault:true})}\n      ${selectField("businessSize","Tamaño operativo","business_size",flowValue("businessSize"),{required:true,noDefault:true})}\n      ${selectField("operationMode","Tipo de operación","operation_mode",flowValue("operationMode"),{required:true,noDefault:true})}\n      ${selectField("acquisitionChannel","Cómo llegó el cliente","acquisition_channel",flowValue("acquisitionChannel"),{required:true,noDefault:true})}\n      ${selectField("country","País","country",country,{noDefault:true})}\n      ${country==="MX"?selectField("state","Estado","state_mx",flowValue("state"),{noDefault:true}):""}\n      ${textField("city","Ciudad",flowValue("city"),{placeholder:"Dato manual verificable"})}\n      ${textField("zone","Zona / colonia",flowValue("zone"),{placeholder:"Opcional"})}\n      <input type="hidden" data-flow-field="clientRequestId" value="${esc(requestId)}" />\n    </div>\n    <div class="cc-impact"><strong>Recomendación automática</strong><span>${esc(catalogLabel("license_plan",r.plan))} · ${esc(catalogLabel("device_type",r.device))}. El plan no se captura dos veces.</span></div>\n    ${actions([actionButton("prepare-client","Preparar alta","primary"),surfaceButton("entitlements","Ver recomendación / licencia"),surfaceButton("fleet","Agregar dispositivo")])}`;\n  }\n'''
js = replace_between(js, "  function clientWizard(){", "  function deviceWizard(){", client_wizard, "JS_CLIENT_WIZARD")

device_wizard = '''  function deviceWizard(){\n    const r=currentRecommendation();\n    const type=flowValue("deviceType",r.device);\n    return `<div class="cc-flow-grid">\n      ${selectField("clientCode","Cliente destino","client",flowValue("clientCode"),{required:true,noDefault:true})}\n      ${selectField("deviceType","Tipo de dispositivo","device_type",type,{required:true})}\n      ${selectField("deviceRole","Rol del dispositivo","device_role",flowValue("deviceRole"),{required:true,noDefault:true})}\n      ${textField("deviceAlias","Alias visible",flowValue("deviceAlias"),{placeholder:"Ej. Caja principal"})}\n    </div>\n    <div class="cc-impact"><strong>Alcance</strong><span>Se deriva del contrato/licencia. La sucursal o zona ya no se duplica manualmente en el dispositivo.</span></div>\n    ${actions([actionButton("prepare-device","Generar dispositivo + código","primary"),actionButton("device-smoke","Registrar prueba cloud"),actionButton("receipt-smoke","Enviar receipt de prueba")])}\n    ${details("Dispositivos preparados", { devices: localRows("devices") }, false)}`;\n  }\n'''
js = replace_between(js, "  function deviceWizard(){", "function licenseWizard(){", device_wizard, "JS_DEVICE_WIZARD")

deactivation_wizard = '''  function deactivationWizard(){\n    const kind=flowValue("targetKind","client");\n    const targetCatalog={client:"client",license:"license_assignment",device:"managed_device"}[kind]||"client";\n    return `<div class="cc-flow-grid">\n      ${selectField("targetKind","Qué se dará de baja","deactivation_target_kind",kind,{required:true})}\n      ${selectField("targetCode","Objetivo exacto",targetCatalog,flowValue("targetCode"),{required:true,noDefault:true})}\n      ${selectField("reason","Motivo","deactivation_reason",flowValue("reason","cancellation"),{required:true})}\n    </div>\n    <div class="cc-impact"><strong>Impacto antes de confirmar</strong><span>Historial se conserva · cloud no se toca todavía · objetivo exacto, sin texto libre</span></div>\n    ${actions([actionButton("prepare-deactivation","Preparar baja segura","primary"),surfaceButton("system","Ver técnico")])}\n    ${details("Bajas preparadas", { deactivations: localRows("deactivations") }, false)}`;\n  }\n\n'''
js = replace_between(js, "  function deactivationWizard(){", "  function jsonValue", deactivation_wizard, "JS_DEACTIVATION_WIZARD")

customer_render = '''  function customerMetricsPanel(){\n    const metrics=ccStore().customerMetrics||{};\n    const q=metrics.dataQuality||{};\n    const acquisition=(metrics.byAcquisition||[]).map((row)=>[catalogLabel("acquisition_channel",row.code)||row.code,row.count]);\n    const relationship=(metrics.byRelationshipStage||[]).map((row)=>[catalogLabel("relationship_stage",row.code)||row.code,row.count]);\n    return [\n      kvGrid([["Perfiles medidos",metrics.profiles||0],["Clasificación legacy del seed",q.seedLegacyClassificationNeedsReview?"Revisar":"Sin inferencias"],["city_zone legacy",q.legacyCityZoneValues||0],["Modo",q.measurementMode||"manual + derivado"]]),\n      acquisition.length?list(acquisition):`<div class="cc-empty">Aún no hay adquisición medida. Se llenará con altas verificadas.</div>`,\n      relationship.length?list(relationship):""\n    ].join("");\n  }\n  function renderCustomers() { const d=derived(); const c=localCounts(); return [\n    panel("Clientes activos","Clientes preparados localmente + cliente observado en cloud.",kvGrid([["Clientes preparados",c.clients||0],["Activos/preparados",c.activeClients||0],["Cliente cloud",d.tenant?.displayName||d.tenant?.slug||FIRST_CUSTOMER_NAME],["Otros por revisar",c.othersPending||0]]),{span:5,tag:"CLIENTES"}),\n    panel("Acciones","Operación centrada en cliente, no en módulos técnicos.",actions([surfaceButton("provisioning","+ Nuevo cliente"),actionButton("copy-clients-local","Copiar clientes locales"),surfaceButton("entitlements","Asignar licencia"),surfaceButton("fleet","Agregar dispositivo"),surfaceButton("security","Dar baja")]),{span:7,tag:"ACCIONES"}),\n    panel("Medición homologada","Adquisición, relación y calidad de datos sin inventar atributos del cliente semilla.",customerMetricsPanel(),{span:12,tag:"MEDICIÓN"}),\n    panel("Mesa de clientes","Abrir filas, revisar vertical/estado y decidir siguiente acción.",localDesk("clients","Todavía no hay clientes preparados."),{span:12,tag:`${c.clients||0} local`}),\n    panel("Auditoría del cliente","Últimos eventos del motor de catálogos/IDs.",localDesk("events","Todavía no hay eventos locales."),{span:12,tag:"AUDIT"}),\n    resultPanel()\n  ].join(""); }\n'''
js = replace_between(js, "  function renderCustomers()", "  function bridgePayload", customer_render, "JS_CUSTOMER_METRICS")

render_anchor = '''  function render() {\n    updateChrome();\n    updateSurfaceHeader();\n    const renderer = renderers[state.surface] || renderCommand;\n    $("surfaceRoot").innerHTML = renderer();\n  }\n'''
render_replacement = render_anchor + '''  function syncFlowFromDom(){\n    const root=$("surfaceRoot");\n    if(!root) return;\n    root.querySelectorAll("[data-flow-field]").forEach((field)=>{ const key=field.dataset.flowField; if(key) state.flow[key]=field.value; });\n    root.querySelectorAll("[data-other-for]").forEach((field)=>{ const key=field.dataset.otherFor; if(key) state.flow[key+"Other"]=field.value; });\n  }\n  function operatorIsInteracting(){\n    const root=$("surfaceRoot"), active=document.activeElement;\n    const focused=!!(root&&active&&root.contains(active)&&active.matches("input,select,textarea,button,[contenteditable='true']"));\n    return focused || !!state.openPicker;\n  }\n  function renderAfterRefresh(){\n    if(operatorIsInteracting()){ state.refreshRenderPending=true; return; }\n    state.refreshRenderPending=false;\n    render();\n  }\n  function reconcileDependencies(changed){\n    if(changed==="vertical"){ const valid=new Set(catalogOptions("subvertical").map((x)=>x.code)); if(state.flow.subvertical&&!valid.has(state.flow.subvertical)) state.flow.subvertical=""; }\n    if(changed==="deviceType"){ const valid=new Set(catalogOptions("device_role").map((x)=>x.code)); if(state.flow.deviceRole&&!valid.has(state.flow.deviceRole)) state.flow.deviceRole=""; }\n    if(changed==="targetKind") state.flow.targetCode="";\n    if(changed==="country" && state.flow.country!=="MX") state.flow.state="";\n  }\n'''
js = replace_once(js, render_anchor, render_replacement, "JS_RENDER_SAFETY")

load_start = js.find("  async function loadAll() {")
load_end = js.find("  async function postAction", load_start)
if load_start < 0 or load_end < 0:
    raise SystemExit("LOADALL_ANCHOR_MISSING")
load_block = js[load_start:load_end]
if load_block.count("    render();") != 1:
    raise SystemExit(f"LOADALL_RENDER_COUNT:{load_block.count('    render();')}")
load_block = load_block.replace("    render();", "    renderAfterRefresh();")
js = js[:load_start] + load_block + js[load_end:]

js = replace_once(
    js,
    '  async function handleAction(action, button) {\n    if (state.busy) return;\n',
    '  async function handleAction(action, button) {\n    syncFlowFromDom();\n    if (state.busy) return;\n',
    "JS_ACTION_SYNC",
)

old_prepare = '      } else if (action === "prepare-client") { result = await postAction("/api/command-center/draft-client", { ...state.flow, other: collectOtherValues() }); setResult("Alta preparada", result.message || "Cliente preparado localmente.", result, { kind: result.ok ? "ok" : "warn" }); toast(result.ok ? "Alta preparada" : "Alta a revisar"); await loadAll();\n'
new_prepare = '''      } else if (action === "prepare-client") {\n        if (!state.flow.clientRequestId) state.flow.clientRequestId = `customer-${Date.now()}-${globalThis.crypto?.randomUUID?.() || Math.random().toString(36).slice(2)}`;\n        result = await safePost("/api/command-center/draft-client", { ...state.flow, other: collectOtherValues() });\n        setResult("Alta preparada", result.message || `${result.resultCode||"REVIEW"}: ${result.error||"Revisar datos"}`, result, { kind: result.ok ? "ok" : "warn" });\n        toast(result.ok ? (result.idempotent ? "Alta ya existente" : "Alta preparada") : "Alta a revisar");\n        if (result.ok) await loadAll();\n'''
js = replace_once(js, old_prepare, new_prepare, "JS_PREPARE_CLIENT")

input_start = js.find('    document.addEventListener("input", (event) => {')
change_start = js.find('    document.addEventListener("change", (event) =>', input_start)
click_start = js.find('    document.addEventListener("click", (event) => {', change_start)
if min(input_start, change_start, click_start) < 0:
    raise SystemExit("JS_EVENT_ANCHOR_MISSING")
event_replacement = '''    document.addEventListener("input", (event) => {\n      const filter=event.target.closest("[data-picker-filter]");\n      if(filter){\n        const panel=filter.closest("[data-picker-panel]");\n        const q=String(filter.value||"").trim().toLowerCase();\n        if(panel) panel.querySelectorAll("[data-picker-search]").forEach((row)=>{row.hidden=!!q&&!String(row.dataset.pickerSearch||"").includes(q);});\n        return;\n      }\n      const field=event.target.closest("[data-flow-field]");\n      if(field){\n        state.flow[field.dataset.flowField]=field.value;\n        if(field.dataset.flowField!=="clientRequestId") state.flow.clientRequestId="";\n        return;\n      }\n      const other=event.target.closest("[data-other-for]");\n      if(other){ state.flow[other.dataset.otherFor+"Other"]=other.value; state.flow.clientRequestId=""; }\n    });\n    document.addEventListener("change", (event) => {\n      const field=event.target.closest("[data-flow-field]");\n      if(field){\n        syncFlowFromDom();\n        state.flow[field.dataset.flowField]=field.value;\n        if(field.dataset.flowField!=="clientRequestId") state.flow.clientRequestId="";\n        reconcileDependencies(field.dataset.flowField);\n        render();\n      }\n    });\n'''
js = js[:input_start] + event_replacement + js[click_start:]

js = replace_once(
    js,
    '        const pickerId = pickerToggleNode.dataset.pickerToggle || "";\n        state.openPicker = state.openPicker === pickerId ? null : pickerId;\n        render();\n        return;\n',
    '        syncFlowFromDom();\n        const pickerId = pickerToggleNode.dataset.pickerToggle || "";\n        state.openPicker = state.openPicker === pickerId ? null : pickerId;\n        render();\n        if(state.openPicker) setTimeout(()=>document.querySelector(`[data-picker-filter="${CSS.escape(pickerId)}"]`)?.focus(),0);\n        return;\n',
    "JS_PICKER_TOGGLE_SYNC",
)
js = replace_once(
    js,
    '        if (field) {\n          state.flow[field] = value;\n          state.openPicker = null;\n          render();\n        }\n',
    '        if (field) {\n          syncFlowFromDom();\n          state.flow[field] = value;\n          state.flow.clientRequestId = "";\n          reconcileDependencies(field);\n          state.openPicker = null;\n          render();\n        }\n',
    "JS_PICKER_VALUE_SYNC",
)

boot_tail = '    loadAll();\n    setInterval(loadAll, 30000);\n'
boot_extra = '''    document.addEventListener("keydown",(event)=>{ if(event.key==="Escape"&&state.openPicker){ state.openPicker=null; render(); } });\n    document.addEventListener("focusout",()=>{ setTimeout(()=>{ if(state.refreshRenderPending&&!operatorIsInteracting()) renderAfterRefresh(); },0); });\n    document.addEventListener("click",(event)=>{ if(state.openPicker && !event.target.closest("[data-picker-toggle],[data-picker-panel]")){ syncFlowFromDom(); state.openPicker=null; render(); } }, true);\n    loadAll();\n    setInterval(loadAll, 30000);\n'''
js = replace_once(js, boot_tail, boot_extra, "JS_BOOT_ERGONOMICS")
JS.write_text(js, encoding="utf-8")

# ---------------------------------------------------------------------------
# HTML semantics and cache-busting for the final browser runtime.
# ---------------------------------------------------------------------------
html = HTML.read_text(encoding="utf-8")
html = replace_once(html, '<html lang="en">', '<html lang="es-MX">', "HTML_LANG")
html = replace_once(html, "cloud_command_center.js?v=tabsel1-20260707_001948", "cloud_command_center.js?v=cloudcust-final-20260814", "HTML_JS_VERSION")
html = (
    html.replace(">Command</button>", ">Inicio</button>")
    .replace(">Customers</button>", ">Clientes</button>")
    .replace(">Entitlements</button>", ">Licencias</button>")
    .replace(">Fleet</button>", ">Dispositivos</button>")
    .replace(">Provisioning</button>", ">Alta de cliente</button>")
    .replace(">Operations</button>", ">Operación</button>")
    .replace(">Security &amp; Audit</button>", ">Bajas &amp; auditoría</button>")
)
HTML.write_text(html, encoding="utf-8")

after = {str(p): sha256(p) for p in (STORE, JS, HTML)}
improvements = [
    "direct_source_application_without_base64",
    "preflight_blob_checksum_guard",
    "current_main_ancestry_gate",
    "runtime_adapter_isolation",
    "temporary_db_override",
    "canonical_customer_catalogs",
    "retire_legacy_city_zone",
    "canonical_license_plan_validation",
    "no_seed_fact_inference",
    "validation_before_identity_generation",
    "contact_method_required",
    "manual_fact_no_implicit_first_option",
    "client_request_idempotency",
    "customer_fingerprint_dedup",
    "other_auto_submission_dedup",
    "dependent_subvertical_picker",
    "acquisition_channel_measurement",
    "country_state_city_zone_split",
    "no_duplicate_plan_field_in_customer_form",
    "exact_customer_for_device",
    "device_role_dependency",
    "device_alias_persistence",
    "exact_customer_for_license",
    "exact_deactivation_target",
    "operator_safe_background_refresh",
    "dom_state_sync_before_actions",
    "no_render_on_each_text_keystroke",
    "searchable_picker_keyboard_open",
    "escape_to_close_picker",
    "outside_click_to_close_picker",
    "dependent_value_auto_reconciliation",
    "customer_metrics_panel",
    "human_readable_validation_result",
    "double_submit_guard_plus_idempotency",
]
report = {
    "status": "SOURCE_PATCHED_PENDING_TESTS",
    "improvementCount": len(improvements),
    "improvements": improvements,
    "beforeSha256": before,
    "afterSha256": after,
}
(EVIDENCE / "SOURCE_PATCH_REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("DIRECT_SOURCE_PATCH_V2_READY")
print(f"improvements={len(improvements)}")
