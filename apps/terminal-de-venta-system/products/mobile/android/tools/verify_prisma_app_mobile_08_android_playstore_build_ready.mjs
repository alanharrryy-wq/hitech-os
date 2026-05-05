import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
function must(rel){ const full=path.join(root, rel); if(!fs.existsSync(full)) throw new Error(`Missing ${rel}`); return full; }
function readJson(rel){ return JSON.parse(fs.readFileSync(must(rel), "utf8")); }
function versionAtLeast(actual, min){ const a=String(actual).split(".").map(Number); const b=String(min).split(".").map(Number); for(let i=0;i<3;i++){ if((a[i]||0)>(b[i]||0)) return true; if((a[i]||0)<(b[i]||0)) return false; } return true; }
const pkg=readJson("products/mobile/app/package.json");
if(!versionAtLeast(pkg.version, "0.8.0")) throw new Error(`mobile package version must be 0.8.0 or later compatible, got ${pkg.version}`);
const cfg=readJson("products/mobile/android/prisma-playstore.config.json");
for (const rel of [
  "products/mobile/android/app/build.gradle.kts",
  "products/mobile/android/app/src/main/AndroidManifest.xml",
  "products/mobile/android/tools/build_prisma_android_aab.ps1",
  "products/mobile/android/tools/create_prisma_upload_keystore.ps1",
  "products/mobile/android/store-listing/es-MX/title.txt",
  "products/mobile/android/store-listing/es-MX/data-safety-draft.md"
]) must(rel);
if(!cfg.packageId && !cfg.applicationId) throw new Error("missing package/application id in playstore config");
console.log("[ANDROID PLAYSTORE OK] PRISMA_APP_MOBILE_08_ANDROID_PLAYSTORE_BUILD_READY Android/TWA scaffold, AAB scripts, store listing, and verification files are installed. root="+root);
if(String(cfg.releaseSigningSha256||"").includes("REPLACE")) console.log("[ANDROID PLAYSTORE NOTE] Production submission still blocked by real releaseSigningSha256. This is expected until signing is assigned.");
