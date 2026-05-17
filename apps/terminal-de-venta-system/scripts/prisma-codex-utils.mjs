import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

export const terminalRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const repoRoot = path.resolve(terminalRoot, "..", "..");
export const reportRoot = process.env.PRISMA_REPORT_ROOT || "F:\\descargasf";

export function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "").replace("T", "_");
}

export function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

export function toWindowsPath(value) {
  return path.resolve(value);
}

export function sha256(filePath) {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

export function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export function writeJson(filePath, payload) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  return filePath;
}

export function writeText(filePath, text) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, text, "utf8");
  return filePath;
}

export function reportPaths(prefix) {
  ensureDir(reportRoot);
  const stamp = timestamp();
  return {
    json: path.join(reportRoot, `${prefix}_${stamp}.json`),
    md: path.join(reportRoot, `${prefix}_${stamp}.md`)
  };
}

export function statusRank(statuses) {
  if (statuses.includes("FAIL")) return "FAIL";
  if (statuses.includes("WARN")) return "WARN";
  if (statuses.includes("SKIP")) return "SKIP";
  return "PASS";
}

export function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: options.cwd || terminalRoot,
    encoding: "utf8",
    shell: false,
    env: { ...process.env, ...(options.env || {}) }
  });
}

export function zipDirectory(sourceDir, zipPath) {
  ensureDir(path.dirname(zipPath));
  const source = sourceDir.replace(/'/g, "''");
  const destination = zipPath.replace(/'/g, "''");
  const command = [
    "$ErrorActionPreference='Stop';",
    `$source='${source}';`,
    `$destination='${destination}';`,
    "$items=Join-Path -Path $source -ChildPath '*';",
    "Compress-Archive -Path $items -DestinationPath $destination -Force;"
  ].join(" ");
  const result = run("powershell", ["-NoProfile", "-Command", command]);
  if (result.status !== 0) {
    throw new Error(`Compress-Archive failed: ${result.stderr || result.stdout}`);
  }
  return zipPath;
}

export function walkFiles(root, options = {}) {
  const files = [];
  const skip = options.skip || [/\\node_modules\\/i, /\\.next\\/i, /\\dist\\/i, /\\out\\/i, /\\coverage\\/i];
  const allowExt = options.allowExt || null;
  function walk(current) {
    if (!fs.existsSync(current)) return;
    const normalized = `${current}${path.sep}`;
    if (skip.some((pattern) => pattern.test(normalized))) return;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) walk(absolute);
      else if (!allowExt || allowExt.includes(path.extname(entry.name).toLowerCase())) files.push(absolute);
    }
  }
  walk(root);
  return files;
}

export function latestManifest(prefix) {
  if (!fs.existsSync(reportRoot)) return null;
  const candidates = fs.readdirSync(reportRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && entry.name.startsWith(prefix))
    .map((entry) => path.join(reportRoot, entry.name, "backup-manifest.json"))
    .filter((entryPath) => fs.existsSync(entryPath))
    .sort();
  return candidates.at(-1) || null;
}
