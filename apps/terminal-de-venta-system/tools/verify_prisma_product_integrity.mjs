#!/usr/bin/env node
import childProcess from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const args = process.argv.slice(2);

function argValue(name, fallback) {
  const index = args.indexOf(name);
  if (index >= 0 && args[index + 1]) return args[index + 1];
  const inline = args.find((item) => item.startsWith(`${name}=`));
  if (inline) return inline.slice(name.length + 1);
  return fallback;
}

const outDir = path.resolve(
  repoRoot,
  argValue("--out-dir", "tools/codex/runs/prisma-round2-product-integrity"),
);

const results = [];

function rel(filePath) {
  return path.relative(repoRoot, filePath).replaceAll(path.sep, "/");
}

function readText(relativePath) {
  return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function exists(relativePath) {
  return fs.existsSync(path.join(repoRoot, relativePath));
}

function add(status, id, title, evidence = []) {
  results.push({
    status,
    id,
    title,
    evidence: Array.isArray(evidence) ? evidence : [String(evidence)],
  });
}

function git(gitArgs) {
  return childProcess.spawnSync("git", gitArgs, {
    cwd: repoRoot,
    encoding: "utf8",
    windowsHide: true,
  });
}

function isGitIgnored(relativePath) {
  return git(["check-ignore", "-q", relativePath]).status === 0;
}

function isGitTracked(relativePath) {
  return git(["ls-files", "--error-unmatch", relativePath]).status === 0;
}

function parseWorkspacePackages() {
  const text = readText("pnpm-workspace.yaml");
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.startsWith("- "))
    .map((line) => line.slice(2).trim())
    .filter(Boolean);
}

function checkWorkspaceLockfile() {
  const packages = parseWorkspacePackages();
  const lockfile = readText("pnpm-lock.yaml");
  const packageEvidence = [];
  const missingPackages = [];
  const missingImporters = [];
  const floatingVersions = [];

  for (const packagePath of packages) {
    const packageJsonPath = `${packagePath}/package.json`;
    if (!exists(packageJsonPath)) {
      missingPackages.push(packageJsonPath);
      continue;
    }

    packageEvidence.push(`${packagePath} has package.json`);
    if (!lockfile.includes(`\n  ${packagePath}:`)) {
      missingImporters.push(packagePath);
    }

    const pkg = readJson(packageJsonPath);
    const dependencyGroups = ["dependencies", "devDependencies", "optionalDependencies"];
    for (const group of dependencyGroups) {
      const entries = Object.entries(pkg[group] ?? {});
      for (const [name, version] of entries) {
        if (version === "latest" || version === "*" || version === "") {
          floatingVersions.push(`${packagePath} ${group}.${name}=${version}`);
        }
      }
    }
  }

  if (missingPackages.length || missingImporters.length || floatingVersions.length) {
    add("FAIL", "workspace-lockfile", "Active workspace packages must be resolvable and locked", [
      ...packageEvidence,
      ...missingPackages.map((item) => `missing package: ${item}`),
      ...missingImporters.map((item) => `missing lockfile importer: ${item}`),
      ...floatingVersions.map((item) => `floating active dependency: ${item}`),
    ]);
  } else {
    add("PASS", "workspace-lockfile", "Active workspace packages are resolvable and locked", packageEvidence);
  }

  if (exists("products/web/app/package.json") && !packages.includes("products/web/app")) {
    add("PASS", "web-off-release-lane", "products/web/app is preserved outside the active workspace", [
      "products/web/app/package.json exists",
      "products/web/app is not listed in pnpm-workspace.yaml",
      "RELEASE_LANES.md documents the off-release decision",
    ]);
  } else if (packages.includes("products/web/app")) {
    add("FAIL", "web-off-release-lane", "products/web/app is active but was not promoted deterministically", [
      "products/web/app should remain outside the active workspace until its exact versions and lockfile contract are approved",
    ]);
  }
}

