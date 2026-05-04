import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2] ?? process.cwd();
const files = {
  scenarios: "src/lib/suppliers/lifecycle-scenarios.ts",
  validator: "src/lib/suppliers/lifecycle-validator.ts",
  transitions: "src/lib/suppliers/transition-policy.ts",
  events: "src/lib/suppliers/event-catalog.ts",
  mapping: "src/lib/suppliers/prisma-mapping.ts",
  reducer: "src/lib/suppliers/action-reducer.ts",
  repository: "src/lib/suppliers/repository-contract.ts",
  memory: "src/lib/suppliers/in-memory-repository.ts",
  dataQuality: "src/lib/suppliers/data-quality.ts",
  exports: "src/lib/suppliers/export-contracts.ts"
};
const failures = [];
for (const [key, rel] of Object.entries(files)) {
  if (!existsSync(join(root, rel))) failures.push(`Falta ${key}: ${rel}`);
}
const read = (rel) => readFileSync(join(root, rel), "utf8");
const scenarios = read(files.scenarios);
const validator = read(files.validator);
const transitions = read(files.transitions);
const events = read(files.events);
const mapping = read(files.mapping);
const reducer = read(files.reducer);
const repository = read(files.repository);
const memory = read(files.memory);
const dataQuality = read(files.dataQuality);
const exports = read(files.exports);

const expectedScenarios = ["SIM_SAFE_BEVERAGES", "SIM_REMOVE_CRITICAL", "ORDER_FROM_RECOMMENDATION", "ORDER_BLOCKED_BY_CASHIER", "RECEIVE_WITH_DIFFERENCE", "PAYMENT_PARTIAL", "BOUNDARY_TABLET_SIGNALS_ONLY"];
for (const id of expectedScenarios) if (!scenarios.includes(id)) failures.push(`Escenario faltante: ${id}`);
const expectedValidators = ["validateSupplierLifecycleSnapshot", "validateCreateSuggestedOrderInput", "validateConfirmReceivingInput", "validateRegisterPaymentInput", "hasPermission"];
for (const name of expectedValidators) if (!validator.includes(name)) failures.push(`Validador faltante: ${name}`);
const expectedTransitions = ["purchaseOrderTransitions", "receivingTransitions", "payableTransitions", "canTransition", "explainAllowedOrderNextStates"];
for (const name of expectedTransitions) if (!transitions.includes(name)) failures.push(`Transicion faltante: ${name}`);
const expectedEvents = ["supplierLifecycleEventCatalog", "listEventsAllowedForSurface", "describeEventForBusiness"];
for (const name of expectedEvents) if (!events.includes(name)) failures.push(`Evento faltante: ${name}`);
const expectedMapping = ["mapSupplierToPrisma", "mapOrderToPrisma", "mapReceiptToPrisma", "mapPayableToPrisma", "estimatePrismaWritePlan"];
for (const name of expectedMapping) if (!mapping.includes(name)) failures.push(`Mapping faltante: ${name}`);
const expectedReducer = ["reduceSupplierLifecycleAction", "reduceManySupplierLifecycleActions", "summarizeLifecycleState"];
for (const name of expectedReducer) if (!reducer.includes(name)) failures.push(`Reducer faltante: ${name}`);
const expectedRepo = ["SupplierRepository", "SupplierRepositoryReadModel", "makeMutationContext"];
for (const name of expectedRepo) if (!repository.includes(name)) failures.push(`Contrato repo faltante: ${name}`);
const expectedMemory = ["InMemorySupplierRepository", "createSuggestedOrder", "confirmReceiving", "registerPayment"];
for (const name of expectedMemory) if (!memory.includes(name)) failures.push(`Repositorio memoria faltante: ${name}`);
for (const name of ["buildSupplierDataQualityReport", "SupplierDataQualityFinding", "nextActions"]) if (!dataQuality.includes(name)) failures.push(`Calidad datos faltante: ${name}`);
for (const name of ["buildSupplierExportBundle", "toCsv", "buildAuditCsv"]) if (!exports.includes(name)) failures.push(`Exportable faltante: ${name}`);

if (failures.length) {
  console.error("BLOCKED supplier lifecycle scenario runner");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("READY supplier lifecycle scenario runner");
console.log(`Escenarios esperados: ${expectedScenarios.length}`);
console.log("Capas verificadas: scenarios, validator, transitions, events, mapping, reducer, repository, memory, data-quality, exports");
