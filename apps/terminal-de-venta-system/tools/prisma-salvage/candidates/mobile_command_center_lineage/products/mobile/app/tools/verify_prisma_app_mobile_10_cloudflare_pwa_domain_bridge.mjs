import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
function must(rel) { const full = path.join(root, rel); if (!fs.existsSync(full)) throw new Error(`Missing ${rel}`); return full; }
function readJson(rel) { return JSON.parse(fs.readFileSync(must(rel), "utf8")); }
const pkg = readJson("products/mobile/app/package.json");
const pwa = readJson("products/mobile/app/public/prisma-mobile-pwa.config.json");
const bridge = readJson("products/mobile/infra/cloudflare/prisma-mobile-cloudflare.config.json");
const deploy = readJson("products/mobile/app/deploy/cloudflare-prisma-mobile-domain.json");
const check = readJson("products/mobile/app/public/.well-known/pwa-domain-check.json");
for (const rel of ["products/mobile/app/public/manifest.webmanifest","products/mobile/app/public/prisma-mobile-sw.js","products/mobile/app/tools/verify_prisma_app_mobile_09_pwa_domain_install_ready.mjs","products/mobile/infra/cloudflare/ensure_prisma_mobile_cloudflare_bridge.py","products/mobile/infra/cloudflare/ensure_prisma_mobile_cloudflare_bridge.ps1","products/mobile/infra/cloudflare/start_prisma_mobile_origin.ps1","products/mobile/infra/cloudflare/smoke_prisma_mobile_public.ps1"]) must(rel);
const expectedHost = "prisma.hitechrts.com";
if (pkg.version !== "0.10.0") throw new Error(`Expected package version 0.10.0, got ${pkg.version}`);
if (!pkg.scripts?.["verify:cloudflare-pwa-domain"]) throw new Error("Missing verify:cloudflare-pwa-domain script");
if (!pkg.scripts?.["cloudflare:pwa:bridge"]) throw new Error("Missing cloudflare:pwa:bridge script");
if (pwa.domain !== expectedHost) throw new Error(`PWA domain mismatch: ${pwa.domain}`);
if (pwa.origin !== `https://${expectedHost}`) throw new Error(`PWA origin mismatch: ${pwa.origin}`);
if (pwa.localOrigin !== "http://127.0.0.1:3140") throw new Error(`PWA local origin mismatch: ${pwa.localOrigin}`);
if (bridge.hostname !== expectedHost) throw new Error(`Bridge hostname mismatch: ${bridge.hostname}`);
if (bridge.originUrl !== "http://127.0.0.1:3140") throw new Error(`Bridge origin mismatch: ${bridge.originUrl}`);
if (deploy.publicUrl !== `https://${expectedHost}/prisma-app`) throw new Error(`Deploy public URL mismatch: ${deploy.publicUrl}`);
if (check.hostname !== expectedHost) throw new Error(`Domain check hostname mismatch: ${check.hostname}`);
console.log(`[CLOUDFLARE PWA DOMAIN OK] PRISMA Mobile is configured for https://${expectedHost}/prisma-app via tunnel engine -> http://127.0.0.1:3140.`);
