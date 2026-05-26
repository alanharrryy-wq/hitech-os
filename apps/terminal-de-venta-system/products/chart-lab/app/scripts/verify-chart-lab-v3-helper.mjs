// PRISMA_CHART_LAB_VERIFIER_HELPER_V3_HOTFIX3
import fs from "node:fs";
import path from "node:path";

export function appRoot() {
  return path.resolve(process.cwd());
}

export function repoRoot() {
  return path.resolve(appRoot(), "../../..");
}

export function read(rel) {
  return fs.readFileSync(path.join(appRoot(), rel), "utf8");
}

export function exists(rel) {
  return fs.existsSync(path.join(appRoot(), rel));
}

export function assert(condition, message, failures) {
  if (!condition) failures.push(message);
}

export function report(name, failures, warnings = []) {
  for (const warning of warnings) console.log(`WARN ${name}: ${warning}`);
  if (failures.length) {
    console.error(`FAIL ${name}: ${failures.length} issue(s)`);
    for (const failure of failures) console.error(` - ${failure}`);
    process.exit(1);
  }
  console.log(`PASS ${name}`);
}

export function countMatches(text, regex) {
  return [...text.matchAll(regex)].length;
}
