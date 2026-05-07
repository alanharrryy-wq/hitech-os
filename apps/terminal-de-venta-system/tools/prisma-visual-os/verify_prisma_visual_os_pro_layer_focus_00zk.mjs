import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

function resolveTerminalRoot() {
  const scriptRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
  const candidates = [
    process.cwd(),
    path.join(process.cwd(), "apps/terminal-de-venta-system"),
    scriptRoot
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, "products/tablet/app")) && fs.existsSync(path.join(candidate, "tools/prisma-visual-os"))) {
      return candidate;
    }
  }
  return process.cwd();
}

const root = resolveTerminalRoot();
const marker = "PRISMA_VISUAL_OS_PRO_LAYER_FOCUS_00ZK";
const files = {
  client: "products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx",
  css: "products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css",
  doc: "tools/prisma-visual-os/docs/VISUAL_OS_PRO_ANTI_PENDEJOS_LAYER_FOCUS_00ZK.md",
  self: "tools/prisma-visual-os/verify_prisma_visual_os_pro_layer_focus_00zk.mjs"
};

function read(rel) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) throw new Error(`missing file: ${rel}`);
  return fs.readFileSync(abs, "utf8");
}

function must(text, needle, label) {
  if (!text.includes(needle)) throw new Error(`missing ${label}: ${needle}`);
}

const client = read(files.client);
const css = read(files.css);
const doc = read(files.doc);
read(files.self);

for (const needle of [
  marker,
  "type WorkbenchMode",
  "type ControlRelevance",
  "layerGuides",
  "layerControlCopy",
  "getControlCopy",
  "affectedVarsFor",
  "workbenchMode",
  "scopeBanner",
  "surfaceStatus",
  "controlsHeader",
  "layerFocusMap",
  "controlHiddenSimple",
  "data-relevance",
  "editorMode",
  "prismaVosFocusedLayer",
  "prismaVosEditorMode",
  "prismaVosLayerFocusPackage"
]) must(client, needle, `client marker ${needle}`);

for (const layer of ["background", "atmosphere", "shell", "surface", "content", "action", "state", "focus", "overlay"]) {
  must(client, `${layer}: {`, `layer guide ${layer}`);
}

for (const cssNeedle of [
  marker,
  ".surfaceStatus",
  ".scopeBanner",
  ".controlsHeader",
  ".control[data-relevance=\"primary\"]",
  ".control[data-relevance=\"ghost\"]",
  ".controlHiddenSimple",
  ".layerFocusMap",
  ".layerInspector li"
]) must(css, cssNeedle, `css marker ${cssNeedle}`);

for (const docNeedle of [
  marker,
  "Simple / Advanced / Expert",
  "does not change",
  "Tablet POS business logic"
]) must(doc, docNeedle, `doc marker ${docNeedle}`);

const forbiddenClientNeedles = [
  "completeSale(",
  "cartTotal =",
  "paymentSession",
  "fetch(\"/api/pos/sales/complete",
  "fetch('/api/pos/sales/complete"
];
const forbiddenHits = forbiddenClientNeedles.filter((needle) => client.includes(needle));
if (forbiddenHits.length) throw new Error(`forbidden business logic touch signals in Visual OS Pro client: ${forbiddenHits.join(", ")}`);

const summary = {
  ok: true,
  verifier: "PRISMA_VISUAL_OS_PRO_LAYER_FOCUS_00ZK",
  files,
  checks: {
    clientMarkers: true,
    cssMarkers: true,
    docMarkers: true,
    noBusinessLogicTouchSignals: true
  }
};
console.log(JSON.stringify(summary, null, 2));
