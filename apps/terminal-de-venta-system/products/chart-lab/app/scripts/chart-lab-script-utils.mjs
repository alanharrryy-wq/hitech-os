import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

export const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const terminalRoot = path.resolve(appRoot, "..", "..", "..");
export const repoRoot = path.resolve(terminalRoot, "..", "..");
export const evidenceRoot = path.join(terminalRoot, "tools", "_local", "evidence", "chart-lab");

export function rel(...parts) {
  return path.join(appRoot, ...parts);
}

export function terminalRel(...parts) {
  return path.join(terminalRoot, ...parts);
}

export function read(relativePath, root = appRoot) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

export function readJson(relativePath, root = appRoot) {
  return JSON.parse(read(relativePath, root));
}

export function exists(relativePath, root = appRoot) {
  return fs.existsSync(path.join(root, relativePath));
}

export function ensureDir(target) {
  fs.mkdirSync(target, { recursive: true });
}

export function writeEvidence(name, data) {
  ensureDir(evidenceRoot);
  const outPath = path.join(evidenceRoot, name);
  fs.writeFileSync(outPath, typeof data === "string" ? data : JSON.stringify(data, null, 2));
  return outPath;
}

export function pass(message) {
  console.log(`[PRISMA Chart Lab] PASS: ${message}`);
}

export function warn(message) {
  console.warn(`[PRISMA Chart Lab] WARN: ${message}`);
}

export function fail(message) {
  console.error(`[PRISMA Chart Lab] FAIL: ${message}`);
  process.exitCode = 1;
}

export function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: options.cwd ?? appRoot,
    env: { ...process.env, ...(options.env ?? {}) },
    encoding: "utf8",
    shell: process.platform === "win32",
    stdio: options.stdio ?? "pipe"
  });
}

export function chartOpsIds() {
  const registry = read("src/prisma-charts/chart-lab-registry.tsx");
  const match = registry.match(/export const chartOpsChartIds = \[([\s\S]*?)\] as const;/);
  if (!match) return [];
  return [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]);
}

export function scriptHas(relativePath, needles) {
  const content = read(relativePath);
  return needles.every((needle) => content.includes(needle));
}

export function parseArgs(argv = process.argv.slice(2)) {
  const parsed = {};
  for (const raw of argv) {
    if (!raw.startsWith("--")) continue;
    const [key, value] = raw.slice(2).split("=");
    parsed[key] = value ?? true;
  }
  return parsed;
}
