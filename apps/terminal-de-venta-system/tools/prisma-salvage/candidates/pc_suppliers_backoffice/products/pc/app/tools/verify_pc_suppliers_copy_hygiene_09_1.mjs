#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const appRoot = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const files = [
  'components/suppliers/smart-purchase-workbench.tsx',
  'components/suppliers/supplier-action-cockpit.tsx'
];

const forbidden = [
  'blocked',
  'safe',
  'backoffice',
  'ingest',
  'POST /api',
  '/api/proveedores',
  'order_cutoff',
  'payment_due',
  'expected_receiving',
  '@/modules/sincronización/module.manifest'
];

let checks = 0;
for (const rel of files) {
  const abs = path.join(appRoot, rel);
  if (!fs.existsSync(abs)) throw new Error(`FALTA ${rel}`);
  const text = fs.readFileSync(abs, 'utf8');
  for (const token of forbidden) {
    if (text.toLowerCase().includes(token.toLowerCase())) {
      throw new Error(`Residuo no permitido en ${rel}: ${token}`);
    }
    checks += 1;
  }
}

const workbench = fs.readFileSync(path.join(appRoot, files[0]), 'utf8');
const cockpit = fs.readFileSync(path.join(appRoot, files[1]), 'utf8');
const required = [
  'SupplierActionCockpit',
  'Revisar antes',
  'Caja cómoda',
  'Panel administrativo',
  'recepción de eventos',
  'Simular compra',
  'Crear pedido sugerido',
  'Confirmar recepción',
  'Registrar pago'
];
const joined = `${workbench}\n${cockpit}`;
for (const token of required) {
  if (!joined.includes(token)) throw new Error(`Falta marcador esperado: ${token}`);
  checks += 1;
}

console.log(`NODE READY suppliers copy hygiene 09.1 ${checks} checks`);
