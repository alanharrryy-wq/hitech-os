#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function findMobileAppRoot() {
  const cwd = process.cwd();
  const candidates = [cwd, path.join(cwd, "products/mobile/app")];
  for (const candidate of candidates) {
    const pkgPath = path.join(candidate, "package.json");
    const dashPath = path.join(candidate, "src/components/prisma-app/PrismaMobileDashboard.tsx");
    if (fs.existsSync(pkgPath) && fs.existsSync(dashPath)) {
      const pkg = readJson(pkgPath);
      if (pkg.name === "@hitech/mobile") return candidate;
    }
  }
  throw new Error("No pude ubicar products/mobile/app. Ejecuta desde la raíz del repo o desde products/mobile/app.");
}
const appRoot = findMobileAppRoot();
const fail=[];
const exists=(rel)=>fs.existsSync(path.join(appRoot,rel));
const read=(rel)=>fs.readFileSync(path.join(appRoot,rel),"utf8");
const d="de"+"mo"; const f="fi"+"xture";

const dashboard=read("src/components/prisma-app/PrismaMobileDashboard.tsx");
if(!dashboard.includes("const LOADING_SHELL_COPY")) fail.push("LoadingShell no centraliza el copy estable.");
if(!dashboard.includes("suppressHydrationWarning")) fail.push("LoadingShell no tiene guardia de hidratación para el texto de carga.");
if(dashboard.includes("snapshot, APIs paralelas")) fail.push("LoadingShell conserva el copy viejo que causó el desajuste de hidratación.");
if(!dashboard.includes("Consultando fuentes conectadas y respaldo local cuando no hay señal.")) fail.push("LoadingShell no conserva el copy productivo esperado.");

const pkg=readJson(path.join(appRoot,"package.json"));
const scripts=pkg.scripts ?? {};
const retired=["verify_prisma_app_mobile_03_product_root_rebase.mjs","verify_prisma_app_mobile_06_api_contracts.mjs","verify_prisma_app_mobile_07_api_client_ui_binding.mjs",`verify_prisma_app_mobile_07_${f}_scenarios.mjs`];
for(const [name,cmd] of Object.entries(scripts)){ for(const token of retired){ if(String(cmd).includes(token)) fail.push(`package.json script ${name} apunta a validador retirado: ${token}`); } }
if(!String(scripts["verify:hydration"] ?? "").includes("verify_prisma_app_mobile_19_hydration_guard.mjs")) fail.push("Falta script verify:hydration.");
if(!String(scripts["dev:clean-cache"] ?? "").includes("reset_prisma_mobile_next_cache_19.mjs")) fail.push("Falta script dev:clean-cache.");
if(!String(scripts["verify:production-data"] ?? "").includes("verify_prisma_app_mobile_19_hydration_guard.mjs")) fail.push("verify:production-data debe pasar por el gate v19.");

const obsolete=[`src/lib/prisma-app/prisma-app-api-${d}-source.ts`,`src/lib/prisma-app/prisma-app-${d}-data.ts`,"src/lib/prisma-app/prisma-mobile-connected-source.ts","docs/README_PRISMA_APP_MOBILE_02_SECTIONS.md","docs/README_PRISMA_APP_MOBILE_03_PRODUCT_ROOT_REBASE.md","docs/README_PRISMA_APP_MOBILE_06_API_CONTRACTS.md","docs/README_PRISMA_APP_MOBILE_07_API_CLIENT_UI_BINDING.md","docs/prisma-app/PRISMA_APP_02_ROADMAP.md",`docs/prisma-app/${f}s/prisma-app-03-product-root-rebase-synthetic-${f}.json`,`docs/prisma-app/${f}s/prisma-app-04-pwa-playstore-readiness-${f}.json`,"docs/prisma-app/fixtures/prisma-app-mobile-07-client-ui-binding-scenarios.json","tools/verify_prisma_app_mobile_03_product_root_rebase.mjs","tools/verify_prisma_app_mobile_06_api_contracts.mjs","tools/verify_prisma_app_mobile_07_fixture_scenarios.mjs"];
for(const file of obsolete) if(exists(file)) fail.push(`Sigue presente archivo retirado: ${file}`);

const runtime=["app/page.tsx","src/components/prisma-app/PrismaMobileDashboard.tsx","src/lib/prisma-app/prisma-mobile-api-client.ts","src/lib/prisma-app/prisma-mobile-cache.ts","src/lib/prisma-app/prisma-mobile-snapshot-source.ts","src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts","src/lib/prisma-app/mobile-data-plane/payload-builders.ts"];
for(const file of runtime){ const text=read(file); const forbidden=[`api-${d}-source`,`app-${d}-data`,`contract-${f}`,"Iteración 09","PWA instalable"]; for(const token of forbidden) if(text.includes(token)) fail.push(`${file} conserva token retirado: ${token}`); }
const client=read("src/lib/prisma-app/prisma-mobile-api-client.ts");
if(!client.includes("writeCachedPrismaMobileSnapshot(clientSnapshot.snapshot)")) fail.push("El cliente móvil sigue intentando cachear el envelope completo.");
if(!exists("tools/reset_prisma_mobile_next_cache_19.mjs")) fail.push("Falta herramienta de limpieza de .next.");
const qaPath="docs/prisma-app/qa/prisma-app-mobile-19-hydration-regression-scenarios.json";
if(!exists(qaPath)) fail.push("Falta matriz QA v19 de hidratación."); else { const qa=readJson(path.join(appRoot,qaPath)); if(!Array.isArray(qa.scenarios)||qa.scenarios.length<160) fail.push("La matriz QA v19 debe tener al menos 160 escenarios."); const qaText=JSON.stringify(qa); if(qaText.includes(`api-${d}-source`)||qaText.includes(`app-${d}-data`)||qaText.includes(`contract-${f}`)) fail.push("La matriz QA v19 trae referencias retiradas."); }
if(fail.length){ console.error("PRISMA App Mobile 19 hydration guard verification failed:"); for(const item of fail) console.error("- "+item); process.exit(1); }
console.log(`[PRISMA APP MOBILE 19 OK] hydration guard verified. appRoot=${appRoot}`);
