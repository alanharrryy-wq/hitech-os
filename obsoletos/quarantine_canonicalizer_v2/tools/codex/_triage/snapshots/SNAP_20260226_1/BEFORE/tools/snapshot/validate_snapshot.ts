import { readFileSync } from "node:fs";
import * as path from "node:path";
import { ErrorObject } from "ajv";
import Ajv2020 from "ajv/dist/2020";

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | readonly JsonValue[] | { readonly [key: string]: JsonValue };

interface SnapshotLike {
  readonly workspace_manager?: {
    readonly workspace_packages?: readonly string[];
  };
  readonly root_scripts?: Readonly<Record<string, string>>;
  readonly factory_modules?: Readonly<Record<string, { readonly files?: readonly string[] }>>;
  readonly factory_contracts?: {
    readonly files?: readonly string[];
  };
  readonly factory_configs?: {
    readonly files?: readonly string[];
  };
  readonly smoke?: {
    readonly tests_smoke_files?: readonly string[];
    readonly smoke_commands?: readonly string[];
  };
  readonly health_checks?: {
    readonly commands?: readonly string[];
    readonly script_refs?: readonly string[];
  };
  readonly notes_unknowns?: readonly string[];
}

const SCHEMA_RELATIVE_PATH = "docs/snapshots/HITECH_OS__SNAPSHOT_MINI.schema.json";
const SNAPSHOT_RELATIVE_PATH = "docs/snapshots/HITECH_OS__SNAPSHOT_MINI.json";
const MODULES: readonly string[] = [
  "A_core",
  "B_tooling",
  "C_features",
  "D_validation",
  "Z_aggregator",
];

function normalizeRepoPath(value: string): string {
  return value.replace(/\\/g, "/");
}

function toJsonValue(value: unknown): JsonValue {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((entry) => toJsonValue(entry));
  }
  if (typeof value === "object") {
    const objectValue = value as Readonly<Record<string, unknown>>;
    const output: Record<string, JsonValue> = {};
    for (const key of Object.keys(objectValue).sort((left, right) => left.localeCompare(right))) {
      const child = objectValue[key];
      if (child === undefined) {
        continue;
      }
      output[key] = toJsonValue(child);
    }
    return output;
  }
  return String(value);
}

function stableStringify(value: unknown): string {
  return JSON.stringify(toJsonValue(value));
}

function readJson(absolutePath: string, label: string): unknown {
  try {
    return JSON.parse(readFileSync(absolutePath, "utf8")) as unknown;
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Unknown parse error";
    throw new Error(`${label} parse failed: ${message}`);
  }
}

function isSorted(values: readonly string[]): boolean {
  for (let index = 0; index < values.length - 1; index += 1) {
    const current = values[index];
    const next = values[index + 1];
    if (current === undefined || next === undefined) {
      return false;
    }
    if (current.localeCompare(next) > 0) {
      return false;
    }
  }
  return true;
}

function checkSortedArray(
  values: readonly string[] | undefined,
  pathLabel: string,
  errors: string[],
): void {
  if (values === undefined) {
    return;
  }
  if (!isSorted(values)) {
    errors.push(`${pathLabel} array must be lexicographically sorted.`);
  }
}

function checkRootScriptsOrder(
  rootScripts: Readonly<Record<string, string>> | undefined,
  errors: string[],
): void {
  if (rootScripts === undefined) {
    return;
  }
  const actualKeys = Object.keys(rootScripts);
  const expectedKeys = [...actualKeys].sort((left, right) => left.localeCompare(right));
  for (let index = 0; index < actualKeys.length; index += 1) {
    const actual = actualKeys[index];
    const expected = expectedKeys[index];
    if (actual !== expected && actual !== undefined && expected !== undefined) {
      errors.push(`root_scripts keys must be sorted: expected ${expected} before ${actual}.`);
      return;
    }
  }
}

function schemaErrorsToMessages(errors: readonly ErrorObject[]): readonly string[] {
  return errors.map((error) => {
    const instancePath = error.instancePath.length === 0 ? "/" : error.instancePath;
    const params = stableStringify(error.params);
    return `${instancePath} ${error.keyword} ${error.message ?? "validation error"} params=${params}`;
  });
}

function deterministicChecks(snapshot: SnapshotLike): readonly string[] {
  const errors: string[] = [];
  checkRootScriptsOrder(snapshot.root_scripts, errors);
  checkSortedArray(snapshot.workspace_manager?.workspace_packages, "/workspace_manager/workspace_packages", errors);

  for (const moduleName of MODULES) {
    checkSortedArray(
      snapshot.factory_modules?.[moduleName]?.files,
      `/factory_modules/${moduleName}/files`,
      errors,
    );
  }

  checkSortedArray(snapshot.factory_contracts?.files, "/factory_contracts/files", errors);
  checkSortedArray(snapshot.factory_configs?.files, "/factory_configs/files", errors);
  checkSortedArray(snapshot.smoke?.tests_smoke_files, "/smoke/tests_smoke_files", errors);
  checkSortedArray(snapshot.smoke?.smoke_commands, "/smoke/smoke_commands", errors);
  checkSortedArray(snapshot.health_checks?.commands, "/health_checks/commands", errors);
  checkSortedArray(snapshot.health_checks?.script_refs, "/health_checks/script_refs", errors);
  checkSortedArray(snapshot.notes_unknowns, "/notes_unknowns", errors);
  return errors;
}

function run(): number {
  const repoRoot = process.cwd();
  const schemaPath = path.join(repoRoot, SCHEMA_RELATIVE_PATH);
  const snapshotPath = path.join(repoRoot, SNAPSHOT_RELATIVE_PATH);

  const schema = readJson(schemaPath, SCHEMA_RELATIVE_PATH);
  const snapshot = readJson(snapshotPath, SNAPSHOT_RELATIVE_PATH);

  const ajv = new Ajv2020({
    allErrors: true,
    strict: false,
  });
  const validate = ajv.compile(schema);

  const validationPassed = validate(snapshot);
  const schemaMessages = validationPassed
    ? []
    : schemaErrorsToMessages((validate.errors ?? []) as readonly ErrorObject[]);
  const deterministicMessages = deterministicChecks(snapshot as SnapshotLike);

  const allMessages = Array.from(new Set([...schemaMessages, ...deterministicMessages])).sort((left, right) =>
    left.localeCompare(right),
  );

  if (allMessages.length > 0) {
    process.stderr.write("Snapshot validation FAILED\n");
    for (const message of allMessages) {
      process.stderr.write(`${message}\n`);
    }
    return 1;
  }

  process.stdout.write(
    `Snapshot validation PASS (${normalizeRepoPath(path.relative(repoRoot, snapshotPath))})\n`,
  );
  return 0;
}

try {
  process.exit(run());
} catch (error: unknown) {
  const message = error instanceof Error ? error.message : "Unknown validation error";
  process.stderr.write(`snapshot:hos:validate failed: ${message}\n`);
  process.exit(1);
}
