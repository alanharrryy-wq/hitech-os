import { fail, pass, run, writeEvidence } from "./chart-lab-script-utils.mjs";

const commands = [
  ["node", ["scripts/verify-chart-lab.mjs"]],
  ["node", ["scripts/verify-chart-lab-controls.mjs"]],
  ["node", ["scripts/verify-chart-lab-maps.mjs"]],
  ["node", ["scripts/verify-chart-lab-passports.mjs"]],
  ["node", ["scripts/verify-chart-lab-promotion.mjs"]],
  ["node", ["scripts/verify-chart-lab-echarts-boundary.mjs"]]
];

const results = [];
for (const [command, args] of commands) {
  const result = run(command, args);
  const label = `${command} ${args.join(" ")}`;
  results.push({ command: label, status: result.status, stdout: result.stdout, stderr: result.stderr });
  if (result.status === 0) pass(label);
  else fail(label);
}

const outPath = writeEvidence("verify-all-report.json", { generatedAt: new Date().toISOString(), results });
pass(`verify-all evidence: ${outPath}`);
