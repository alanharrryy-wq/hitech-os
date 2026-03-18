#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");
const defaultCodeownersPath = path.join(repoRoot, ".github", "CODEOWNERS");

function toPosix(value) {
  return value.replace(/\\/g, "/");
}

function parseArgs(argv) {
  const args = {
    base: process.env.AFFECTED_BASE ?? null,
    head: process.env.AFFECTED_HEAD ?? "HEAD",
    policy: "policies/security.json",
    codeowners: defaultCodeownersPath,
    output: null,
    strict: false,
    useTripleDot: true
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--base" && next) {
      args.base = next;
      index += 1;
      continue;
    }

    if (token === "--head" && next) {
      args.head = next;
      index += 1;
      continue;
    }

    if (token === "--policy" && next) {
      args.policy = next;
      index += 1;
      continue;
    }

    if (token === "--codeowners" && next) {
      args.codeowners = path.resolve(repoRoot, next);
      index += 1;
      continue;
    }

    if (token === "--output" && next) {
      args.output = next;
      index += 1;
      continue;
    }

    if (token === "--strict") {
      args.strict = true;
      continue;
    }

    if (token === "--two-dot") {
      args.useTripleDot = false;
      continue;
    }
  }

  if (!args.base) {
    args.base = "HEAD~1";
  }

  return args;
}

function readJson(relativePath) {
  return JSON.parse(readFileSync(path.resolve(repoRoot, relativePath), "utf8"));
}

function runGitDiff(base, head, tripleDot) {
  const refs = tripleDot ? `${base}...${head}` : `${base}..${head}`;
  const output = execFileSync("git", ["diff", "--name-only", refs], {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });

  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => toPosix(line));
}

