#!/usr/bin/env node
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const serviceRoot = path.resolve(__dirname, "..");
const baseUrl = "http://127.0.0.1:3101";
const fixedNowUtc = "2026-01-01T00:00:00.000Z";

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitFor(url, timeoutMs = 10000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return true;
      }
    } catch {
      // retry
    }
    await wait(200);
  }
  return false;
}

async function readJson(response) {
  const text = await response.text();
  return text.length === 0 ? {} : JSON.parse(text);
}

function stableSort(input) {
  if (Array.isArray(input)) {
    return input.map((item) => stableSort(item));
  }

  if (input && typeof input === "object") {
    return Object.keys(input)
      .sort((left, right) => left.localeCompare(right))
      .reduce((accumulator, key) => {
        accumulator[key] = stableSort(input[key]);
        return accumulator;
      }, {});
  }

  return input;
}

async function run() {
  const child = spawn(process.execPath, ["--experimental-strip-types", "src/index.ts"], {
    cwd: serviceRoot,
    env: {
      ...process.env,
      CORE_API_HOST: "127.0.0.1",
      CORE_API_PORT: "3101",
      CORE_API_FIXED_NOW_UTC: fixedNowUtc
    },
    stdio: ["ignore", "pipe", "pipe"]
  });

  child.stdout.on("data", (chunk) => process.stdout.write(`[core-api] ${chunk}`));
  child.stderr.on("data", (chunk) => process.stderr.write(`[core-api:err] ${chunk}`));

  try {
    const ready = await waitFor(`${baseUrl}/health`);
    if (!ready) {
      throw new Error("core-api did not become healthy within timeout");
    }

    const enqueue = await fetch(`${baseUrl}/jobs`, {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify({
        jobId: "smoke-core-001",
        kind: "echo",
        input: {
          text: "hello"
        },
        requestedAtUtc: "2026-01-01T00:00:00.000Z",
        flags: {
          enableAiExecution: false,
          enableCapabilitiesProxy: false,
          enableExperimentalUi: false,
          enableHealthDashboard: false
        }
      })
    });

    const enqueuedResult = await readJson(enqueue);
    const status = await fetch(`${baseUrl}/jobs/smoke-core-001`);
    const statusResult = await readJson(status);
    const stage = await fetch(`${baseUrl}/governance/stage/S1`);
    const stageResult = await readJson(stage);
    const runs = await fetch(`${baseUrl}/governance/runs`);
    const runsResult = await readJson(runs);
    const manifestRunId =
      typeof runsResult.latestRunId === "string" && runsResult.latestRunId.length > 0
        ? runsResult.latestRunId
        : "missing-governance-run";
    const artifacts = await fetch(
      `${baseUrl}/governance/runs/${encodeURIComponent(manifestRunId)}/artifacts`
    );
    const artifactsResult = await readJson(artifacts);

    console.log("[smoke-core-api] enqueue", JSON.stringify(stableSort(enqueuedResult)));
    console.log("[smoke-core-api] status", JSON.stringify(stableSort(statusResult)));
    console.log("[smoke-core-api] governance-stage", JSON.stringify(stableSort(stageResult)));
    console.log("[smoke-core-api] governance-runs", JSON.stringify(stableSort(runsResult)));
    console.log(
      "[smoke-core-api] governance-artifacts",
      JSON.stringify(stableSort(artifactsResult))
    );
  } finally {
    child.kill("SIGTERM");
  }
}

run().catch((error) => {
  console.error("[smoke-core-api] FAILED", error.message);
  process.exitCode = 1;
});
