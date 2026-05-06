#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);

function val(flag, fallback) {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
}

const root = path.resolve(val("--root", process.cwd()));
const verifiers = [
  { name: "verify_pc_runtime_01.mjs", phase: "I01", critical: true },
  { name: "verify_pc_labels_01.mjs", phase: "I01", critical: true },
  { name: "verify_pc_routes_01.mjs", phase: "I01", critical: true },
  { name: "verify_pc_catalog_02.mjs", phase: "I02", critical: false },
  { name: "verify_pc_stock_counts_audit_03.mjs", phase: "I03", critical: false },
  { name: "verify_pc_procurement_04.mjs", phase: "I04", critical: false },
  { name: "verify_pc_operation_04.mjs", phase: "I04", critical: false },
  { name: "verify_pc_dashboard_05.mjs", phase: "I05", critical: false },
  { name: "verify_pc_sync_ingest_06.mjs", phase: "I06", critical: false },
];

function hasReferenceError(text) {
  return /ReferenceError|require is not defined/.test(text);
}

function sample(text, size = 900) {
  return (text || "").slice(0, size);
}

const runs = verifiers.map((verifier) => {
  const res = spawnSync(process.execPath, [`tools/${verifier.name}`, "--root", root], {
    cwd: root,
    encoding: "utf8",
    timeout: 10000,
  });
  const combo = `${res.stdout || ""}\n${res.stderr || ""}`;
  return {
    ...verifier,
    exitCode: res.status,
    referenceError: hasReferenceError(combo),
    stdoutSample: sample(res.stdout),
    stderrSample: sample(res.stderr),
  };
});

const smoke = spawnSync(process.execPath, ["tools/smoke_pc_i01_routes.mjs", "--mode", "source", "--root", root], {
  cwd: root,
  encoding: "utf8",
  timeout: 10000,
});
const smokeCombo = `${smoke.stdout || ""}\n${smoke.stderr || ""}`;
const routeSmoke = {
  exitCode: smoke.status,
  referenceError: hasReferenceError(smokeCombo),
  stdoutSample: sample(smoke.stdout, 1200),
  stderrSample: sample(smoke.stderr, 1200),
};

const failed = runs.filter((run) => run.exitCode !== 0 || run.referenceError);
const criticalFailures = failed.filter((run) => run.critical);
const downstreamFailures = failed.filter((run) => !run.critical);
const routeSmokeOk = routeSmoke.exitCode === 0 && !routeSmoke.referenceError;
const ok = failed.length === 0 && routeSmokeOk;
const i01Ok = criticalFailures.length === 0 && routeSmokeOk;

console.log(
  JSON.stringify(
    {
      verifier: "pc_i01_release_gate",
      phase: "I01-I06",
      ok,
      i01Ok,
      finalState: ok ? "READY" : i01Ok ? "READY_WITH_CAVEATS" : "BLOCKED",
      root,
      criticalFailures,
      downstreamFailures,
      routeSmoke,
      runs,
      checkedAt: new Date().toISOString(),
    },
    null,
    2,
  ),
);

process.exit(ok ? 0 : 1);
