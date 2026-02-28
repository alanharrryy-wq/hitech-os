import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PATTERNS = Object.freeze([
  /layerId\s*[:=]\s*["'`]([a-z0-9._-]+)["'`]/gi,
  /data-layer-id\s*=\s*["'`]([a-z0-9._-]+)["'`]/gi,
  /data-layer-([a-z0-9-]+)\s*=\s*["'`](?:on|off)["'`]/gi,
  /(?:[?&]layers=)([^\s"'`]+)/gi,
  /@layer\s+([a-z0-9._-]+)/gi
]);

const VALID_LAYER_ID = /^[a-z0-9]+(?:[._-][a-z0-9]+)+$/;
const SKIP_DIRS = new Set(["node_modules", "dist", "coverage", ".next", ".turbo"]);

export function resolveRepoRoot(importMetaUrl) {
  return path.resolve(path.dirname(fileURLToPath(importMetaUrl)), "../../../../");
}

export function normalizeLayerId(value) {
  return value.trim().toLowerCase().replace(/-/g, ".").replace(/^\.+|\.+$/g, "");
}

export function extractLayerIdsFromText(sourceText) {
  const ids = new Set();

  for (const pattern of PATTERNS) {
    pattern.lastIndex = 0;
    let match = pattern.exec(sourceText);
    while (match) {
      const capture = match[1] ?? "";

      if (pattern.source.includes("layers=")) {
        const values = capture.split(/[;,]/g).map((entry) => normalizeLayerId(entry));
        for (const candidate of values) {
          if (candidate === "all" || candidate === "none" || candidate.length === 0) {
            continue;
          }
          if (VALID_LAYER_ID.test(candidate)) {
            ids.add(candidate);
          }
        }
      } else {
        const normalized = normalizeLayerId(capture);
        if (VALID_LAYER_ID.test(normalized)) {
          ids.add(normalized);
        }
      }

      match = pattern.exec(sourceText);
    }
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}

export function collectFiles(rootDir, extensionPattern = /\.(?:ts|tsx|js|jsx|mjs|cjs|css)$/) {
  if (!fs.existsSync(rootDir)) {
    return [];
  }

  const files = [];
  const stack = [rootDir];

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current) {
      continue;
    }

    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const absPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(entry.name)) {
          continue;
        }
        stack.push(absPath);
        continue;
      }

      if (entry.isFile() && extensionPattern.test(absPath)) {
        files.push(absPath);
      }
    }
  }

  return files.sort((left, right) => left.localeCompare(right));
}

export function parseCanonicalLayerIds(candidatePaths) {
  const literals = new Set();

  for (const candidatePath of candidatePaths) {
    if (!fs.existsSync(candidatePath)) {
      continue;
    }

    const content = fs.readFileSync(candidatePath, "utf8");
    const literalPattern = /["'`]([a-z0-9](?:[a-z0-9._-]*[a-z0-9])?)["'`]/gi;
    literalPattern.lastIndex = 0;

    let match = literalPattern.exec(content);
    while (match) {
      const normalized = normalizeLayerId(match[1] ?? "");
      if (VALID_LAYER_ID.test(normalized)) {
        literals.add(normalized);
      }
      match = literalPattern.exec(content);
    }
  }

  return [...literals].sort((left, right) => left.localeCompare(right));
}

export function collectUsedLayerIds(filePaths) {
  const usage = new Map();

  for (const filePath of filePaths) {
    const content = fs.readFileSync(filePath, "utf8");
    const ids = extractLayerIdsFromText(content);

    for (const id of ids) {
      const hitList = usage.get(id) ?? [];
      hitList.push(filePath);
      usage.set(id, hitList);
    }
  }

  return usage;
}

export function toRelativePosix(rootDir, absPath) {
  return path.relative(rootDir, absPath).split(path.sep).join("/");
}
