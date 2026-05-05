import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const appRoot = process.cwd();
const projectRoot = path.resolve(appRoot, "../../..");
const androidRoot = path.join(projectRoot, "products/mobile/android");

function fail(message) {
  console.error(`[PLAYSTORE FAIL] ${message}`);
  process.exit(1);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function read(rel) {
  const full = path.join(projectRoot, rel);
  assert(existsSync(full), `Missing ${rel}`);
  return readFileSync(full, "utf8");
}

function readApp(rel) {
  const full = path.join(appRoot, rel);
  assert(existsSync(full), `Missing ${rel}`);
  return readFileSync(full, "utf8");
}

assert(existsSync(androidRoot), "products/mobile/android root must exist");
read("products/mobile/android/README_ANDROID_TWA.md");
read("products/mobile/android/twa-manifest.template.json");
read("products/mobile/android/build-readiness.md");

const assetlinks = readApp("public/.well-known/assetlinks.template.json");
assert(assetlinks.includes("delegate_permission/common.handle_all_urls"), "assetlinks template must include TWA relation");
assert(assetlinks.includes("REPLACE_WITH_RELEASE_SIGNING_CERT_SHA256_FINGERPRINT"), "assetlinks template must keep fingerprint placeholder");

const twa = JSON.parse(read("products/mobile/android/twa-manifest.template.json"));
assert(twa.packageId === "com.prisma.mobile", "TWA packageId placeholder must be com.prisma.mobile");
assert(Number(twa.targetSdkVersion) >= 35, "TWA targetSdkVersion should be 35 or higher");
assert(twa.host === "REPLACE_WITH_PRISMA_APP_DOMAIN", "TWA host must remain a placeholder until production domain is known");

const docs = [
  read("products/mobile/android/README_ANDROID_TWA.md"),
  read("products/mobile/android/build-readiness.md"),
  read("products/mobile/app/docs/PLAY_STORE_READINESS.md"),
  read("products/mobile/app/docs/PWA_READINESS.md"),
  read("products/mobile/app/docs/TWA_ANDROID_READINESS.md"),
].join("\n");

for (const required of ["Android App Bundle", ".aab", "API 35", "HTTPS", "Digital Asset Links", "SHA-256", "internal testing"]) {
  assert(docs.includes(required), `Readiness docs must mention ${required}`);
}

assert(!existsSync(path.join(appRoot, "public/.well-known/assetlinks.json")), "Do not ship final assetlinks.json without real domain/package/fingerprint");

console.log("[PLAYSTORE OK] PRISMA Mobile Play Store readiness scaffold is present. Release submission still requires real domain, signing, AAB build, and Play Console work.");
