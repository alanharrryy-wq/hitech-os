#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const pcRoot = path.join(root, "products", "pc", "app");
const allowedStarts = ["Revisar","Crear","Guardar","Descargar","Reintentar","Sincronizar","Registrar","Ver","Copiar","Restaurar","Corregir","Comparar","Continuar","Cancelar","Confirmar","Actualizar","Enviar","Aplicar","Cerrar","Abrir","Quitar","Agregar","Editar","Buscar","Probar","Duplicar","Filtrar","Limpiar","Reset","Exportar","Simular"];
const dangerous = ["Eliminar", "Restaurar", "Rehacer sincronización", "Enviar catálogo completo", "Cambiar configuración global", "Registrar recepción", "Registrar pago", "Crear pedido real"];
const ignoreDirs = new Set(["node_modules", ".next", "out", "dist", "build", "coverage", "test-results", "playwright-report"]);
const ignoredPathHints = ["/docs/", "/src/uiux/", "/api/", "/server/"];

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

function ignored(file) {
  const n = file.replace(/\\/g, "/");
  return ignoredPathHints.some(h => n.includes(h));
}

function cleanLabel(s) {
  return s
    .replace(/\{[\s\S]*?\}/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/[()[\]]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const files = walk(pcRoot).filter(f => /\.(tsx|jsx)$/.test(f) && !ignored(f));
const badLabels = [];
const dangerousWithoutConfirm = [];
const possibleNoHandler = [];

for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const buttonRx = /<(button|Button)\b([^>]*)>([\s\S]*?)<\/\1>/g;
  let m;
  while ((m = buttonRx.exec(text))) {
    const attrs = m[2] || "";
    const body = m[3] || "";
    const label = cleanLabel(body);
    if (!label || label.length > 60 || /^[+×…·]$/.test(label)) continue;

    const line = text.slice(0, m.index).split(/\r?\n/).length;
    const rel = path.relative(root, file).replace(/\\/g, "/");
    const allowed = allowedStarts.some(v => label === v || label.startsWith(v + " "));
    if (!allowed) badLabels.push({ file: rel, line, label });

    const hasHandler = /onClick\s*=|type\s*=\s*["']submit["']|href\s*=/.test(attrs);
    if (!hasHandler) possibleNoHandler.push({ file: rel, line, label });

    const isDangerous = dangerous.some(d => label === d || label.startsWith(d));
    const hasConfirmHint = /confirm|Confirm|dialog|Dialog|modal|Modal|danger|destructive|areYouSure|confirmacion|Confirmacion/.test(attrs + body);
    if (isDangerous && !hasConfirmHint) dangerousWithoutConfirm.push({ file: rel, line, label });
  }
}

const fail = dangerousWithoutConfirm.length > 0;
console.log(JSON.stringify({ verifier: "verify_pc_uiux_button_contract", status: fail ? "FAIL" : "PASS", badLabelCount: badLabels.length, dangerousWithoutConfirmCount: dangerousWithoutConfirm.length, possibleNoHandlerCount: possibleNoHandler.length, badLabels: badLabels.slice(0, 120), dangerousWithoutConfirm: dangerousWithoutConfirm.slice(0, 120), possibleNoHandler: possibleNoHandler.slice(0, 120), note: "Bad labels are advisory; dangerous actions without confirmation fail." }, null, 2));
process.exit(fail ? 1 : 0);
