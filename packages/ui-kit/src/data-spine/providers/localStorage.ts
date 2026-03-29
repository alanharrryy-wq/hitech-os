import type {
  DataProvider,
  DataSetId,
  DataShapeId,
  ProviderId,
  ProviderResponse,
  Query
} from "../types.js";

const LOCAL_STORAGE_PROVIDER_ID: ProviderId = "localStorage";
const DEFAULT_PREFIX = "hitech:data-spine";

export interface LocalStorageProviderOptions {
  readonly id?: ProviderId;
  readonly keyPrefix?: string;
  readonly cacheTtlMs?: number;
}

export interface WriteLocalStorageDatasetInput {
  readonly datasetId: DataSetId;
  readonly dataShapeId: DataShapeId;
  readonly payload: unknown;
  readonly keyPrefix?: string;
}

interface StoredDatasetRecord {
  readonly datasetId: DataSetId;
  readonly dataShapeId: DataShapeId;
  readonly payload: unknown;
  readonly updatedAt: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function resolveStorage(): Storage {
  if (typeof window === "undefined" || typeof window.localStorage === "undefined") {
    throw new Error("localStorage provider can only run in a browser environment.");
  }

  return window.localStorage;
}

function assertDevelopmentRuntime(): void {
  if (typeof process !== "undefined" && process.env["NODE_ENV"] === "production") {
    throw new Error("localStorage provider is dev-only and is disabled in production.");
  }
}

function getStorageKey(datasetId: DataSetId, keyPrefix: string): string {
  return `${keyPrefix}:${datasetId}`;
}

export function writeLocalStorageDataset(input: WriteLocalStorageDatasetInput): void {
  assertDevelopmentRuntime();

  const storage = resolveStorage();
  const keyPrefix = input.keyPrefix ?? DEFAULT_PREFIX;
  const record: StoredDatasetRecord = {
    datasetId: input.datasetId,
    dataShapeId: input.dataShapeId,
    payload: input.payload,
    updatedAt: new Date().toISOString()
  };

  storage.setItem(getStorageKey(input.datasetId, keyPrefix), JSON.stringify(record));
}

export function createLocalStorageProvider(options: LocalStorageProviderOptions = {}): DataProvider {
  const providerId = options.id ?? LOCAL_STORAGE_PROVIDER_ID;
  const keyPrefix = options.keyPrefix ?? DEFAULT_PREFIX;
  const cacheTtlMs = options.cacheTtlMs ?? 5_000;

  return {
    id: providerId,
    query(input: Query): ProviderResponse {
      assertDevelopmentRuntime();

      const datasetId = input.datasetId;
      if (datasetId === undefined || datasetId.trim().length === 0) {
        throw new Error("localStorage provider requires query.datasetId.");
      }

      const storage = resolveStorage();
      const raw = storage.getItem(getStorageKey(datasetId, keyPrefix));

      if (raw === null) {
        throw new Error(`localStorage dataset '${datasetId}' was not found under prefix '${keyPrefix}'.`);
      }

      let parsed: unknown;
      try {
        parsed = JSON.parse(raw) as unknown;
      } catch (error) {
        throw new Error(
          `localStorage dataset '${datasetId}' contains invalid JSON: ${
            error instanceof Error ? error.message : String(error)
          }`
        );
      }

      if (!isRecord(parsed)) {
        throw new Error(`localStorage dataset '${datasetId}' must deserialize to an object.`);
      }

      const parsedShape = parsed["dataShapeId"];
      const dataShapeId =
        typeof parsedShape === "string"
          ? (parsedShape as DataShapeId)
          : input.dataShapeId;

      if (dataShapeId === undefined) {
        throw new Error(`localStorage dataset '${datasetId}' is missing dataShapeId.`);
      }

      if (!("payload" in parsed)) {
        throw new Error(`localStorage dataset '${datasetId}' is missing payload.`);
      }

      return {
        providerId,
        datasetId,
        dataShapeId,
        data: parsed["payload"],
        cacheTtlMs,
        metadata: {
          source: "local-storage"
        }
      };
    }
  };
}


