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
const pkgPath = "products/tablet/app/package.json";

must(has(posScreenPath), `${posScreenPath} existe`);
must(has(posCssPath), `${posCssPath} existe`);
must(has(shellTsxPath), `${shellTsxPath} existe`);
must(has(shellCssPath), `${shellCssPath} existe`);
must(has(pkgPath), `${pkgPath} existe`);

if (process.exitCode) process.exit(process.exitCode);

const posScreen = read(posScreenPath);
const posCss = read(posCssPath);
const shellTsx = read(shellTsxPath);
const shellCss = read(shellCssPath);
const pkg = JSON.parse(read(pkgPath));

must(posScreen.includes("PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B"), "PosScreen declara hook 00B");
must(posScreen.includes('visualSurface="tablet-pos"'), "Shell recibe visualSurface tablet-pos");
must(posScreen.includes('visualPreset="pos-touch-00b"'), "Shell recibe visualPreset pos-touch-00b");
must(posScreen.includes('data-prisma-vos="00B"'), "Workspace declara data-prisma-vos 00B");
must(posScreen.includes('data-prisma-vsurface="tablet-pos"'), "Workspace declara superficie tablet-pos");
must(posScreen.includes('data-prisma-vpreset="POS_TOUCH"'), "Workspace declara preset POS_TOUCH");
must(posScreen.includes("resultCount={visibleProducts.length}"), "Search recibe conteo visible");
must(posScreen.includes("activeCount={activeProductCount}"), "Search recibe conteo activo");
must(posScreen.includes("state={productState}"), "Search recibe estado operativo");

must(shellTsx.includes("visualSurface?: string"), "Shell acepta visualSurface opcional");
must(shellTsx.includes("visualPreset?: string"), "Shell acepta visualPreset opcional");
must(shellTsx.includes("data-prisma-visual-surface={visualSurface}"), "Shell expone data-prisma-visual-surface");
must(shellTsx.includes("data-prisma-visual-preset={visualPreset}"), "Shell expone data-prisma-visual-preset");

must(posCss.includes("PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B"), "CSS POS contiene capa 00B");
must(posCss.includes('.posWorkspace[data-prisma-vos="00B"]'), "CSS POS está acotado a data-prisma-vos");
must(posCss.includes("--vos-pos-hit-target"), "CSS POS declara hit target táctil");
must(posCss.includes(".catalogInsight"), "CSS POS cubre catalogInsight");
must(posCss.includes("prefers-reduced-motion"), "CSS POS respeta reduced motion");
must(shellCss.includes("PRISMA_VISUAL_OS_TABLET_POS_SHELL_BINDING_00B"), "CSS shell contiene binding 00B");
must(shellCss.includes('.shell[data-prisma-visual-surface="tablet-pos"]'), "CSS shell está acotado a tablet-pos");

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
  console.error("[VOS 00B] BLOCKED Visual OS POS Touch binding incompleto");
  process.exit(process.exitCode);
}
console.log("[VOS 00B] PASS Visual OS POS Touch binding listo");
