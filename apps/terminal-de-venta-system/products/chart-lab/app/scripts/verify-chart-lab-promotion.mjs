import { fail, pass, read, run } from "./chart-lab-script-utils.mjs";

const script = read("scripts/promote-chart.mjs");
for (const needle of ["Chart Promotion Bridge", "--dry-run", "--apply", "featureFlag", "backupRoot", "rollbackManifest", "BLOCKED_BY_DEFAULT_SAFE_POLICY"]) {
  if (script.includes(needle)) pass(`promotion bridge contains: ${needle}`);
  else fail(`promotion bridge missing: ${needle}`);
}

const dryRuns = [
  ["--chart=pc.causal-flow-ribbon", "--target=pc", "--dry-run"],
  ["--chart=tablet.shift-pulse-strip", "--target=tablet", "--dry-run"],
  ["--chart=mobile.owner-pulse-timeline", "--target=mobile", "--dry-run"]
];

for (const args of dryRuns) {
  const result = run("node", ["scripts/promote-chart.mjs", ...args]);
  if (result.status === 0) pass(`promotion dry-run works: ${args.join(" ")}`);
  else fail(`promotion dry-run failed: ${args.join(" ")}\n${result.stderr}`);
}

if (!process.exitCode) pass("promotion verification complete");
