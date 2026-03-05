import { validateDataShape } from "@hitech/ui-kit";

export interface DevSeedOptions {
  readonly defaultSeed?: string;
  readonly supportedSeeds?: readonly string[];
}

export interface DevDatasetRegistryEntry {
  readonly datasetId: string;
  readonly dataShapeId: string;
  readonly semanticIntent: string;
  readonly recommendedWidgets: readonly string[];
  readonly tags: readonly string[];
  readonly file: string;
  readonly seedOptions?: DevSeedOptions;
}

export interface DevDatasetRegistry {
  readonly version: number;
  readonly datasets: readonly DevDatasetRegistryEntry[];
}

export interface DevDatasetResponse {
  readonly datasetId: string;
  readonly dataShapeId: string;
  readonly payload: unknown;
  readonly semanticIntent: string;
  readonly recommendedWidgets: readonly string[];
  readonly tags: readonly string[];
}

export interface PresetValidationResult {
  readonly ok: boolean;
  readonly errors: readonly string[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function parseStringArray(value: unknown, path: string, errors: string[]): string[] {
  if (!Array.isArray(value)) {
    errors.push(`${path} must be an array of strings.`);
    return [];
  }

  const output: string[] = [];

  for (let index = 0; index < value.length; index += 1) {
    const entry = value[index];
    if (typeof entry !== "string" || entry.trim().length === 0) {
      errors.push(`${path}[${index}] must be a non-empty string.`);
      continue;
    }
    output.push(entry.trim());
  }

  return output;
}

function parseSeedOptions(value: unknown, path: string, errors: string[]): DevSeedOptions | undefined {
  if (value === undefined) {
    return undefined;
  }

  if (!isRecord(value)) {
    errors.push(`${path} must be an object.`);
    return undefined;
  }

  const defaultSeed =
    typeof value["defaultSeed"] === "string" && value["defaultSeed"].trim().length > 0
      ? value["defaultSeed"].trim()
      : undefined;

  const supportedSeeds = value["supportedSeeds"] === undefined
    ? undefined
    : parseStringArray(value["supportedSeeds"], `${path}.supportedSeeds`, errors);

  return {
    ...(defaultSeed !== undefined ? { defaultSeed } : {}),
    ...(supportedSeeds !== undefined ? { supportedSeeds } : {})
  };
}

function parseRegistryEntry(
  value: unknown,
  path: string,
  errors: string[]
): DevDatasetRegistryEntry | undefined {
  if (!isRecord(value)) {
    errors.push(`${path} must be an object.`);
    return undefined;
  }

  const datasetId = typeof value["datasetId"] === "string" ? value["datasetId"].trim() : "";
  const dataShapeId = typeof value["dataShapeId"] === "string" ? value["dataShapeId"].trim() : "";
  const semanticIntent =
    typeof value["semanticIntent"] === "string" ? value["semanticIntent"].trim() : "";
  const file = typeof value["file"] === "string" ? value["file"].trim() : "";

  if (datasetId.length === 0) {
    errors.push(`${path}.datasetId must be a non-empty string.`);
  }

  if (dataShapeId.length === 0) {
    errors.push(`${path}.dataShapeId must be a non-empty string.`);
  }

  if (semanticIntent.length === 0) {
    errors.push(`${path}.semanticIntent must be a non-empty string.`);
  }

  if (file.length === 0) {
    errors.push(`${path}.file must be a non-empty string.`);
  }

  const recommendedWidgets = parseStringArray(value["recommendedWidgets"], `${path}.recommendedWidgets`, errors);
  const tags = parseStringArray(value["tags"], `${path}.tags`, errors);
  const seedOptions = parseSeedOptions(value["seedOptions"], `${path}.seedOptions`, errors);

  if (errors.length > 0) {
    return undefined;
  }

  return {
    datasetId,
    dataShapeId,
    semanticIntent,
    recommendedWidgets,
    tags,
    file,
    ...(seedOptions !== undefined ? { seedOptions } : {})
  };
}

export function validatePresetJSON(input: unknown): PresetValidationResult {
  const errors: string[] = [];

  if (!isRecord(input)) {
    return {
      ok: false,
      errors: ["Preset JSON must be an object."]
    };
  }

  if (!Array.isArray(input["datasets"])) {
    return {
      ok: false,
      errors: ["Preset JSON must include datasets[] registry."]
    };
  }

  const datasets = input["datasets"];

  for (let index = 0; index < datasets.length; index += 1) {
    parseRegistryEntry(datasets[index], `datasets[${index}]`, errors);
  }

  return {
    ok: errors.length === 0,
    errors
  };
}

/**
 * Anti-flicker guidance:
 * - Do not rewrite URL params during mount.
 * - Perform only idempotent normalization.
 * - Apply normalization only on explicit user action (e.g. Apply button).
 */
export function validateDatasetResponse(input: unknown): DevDatasetResponse {
  if (!isRecord(input)) {
    throw new Error("Dataset response must be an object.");
  }

  const datasetId = typeof input["datasetId"] === "string" ? input["datasetId"].trim() : "";
  const dataShapeId = typeof input["dataShapeId"] === "string" ? input["dataShapeId"].trim() : "";
  const semanticIntent =
    typeof input["semanticIntent"] === "string" ? input["semanticIntent"].trim() : "";

  if (datasetId.length === 0) {
    throw new Error("datasetId must be a non-empty string.");
  }

  if (dataShapeId.length === 0) {
    throw new Error("dataShapeId must be a non-empty string.");
  }

  if (!("payload" in input)) {
    throw new Error(`Dataset '${datasetId}' is missing payload.`);
  }

  if (semanticIntent.length === 0) {
    throw new Error(`Dataset '${datasetId}' requires semanticIntent.`);
  }

  const recommendedWidgets = parseStringArray(
    input["recommendedWidgets"],
    "recommendedWidgets",
    []
  );
  const tags = parseStringArray(input["tags"], "tags", []);

  if (recommendedWidgets.length === 0) {
    throw new Error(`Dataset '${datasetId}' requires recommendedWidgets[].`);
  }

  validateDataShape(dataShapeId as never, input["payload"]);

  return {
    datasetId,
    dataShapeId,
    payload: input["payload"],
    semanticIntent,
    recommendedWidgets,
    tags
  };
}

