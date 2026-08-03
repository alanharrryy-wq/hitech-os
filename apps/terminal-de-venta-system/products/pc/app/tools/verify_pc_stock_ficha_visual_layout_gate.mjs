import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, "..");
const repoRoot = path.resolve(appRoot, "../../../../..");
const outDir = path.resolve(process.argv[2] || path.join(process.cwd(), "pc-stock-ficha-layout-evidence"));
fs.mkdirSync(outDir, { recursive: true });
const require = createRequire(import.meta.url);
function uniqExisting(values) {
  const out = []; const seen = new Set();
  for (const value of values) {
    if (!value) continue;
    const resolved = path.resolve(String(value));
    const key = resolved.toLowerCase();
    if (!seen.has(key) && fs.existsSync(resolved)) { seen.add(key); out.push(resolved); }
  }
  return out;
}
function ancestors(start) {
  const out = []; let current = path.resolve(start);
  for (;;) { out.push(current); const parent = path.dirname(current); if (parent === current) break; current = parent; }
  return out;
}
function listPnpmCandidates(root) {
  const pnpm = path.join(root, "node_modules", ".pnpm");
  if (!fs.existsSync(pnpm)) return [];
  let names = []; try { names = fs.readdirSync(pnpm); } catch { return []; }
  const out = [];
  for (const name of names) {
    if (name.startsWith("@playwright+test@")) out.push({ moduleName: "@playwright/test", file: path.join(pnpm, name, "node_modules", "@playwright", "test", "index.js") });
    if (name.startsWith("playwright@")) out.push({ moduleName: "playwright", file: path.join(pnpm, name, "node_modules", "playwright", "index.js") });
  }
  return out;
}
function candidateRoots() {
  const envRoots = String(process.env.PRISMA_POINT_RESOLVE_ROOTS || "").split(";").filter(Boolean);
  return uniqExisting([
    ...envRoots,
    process.env.PRISMA_REPO_ROOT,
    process.env.PRISMA_APP_ROOT,
    process.env.PRISMA_PC_APP_ROOT,
    process.env.PRISMA_TOOL_ROOT,
    repoRoot,
    appRoot,
    path.join(repoRoot, "apps", "terminal-de-venta-system"),
    path.join(repoRoot, "tools", "Plawright Mamastrophic"),
    process.cwd(),
    ...ancestors(here),
    ...ancestors(process.cwd())
  ]);
}
function loadCandidate(file, moduleName, root, method) {
  const req = createRequire(fs.existsSync(path.join(root, "package.json")) ? path.join(root, "package.json") : file);
  const loaded = method === "direct-file" ? req(file) : req(moduleName);
  return { loaded, moduleName, root, resolved: method === "direct-file" ? file : req.resolve(moduleName), method };
}
function resolvePlaywrightDetailed() {
  const attempts = [];
  const explicit = process.env.PRISMA_PLAYWRIGHT_MODULE;
  if (explicit) {
    try {
      const file = path.resolve(explicit);
      const hit = loadCandidate(file, "explicit", path.dirname(file), "direct-file");
      if (hit.loaded?.chromium) return { ok: true, playwright: hit.loaded, moduleName: "explicit", root: hit.root, resolved: file, method: hit.method, attempts };
      attempts.push({ moduleName: "explicit", resolved: file, ok: false, error: "chromium export missing" });
    } catch (error) { attempts.push({ moduleName: "explicit", resolved: explicit, ok: false, error: String(error?.message || error) }); }
  }
  const roots = candidateRoots();
  for (const root of roots) {
    for (const moduleName of ["@playwright/test", "playwright"]) {
      try {
        const hit = loadCandidate(path.join(root, "noop.js"), moduleName, root, "createRequire");
        if (hit.loaded?.chromium) return { ok: true, playwright: hit.loaded, moduleName, root, resolved: hit.resolved, method: hit.method, attempts };
        attempts.push({ root, moduleName, ok: false, error: "chromium export missing", resolved: hit.resolved });
      } catch (error) { attempts.push({ root, moduleName, ok: false, error: String(error?.message || error), method: "createRequire" }); }
    }
    const direct = [
      { moduleName: "@playwright/test", file: path.join(root, "node_modules", "@playwright", "test", "index.js") },
      { moduleName: "playwright", file: path.join(root, "node_modules", "playwright", "index.js") },
      ...listPnpmCandidates(root)
    ];
    for (const candidate of direct) {
      try {
        if (!fs.existsSync(candidate.file)) continue;
        const hit = loadCandidate(candidate.file, candidate.moduleName, root, "direct-file");
        if (hit.loaded?.chromium) return { ok: true, playwright: hit.loaded, moduleName: candidate.moduleName, root, resolved: candidate.file, method: hit.method, attempts };
        attempts.push({ root, moduleName: candidate.moduleName, ok: false, error: "chromium export missing", resolved: candidate.file });
      } catch (error) { attempts.push({ root, moduleName: candidate.moduleName, ok: false, error: String(error?.message || error), resolved: candidate.file, method: "direct-file" }); }
    }
  }
  return { ok: false, roots, attempts };
}
const resolution = resolvePlaywrightDetailed();
fs.writeFileSync(path.join(outDir, "PLAYWRIGHT_RESOLUTION.json"), JSON.stringify({ ...resolution, playwright: undefined }, null, 2) + "\n");
if (process.argv.includes("--selftest-resolve")) {
  if (!resolution.ok) { console.error("PLAYWRIGHT_RESOLUTION_FAIL"); process.exit(2); }
  console.log(`PLAYWRIGHT_RESOLVED module=${resolution.moduleName} method=${resolution.method} resolved=${resolution.resolved}`);
  process.exit(0);
}
if (!resolution.ok || !resolution.playwright?.chromium) throw new Error("Playwright/Chromium no está resoluble desde el runtime certificado. Revisa PLAYWRIGHT_RESOLUTION.json.");
const playwright = resolution.playwright;
const edgeCandidates = [
  process.env["PROGRAMFILES(X86)"] && path.join(process.env["PROGRAMFILES(X86)"], "Microsoft", "Edge", "Application", "msedge.exe"),
  process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, "Microsoft", "Edge", "Application", "msedge.exe"),
  process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, "Microsoft", "Edge", "Application", "msedge.exe")
].filter(Boolean);
const executablePath = edgeCandidates.find(p => fs.existsSync(p));
const launchOptions = { headless: true };
if (executablePath) launchOptions.executablePath = executablePath;
const browser = await playwright.chromium.launch(launchOptions);
const cssPath = path.join(repoRoot, "apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css");
const allCss = fs.readFileSync(cssPath, "utf8");
const marker = "/* PRISMA_PC_STOCK_FICHA_TABLET_LICENSES_PILOT_V1_BEGIN */";
const beforeCss = allCss.includes(marker) ? allCss.slice(0, allCss.indexOf(marker)) : allCss;
const base = `
*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#15263a}body{padding:24px;background:radial-gradient(circle at 15% 10%,#fff,transparent 30%),linear-gradient(135deg,#e9eef3,#d9e3eb)}main{max-width:1180px;margin:0 auto}.productFicha{width:min(100%,430px);padding:20px}.fichaHeader{display:flex;justify-content:space-between;gap:14px;align-items:flex-start;margin-bottom:14px}.fichaHeader h2{margin:4px 0 0;letter-spacing:-.035em}.kicker{text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;font-weight:850}.fichaStack{display:grid;gap:10px}.fichaRow{display:flex;justify-content:space-between;gap:14px;padding:12px}.fichaRow strong{text-align:right}.actionRail{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.actionRail a,.actionRail span{display:inline-flex;align-items:center;min-height:34px;padding:7px 11px;font-size:.82rem}.status{border-radius:999px;padding:6px 10px;background:#d9f2e4;color:#16472e;font-weight:800}.empty{padding:20px 0;color:#4b6177}.stage{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,430px);gap:18px;align-items:start}.ledger{min-height:380px;border:1px solid rgba(90,110,130,.16);border-radius:22px;background:rgba(255,255,255,.42);padding:20px}.ledgerLine{height:40px;border-bottom:1px solid rgba(80,100,120,.12)}@media(max-width:720px){body{padding:12px}.stage{grid-template-columns:1fr}.productFicha{width:100%}}
`;
const scenarios = [
  {id:"normal", title:"Café molido Sierra", rows:[["SKU","CAF-600"],["Ubicación","Almacén principal"],["Existencia","128"],["Reservado","18"],["Disponible","110"],["Cobertura","14 días"]], actions:["Crear conteo","Preparar ajuste","Mandar a reabasto","Auditoría"]},
  {id:"long-copy", title:"Producto de nombre extraordinariamente largo para probar lectura operativa sin colisiones", rows:[["SKU","PRODUCTO-ULTRA-LARGO-2026-000001"],["Ubicación","Almacén principal, pasillo siete, anaquel superior"],["Existencia","12,889"],["Reservado","1,204"],["Disponible","11,685"],["Cobertura","Ciento veintiocho días estimados"]], actions:["Crear conteo físico","Preparar ajuste auditable","Mandar a reabasto prioritario","Abrir auditoría completa"]},
  {id:"empty", title:"Sin corte seleccionado", rows:[], actions:[]},
  {id:"critical", title:"Refresco 600 ml", rows:[["SKU","REF-600"],["Ubicación","Mostrador"],["Existencia","0"],["Reservado","0"],["Disponible","0"],["Cobertura","Sin cobertura"]], actions:["Crear conteo","Preparar ajuste","Mandar a reabasto","Auditoría"]},
  {id:"many-actions", title:"Aceite vegetal 1 L", rows:[["SKU","ACE-1L"],["Ubicación","Bodega"],["Existencia","48"],["Reservado","4"],["Disponible","44"],["Cobertura","9 días"]], actions:["Crear conteo","Preparar ajuste","Mandar a reabasto","Auditoría","Historial","Proveedor","Exportar"]},
  {id:"keyboard", title:"Leche entera 1 L", rows:[["SKU","LEC-1L"],["Ubicación","Refrigerador"],["Existencia","36"],["Reservado","5"],["Disponible","31"],["Cobertura","3 días"]], actions:["Crear conteo","Preparar ajuste","Mandar a reabasto","Auditoría"], focus:true},
  {id:"reduced-motion", title:"Arroz 1 kg", rows:[["SKU","ARR-1K"],["Ubicación","Pasillo 3"],["Existencia","82"],["Reservado","7"],["Disponible","75"],["Cobertura","21 días"]], actions:["Crear conteo","Preparar ajuste","Mandar a reabasto","Auditoría"], reduced:true}
];
const viewports = [{width:1365,height:768},{width:1024,height:768},{width:900,height:768},{width:640,height:900}];
function markup(s){
 const rows=s.rows.map(([a,b])=>`<div class="fichaRow"><span>${a}</span><strong>${b}</strong></div>`).join("");
 const actions=s.actions.map((a,i)=>`<a href="#" ${i===0&&s.focus?'autofocus':''}>${a}</a>`).join("");
 const empty=s.rows.length?"":`<div class="empty">Cuando haya cortes de inventario, esta ficha mostrará ubicación, disponible, reservado, cobertura y acciones contextuales.</div>`;
 return `<main><div class="stage"><section class="ledger">${Array.from({length:8},()=>'<div class="ledgerLine"></div>').join('')}</section><section class="productFicha" data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1" data-pcinv-product-ficha="${s.rows.length?'stock':'stock-empty'}"><div class="fichaHeader"><div><span class="kicker">acción rápida</span><h2>${s.title}</h2></div><span class="status">${s.id==='critical'?'crítico':'ok'}</span></div><div class="fichaStack">${rows}</div>${empty}<div class="actionRail">${actions}<span aria-disabled="true">Ajuste directo bloqueado</span></div></section></div></main>`;
}
function doc(css,s){return `<!doctype html><html><head><meta charset="utf-8"><style>${base}\n${css}</style></head><body>${markup(s)}</body></html>`}
const records=[];
for(const viewport of viewports){
 for(const scenario of scenarios){
  const context=await browser.newContext({viewport, reducedMotion:scenario.reduced?"reduce":"no-preference"});
  const page=await context.newPage();
  await page.setContent(doc(allCss,scenario),{waitUntil:"load"});
  if(scenario.focus) await page.locator(".actionRail a").first().focus();
  const measurement=await page.evaluate(()=>{
   const card=document.querySelector(".productFicha"); const r=card.getBoundingClientRect(); const doc=document.documentElement;
   const actions=[...document.querySelectorAll(".actionRail a,.actionRail span")].map(x=>{const q=x.getBoundingClientRect();return{l:q.left,r:q.right,t:q.top,b:q.bottom}});
   let collisions=0; for(let i=0;i<actions.length;i++)for(let j=i+1;j<actions.length;j++){const a=actions[i],b=actions[j];if(a.l<b.r&&a.r>b.l&&a.t<b.b&&a.b>b.t)collisions++;}
   return {horizontalOverflow:Math.max(0,doc.scrollWidth-doc.clientWidth),cardRightOverflow:Math.max(0,r.right-doc.clientWidth),cardLeftOverflow:Math.max(0,-r.left),cardScrollOverflow:Math.max(0,card.scrollWidth-card.clientWidth),collisions};
  });
  const pass=Object.values(measurement).every(v=>v<=1);
  records.push({scenario:scenario.id,viewport,status:pass?"PASS":"FAIL",measurement});
  await context.close();
 }
}
for(const mode of ["before","after"]){
 const context=await browser.newContext({viewport:{width:1365,height:768}}); const page=await context.newPage();
 await page.setContent(doc(mode==="before"?beforeCss:allCss,scenarios[0]),{waitUntil:"load"});
 await page.screenshot({path:path.join(outDir,`${mode.toUpperCase()}_1365x768.png`),fullPage:true}); await context.close();
}
for(const mode of ["before","after"]){
 const context=await browser.newContext({viewport:{width:640,height:900}}); const page=await context.newPage();
 await page.setContent(doc(mode==="before"?beforeCss:allCss,scenarios[1]),{waitUntil:"load"});
 await page.screenshot({path:path.join(outDir,`${mode.toUpperCase()}_640x900.png`),fullPage:true}); await context.close();
}
await browser.close();
const failures=records.filter(x=>x.status!=="PASS");
const report={schema:"prisma.pc-stock-ficha.visual-layout-gate.v1",taskId:"PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1",status:failures.length?"FAIL":"PASS_COLLISION_OVERFLOW_28_OF_28",viewports,scenarios:scenarios.map(x=>x.id),recordCount:records.length,passCount:records.length-failures.length,failCount:failures.length,records};
fs.writeFileSync(path.join(outDir,"PC_STOCK_FICHA_VISUAL_LAYOUT_GATE.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({status:report.status,passCount:report.passCount,recordCount:report.recordCount},null,2));
if(failures.length)process.exit(1);
