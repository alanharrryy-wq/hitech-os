// PRISMA_CHART_LAB_V31_RUNTIME_SMOKE_FIX
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(__dirname, "..");
const terminalRoot = path.resolve(appRoot, "../../..");
const timestamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "_");
const evidenceRoot = "F:\\descargasf";
const trashRoot = path.join("F:\\Trash-old", `chart_lab_v31_runtime_fix_${timestamp}`);
const logPath = path.join(evidenceRoot, `chart_lab_dev_smoke_${timestamp}.log`);
const controlLogPath = path.join(evidenceRoot, `chart_lab_dev_smoke_${timestamp}.control.log`);
const reportPath = path.join(evidenceRoot, `chart_lab_dev_smoke_${timestamp}.json`);
const manifestPath = path.join(trashRoot, "MANIFEST.json");
const targetUrl = "http://127.0.0.1:3000/";
const timeoutMs = 120_000;
const launcherPath = path.join(evidenceRoot, `chart_lab_dev_smoke_${timestamp}.cmd`);
const movedItems = [];
const killedPids = [];

fs.mkdirSync(evidenceRoot, { recursive: true });
fs.mkdirSync(trashRoot, { recursive: true });

function appendLog(message) {
  fs.appendFileSync(controlLogPath, `${message}\n`, "utf8");
}

function isInside(parent, candidate) {
  const relative = path.relative(parent, candidate);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function collectDirectoryStats(target) {
  const stats = fs.lstatSync(target);
  if (!stats.isDirectory()) {
    return { sizeBytes: stats.size, fileCount: 1, sha256: null };
  }
  let sizeBytes = 0;
  let fileCount = 0;
  const stack = [target];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(fullPath);
      } else if (entry.isFile()) {
        const fileStats = fs.lstatSync(fullPath);
        sizeBytes += fileStats.size;
        fileCount += 1;
      }
    }
  }
  return { sizeBytes, fileCount, sha256: null };
}

function moveGeneratedItem(relativePath, reason) {
  const source = path.resolve(appRoot, relativePath);
  if (!isInside(appRoot, source)) throw new Error(`Refusing to move path outside app root: ${source}`);
  if (!fs.existsSync(source)) return;
  const trashPath = path.join(trashRoot, relativePath);
  fs.mkdirSync(path.dirname(trashPath), { recursive: true });
  const stats = collectDirectoryStats(source);
  fs.renameSync(source, trashPath);
  movedItems.push({
    originalPath: source,
    trashPath,
    reason,
    sha256: stats.sha256,
    sizeBytes: stats.sizeBytes,
    fileCount: stats.fileCount,
    movedAt: new Date().toISOString()
  });
  appendLog(`[trash-old] moved ${source} -> ${trashPath}`);
}

function writeManifest() {
  fs.writeFileSync(manifestPath, JSON.stringify(movedItems, null, 2), "utf8");
}

function findPort3000Pids() {
  const result = spawnSync("netstat", ["-ano", "-p", "tcp"], { encoding: "utf8" });
  if (result.status !== 0) return [];
  const pids = new Set();
  for (const line of result.stdout.split(/\r?\n/)) {
    if (!line.includes(":3000")) continue;
    const parts = line.trim().split(/\s+/);
    const local = parts[1] ?? "";
    const state = parts[3] ?? "";
    const pid = Number(parts[4]);
    if ((local.startsWith("127.0.0.1:3000") || local.startsWith("0.0.0.0:3000") || local.startsWith("[::1]:3000")) && state === "LISTENING" && Number.isInteger(pid)) {
      pids.add(pid);
    }
  }
  return [...pids];
}

function killPort3000Listeners() {
  for (const pid of findPort3000Pids()) {
    appendLog(`[port] stopping existing listener on 3000 pid=${pid}`);
    const result = spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], { encoding: "utf8" });
    killedPids.push({ pid, exitCode: result.status, stdout: result.stdout, stderr: result.stderr });
  }
}

