/* eslint-env node */
/* global Buffer, clearTimeout, setTimeout */
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import process from "node:process";

function parseArgValue(args, key) {
  const prefix = `--${key}=`;
  const match = args.find((arg) => arg.startsWith(prefix));
  return match ? match.slice(prefix.length) : undefined;
}

function parseIntegerArg(value, fallback) {
  if (value === undefined) {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }

  return parsed;
}

function formatCommand(command, commandArgs) {
  return [command, ...commandArgs].join(" ");
}

function createOutputTailBuffer(limitBytes) {
  const chunks = [];
  let sizeBytes = 0;

  return {
    append(chunk) {
      if (!chunk || chunk.length === 0) {
        return;
      }

      chunks.push(chunk);
      sizeBytes += chunk.length;

      while (sizeBytes > limitBytes && chunks.length > 0) {
        const head = chunks[0];
        if (!head) {
          break;
        }

        const overflow = sizeBytes - limitBytes;
        if (overflow >= head.length) {
          chunks.shift();
          sizeBytes -= head.length;
          continue;
        }

        chunks[0] = head.subarray(overflow);
        sizeBytes -= overflow;
        break;
      }
    },
    toString() {
      if (chunks.length === 0) {
        return "";
      }

      return Buffer.concat(chunks).toString("utf8");
    }
  };
}

function toBuffer(chunk) {
  return Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk, "utf8");
}

const args = process.argv.slice(2);
const passthroughIndex = args.indexOf("--");

const jsonOutput = args.includes("--json");
const updateBaseline = args.includes("--update-baseline");
const strict = args.includes("--strict");
const smoke = args.includes("--smoke");
const full = args.includes("--full");
const serverMode = parseArgValue(args, "server-mode") ?? "prod";
const strictThreshold = parseArgValue(args, "strict-threshold");
const routeFilter = parseArgValue(args, "route");
const claimId = parseArgValue(args, "claim-id");
const runId = parseArgValue(args, "run-id") ?? claimId ?? new Date().toISOString().replaceAll(":", "-");
const timeoutMs = parseIntegerArg(parseArgValue(args, "timeout-ms"), 0);
const baseUrl = parseArgValue(args, "base-url");
const outputLimitBytes = parseIntegerArg(parseArgValue(args, "output-limit-bytes"), 512_000);

const sceneIds = args
  .filter((arg) => arg.startsWith("--scene-id="))
  .map((arg) => arg.slice("--scene-id=".length))
  .filter((value) => value.length > 0);

const sceneTags = args
  .filter((arg) => arg.startsWith("--tag="))
  .map((arg) => arg.slice("--tag=".length))
  .filter((value) => value.length > 0);

const consumed = new Set([
  "--json",
  "--update-baseline",
  "--strict",
  "--smoke",
  "--full",
  ...args.filter((arg) =>
    [
      "--strict-threshold=",
      "--route=",
      "--run-id=",
      "--claim-id=",
      "--server-mode=",
      "--timeout-ms=",
      "--base-url=",
      "--output-limit-bytes=",
      "--scene-id=",
      "--tag="
    ]
      .some((prefix) => arg.startsWith(prefix))
  )
]);

const passthroughArgs =
  passthroughIndex >= 0
    ? args.slice(passthroughIndex + 1)
    : args.filter((arg) => !consumed.has(arg));

const env = {
  ...process.env,
  UI_IMPROVEMENT_SERVER_MODE: serverMode,
  SCENE_STUDIO_RUN_ID: runId,
  SCENE_STUDIO_SMOKE: smoke && !full ? "1" : "0",
  ...(baseUrl ? { UI_IMPROVEMENT_BASE_URL: baseUrl } : {}),
  ...(updateBaseline ? { UI_IMPROVEMENT_UPDATE_BASELINE: "1" } : {}),
  ...(strict ? { UI_IMPROVEMENT_STRICT: "1" } : {}),
  ...(strictThreshold ? { UI_IMPROVEMENT_STRICT_THRESHOLD: strictThreshold } : {}),
  ...(routeFilter ? { SCENE_STUDIO_FILTER_ROUTE: routeFilter } : {}),
  ...(sceneIds.length > 0 ? { SCENE_STUDIO_FILTER_IDS: sceneIds.join(",") } : {}),
  ...(sceneTags.length > 0 ? { SCENE_STUDIO_FILTER_TAGS: sceneTags.join(",") } : {})
};

const require = createRequire(import.meta.url);
const playwrightCli = require.resolve("@playwright/test/cli");

const command = process.execPath;
const commandArgs = [
  playwrightCli,
  "test",
  "--config",
  "playwright.config.ts",
  "visual-tests/ui-improvement.spec.ts",
  ...passthroughArgs
];

async function runPlaywright() {
  const startedAt = Date.now();
  const stdoutTail = createOutputTailBuffer(outputLimitBytes);
  const stderrTail = createOutputTailBuffer(outputLimitBytes);
  const streamOutput = !jsonOutput;

  let child;
  try {
    child = spawn(command, commandArgs, {
      cwd: process.cwd(),
      env,
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"]
    });
  } catch (error) {
    return {
      kind: "spawn_failed",
      command: formatCommand(command, commandArgs),
      cwd: process.cwd(),
      exitCode: 1,
      signal: null,
      durationMs: Date.now() - startedAt,
      timedOut: false,
      stdout: "",
      stderr: "",
      errorMessage: error instanceof Error ? error.message : String(error)
    };
  }

  if (child.stdout) {
    child.stdout.on("data", (chunk) => {
      const buffer = toBuffer(chunk);
      stdoutTail.append(buffer);
      if (streamOutput) {
        process.stdout.write(buffer);
      }
    });
  }

  if (child.stderr) {
    child.stderr.on("data", (chunk) => {
      const buffer = toBuffer(chunk);
      stderrTail.append(buffer);
      if (streamOutput) {
        process.stderr.write(buffer);
      }
    });
  }

  return await new Promise((resolve) => {
    let timedOut = false;
    let hardKillTimer;
    const timeoutTimer =
      timeoutMs > 0
        ? setTimeout(() => {
            timedOut = true;
            child.kill("SIGTERM");
            hardKillTimer = setTimeout(() => {
              child.kill("SIGKILL");
            }, 5_000);
          }, timeoutMs)
        : undefined;

    const finalize = (result) => {
      if (timeoutTimer) {
        clearTimeout(timeoutTimer);
      }
      if (hardKillTimer) {
        clearTimeout(hardKillTimer);
      }

      resolve({
        ...result,
        command: formatCommand(command, commandArgs),
        cwd: process.cwd(),
        durationMs: Date.now() - startedAt,
        timedOut,
        stdout: stdoutTail.toString(),
        stderr: stderrTail.toString()
      });
    };

    child.once("error", (error) => {
      finalize({
        kind: "spawn_failed",
        exitCode: 1,
        signal: null,
        errorMessage: error instanceof Error ? error.message : String(error)
      });
    });

    child.once("close", (code, signal) => {
      finalize({
        kind: timedOut ? "timeout" : "exited",
        exitCode: typeof code === "number" ? code : 1,
        signal: signal ?? null,
        errorMessage: null
      });
    });
  });
}

const summary = await runPlaywright();

if (jsonOutput) {
  process.stdout.write(`${JSON.stringify(summary)}\n`);
}

process.exit(summary.exitCode ?? 1);
