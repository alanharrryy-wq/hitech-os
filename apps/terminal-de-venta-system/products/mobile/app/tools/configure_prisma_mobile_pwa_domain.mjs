#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const ROOT = process.cwd();
const CONFIG = path.join(ROOT, "public", "prisma-mobile-pwa.config.json");
const MANIFEST = path.join(ROOT, "public", "manifest.webmanifest");

function arg(name) {
  const prefix = `--${name}=`;
  const hit = process.argv.find((item) => item.startsWith(prefix));
  return hit ? hit.slice(prefix.length) : undefined;
}

function fail(message) {
  console.error(`[PWA DOMAIN ERROR] ${message}`);
  process.exit(1);
}

const rawDomain = arg("domain") || process.env.PRISMA_MOBILE_PWA_DOMAIN;
if (!rawDomain) fail("Falta --domain=tu-dominio.com o PRISMA_MOBILE_PWA_DOMAIN.");
const domain = rawDomain.replace(/^https?:\/\//, "").replace(/\/$/, "").trim().toLowerCase();
if (!/^[a-z0-9.-]+\.[a-z]{2,}$/.test(domain) && domain !== "localhost") fail(`Dominio inválido: ${rawDomain}`);
const origin = domain === "localhost" ? "http://localhost:3140" : `https://${domain}`;

for (const file of [CONFIG, MANIFEST]) {
  if (!fs.existsSync(file)) fail(`No existe ${file}`);
}

const config = JSON.parse(fs.readFileSync(CONFIG, "utf8"));
config.domain = domain;
config.origin = origin;
config.supportContact = arg("support") || process.env.PRISMA_MOBILE_SUPPORT_CONTACT || `soporte@${domain}`;
config.lastConfiguredAt = new Date().toISOString();
fs.writeFileSync(CONFIG, `${JSON.stringify(config, null, 2)}\n`, "utf8");

const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
manifest.start_url = "/prisma-app?source=pwa";
manifest.id = "/prisma-app";
manifest.scope = "/";
fs.writeFileSync(MANIFEST, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

console.log(`[PWA DOMAIN OK] PRISMA App configurada para ${origin}/prisma-app`);
console.log(`[PWA DOMAIN OK] Soporte: ${config.supportContact}`);
