#!/usr/bin/env node
import { spawnSync } from "node:child_process";

function run(command, args) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });

  return {
    command: [command, ...args].join(" "),
    rc: result.status ?? 1,
    stdout: result.stdout?.trim() ?? "",
    stderr: result.stderr?.trim() ?? ""
  };
}

const checks = [
  run("node", ["--version"]),
  run(process.platform === "win32" ? "pnpm.cmd" : "pnpm", ["--version"]),
  run("git", ["--version"]),
  run("node", ["tools/hos/quality/governance/pitch_engine_gate.mjs"])
];

const pass = checks.every((check) => check.rc === 0);

console.log(`${pass ? "PASS" : "FAIL"} verification_doctor`);
console.log(JSON.stringify({ pass, checks }, null, 2));
process.exit(pass ? 0 : 1);
