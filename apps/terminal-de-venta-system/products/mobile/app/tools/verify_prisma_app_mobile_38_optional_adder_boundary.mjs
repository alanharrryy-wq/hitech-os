#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const phase = "MOBILE_OPTIONAL_ADDER_BOUNDARY_PHASE_1";
const root = process.cwd();
const requiredCopy = ["Mobile supervisa", "Tablet Solo vende sola", "Mobile no es requisito para vender", "Mobile no bloquea POS", "PC y Mobile son adders opcionales", "Cloudflare y soporte remoto son opcionales", "Internet no es requisito para venta base Tablet Solo"];
const forbiddenCopy = ["Mobile requerido para operar", "Conecta la app movil para vender", "Conecta la app móvil para vender", "Supervision movil obligatoria", "Supervisión móvil obligatoria", "Cloudflare requerido", "Internet requerido para venta base", "PC o Mobile requeridos para licencia base", "Mobile bloquea POS", "Mobile bloquea cobro", "Mobile bloquea corte", "Mobile bloquea ticket", "Mobile bloquea licencia local", "Mobile bloquea operacion offline", "Mobile bloquea operación offline"];
const requiredFiles = ["docs/atlas/ATLAS_MOBILE_OPTIONAL_ADDER_BOUNDARY_ADDENDUM.md", "docs/atlas/ATLAS_MOBILE_OPTIONAL_ADDER_BOUNDARY_ROLLBACK.md", "docs/prisma-app/PRISMA_APP_MOBILE_38_OPTIONAL_ADDER_BOUNDARY.md", "docs/prisma-app/qa/prisma-app-mobile-38-optional-adder-boundary-scenarios.json", "tools/verify_prisma_app_mobile_38_optional_adder_boundary.mjs"];
const textExt = new Set([".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".css", ".html", ".txt"]);
const skipDirs = new Set(["node_modules", ".next", "dist", "build", ".git", ".turbo", "coverage", "_local", "tmp", ".prisma_backups", ".prisma_installer_backups", "backups"]);
const skipFiles = new Set(["tools/verify_prisma_app_mobile_38_optional_adder_boundary.mjs"]);
function fail(message, extra = {}) { console.error(JSON.stringify({ ok: false, phase, message, ...extra }, null, 2)); process.exit(1); }
function walk(dir, out = []) { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { if (skipDirs.has(entry.name)) continue; const full = path.join(dir, entry.name); if (entry.isDirectory()) walk(full, out); else if (entry.isFile() && textExt.has(path.extname(entry.name))) out.push(full); } return out; }
if (!fs.existsSync(path.join(root, "package.json"))) fail("Run from products/mobile/app.");
for (const rel of requiredFiles) if (!fs.existsSync(path.join(root, rel))) fail("Missing required Mobile boundary file.", { file: rel });
const files = walk(root); let allText = "";
for (const file of files) { const rel = path.relative(root, file).replace(/\\/g, "/"); if (skipFiles.has(rel)) continue; const text = fs.readFileSync(file, "utf8"); allText += "\n" + text; for (const bad of forbiddenCopy) if (text.includes(bad)) fail("Forbidden Mobile dependency copy found.", { file: rel, forbiddenCopy: bad }); }
const missing = requiredCopy.filter((copy) => !allText.includes(copy));
if (missing.length) fail("Required optional-adder copy missing.", { missing });
const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
if (!pkg.scripts || !pkg.scripts["verify:optional-adder-boundary"]) fail("Missing package script verify:optional-adder-boundary.");
console.log(JSON.stringify({ ok: true, phase, checkedFiles: files.length, message: "Mobile supervisa. Tablet Solo vende sola. Boundary Mobile-only verificado." }, null, 2));
