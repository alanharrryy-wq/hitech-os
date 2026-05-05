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
const forbidden = ["payload", "outbox", "runtime", "fixture", "mock", "demo", "TODO"];
const allowedTechnicalIdentifiers = new Set(["data-prisma-screen", "data-prisma-component"]);
const checks = [];
for (const rel of files) {
  const full = path.join(root, rel);
  const text = fs.readFileSync(full, "utf8");
  for (const term of forbidden) {
    const pattern = term === "TODO" ? /\bTODO\b/ : new RegExp(`\\b${term}\\b`, "i");
    if (pattern.test(text)) {
      const safe = [...allowedTechnicalIdentifiers].some((token) => pattern.test(token));
      if (!safe) throw new Error(`Forbidden visible/near-visible term '${term}' found in ${rel}`);
    }
  }
  checks.push(`OK no raw technical copy in ${rel}`);
}
console.log(checks.join("\n"));
console.log(`READY no-tech-copy ${checks.length} checks`);
