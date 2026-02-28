import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TEXT_EXTRACTORS = Object.freeze([
  /(?:^|[^\w])layerId\s*[:=]\s*["'`]([^"'`]+)["'`]/g,
  /data-layer-id\s*=\s*["'`]([^"'`]+)["'`]/g,
  /["'`]layerId["'`]\s*:\s*["'`]([^"'`]+)["'`]/g,
  /@layer\s+([a-z0-9](?:[a-z0-9._-]*[a-z0-9])?)/gi
]);

const STRIP_EDGE_SEPARATORS = /^[._-]+|[._-]+$/g;
const VALID_LAYER_ID = /^[a-z0-9]+(?:[._-][a-z0-9]+)+$/;

export function resolveRepoRoot(importMetaUrl) {
  return path.resolve(path.dirname(fileURLToPath(importMetaUrl)), "../../../../");
}

export function normalizeLayerId(value) {
  const normalized = value.trim().toLowerCase().replace(STRIP_EDGE_SEPARATORS, "");
  return normalized;
}

export function isLayerId(value) {
  return VALID_LAYER_ID.test(value);
}

export function extractLayerIdsFromText(text) {
  const ids = new Set();

  for (const matcher of TEXT_EXTRACTORS) {
    matcher.lastIndex = 0;
    let match = matcher.exec(text);
    while (match) {
      const candidate = normalizeLayerId(match[1] ?? "");
      if (isLayerId(candidate)) {
        ids.add(candidate);
      }
      match = matcher.exec(text);
    }
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}

function shouldScanFile(entryPath) {
  return /\.(?:css|tsx?|jsx?|mjs|cjs|mts|cts)$/.test(entryPath);
}

export function collectFiles(rootDir) {
  if (!fs.existsSync(rootDir)) {
    return [];
  }

  const stack = [rootDir];
  const files = [];

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current) {
      continue;
    }

    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const absolutePath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "dist" || entry.name === "node_modules" || entry.name === "coverage") {
          continue;
        }
        stack.push(absolutePath);
        continue;
      }

      if (entry.isFile() && shouldScanFile(absolutePath)) {
        files.push(absolutePath);
      }
    }
  }

  return files.sort((left, right) => left.localeCompare(right));
}

export function collectUsedLayerIds(filePaths) {
  const usage = new Map();

  for (const filePath of filePaths) {
    const content = fs.readFileSync(filePath, "utf8");
    const ids = extractLayerIdsFromText(content);
    if (ids.length === 0) {
      continue;
    }

    for (const id of ids) {
      const files = usage.get(id) ?? [];
      files.push(filePath);
      usage.set(id, files);
    }
  }

  return usage;
}

export function parseStaticLayerIds(content) {
  const ids = new Set();
  const matcher = /["'`]([a-z0-9](?:[a-z0-9._-]*[a-z0-9])?)["'`]/gi;
  let match = matcher.exec(content);

  while (match) {
    const candidate = normalizeLayerId(match[1] ?? "");
    if (isLayerId(candidate)) {
      ids.add(candidate);
    }
    match = matcher.exec(content);
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}

export function firstExistingPath(paths) {
  for (const candidate of paths) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

export function toRelativePosix(rootDir, targetPath) {
  return path.relative(rootDir, targetPath).split(path.sep).join("/");
}
