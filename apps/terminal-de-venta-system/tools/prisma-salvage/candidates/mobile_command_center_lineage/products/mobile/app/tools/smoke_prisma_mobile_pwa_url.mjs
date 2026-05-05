#!/usr/bin/env node
import process from "node:process";

const base = (process.argv.find((arg) => arg.startsWith("--url=")) || "").slice("--url=".length).replace(/\/$/, "");
if (!base) {
  console.error("Uso: node tools/smoke_prisma_mobile_pwa_url.mjs --url=https://tu-dominio.com");
  process.exit(2);
}

const paths = ["/prisma-app", "/prisma-app/install", "/manifest.webmanifest", "/prisma-mobile-pwa.config.json", "/prisma-mobile-sw.js", "/prisma-offline.html", "/.well-known/pwa-domain-check.json"];
let failed = false;
for (const route of paths) {
  const url = `${base}${route}`;
  try {
    const response = await fetch(url, { redirect: "manual" });
    const ok = response.status >= 200 && response.status < 400;
    console.log(`${ok ? "OK" : "FAIL"} ${response.status} ${url}`);
    if (!ok) failed = true;
  } catch (error) {
    console.log(`FAIL fetch ${url}: ${error instanceof Error ? error.message : String(error)}`);
    failed = true;
  }
}
if (failed) process.exit(1);
console.log("[PWA URL OK] rutas públicas mínimas responden.");
