#!/usr/bin/env node
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA6O5Ql5/3UKOFfaMVZlhPw9+REGHkdNKjHXnW48eRzeg=\n-----END PUBLIC KEY-----\n";
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
function fromB64url(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  return Buffer.from(normalized + "===".slice((normalized.length + 3) % 4), "base64");
}
function verify(file) {
  const envelope = JSON.parse(fs.readFileSync(file, "utf8"));
  const ok = crypto.verify(null, Buffer.from(canonical(envelope.payload), "utf8"), PUBLIC_KEY, fromB64url(envelope.signature));
  return ok;
}
const rootIndex = process.argv.indexOf("--root");
const root = rootIndex >= 0 ? process.argv[rootIndex + 1] : process.cwd();
const dir = path.join(root, "tooling", "licensing", "fixtures");
const valid = path.join(dir, "tablet-pro.active.signed.license.json");
const tampered = path.join(dir, "tampered.signed.license.json");
if (!fs.existsSync(valid)) { console.error(`Missing fixture ${valid}`); process.exit(2); }
if (!verify(valid)) { console.error("Valid signed fixture failed verification"); process.exit(3); }
if (fs.existsSync(tampered) && verify(tampered)) { console.error("Tampered signed fixture incorrectly verified"); process.exit(4); }
console.log("OK signed license fixtures verified");
