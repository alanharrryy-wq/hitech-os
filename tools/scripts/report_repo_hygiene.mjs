#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");

const GENERATED_PREFIXES = [
  "tools/graphviz/graphs/",
  "tools/_local/",
  "_reports/",
  ".repo_map/",
  "docs/knowledge/codex_chats/",
  "artifacts/"
];

const BINARY_EXTENSIONS = new Set([
  ".png",
  ".jpg",
  ".jpeg",
  ".gif",
  ".webp",
  ".zip",
  ".7z",
  ".gz",
  ".sqlite",
  ".pdf",
  ".mp4",
  ".mov",
  ".exe",
  ".dll"
]);

function toPosix(value) {
  return value.replace(/\\/g, "/");
}

function parseArgs(argv) {
  const args = {
    output: null,
    warnMb: 5,
    lfsMb: 20,
    strict: false
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--output" && next) {
      args.output = next;
      index += 1;
      continue;
    }

    if (token === "--warn-mb" && next) {
      args.warnMb = Number(next);
      index += 1;
      continue;
    }

    if (token === "--lfs-mb" && next) {
      args.lfsMb = Number(next);
      index += 1;
      continue;
    }

    if (token === "--strict") {
      args.strict = true;
    }
  }

  return args;
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
    .map((line) => toPosix(line));
}

function getIsShallow() {
  try {
    const output = execFileSync("git", ["rev-parse", "--is-shallow-repository"], {
      cwd: repoRoot,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"]
    });
    return output.trim() === "true";
  } catch {
    return null;
  }
}

function toMb(bytes) {
  return Number((bytes / (1024 * 1024)).toFixed(2));
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const trackedFiles = listTrackedFiles();

  const warnBytes = Math.max(1, args.warnMb) * 1024 * 1024;
  const lfsBytes = Math.max(args.warnMb, args.lfsMb) * 1024 * 1024;

  const sizeRows = [];
  for (const relativePath of trackedFiles) {
    const absolutePath = path.join(repoRoot, relativePath);
    if (!existsSync(absolutePath)) {
      continue;
    }

    const stats = statSync(absolutePath);
    if (!stats.isFile()) {
      continue;
    }

    sizeRows.push({
      file: relativePath,
      size_bytes: stats.size,
      extension: path.extname(relativePath).toLowerCase()
    });
  }

  const largeFiles = sizeRows
    .filter((row) => row.size_bytes >= warnBytes)
    .sort((left, right) => right.size_bytes - left.size_bytes);

  const generatedTracked = sizeRows.filter((row) =>
    GENERATED_PREFIXES.some((prefix) => row.file.startsWith(prefix))
  );

  const lfsCandidates = sizeRows
    .filter((row) => row.size_bytes >= lfsBytes)
    .filter((row) => BINARY_EXTENSIONS.has(row.extension) || row.extension === "")
    .sort((left, right) => right.size_bytes - left.size_bytes);

  const topDirectories = new Map();
  for (const row of sizeRows) {
    const top = row.file.split("/", 1)[0] ?? "root";
    topDirectories.set(top, (topDirectories.get(top) ?? 0) + row.size_bytes);
  }

  const topDirectoryRows = [...topDirectories.entries()]
    .map(([directory, sizeBytes]) => ({ directory, size_mb: toMb(sizeBytes) }))
    .sort((left, right) => right.size_mb - left.size_mb)
    .slice(0, 20);

  const strictShouldFail = args.strict && largeFiles.some((row) => row.size_bytes >= 50 * 1024 * 1024);

  const report = {
    schema_version: 1,
    generated_at_utc: new Date().toISOString(),
    repository: {
      root: toPosix(repoRoot),
      tracked_file_count: sizeRows.length,
      shallow_history: getIsShallow()
    },
    thresholds: {
      large_file_warn_mb: args.warnMb,
      lfs_candidate_mb: args.lfsMb
    },
    counts: {
      large_file_count: largeFiles.length,
      generated_prefix_tracked_count: generatedTracked.length,
      lfs_candidate_count: lfsCandidates.length
    },
    top_directories_by_size_mb: topDirectoryRows,
    large_files: largeFiles.slice(0, 200).map((row) => ({
      file: row.file,
      size_mb: toMb(row.size_bytes)
    })),
    generated_prefix_tracked_samples: generatedTracked.slice(0, 200).map((row) => ({
      file: row.file,
      size_mb: toMb(row.size_bytes)
    })),
    lfs_candidate_samples: lfsCandidates.slice(0, 200).map((row) => ({
      file: row.file,
      size_mb: toMb(row.size_bytes)
    })),
    recommendations: [
      "Keep generated artifacts out of tracked source paths when possible.",
      "Use Git LFS for very large binary assets that must stay in-repo.",
      "Prefer sparse-checkout and partial clone for contributors focused on runtime code only."
    ],
    status: strictShouldFail ? "fail" : largeFiles.length > 0 || generatedTracked.length > 0 ? "warn" : "pass"
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (strictShouldFail) {
    process.stderr.write("[repo-hygiene] FAILED: very large tracked files detected\n");
    process.exit(1);
  }
}

main();
