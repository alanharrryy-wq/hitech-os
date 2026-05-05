#!/usr/bin/env node
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = process.argv[2] || process.cwd();
const checks = [
  ['app/globals.css', ['PRISMA_PC_SHELL_ZOOM_SCROLL_TRACE_03 START','max-height: calc(100dvh - 44px)','overflow-y: auto !important','.skip-link:focus']],
  ['components/layout/app-shell.tsx', ['className="skip-link"','id="prisma-main-content"','aria-label="Navegación principal PC"']],
  ['app/suppliers.css', ['PRISMA_PC_SUPPLIERS_CHANGE_MAP_03 START','.supplier-change-map','.change-map-grid']],
  ['components/suppliers/smart-purchase-workbench.tsx', ['Mapa visible de la inyeccion PC Proveedores v03','Dónde pegó este cambio','/api/proveedores/calidad-datos']],
  ['docs/PC_SHELL_ZOOM_SCROLL_TRACE_03.md', ['zoom','barra lateral','/proveedores']]
];
let failed = false;
for (const [file, needles] of checks) {
  const path = join(root, file);
  if (!existsSync(path)) { console.error(`[FAIL] falta ${file}`); failed = true; continue; }
  const text = readFileSync(path, 'utf8');
  for (const needle of needles) if (!text.includes(needle)) { console.error(`[FAIL] ${file} no contiene: ${needle}`); failed = true; }
  if (!failed) console.log(`[OK] ${file}`);
}
if (failed) process.exit(2);
console.log('[OK] PRISMA PC shell zoom scroll trace v03 instalado');
