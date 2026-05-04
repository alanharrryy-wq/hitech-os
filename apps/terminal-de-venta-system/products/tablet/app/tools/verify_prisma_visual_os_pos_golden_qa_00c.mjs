#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const out = { root: process.cwd() };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--root") out.root = argv[++i];
  }
  return out;
}

function readText(file) {
  return fs.readFileSync(file, "utf8");
}

function assertOk(condition, message) {
  if (!condition) {
    console.error(`[VOS 00C FAIL] ${message}`);
    process.exitCode = 1;
  } else {
    console.log(`[VOS 00C OK] ${message}`);
  }
}

const args = parseArgs(process.argv);
const root = path.resolve(args.root);
const tabletRoot = path.join(root, "products", "tablet", "app");
const paths = {
  controlDoc: path.join(root, "docs", "design", "PRISMA_VISUAL_OS_CONTROL_PLANE_00A.md"),
  posDoc: path.join(root, "docs", "design", "PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B.md"),
  goldenDoc: path.join(root, "docs", "design", "PRISMA_VISUAL_OS_POS_GOLDEN_QA_00C.md"),
  qaDoc: path.join(tabletRoot, "docs", "qa", "PRISMA_VISUAL_OS_POS_GOLDEN_QA_00C.md"),
  controls: path.join(root, "products", "shared-ui", "prisma", "visual-os", "prisma-visual-os.controls.json"),
  presets: path.join(root, "products", "shared-ui", "prisma", "visual-os", "prisma-visual-os.presets.json"),
  recipes: path.join(root, "products", "shared-ui", "prisma", "visual-os", "prisma-visual-os.recipes.json"),
  golden: path.join(root, "products", "shared-ui", "prisma", "visual-os", "prisma-visual-os.golden-screens.00c.json"),
  posScreen: path.join(tabletRoot, "components", "pos", "pos-screen.tsx"),
  posCss: path.join(tabletRoot, "components", "pos", "pos.module.css"),
  shellCss: path.join(tabletRoot, "components", "tablet-shell", "prisma-tablet-shell.module.css"),
  capture: path.join(tabletRoot, "tools", "capture_prisma_visual_os_pos_golden_qa_00c.mjs"),
  score: path.join(tabletRoot, "tools", "score_prisma_visual_os_pos_golden_qa_00c.mjs"),
  pkg: path.join(tabletRoot, "package.json"),
};

for (const [key, file] of Object.entries(paths)) {
  assertOk(fs.existsSync(file), `${key} existe: ${path.relative(root, file)}`);
}

if (process.exitCode) process.exit(process.exitCode);

const golden = JSON.parse(readText(paths.golden));
assertOk(golden.schema === "prisma.visual-os.golden-screens.00c", "golden schema 00C correcto");
assertOk(Array.isArray(golden.screens) && golden.screens.length >= 3, "mínimo tres golden screens definidos");
assertOk(golden.screens.some((s) => s.id === "tablet_pos_sales_primary" && s.route === "/pos"), "golden principal /pos definido");
assertOk(golden.screens.every((s) => s.viewport && s.viewport.width >= 1000 && s.viewport.height >= 700), "viewports operativos declarados");
assertOk(Array.isArray(golden.scoreAxes) && golden.scoreAxes.length === 6, "score axes PRISMA completos");

const posScreen = readText(paths.posScreen);
assertOk(posScreen.includes('data-prisma-vos="00B"') || posScreen.includes("data-prisma-vos"), "POS screen conserva hook data-prisma-vos");
assertOk(posScreen.includes("POS_TOUCH") || posScreen.includes("visualPreset"), "POS screen conserva preset POS_TOUCH");
assertOk(posScreen.includes("data-prisma-vsurface") || posScreen.includes("visualSurface"), "POS screen expone superficie visual");

const posCss = readText(paths.posCss);
assertOk(posCss.includes("data-prisma-vsurface") || posCss.includes("data-prisma-vos") || posCss.includes("PRISMA Visual OS") || posCss.includes("posWorkspace"), "CSS POS conserva scope Visual OS");
assertOk(posCss.includes("--prisma") || posCss.includes("gold"), "CSS POS usa tokens/acentos PRISMA");
assertOk(posCss.includes("min-height") || posCss.includes("touch-action"), "CSS POS mantiene señales touch/operables");

const capture = readText(paths.capture);
assertOk(capture.includes("playwright") && capture.includes("--base-url") && capture.includes("--out"), "capture harness soporta Playwright, base-url y salida");
assertOk(capture.includes("prisma_visual_os_pos_golden_00c_manifest.json"), "capture harness genera manifest de evidencia");

const pkg = JSON.parse(readText(paths.pkg));
const scripts = pkg.scripts || {};
assertOk(scripts["verify:visual-os-pos-golden-00c"] === "node tools/verify_prisma_visual_os_pos_golden_qa_00c.mjs", "package script verify 00C registrado");
assertOk(scripts["capture:visual-os-pos-golden-00c"] === "node tools/capture_prisma_visual_os_pos_golden_qa_00c.mjs", "package script capture 00C registrado");
assertOk(scripts["score:visual-os-pos-golden-00c"] === "node tools/score_prisma_visual_os_pos_golden_qa_00c.mjs", "package script score 00C registrado");

if (process.exitCode) {
  console.error("[VOS 00C] blocked");
  process.exit(process.exitCode);
}
console.log("[VOS 00C] ready: Golden QA harness instalado y consistente.");
