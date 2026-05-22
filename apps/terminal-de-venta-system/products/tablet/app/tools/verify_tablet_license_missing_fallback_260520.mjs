#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const repoRoot = path.resolve(appRoot, "..", "..", "..");
const failures = [];
const notes = [];

function read(rel) {
  return fs.readFileSync(path.join(repoRoot, rel), "utf8");
}

function functionBlock(text, marker) {
  const start = text.indexOf(marker);
  if (start < 0) return "";
  const brace = text.indexOf("{", start);
  if (brace < 0) return "";
  let depth = 0;
  for (let i = brace; i < text.length; i += 1) {
    const ch = text[i];
    if (ch === "{") depth += 1;
    if (ch === "}") {
      depth -= 1;
      if (depth === 0) return text.slice(start, i + 1);
    }
  }
  return "";
}

function must(condition, label) {
  if (!condition) failures.push(label);
}

const normalizer = read("shared/licensing/license-normalizer.ts");
const resolver = read("shared/licensing/feature-resolver.ts");
const block = functionBlock(normalizer, "export function missingLicenseStatus");

must(block.length > 0, "missingLicenseStatus debe existir");

if (block.includes("assignmentState")) {
  must(block.includes('assignmentState: "unknown"'), "si missingLicenseStatus define assignmentState, debe ser unknown");
  must(!block.includes('assignmentState: "unassigned"'), "missingLicenseStatus no debe marcar licencia faltante como unassigned");
} else {
  notes.push("origin/main compatible: missingLicenseStatus no define assignmentState, por lo tanto no existe falso unassigned en normalizer");
}

if (resolver.includes("assignmentState")) {
  must(resolver.includes("function shouldHardDenyAssignment"), "assignmentState hard-deny debe pasar por shouldHardDenyAssignment");
  must(resolver.includes('status.state !== "missing"'), "missing no debe entrar a hard deny");
  must(resolver.includes('status.source !== "missing_license"'), "missing_license no debe entrar a hard deny");
} else {
  notes.push("origin/main compatible: feature-resolver no contiene assignmentState hard-deny");
}

if (failures.length) {
  console.error("FAIL PRISMA_TABLET_LICENSE_MISSING_FALLBACK_ADAPTIVE");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS PRISMA_TABLET_LICENSE_MISSING_FALLBACK_ADAPTIVE");
for (const note of notes) console.log(`NOTE ${note}`);
console.log("Missing-license fallback está protegido o no aplica en esta base limpia.");
