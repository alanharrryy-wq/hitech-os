import { spawn } from "node:child_process";
import net from "node:net";
import process from "node:process";

const DEFAULT_PORT = 3100;
const DEFAULT_MAX_PORT = 3199;
const PORT_SCAN_WINDOW = 100;

function parsePort(raw) {
  if (raw === undefined || raw === null) {
    return null;
  }
  const value = String(raw).trim();
  if (value.length === 0) {
    return null;
  }
  const parsed = Number.parseInt(value, 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 65535) {
    return null;
  }
  return parsed;
}

function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.unref();

    server.on("error", () => {
      resolve(false);
    });

    server.listen(port, () => {
      server.close(() => resolve(true));
    });
  });
}

async function resolvePort() {
  const envPort = parsePort(process.env.KEYSTONE_PORT ?? process.env.PORT);
  const startPort = envPort ?? DEFAULT_PORT;
  const endPort = envPort ? Math.min(65535, startPort + PORT_SCAN_WINDOW - 1) : DEFAULT_MAX_PORT;

  for (let candidate = startPort; candidate <= endPort; candidate += 1) {
    // Deterministic: first available port in ascending order.
    if (await isPortAvailable(candidate)) {
      return {
        requestedPort: startPort,
        selectedPort: candidate,
        usedFallback: candidate !== startPort,
        fromEnvOverride: envPort !== null,
        scanEnd: endPort
      };
    }
  }

  throw new Error(
    `No available port found in range ${startPort}-${endPort}. Set KEYSTONE_PORT to a free port.`
  );
}

function printBanner(portResolution) {
  const { requestedPort, selectedPort, usedFallback, fromEnvOverride, scanEnd } = portResolution;
  console.log("[keystone:scene:studio] Keystone Scene Studio");
  console.log(`[keystone:scene:studio] Selected port: ${selectedPort}`);
  console.log(`[keystone:scene:studio] URL: http://localhost:${selectedPort}`);
  if (usedFallback) {
    const source = fromEnvOverride ? "requested env port" : "default port";
    console.log(
      `[keystone:scene:studio] ${source} ${requestedPort} is busy; using first free port in ${requestedPort}-${scanEnd}.`
    );
  }
  console.log(
    "[keystone:scene:studio] Override port: KEYSTONE_PORT=3115 pnpm -C apps/keystone keystone:scene:studio"
  );
}

function printLockHint(portResolution) {
  console.error(
    "[keystone:scene:studio] Another Next.js dev instance is holding the .next dev lock."
  );
  if (portResolution.requestedPort === DEFAULT_PORT) {
    console.error(
      `[keystone:scene:studio] If Keystone is already running, reuse http://localhost:${DEFAULT_PORT}.`
    );
  }
  console.error("[keystone:scene:studio] Otherwise stop existing Next.js dev processes and retry.");
}

async function main() {
  const passthroughArgs = process.argv.slice(2);
  const portResolution = await resolvePort();
  printBanner(portResolution);

  const env = {
    ...process.env,
    PORT: String(portResolution.selectedPort),
    KEYSTONE_PORT: String(portResolution.selectedPort)
  };

  const commandArgs = [
    "exec",
    "next",
    "dev",
    "-p",
    String(portResolution.selectedPort),
    ...passthroughArgs
  ];
  const child = spawn("pnpm", commandArgs, {
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

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }

    const normalized = combined.toLowerCase();
    const lockDetected = normalized.includes("unable to acquire lock");
    if ((code ?? 1) !== 0 && lockDetected) {
      printLockHint(portResolution);
    }

    process.exit(code ?? 1);
  });
}

void main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`[keystone:scene:studio] ${message}`);
  process.exit(1);
});