function requestHome() {
  return new Promise((resolve) => {
    const req = http.get(targetUrl, { timeout: 5000 }, (res) => {
      let body = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => {
        body += chunk;
      });
      res.on("end", () => {
        resolve({ ok: true, statusCode: res.statusCode ?? 0, body });
      });
    });
    req.on("timeout", () => {
      req.destroy(new Error("HTTP request timed out"));
    });
    req.on("error", (error) => {
      resolve({ ok: false, statusCode: 0, body: "", error: error instanceof Error ? error.message : String(error) });
    });
  });
}

async function waitForSmoke() {
  const startedAt = Date.now();
  let lastResult = null;
  while (Date.now() - startedAt < timeoutMs) {
    lastResult = await requestHome();
    if (lastResult.ok && lastResult.statusCode === 200 && lastResult.body.includes("PRISMA Chart Lab")) return lastResult;
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
  const message = lastResult?.error ?? `Last HTTP status: ${lastResult?.statusCode ?? "none"}`;
  throw new Error(`Timed out waiting for ${targetUrl}. ${message}`);
}

function writeReport(report) {
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf8");
}

function writeLauncher() {
  const lines = [
    "@echo off",
    `cd /d "${terminalRoot}"`,
    `pnpm.cmd -C "${terminalRoot}" chart-lab:dev >> "${logPath}" 2>&1`
  ];
  fs.writeFileSync(launcherPath, `${lines.join("\r\n")}\r\n`, "utf8");
}

async function main() {
  let child = null;
  try {
    appendLog(`[start] PRISMA Chart Lab dev smoke ${timestamp}`);
    appendLog(`[root] terminal=${terminalRoot}`);
    killPort3000Listeners();
    moveGeneratedItem(".next", "Generated Next.js cache/build output; moved before local dev smoke to clear stale SST/Turbopack state.");
    moveGeneratedItem(".turbo", "Generated Turbo cache; moved before local dev smoke to clear stale task database state.");
    moveGeneratedItem("out", "Generated static export output; not used by local dev and can be regenerated by cf:build/cf:verify.");
    moveGeneratedItem(".tmp-visual-qa", "Temporary visual QA staging directory; out of scope for code-only local dev smoke.");
    writeManifest();

    writeLauncher();
    child = spawn("cmd.exe", ["/d", "/c", launcherPath], {
      cwd: terminalRoot,
      detached: true,
      stdio: "ignore",
      windowsHide: true
    });
    child.unref();
    appendLog(`[server] spawned pnpm chart-lab:dev wrapper pid=${child.pid}`);

    const smoke = await waitForSmoke();
    const listeners = findPort3000Pids();
    const report = {
      status: "PASS",
      url: targetUrl,
      httpStatus: smoke.statusCode,
      containsPrismaChartLab: smoke.body.includes("PRISMA Chart Lab"),
      spawnedPid: child?.pid ?? null,
      listeningPids: listeners,
      killedPids,
      logPath,
      controlLogPath,
      launcherPath,
      reportPath,
      trashManifestPath: manifestPath,
      movedItems,
      serverLeftRunning: listeners.length > 0,
      completedAt: new Date().toISOString()
    };
    writeReport(report);
    appendLog(`[pass] HTTP ${smoke.statusCode}; PRISMA Chart Lab token present; server left running.`);
    process.exit(0);
  } catch (error) {
    appendLog(`[fail] ${error instanceof Error ? error.stack ?? error.message : String(error)}`);
    for (const pid of findPort3000Pids()) {
      spawnSync("taskkill", ["/PID", String(pid), "/T", "/F"], { encoding: "utf8" });
    }
    const report = {
      status: "FAIL",
      url: targetUrl,
      error: error instanceof Error ? error.message : String(error),
      spawnedPid: child?.pid ?? null,
      killedPids,
      logPath,
      controlLogPath,
      launcherPath,
      reportPath,
      trashManifestPath: manifestPath,
      movedItems,
      serverLeftRunning: false,
      completedAt: new Date().toISOString()
    };
    writeReport(report);
    process.exit(1);
  }
}

main();
