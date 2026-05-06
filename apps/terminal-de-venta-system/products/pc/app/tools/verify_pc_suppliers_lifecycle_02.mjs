import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? process.cwd();
const required = [
  "app/proveedores/page.tsx",
  "app/api/proveedores/compra-inteligente/route.ts",
  "app/api/proveedores/operacion/route.ts",
  "app/api/proveedores/compra-inteligente/simular/route.ts",
  "app/api/proveedores/compra-inteligente/crear-pedido/route.ts",
  "app/api/proveedores/recepciones/confirmar/route.ts",
  "app/api/proveedores/cuentas-pagar/registrar-pago/route.ts",
  "components/suppliers/smart-purchase-workbench.tsx",
  "src/lib/suppliers/lifecycle-engine.ts",
  "src/lib/suppliers/server.ts",
  "src/lib/suppliers/types.ts",
  "src/lib/suppliers/fixtures.ts",
  "docs/PC_SUPPLIERS_OPERATION_LIFECYCLE_02.md",
  "docs/PC_SUPPLIERS_LIFECYCLE_ACCEPTANCE_02.md",
  "src/lib/suppliers/lifecycle-validator.ts",
  "src/lib/suppliers/lifecycle-scenarios.ts",
  "src/lib/suppliers/lifecycle-report.ts",
  "app/api/proveedores/auditoria/route.ts",
  "app/api/proveedores/calendario/route.ts",
  "app/api/proveedores/senales/route.ts",
  "app/api/proveedores/pedidos/route.ts",
  "app/api/proveedores/recepciones/route.ts",
  "app/api/proveedores/cuentas-pagar/route.ts",
  "app/api/proveedores/qa/escenarios/route.ts",
  "src/lib/suppliers/event-catalog.ts",
  "src/lib/suppliers/transition-policy.ts",
  "src/lib/suppliers/repository-contract.ts",
  "src/lib/suppliers/in-memory-repository.ts",
  "src/lib/suppliers/action-reducer.ts",
  "src/lib/suppliers/prisma-mapping.ts",
  "docs/PC_SUPPLIERS_API_CONTRACTS_02.md",
  "docs/PC_SUPPLIERS_PERSISTENCE_PLAN_03.md",
  "tools/run_pc_suppliers_lifecycle_scenarios_02.mjs",
  "src/lib/suppliers/data-quality.ts",
  "src/lib/suppliers/export-contracts.ts",
  "app/api/proveedores/calidad-datos/route.ts",
  "app/api/proveedores/exportables/route.ts",
  "docs/PC_SUPPLIERS_DATA_QUALITY_EXPORTS_02.md"
];

const failures = [];
for (const rel of required) {
  if (!existsSync(join(root, rel))) failures.push(`Falta ${rel}`);
}

const read = (rel) => readFileSync(join(root, rel), "utf8");
const component = read("components/suppliers/smart-purchase-workbench.tsx");
const lifecycle = read("src/lib/suppliers/lifecycle-engine.ts");
const server = read("src/lib/suppliers/server.ts");
const fixtures = read("src/lib/suppliers/fixtures.ts");
const route = read("app/api/proveedores/compra-inteligente/route.ts");
const validator = read("src/lib/suppliers/lifecycle-validator.ts");
const scenarios = read("src/lib/suppliers/lifecycle-scenarios.ts");
const report = read("src/lib/suppliers/lifecycle-report.ts");
const dataQuality = read("src/lib/suppliers/data-quality.ts");
const exports = read("src/lib/suppliers/export-contracts.ts");

for (const needle of ["SupplierLifecycleSnapshot", "createSuggestedOrderFromRecommendation", "confirmSupplierReceiving", "registerSupplierPayment", "buildSupplierLifecycleSnapshot"]) {
  if (!lifecycle.includes(needle)) failures.push(`lifecycle-engine.ts no contiene ${needle}`);
}
for (const needle of ["API operacion", "Flujo de pedido sugerido", "Movimientos previstos", "Rastro operativo", "Tablet y App movil"]) {
  if (!component.includes(needle)) failures.push(`workbench no contiene seccion ${needle}`);
}
for (const needle of ["getSupplierOperationsSnapshot", "runSmartPurchaseSimulation", "createOrderFromSmartPurchase", "confirmReceivingFromOrder", "registerPayablePayment"]) {
  if (!server.includes(needle)) failures.push(`server.ts no exporta ${needle}`);
}
if (!route.includes("lifecycle")) failures.push("ruta compra-inteligente no devuelve lifecycle");
if (!validator.includes("validateSupplierLifecycleSnapshot")) failures.push("validator no valida snapshot lifecycle");
if (!scenarios.includes("ORDER_BLOCKED_BY_CASHIER")) failures.push("scenarios no cubre frontera cajero/tablet");
if (!report.includes("buildSupplierLifecycleReport")) failures.push("report no construye reporte lifecycle");
if (!dataQuality.includes("buildSupplierDataQualityReport")) failures.push("data-quality no construye reporte de calidad");
if (!exports.includes("buildSupplierExportBundle")) failures.push("export-contracts no construye bundle exportable");
if (!fixtures.includes("supplierLifecycleFixtures")) failures.push("fixtures no incluye supplierLifecycleFixtures");
if (/\"id\": \"prod_\d+\",\n\s+\"sku\"/.test(fixtures)) failures.push("hay supplierProductLinks sin productId despues de id");

const forbiddenVisible = ["Smart Purchasing", "Purchase order", "Runtime exception", "Payload invalido"];
for (const bad of forbiddenVisible) {
  if (component.includes(bad)) failures.push(`copy visible prohibido: ${bad}`);
}

if (failures.length) {
  console.error("BLOCKED PRISMA PC suppliers lifecycle 02");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("READY PRISMA PC suppliers lifecycle 02");
console.log(`Archivos verificados: ${required.length}`);
console.log("Ciclo cubierto: recomendacion -> simulacion -> pedido -> recepcion -> cuenta por pagar -> auditoria");