function checkGeneratedArtifacts() {
  const generatedNames = new Set([".next", "dist", "build", ".turbo", "coverage"]);
  const skipNames = new Set([
    ".git",
    "node_modules",
    "tools/codex/runs",
    "tools/_local",
    "tools/prisma-salvage",
    ".prisma_installer_backups",
    ".prisma_install_state",
    ".prisma_installer_tmp",
  ]);
  const roots = ["products", "prisma", "shared", "tools", "docs/release/prisma-round2"];
  const found = [];

  function shouldSkip(relativePath) {
    return [...skipNames].some((skip) => relativePath === skip || relativePath.startsWith(`${skip}/`));
  }

  function walk(dir) {
    const relativeDir = rel(dir);
    if (shouldSkip(relativeDir)) return;
    const entries = fs.existsSync(dir) ? fs.readdirSync(dir, { withFileTypes: true }) : [];
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const fullPath = path.join(dir, entry.name);
      const relativePath = rel(fullPath);
      if (shouldSkip(relativePath)) continue;
      if (generatedNames.has(entry.name)) {
        found.push(relativePath);
        continue;
      }
      walk(fullPath);
    }
  }

  for (const root of roots) {
    walk(path.join(repoRoot, root));
  }

  if (found.length) {
    const blocking = found.filter((item) => isGitTracked(item) || !isGitIgnored(item));
    const ignoredLocal = found.filter((item) => !blocking.includes(item));
    if (blocking.length) {
      add("FAIL", "generated-artifacts", "Generated artifact directories must stay out of source lanes", [
        ...blocking.map((item) => `${item} is tracked or not ignored`),
        ...ignoredLocal.map((item) => `${item} is ignored local build output`),
      ]);
    } else {
      add("WARN", "generated-artifacts", "Ignored local generated artifact directories are present but not source", [
        ...ignoredLocal.map((item) => `${item} is ignored by git and not tracked`),
        "No source contract was changed; local build output should stay uncommitted.",
      ]);
    }
  } else {
    add("PASS", "generated-artifacts", "No generated artifact directories found in source lanes", [
      "checked .next, dist, build, .turbo, and coverage outside ignored/runtime locations",
    ]);
  }
}

function checkTrackedLocalState() {
  const tracked = git(["ls-files"]).stdout.split(/\r?\n/).filter(Boolean);
  const trackedDb = tracked.filter((item) => /\.(db|sqlite|sqlite3)$/i.test(item));
  const trackedGeneratedPrisma = tracked.filter((item) => (
    item.includes("node_modules/.prisma/")
    || item.includes("/.prisma/client/")
    || item.includes("\\.prisma\\client\\")
  ));

  if (trackedDb.length || trackedGeneratedPrisma.length) {
    add("FAIL", "tracked-local-state", "Local DB and generated Prisma output must not be tracked", [
      ...trackedDb.map((item) => `tracked db: ${item}`),
      ...trackedGeneratedPrisma.map((item) => `tracked generated Prisma: ${item}`),
    ]);
  } else {
    add("PASS", "tracked-local-state", "No tracked local DB or generated Prisma client output", [
      "git ls-files has no .db/.sqlite/.sqlite3 files",
      "git ls-files has no generated Prisma client output",
    ]);
  }
}

function checkNextEnvChurn() {
  const activeNextEnv = [
    "products/tablet/app/next-env.d.ts",
    "products/pc/app/next-env.d.ts",
    "products/mobile/app/next-env.d.ts",
    "products/chart-lab/app/next-env.d.ts",
  ];
  const status = git(["status", "--short", "--", ...activeNextEnv]).stdout
    .split(/\r?\n/)
    .filter(Boolean);

  if (status.length) {
    add("WARN", "next-env-churn", "Active Next.js generated env files have local drift", [
      ...status,
      "next-env.d.ts is generated by Next.js; preserve it as visible local churn but do not block Round 2 source integrity unless it is intentionally staged.",
    ]);
  } else {
    add("PASS", "next-env-churn", "No active Next.js env-file churn", activeNextEnv);
  }
}

function checkReleaseLaneDocs() {
  const lanesPath = "docs/release/prisma-round2/RELEASE_LANES.md";
  const gatePath = "docs/release/prisma-round2/PRODUCT_INTEGRITY_GATE.md";
  if (!exists(lanesPath) || !exists(gatePath)) {
    add("FAIL", "integrity-docs", "Release lanes and integrity gate docs must exist", [
      `${lanesPath}: ${exists(lanesPath) ? "present" : "missing"}`,
      `${gatePath}: ${exists(gatePath) ? "present" : "missing"}`,
    ]);
    return;
  }

  const lanes = readText(lanesPath);
  const requiredMarkers = [
    "Round 2 Core",
    "Control Center / Phase 5",
    "products/web/app",
    "Off-release",
    "Tablet Core First",
  ];
  const missing = requiredMarkers.filter((marker) => !lanes.includes(marker));
  if (missing.length) {
    add("FAIL", "integrity-docs", "Release lane docs must classify dirty lanes", missing.map((item) => `missing marker: ${item}`));
  } else {
    add("PASS", "integrity-docs", "Release lane and integrity gate docs exist and classify dirty lanes", [
      lanesPath,
      gatePath,
    ]);
  }
}

