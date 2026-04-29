#!/usr/bin/env node
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIFsQhNMkOpEGSMvieWuSh3fabivJhJf/pKfuGRJmSAJX\n-----END PRIVATE KEY-----\n";
function canonical(value) {
  if (value === null) return "null";
  if (typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") return Number.isFinite(value) ? JSON.stringify(value) : "null";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (Array.isArray(value)) return "[" + value.map(canonical).join(",") + "]";
  if (typeof value === "object") {
    const keys = Object.keys(value).filter((key) => value[key] !== undefined).sort();
    return "{" + keys.map((key) => JSON.stringify(key) + ":" + canonical(value[key])).join(",") + "}";
  }
  return "null";
}
function b64url(buffer) { return Buffer.from(buffer).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }
const input = process.argv[2];
const output = process.argv[3];
if (!input || !output) {
  console.error("Usage: node tooling/licensing/create_dev_signed_license.js payload.json output.signed.license.json");
  process.exit(2);
}
const payload = JSON.parse(fs.readFileSync(input, "utf8"));
const signature = b64url(crypto.sign(null, Buffer.from(canonical(payload), "utf8"), PRIVATE_KEY));
const envelope = { payload, alg: "Ed25519", keyId: "prisma_dev_2026_02cd", signature };
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify(envelope, null, 2) + "
", "utf8");
console.log(`Wrote ${output}`);
