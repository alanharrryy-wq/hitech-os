import { validateDataShape } from "./schema/registry.js";
import type {
  DataProvider,
  DataSetId,
  DataShapeId,
  DataSpine,
  ProviderId,
  Query,
  QueryPrimitive,
  Result
} from "./types.js";

export const DATA_SPINE_DEFAULT_CACHE_TTL_MS = 30_000;

export interface CreateSpineOptions {
  readonly defaultProviderId?: ProviderId;
  readonly cacheTtlMs?: number;
  readonly providers?: readonly DataProvider[];
  readonly now?: () => number;
}

interface CacheEntry {
  value?: Result<unknown> | undefined;
  expiresAt: number;
  inFlight?: Promise<Result<unknown>> | undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function stableSerialize(input: unknown): string {
  if (input === null) {
    return "null";
  }

  if (typeof input === "string") {
    return JSON.stringify(input);
  }

  if (typeof input === "number" || typeof input === "boolean") {
    return String(input);
  }

  if (Array.isArray(input)) {
    return `[${input.map((entry) => stableSerialize(entry)).join(",")}]`;
  }

  if (isRecord(input)) {
    const keys = Object.keys(input).sort((left, right) => left.localeCompare(right));
    const pairs = keys
      .map((key) => {
        const value = input[key];
        if (value === undefined) {
          return undefined;
        }
        return `${JSON.stringify(key)}:${stableSerialize(value)}`;
      })
      .filter((value): value is string => value !== undefined);

    return `{${pairs.join(",")}}`;
  }

  return JSON.stringify(String(input));
}

function normalizeQueryForKey(
  input: Query & { providerId?: ProviderId | undefined }
): Record<string, unknown> {
  const { signal, ...rest } = input;
  void signal;
  return rest;
}

export function createStableQueryKey(
  input: Query & { providerId?: ProviderId | undefined }
): string {
  const providerId = input.providerId ?? "<unresolved-provider>";
  const normalized = normalizeQueryForKey({ ...input, providerId });
  return stableSerialize(normalized);
}

function toMetadata(input: unknown): Readonly<Record<string, QueryPrimitive>> {
  if (!isRecord(input)) {
    return {};
  }

  const output: Record<string, QueryPrimitive> = {};

  for (const [key, value] of Object.entries(input)) {
    if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      output[key] = value;
    }
  }

  return output;
}

export function createSpine(options: CreateSpineOptions = {}): DataSpine {
  const providers = new Map<ProviderId, DataProvider>();
  const cache = new Map<string, CacheEntry>();
  const defaultCacheTtlMs = options.cacheTtlMs ?? DATA_SPINE_DEFAULT_CACHE_TTL_MS;
  const now = options.now ?? (() => Date.now());

  for (const provider of options.providers ?? []) {
    providers.set(provider.id, provider);
  }

  function registerProvider(provider: DataProvider): void {
    providers.set(provider.id, provider);
  }

  function unregisterProvider(providerId: ProviderId): void {
    providers.delete(providerId);
  }

  function hasProvider(providerId: ProviderId): boolean {
    return providers.has(providerId);
  }

  async function query<TData = unknown>(input: Query): Promise<Result<TData>> {
    const providerId = input.providerId ?? options.defaultProviderId;

    if (providerId === undefined) {
      throw new Error("DataSpine query requires providerId or a default provider.");
    }

    const provider = providers.get(providerId);

    if (provider === undefined) {
      throw new Error(`Provider '${providerId}' is not registered in this DataSpine.`);
    }

    const stableQueryKey = createStableQueryKey({ ...input, providerId });
    const timestamp = now();
    const cached = cache.get(stableQueryKey);

    if (!input.forceRefresh && cached?.value !== undefined && cached.expiresAt > timestamp) {
      return cached.value as Result<TData>;
    }

    if (!input.forceRefresh && cached?.inFlight !== undefined) {
      return (await cached.inFlight) as Result<TData>;
    }

    const inFlight = (async () => {
      const response = await provider.query(
        { ...input, providerId },
        {
          providerId,
          stableQueryKey,
          now
        }
      );

      const dataShapeId = (response.dataShapeId ?? input.dataShapeId) as DataShapeId | undefined;
      if (dataShapeId === undefined || String(dataShapeId).trim().length === 0) {
        throw new Error(`Query '${stableQueryKey}' is missing dataShapeId.`);
      }

      const validated = validateDataShape<TData>(dataShapeId, response.data);
      const cacheTtlMs =
        input.cacheTtlMs ?? response.cacheTtlMs ?? defaultCacheTtlMs;

      const result: Result<TData> = {
        providerId,
        datasetId: (response.datasetId ?? input.datasetId) as DataSetId | undefined,
        dataShapeId,
        data: validated,
        stableQueryKey,
        receivedAt: new Date(timestamp).toISOString(),
        cacheTtlMs,
        determinism: response.determinism ?? null,
        metadata: toMetadata(response.metadata)
      };

      cache.set(stableQueryKey, {
        value: result,
        expiresAt: now() + cacheTtlMs
      });

      return result as Result<unknown>;
    })();

    cache.set(stableQueryKey, {
      value: cached?.value,
      expiresAt: cached?.expiresAt ?? 0,
      inFlight
    });

    try {
      return (await inFlight) as Result<TData>;
    } catch (error) {
      if (cached !== undefined) {
        cache.set(stableQueryKey, cached);
      } else {
        cache.delete(stableQueryKey);
      }
      throw error;
    }
  }

  return {
    registerProvider,
    unregisterProvider,
    hasProvider,
    query
  };
}


