import {
  Dirent,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from "node:fs";
import * as path from "node:path";

type ComponentState = "PRESENT" | "MISSING" | "UNKNOWN";

interface ModuleEntry {
  readonly state: ComponentState;
  readonly files: readonly string[];
}

interface FileGroup {
  readonly state: ComponentState;
  readonly files: readonly string[];
}

interface WorkspaceManager {
  readonly package_manager: string;
  readonly workspace_file: string;
  readonly workspace_file_state: ComponentState;
  readonly workspace_packages: readonly string[];
}

interface SmokeSnapshot {
  readonly tests_smoke_state: ComponentState;
  readonly tests_smoke_files: readonly string[];
  readonly run_factory_smoke_ps1_state: ComponentState;
  readonly smoke_commands: readonly string[];
}

interface HealthChecksSnapshot {
  readonly state: ComponentState;
  readonly commands: readonly string[];
  readonly script_refs: readonly string[];
}

interface SnapshotMini {
  readonly schema_version: "1.0.0";
  readonly workspace_manager: WorkspaceManager;
  readonly root_scripts: Readonly<Record<string, string>>;
  readonly factory_modules: Readonly<Record<FactoryModuleName, ModuleEntry>>;
  readonly factory_contracts: FileGroup;
  readonly factory_configs: FileGroup;
  readonly smoke: SmokeSnapshot;
  readonly health_checks: HealthChecksSnapshot;
  readonly notes_unknowns: readonly string[];
}

type FactoryModuleName =
  | "A_core"
  | "B_tooling"
  | "C_features"
  | "D_validation"
  | "Z_aggregator";

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | readonly JsonValue[] | { readonly [key: string]: JsonValue };

const EXPECTED_FACTORY_MODULES: readonly FactoryModuleName[] = [
  "A_core",
  "B_tooling",
  "C_features",
  "D_validation",
  "Z_aggregator",
];

const SNAPSHOT_RELATIVE_PATH = "docs/snapshots/HITECH_OS__SNAPSHOT_MINI.json";
const WORKSPACE_FILE_RELATIVE_PATH = "pnpm-workspace.yaml";

function normalizeRepoPath(value: string): string {
  return value.replace(/\\/g, "/");
}

function sortUnique(values: readonly string[]): readonly string[] {
  return Array.from(new Set(values)).sort((left, right) => left.localeCompare(right));
}

function tryGetStat(absolutePath: string): ReturnType<typeof statSync> | undefined {
  try {
    return statSync(absolutePath);
  } catch {
    return undefined;
  }
}

function detectPathState(absolutePath: string, expectedType: "file" | "directory"): ComponentState {
  const stats = tryGetStat(absolutePath);
  if (stats === undefined) {
    return "MISSING";
  }
  if (expectedType === "file" && stats.isFile()) {
    return "PRESENT";
  }
  if (expectedType === "directory" && stats.isDirectory()) {
    return "PRESENT";
  }
  return "UNKNOWN";
}

function readJsonObject(
  absolutePath: string,
  notesUnknowns: string[],
): Readonly<Record<string, unknown>> | undefined {
  try {
    const rawText = readFileSync(absolutePath, "utf8");
    const parsed: unknown = JSON.parse(rawText);
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      notesUnknowns.push(`UNKNOWN: ${normalizeRepoPath(path.relative(process.cwd(), absolutePath))} is not a JSON object.`);
      return undefined;
    }
    return parsed as Readonly<Record<string, unknown>>;
  } catch {
    notesUnknowns.push(`UNKNOWN: unable to parse ${normalizeRepoPath(path.relative(process.cwd(), absolutePath))}.`);
    return undefined;
  }
}

function listFilesRecursive(absoluteDirectory: string, repoRoot: string): readonly string[] {
  const directoryState = detectPathState(absoluteDirectory, "directory");
  if (directoryState !== "PRESENT") {
    return [];
  }

  const results: string[] = [];
  const walk = (currentDirectory: string): void => {
    const entries: readonly Dirent[] = readdirSync(currentDirectory, { withFileTypes: true }).sort((left, right) =>
      left.name.localeCompare(right.name),
    );
    for (const entry of entries) {
      const absoluteEntryPath = path.join(currentDirectory, entry.name);
      if (entry.isDirectory()) {
        walk(absoluteEntryPath);
        continue;
      }
      if (entry.isFile()) {
        const relativePath = normalizeRepoPath(path.relative(repoRoot, absoluteEntryPath));
        results.push(relativePath);
      }
    }
  };

  walk(absoluteDirectory);
  return sortUnique(results);
}

