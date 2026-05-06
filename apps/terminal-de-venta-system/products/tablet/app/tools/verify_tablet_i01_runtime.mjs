#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const toolsDir = path.dirname(__filename);
const appRoot = path.resolve(toolsDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function commandExists(cmd) {
  const probe = process.platform === "win32" ? "where" : "which";
  const r = spawnSync(probe, [cmd], { encoding: "utf8" });
  return r.status === 0;
}

const packagePath = path.join(appRoot, "package.json");
const schemaPath = path.join(appRoot, "prisma", "schema.prisma");
const dataDir = path.join(appRoot, "data");
const runtimeGate = path.join(appRoot, "scripts", "tablet-runtime-gates.mjs");

const checks = [];
function check(id, ok, detail) {
  checks.push({ id, ok, detail });
}

check("I01-001 app root exists", exists(appRoot), appRoot);
check("I01-002 package.json exists", exists(packagePath), packagePath);
check("I01-003 prisma schema exists", exists(schemaPath), schemaPath);
check("I01-004 data dir exists", exists(dataDir), dataDir);
check("I01-005 runtime gate exists", exists(runtimeGate), runtimeGate);
check("I01-006 node exists", commandExists("node"), "node");
check("I01-007 pnpm or npm exists", commandExists("pnpm") || commandExists("npm"), "pnpm/npm");

if (exists(packagePath)) {
  const pkg = readJson(packagePath);
  check("I01-008 verify:i01-runtime script registered", Boolean(pkg.scripts && pkg.scripts["verify:i01-runtime"]), "scripts.verify:i01-runtime");
  check("I01-009 tablet:i01:runtime script registered", Boolean(pkg.scripts && pkg.scripts["tablet:i01:runtime"]), "scripts.tablet:i01:runtime");
  check("I01-010 db:tablet:init:safe script registered", Boolean(pkg.scripts && pkg.scripts["db:tablet:init:safe"]), "scripts.db:tablet:init:safe");
}

const ok = checks.every((c) => c.ok);
console.log(JSON.stringify({
  ok,
  appRoot,
  checks,
  verdict: ok ? "PASS" : "FAIL",
  note: "I01 validates runtime scaffolding. Full DB/typecheck requires installed Node dependencies."
}, null, 2));
process.exit(ok ? 0 : 2);
