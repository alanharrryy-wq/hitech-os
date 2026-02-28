import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const STRING_LITERAL_PATTERN = /(?:"([^"\\]*(?:\\.[^"\\]*)*)"|'([^'\\]*(?:\\.[^'\\]*)*)'|`([^`\\]*(?:\\.[^`\\]*)*)`)/g;
const INLINE_WS = /\s+/g;
const PUNCT_TRIM = /^[\s\-_,.:;!?()\[\]{}'"`]+|[\s\-_,.:;!?()\[\]{}'"`]+$/g;
const REPO_SKIP_DIRS = new Set(["node_modules", "dist", "coverage", ".next", ".turbo"]);
const MIN_HUMAN_LEN = 14;

export function resolveRepoRoot(importMetaUrl) {
  return path.resolve(path.dirname(fileURLToPath(importMetaUrl)), "../../../../");
}

export function normalizeHumanPhrase(value) {
  return value
    .replace(/\\n/g, " ")
    .replace(/\\r/g, " ")
    .replace(/\\t/g, " ")
    .replace(INLINE_WS, " ")
    .replace(PUNCT_TRIM, "")
    .trim()
    .toLowerCase();
}

export function looksLikeHumanCopy(value) {
  const normalized = normalizeHumanPhrase(value);
  if (normalized.length < MIN_HUMAN_LEN) {
    return false;
  }

  if (!/[a-z]/.test(normalized)) {
    return false;
  }

  if (/[{}<>$]|https?:\/\//.test(normalized)) {
    return false;
  }

  const words = normalized.split(" ").filter((chunk) => chunk.length > 0);
  if (words.length < 3) {
    return false;
  }

  const alphaWords = words.filter((chunk) => /[a-z]/.test(chunk));
  if (alphaWords.length < 3) {
    return false;
  }

  return true;
}

export function extractStringLiterals(sourceText) {
  const values = [];
  STRING_LITERAL_PATTERN.lastIndex = 0;

  let match = STRING_LITERAL_PATTERN.exec(sourceText);
  while (match) {
    const raw = match[1] ?? match[2] ?? match[3] ?? "";
    if (raw.length > 0) {
      values.push(raw);
    }
    match = STRING_LITERAL_PATTERN.exec(sourceText);
  }

  return values;
}

export function collectFiles(rootDir, includePattern = /\.(?:ts|tsx|js|jsx|mjs|cjs)$/) {
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
        if (REPO_SKIP_DIRS.has(entry.name)) {
          continue;
        }
        stack.push(absPath);
        continue;
      }

      if (entry.isFile() && includePattern.test(absPath)) {
        files.push(absPath);
      }
    }
  }

  return files.sort((left, right) => left.localeCompare(right));
}

export function firstExisting(paths) {
  for (const candidate of paths) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return null;
}

export function collectAllowedPhrases(candidateFiles) {
  const allowed = new Set();

  for (const filePath of candidateFiles) {
    if (!fs.existsSync(filePath)) {
      continue;
    }

    const content = fs.readFileSync(filePath, "utf8");
    const literals = extractStringLiterals(content);

    for (const literal of literals) {
      if (!looksLikeHumanCopy(literal)) {
        continue;
      }
      allowed.add(normalizeHumanPhrase(literal));
    }
  }

  return allowed;
}

export function analyzePitchHardcodeViolations(input) {
  const { sourceFiles, allowedPhrases } = input;
  const violations = [];

  for (const filePath of sourceFiles) {
    const content = fs.readFileSync(filePath, "utf8");
    const literals = extractStringLiterals(content);

    for (const literal of literals) {
      if (!looksLikeHumanCopy(literal)) {
        continue;
      }

      const normalized = normalizeHumanPhrase(literal);
      if (!allowedPhrases.has(normalized)) {
        violations.push({
          filePath,
          literal,
          normalized
        });
      }
    }
  }

  return violations;
}

export function toRelativePosix(rootDir, absPath) {
  return path.relative(rootDir, absPath).split(path.sep).join("/");
}