function parseWorkspacePackages(
  workspaceFilePath: string,
  notesUnknowns: string[],
): readonly string[] {
  try {
    const raw = readFileSync(workspaceFilePath, "utf8");
    const globs: string[] = [];
    for (const line of raw.split(/\r?\n/)) {
      const match = /^\s*-\s*["']?([^"']+)["']?\s*$/.exec(line);
      if (match?.[1] !== undefined) {
        globs.push(match[1].trim());
      }
    }
    return sortUnique(globs.filter((value) => value.length > 0));
  } catch {
    notesUnknowns.push("UNKNOWN: unable to parse pnpm-workspace.yaml package globs.");
    return [];
  }
}

function sortedScripts(
  packageJson: Readonly<Record<string, unknown>> | undefined,
  notesUnknowns: string[],
): Readonly<Record<string, string>> {
  if (packageJson === undefined) {
    notesUnknowns.push("UNKNOWN: root package.json was not available; root_scripts may be incomplete.");
    return {};
  }

  const scriptsUnknown = packageJson["scripts"];
  if (scriptsUnknown === undefined) {
    return {};
  }
  if (typeof scriptsUnknown !== "object" || scriptsUnknown === null || Array.isArray(scriptsUnknown)) {
    notesUnknowns.push("UNKNOWN: package.json scripts field is not a JSON object.");
    return {};
  }

  const scriptsObject = scriptsUnknown as Readonly<Record<string, unknown>>;
  const sorted: Record<string, string> = {};
  const scriptNames = Object.keys(scriptsObject).sort((left, right) => left.localeCompare(right));
  for (const scriptName of scriptNames) {
    const rawValue = scriptsObject[scriptName];
    if (typeof rawValue !== "string") {
      notesUnknowns.push(`UNKNOWN: script ${scriptName} has non-string value.`);
      continue;
    }
    sorted[scriptName] = rawValue;
  }
  return sorted;
}

function findScriptCommands(
  rootScripts: Readonly<Record<string, string>>,
  matcher: (scriptName: string, scriptCommand: string) => boolean,
): readonly string[] {
  const rows: string[] = [];
  const sortedScriptNames = Object.keys(rootScripts).sort((left, right) => left.localeCompare(right));
  for (const scriptName of sortedScriptNames) {
    const scriptCommand = rootScripts[scriptName];
    if (scriptCommand === undefined) {
      continue;
    }
    if (matcher(scriptName, scriptCommand)) {
      rows.push(`${scriptName}=${scriptCommand}`);
    }
  }
  return sortUnique(rows);
}

function extractScriptReferences(commands: readonly string[]): readonly string[] {
  const references: string[] = [];
  const pattern = /([A-Za-z0-9_./-]+\.(?:json|mjs|cjs|js|ts|py|ps1)\b)/g;
  for (const command of commands) {
    const matches = command.match(pattern) ?? [];
    for (const match of matches) {
      references.push(normalizeRepoPath(match));
    }
  }
  return sortUnique(references);
}

function buildFactoryModules(repoRoot: string): Readonly<Record<FactoryModuleName, ModuleEntry>> {
  const result: Record<FactoryModuleName, ModuleEntry> = {
    A_core: { state: "MISSING", files: [] },
    B_tooling: { state: "MISSING", files: [] },
    C_features: { state: "MISSING", files: [] },
    D_validation: { state: "MISSING", files: [] },
    Z_aggregator: { state: "MISSING", files: [] },
  };

  for (const moduleName of EXPECTED_FACTORY_MODULES) {
    const moduleAbsolutePath = path.join(repoRoot, "factory", moduleName);
    const state = detectPathState(moduleAbsolutePath, "directory");
    const files = state === "PRESENT" ? listFilesRecursive(moduleAbsolutePath, repoRoot) : [];
    result[moduleName] = {
      state,
      files,
    };
  }

  return result;
}

function buildFileGroup(
  absoluteDirectory: string,
  repoRoot: string,
  directFileExtensionFilter: string | undefined = undefined,
): FileGroup {
  const state = detectPathState(absoluteDirectory, "directory");
  if (state !== "PRESENT") {
    return {
      state,
      files: [],
    };
  }

  const entries = readdirSync(absoluteDirectory, { withFileTypes: true }).sort((left, right) =>
    left.name.localeCompare(right.name),
  );
  const files: string[] = [];
  for (const entry of entries) {
    if (!entry.isFile()) {
      continue;
    }
    if (directFileExtensionFilter !== undefined && !entry.name.endsWith(directFileExtensionFilter)) {
      continue;
    }
    const absoluteEntryPath = path.join(absoluteDirectory, entry.name);
    files.push(normalizeRepoPath(path.relative(repoRoot, absoluteEntryPath)));
  }
  return {
    state,
    files: sortUnique(files),
  };
}

function canonicalize(value: JsonValue): JsonValue {
  if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((entry) => canonicalize(entry));
  }

  const sortedKeys = Object.keys(value).sort((left, right) => left.localeCompare(right));
  const output: Record<string, JsonValue> = {};
  for (const key of sortedKeys) {
    const child = value[key];
    if (child === undefined) {
      continue;
    }
    output[key] = canonicalize(child);
  }
  return output;
}

