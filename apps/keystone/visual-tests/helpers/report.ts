import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import type { PixelDiffResult } from "./diff.js";
import type { VisualSceneDefinition } from "./scene-manifest.js";

export type ChangeCategory = "NO_CHANGE" | "SMALL_CHANGE" | "SIGNIFICANT_CHANGE";
export type ChangeBand = "none" | "small" | "moderate" | "significant";

export interface SceneImprovementReport {
  readonly id: string;
  readonly runId: string;
  readonly route: string;
  readonly query: string;
  readonly viewport: VisualSceneDefinition["viewport"];
  readonly url: string;
  readonly layers: string;
  readonly layerProfile: string;
  readonly motion: string;
  readonly timestamp: string;
  readonly environment: {
    readonly node: string;
    readonly platform: string;
    readonly browser: string;
    readonly baseUrl: string;
  };
  readonly artifactDir: string;
  readonly baselinePath: string;
  readonly beforePath: string;
  readonly afterPath: string;
  readonly diffPath: string;
  readonly category: ChangeCategory;
  readonly changeBand: ChangeBand;
  readonly evidenceScore: number;
  readonly notes: readonly string[];
  readonly diff: PixelDiffResult;
  readonly diagnostics?: {
    readonly unknownTokens: readonly string[];
    readonly sceneReady?: string;
  };
}

export function classifyVisualChange(percentChanged: number): {
  readonly category: ChangeCategory;
  readonly band: ChangeBand;
  readonly evidenceScore: number;
} {
  if (percentChanged === 0) {
    return {
      category: "NO_CHANGE",
      band: "none",
      evidenceScore: 0
    };
  }

  if (percentChanged < 0.5) {
    return {
      category: "SMALL_CHANGE",
      band: "small",
      evidenceScore: 35
    };
  }

  if (percentChanged <= 5) {
    return {
      category: "SIGNIFICANT_CHANGE",
      band: "moderate",
      evidenceScore: 70
    };
  }

  return {
    category: "SIGNIFICANT_CHANGE",
    band: "significant",
    evidenceScore: 90
  };
}

function toPercent(value: number): string {
  return `${value.toFixed(4)}%`;
}

function renderBoundingBox(diff: PixelDiffResult): string {
  if (!diff.changedBoundingBox) {
    return "none";
  }

  const box = diff.changedBoundingBox;
  return `x=${box.x}, y=${box.y}, width=${box.width}, height=${box.height}`;
}

function buildSceneMarkdown(report: SceneImprovementReport): string {
  const lines: string[] = [
    `# UI Improvement Report: ${report.id}`,
    "",
    `- Run ID: \`${report.runId}\``,
    `- Category: \`${report.category}\``,
    `- Change Band: \`${report.changeBand}\``,
    `- Evidence Score: \`${report.evidenceScore}\` / 100`,
    `- Pixel Change: \`${report.diff.changedPixels}\` / \`${report.diff.totalPixels}\` (\`${toPercent(report.diff.percentChanged)}\`)`,
    `- Changed Bounding Box: \`${renderBoundingBox(report.diff)}\``,
    `- Scene URL: \`${report.url}\``,
    `- Route: \`${report.route}\``,
    `- Query: \`${report.query || "(none)"}\``,
    `- Viewport: \`${report.viewport}\` (\`${report.diff.width}x${report.diff.height}\`)`,
    `- Layers: \`${report.layers || "(none)"}\``,
    `- Profile: \`${report.layerProfile || "(none)"}\``,
    `- Motion: \`${report.motion || "(default)"}\``,
    `- Timestamp: \`${report.timestamp}\``,
    `- Environment: node=\`${report.environment.node}\`, platform=\`${report.environment.platform}\`, browser=\`${report.environment.browser}\`, baseURL=\`${report.environment.baseUrl}\``,
    "",
    "## Scorecard",
    "",
    `- Status: **${report.category}**`,
    `- Pixel Diff %: **${toPercent(report.diff.percentChanged)}**`,
    `- Band: **${report.changeBand}**`,
    `- Bounding Box: **${renderBoundingBox(report.diff)}**`,
    "",
    "## Snapshots",
    "",
    "### Before",
    "",
    "![Before](./before.png)",
    "",
    "### After",
    "",
    "![After](./after.png)",
    "",
    "### Diff",
    "",
    "![Diff](./diff.png)"
  ];

  if (report.notes.length > 0) {
    lines.push("", "## Notes", "");
    for (const note of report.notes) {
      lines.push(`- ${note}`);
    }
  }

  return `${lines.join("\n")}\n`;
}