function collectChangedFiles(base, head, preferTripleDot) {
  if (preferTripleDot) {
    try {
      return {
        mode: "triple-dot",
        files: runGitDiff(base, head, true)
      };
    } catch {
      return {
        mode: "two-dot-fallback",
        files: runGitDiff(base, head, false)
      };
    }
  }

  return {
    mode: "two-dot",
    files: runGitDiff(base, head, false)
  };
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
    .replace(/[.+^${}()|[\\]\\]/g, "\\$&")
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
  if (!existsSync(codeownersPath)) {
    return [];
  }

  const entries = [];
  const lines = readFileSync(codeownersPath, "utf8").split(/\r?\n/);

  for (let lineNumber = 0; lineNumber < lines.length; lineNumber += 1) {
    const raw = lines[lineNumber];
    const value = raw.split("#", 1)[0].trim();
    if (!value) {
      continue;
    }

    const parts = value.split(/\s+/).filter((item) => item.length > 0);
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

function matchOwners(entries, relativePath) {
  let matchedOwners = null;
  for (const entry of entries) {
    if (entry.regex.test(relativePath)) {
      matchedOwners = entry.owners;
    }
  }
  return matchedOwners;
}

function fileIsText(content) {
  return !content.includes("\u0000");
}

function shouldScanFile(relativePath, includeExtensions) {
  const extension = path.extname(relativePath).toLowerCase();
  if (extension && includeExtensions.has(extension)) {
    return true;
  }

  if (!extension && path.basename(relativePath).toLowerCase().includes("env")) {
    return true;
  }

  return false;
}

function compilePatterns(policyPatterns) {
  const patterns = [];
  for (const item of policyPatterns) {
    if (!item || typeof item !== "object") {
      continue;
    }

    const id = String(item.id ?? "pattern");
    const raw = String(item.regex ?? "");
    if (!raw) {
      continue;
    }

    try {
      patterns.push({ id, regex: new RegExp(raw, "g") });
    } catch {
      // ignore invalid regex in policy report mode
    }
  }
  return patterns;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const policy = readJson(args.policy);

  const sensitivePrefixes = Array.isArray(policy.sensitive_path_prefixes)
    ? policy.sensitive_path_prefixes
    : [];

  const scanConfig = policy.secret_scan ?? {};
  const includeExtensions = new Set(
    Array.isArray(scanConfig.include_extensions)
      ? scanConfig.include_extensions.map((value) => String(value).toLowerCase())
      : []
  );
  const scanMaxFileBytes = Number(scanConfig.scan_max_file_bytes ?? 1024 * 1024);
  const scanEnabled = scanConfig.enabled !== false;
  const patterns = compilePatterns(
    Array.isArray(scanConfig.high_confidence_patterns) ? scanConfig.high_confidence_patterns : []
  );

  const { mode, files: changedFiles } = collectChangedFiles(args.base, args.head, args.useTripleDot);
  const sensitiveChanges = changedFiles.filter((filePath) =>
    sensitivePrefixes.some((prefix) => filePath.startsWith(prefix))
  );

  const codeownersEntries = parseCodeowners(args.codeowners);
  const sensitiveOwnership = sensitiveChanges.map((filePath) => {
    const owners = matchOwners(codeownersEntries, filePath);
    return {
      file: filePath,
      owners
    };
  });

  const sensitiveUnowned = sensitiveOwnership
    .filter((entry) => entry.owners === null)
    .map((entry) => entry.file);

  const sensitiveOwnerSet = new Set();
  for (const entry of sensitiveOwnership) {
    for (const owner of entry.owners ?? []) {
      sensitiveOwnerSet.add(owner);
    }
  }

  const findings = [];
  const scannedFiles = [];
  if (scanEnabled && patterns.length > 0) {
    for (const relativePath of changedFiles) {
      if (!shouldScanFile(relativePath, includeExtensions)) {
        continue;
      }

      const absolutePath = path.join(repoRoot, relativePath);
      if (!existsSync(absolutePath)) {
        continue;
      }

      const stats = statSync(absolutePath);
      if (stats.size > scanMaxFileBytes) {
        continue;
      }

      const content = readFileSync(absolutePath, "utf8");
      if (!fileIsText(content)) {
        continue;
      }

      scannedFiles.push(relativePath);

      for (const pattern of patterns) {
        pattern.regex.lastIndex = 0;
        let match = pattern.regex.exec(content);
        while (match) {
          const full = match[0] ?? "";
          const start = match.index;
          const line = content.slice(0, start).split(/\r?\n/).length;
          findings.push({
            file: relativePath,
            pattern_id: pattern.id,
            line,
            excerpt: full.slice(0, 80)
          });
          match = pattern.regex.exec(content);
        }
      }
    }
  }

  findings.sort((left, right) => {
    const byFile = left.file.localeCompare(right.file);
    if (byFile !== 0) {
      return byFile;
    }
    const byPattern = left.pattern_id.localeCompare(right.pattern_id);
    if (byPattern !== 0) {
      return byPattern;
    }
    return left.line - right.line;
  });

  const strictShouldFail = args.strict && (sensitiveUnowned.length > 0 || findings.length > 0);

  const report = {
    schema_version: 1,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    codeowners_path: toPosix(path.relative(repoRoot, path.resolve(args.codeowners))),
    diff: {
      base: args.base,
      head: args.head,
      mode,
      changed_file_count: changedFiles.length
    },
    strict_mode: args.strict,
    sensitive_paths: {
      changed_count: sensitiveChanges.length,
      changed_files: sensitiveChanges,
      unowned_count: sensitiveUnowned.length,
      unowned_files: sensitiveUnowned,
      owner_count: sensitiveOwnerSet.size,
      single_owner_mode: sensitiveOwnerSet.size === 1,
      ownership: sensitiveOwnership
    },
    secret_scan: {
      enabled: scanEnabled,
      scanned_file_count: scannedFiles.length,
      finding_count: findings.length,
      findings: findings.slice(0, 500)
    },
    status:
      sensitiveUnowned.length === 0 && findings.length === 0
        ? "pass"
        : args.strict
          ? "fail"
          : "warn"
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (strictShouldFail) {
    process.stderr.write("[sensitive-paths] FAILED\n");
    process.exit(1);
  }
}

main();
