#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.env.PRISMA_ROOT || process.argv[2] || "F:\\repos\\hitech-os\\apps\\terminal-de-venta-system";
const app = path.join(root, "products", "tablet", "app");
const sourceDir = process.env.PRISMA_TABLET_VISUAL_SOURCE_DIR || path.join(root, "docs", "design", "tablet-light-visual-preset-engine");
const publicSourceDir = path.join(app, "public", "visual-os", "tablet-light-visual-preset-engine");

const checks = [];
function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail });
}
function fileExists(file) {
  try { return fs.existsSync(file) && fs.statSync(file).isFile(); } catch { return false; }
}
function dirExists(file) {
  try { return fs.existsSync(file) && fs.statSync(file).isDirectory(); } catch { return false; }
}
function read(file) {
  return fs.readFileSync(file, "utf8");
}
function parseJson(file) {
  try {
    JSON.parse(read(file));
    return { ok: true, detail: "parse ok" };
  } catch (error) {
    return { ok: false, detail: error?.message || String(error) };
  }
}
function firstExisting(dir, names) {
  for (const name of names) {
    const file = path.join(dir, name);
    if (fileExists(file)) return file;
  }
  return "";
}
function countDarkDominant(text) {
  const hard = [
    /data-theme=["']prisma-dark["']/i,
    /data-prisma-skin=["']dark["']/i,
    /NEXT_PUBLIC_PRISMA_THEME\s*===\s*["']prisma-dark["']/i,
    /background\s*:\s*#0[0-9a-f]{5}/i,
    /background-color\s*:\s*#0[0-9a-f]{5}/i,
    /--.*(?:obsidian|night|dark|graphite|black).*:\s*#0[0-9a-f]{5}/i
  ];
  return hard.filter((regex) => regex.test(text)).map(String);
}

const routeFiles = [
  path.join(app, "app", "visual-os", "_tablet-gallery-runtime.tsx"),
  path.join(app, "app", "visual-os", "tablet-codex-gallery", "page.tsx"),
  path.join(app, "app", "visual-os", "tablet-background-gallery", "page.tsx")
];

check("tablet_app_exists", dirExists(app), app);
check("app_router_layout_exists", fileExists(path.join(app, "app", "layout.tsx")), "app/layout.tsx");
check("visual_os_route_dir_exists", dirExists(path.join(app, "app", "visual-os")), "app/visual-os");
for (const file of routeFiles) {
  check(`route_file_exists:${path.relative(app, file)}`, fileExists(file), file);
}

const sourceCandidates = [sourceDir, publicSourceDir].filter(dirExists);
check("visual_source_dir_available", sourceCandidates.length > 0, sourceCandidates.join(" | "));

const codexHtml = sourceCandidates.map((dir) => firstExisting(dir, ["tablet-codex-glass-gallery-smoke-test.html"])).find(Boolean) || "";
const backgroundHtml = sourceCandidates.map((dir) => firstExisting(dir, ["tablet-codex-background-gallery-smoke-test.html", "background-presets-smoke-test.html"])).find(Boolean) || "";
check("codex_html_source_exists", Boolean(codexHtml), codexHtml || "missing tablet-codex-glass-gallery-smoke-test.html");
check("background_html_source_exists_or_equivalent", Boolean(backgroundHtml), backgroundHtml || "missing background gallery html and background-presets equivalent");

const jsonFiles = [
  "tablet-codex-glass-gallery.demo.json",
  "tablet-background-presets.light.json",
  "tablet-background-presets.light.patch.json",
  "visual-verifier-rules.json",
  "tablet-light-preset.schema.json"
];
for (const name of jsonFiles) {
  const found = sourceCandidates.map((dir) => path.join(dir, name)).find(fileExists);
  if (!found) {
    check(`json_exists:${name}`, false, "missing");
    continue;
  }
  const parsed = parseJson(found);
  check(`json_parse:${name}`, parsed.ok, parsed.detail);
}

const cssSources = [
  ...sourceCandidates.map((dir) => path.join(dir, "prisma-tablet-codex-glass-gallery.css")),
  ...sourceCandidates.map((dir) => path.join(dir, "background-presets-smoke-test.html")),
  ...sourceCandidates.map((dir) => path.join(dir, "prisma-tablet-pearl-grey-mist-v2.css"))
].filter(fileExists);

const reducedMotionHit = cssSources.some((file) => /prefers-reduced-motion\s*:\s*reduce/i.test(read(file)));
check("reduced_motion_rule_present", reducedMotionHit, cssSources.map((file) => path.basename(file)).join(", "));

const touchTargetHit = cssSources.some((file) => /(?:min-height|min-width)\s*:\s*48px|48px/i.test(read(file)));
check("touch_target_48px_concept_present", touchTargetHit, cssSources.map((file) => path.basename(file)).join(", "));

const touchedText = routeFiles.filter(fileExists).map(read).join("\n\n") + "\n\n" + cssSources.map(read).join("\n\n");
const darkDominant = countDarkDominant(touchedText);
check("no_dark_dominant_tokens_introduced", darkDominant.length === 0, darkDominant.join(" | ") || "light-only route wrapper; source dark words are references only");

const posPage = path.join(app, "app", "pos", "page.tsx");
check("pos_productive_page_exists_and_untouched_by_route_verifier", fileExists(posPage), posPage);

const failed = checks.filter((item) => !item.ok);
const report = {
  generated_at: new Date().toISOString(),
  root,
  app,
  sourceDir,
  publicSourceDir,
  checks,
  status: failed.length ? "FAIL" : "PASS"
};

console.log(JSON.stringify(report, null, 2));
if (failed.length) process.exit(1);
