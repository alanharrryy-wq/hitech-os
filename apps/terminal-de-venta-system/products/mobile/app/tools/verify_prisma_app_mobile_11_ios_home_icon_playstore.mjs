import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

function fail(message) {
  console.error(`[IOS HOME ICON FAIL] ${message}`);
  process.exit(1);
}

function must(rel) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) fail(`Missing ${rel}`);
  return full;
}

function readText(rel) {
  return fs.readFileSync(must(rel), "utf8");
}

function readJson(rel) {
  try {
    return JSON.parse(readText(rel));
  } catch (error) {
    fail(`Invalid JSON in ${rel}: ${error.message}`);
  }
}

function pngSize(rel) {
  const buffer = fs.readFileSync(must(rel));
  if (buffer.length < 32) fail(`PNG too small: ${rel}`);
  const signature = buffer.subarray(0, 8).toString("hex");
  if (signature !== "89504e470d0a1a0a") fail(`Not a PNG file: ${rel}`);
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function assert(condition, message) {
  if (!condition) fail(message);
}

const icon512 = pngSize("public/icons/prisma_playstore_icon_512.png");
assert(icon512.width === 512 && icon512.height === 512, "prisma_playstore_icon_512.png must be 512x512");

const icon192 = pngSize("public/icons/prisma_playstore_icon_192.png");
assert(icon192.width === 192 && icon192.height === 192, "prisma_playstore_icon_192.png must be 192x192");

const layout = readText("app/layout.tsx");
assert(layout.includes('manifest: "/manifest.webmanifest"'), "layout must keep manifest.webmanifest metadata");
assert(layout.includes('apple: ['), "layout must declare apple touch icons");
assert(layout.includes('/icons/prisma_playstore_icon_512.png'), "layout must reference the Play Store icon 512 PNG");
assert(layout.includes('/icons/prisma_playstore_icon_192.png'), "layout must reference the Play Store icon 192 PNG");
assert(!layout.includes('apple: [{ url: "/icons/prisma-pwa-192.png"'), "layout apple icon must not point to prisma-pwa-192.png");

const manifest = readJson("public/manifest.webmanifest");
assert(Array.isArray(manifest.icons), "manifest icons must be an array");
const iconSources = manifest.icons.map((icon) => icon.src);
assert(iconSources[0] === "/icons/prisma_playstore_icon_192.png", "manifest first icon must be prisma_playstore_icon_192.png");
assert(iconSources[1] === "/icons/prisma_playstore_icon_512.png", "manifest second icon must be prisma_playstore_icon_512.png");
assert(!JSON.stringify(manifest).includes("/icons/prisma-pwa-"), "manifest and shortcuts must stop referencing prisma-pwa icons");

const sw = readText("public/prisma-mobile-sw.js");
assert(sw.includes("prisma-mobile-pwa-v11-ios-home-icon-20260502"), "service worker cache version must be bumped for icon cache refresh");
assert(sw.includes('/icons/prisma_playstore_icon_512.png'), "service worker must precache 512 Play Store icon");
assert(sw.includes('/icons/prisma_playstore_icon_192.png'), "service worker must precache 192 Play Store icon");

console.log("[IOS HOME ICON OK] PRISMA App iOS home-screen icon now resolves to prisma_playstore_icon_512.png.");
