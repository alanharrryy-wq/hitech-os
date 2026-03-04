import { mkdirSync } from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import process from "node:process";

function resolveCommandArgs() {
  const passthrough = process.argv.slice(2);
  if (passthrough.length === 0) {
    return ["preview", "--env", "preview"];
  }
  return passthrough;
}

function resolveWindowsSafeEnv() {
  if (process.platform !== "win32") {
    return {
      env: { ...process.env },
      tmpDir: null
    };
  }

  const tmpDir = path.join(process.cwd(), ".wrangler", "tmp");
  mkdirSync(tmpDir, { recursive: true });

  return {
    env: {
      ...process.env,
      TEMP: tmpDir,
      TMP: tmpDir,
      TMPDIR: tmpDir
    },
    tmpDir
  };
}

function printEnoentHint(tmpDir) {
  console.error("[cf:preview] Detected ENOENT while running OpenNext/Wrangler preview.");
  if (tmpDir) {
    console.error(`[cf:preview] Windows temp override used: ${tmpDir}`);
  }
  console.error("[cf:preview] Run preview from WSL for best reliability on Windows.");
  console.error(
    "[cf:preview] See apps/keystone/docs/CLOUDFLARE_DEPLOY.md#10-troubleshooting for details."
  );
}

async function main() {
  const commandArgs = resolveCommandArgs();
  const { env, tmpDir } = resolveWindowsSafeEnv();

  if (tmpDir) {
    console.log(`[cf:preview] Windows temp override: ${tmpDir}`);
  }

  const child = spawn("opennextjs-cloudflare", commandArgs, {
    cwd: process.cwd(),
    env,
    stdio: ["inherit", "pipe", "pipe"],
    shell: process.platform === "win32"
  });

  let combined = "";

  child.stdout.on("data", (chunk) => {
    const text = String(chunk);
    combined += text;
    process.stdout.write(chunk);
  });

  child.stderr.on("data", (chunk) => {
    const text = String(chunk);
    combined += text;
    process.stderr.write(chunk);
  });

  child.on("error", (error) => {
    const text = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
    combined += text;
  });

  child.on("close", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }

    const normalized = combined.toUpperCase();
    const hasEnoent = normalized.includes("ENOENT");
    if ((code ?? 1) !== 0 && hasEnoent) {
      printEnoentHint(tmpDir);
    }

    process.exit(code ?? 1);
  });
}

void main().catch((error) => {
  const text = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
  if (text.toUpperCase().includes("ENOENT")) {
    printEnoentHint(null);
  } else {
    console.error(`[cf:preview] ${text}`);
  }
  process.exit(1);
});
