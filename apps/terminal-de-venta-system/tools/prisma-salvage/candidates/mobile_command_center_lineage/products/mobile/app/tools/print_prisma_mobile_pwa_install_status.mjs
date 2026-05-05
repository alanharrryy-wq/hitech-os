#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const configPath = path.join(root, "public", "prisma-mobile-pwa.config.json");
const manifestPath = path.join(root, "public", "manifest.webmanifest");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
const placeholder = config.domain.includes("REPLACE_WITH");
console.log("PRISMA App Mobile PWA status");
console.log(`  contract: ${config.contractId}`);
console.log(`  domain:   ${config.domain}${placeholder ? " (pendiente)" : ""}`);
console.log(`  app:      ${config.origin}${config.appPath}`);
console.log(`  install:  ${config.origin}${config.installPath}`);
console.log(`  offline:  ${config.offlinePath}`);
console.log(`  manifest: ${manifest.name} / ${manifest.display} / ${manifest.start_url}`);
console.log(`  next:     ${placeholder ? "configura dominio con pwa:configure-domain" : "deploy HTTPS y prueba desde celular"}`);
