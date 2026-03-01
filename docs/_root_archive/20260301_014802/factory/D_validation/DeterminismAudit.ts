import * as path from "node:path";
import { FACTORY_BLOCK_SEQUENCE, FeatureFlags } from "../contracts/FactoryContracts";
import { JsonObject } from "../shared/DeterministicJson";

export type DeterminismViolationCode =
  | "TEMPORAL_USAGE"
  | "NON_DETERMINISTIC_API"
  | "CROSS_MODULE_IMPORT";

export interface DeterminismViolation {
  readonly code: DeterminismViolationCode;
  readonly filePath: string;
  readonly line: number;
  readonly message: string;
}

export interface DeterminismAuditReport {
  readonly passed: boolean;
  readonly violations: readonly DeterminismViolation[];
  readonly summary: JsonObject;
}

export interface DeterminismAuditInput {
  readonly files: Readonly<Record<string, string>>;
  readonly featureFlags: FeatureFlags;
}

interface PatternDefinition {
  readonly code: DeterminismViolationCode;
  readonly expression: RegExp;
  readonly message: string;
}

const TEMPORAL_PATTERNS: readonly PatternDefinition[] = [
  {
    code: "TEMPORAL_USAGE",
    expression: /\bDate\.now\s*\(/,
    message: "Date.now introduces temporal dependency.",
  },
  {
    code: "TEMPORAL_USAGE",
    expression: /\bnew\s+Date\s*\(/,
    message: "new Date introduces temporal dependency.",
  },
  {
    code: "TEMPORAL_USAGE",
    expression: /\bperformance\.now\s*\(/,
    message: "performance.now introduces temporal dependency.",
  },
  {
    code: "TEMPORAL_USAGE",
    expression: /\bsetTimeout\s*\(/,
    message: "setTimeout is non-deterministic for orchestration.",
  },
  {
    code: "TEMPORAL_USAGE",
    expression: /\bsetInterval\s*\(/,
    message: "setInterval is non-deterministic for orchestration.",
  },
];

const NON_DETERMINISTIC_PATTERNS: readonly PatternDefinition[] = [
  {
    code: "NON_DETERMINISTIC_API",
    expression: /\bMath\.random\s*\(/,
    message: "Math.random introduces non-determinism.",
  },
  {
    code: "NON_DETERMINISTIC_API",
    expression: /\bcrypto\.randomUUID\s*\(/,
    message: "randomUUID introduces non-determinism.",
  },
  {
    code: "NON_DETERMINISTIC_API",
    expression: /\bcrypto\.randomBytes\s*\(/,
    message: "randomBytes introduces non-determinism.",
  },
];

const IMPORT_PATTERN = /(?:import|export)\s+[^'"]*from\s+["']([^"']+)["']/g;

function normalizeFilePath(filePath: string): string {
  return filePath.replace(/\\/g, "/");
}

function detectLineNumbers(content: string, expression: RegExp): readonly number[] {
  const lines = content.split(/\r?\n/);
  const lineNumbers: number[] = [];
  for (const [index, line] of lines.entries()) {
    expression.lastIndex = 0;
    if (expression.test(line)) {
      lineNumbers.push(index + 1);
    }
  }
  return lineNumbers;
}

function pushPatternViolations(
  violations: DeterminismViolation[],
  filePath: string,
  content: string,
  patterns: readonly PatternDefinition[],
): void {
  for (const pattern of patterns) {
    const lines = detectLineNumbers(content, pattern.expression);
    for (const line of lines) {
      violations.push({
        code: pattern.code,
        filePath,
        line,
        message: pattern.message,
      });
    }
  }
}

function resolveImportPath(sourcePath: string, specifier: string): string {
  if (specifier.startsWith(".")) {
    return normalizeFilePath(
      path.posix.normalize(path.posix.join(path.posix.dirname(sourcePath), specifier)),
    );
  }
  return normalizeFilePath(specifier);
}

function inferFactoryBlock(filePath: string): string | null {
  const normalizedPath = normalizeFilePath(filePath);
  for (const blockId of FACTORY_BLOCK_SEQUENCE) {
    if (normalizedPath.includes(`/factory/${blockId}/`) || normalizedPath.startsWith(`factory/${blockId}/`)) {
      return blockId;
    }
  }
  return null;
}

function isAllowedSharedImport(resolvedImportPath: string): boolean {
  return (
    resolvedImportPath.includes("/factory/contracts/") ||
    resolvedImportPath.includes("/factory/shared/") ||
    resolvedImportPath.startsWith("factory/contracts/") ||
    resolvedImportPath.startsWith("factory/shared/")
  );
}

function detectCrossModuleImports(
  sourceFilePath: string,
  content: string,
): readonly DeterminismViolation[] {
  const sourceBlock = inferFactoryBlock(sourceFilePath);
  if (sourceBlock === null) {
    return [];
  }

  const violations: DeterminismViolation[] = [];
  const lines = content.split(/\r?\n/);
  for (const [lineIndex, line] of lines.entries()) {
    IMPORT_PATTERN.lastIndex = 0;
    const match = IMPORT_PATTERN.exec(line);
    if (match === null) {
      continue;
    }
    const specifier = match[1];
    if (specifier === undefined) {
      continue;
    }

    const resolved = resolveImportPath(normalizeFilePath(sourceFilePath), specifier);
    if (isAllowedSharedImport(resolved)) {
      continue;
    }

    const targetBlock = inferFactoryBlock(resolved);
    if (targetBlock !== null && targetBlock !== sourceBlock) {
      violations.push({
        code: "CROSS_MODULE_IMPORT",
        filePath: sourceFilePath,
        line: lineIndex + 1,
        message: `Cross-module import from ${sourceBlock} to ${targetBlock} is forbidden.`,
      });
    }
  }

  return violations;
}

function compareViolations(left: DeterminismViolation, right: DeterminismViolation): number {
  const byFilePath = left.filePath.localeCompare(right.filePath);
  if (byFilePath !== 0) {
    return byFilePath;
  }
  const byLine = left.line - right.line;
  if (byLine !== 0) {
    return byLine;
  }
  return left.code.localeCompare(right.code);
}

export class DeterminismAudit {
  run(input: DeterminismAuditInput): DeterminismAuditReport {
    const violations: DeterminismViolation[] = [];
    const filePaths = Object.keys(input.files).sort((left, right) => left.localeCompare(right));

    for (const filePath of filePaths) {
      const content = input.files[filePath];
      if (content === undefined) {
        continue;
      }

      if (!input.featureFlags.allowTemporalSignals) {
        pushPatternViolations(violations, filePath, content, TEMPORAL_PATTERNS);
      }
      if (!input.featureFlags.allowNonDeterministicApis) {
        pushPatternViolations(violations, filePath, content, NON_DETERMINISTIC_PATTERNS);
      }
      if (!input.featureFlags.allowCrossModuleImports) {
        violations.push(...detectCrossModuleImports(filePath, content));
      }
    }

    const sortedViolations = violations.sort(compareViolations);
    const summary: JsonObject = {
      fileCount: filePaths.length,
      violationCount: sortedViolations.length,
      temporalViolations: sortedViolations.filter((item) => item.code === "TEMPORAL_USAGE").length,
      nondeterministicViolations: sortedViolations.filter((item) => item.code === "NON_DETERMINISTIC_API")
        .length,
      crossModuleViolations: sortedViolations.filter((item) => item.code === "CROSS_MODULE_IMPORT").length,
    };

    return {
      passed: sortedViolations.length === 0,
      violations: sortedViolations,
      summary,
    };
  }
}
