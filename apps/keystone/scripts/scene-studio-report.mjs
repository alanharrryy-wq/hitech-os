import { readdir, readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");
const artifactsRoot = path.join(repoRoot, "artifacts", "keystone-scene-studio");
const scenesRoot = path.join(artifactsRoot, "scenes");

async function safeReadJson(filePath) {
  try {
    const raw = await readFile(filePath, "utf8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function toPercent(value) {
  return `${Number(value).toFixed(4)}%`;
}

async function collectLatestReports() {
  const reports = [];

  let sceneDirs = [];
  try {
    sceneDirs = await readdir(scenesRoot, { withFileTypes: true });
  } catch {
    return reports;
  }

  for (const sceneDir of sceneDirs) {
    if (!sceneDir.isDirectory()) {
      continue;
    }

    const scenePath = path.join(scenesRoot, sceneDir.name);
    const runDirs = (await readdir(scenePath, { withFileTypes: true }))
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .sort((left, right) => right.localeCompare(left));

    const latestRun = runDirs[0];
    if (!latestRun) {
      continue;
    }

    const report = await safeReadJson(path.join(scenePath, latestRun, "report.json"));
    if (report) {
      reports.push(report);
    }
  }

  return reports.sort((left, right) => left.id.localeCompare(right.id));
}

function buildMarkdown(reports) {
  const rows = reports
    .map(
      (report) =>
        `| ${report.id} | ${report.category} | ${report.changeBand} | ${toPercent(report.diff.percentChanged)} | ${report.evidenceScore} | [report](./scenes/${report.id}/${report.runId}/report.md) |`
    )
    .join("\n");

  return [
    "# Keystone Scene Studio - Improvement Index",
    "",
    `- Generated: \`${new Date().toISOString()}\``,
    `- Scenes listed: \`${reports.length}\``,
    "",
    "| Scene | Category | Band | Pixel Change | Evidence Score | Report |",
    "| --- | --- | --- | --- | --- | --- |",
    rows,
    ""
  ].join("\n");
}

function buildHtml(reports) {
  const rows = reports
    .map(
      (report) =>
        `<tr><td>${report.id}</td><td>${report.category}</td><td>${report.changeBand}</td><td>${toPercent(report.diff.percentChanged)}</td><td>${report.evidenceScore}</td><td><a href="./scenes/${report.id}/${report.runId}/report.html">report</a></td></tr>`
    )
    .join("");

  return [
    "<!doctype html>",
    "<html lang=\"en\">",
    "<head>",
    "  <meta charset=\"utf-8\" />",
    "  <title>Keystone Scene Studio - Improvement Index</title>",
    "  <style>",
    "    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; margin: 24px; color: #101828; }",
    "    table { border-collapse: collapse; width: 100%; }",
    "    th, td { border: 1px solid #d0d5dd; padding: 8px; text-align: left; }",
    "    th { background: #f2f4f7; }",
    "  </style>",
    "</head>",
    "<body>",
    "  <h1>Keystone Scene Studio - Improvement Index</h1>",
    `  <p>Generated: <code>${new Date().toISOString()}</code></p>`,
    `  <p>Scenes listed: <code>${reports.length}</code></p>`,
    "  <table>",
    "    <thead><tr><th>Scene</th><th>Category</th><th>Band</th><th>Pixel Change</th><th>Evidence Score</th><th>Report</th></tr></thead>",
    `    <tbody>${rows}</tbody>`,
    "  </table>",
    "</body>",
    "</html>",
    ""
  ].join("\n");
}

async function main() {
  const reports = await collectLatestReports();
  await mkdir(artifactsRoot, { recursive: true });

  const markdown = buildMarkdown(reports);
  const html = buildHtml(reports);

  await Promise.all([
    writeFile(path.join(artifactsRoot, "index.md"), markdown, "utf8"),
    writeFile(path.join(artifactsRoot, "index.html"), html, "utf8"),
    writeFile(path.join(artifactsRoot, "summary.md"), markdown, "utf8"),
    writeFile(path.join(artifactsRoot, "summary.html"), html, "utf8")
  ]);

  process.stdout.write(`Scene report index generated at ${artifactsRoot}\n`);
}

await main();
