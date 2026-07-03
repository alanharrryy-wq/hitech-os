import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const app = path.join(root, "apps", "terminal-de-venta-system");
const read = (rel) => fs.readFileSync(path.join(app, rel), "utf8");
const failures = [];

function mustInclude(rel, token) {
  if (!read(rel).includes(token)) failures.push(`${rel} missing ${token}`);
}
function mustNotInclude(rel, token) {
  if (read(rel).includes(token)) failures.push(`${rel} still contains ${token}`);
}

mustInclude("products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css", "TABNP1_SHELL_CONTEXT_NAV_0207");
mustInclude("products/tablet/app/components/reports/contextual-export-actions.tsx", "<details");
mustInclude("products/tablet/app/components/reports/contextual-export.module.css", "TABNP1_EXPORT_SECONDARY_0207");
mustInclude("products/tablet/app/components/tablet-home/tablet-home.module.css", "TABNP1_HOME_PRODUCT_TRIM_0207");
mustNotInclude("products/tablet/app/app/offline/page.tsx", "outbox");

const cssFiles = [
  "products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css",
  "products/tablet/app/components/reports/contextual-export.module.css",
  "products/tablet/app/components/tablet-home/tablet-home.module.css"
];
for (const rel of cssFiles) {
  if (read(rel).includes("!important")) failures.push(`${rel} contains !important`);
}

if (failures.length) {
  console.error("FAIL TABNP1_TABLET_NON_POS_0207");
  for (const failure of failures) console.error("- " + failure);
  process.exit(1);
}
console.log("PASS TABNP1_TABLET_NON_POS_0207");
