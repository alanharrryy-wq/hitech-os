import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const mustContain = [
  ["products/pc/app/src/server/services/pc-command-center.service.ts", "salesControl: salesControlView"],
  ["products/pc/app/src/server/services/pc-command-center.service.ts", "buildSalesControlView"],
  ["products/pc/app/components/control/pc-command-center-page.tsx", "SalesControlBranchView"],
  ["products/pc/app/components/control/sales-control-branch-view.tsx", "Agregar sucursal nueva"],
  ["products/pc/app/components/control/sales-control-branch-view.tsx", "Ventas por sucursal"],
  ["products/pc/app/components/control/sales-control-branch-view.tsx", "TicketDetail"],
  ["products/pc/app/components/control/sales-control-branch-view.module.css", ".addBranchDock"],
  ["products/pc/app/components/layout/app-shell.tsx", "hideRouteIntentStrip"]
];

const errors = [];
for (const [rel, needle] of mustContain) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) {
    errors.push(`missing ${rel}`);
    continue;
  }
  const text = fs.readFileSync(abs, "utf8");
  if (!text.includes(needle)) errors.push(`${rel} missing ${needle}`);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log("[OK] PC sales-control branch layout verified");
