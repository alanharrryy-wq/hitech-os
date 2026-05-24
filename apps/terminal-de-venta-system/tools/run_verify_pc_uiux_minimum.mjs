#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import path from "node:path";

const root = process.cwd();
const verifiers = [
  "tools/verify_pc_uiux_routes_alive.mjs",
  "tools/verify_pc_uiux_no_jargon.mjs",
  "tools/verify_pc_uiux_button_contract.mjs",
  "tools/verify_pc_uiux_page_contracts.mjs",
  "tools/verify_pc_uiux_states_contract.mjs",
  "tools/verify_pc_uiux_no_downgrade.mjs",
  "tools/verify_pc_uiux_table_contract.mjs",
  "tools/verify_pc_uiux_chart_contract.mjs"
];

let failed = 0;
for (const vf of verifiers) {
  console.log(`\n=== ${vf} ===`);
  const result = spawnSync(process.execPath, [path.join(root, vf)], { cwd: root, encoding: "utf8", stdio: "pipe" });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.status !== 0) failed++;
}
console.log(`\nPC UIUX verifiers: ${failed ? "FAIL" : "PASS"} (${verifiers.length - failed}/${verifiers.length} passed)`);
process.exit(failed ? 1 : 0);