function buildSceneHtml(report: SceneImprovementReport): string {
  const notes = report.notes.map((note) => `<li>${note}</li>`).join("");

  return [
    "<!doctype html>",
    "<html lang=\"en\">",
    "<head>",
    "  <meta charset=\"utf-8\" />",
    `  <title>UI Improvement Report - ${report.id}</title>`,
    "  <style>",
    "    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; margin: 24px; color: #101828; }",
    "    h1, h2 { margin: 0 0 12px; }",
    "    ul { padding-left: 20px; }",
    "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }",
    "    figure { margin: 0; border: 1px solid #d0d5dd; border-radius: 12px; padding: 12px; background: #f8fafc; }",
    "    figcaption { margin-bottom: 8px; font-weight: 600; font-size: 14px; }",
    "    img { width: 100%; height: auto; border-radius: 8px; border: 1px solid #eaecf0; }",
    "    code { background: #f2f4f7; border-radius: 4px; padding: 2px 4px; }",
    "  </style>",
    "</head>",
    "<body>",
    `  <h1>UI Improvement Report: ${report.id}</h1>`,
    "  <ul>",
    `    <li><strong>Run ID:</strong> <code>${report.runId}</code></li>`,
    `    <li><strong>Category:</strong> <code>${report.category}</code></li>`,
    `    <li><strong>Change Band:</strong> <code>${report.changeBand}</code></li>`,
    `    <li><strong>Evidence Score:</strong> <code>${report.evidenceScore}</code> / 100</li>`,
    `    <li><strong>Pixel Change:</strong> <code>${report.diff.changedPixels}</code> / <code>${report.diff.totalPixels}</code> (<code>${toPercent(report.diff.percentChanged)}</code>)</li>`,
    `    <li><strong>Bounding Box:</strong> <code>${renderBoundingBox(report.diff)}</code></li>`,
    `    <li><strong>Scene URL:</strong> <code>${report.url}</code></li>`,
    `    <li><strong>Route:</strong> <code>${report.route}</code></li>`,
    `    <li><strong>Query:</strong> <code>${report.query || "(none)"}</code></li>`,
    `    <li><strong>Viewport:</strong> <code>${report.viewport}</code> (<code>${report.diff.width}x${report.diff.height}</code>)</li>`,
    `    <li><strong>Layers:</strong> <code>${report.layers || "(none)"}</code></li>`,
    `    <li><strong>Profile:</strong> <code>${report.layerProfile || "(none)"}</code></li>`,
    `    <li><strong>Motion:</strong> <code>${report.motion || "(default)"}</code></li>`,
    `    <li><strong>Timestamp:</strong> <code>${report.timestamp}</code></li>`,
    `    <li><strong>Environment:</strong> node=<code>${report.environment.node}</code>, platform=<code>${report.environment.platform}</code>, browser=<code>${report.environment.browser}</code>, baseURL=<code>${report.environment.baseUrl}</code></li>`,
    "  </ul>",
    report.notes.length > 0
      ? `  <h2>Notes</h2><ul>${notes}</ul>`
      : "  <p><em>No additional notes.</em></p>",
    "  <h2>Snapshots</h2>",
    "  <div class=\"grid\">",
    "    <figure><figcaption>Before</figcaption><img src=\"./before.png\" alt=\"Before snapshot\" /></figure>",
    "    <figure><figcaption>After</figcaption><img src=\"./after.png\" alt=\"After snapshot\" /></figure>",
    "    <figure><figcaption>Diff</figcaption><img src=\"./diff.png\" alt=\"Pixel diff snapshot\" /></figure>",
    "  </div>",
    "</body>",
    "</html>",
    ""
  ].join("\n");
}

export async function writeSceneReport(sceneDir: string, report: SceneImprovementReport): Promise<void> {
  await mkdir(sceneDir, { recursive: true });

  const markdownPath = path.join(sceneDir, "report.md");
  const htmlPath = path.join(sceneDir, "report.html");
  const jsonPath = path.join(sceneDir, "report.json");

  await Promise.all([
    writeFile(markdownPath, buildSceneMarkdown(report), "utf8"),
    writeFile(htmlPath, buildSceneHtml(report), "utf8"),
    writeFile(jsonPath, `${JSON.stringify(report, null, 2)}\n`, "utf8")
  ]);
}

export async function writeSummaryReport(
  rootDir: string,
  reports: readonly SceneImprovementReport[]
): Promise<void> {
  await mkdir(rootDir, { recursive: true });

  const rows = reports
    .map(
      (report) =>
        `| ${report.id} | ${report.category} | ${report.changeBand} | ${toPercent(report.diff.percentChanged)} | ${report.evidenceScore} | [report](./scenes/${report.id}/${report.runId}/report.md) |`
    )
    .join("\n");

  const markdown = [
    "# Keystone Scene Studio - Improvement Index",
    "",
    `- Generated: \`${new Date().toISOString()}\``,
    `- Scenes evaluated: \`${reports.length}\``,
    "",
    "| Scene | Category | Band | Pixel Change | Evidence Score | Report |",
    "| --- | --- | --- | --- | --- | --- |",
    rows,
    ""
  ].join("\n");

  const htmlRows = reports
    .map(
      (report) =>
        `<tr><td>${report.id}</td><td>${report.category}</td><td>${report.changeBand}</td><td>${toPercent(report.diff.percentChanged)}</td><td>${report.evidenceScore}</td><td><a href="./scenes/${report.id}/${report.runId}/report.html">report</a></td></tr>`
    )
    .join("");

  const html = [
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
    `  <p>Scenes evaluated: <code>${reports.length}</code></p>`,
    "  <table>",
    "    <thead><tr><th>Scene</th><th>Category</th><th>Band</th><th>Pixel Change</th><th>Evidence Score</th><th>Report</th></tr></thead>",
    `    <tbody>${htmlRows}</tbody>`,
    "  </table>",
    "</body>",
    "</html>",
    ""
  ].join("\n");

  await Promise.all([
    writeFile(path.join(rootDir, "index.md"), markdown, "utf8"),
    writeFile(path.join(rootDir, "index.html"), html, "utf8"),
    writeFile(path.join(rootDir, "summary.md"), markdown, "utf8"),
    writeFile(path.join(rootDir, "summary.html"), html, "utf8")
  ]);
}
