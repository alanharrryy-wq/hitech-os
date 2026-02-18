#!/usr/bin/env node
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");
const coreApiDir = path.join(repoRoot, "services/core-api");
const aiAgentDir = path.join(repoRoot, "services/ai-agent");

const coreApiBaseUrl = "http://127.0.0.1:3001";
const aiAgentBaseUrl = "http://127.0.0.1:8001";

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForHealth(url, timeoutMs = 12000) {
  const startedAt = Date.now();

  while (Date.now() - startedAt <= timeoutMs) {
    try {
      const response = await fetch(url, { method: "GET" });
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
  return text.trim().length > 0 ? JSON.parse(text) : {};
}

function startProcess(command, args, cwd, label, extraEnv = {}) {
  const child = spawn(command, args, {
    cwd,
    env: {
      ...process.env,
      ...extraEnv
    },
    stdio: ["ignore", "pipe", "pipe"]
  });

  child.stdout.on("data", (chunk) => {
    process.stdout.write(`[${label}] ${chunk}`);
  });

  child.stderr.on("data", (chunk) => {
    process.stderr.write(`[${label}:err] ${chunk}`);
  });

  return child;
}

function stopProcess(child) {
  if (!child || child.killed) {
    return;
  }

  child.kill("SIGTERM");
}

async function runSmoke() {
  const ai = startProcess(
    "python",
    ["-m", "app.main", "--host", "127.0.0.1", "--port", "8001"],
    aiAgentDir,
    "ai-agent"
  );

  const core = startProcess(
    process.execPath,
    ["--experimental-strip-types", "src/index.ts"],
    coreApiDir,
    "core-api",
    {
      CORE_API_HOST: "127.0.0.1",
      CORE_API_PORT: "3001",
      AI_AGENT_URL: aiAgentBaseUrl,
      AI_AGENT_TIMEOUT_MS: "1200"
    }
  );

  try {
    const aiReady = await waitForHealth(`${aiAgentBaseUrl}/health`);
    if (!aiReady) {
      throw new Error("ai-agent health endpoint did not become ready");
    }

    const coreReady = await waitForHealth(`${coreApiBaseUrl}/health`);
    if (!coreReady) {
      throw new Error("core-api health endpoint did not become ready");
    }

    const jobId = "bridge-smoke-001";

    const enqueueResponse = await fetch(`${coreApiBaseUrl}/jobs`, {
      method: "POST",
      headers: {
        "content-type": "application/json"
      },
      body: JSON.stringify({
        jobId,
        kind: "summarize_text",
        input: {
          text: "Deterministic systems prefer stable contracts. Stable contracts reduce regressions."
        },
        requestedAtUtc: "2026-01-01T00:00:00.000Z",
        flags: {
          enableAiExecution: true,
          enableCapabilitiesProxy: false,
          enableExperimentalUi: false,
          enableHealthDashboard: false
        }
      })
    });

    const runResponse = await fetch(`${coreApiBaseUrl}/jobs/${jobId}/run`, {
      method: "POST"
    });

    const statusResponse = await fetch(`${coreApiBaseUrl}/jobs/${jobId}`, {
      method: "GET"
    });

    const capabilitiesResponse = await fetch(`${coreApiBaseUrl}/capabilities`, {
      method: "GET"
    });

    const enqueue = await readJson(enqueueResponse);
    const run = await readJson(runResponse);
    const status = await readJson(statusResponse);
    const capabilities = await readJson(capabilitiesResponse);

    console.log("[smoke-bridge] enqueue", JSON.stringify(enqueue));
    console.log("[smoke-bridge] run", JSON.stringify(run));
    console.log("[smoke-bridge] status", JSON.stringify(status));
    console.log("[smoke-bridge] capabilities", JSON.stringify(capabilities));

    if (!enqueueResponse.ok || !runResponse.ok || !statusResponse.ok || !capabilitiesResponse.ok) {
      throw new Error(
        `Unexpected statuses enqueue=${enqueueResponse.status} run=${runResponse.status} status=${statusResponse.status} capabilities=${capabilitiesResponse.status}`
      );
    }

    if (status.status !== "completed") {
      throw new Error(`Expected completed status but received ${status.status}`);
    }
  } finally {
    stopProcess(core);
    stopProcess(ai);
  }
}

runSmoke().catch((error) => {
  console.error("[smoke-bridge] FAILED", error.message);
  process.exitCode = 1;
});
