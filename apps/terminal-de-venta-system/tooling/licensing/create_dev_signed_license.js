#!/usr/bin/env node
/* 11C sanitized: no embedded PEM private key. Reads local-runtime dev signing material. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "..", "..");
const matPath = path.join(root, "local-runtime", "license-keys", "dev", "dev-signing-secret.local.json");

function b64u(buffer) {
  return Buffer.from(buffer).toString("base64").replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function canonical(value) {
  return JSON.stringify(value, Object.keys(value).sort());
}

export function loadDevSigningMaterial(materialPath = matPath) {
  const raw = JSON.parse(fs.readFileSync(materialPath, "utf8"));
  const keyId = raw.key_id || raw.keyId;
  const sec = raw.secret_b64url || raw.secretMaterialBase64Url;
  const alg = raw.algorithm === "HS256_DEV_ONLY" ? "HS256_DEV_LOCAL" : (raw.algorithm || "HS256_DEV_LOCAL");
  if (!keyId || !sec) {
    throw new Error("Missing local dev signing material fields");
  }
  return { keyId, sec, alg };
}

export function signPayload(payload, materialPath = matPath) {
  const m = loadDevSigningMaterial(materialPath);
  const secret = Buffer.from(m.sec.replace(/-/g, "+").replace(/_/g, "/"), "base64");
  const value = b64u(crypto.createHmac("sha256", secret).update(canonical(payload)).digest());
  return {
    payload,
    signature: {
      schemaVersion: "11C",
      algorithm: m.alg,
      keyId: m.keyId,
      value,
    },
  };
}

export default { signPayload, loadDevSigningMaterial };

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const signed = signPayload({
    licenseId: "lic_dev_signed_local",
    plan: "TABLET_PC_MANAGED",
    state: "active",
    issuedAt: new Date().toISOString(),
  });
  process.stdout.write(JSON.stringify(signed, null, 2) + "\n");
}
