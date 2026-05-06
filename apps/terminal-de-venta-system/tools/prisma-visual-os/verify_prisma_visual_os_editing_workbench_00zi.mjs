#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const PACKAGE = "PRISMA_VISUAL_OS_EDITING_WORKBENCH_00ZI";
const root = process.cwd();
const requiredFiles = [
  "tools/prisma-visual-os/docs/VISUAL_OS_EDITING_MAP.md",
  "tools/prisma-visual-os/config/visual-os-editing-map.json",
  "tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py",
  "tools/prisma-visual-os/verify_prisma_visual_os_editing_workbench_00zi.mjs"
];
const requiredLanes = ["realtime-api", "tablet-realtime-ui", "tablet-pro-ui", "doctors", "ai-doctor", "gates", "qa", "scoring", "generators", "launchers", "compatibility-shims", "legacy-tolerated"];
const canonicalUrls = ["http://127.0.0.1:3120/", "http://127.0.0.1:3130/", "http://127.0.0.1:3140/", "http://127.0.0.1:4177/health", "http://127.0.0.1:4177/state", "http://127.0.0.1:3120/visual-os/realtime", "http://127.0.0.1:3120/visual-os/pro"];
const legacyUrls = ["http://127.0.0.1:3120/prisma-dark-pos-reference", "http://127.0.0.1:3140/prisma-app"];
const checks = [];
const errors = [];
function exists(rel) { return fs.existsSync(path.join(root, rel)); }
function run(name, args) {
  const result = spawnSync(args[0], args.slice(1), { cwd: root, encoding: "utf8", shell: false, env: { ...process.env, NO_COLOR: "1" }});
  return { name, command: args, ok: result.status === 0, status: result.status, stdoutTail: (result.stdout || "").slice(-2000), stderrTail: (result.stderr || "").slice(-2000) };
}
for (const rel of requiredFiles) {
  const ok = exists(rel);
  checks.push({ name: `file ${rel}`, ok });
  if (!ok) errors.push(`Missing required file: ${rel}`);
}
const docsPath = path.join(root, "tools/prisma-visual-os/docs/VISUAL_OS_EDITING_MAP.md");
if (fs.existsSync(docsPath)) {
  const ok = fs.readFileSync(docsPath, "utf8").includes(PACKAGE);
  checks.push({ name: "docs marker", ok });
  if (!ok) errors.push("Docs missing package marker");
}
const manifestPath = path.join(root, "tools/prisma-visual-os/config/visual-os-editing-map.json");
let manifest = null;
try {
  manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  checks.push({ name: "manifest parses", ok: true });
} catch (err) {
  checks.push({ name: "manifest parses", ok: false, detail: String(err) });
  errors.push(`Manifest does not parse: ${err}`);
}
if (manifest) {
  const laneIds = new Set((manifest.lanes || []).map((lane) => lane.id));
  const canonical = new Set(manifest.canonicalUrls || []);
  const legacy = new Set(manifest.legacyUrls || []);
  for (const lane of requiredLanes) { const ok = laneIds.has(lane); checks.push({ name: `lane ${lane}`, ok }); if (!ok) errors.push(`Missing lane: ${lane}`); }
  for (const url of canonicalUrls) { const ok = canonical.has(url); checks.push({ name: `canonical ${url}`, ok }); if (!ok) errors.push(`Missing canonical URL: ${url}`); }
  for (const url of legacyUrls) { const ok = legacy.has(url) && !canonical.has(url); checks.push({ name: `legacy ${url}`, ok }); if (!legacy.has(url)) errors.push(`Missing legacy URL: ${url}`); if (canonical.has(url)) errors.push(`Legacy URL listed as canonical: ${url}`); }
}
const python = process.env.PYTHON || "python";
const helper = "tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py";
const helperRuns = [
  run("helper verify", [python, helper, "--target-root", root, "--verify"]),
  run("helper list lanes", [python, helper, "--target-root", root, "--list-lanes"]),
  run("helper lane realtime-api", [python, helper, "--target-root", root, "--lane", "realtime-api"]),
  run("helper lane tablet-pro-ui", [python, helper, "--target-root", root, "--lane", "tablet-pro-ui"]),
  run("helper lane compatibility-shims", [python, helper, "--target-root", root, "--lane", "compatibility-shims"])
];
for (const item of helperRuns) { checks.push({ name: item.name, ok: item.ok, status: item.status }); if (!item.ok) errors.push(`${item.name} failed: ${item.stderrTail || item.stdoutTail}`); }
const summary = { ok: errors.length === 0, package: PACKAGE, root, checks, helperRuns, errors };
console.log(JSON.stringify(summary, null, 2));
process.exit(summary.ok ? 0 : 1);
