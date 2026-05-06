import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const requiredFiles = [
  "src/lib/prisma-app/prisma-mobile-command-center.ts",
  "src/components/prisma-app/PrismaMobileCommandCenter.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "app/api/mobile/command-center/route.ts",
  "docs/prisma-app/PRISMA_APP_MOBILE_20_COMMAND_CENTER.md",
  "docs/prisma-app/qa/prisma-app-mobile-20-command-center-scenarios.json"
];

function read(rel) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) throw new Error(`Falta archivo requerido: ${rel}`);
  return fs.readFileSync(abs, "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const file of requiredFiles) read(file);

const commandCenter = read("src/lib/prisma-app/prisma-mobile-command-center.ts");
const commandComponent = read("src/components/prisma-app/PrismaMobileCommandCenter.tsx");
const dashboard = read("src/components/prisma-app/PrismaMobileDashboard.tsx");
const css = read("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const route = read("app/api/mobile/command-center/route.ts");
const pkg = JSON.parse(read("package.json"));
const scenarios = JSON.parse(read("docs/prisma-app/qa/prisma-app-mobile-20-command-center-scenarios.json"));

assert(commandCenter.includes("PRISMA_APP_MOBILE_20_COMMAND_CENTER"), "El contrato v20 no está declarado.");
assert(commandCenter.includes("buildPrismaMobileCommandCenter"), "Falta builder del Centro de Mando.");
assert(commandCenter.includes("readinessScore"), "Falta score de readiness.");
assert(commandCenter.includes("decisionQueue"), "Falta cola de decisión.");
assert(commandCenter.includes("dataQuality"), "Falta salud/calidad de datos.");
assert(!/Date\.now\(|Math\.random\(/.test(commandCenter), "El builder no debe usar Date.now ni Math.random.");
assert(!/demo|mock|fixture|lorem/i.test(commandCenter), "El builder contiene lenguaje de demo/mock/fixture.");

assert(commandComponent.includes("Centro de mando móvil"), "El componente no expone título operativo.");
assert(commandComponent.includes("data-prisma-contract"), "El componente no marca contrato PRISMA.");
assert(commandComponent.includes("command.decisionQueue.map"), "El componente no renderiza la cola priorizada.");
assert(commandComponent.includes("command.signals.map"), "El componente no renderiza señales ejecutivas.");
assert(!/Date\.now\(|Math\.random\(/.test(commandComponent), "El componente no debe generar valores variables durante render.");

assert(dashboard.includes("PrismaMobileCommandCenter"), "Dashboard no integra el Centro de Mando.");
assert(dashboard.indexOf("<PrismaMobileCommandCenter") < dashboard.indexOf("<section className={styles.metricGrid}"), "El Centro de Mando debe aparecer antes de KPI cards.");

for (const cls of ["commandCenter", "commandHeader", "commandScoreCard", "commandSignalGrid", "commandDecisionGrid", "commandDataQuality"]) {
  assert(css.includes(`.${cls}`), `Falta clase CSS ${cls}.`);
}

assert(!route.includes("http://") && !route.includes("https://"), "La ruta no debe depender de URLs absolutas.");
assert(route.includes("buildPrismaMobileCommandCenter"), "La API command-center no usa el builder canónico.");
assert(route.includes("noStoreJsonInit"), "La API command-center debe ser no-store.");

assert(pkg.scripts?.["verify:command-center"] === "node tools/verify_prisma_app_mobile_20_command_center.mjs", "package.json no declara verify:command-center.");
assert(pkg.prismaMobileCommandCenterVersion === "0.20.0", "package.json no declara prismaMobileCommandCenterVersion 0.20.0.");

assert(Array.isArray(scenarios.scenarios), "QA debe exponer scenarios[].");
assert(scenarios.scenarios.length >= 300, "QA debe cubrir al menos 300 escenarios útiles.");
assert(scenarios.contractId === "PRISMA_APP_MOBILE_20_COMMAND_CENTER", "QA debe declarar contrato v20.");
for (const item of scenarios.scenarios.slice(0, 12)) {
  assert(item.input && item.expected && item.expected.firstAction, "Escenario QA incompleto.");
}

console.log("OK PRISMA_APP_MOBILE_20_COMMAND_CENTER verified");
