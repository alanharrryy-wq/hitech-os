import type {
  DataProvider,
  DataSetId,
  ProviderId,
  ProviderResponse,
  Query
} from "../types.js";

const JSON_VAULT_PROVIDER_ID: ProviderId = "jsonVault";

interface JsonVaultRegistryEntry {
  readonly datasetId: string;
  readonly dataShapeId?: string;
}

interface JsonVaultRegistryResponse {
  readonly datasets: readonly JsonVaultRegistryEntry[];
}

export interface JsonVaultProviderOptions {
  readonly id?: ProviderId;
  readonly basePath?: string;
  readonly listPath?: string;
  readonly datasetPath?: (datasetId: DataSetId) => string;
  readonly fetchImpl?: typeof fetch;
  readonly cacheTtlMs?: number;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function normalizePath(basePath: string, path: string): string {
  const normalizedBase = basePath.endsWith("/") ? basePath.slice(0, -1) : basePath;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function parseRegistry(input: unknown): JsonVaultRegistryResponse {
  if (!isRecord(input) || !Array.isArray(input["datasets"])) {
    return { datasets: [] };
  }

  const datasets = input["datasets"]
    .filter((item): item is Record<string, unknown> => isRecord(item))
    .map((item) => ({
      datasetId: typeof item["datasetId"] === "string" ? item["datasetId"] : "",
      ...(typeof item["dataShapeId"] === "string" ? { dataShapeId: item["dataShapeId"] } : {})
    }))
    .filter((item) => item.datasetId.length > 0);

  return { datasets };
}

export function createJsonVaultProvider(options: JsonVaultProviderOptions = {}): DataProvider {
  const providerId = options.id ?? JSON_VAULT_PROVIDER_ID;
  const basePath = options.basePath ?? "";
  const listPath = options.listPath ?? "/api/dev/kpi/datasets";
  const datasetPath = options.datasetPath ?? ((datasetId: DataSetId) => `/api/dev/kpi/datasets/${datasetId}`);
  const fetchImpl = options.fetchImpl ?? fetch;
  const cacheTtlMs = options.cacheTtlMs ?? 20_000;

  let registryMap = new Map<string, JsonVaultRegistryEntry>();
  let registryPromise: Promise<void> | undefined;

  async function loadRegistry(signal?: AbortSignal): Promise<void> {
    if (registryPromise !== undefined) {
      await registryPromise;
      return;
    }

    registryPromise = (async () => {
      const listRequest: RequestInit = {
        method: "GET",
        cache: "no-store"
      };
      if (signal !== undefined) {
        listRequest.signal = signal;
      }

      const response = await fetchImpl(normalizePath(basePath, listPath), listRequest);

      if (!response.ok) {
        throw new Error(`jsonVault list request failed with status ${response.status}.`);
      }

      const parsed = parseRegistry((await response.json()) as unknown);
      registryMap = new Map(parsed.datasets.map((entry) => [entry.datasetId, entry]));
    })();

    await registryPromise;
  }

  return {
    id: providerId,
    async query(input: Query): Promise<ProviderResponse> {
      const datasetId = input.datasetId;
      if (datasetId === undefined || datasetId.trim().length === 0) {
        throw new Error("jsonVault provider requires query.datasetId.");
      }

      await loadRegistry(input.signal);

      const datasetRequest: RequestInit = {
        method: "GET",
        cache: "no-store"
      };
      if (input.signal !== undefined) {
        datasetRequest.signal = input.signal;
      }

      const response = await fetchImpl(normalizePath(basePath, datasetPath(datasetId)), datasetRequest);

      if (!response.ok) {
        throw new Error(`jsonVault dataset request failed for '${datasetId}' with status ${response.status}.`);
      }

      const json = (await response.json()) as unknown;
      if (!isRecord(json)) {
        throw new Error(`jsonVault dataset '${datasetId}' returned a non-object payload.`);
      }

      const inferred = registryMap.get(datasetId);
      const dataShapeId =
        (typeof json["dataShapeId"] === "string" ? json["dataShapeId"] : undefined) ??
        input.dataShapeId ??
        inferred?.dataShapeId;

      if (dataShapeId === undefined) {
        throw new Error(`jsonVault dataset '${datasetId}' does not declare dataShapeId.`);
      }

      const payload = json["payload"] ?? json["data"];
      if (payload === undefined) {
        throw new Error(`jsonVault dataset '${datasetId}' is missing payload/data.`);
      }

      const metadata: Record<string, string | number | boolean | null> = {
        source: "json-vault",
        registryKnown: inferred !== undefined
      };

      return {
        providerId,
        datasetId,
        dataShapeId,
        data: payload,
        cacheTtlMs,
        metadata
      };
    }
  };
}


