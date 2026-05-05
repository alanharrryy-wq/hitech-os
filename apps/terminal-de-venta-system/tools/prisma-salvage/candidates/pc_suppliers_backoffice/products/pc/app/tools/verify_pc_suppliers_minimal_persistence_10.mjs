#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] || process.cwd();
const checks = [];
function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) throw new Error(`missing ${rel}`);
  return fs.readFileSync(file, "utf8");
}
function ok(name, pass, detail = "") {
  checks.push({ name, pass, detail });
  if (!pass) throw new Error(`FAIL ${name}${detail ? `: ${detail}` : ""}`);
  console.log(`OK ${name}`);
}

const cockpit = read("components/suppliers/supplier-action-cockpit.tsx");
const css = read("app/suppliers-ux-v08.css");
const persistence = read("src/lib/suppliers/client-persistence.ts");

ok("v10 persistence helper", persistence.includes("readSupplierPersistence") && persistence.includes("appendSupplierActionRecord"));
ok("v10 storage key", persistence.includes("prisma.pc.proveedores.persistencia.v10"));
ok("cockpit imports persistence", cockpit.includes("@/lib/suppliers/client-persistence"));
ok("cockpit renders persistence panel", cockpit.includes("supplier-persistence-v10") && cockpit.includes("Registro local de decisiones"));
ok("cockpit can export", cockpit.includes("Exportar registro") && cockpit.includes("supplierPersistenceFileName"));
ok("cockpit can clear", cockpit.includes("Limpiar registro") && cockpit.includes("clearSupplierPersistence"));
ok("css persistence classes", css.includes("supplier-persistence-v10") && css.includes("supplier-persistence-metrics-v10"));

const forbidden = ["POST /api", "/api/" + "proveedores", "order_" + "cutoff", "payment_" + "due", "expected_" + "receiving", "block" + "ed", "sa" + "fe", "back" + "office", "ing" + "est"];
for (const word of forbidden) {
  ok(`no visible residue ${word}`, !cockpit.includes(word), "cockpit limpio");
}

console.log(`NODE READY suppliers minimal persistence v10 ${checks.length} checks`);
