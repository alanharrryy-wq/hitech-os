import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(process.cwd());
function must(rel) {
  const full = join(root, rel);
  if (!existsSync(full)) throw new Error(`Missing ${rel} at ${full}`);
  return full;
}
function pngSize(rel) {
  const buf = readFileSync(must(rel));
  if (buf.toString("ascii", 1, 4) !== "PNG") throw new Error(`${rel} is not a PNG`);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }

for (const [rel, size] of [
  ["public/apple-touch-icon.png", 180],
  ["public/apple-touch-icon-precomposed.png", 180],
  ["public/icons/prisma_ios_touch_icon_180.png", 180],
  ["public/icons/prisma_playstore_icon_192.png", 192],
  ["public/icons/prisma_playstore_icon_512.png", 512],
]) {
  const actual = pngSize(rel);
  assert(actual.width === size && actual.height === size, `${rel} must be ${size}x${size}`);
}

const layout = readFileSync(must("app/layout.tsx"), "utf8");
assert(layout.includes('manifest: "/manifest.webmanifest"'), "layout must declare manifest");
assert(layout.includes('url: "/apple-touch-icon.png"'), "layout apple icon must point to root apple-touch-icon.png");
assert(layout.includes('url: "/icons/prisma_ios_touch_icon_180.png"'), "layout must include ios 180 icon");
assert(!layout.includes('apple: [{ url: "/icons/prisma-pwa-192.png"'), "layout must not use old pwa apple icon");

const manifest = JSON.parse(readFileSync(must("public/manifest.webmanifest"), "utf8"));
const srcs = manifest.icons.map((x) => x.src);
assert(srcs.includes("/icons/prisma_playstore_icon_512.png"), "manifest must include playstore 512 icon");
assert(srcs.includes("/apple-touch-icon.png"), "manifest must include root apple touch icon");
assert(!JSON.stringify(manifest).includes("/icons/prisma-pwa-"), "manifest must not reference old prisma-pwa icons");

const sw = readFileSync(must("public/prisma-mobile-sw.js"), "utf8");
assert(sw.includes("prisma-mobile-pwa-v12-ios-root-touch-icon-20260502"), "service worker cache version must be v12");
assert(sw.includes('"/apple-touch-icon.png"'), "service worker must precache root apple touch icon");
assert(sw.includes('"/apple-touch-icon-precomposed.png"'), "service worker must precache precomposed touch icon");

console.log("[IOS ROOT TOUCH ICON OK] Root apple-touch-icon and manifest icons point to PRISMA playstore icon assets.");
