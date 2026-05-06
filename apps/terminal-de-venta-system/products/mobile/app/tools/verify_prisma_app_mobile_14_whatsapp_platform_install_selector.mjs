import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
function must(rel) {
  const p = path.join(ROOT, rel);
  if (!existsSync(p)) throw new Error(`Missing ${rel}`);
  return p;
}
function text(rel) {
  return readFileSync(must(rel), "utf8");
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const installPage = text("app/prisma-app/install/page.tsx");
assert(installPage.includes("PrismaMobilePwaInstallPage"), "install page must render PrismaMobilePwaInstallPage");
assert(installPage.includes("Android o iOS"), "install page metadata must mention Android or iOS");

const page = text("src/components/prisma-app/PrismaMobilePwaInstallPage.tsx");
assert(page.includes("Elige Android o iPhone"), "install page hero must ask user to choose Android or iPhone");
assert(page.includes("WhatsApp"), "install page copy must acknowledge WhatsApp install links");

const card = text("src/components/prisma-app/PrismaMobilePwaInstallCard.tsx");
assert(card.includes("beforeinstallprompt"), "card must listen for Android install prompt");
assert(card.includes("installAndroid"), "card must include Android install handler");
assert(card.includes("installIos"), "card must include iOS install handler");
assert(card.includes("Copiar link para WhatsApp"), "card must expose WhatsApp copy action");
assert(card.includes("isWhatsAppWebView"), "card must detect WhatsApp webview");
assert(card.includes("isIOSSafari"), "card must detect iOS Safari");
assert(card.includes("data-prisma-pwa-status"), "card must keep PWA status surface");

const client = text("src/lib/prisma-app/prisma-mobile-pwa-client.ts");
assert(client.includes("isAndroidChrome"), "client must expose Android Chrome detection");
assert(client.includes("isIOSDevice"), "client must expose iOS detection");
assert(client.includes("isIOSSafari"), "client must expose iOS Safari detection");
assert(client.includes("isWhatsAppWebView"), "client must expose WhatsApp webview detection");
assert(client.includes("currentInstallUrl"), "client must expose shareable install url");
assert(client.includes("copyText"), "client must expose clipboard helper");

const css = text("src/components/prisma-app/prisma-mobile-pwa.module.css");
assert(css.includes(".platformChooser"), "CSS must include platform chooser layout");
assert(css.includes(".platformCard"), "CSS must include platform card styling");
assert(css.includes("prefers-reduced-motion"), "CSS must respect reduced motion");

const manifest = JSON.parse(text("public/manifest.webmanifest"));
assert(manifest.start_url === "/prisma-app", "manifest start_url must remain /prisma-app");
assert(manifest.scope === "/prisma-app", "manifest scope must remain /prisma-app");
assert(manifest.display === "standalone", "manifest display must remain standalone");
assert(manifest.icons.some((icon) => icon.src === "/icons/prisma_playstore_icon_512.png"), "manifest must keep Android 512 icon");
assert(manifest.icons.some((icon) => icon.src === "/apple-touch-icon.png"), "manifest must keep iOS apple touch icon");

const sw = text("public/prisma-mobile-sw.js");
assert(sw.includes("v14-whatsapp-platform-install-selector"), "service worker version must be v14");
assert(sw.includes("/prisma-app/install"), "service worker must cache install selector route");
assert(sw.includes("PRISMA_MOBILE_INSTALL"), "service worker must name install route");

console.log("[WHATSAPP PLATFORM INSTALL SELECTOR OK] PRISMA App install link now routes users to Android/iOS guided install screen.");
