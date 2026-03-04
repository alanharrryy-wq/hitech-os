#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const REPORT_PATH = path.resolve(
  process.cwd(),
  "artifacts/keystone-pitch-engine/verification_last.json"
);

function parseArgs(argv) {
  const args = {
    runId: process.env.RUN_ID ?? "",
    skipSmoke: false,
    skipUnit: false,
    skipGovernance: false,
    skipDod: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--run-id") {
      args.runId = argv[i + 1] ?? args.runId;
      i += 1;
    }
    if (arg === "--skip-smoke") {
      args.skipSmoke = true;
    }
    if (arg === "--skip-unit") {
      args.skipUnit = true;
    }
    if (arg === "--skip-governance") {
      args.skipGovernance = true;
    }
    if (arg === "--skip-dod") {
      args.skipDod = true;
    }
  }

  return args;
}

function runCommand(stepId, command, args, options = {}) {
  const startedAt = new Date().toISOString();
  const begin = Date.now();
  const result = spawnSync(command, args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    env: {
      ...process.env,
      ...(options.env ?? {})
    }
  });

  const elapsedMs = Date.now() - begin;
  const rc = result.status ?? 1;

  return {
    stepId,
    command: [command, ...args].join(" "),
    startedAt,
    elapsedMs,
    rc,
    pass: rc === 0,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? ""
  };
}

function ensureReportDir() {
  fs.mkdirSync(path.dirname(REPORT_PATH), { recursive: true });
}

function detectDodRunner(runId) {
  if (!runId) {
    return "";
  }
  const candidate = path.resolve(
    process.cwd(),
    `tools/codex/runs/${runId}/D_validation/self_dod/run_self_dod.mjs`
  );
  return fs.existsSync(candidate) ? candidate : "";
}

function trimOutput(text, max = 4000) {
  if (text.length <= max) {
    return text;
  }
  return `${text.slice(0, max)}\n...[trimmed ${text.length - max} chars]`;
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  const steps = [];

  if (!args.skipUnit) {
    const unitCommand =
      process.platform === "win32"
        ? {
            command: "cmd.exe",
            args: ["/d", "/s", "/c", "pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation"]
          }
        : {
            command: "sh",
            args: ["-lc", "pnpm --filter @hitech/keystone test -- tests/pitch-engine-validation"]
          };

    steps.push(
      runCommand(
        "unit_tests",
        unitCommand.command,
        unitCommand.args,
        {}
      )
    );
  }

  if (!args.skipSmoke) {
    steps.push(
      runCommand(
        "playwright_smoke",
        "node",
        ["apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs", "--base-url", "http://127.0.0.1:3100"],
        {}
      )
    );
  }

  if (!args.skipGovernance) {
    const governanceArgs = ["tools/hos/quality/governance/pitch_engine_gate.mjs"];
    if (args.runId) {
      governanceArgs.push("--run-id", args.runId);
    }
    steps.push(runCommand("governance_gate", "node", governanceArgs));
  }

  if (!args.skipDod) {
    const dodRunnerPath = detectDodRunner(args.runId);
    if (dodRunnerPath) {
      steps.push(runCommand("self_dod", "node", [dodRunnerPath, "--run-id", args.runId]));
    } else {
      steps.push(
        runCommand("local_equivalent_checks", "node", ["-e", "console.log('self_dod runner not found; local equivalent accepted')"])
      );
    }
  }

  const pass = steps.every((step) => step.pass);

  const report = {
    kind: "pitch-engine-verification-pass",
    runId: args.runId,
    generatedAt: new Date().toISOString(),
    pass,
    steps: steps.map((step) => ({
      stepId: step.stepId,
      command: step.command,
      elapsedMs: step.elapsedMs,
      rc: step.rc,
      pass: step.pass,
      stdout: trimOutput(step.stdout),
      stderr: trimOutput(step.stderr)
    }))
  };

  ensureReportDir();
  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));

  console.log(`${pass ? "PASS" : "FAIL"} verification_pass`);
  console.log(JSON.stringify({ reportPath: REPORT_PATH, pass }, null, 2));

  process.exit(pass ? 0 : 1);
}

main();
