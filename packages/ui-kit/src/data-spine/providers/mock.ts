import type {
  DataProvider,
  DataShapeId,
  DeterminismContract,
  ProviderId,
  ProviderResponse,
  Query,
  QueryParams
} from "../types.js";
import type {
  BreakdownData,
  GaugeData,
  MatrixData,
  TableMiniData,
  TimeSeriesData
} from "../schema/shapes.js";

const MOCK_PROVIDER_ID: ProviderId = "mock";

export interface MockProviderOptions {
  readonly id?: ProviderId;
  readonly defaultSeed?: string;
  readonly defaultShapeId?: DataShapeId;
  readonly cacheTtlMs?: number;
}

type RandomSource = () => number;

function hashString(input: string): number {
  let hash = 0;
  for (let index = 0; index < input.length; index += 1) {
    hash = Math.imul(hash ^ input.charCodeAt(index), 0x45d9f3b);
  }
  return hash >>> 0;
}

function createMulberry32(seed: number): RandomSource {
  let state = seed >>> 0;
  return () => {
    state += 0x6d2b79f5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function readStringParam(params: QueryParams | undefined, key: string): string | undefined {
  if (params === undefined) {
    return undefined;
  }

  const value = params[key];

  if (typeof value === "string") {
    return value;
  }

  if (Array.isArray(value) && typeof value[0] === "string") {
    return value[0];
  }

  return undefined;
}

function readNumberParam(params: QueryParams | undefined, key: string): number | undefined {
  if (params === undefined) {
    return undefined;
  }

  const value = params[key];
  const candidate = Array.isArray(value) ? value[0] : value;

  if (typeof candidate === "number" && Number.isFinite(candidate)) {
    return candidate;
  }

  if (typeof candidate === "string") {
    const parsed = Number(candidate);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return undefined;
}

function clampInteger(input: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, Math.floor(input)));
}

function inferShapeId(datasetId: string | undefined, fallback: DataShapeId): DataShapeId {
  if (!datasetId) {
    return fallback;
  }

  const normalized = datasetId.toLowerCase();
  if (normalized.includes("breakdown") || normalized.includes("share")) {
    return "breakdown";
  }
  if (normalized.includes("matrix")) {
    return "matrix";
  }
  if (normalized.includes("gauge")) {
    return "gauge";
  }
  if (normalized.includes("table")) {
    return "tableMini";
  }
  if (normalized.includes("series") || normalized.includes("trend") || normalized.includes("time")) {
    return "timeSeries";
  }
  return fallback;
}

function buildDeterminism(seed: string): DeterminismContract {
  return {
    deterministic: true,
    seed,
    algorithm: "mulberry32",
    version: 1
  };
}

function generateTimeSeries(rng: RandomSource, input: Query): TimeSeriesData {
  const requested = readNumberParam(input.params, "points") ?? 12;
  const count = input.perfProfile === "perf" ? clampInteger(requested, 4, 8) : clampInteger(requested, 6, 36);
  const base = readNumberParam(input.params, "base") ?? 120;

  const points = Array.from({ length: count }, (_, index) => {
    const drift = index * (2.4 + rng() * 2.2);
    const seasonality = Math.sin((index / 3) * Math.PI) * (4 + rng() * 6);
    const noise = (rng() - 0.5) * 6;
    const timestamp = new Date(Date.UTC(2025, index, 1)).toISOString().slice(0, 10);
    const value = Number((base + drift + seasonality + noise).toFixed(2));
    return {
      timestamp,
      value,
      label: `P${String(index + 1).padStart(2, "0")}`
    };
  });

  return {
    points,
    unit: readStringParam(input.params, "unit") ?? "pts",
    seriesLabel: readStringParam(input.params, "seriesLabel") ?? "Mock Series"
  };
}

function generateBreakdown(rng: RandomSource, input: Query): BreakdownData {
  const labels = ["North", "South", "Central", "Export", "Digital", "Retail"];
  const requested = readNumberParam(input.params, "slices") ?? 4;
  const count = input.perfProfile === "perf" ? clampInteger(requested, 3, 4) : clampInteger(requested, 3, 6);

  const slices = labels.slice(0, count).map((label, index) => {
    const value = Number((18 + rng() * 28 + index * 3).toFixed(2));
    return {
      key: label.toLowerCase(),
      label,
      value,
      color: `hsl(${Math.floor(rng() * 360)}, 60%, 52%)`
    };
  });

  const total = Number(slices.reduce((sum, item) => sum + item.value, 0).toFixed(2));
  return {
    slices,
    total,
    unit: readStringParam(input.params, "unit") ?? "%"
  };
}

function generateMatrix(rng: RandomSource, input: Query): MatrixData {
  const requestedRows = readNumberParam(input.params, "rows") ?? 4;
  const requestedColumns = readNumberParam(input.params, "columns") ?? 4;

  const rowCount = input.perfProfile === "perf" ? clampInteger(requestedRows, 2, 3) : clampInteger(requestedRows, 2, 6);
  const columnCount =
    input.perfProfile === "perf"
      ? clampInteger(requestedColumns, 2, 3)
      : clampInteger(requestedColumns, 2, 6);

  const rows = Array.from({ length: rowCount }, (_, index) => `R${index + 1}`);
  const columns = Array.from({ length: columnCount }, (_, index) => `C${index + 1}`);
  const values = rows.map(() => columns.map(() => Number((40 + rng() * 60).toFixed(2))));

  return {
    rows,
    columns,
    values,
    unit: readStringParam(input.params, "unit") ?? "%"
  };
}

function generateGauge(rng: RandomSource, input: Query): GaugeData {
  const min = readNumberParam(input.params, "min") ?? 0;
  const max = readNumberParam(input.params, "max") ?? 100;
  const spread = max - min <= 0 ? 100 : max - min;
  const value = Number((min + rng() * spread).toFixed(2));
  const target = Number((min + spread * 0.78).toFixed(2));

  const status: GaugeData["status"] = value >= target ? "good" : value >= target * 0.82 ? "warning" : "critical";

  return {
    value,
    min,
    max,
    target,
    unit: readStringParam(input.params, "unit") ?? "%",
    status
  };
}

function generateTableMini(rng: RandomSource, input: Query): TableMiniData {
  const baseColumns = ["Planned", "Actual", "Delta"];
  const rowLabels = ["Line A", "Line B", "Line C", "Line D", "Line E"];
  const requested = readNumberParam(input.params, "rows") ?? 4;
  const rowCount = input.perfProfile === "perf" ? clampInteger(requested, 2, 3) : clampInteger(requested, 2, 5);

  const rows = rowLabels.slice(0, rowCount).map((label) => {
    const planned = Number((80 + rng() * 30).toFixed(2));
    const actual = Number((planned - 6 + rng() * 12).toFixed(2));
    const delta = Number((actual - planned).toFixed(2));
    return {
      label,
      cells: [planned, actual, delta]
    };
  });

  return {
    columns: baseColumns,
    rows
  };
}

function generatePayload(shapeId: DataShapeId, rng: RandomSource, input: Query): unknown {
  switch (shapeId) {
    case "timeSeries":
      return generateTimeSeries(rng, input);
    case "breakdown":
      return generateBreakdown(rng, input);
    case "matrix":
      return generateMatrix(rng, input);
    case "gauge":
      return generateGauge(rng, input);
    case "tableMini":
      return generateTableMini(rng, input);
    default:
      return generateTimeSeries(rng, input);
  }
}

export function createMockProvider(options: MockProviderOptions = {}): DataProvider {
  const providerId = options.id ?? MOCK_PROVIDER_ID;
  const defaultSeed = options.defaultSeed ?? "mock-seed-v1";
  const defaultShapeId = options.defaultShapeId ?? "timeSeries";
  const cacheTtlMs = options.cacheTtlMs ?? 45_000;

  return {
    id: providerId,
    query(input: Query): ProviderResponse {
      const datasetId = input.datasetId;
      const shapeId = input.dataShapeId ?? inferShapeId(datasetId, defaultShapeId);

      const explicitSeed = input.seed?.trim().length ? input.seed.trim() : undefined;
      const seed = explicitSeed ?? `${defaultSeed}:${datasetId ?? "anonymous"}:${shapeId}`;

      const rng = createMulberry32(hashString(seed));
      const data = generatePayload(shapeId, rng, input);

      return {
        providerId,
        datasetId,
        dataShapeId: shapeId,
        data,
        cacheTtlMs,
        determinism: buildDeterminism(seed),
        metadata: {
          source: "mock-provider",
          randomSeedHash: hashString(seed)
        }
      };
    }
  };
}


