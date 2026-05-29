#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");
const defaultCodeownersPath = path.join(repoRoot, ".github", "CODEOWNERS");

const SENSITIVE_PATH_PREFIXES = [
  ".github/workflows/",
  "apps/keystone/app/api/",
  "services/",
  "packages/contracts/",
  "tools/codex/",
  "tools/graphviz/",
  "tools/hos/",
  "terraform/",
  "helm/",
  "k8s/",
  "policies/"
];

function toPosix(value) {
  return value.replace(/\\/g, "/");
}

function parseArgs(argv) {
  const args = {
    codeowners: defaultCodeownersPath,
    output: null
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--codeowners" && next) {
      args.codeowners = path.resolve(repoRoot, next);
      index += 1;
      continue;
    }

    if (token === "--output" && next) {
      args.output = next;
      index += 1;
    }
  }

  return args;
}

function codeownersPatternToRegex(pattern) {
  let normalized = pattern.trim();
  if (normalized.length === 0) {
    return null;
  }

  if (normalized.endsWith("/")) {
    normalized = `${normalized}**`;
  }

  const anchored = normalized.startsWith("/");
  if (anchored) {
    normalized = normalized.slice(1);
  }

  const escaped = normalized
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*\*/g, "__DOUBLE_STAR__")
    .replace(/\*/g, "__SINGLE_STAR__")
    .replace(/\?/g, "__QMARK__");

  const regexBody = escaped
    .replace(/__DOUBLE_STAR__/g, ".*")
    .replace(/__SINGLE_STAR__/g, "[^/]*")
    .replace(/__QMARK__/g, "[^/]");

  const prefix = anchored ? "^" : "(^|.*/)";
  return new RegExp(`${prefix}${regexBody}$`);
}

function parseCodeowners(codeownersPath) {
  const entries = [];
  const text = readFileSync(codeownersPath, "utf8");
  const lines = text.split(/\r?\n/);

  for (let lineNumber = 0; lineNumber < lines.length; lineNumber += 1) {
    const rawLine = lines[lineNumber];
    const withoutComments = rawLine.split("#", 1)[0].trim();
    if (withoutComments.length === 0) {
      continue;
    }

    const parts = withoutComments.split(/\s+/).filter((value) => value.length > 0);
    if (parts.length < 2) {
      continue;
    }

    const pattern = parts[0];
    const owners = parts.slice(1);
    const regex = codeownersPatternToRegex(pattern);
    if (!regex) {
      continue;
    }

    entries.push({
      line: lineNumber + 1,
      pattern,
      owners,
      regex
    });
  }

  return entries;
}

function listTrackedFiles() {
  const output = execFileSync("git", ["ls-files"], {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 128 * 1024 * 1024,
    stdio: ["ignore", "pipe", "pipe"]
  });

  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => toPosix(line))
    .sort((left, right) => left.localeCompare(right));
}

function matchOwners(entries, relativePath) {
  let matchedOwners = null;
  for (const entry of entries) {
    if (entry.regex.test(relativePath)) {
      matchedOwners = entry.owners;
    }
  }
  return matchedOwners;
}

function computeCoverage(entries, trackedFiles) {
  const ownership = trackedFiles.map((filePath) => {
    const owners = matchOwners(entries, filePath);
    return {
      file: filePath,
      owners
    };
  });

  const unowned = ownership.filter((item) => item.owners === null).map((item) => item.file);
  const ownerSet = new Set();
  for (const item of ownership) {
    for (const owner of item.owners ?? []) {
      ownerSet.add(owner);
    }
  }

  const sensitivePaths = SENSITIVE_PATH_PREFIXES.map((prefix) => {
    const matchedFiles = ownership.filter((item) => item.file.startsWith(prefix));
    const unmatchedCount = matchedFiles.filter((item) => item.owners === null).length;
    const ownerSetForPrefix = new Set();
    for (const file of matchedFiles) {
      for (const owner of file.owners ?? []) {
        ownerSetForPrefix.add(owner);
      }
    }

    return {
      path_prefix: prefix,
      file_count: matchedFiles.length,
      unowned_file_count: unmatchedCount,
      owners: [...ownerSetForPrefix].sort((left, right) => left.localeCompare(right))
    };
  });

  const ownedCount = ownership.length - unowned.length;
  const coverage = ownership.length === 0 ? 100 : (ownedCount / ownership.length) * 100;

  return {
    ownership,
    unowned,
    owners: [...ownerSet].sort((left, right) => left.localeCompare(right)),
    sensitivePaths,
    ownedCount,
    totalCount: ownership.length,
    coverage
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const codeownersPath = args.codeowners;

  if (!existsSync(codeownersPath)) {
    process.stderr.write(`[codeowners] file not found: ${toPosix(path.relative(repoRoot, codeownersPath))}\n`);
    process.exit(2);
  }

  const entries = parseCodeowners(codeownersPath);
  const trackedFiles = listTrackedFiles();
  const coverage = computeCoverage(entries, trackedFiles);

  const report = {
    schema_version: 1,
    generated_at_utc: new Date().toISOString(),
    codeowners_path: toPosix(path.relative(repoRoot, codeownersPath)),
    codeowners_entry_count: entries.length,
    tracked_file_count: coverage.totalCount,
    owned_file_count: coverage.ownedCount,
    unowned_file_count: coverage.unowned.length,
    coverage_percent: Number(coverage.coverage.toFixed(2)),
    owner_count: coverage.owners.length,
    owners: coverage.owners,
    single_owner_mode: coverage.owners.length === 1,
    unowned_samples: coverage.unowned.slice(0, 200),
    sensitive_path_coverage: coverage.sensitivePaths
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }
}

main();
