import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "products/shared-ui/prisma/visual-os/prisma-visual-os.controls.json",
  "products/shared-ui/prisma/visual-os/prisma-visual-os.presets.json",
  "products/shared-ui/prisma/visual-os/prisma-visual-os.recipes.json",
  "products/shared-ui/prisma/visual-os/prisma-visual-os.layers.json",
  "products/shared-ui/prisma/visual-os/prisma-visual-os.runtime.schema.json",
  "config/prisma-visual-os/prisma-visual-controls.active.json",
  "styles/prisma-visual-os/prisma-visual-layers.css",
  "styles/prisma-visual-os/prisma-visual-controls.generated.css",
  "docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md"
];
const missing = required.filter((rel) => !fs.existsSync(path.join(root, rel)));
if (missing.length) {
  for (const rel of missing) console.error(`ERROR missing ${rel}`);
  process.exit(1);
}
const layers = JSON.parse(fs.readFileSync(path.join(root, "products/shared-ui/prisma/visual-os/prisma-visual-os.layers.json"), "utf8"));
const expectedLayers = ["background", "atmosphere", "shell", "surface", "content", "action", "state", "focus", "overlay", "debug"];
const found = new Set((layers.layers || []).map((x) => x.id));
for (const id of expectedLayers) if (!found.has(id)) { console.error(`ERROR layer missing ${id}`); process.exit(1); }
const active = JSON.parse(fs.readFileSync(path.join(root, "config/prisma-visual-os/prisma-visual-controls.active.json"), "utf8"));
if (active.safety?.allowManualCssDrift !== false) { console.error("ERROR allowManualCssDrift debe ser false"); process.exit(1); }
if (active.controls?.touch < 80) { console.error("ERROR touch control insuficiente para Tablet POS"); process.exit(1); }
const css = fs.readFileSync(path.join(root, "styles/prisma-visual-os/prisma-visual-controls.generated.css"), "utf8");
for (const token of ["--prisma-vos-layer-action-strength", "--prisma-vos-runtime-action-shadow", "--prisma-vos-min-touch-target-runtime"]) {
  if (!css.includes(token)) { console.error(`ERROR generated css sin token ${token}`); process.exit(1); }
}
console.log("OK PRISMA Visual OS core 00D/00E verified");
