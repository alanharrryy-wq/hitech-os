import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { appRoot, ensureDir, fail, pass, run, terminalRoot, writeEvidence } from "./chart-lab-script-utils.mjs";

const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
const packRoot = path.join(terminalRoot, "tools", "_local", "evidence", "chart-lab", `handoff-pack-${timestamp}`);
const payloadRoot = path.join(packRoot, "payload");
const includePaths = [
  "products/chart-lab/app/app",
  "products/chart-lab/app/src",
  "products/chart-lab/app/scripts",
  "products/chart-lab/app/docs",
  "products/chart-lab/app/deploy",
  "products/chart-lab/app/package.json",
  "products/chart-lab/app/next.config.mjs",
  "products/chart-lab/app/wrangler.jsonc",
  "products/chart-lab/app/README.md",
  "products/chart-lab/app/PROMOTION.md",
  "products/chart-lab/app/NEW_CHART_TEMPLATE.md",
  "docs/prisma",
  "shared/prisma-charts"
];
const excludeParts = new Set(["node_modules", ".next", "out", ".turbo"]);
const excludeNames = new Set([".env", ".env.local", ".env.production", ".env.development"]);
const keywords = [
  "ChartControlDeck",
  "runtimeControls",
  "chartControls",
  "VisualTuningPassport",
  "CopyCurrentConfig",
  "promotionManifest",
  "SurfaceTransport",
  "Cloudflare",
  "cloudflared",
  "wrangler",
  "tunnel",
  "public-safe",
  "no-leak",
  "source map",
  "state gallery",
  "human intent"
];

function shouldSkip(source) {
  const parts = source.split(path.sep);
  return parts.some((part) => excludeParts.has(part)) || excludeNames.has(path.basename(source));
}

function copyRecursive(source, target) {
  if (!fs.existsSync(source) || shouldSkip(source)) return;
  const stat = fs.statSync(source);
  if (stat.isDirectory()) {
    ensureDir(target);
    for (const entry of fs.readdirSync(source)) copyRecursive(path.join(source, entry), path.join(target, entry));
  } else {
    ensureDir(path.dirname(target));
    fs.copyFileSync(source, target);
  }
}

function walkFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(absolute));
    else files.push(absolute);
  }
  return files;
}

ensureDir(payloadRoot);
for (const rel of includePaths) {
  copyRecursive(path.join(terminalRoot, rel), path.join(payloadRoot, rel));
}

const files = walkFiles(payloadRoot);
const hashes = files.map((file) => ({
  path: path.relative(payloadRoot, file).replace(/\\/g, "/"),
  sha256: crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex")
}));

const warnings = [];
for (const required of [
  "products/chart-lab/app/src/prisma-charts/maps/chart-lab-maps.ts",
  "products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts",
  "products/chart-lab/app/deploy/cloudflare-pages.json",
  "products/chart-lab/app/deploy/cloudflare-tunnel/prisma-chart-lab.tunnel.template.yml",
  "products/chart-lab/app/scripts/promote-chart.mjs"
]) {
  if (!fs.existsSync(path.join(payloadRoot, required))) warnings.push(`missing:${required}`);
}

const manifest = {
  schemaVersion: "1.0",
  generatedAt: new Date().toISOString(),
  canonicalZipRoot: "repo/apps/terminal-de-venta-system",
  includePaths,
  excluded: ["node_modules", ".next", "out", ".env files", "build outputs"],
  keywords,
  warnings,
  fileCount: files.length,
  hashes
};
fs.writeFileSync(path.join(packRoot, "HANDOFF_PACK_MANIFEST.json"), JSON.stringify(manifest, null, 2));
fs.writeFileSync(path.join(packRoot, "README.md"), "# PRISMA Chart Lab Handoff Pack\n\nThis pack contains Chart Lab code, governance maps, controls, Cloudflare/tunnel config templates, promotion tooling, docs, and hashes.\n");

const zipPath = path.join(terminalRoot, "tools", "_local", "evidence", "chart-lab", `prisma-chart-lab-handoff-${timestamp}.zip`);
const zip = run("powershell", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", `Compress-Archive -Path '${packRoot}\\*' -DestinationPath '${zipPath}' -Force`]);
writeEvidence("handoff-pack-latest-report.json", { packRoot, zipPath, warnings, zipStatus: zip.status, stdout: zip.stdout, stderr: zip.stderr });
if (zip.status === 0) pass(`handoff ZIP created: ${zipPath}`);
else fail(`handoff ZIP creation failed: ${zip.stderr}`);

if (warnings.length) {
  for (const warning of warnings) console.warn(`[PRISMA Chart Lab] WARN: ${warning}`);
}

pass(`handoff pack root: ${packRoot}`);
