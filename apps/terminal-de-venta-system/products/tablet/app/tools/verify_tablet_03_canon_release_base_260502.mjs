#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function argRoot() {
  const idx = process.argv.indexOf('--root');
  if (idx >= 0 && process.argv[idx + 1]) return path.resolve(process.argv[idx + 1]);
  return process.cwd();
}
const root = argRoot();
function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}
function exists(rel) {
  if (!fs.existsSync(path.join(root, rel))) throw new Error(`missing ${rel}`);
}
function has(rel, needles) {
  const txt = read(rel);
  for (const n of needles) {
    if (!txt.includes(n)) throw new Error(`missing ${n} in ${rel}`);
  }
}
function countLines(rel) {
  const txt = read(rel).trim();
  if (!txt) return 0;
  return txt.split(/\r?\n/).length;
}

const manifest = JSON.parse(read('tools/fixtures/tablet_03_canon_release_base_260502_manifest.json'));
for (const route of manifest.criticalRoutes) {
  const rel = route === '/pos' ? 'app/pos/page.tsx' : `app${route}/page.tsx`;
  exists(rel);
}
for (const rel of [
  'app/api/pos/shift/current/route.ts',
  'app/api/pos/shift/open/route.ts',
  'app/api/pos/shift/close/route.ts',
  'app/api/pos/sync/panel/route.ts',
  'app/api/pos/sync/retry/route.ts',
  'app/api/pos/export/contextual/route.ts',
  'app/api/pos/release-gate/route.ts'
]) exists(rel);

has('components/tablet-shell/tablet-nav.ts', ['/catalog', '/stock', '/shift', '/sync', '/release-gate']);
has('components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx', ['Agregar a venta', 'Sin stock', 'Stock bajo']);
has('components/shift/shift-cash-closure-screen.tsx', ['Abrir turno', 'Cerrar turno', 'Diferencia']);
has('components/sync/pending-offline-sync-panel-screen.tsx', ['Pendientes', 'Reintentar']);
has('components/reports/contextual-export-actions.tsx', ['Exportar datos', 'format.toUpperCase']);
has('components/release-gate/tablet-operable-release-gate-screen.tsx', ['Cierre de ola Tablet', 'Capturas esperadas']);

// Prior no-tech-copy verifiers cover cashier-facing language.
const vectorChecks = [
  ['tools/fixtures/tablet_shift_cash_closure_cash_math_vectors_03l.jsonl', manifest.expectedVectorCounts.shiftCashMath],
  ['tools/fixtures/tablet_pending_offline_sync_panel_vectors_03m.jsonl', manifest.expectedVectorCounts.syncPanel],
  ['tools/fixtures/tablet_contextual_export_reports_vectors_03n.jsonl', manifest.expectedVectorCounts.contextualExport],
  ['tools/fixtures/tablet_operable_release_gate_vectors_03z.jsonl', manifest.expectedVectorCounts.releaseGate],
];
for (const [rel, expected] of vectorChecks) {
  const actual = countLines(rel);
  if (actual !== expected) throw new Error(`vector count mismatch ${rel}: expected ${expected}, got ${actual}`);
}

console.log('OK canon release base surfaces ' + manifest.criticalRoutes.length);
console.log('OK canon release base APIs 7');
console.log('OK canon vector totals ' + Object.values(manifest.expectedVectorCounts).reduce((a,b) => a + b, 0));
console.log('READY PRISMA Tablet 03 canon release base 260502');
