import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const toolsDir = path.dirname(fileURLToPath(import.meta.url));
const systemRoot = path.resolve(toolsDir, "..");
const appRoot = process.cwd();
const localRoot = path.join(systemRoot, "tools", "_local");
const safeHome = path.join(localRoot, "next-build-home");
const safeTmp = path.join(localRoot, "tmp");

mkdirSync(safeHome, { recursive: true });
mkdirSync(safeTmp, { recursive: true });

const env = {
  ...process.env,
  HOME: safeHome,
  USERPROFILE: safeHome,
  TEMP: safeTmp,
  TMP: safeTmp,
  NEXT_TELEMETRY_DISABLED: "1",
  PRISMA_HIDE_UPDATE_MESSAGE: "1",
};

const isWindows = process.platform === "win32";
const command = isWindows ? "cmd.exe" : "next";
const args = isWindows ? ["/d", "/s", "/c", "next.cmd build --webpack"] : ["build", "--webpack"];
const child = spawn(command, args, {
  cwd: appRoot,
  env,
  stdio: "inherit",
  shell: false,
});

child.on("exit", (code, signal) => {
  if (signal) {
    console.error(`next build terminated by signal ${signal}`);
    process.exit(1);
  }
  process.exit(code ?? 1);
});

child.on("error", (error) => {
  console.error(error);
  process.exit(1);
});
