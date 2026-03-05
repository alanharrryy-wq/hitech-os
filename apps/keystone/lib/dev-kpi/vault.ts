import fs from "node:fs/promises";
import path from "node:path";
import {
  type DevSeedOptions,
  validateDatasetResponse,
  validatePresetJSON,
  type DevDatasetRegistry,
  type DevDatasetRegistryEntry,
  type DevDatasetResponse
} from "./validation";

interface ResolvedVault {
  readonly rootDir: string;
  readonly indexPath: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asNonEmptyString(value: unknown): string | undefined {
  if (typeof value !== "string") {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((entry) => asNonEmptyString(entry))
    .filter((entry): entry is string => entry !== undefined);
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function resolveVault(): Promise<ResolvedVault> {
  const candidates = [
    path.resolve(process.cwd(), "apps", "keystone", "dev-datasets"),
    path.resolve(process.cwd(), "dev-datasets")
  ];

  for (const candidate of candidates) {
    const indexPath = path.join(candidate, "index.json");
    if (await fileExists(indexPath)) {
      return {
        rootDir: candidate,
        indexPath
      };
    }
  }

  throw new Error(`Unable to locate dev dataset vault. Checked: ${candidates.join(", ")}`);
}

async function readJson(filePath: string): Promise<unknown> {
  const raw = await fs.readFile(filePath, "utf8");
  return JSON.parse(raw) as unknown;
}

function toRegistry(input: unknown): DevDatasetRegistry {
  const parsed = validatePresetJSON(input);
  if (!parsed.ok) {
    throw new Error(`Dataset index validation failed: ${parsed.errors.join(" | ")}`);
  }

  const node = input as {
    version?: unknown;
    datasets: readonly Record<string, unknown>[];
  };

  const datasets: DevDatasetRegistryEntry[] = node.datasets.map((entry) => {
    const datasetId = asNonEmptyString(entry["datasetId"]);
    const dataShapeId = asNonEmptyString(entry["dataShapeId"]);
    const semanticIntent = asNonEmptyString(entry["semanticIntent"]);
    const file = asNonEmptyString(entry["file"]);

    if (!datasetId || !dataShapeId || !semanticIntent || !file) {
      throw new Error("Dataset index contains malformed entry after validation pass.");
    }

    const recommendedWidgets = asStringArray(entry["recommendedWidgets"]);
    const tags = asStringArray(entry["tags"]);

    let seedOptions: DevSeedOptions | undefined;
    if (isRecord(entry["seedOptions"])) {
      const defaultSeed = asNonEmptyString(entry["seedOptions"]["defaultSeed"]);
      const supportedSeeds = Array.isArray(entry["seedOptions"]["supportedSeeds"])
        ? asStringArray(entry["seedOptions"]["supportedSeeds"])
        : undefined;

      seedOptions = {
        ...(defaultSeed !== undefined ? { defaultSeed } : {}),
        ...(supportedSeeds !== undefined ? { supportedSeeds } : {})
      };
    }

    return {
      datasetId,
      dataShapeId,
      semanticIntent,
      file,
      recommendedWidgets,
      tags,
      ...(seedOptions !== undefined ? { seedOptions } : {})
    };
  });

  const version = typeof node.version === "number" && Number.isFinite(node.version) ? node.version : 1;

  return {
    version,
    datasets: [...datasets].sort((left, right) => left.datasetId.localeCompare(right.datasetId))
  };
}

function resolveDatasetFile(rootDir: string, fileRelative: string): string {
  const resolved = path.resolve(rootDir, fileRelative);
  const normalizedRoot = path.resolve(rootDir);

  if (!resolved.startsWith(normalizedRoot)) {
    throw new Error(`Dataset file '${fileRelative}' escapes vault root.`);
  }

  return resolved;
}

export async function loadDatasetRegistry(): Promise<DevDatasetRegistry> {
  const vault = await resolveVault();
  const parsed = await readJson(vault.indexPath);
  return toRegistry(parsed);
}

export async function listDatasets(): Promise<readonly DevDatasetRegistryEntry[]> {
  const registry = await loadDatasetRegistry();
  return registry.datasets;
}

export async function loadDatasetById(datasetId: string): Promise<DevDatasetResponse> {
  const vault = await resolveVault();
  const registry = await loadDatasetRegistry();
  const entry = registry.datasets.find((item) => item.datasetId === datasetId);

  if (entry === undefined) {
    throw new Error(`Dataset '${datasetId}' is not registered in index.json.`);
  }

  const datasetPath = resolveDatasetFile(vault.rootDir, entry.file);
  const raw = await readJson(datasetPath);

  if (!isRecord(raw)) {
    throw new Error(`Dataset file '${entry.file}' must contain an object.`);
  }

  const responseCandidate = {
    datasetId: asNonEmptyString(raw["datasetId"]) ?? entry.datasetId,
    dataShapeId: asNonEmptyString(raw["dataShapeId"]) ?? entry.dataShapeId,
    payload: raw["payload"],
    semanticIntent: asNonEmptyString(raw["semanticIntent"]) ?? entry.semanticIntent,
    recommendedWidgets:
      asStringArray(raw["recommendedWidgets"]).length > 0
        ? asStringArray(raw["recommendedWidgets"])
        : entry.recommendedWidgets,
    tags: asStringArray(raw["tags"]).length > 0 ? asStringArray(raw["tags"]) : entry.tags
  };

  return validateDatasetResponse(responseCandidate);
}

