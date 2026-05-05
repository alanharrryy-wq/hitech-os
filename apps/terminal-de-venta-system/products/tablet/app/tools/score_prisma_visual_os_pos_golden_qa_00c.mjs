#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const out = { root: process.cwd(), json: false };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--root") out.root = argv[++i];
    if (arg === "--json") out.json = true;
  }
  return out;
}
function exists(file) { return fs.existsSync(file); }
function text(file) { return fs.readFileSync(file, "utf8"); }
function clamp(n) { return Math.max(0, Math.min(100, n)); }

const args = parseArgs(process.argv);
const root = path.resolve(args.root);
const tabletRoot = path.join(root, "products", "tablet", "app");
const checks = [];
function add(id, weight, pass, detail) { checks.push({ id, weight, pass: Boolean(pass), detail }); }

const controlDoc = path.join(root, "docs/design/PRISMA_VISUAL_OS_CONTROL_PLANE_00A.md");
const posDoc = path.join(root, "docs/design/PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B.md");
const goldenDoc = path.join(root, "docs/design/PRISMA_VISUAL_OS_POS_GOLDEN_QA_00C.md");
const goldenPath = path.join(root, "products/shared-ui/prisma/visual-os/prisma-visual-os.golden-screens.00c.json");
const posCssPath = path.join(tabletRoot, "components/pos/pos.module.css");
const posScreenPath = path.join(tabletRoot, "components/pos/pos-screen.tsx");
const capturePath = path.join(tabletRoot, "tools/capture_prisma_visual_os_pos_golden_qa_00c.mjs");
const pkgPath = path.join(tabletRoot, "package.json");

add("control-plane-00a", 12, exists(controlDoc), "Control Plane 00A presente");
add("pos-binding-00b", 12, exists(posDoc), "POS Touch Binding 00B presente");
add("golden-doc-00c", 8, exists(goldenDoc), "Documento 00C presente");

let golden = null;
try { golden = JSON.parse(text(goldenPath)); } catch {}
add("golden-schema", 12, golden?.schema === "prisma.visual-os.golden-screens.00c", "Schema golden 00C válido");
add("golden-coverage", 12, Array.isArray(golden?.screens) && golden.screens.length >= 3, "Cobertura mínima de tres pantallas");
add("golden-score-axes", 8, Array.isArray(golden?.scoreAxes) && golden.scoreAxes.length === 6, "Seis ejes de score PRISMA");

let posCss = exists(posCssPath) ? text(posCssPath) : "";
let posScreen = exists(posScreenPath) ? text(posScreenPath) : "";
add("visual-scope", 10, posScreen.includes("data-prisma-vsurface") || posScreen.includes("visualSurface"), "POS expone superficie visual");
add("pos-touch-preset", 10, posScreen.includes("POS_TOUCH") || posCss.includes("POS Touch"), "Preset POS_TOUCH detectable");
add("css-prisma-depth", 8, posCss.includes("backdrop-filter") || posCss.includes("box-shadow"), "Profundidad visual presente");
add("css-operability", 8, posCss.includes("min-height") || posCss.includes("touch-action") || posCss.includes("focus-visible"), "Señales operativas/touch presentes");

let capture = exists(capturePath) ? text(capturePath) : "";
add("capture-harness", 10, capture.includes("playwright") && capture.includes("screenshot") && capture.includes("manifest"), "Arnés de captura con evidencia");

let pkg = null;
try { pkg = JSON.parse(text(pkgPath)); } catch {}
add("package-scripts", 8, Boolean(pkg?.scripts?.["visual-os:pos-golden-00c"]), "Scripts npm/pnpm registrados");

const totalWeight = checks.reduce((acc, c) => acc + c.weight, 0);
const earned = checks.reduce((acc, c) => acc + (c.pass ? c.weight : 0), 0);
const score = clamp(Math.round((earned / totalWeight) * 100));
const pass = score >= 90 && checks.every((c) => c.weight < 12 || c.pass);
const report = { package: "PRISMA_VISUAL_OS_POS_GOLDEN_QA_00C_20260503_v01", score, pass, checks };

if (args.json) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log(`[VOS 00C SCORE] ${score} pass=${pass}`);
  for (const c of checks) console.log(`${c.pass ? "OK" : "FAIL"} ${c.id}: ${c.detail}`);
}
if (!pass) process.exit(1);
