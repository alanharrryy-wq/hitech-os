import fs from "node:fs";
import path from "node:path";
import { chartOpsIds, fail, pass, read, terminalRoot } from "./chart-lab-script-utils.mjs";

const maps = read("src/prisma-charts/maps/chart-lab-maps.ts");
const sharedAtlas = read("shared/prisma-charts/prismaChartAtlas.ts", terminalRoot);
const chartIds = chartOpsIds();

if (maps.includes("visualTuningPassports")) pass("lab visual tuning passports exported");
else fail("visualTuningPassports export is missing");

for (const id of chartIds) {
  const passportFile = path.join(terminalRoot, "shared", "prisma-charts", "passports", `${id}.passport.ts`);
  const expectedSymbol = id
    .split(/[.-]/)
    .map((part, index) => (index === 0 ? part : part.charAt(0).toUpperCase() + part.slice(1)))
    .join("");
  if (fs.existsSync(passportFile) && sharedAtlas.includes(expectedSymbol)) pass(`passport registered: ${id}`);
  else fail(`passport missing or not registered: ${id}`);
}

const requiredFields = [
  "questionAnswered",
  "primaryUser",
  "contract",
  "adapter",
  "mock",
  "optionBuilder",
  "visualRecipe",
  "visualKnobs",
  "runtimeControls",
  "states",
  "interactions",
  "accessibility",
  "knownRisks",
  "doNotTouch",
  "editPlaybook",
  "validation"
];
for (const field of requiredFields) {
  if (maps.includes(field)) pass(`passport field covered: ${field}`);
  else fail(`passport field missing: ${field}`);
}

for (const field of ["safeRange", "premiumValue", "riskLevel", "surfaceSuitability", "accessibilityImpact", "performanceImpact", "promotionStatus", "failureMode"]) {
  if (maps.includes(field)) pass(`visual knob field covered: ${field}`);
  else fail(`visual knob field missing: ${field}`);
}

if (!process.exitCode) pass("passports verification complete");
