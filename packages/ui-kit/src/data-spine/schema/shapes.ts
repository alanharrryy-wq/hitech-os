export const DATA_SHAPE_IDS = ["timeSeries", "breakdown", "matrix", "gauge", "tableMini"] as const;

export interface TimeSeriesPoint {
  readonly timestamp: string;
  readonly value: number;
  readonly label?: string;
}

export interface TimeSeriesData {
  readonly points: readonly TimeSeriesPoint[];
  readonly unit?: string;
  readonly seriesLabel?: string;
}

export interface BreakdownSlice {
  readonly key: string;
  readonly label: string;
  readonly value: number;
  readonly color?: string;
}

export interface BreakdownData {
  readonly slices: readonly BreakdownSlice[];
  readonly total?: number;
  readonly unit?: string;
}

export interface MatrixData {
  readonly rows: readonly string[];
  readonly columns: readonly string[];
  readonly values: readonly (readonly number[])[];
  readonly unit?: string;
}

export interface GaugeData {
  readonly value: number;
  readonly min: number;
  readonly max: number;
  readonly target?: number;
  readonly unit?: string;
  readonly status?: "neutral" | "good" | "warning" | "critical";
}

export type TableMiniCell = string | number | null;

export interface TableMiniRow {
  readonly label: string;
  readonly cells: readonly TableMiniCell[];
}

export interface TableMiniData {
  readonly columns: readonly string[];
  readonly rows: readonly TableMiniRow[];
}

export interface DataShapeMap {
  readonly timeSeries: TimeSeriesData;
  readonly breakdown: BreakdownData;
  readonly matrix: MatrixData;
  readonly gauge: GaugeData;
  readonly tableMini: TableMiniData;
}

