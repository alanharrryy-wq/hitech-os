// PRISMA_CHART_LAB_V31_GATE_RUNNER
import { spawnSync } from "node:child_process";
import { appRoot, report } from "./verify-chart-lab-v3-helper.mjs";

const failures = [];

for (const script of [
  "scripts/verify-chart-lab-v31-visual-qa-contract.mjs",
  "scripts/verify-chart-lab-v31-nonblank-chart-contract.mjs",
  "scripts/verify-chart-lab-v31-responsive-contract.mjs",
  "scripts/verify-chart-lab-code-drawers-contract.mjs"
]) {
  const result = spawnSync(process.execPath, [script], { cwd: appRoot(), stdio: "inherit" });
  if (result.status !== 0) failures.push(`${script} failed with exit code ${result.status}`);
}

report("chart-lab-v31-gates", failures);
