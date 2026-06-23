#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function val(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 && process.argv[index + 1] ? process.argv[index + 1] : fallback;
}

const root = process.cwd().endsWith(path.join("products", "mobile", "android"))
  ? path.resolve(process.cwd(), "..", "..", "..")
  : process.cwd();

const configPath = path.resolve(root, val("--config", "products/mobile/android/prisma-playstore.config.json"));
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));

if (!config.packageId) {
  throw new Error("Missing packageId in Prisma Play Store config");
}

if (String(config.releaseSigningSha256).includes("REPLACE_WITH")) {
  throw new Error("Refusing placeholder SHA-256");
}

const out = path.resolve(root, val("--out", "products/mobile/app/public/.well-known/assetlinks.json"));
const payload = [
  {
    relation: ["delegate_permission/common.handle_all_urls"],
    target: {
      namespace: "android_app",
      package_name: config.packageId,
      sha256_cert_fingerprints: [config.releaseSigningSha256],
    },
  },
];

fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify(payload, null, 2) + "\n");
console.log(`assetlinks written: ${path.relative(root, out)}`);
