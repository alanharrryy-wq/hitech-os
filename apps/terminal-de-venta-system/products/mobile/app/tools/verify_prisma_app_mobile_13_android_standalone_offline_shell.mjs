import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
function must(rel) {
  const path = join(ROOT, rel);
  if (!existsSync(path)) throw new Error(`Missing required file: ${rel}`);
  return path;
}
function read(rel) { return readFileSync(must(rel), "utf8"); }
function assert(condition, message) { if (!condition) throw new Error(message); }
function readJson(rel) { return JSON.parse(read(rel)); }
function pngSize(rel) {
  const buffer = readFileSync(must(rel));
  const png = buffer.toString("ascii", 1, 4) === "PNG";
  assert(png, `${rel} must be a PNG`);
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

const manifest = readJson("public/manifest.webmanifest");
assert(manifest.id === "/prisma-app", "manifest id must remain /prisma-app");
assert(manifest.start_url === "/prisma-app", "manifest start_url must open PRISMA App shell");
assert(manifest.scope === "/prisma-app", "manifest scope must keep Android standalone navigation inside /prisma-app");
assert(manifest.display === "standalone", "manifest display must be standalone");
assert(Array.isArray(manifest.display_override) && manifest.display_override.includes("standalone"), "manifest display_override must include standalone");
assert(manifest.prefer_related_applications === false, "manifest must prefer the web PWA, not a store redirect");
assert(Array.isArray(manifest.related_applications) && manifest.related_applications.some((entry) => entry.platform === "webapp" && entry.url === "/manifest.webmanifest"), "manifest must declare its own webapp relation for install-state checks");
const manifestText = JSON.stringify(manifest);
assert(!manifestText.includes("/icons/prisma-pwa-"), "manifest must not reference old prisma-pwa icons");
const iconSources = manifest.icons.map((icon) => icon.src);
assert(iconSources.includes("/icons/prisma_playstore_icon_192.png"), "manifest must include Android 192 icon");
assert(iconSources.includes("/icons/prisma_playstore_icon_512.png"), "manifest must include Android 512 icon");
assert(iconSources.includes("/apple-touch-icon.png"), "manifest must include root apple touch icon");
const icon512 = manifest.icons.find((icon) => icon.src === "/icons/prisma_playstore_icon_512.png");
assert(icon512?.purpose?.includes("maskable"), "512 icon must be maskable for Android splash/launcher");
assert(pngSize("public/icons/prisma_playstore_icon_192.png").width === 192, "192 icon width must be 192");
assert(pngSize("public/icons/prisma_playstore_icon_512.png").width === 512, "512 icon width must be 512");
assert(pngSize("public/apple-touch-icon.png").width === 180, "apple touch icon width must be 180");

const layout = read("app/layout.tsx");
assert(layout.includes('manifest: "/manifest.webmanifest"'), "layout must declare manifest");
assert(layout.includes('/icons/prisma_playstore_icon_512.png'), "layout must reference Android/Playstore 512 icon");
assert(layout.includes('url: "/apple-touch-icon.png"'), "layout must reference root apple touch icon");
assert(!layout.includes('/icons/prisma-pwa-'), "layout must not reference old prisma-pwa icons");

const sw = read("public/prisma-mobile-sw.js");
assert(sw.includes("prisma-mobile-pwa-v13-android-standalone-offline-20260502"), "service worker must use v13 cache version");
assert(sw.includes('"/prisma-app"'), "service worker must precache app shell");
assert(sw.includes('"/prisma-offline.html"'), "service worker must precache offline page");
assert(sw.includes('"/icons/prisma_playstore_icon_512.png"'), "service worker must precache Android 512 icon");
assert(sw.includes('"/apple-touch-icon.png"'), "service worker must precache root touch icon");
assert(sw.includes("Promise.allSettled"), "service worker install must tolerate optional missing assets");
assert(sw.includes('request.mode === "navigate"'), "service worker must handle navigations offline");
assert(sw.includes("self.skipWaiting"), "service worker must activate fresh cache promptly");

const runtime = read("src/components/prisma-app/PrismaMobilePwaRuntime.tsx");
assert(runtime.includes('register("/prisma-mobile-sw.js", { scope: "/" })'), "runtime must register root-scope service worker");
assert(runtime.includes("registration.update"), "runtime must request service worker update");
assert(runtime.includes("controllerchange"), "runtime must react to updated service worker controller");

const client = read("src/lib/prisma-app/prisma-mobile-pwa-client.ts");
assert(client.includes('"fullscreen"') && client.includes('"minimal-ui"') && client.includes('"window-controls-overlay"'), "standalone detection must include supported display modes");
assert(client.includes("isAndroidChrome"), "PWA client must expose Android Chrome detection");

const card = read("src/components/prisma-app/PrismaMobilePwaInstallCard.tsx");
assert(card.includes("beforeinstallprompt"), "install card must handle Android beforeinstallprompt");
assert(card.includes("appinstalled"), "install card must handle appinstalled");
assert(card.includes("Instalar en Android"), "install card must expose Android install copy");
assert(card.includes("Cierra Chrome y entra desde el ícono"), "Android guide must validate launcher standalone flow");

console.log("[ANDROID STANDALONE OFFLINE OK] PRISMA App manifest, service worker, icons, runtime, and install card are Android/iOS PWA ready.");
