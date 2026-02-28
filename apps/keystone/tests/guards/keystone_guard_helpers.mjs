import fs from "node:fs";
import path from "node:path";

const PATTERNS = Object.freeze([
  /(?:^|[^\w])layerId\s*[:=]\s*["'`]([^"'`]+)["'`]/g,
  /data-layer-id\s*=\s*["'`]([^"'`]+)["'`]/g,
  /@layer\s+([a-z0-9](?:[a-z0-9._-]*[a-z0-9])?)/gi
]);

const VALID = /^[a-z0-9]+(?:[._-][a-z0-9]+)+$/;

export function findFiles(rootDir, extensionPattern = /\.(?:ts|tsx|js|jsx|css|mjs|cjs)$/) {
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

    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (entry.name === "node_modules" || entry.name === "dist") {
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

export function extractLayerIds(content) {
  const ids = new Set();

  for (const pattern of PATTERNS) {
    pattern.lastIndex = 0;
    let match = pattern.exec(content);
    while (match) {
      const id = (match[1] ?? "").trim().toLowerCase();
      if (VALID.test(id)) {
        ids.add(id);
      }
      match = pattern.exec(content);
    }
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}

export function parseLayerIdsRegistry(content) {
  const ids = new Set();
  const pattern = /["'`]([a-z0-9](?:[a-z0-9._-]*[a-z0-9])?)["'`]/gi;

  pattern.lastIndex = 0;
  let match = pattern.exec(content);
  while (match) {
    const id = (match[1] ?? "").trim().toLowerCase();
    if (VALID.test(id)) {
      ids.add(id);
    }
    match = pattern.exec(content);
  }

  return [...ids].sort((left, right) => left.localeCompare(right));
}