function checkRound2Contracts() {
  const pkg = readJson("package.json");
  const pcSchema = readText("products/pc/app/prisma/schema.prisma");
  const required = [
    ["verify:round2", "node tools/verify_prisma_round2_productization.mjs"],
    ["verify:product-integrity", "node tools/verify_prisma_product_integrity.mjs"],
  ];
  const scriptProblems = required
    .filter(([name, command]) => pkg.scripts?.[name] !== command)
    .map(([name, command]) => `${name} must be ${command}`);
  const fileProblems = [
    "tools/qa/prisma_round2_readonly_audit.py",
    "tools/verify_prisma_round2_productization.mjs",
    "shared/contracts/prisma-round2-event-map.v1.json",
  ].filter((item) => !exists(item));
  const pcHeaderOk = pcSchema.includes("BUILD-LOCAL NON-CANONICAL COPY")
    && pcSchema.includes("Canonical source of truth");

  if (scriptProblems.length || fileProblems.length || !pcHeaderOk) {
    add("FAIL", "round2-contracts", "Round 2 contracts and gates must remain wired", [
      ...scriptProblems,
      ...fileProblems.map((item) => `missing file: ${item}`),
      pcHeaderOk ? "PC schema header present" : "PC schema non-canonical header missing",
    ]);
  } else {
    add("PASS", "round2-contracts", "Round 2 contracts and gates remain wired", [
      "verify:round2 present",
      "verify:product-integrity present",
      "PC schema is marked build-local and non-canonical",
    ]);
  }
}

function checkScopedDiffWhitespace() {
  const paths = [
    "package.json",
    "pnpm-workspace.yaml",
    "docs/architecture/PRISMA_SCHEMA_OWNERSHIP.md",
    "docs/release/prisma-round2",
    "prisma/schema.prisma",
    "products/pc/app/prisma/schema.prisma",
    "products/tablet/app/prisma/schema.prisma",
    "products/tablet/app/components/reports/contextual-export-actions.tsx",
    "products/tablet/app/components/reports/contextual-export-band.tsx",
    "products/tablet/app/tools/verify_tablet_standalone_core_closeout_02.mjs",
    "shared/contracts/prisma-round2-event-map.v1.json",
    "tools/qa/prisma_round2_readonly_audit.py",
    "tools/verify_prisma_round2_productization.mjs",
    "tools/verify_prisma_product_integrity.mjs",
  ];
  const diffCheck = git(["diff", "--check", "--", ...paths]);
  const output = `${diffCheck.stdout}${diffCheck.stderr}`.trim();
  if (diffCheck.status !== 0) {
    add("FAIL", "scoped-diff-whitespace", "Scoped release diff must be whitespace-clean", output.split(/\r?\n/).filter(Boolean));
  } else {
    add("PASS", "scoped-diff-whitespace", "Scoped release diff is whitespace-clean", [
      "git diff --check passed for Product Integrity and Round 2 release paths",
    ]);
  }
}

function writeReports() {
  fs.mkdirSync(outDir, { recursive: true });
  const pass = results.filter((item) => item.status === "PASS").length;
  const warn = results.filter((item) => item.status === "WARN").length;
  const fail = results.filter((item) => item.status === "FAIL").length;
  const status = fail === 0 ? "GO" : "NO-GO";
  const payload = {
    status,
    counts: { pass, warn, fail },
    repoRoot,
    generatedAt: new Date().toISOString(),
    results,
  };
  fs.writeFileSync(path.join(outDir, "product-integrity-results.json"), `${JSON.stringify(payload, null, 2)}\n`, "utf8");

  const lines = [
    "# PRISMA Round 2.1 Product Integrity Results",
    "",
    `STATUS: ${status}`,
    "",
    `PASS: ${pass}`,
    `WARN: ${warn}`,
    `FAIL: ${fail}`,
    "",
    `Repo root: ${repoRoot}`,
    "",
    "| Status | Check | Evidence |",
    "| --- | --- | --- |",
  ];

  for (const result of results) {
    const evidence = result.evidence.map((item) => String(item).replaceAll("|", "\\|")).join("<br>");
    lines.push(`| ${result.status} | ${result.id} - ${result.title} | ${evidence} |`);
  }

  fs.writeFileSync(path.join(outDir, "PRODUCT_INTEGRITY_RESULTS.md"), `${lines.join("\n")}\n`, "utf8");
  return { status, pass, warn, fail };
}

checkWorkspaceLockfile();
checkGeneratedArtifacts();
checkTrackedLocalState();
checkNextEnvChurn();
checkReleaseLaneDocs();
checkRound2Contracts();
checkScopedDiffWhitespace();

const summary = writeReports();
console.log(`STATUS: ${summary.status}`);
console.log(`PASS: ${summary.pass}`);
console.log(`WARN: ${summary.warn}`);
console.log(`FAIL: ${summary.fail}`);
console.log(`REPORT: ${path.join(outDir, "PRODUCT_INTEGRITY_RESULTS.md")}`);

if (summary.fail > 0) {
  process.exitCode = 1;
}
