import { spawnSync } from "node:child_process";
import process from "node:process";

function parseArgValue(args, key) {
  const prefix = `--${key}=`;
  const match = args.find((arg) => arg.startsWith(prefix));
  return match ? match.slice(prefix.length) : undefined;
}

const args = process.argv.slice(2);
const smoke = args.includes("--smoke");
const serverMode = parseArgValue(args, "server-mode") ?? "prod";
const runId = parseArgValue(args, "run-id") ?? new Date().toISOString().replaceAll(":", "-");

const consumedArgs = new Set([
  "--smoke",
  ...args.filter((arg) => arg.startsWith("--server-mode=") || arg.startsWith("--run-id="))
]);

const passthroughArgs = args.filter((arg) => !consumedArgs.has(arg));
const overlayFlag = String(process.env.NEXT_PUBLIC_PITCH_DEBUG ?? "").trim() === "1" ? "1" : "0";

const env = {
  ...process.env,
  NEXT_PUBLIC_PITCH_DEBUG: overlayFlag,
  NEXT_PUBLIC_PITCH_DEBUG_LOCAL:
    String(process.env.NEXT_PUBLIC_PITCH_DEBUG_LOCAL ?? "").trim() === "1" ? "1" : "0",
  UI_IMPROVEMENT_SERVER_MODE: serverMode,
  SCENE_STUDIO_RUN_ID: runId
};

const commandArgs = [
  "exec",
  "playwright",
  "test",
  "--config",
  "playwright.config.ts",
  "visual-tests/ui-improvement.spec.ts",
  ...(smoke ? ["--grep", "@smoke"] : []),
  ...passthroughArgs
];

const result = spawnSync("pnpm", commandArgs, {
  cwd: process.cwd(),
  env,
  stdio: "inherit",
  shell: process.platform === "win32"
});

if (typeof result.status === "number") {
  process.exit(result.status);
}

if (result.error) {
  throw result.error;
}

process.exit(1);
