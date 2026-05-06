import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();

function fail(message) {
  console.error(`[PWA FAIL] ${message}`);
  process.exit(1);
}

function readJson(rel) {
  const full = path.join(root, rel);
  if (!existsSync(full)) fail(`Missing ${rel}`);
  try {
    return JSON.parse(readFileSync(full, "utf8"));
  } catch (error) {
    fail(`Invalid JSON in ${rel}: ${error.message}`);
  }
}

function assert(condition, message) {
  if (!condition) fail(message);
}

const manifest = readJson("public/manifest.webmanifest");

for (const field of ["name", "short_name", "start_url", "scope", "display", "icons"]) {
  assert(Boolean(manifest[field]), `manifest.webmanifest missing ${field}`);
}

assert(manifest.name === "PRISMA App", "manifest name must be PRISMA App");
assert(manifest.short_name === "PRISMA", "manifest short_name must be PRISMA");
assert(manifest.start_url === "/prisma-app", "manifest start_url must be /prisma-app");
assert(manifest.display === "standalone", "manifest display must be standalone");
assert(Array.isArray(manifest.icons) && manifest.icons.length >= 2, "manifest must define at least two icons");

for (const icon of manifest.icons) {
  assert(icon.src, "manifest icon missing src");
  const local = icon.src.startsWith("/") ? icon.src.slice(1) : icon.src;
  const full = path.join(root, "public", local);
  assert(existsSync(full), `manifest icon path not found: ${icon.src}`);
  assert(statSync(full).size > 100, `manifest icon file is too small: ${icon.src}`);
}

const assetlinks = readJson("public/.well-known/assetlinks.template.json");
assert(Array.isArray(assetlinks), "assetlinks template must be an array");
assert(assetlinks.length > 0, "assetlinks template must include at least one statement");
assert(
  assetlinks[0]?.relation?.includes("delegate_permission/common.handle_all_urls"),
  "assetlinks template must include delegate_permission/common.handle_all_urls",
);
assert(
  assetlinks[0]?.target?.namespace === "android_app",
  "assetlinks template target namespace must be android_app",
);

const layout = readFileSync(path.join(root, "app/layout.tsx"), "utf8");
assert(layout.includes("manifest: \"/manifest.webmanifest\""), "layout metadata must reference manifest.webmanifest");
assert(layout.includes("themeColor"), "layout viewport must declare themeColor");
assert(layout.includes("PRISMA App"), "layout metadata must mention PRISMA App");

console.log("[PWA OK] PRISMA Mobile PWA readiness files are present and coherent.");
