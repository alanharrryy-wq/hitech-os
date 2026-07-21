#!/usr/bin/env node
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const rootArgIndex = process.argv.indexOf("--root");
const root = rootArgIndex >= 0 ? process.argv[rootArgIndex + 1] : process.cwd();
const must = (condition, message) => {
  if (!condition) {
    console.error(`[VOS 00B] FAIL ${message}`);
    process.exitCode = 1;
  } else {
    console.log(`[VOS 00B] OK ${message}`);
  }
};
const read = (relative) => readFileSync(join(root, relative), "utf8");
const has = (relative) => existsSync(join(root, relative));

const posScreenPath = "products/tablet/app/components/pos/pos-screen.tsx";
const posCssPath = "products/tablet/app/components/pos/pos.module.css";
const shellTsxPath = "products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx";
const shellCssPath = "products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css";
const layoutPath = "products/tablet/app/app/layout.tsx";
const canonicalCssPath = "products/tablet/app/app/prisma-tablet-nocturne-canonical.css";
const pkgPath = "products/tablet/app/package.json";

must(has(posScreenPath), `${posScreenPath} existe`);
must(has(posCssPath), `${posCssPath} existe`);
must(has(shellTsxPath), `${shellTsxPath} existe`);
must(has(shellCssPath), `${shellCssPath} existe`);
must(has(layoutPath), `${layoutPath} existe`);
must(has(canonicalCssPath), `${canonicalCssPath} existe`);
must(has(pkgPath), `${pkgPath} existe`);

if (process.exitCode) process.exit(process.exitCode);

const posScreen = read(posScreenPath);
const posCss = read(posCssPath);
const shellTsx = read(shellTsxPath);
const shellCss = read(shellCssPath);
const layout = read(layoutPath);
const canonicalCss = read(canonicalCssPath);
const pkg = JSON.parse(read(pkgPath));

must(layout.includes('data-prisma-canonical-shell="nocturne-reference-1607"'), "Layout declara el shell canónico vigente");
must(layout.includes('import "./prisma-tablet-nocturne-canonical.css"'), "Layout importa el owner material canónico");
must(canonicalCss.includes("--prisma-canonical-card-backdrop-count: 0"), "Contrato canónico prohíbe backdrop blur en cards");
must(canonicalCss.includes("prefers-reduced-transparency"), "Contrato canónico respeta transparencia reducida");

must(posScreen.includes('visualSurface="tablet-pos-nocturne"'), "POS recibe la superficie canónica nocturne");
must(posScreen.includes("PosTerminalSurface"), "POS conserva una superficie terminal principal");
must(posScreen.includes("PosCommandDock"), "POS conserva un solo command dock operativo");
must(posScreen.includes("showBottomDock={!checkoutBackdrop}"), "POS evita duplicar docks durante checkout");
must(posScreen.includes("resultCount={visibleProducts.length}"), "Búsqueda recibe conteo visible");
must(posScreen.includes("activeCount={activeProductCount}"), "Búsqueda recibe conteo activo");
must(posScreen.includes("state={productState}"), "Búsqueda recibe estado operativo");

must(shellTsx.includes("visualSurface?: string"), "Shell acepta visualSurface opcional");
must(shellTsx.includes('data-prisma-canonical-shell="nocturne-reference-1607"'), "Shell expone el owner canónico");
must(shellTsx.includes("data-prisma-visual-surface={resolvedVisualSurface}"), "Shell expone la superficie visual resuelta");
must(shellTsx.includes("showBottomDock?: boolean"), "Shell gobierna la visibilidad del dock");

must(/min-height:\s*(?:4[4-9]|5\d)px/.test(posCss), "CSS POS conserva objetivos táctiles de al menos 44px");
must(posCss.includes("prefers-reduced-transparency"), "CSS POS respeta transparencia reducida");
must(/min-height:\s*(?:4[4-9]|5\d)px/.test(shellCss), "CSS shell conserva objetivos táctiles de al menos 44px");
must(shellCss.includes("prefers-reduced-transparency"), "CSS shell respeta transparencia reducida");

must(Boolean(pkg.scripts?.["verify:visual-os-pos-touch-00b"]), "package.json registra verify:visual-os-pos-touch-00b");

const forbidden = ["products/pc/app/", "products/mobile/app/", "packages/shared-kernel/"];
const manifestPath = "manifests/PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B_20260503_v01.manifest.json";
if (has(manifestPath)) {
  const manifest = JSON.parse(read(manifestPath));
  const touched = manifest.files?.map((item) => item.target) ?? [];
  for (const prefix of forbidden) {
    must(!touched.some((target) => target.startsWith(prefix)), `manifest no toca ${prefix}`);
  }
}

if (process.exitCode) {
  console.error("[VOS 00B] BLOCKED contrato táctil canónico incompleto");
  process.exit(process.exitCode);
}
console.log("[VOS 00B] PASS contrato táctil reconciliado con nocturne-reference-1607");
