#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const scriptDir = path.dirname(__filename);
const appRoot = path.resolve(scriptDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function commandExists(cmd) {
  const probe = process.platform === "win32" ? "where" : "which";
  const r = spawnSync(probe, [cmd], { encoding: "utf8" });
  return r.status === 0;
}

function run(cmd, args, options = {}) {
  const r = spawnSync(cmd, args, {
    cwd: appRoot,
    encoding: "utf8",
    shell: process.platform === "win32",
    ...options
  });
  return {
    command: [cmd, ...args].join(" "),
    status: r.status,
    stdout: (r.stdout || "").trim(),
    stderr: (r.stderr || "").trim()
  };
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function main() {
  const modeArg = process.argv.find((a) => a.startsWith("--mode="));
  const mode = modeArg ? modeArg.split("=")[1] : "verify";

  const packagePath = path.join(appRoot, "package.json");
  const schemaPath = path.join(appRoot, "prisma", "schema.prisma");
  const dataDir = path.join(appRoot, "data");
  const dbPath = path.join(dataDir, "tablet-pos.db");

  const report = {
    ok: true,
    mode,
    appRoot,
    checks: [],
    commands: [],
    recommendations: []
  };

  function check(name, ok, detail) {
    report.checks.push({ name, ok, detail });
    if (!ok) report.ok = false;
  }

  check("appRoot exists", exists(appRoot), appRoot);
  check("package.json exists", exists(packagePath), packagePath);
  check("prisma/schema.prisma exists", exists(schemaPath), schemaPath);
  check("data directory exists", exists(dataDir), dataDir);
  check("node command exists", commandExists("node"), "node");
  check("npm command exists", commandExists("npm"), "npm");
  check("pnpm command exists or npm fallback available", commandExists("pnpm") || commandExists("npm"), "pnpm/npm");

  if (exists(packagePath)) {
    const pkg = readJson(packagePath);
    check("verify:i01-runtime script exists", Boolean(pkg.scripts && pkg.scripts["verify:i01-runtime"]), "package.json scripts.verify:i01-runtime");
    check("tablet:i01:runtime script exists", Boolean(pkg.scripts && pkg.scripts["tablet:i01:runtime"]), "package.json scripts.tablet:i01:runtime");
  }

  if (mode === "db-init") {
    fs.mkdirSync(dataDir, { recursive: true });
    const prismaCmd = commandExists("pnpm") ? "pnpm" : "npm";
    const prismaArgs = commandExists("pnpm")
      ? ["exec", "prisma", "db", "push", "--schema", "prisma/schema.prisma"]
      : ["exec", "--", "prisma", "db", "push", "--schema", "prisma/schema.prisma"];

    report.commands.push(run(prismaCmd, prismaArgs));
    const last = report.commands[report.commands.length - 1];
    if (last.status !== 0) {
      report.ok = false;
      report.recommendations.push("Instalar dependencias antes de db-init: pnpm install o npm install dentro de products/tablet/app.");
    }
  }

  if (mode === "typecheck") {
    const cmd = commandExists("pnpm") ? "pnpm" : "npm";
    const args = commandExists("pnpm") ? ["exec", "tsc", "--noEmit"] : ["exec", "--", "tsc", "--noEmit"];
    report.commands.push(run(cmd, args));
    const last = report.commands[report.commands.length - 1];
    if (last.status !== 0) report.ok = false;
  }

  if (!exists(dbPath)) {
    report.recommendations.push("DB local no encontrada todavía. Ejecutar db init después de instalar dependencias.");
  }

  console.log(JSON.stringify(report, null, 2));
  process.exit(report.ok ? 0 : 2);
}

main();
