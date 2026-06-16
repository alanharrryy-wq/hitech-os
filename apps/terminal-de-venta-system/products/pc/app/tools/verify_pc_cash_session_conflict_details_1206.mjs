import fs from "node:fs";
import path from "node:path";

const root = process.argv.includes("--root")
  ? process.argv[process.argv.indexOf("--root") + 1]
  : process.cwd();

const checks = [
  {
    file: "products/pc/app/src/server/services/pc-command-center.service.ts",
    markers: [
      "syncConflict.findMany",
      "Conflictos de sync relacionados con caja",
      "buildConflictDetailItems",
      "getCashConflictAction",
      "__rowDetailTitle",
      "cashConflictSample",
      "Tablet puede abrir, vender y cerrar localmente"
    ]
  },
  {
    file: "products/pc/app/components/backoffice/data-table.tsx",
    markers: [
      "<details",
      "Ver detalle",
      "Payload técnico",
      "__rowDetailItems",
      "status-detail-trigger"
    ]
  },
  {
    file: "products/pc/app/docs/PC_CASH_SESSION_CONFLICT_DIAGNOSTICS.md",
    markers: [
      "PC Cash Session Conflict Diagnostics",
      "No cambia schema Prisma",
      "Reglas de matching"
    ]
  }
];

const failures = [];
for (const check of checks) {
  const full = path.join(root, check.file);
  if (!fs.existsSync(full)) {
    failures.push(`missing file: ${check.file}`);
    continue;
  }
  const text = fs.readFileSync(full, "utf8");
  for (const marker of check.markers) {
    if (!text.includes(marker)) failures.push(`${check.file} missing marker: ${marker}`);
  }
}

const forbiddenFiles = [
  "products/tablet",
  "products/mobile",
  "products/chart-lab"
];

const summary = {
  verifier: "verify_pc_cash_session_conflict_details_1206",
  root,
  checked: checks.map((item) => item.file),
  forbidden_surfaces_not_modified_by_this_verifier: forbiddenFiles,
  failures
};

console.log(JSON.stringify(summary, null, 2));
if (failures.length) process.exit(1);
