import { readFileSync, statSync } from "node:fs";
import { join } from "node:path";

function must(rel) {
  const path = join(process.cwd(), rel);
  try {
    statSync(path);
    return path;
  } catch (_error) {
    throw new Error(`Missing required file: ${rel}`);
  }
}

function text(rel) {
  return readFileSync(must(rel), "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const page = text("src/components/prisma-app/PrismaMobilePwaInstallPage.tsx");
const card = text("src/components/prisma-app/PrismaMobilePwaInstallCard.tsx");
const css = text("src/components/prisma-app/prisma-mobile-pwa.module.css");
const client = text("src/lib/prisma-app/prisma-mobile-pwa-client.ts");
const manifest = JSON.parse(text("public/manifest.webmanifest"));
const sw = text("public/prisma-mobile-sw.js");

assert(page.includes("Elige tu celular"), "install page must be the minimal platform selector");
assert(!page.includes("Abrir tablero"), "install page must not show dashboard link in hero");
assert(!page.includes("Ver manifest"), "install page must not show manifest link");
assert(card.includes('data-platform="android"'), "android platform card missing");
assert(card.includes('data-platform="ios"'), "ios platform card missing");
assert(card.includes("tryOpenAndroidChrome"), "android chrome handoff missing");
assert(card.includes("beforeinstallprompt"), "android native PWA prompt capture missing");
assert(!card.includes("Guide({"), "guide component must be removed from minimal selector");
assert(!card.includes("stepsGrid"), "minimal selector must not render long steps grid");
assert(css.includes("platformChooserMinimal"), "minimal platform grid styles missing");
assert(css.includes("platformOrbCard"), "fancy platform card styles missing");
assert(css.includes("backdrop-filter"), "premium glass effect missing");
assert(css.includes("prismaFloat"), "ambient motion effect missing");
assert(client.includes("androidChromeIntentUrl"), "android intent URL helper missing");
assert(client.includes("package=com.android.chrome"), "Chrome package handoff missing");
assert(manifest.display === "standalone", "manifest display must stay standalone");
assert(manifest.start_url === "/prisma-app", "manifest start_url must stay /prisma-app");
assert(JSON.stringify(manifest).includes("/icons/prisma_playstore_icon_512.png"), "manifest must keep 512 icon");
assert(sw.includes("prisma-mobile-pwa-v15-minimal-platform-install-selector-20260502"), "service worker version must be v15");
assert(sw.includes("/prisma-app/install"), "service worker must cache install route");

console.log("[PRISMA APP MOBILE 15 OK] Minimal fancy Android/iPhone install selector is installed.");
