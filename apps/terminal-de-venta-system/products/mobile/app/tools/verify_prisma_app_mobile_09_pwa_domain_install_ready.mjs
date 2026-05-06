import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
function must(rel){ const full=path.join(root, rel); if(!fs.existsSync(full)) throw new Error(`Missing ${rel}`); return full; }
function readJson(rel){ return JSON.parse(fs.readFileSync(must(rel), "utf8")); }
const cfg = readJson("public/prisma-mobile-pwa.config.json");
const validContracts = new Set(["PRISMA_APP_MOBILE_09_PWA_DOMAIN_INSTALL_READY", "PRISMA_APP_MOBILE_10_CLOUDFLARE_PWA_DOMAIN_BRIDGE"]);
if(!validContracts.has(cfg.contractId)) throw new Error("config contractId inválido");
for (const rel of [
  "public/manifest.webmanifest",
  "public/prisma-mobile-sw.js",
  "public/prisma-offline.html",
  "public/icons/prisma-pwa-192.png",
  "public/icons/prisma-pwa-512.png",
  "public/.well-known/pwa-domain-check.json",
  "app/prisma-app/install/page.tsx",
  "app/prisma-app/offline/page.tsx",
  "src/components/prisma-app/PrismaMobilePwaInstallCard.tsx",
  "src/components/prisma-app/PrismaMobilePwaRuntime.tsx"
]) must(rel);
console.log("[PWA INSTALL READY OK] PRISMA App Mobile PWA installable domain flow is installed.");