function stableStringify(value: JsonValue): string {
  return JSON.stringify(canonicalize(value), null, 2) + "\n";
}

function buildSnapshot(repoRoot: string): SnapshotMini {
  const notesUnknowns: string[] = [];
  const packageJsonPath = path.join(repoRoot, "package.json");
  const workspaceFilePath = path.join(repoRoot, WORKSPACE_FILE_RELATIVE_PATH);

  const packageJsonState = detectPathState(packageJsonPath, "file");
  const packageJson = packageJsonState === "PRESENT" ? readJsonObject(packageJsonPath, notesUnknowns) : undefined;
  if (packageJsonState !== "PRESENT") {
    notesUnknowns.push("UNKNOWN: root package.json is missing or invalid type.");
  }

  let packageManager = "UNKNOWN";
  if (packageJson !== undefined) {
    const packageManagerRaw = packageJson["packageManager"];
    if (typeof packageManagerRaw === "string" && packageManagerRaw.trim().length > 0) {
      packageManager = packageManagerRaw;
    } else {
      notesUnknowns.push("UNKNOWN: package.json packageManager was missing.");
    }
  }

  const workspaceFileState = detectPathState(workspaceFilePath, "file");
  const workspacePackages =
    workspaceFileState === "PRESENT" ? parseWorkspacePackages(workspaceFilePath, notesUnknowns) : [];
  if (workspaceFileState === "MISSING") {
    notesUnknowns.push("UNKNOWN: pnpm-workspace.yaml missing; workspace_packages unavailable.");
  }

  const rootScripts = sortedScripts(packageJson, notesUnknowns);
  const smokeCommands = findScriptCommands(rootScripts, (scriptName, scriptCommand) => {
    return scriptName.includes("smoke") || scriptCommand.includes("smoke");
  });
  const healthCommands = findScriptCommands(rootScripts, (scriptName, scriptCommand) => {
    return scriptName.includes("health") || scriptCommand.includes("health");
  });

  const smokeTestsPath = path.join(repoRoot, "tests", "smoke");
  const testsSmokeState = detectPathState(smokeTestsPath, "directory");
  const testsSmokeFiles = testsSmokeState === "PRESENT" ? listFilesRecursive(smokeTestsPath, repoRoot) : [];

  const runFactorySmokePath = path.join(repoRoot, "scripts", "run_factory_smoke.ps1");
  const runFactorySmokeState = detectPathState(runFactorySmokePath, "file");

  const healthScriptRefs = extractScriptReferences(healthCommands);
  const healthChecksState: ComponentState = healthCommands.length > 0 ? "PRESENT" : "MISSING";

  const snapshot: SnapshotMini = {
    schema_version: "1.0.0",
    workspace_manager: {
      package_manager: packageManager,
      workspace_file: WORKSPACE_FILE_RELATIVE_PATH,
      workspace_file_state: workspaceFileState,
      workspace_packages: workspacePackages,
    },
    root_scripts: rootScripts,
    factory_modules: buildFactoryModules(repoRoot),
    factory_contracts: buildFileGroup(path.join(repoRoot, "factory", "contracts"), repoRoot, ".ts"),
    factory_configs: buildFileGroup(path.join(repoRoot, "configs", "factory"), repoRoot, ".json"),
    smoke: {
      tests_smoke_state: testsSmokeState,
      tests_smoke_files: testsSmokeFiles,
      run_factory_smoke_ps1_state: runFactorySmokeState,
      smoke_commands: smokeCommands,
    },
    health_checks: {
      state: healthChecksState,
      commands: healthCommands,
      script_refs: healthScriptRefs,
    },
    notes_unknowns: sortUnique(notesUnknowns),
  };

  return snapshot;
}

function writeSnapshot(repoRoot: string, snapshot: SnapshotMini): void {
  const outputPath = path.join(repoRoot, SNAPSHOT_RELATIVE_PATH);
  mkdirSync(path.dirname(outputPath), { recursive: true });
  const text = stableStringify(snapshot as unknown as JsonValue);
  writeFileSync(outputPath, text, { encoding: "utf8" });
}

function run(): number {
  const repoRoot = process.cwd();
  const snapshot = buildSnapshot(repoRoot);
  writeSnapshot(repoRoot, snapshot);

  const outputPath = normalizeRepoPath(path.join(repoRoot, SNAPSHOT_RELATIVE_PATH));
  process.stdout.write(`Wrote ${outputPath}\n`);
  return 0;
}

try {
  process.exit(run());
} catch (error: unknown) {
  const message = error instanceof Error ? error.message : "Unknown error";
  process.stderr.write(`snapshot:hos failed: ${message}\n`);
  process.exit(1);
}
