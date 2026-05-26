#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.env.PRISMA_ROOT || process.argv[2] || "F:\\repos\\hitech-os\\apps\\terminal-de-venta-system";
const app = path.join(root, "products", "tablet", "app");
const sourceDir = process.env.PRISMA_TABLET_VISUAL_SOURCE_DIR || path.join(root, "docs", "design", "tablet-light-visual-preset-engine");
const publicSourceDir = path.join(app, "public", "visual-os", "tablet-light-visual-preset-engine");
const checks = [];
const check = (name, ok, detail = "") => checks.push({ name, ok: Boolean(ok), detail });
const fileExists = (file) => { try { return fs.existsSync(file) && fs.statSync(file).isFile(); } catch { return false; } };
const dirExists = (file) => { try { return fs.existsSync(file) && fs.statSync(file).isDirectory(); } catch { return false; } };
const read = (file) => fs.readFileSync(file, "utf8");
const parseJson = (file) => { try { return { ok: true, value: JSON.parse(read(file)), detail: "parse ok" }; } catch (error) { return { ok: false, value: null, detail: error?.message || String(error) }; } };

check("tablet_app_exists", dirExists(app), app);
check("background_route_exists", fileExists(path.join(app, "app", "visual-os", "tablet-background-gallery", "page.tsx")), "app/visual-os/tablet-background-gallery/page.tsx");
check("pos_not_targeted_by_v4", fileExists(path.join(app, "app", "pos", "page.tsx")), "POS page exists but V4 does not modify it");
const candidates = [sourceDir, publicSourceDir].filter(dirExists);
check("source_candidates_available", candidates.length > 0, candidates.join(" | "));

const required = [
  "tablet-codex-background-gallery-smoke-test.html",
  "prisma-tablet-background-atmospheric-v4.css",
  "prisma-tablet-background-atmospheric-v4.js",
  "tablet-background-presets.atmospheric-v4.json",
  "tablet-background-presets.atmospheric-v4.patch.json",
  "PRISMA_TABLET_ATMOSPHERIC_BACKGROUNDS_V4.md",
  "assets/backgrounds/tablet-soft-gray-clouds.svg",
  "assets/backgrounds/obsidian-cloud-motion.svg",
  "assets/backgrounds/storm-glass-horizon.svg",
  "assets/backgrounds/aurora-slate-veil.svg"
];
for (const name of required) {
  const found = candidates.map(dir => path.join(dir, name)).find(fileExists);
  check(`v4_file_exists:${name}`, Boolean(found), found || "missing");
}

const jsonPath = candidates.map(dir => path.join(dir, "tablet-background-presets.atmospheric-v4.json")).find(fileExists);
const parsed = jsonPath ? parseJson(jsonPath) : { ok: false, value: null, detail: "missing" };
check("v4_json_parse", parsed.ok, parsed.detail);
if (parsed.ok) {
  const presets = parsed.value.presets || [];
  check("v4_has_four_presets", presets.length === 4, String(presets.length));
  check("v4_light_default_is_soft_gray_clouds", parsed.value.policy?.lightPresetId === "tablet-soft-gray-clouds", parsed.value.policy?.lightPresetId || "missing");
  const dark = presets.filter(p => String(p.tone).includes("dark"));
  check("v4_has_three_dark_showcase_presets", dark.length === 3, String(dark.length));
  check("v4_dark_showcase_not_default", dark.every(p => p.darkShowcase === true && p.applyDefault === false), "dark presets tagged darkShowcase=true and applyDefault=false");
  check("v4_pos_guardrail", parsed.value.policy?.doNotTouchPos === true, "doNotTouchPos true");
  check("v4_auto_update_guardrail", parsed.value.policy?.sourceUpdatesAutoReflectInRoute === true, "sourceUpdatesAutoReflectInRoute true");
}

const htmlPath = candidates.map(dir => path.join(dir, "tablet-codex-background-gallery-smoke-test.html")).find(fileExists);
const cssPath = candidates.map(dir => path.join(dir, "prisma-tablet-background-atmospheric-v4.css")).find(fileExists);
const jsPath = candidates.map(dir => path.join(dir, "prisma-tablet-background-atmospheric-v4.js")).find(fileExists);
const corpus = [htmlPath, cssPath, jsPath].filter(Boolean).map(read).join("\n\n");
check("v4_reduced_motion_present", /prefers-reduced-motion\s*:\s*reduce/i.test(corpus), "prefers-reduced-motion: reduce");
check("v4_touch_target_48px_present", /(?:min-height|min-width)\s*:\s*48px|48px/i.test(corpus), "48px touch target concept");
check("v4_uses_image_assets_not_only_gradients", /\.svg/i.test(corpus) && /--atm-image/i.test(corpus), "SVG image assets + CSS layers detected");
check("v4_dark_terms_have_showcase_guardrail", /dark showcase/i.test(corpus) || /Showcase only/i.test(corpus), "dark showcase guardrail visible");

const routeText = fileExists(path.join(app, "app", "visual-os", "tablet-background-gallery", "page.tsx")) ? read(path.join(app, "app", "visual-os", "tablet-background-gallery", "page.tsx")) : "";
check("background_route_requires_v4_json", routeText.includes("tablet-background-presets.atmospheric-v4.json"), "route requiredJsonFiles includes V4 JSON");

const failed = checks.filter(c => !c.ok);
const report = { generated_at: new Date().toISOString(), root, app, sourceDir, publicSourceDir, checks, status: failed.length ? "FAIL" : "PASS" };
console.log(JSON.stringify(report, null, 2));
if (failed.length) process.exit(1);
