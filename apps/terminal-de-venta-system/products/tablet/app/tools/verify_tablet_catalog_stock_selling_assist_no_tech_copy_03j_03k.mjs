#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}

const root = path.resolve(arg("--root", process.cwd()));
const files = [
  "components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx",
  "components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css",
  "app/catalog/page.tsx",
  "app/stock/page.tsx",
  "app/existencias/page.tsx"
];
const forbidden = [
  { label: "payload", pattern: /\bpayload\b/i },
  { label: "outbox", pattern: /\boutbox\b/i },
  { label: "runtime", pattern: /\bruntime\b/i },
  { label: "fixture", pattern: /\bfixture\b/i },
  { label: "mock", pattern: /\bmock\b/i },
  { label: "demo", pattern: /\bdemo\b/i },
  { label: "TODO", pattern: /\bTODO\b/ },
  { label: "Stock", pattern: /\bStock\b/ },
  { label: "Sin stock", pattern: /\bSin stock\b/i }
];
const allowedTechnicalIdentifiers = new Set(["data-prisma-screen", "data-prisma-component"]);
const checks = [];
function looksLikeForbiddenCopy(value) {
  return forbidden.some((term) => term.pattern.test(value));
}
function looksTechnicalString(value) {
  if (!value.trim()) return true;
  if (value.startsWith("@/") || value.startsWith("@components/") || value.startsWith("./") || value.startsWith("../")) return true;
  if (value.startsWith("/") || value.startsWith("api/")) return true;
  if (allowedTechnicalIdentifiers.has(value)) return true;
  return /^[a-z0-9_./:-]+$/i.test(value) && !/\s/.test(value) && !looksLikeForbiddenCopy(value);
}
function extractLikelyVisibleStrings(source) {
  const values = [];
  const literalPattern = /(["'`])((?:\\.|(?!\1)[\s\S])*?)\1/g;
  for (const match of source.matchAll(literalPattern)) {
    const value = match[2].replace(/\$\{[^}]*\}/g, " ").replace(/\\n/g, " ").trim();
    if (!looksTechnicalString(value)) values.push(value);
  }
  const jsxTextPattern = />\s*([^<>{}][^<>{}]*)\s*</g;
  for (const match of source.matchAll(jsxTextPattern)) {
    const value = match[1].replace(/\s+/g, " ").trim();
    if (!looksTechnicalString(value)) values.push(value);
  }
  return values;
}
for (const rel of files) {
  const full = path.join(root, rel);
  const visibleStrings = extractLikelyVisibleStrings(fs.readFileSync(full, "utf8"));
  for (const term of forbidden) {
    for (const value of visibleStrings) {
      if (term.pattern.test(value)) {
        throw new Error(`Forbidden visible/near-visible term '${term.label}' found in ${rel}: ${value}`);
      }
    }
  }
  checks.push(`OK no raw technical copy in ${rel}`);
}
console.log(checks.join("\n"));
console.log(`READY no-tech-copy ${checks.length} checks`);
