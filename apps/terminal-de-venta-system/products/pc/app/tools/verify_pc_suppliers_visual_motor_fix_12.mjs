#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.argv.includes("--root")
  ? process.argv[process.argv.indexOf("--root") + 1]
  : process.cwd();

const files = {
  cockpit: path.join(root, "products/pc/app/components/suppliers/supplier-action-cockpit.tsx"),
  css: path.join(root, "products/pc/app/app/suppliers-ux-v08.css"),
};

const failures = [];
function check(condition, label) {
  if (!condition) failures.push(label);
}
function mustContain(text, needle, label) {
  check(text.includes(needle), label || `missing ${needle}`);
}

for (const [name, file] of Object.entries(files)) {
  check(existsSync(file), `${name} file is missing: ${file}`);
}

if (failures.length === 0) {
  const cockpit = readFileSync(files.cockpit, "utf8");
  const css = readFileSync(files.css, "utf8");

  check(cockpit.trimStart().startsWith('"use client";'), "cockpit must keep the Next.js client directive first");
  mustContain(cockpit, "PRISMA_PROVEEDORES_VISUAL_MOTOR_FIX_12", "cockpit marker missing");
  mustContain(cockpit, "const [hydrated, setHydrated] = useState(false)", "hydration guard missing");
  mustContain(cockpit, "if (!hydrated) return;", "draft persistence must wait for hydration");
  mustContain(cockpit, "readJsonEnvelope(response)", "safe JSON response reader missing");
  mustContain(cockpit, "function safeReason", "safe reason fallback missing");
  mustContain(cockpit, "function normalizeMoneyInput", "money input sanitizer missing");
  mustContain(cockpit, "aria-busy={busy}", "aria busy state missing");
  mustContain(cockpit, "supplier-action-command-v12", "command summary strip missing");
  mustContain(cockpit, "Sin recomendaciones disponibles", "empty recommendation option missing");
  mustContain(cockpit, "Sin pedidos recepcionables", "empty orders option missing");
  mustContain(cockpit, "Sin cuentas pendientes", "empty payables option missing");
  mustContain(cockpit, "Presupuesto inválido", "budget validation missing");
  mustContain(cockpit, "Pago inválido", "payment validation missing");

  mustContain(css, "PRISMA_PROVEEDORES_VISUAL_MOTOR_FIX_12_START", "CSS fix start marker missing");
  mustContain(css, "PRISMA_PROVEEDORES_VISUAL_MOTOR_FIX_12_END", "CSS fix end marker missing");
  mustContain(css, "body:has(.supplier-page) .shell", "supplier scoped shell compaction missing");
  mustContain(css, ".supplier-action-cockpit-v12", "cockpit v12 class missing in CSS");
  mustContain(css, ".supplier-action-command-v12", "command strip CSS missing");
  mustContain(css, ".supplier-hero-v07 .hero-title", "hero title compaction missing");
  mustContain(css, ".sidebar .search-shell input", "sidebar search clipping fix missing");

  const opens = (css.match(/\{/g) || []).length;
  const closes = (css.match(/\}/g) || []).length;
  check(opens === closes, `CSS brace balance mismatch: ${opens} opens vs ${closes} closes`);

  check(!/kill\s*-?process|Stop-Process|taskkill|next dev -p|dev server/i.test(cockpit + css), "fix must not contain process/port control logic");
}

if (failures.length) {
  console.error("PRISMA proveedores visual/motor fix verification failed:");
  for (const failure of failures) console.error(` - ${failure}`);
  process.exit(1);
}

console.log("PRISMA proveedores visual/motor fix verification OK");
