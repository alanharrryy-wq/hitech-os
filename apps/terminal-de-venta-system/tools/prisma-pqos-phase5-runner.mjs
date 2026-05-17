import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { runPhase5All, PHASE5_TITLE } from "../quality/gates/_phase5_release_operator_readiness_common.mjs";

const OUT_DIR = "F:/descargasf";
const LF = String.fromCharCode(10);

function stamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + LF, "utf8");
}

function escapeHtml(text) {
  return String(text).replace(/[&<>]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]));
}

function markdownReport(summary) {
  const lines = [];
  lines.push(`# ${PHASE5_TITLE}`);
  lines.push("");
  lines.push(`Generated: ${summary.timestamp}`);
  lines.push(`Root: ${summary.root}`);
  lines.push(`Status: ${summary.status}`);
  lines.push("");
  lines.push("## Gates");
  lines.push("");
  lines.push("| Gate | Status | Blockers | Warnings |");
  lines.push("| --- | --- | ---: | ---: |");
  for (const result of summary.results) {
    lines.push(`| ${result.id} | ${result.status} | ${result.blockers.length} | ${result.warnings.length} |`);
  }
  lines.push("");
  for (const result of summary.results) {
    lines.push(`## ${result.id} ${result.title}`);
    lines.push("");
    lines.push(`Status: ${result.status}`);
    lines.push("");
    if (result.blockers.length) {
      lines.push("### Blockers");
      for (const item of result.blockers) lines.push(`- ${item}`);
      lines.push("");
    }
    if (result.warnings.length) {
      lines.push("### Warnings");
      for (const item of result.warnings) lines.push(`- ${item}`);
      lines.push("");
    }
    if (result.evidence.length) {
      lines.push("### Evidence");
      for (const item of result.evidence) lines.push(`- ${item}`);
      lines.push("");
    }
  }
  return lines.join(LF) + LF;
}

function htmlReport(summary) {
  const rows = summary.results
    .map((r) => `<tr><td>${escapeHtml(r.id)}</td><td>${escapeHtml(r.status)}</td><td>${r.blockers.length}</td><td>${r.warnings.length}</td></tr>`)
    .join(LF);
  return `<!doctype html><meta charset="utf-8"><title>${escapeHtml(PHASE5_TITLE)}</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:#0b0d10;color:#e8edf5;padding:24px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #303744;padding:8px}</style><h1>${escapeHtml(PHASE5_TITLE)}</h1><p>Status: <strong>${escapeHtml(summary.status)}</strong></p><p>Root: ${escapeHtml(summary.root)}</p><table><thead><tr><th>Gate</th><th>Status</th><th>Blockers</th><th>Warnings</th></tr></thead><tbody>${rows}</tbody></table><pre>${escapeHtml(JSON.stringify(summary, null, 2))}</pre>`;
}

function psQuote(value) {
  return String(value).replaceAll("'", "''");
}

function compress(reportDir, zipPath) {
  const script = `
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$source = '${psQuote(reportDir)}'
$dest = '${psQuote(zipPath)}'
if (-not (Test-Path -LiteralPath $source)) { throw "Report directory does not exist: $source" }
if (Test-Path -LiteralPath $dest) { Remove-Item -LiteralPath $dest -Force }
[System.IO.Compression.ZipFile]::CreateFromDirectory($source, $dest)
if (-not (Test-Path -LiteralPath $dest)) { throw "Zip was not created: $dest" }
`;
  const proc = spawnSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], { encoding: "utf8" });
  if (proc.status !== 0 || !fs.existsSync(zipPath)) {
    return { ok: false, stdout: proc.stdout || "", stderr: proc.stderr || `ZIP missing after compression: ${zipPath}`, status: proc.status };
  }
  return { ok: true, stdout: proc.stdout || "", stderr: proc.stderr || "", status: proc.status };
}

const root = process.cwd();
const runStamp = stamp();
ensureDir(OUT_DIR);
const reportDir = path.join(OUT_DIR, `PRISMA_PQOS_PHASE5_RELEASE_OPERATOR_READINESS_${runStamp}`);
ensureDir(reportDir);

try {
  const results = await runPhase5All({ root });
  const blockers = results.flatMap((result) => result.blockers.map((item) => `${result.id}: ${item}`));
  const warnings = results.flatMap((result) => result.warnings.map((item) => `${result.id}: ${item}`));
  const summary = {
    name: PHASE5_TITLE,
    status: blockers.length ? "BLOCKED" : warnings.length ? "WARN" : "PASS",
    timestamp: new Date().toISOString(),
    root,
    blockers,
    warnings,
    results,
    reportDir,
  };

  writeJson(path.join(reportDir, "summary.json"), summary);
  fs.writeFileSync(path.join(reportDir, "phase5-report.md"), markdownReport(summary), "utf8");
  fs.writeFileSync(path.join(reportDir, "phase5-report.html"), htmlReport(summary), "utf8");

  const zipPath = path.join(OUT_DIR, `PRISMA_PQOS_PHASE5_RELEASE_OPERATOR_READINESS_${runStamp}_RESULT.zip`);
  const latestPath = path.join(OUT_DIR, "PRISMA_PQOS_PHASE5_RELEASE_OPERATOR_READINESS_latest_RESULT.zip");
  const zipResult = compress(reportDir, zipPath);

  summary.zipPath = zipPath;
  summary.latestZipPath = latestPath;
  summary.zipCreated = zipResult.ok;
  summary.zipError = zipResult.ok ? null : zipResult.stderr;
  writeJson(path.join(reportDir, "summary.json"), summary);

  if (!zipResult.ok) {
    console.error(JSON.stringify(summary, null, 2));
    console.error(zipResult.stderr || "ZIP creation failed without stderr.");
    process.exit(2);
  }

  fs.copyFileSync(zipPath, latestPath);
  console.log(JSON.stringify(summary, null, 2));
  process.exit(blockers.length ? 1 : 0);
} catch (error) {
  const failure = {
    name: PHASE5_TITLE,
    status: "RUNNER_ERROR",
    timestamp: new Date().toISOString(),
    root,
    reportDir,
    error: error?.stack || String(error),
  };
  writeJson(path.join(reportDir, "runner-error.json"), failure);
  console.error(JSON.stringify(failure, null, 2));
  process.exit(2);
}