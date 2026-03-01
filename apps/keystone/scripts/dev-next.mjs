import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs/promises";
import net from "node:net";
import path from "node:path";

const basePortRaw = process.env.KEYSTONE_PORT ?? process.env.PORT ?? "3100";
const scanWindowRaw = process.env.KEYSTONE_PORT_SCAN ?? "20";
const basePort = Number.parseInt(basePortRaw, 10);
const scanWindow = Number.parseInt(scanWindowRaw, 10);
const extraArgs = process.argv.slice(2);
const require = createRequire(import.meta.url);

if (Number.isNaN(basePort) || basePort <= 0) {
  console.error(`[keystone] Invalid base port: ${basePortRaw}`);
  process.exit(1);
}

if (Number.isNaN(scanWindow) || scanWindow < 0) {
  console.error(`[keystone] Invalid scan window: ${scanWindowRaw}`);
  process.exit(1);
}

function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();

    server.once("error", () => {
      resolve(false);
    });

    server.once("listening", () => {
      server.close(() => resolve(true));
    });

    server.listen({ port });
  });
}

async function handleNextDevLock() {
  const lockPath = path.join(process.cwd(), ".next", "dev", "lock");

  try {
    const fd = await fs.open(lockPath, "r+");
    await fd.close();
    await fs.unlink(lockPath);
    console.warn(`[keystone] Removed stale Next dev lock: ${lockPath}`);
    return false;
  } catch (error) {
    if (error?.code === "ENOENT") {
      return false;
    }

    if (error?.code === "EBUSY" || error?.code === "EPERM") {
      console.warn(
        "[keystone] Next dev lock is active. Keystone is already running in another process.",
      );
      return true;
    }

    throw error;
  }
}

async function pickPort() {
  for (let i = 0; i <= scanWindow; i += 1) {
    const candidate = basePort + i;
    // eslint-disable-next-line no-await-in-loop
    const available = await isPortAvailable(candidate);
    if (available) {
      return candidate;
    }
  }

  return null;
}

const alreadyRunning = await handleNextDevLock();
if (alreadyRunning) {
  process.exit(0);
}

const selectedPort = await pickPort();
if (!selectedPort) {
  console.error(
    `[keystone] No free port found in range ${basePort}-${basePort + scanWindow}.`,
  );
  process.exit(1);
}

if (selectedPort !== basePort) {
  console.warn(
    `[keystone] Port ${basePort} is busy, switching to ${selectedPort}.`,
  );
}

const child = spawn(
  process.execPath,
  [
    require.resolve("next/dist/bin/next"),
    "dev",
    "-p",
    String(selectedPort),
    ...extraArgs,
  ],
  {
    stdio: "inherit",
    env: { ...process.env, PORT: String(selectedPort) },
  },
);

child.on("error", (error) => {
  console.error(`[keystone] Failed to start Next dev server: ${error.message}`);
  process.exit(1);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  process.exit(code ?? 0);
});
