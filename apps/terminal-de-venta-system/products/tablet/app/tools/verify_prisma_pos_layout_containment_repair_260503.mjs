#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const files = {
  pos: path.join(root, "components", "pos", "pos.module.css"),
  shell: path.join(root, "components", "tablet-shell", "prisma-tablet-shell.module.css"),
};
const checks = [
  [files.pos, "PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN"],
  [files.pos, "grid-template-columns: minmax(0, 1fr) clamp(320px, 32vw, 430px)"],
  [files.pos, ":global([data-prisma-component=\"CartPanel\"])"],
  [files.pos, "@media (max-width: 1160px)"],
  [files.shell, "PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN"],
  [files.shell, "grid-template-columns: clamp(88px, 13vw, 220px) minmax(0, 1fr)"],
  [files.shell, "@media (max-width: 760px)"],
  [files.shell, "overflow-wrap: normal"],
];
const failures = [];
for (const [file, needle] of checks) {
  if (!fs.existsSync(file)) failures.push(`missing ${file}`);
  else if (!fs.readFileSync(file, "utf8").includes(needle)) failures.push(`missing ${needle} in ${file}`);
}
for (const file of Object.values(files)) {
  if (fs.existsSync(file) && fs.readFileSync(file, "utf8").includes("PRISMA_POS_VISUAL_DOM_ALIGNMENT_LOCK_260503")) {
    failures.push(`alignment lock marker still present in ${file}`);
  }
}
if (failures.length) {
  console.error("[PRISMA POS LAYOUT REPAIR FAIL]");
  for (const f of failures) console.error("- " + f);
  process.exit(1);
}
console.log("OK PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503 verified shell/pos containment CSS");
