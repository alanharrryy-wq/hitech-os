import fs from 'node:fs';
import path from 'node:path';

const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const required = [
  'components/suppliers/smart-purchase-workbench.tsx',
  'src/lib/suppliers/visible-labels.ts',
  'src/lib/suppliers/operations-view-model.ts',
  'app/suppliers.css',
  'app/globals.css',
  'components/layout/app-shell.tsx',
  'src/lib/i18n/messages/es.ts'
];

for (const rel of required) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) fail(`Falta ${rel}`);
  if (fs.statSync(file).size < 400) fail(`Archivo demasiado chico o vacio: ${rel}`);
  ok(`existe ${rel}`);
}

const component = read('components/suppliers/smart-purchase-workbench.tsx');
const labels = read('src/lib/suppliers/visible-labels.ts');
const viewModel = read('src/lib/suppliers/operations-view-model.ts');
const globals = read('app/globals.css');
const suppliersCss = read('app/suppliers.css');
const shell = read('components/layout/app-shell.tsx');
const messages = read('src/lib/i18n/messages/es.ts');
const registry = read('src/composition/module-registry.ts');

mustContain(component, 'Centro operativo de proveedores', 'titulo de Proveedores v06');
mustContain(component, 'supplier-table-card-v06', 'tablas/cards v06');
mustContain(component, 'Se queda en PC', 'limite Tablet/App visible');
mustContain(component, 'buildSupplierOperatorBoardModel', 'view model desacoplado');
mustContain(viewModel, 'cleanVisibleText', 'limpieza de textos visibles');
mustContain(labels, 'calendarKindLabel', 'labels calendario');
mustContain(globals, 'PRISMA_PC_SIDEBAR_TRUE_SCROLL_06 START', 'fix scroll real v06');
mustContain(globals, 'overflow-y: auto !important', 'scroll vertical en sidebar');
mustContain(suppliersCss, 'PRISMA_PC_SUPPLIERS_OPERATOR_BOARD_SCROLL_ESMX_06 START', 'css proveedores v06');
mustContain(shell, 'Gemelo', 'shell en español');
mustContain(shell, 'Sincronización', 'footer sincronizacion en español');
mustContain(messages, 'lastSync: "sin respaldo consolidado"', 'mensaje lastSync corregido');
mustContain(messages, 'syncChip: "Validar eventos"', 'mensaje syncChip compatible');
mustContain(registry, '@/modules/sync/module.manifest', 'import sync tecnico correcto');

const visibleComponentForbidden = [
  'POST /api',
  '/api/proveedores',
  'order_cutoff',
  'expected_receiving',
  'payment_due',
  'Backoffice',
  'Dashboard',
  'Bloqueada',
  'Bloqueado',
  'blocked_supplier'
];
for (const bad of visibleComponentForbidden) {
  if (component.includes(bad)) fail(`Texto tecnico visible en componente: ${bad}`);
}

if (registry.includes('sincronización/module.manifest') || registry.includes('sincronizacion/module.manifest')) fail('Import roto de sincronizacion en registry');
if (!component.includes('role="table"')) fail('Faltan estructuras tipo tabla para legibilidad');
if ((component.match(/key=\{/g) || []).length < 8) fail('No hay suficientes keys explicitas para listas');

ok('no-tech-copy visible');
ok('sidebar true-scroll');
ok('operator board suppliers v06');

function read(rel) { return fs.readFileSync(path.join(root, rel), 'utf8'); }
function mustContain(text, needle, label) { if (!text.includes(needle)) fail(`No se encontro ${label}: ${needle}`); }
function ok(msg) { console.log(`OK ${msg}`); }
function fail(msg) { console.error(`FAIL ${msg}`); process.exit(1); }
