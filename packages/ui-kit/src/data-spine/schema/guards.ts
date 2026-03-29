import type {
  DataShapeId,
  DataShapeValidationIssue,
  DataShapeValidationResult
} from "../types.js";
import type {
  BreakdownData,
  BreakdownSlice,
  GaugeData,
  MatrixData,
  TableMiniCell,
  TableMiniData,
  TableMiniRow,
  TimeSeriesData,
  TimeSeriesPoint
} from "./shapes.js";

function issue(path: string, message: string): DataShapeValidationIssue {
  return { path, message };
}

function success<TData>(value: TData): DataShapeValidationResult<TData> {
  return { ok: true, value, errors: [] };
}

function failure<TData = never>(errors: readonly DataShapeValidationIssue[]): DataShapeValidationResult<TData> {
  return { ok: false, errors };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function nonEmptyString(
  value: unknown,
  path: string,
  errors: DataShapeValidationIssue[]
): string | undefined {
  if (typeof value !== "string") {
    errors.push(issue(path, "must be a string."));
    return undefined;
  }

  const next = value.trim();
  if (next.length === 0) {
    errors.push(issue(path, "must not be empty."));
    return undefined;
  }

  return next;
}

function finiteNumber(
  value: unknown,
  path: string,
  errors: DataShapeValidationIssue[]
): number | undefined {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    errors.push(issue(path, "must be a finite number."));
    return undefined;
  }

  return value;
}

function optionalString(
  value: unknown,
  path: string,
  errors: DataShapeValidationIssue[]
): string | undefined {
  if (value === undefined) {
    return undefined;
  }

  if (typeof value !== "string") {
    errors.push(issue(path, "must be a string when provided."));
    return undefined;
  }

  return value;
}

export class DataShapeGuardError extends Error {
  readonly shapeId: DataShapeId;
  readonly issues: readonly DataShapeValidationIssue[];

  constructor(shapeId: DataShapeId, issues: readonly DataShapeValidationIssue[]) {
    super(formatGuardErrors(shapeId, issues));
    this.name = "DataShapeGuardError";
    this.shapeId = shapeId;
    this.issues = issues;
  }
}

export function isDataShapeGuardError(value: unknown): value is DataShapeGuardError {
  return value instanceof DataShapeGuardError;
}

export function formatGuardErrors(
  shapeId: DataShapeId,
  issues: readonly DataShapeValidationIssue[]
): string {
  if (issues.length === 0) {
    return `Validation failed for shape '${shapeId}'.`;
  }

  const head = issues
    .slice(0, 6)
    .map((entry) => `${entry.path} ${entry.message}`)
    .join(" | ");
  const tail = issues.length > 6 ? ` | +${issues.length - 6} more issue(s).` : "";
  return `Validation failed for shape '${shapeId}': ${head}${tail}`;
}

export function validateTimeSeries(input: unknown): DataShapeValidationResult<TimeSeriesData> {
  const errors: DataShapeValidationIssue[] = [];

  if (!isRecord(input)) {
    return failure([issue("timeSeries", "must be an object.")]);
  }

  const pointsRaw = input["points"];
  if (!Array.isArray(pointsRaw)) {
    errors.push(issue("timeSeries.points", "must be an array."));
    return failure(errors);
  }

  if (pointsRaw.length === 0) {
    errors.push(issue("timeSeries.points", "must include at least one point."));
  }

  const points: TimeSeriesPoint[] = [];

  for (let index = 0; index < pointsRaw.length; index += 1) {
    const row = pointsRaw[index];
    const rowPath = `timeSeries.points[${index}]`;

    if (!isRecord(row)) {
      errors.push(issue(rowPath, "must be an object."));
      continue;
    }

    const timestamp = nonEmptyString(row["timestamp"], `${rowPath}.timestamp`, errors);
    const value = finiteNumber(row["value"], `${rowPath}.value`, errors);
    const label = optionalString(row["label"], `${rowPath}.label`, errors);

    if (timestamp === undefined || value === undefined) {
      continue;
    }

    points.push({
      timestamp,
      value,
      ...(label !== undefined ? { label } : {})
    });
  }

  const unit = optionalString(input["unit"], "timeSeries.unit", errors);
  const seriesLabel = optionalString(input["seriesLabel"], "timeSeries.seriesLabel", errors);

  if (errors.length > 0) {
    return failure(errors);
  }

  return success({
    points,
    ...(unit !== undefined ? { unit } : {}),
    ...(seriesLabel !== undefined ? { seriesLabel } : {})
  });
}

export function validateBreakdown(input: unknown): DataShapeValidationResult<BreakdownData> {
  const errors: DataShapeValidationIssue[] = [];

  if (!isRecord(input)) {
    return failure([issue("breakdown", "must be an object.")]);
  }

  const slicesRaw = input["slices"];
  if (!Array.isArray(slicesRaw)) {
    return failure([issue("breakdown.slices", "must be an array.")]);
  }

  if (slicesRaw.length === 0) {
    errors.push(issue("breakdown.slices", "must include at least one slice."));
  }

  const slices: BreakdownSlice[] = [];

  for (let index = 0; index < slicesRaw.length; index += 1) {
    const row = slicesRaw[index];
    const rowPath = `breakdown.slices[${index}]`;

    if (!isRecord(row)) {
      errors.push(issue(rowPath, "must be an object."));
      continue;
    }

    const key = nonEmptyString(row["key"], `${rowPath}.key`, errors);
    const label = nonEmptyString(row["label"], `${rowPath}.label`, errors);
    const value = finiteNumber(row["value"], `${rowPath}.value`, errors);
    const color = optionalString(row["color"], `${rowPath}.color`, errors);

    if (key === undefined || label === undefined || value === undefined) {
      continue;
    }

    slices.push({
      key,
      label,
      value,
      ...(color !== undefined ? { color } : {})
    });
  }

  const total =
    input["total"] === undefined ? undefined : finiteNumber(input["total"], "breakdown.total", errors);
  const unit = optionalString(input["unit"], "breakdown.unit", errors);

  if (errors.length > 0) {
    return failure(errors);
  }

  return success({
    slices,
    ...(total !== undefined ? { total } : {}),
    ...(unit !== undefined ? { unit } : {})
  });
}

export function validateMatrix(input: unknown): DataShapeValidationResult<MatrixData> {
  const errors: DataShapeValidationIssue[] = [];

  if (!isRecord(input)) {
    return failure([issue("matrix", "must be an object.")]);
  }

  const rowsRaw = input["rows"];
  const columnsRaw = input["columns"];
  const valuesRaw = input["values"];

  if (!Array.isArray(rowsRaw)) {
    errors.push(issue("matrix.rows", "must be an array of row labels."));
  }

  if (!Array.isArray(columnsRaw)) {
    errors.push(issue("matrix.columns", "must be an array of column labels."));
  }

  if (!Array.isArray(valuesRaw)) {
    errors.push(issue("matrix.values", "must be a two-dimensional array."));
  }

  if (errors.length > 0) {
    return failure(errors);
  }

  const rowEntries = rowsRaw as unknown[];
  const columnEntries = columnsRaw as unknown[];
  const valueEntries = valuesRaw as unknown[];

  const rows: string[] = [];
  const columns: string[] = [];

  for (let index = 0; index < rowEntries.length; index += 1) {
    const next = nonEmptyString(rowEntries[index], `matrix.rows[${index}]`, errors);
    if (next !== undefined) {
      rows.push(next);
    }
  }

  for (let index = 0; index < columnEntries.length; index += 1) {
    const next = nonEmptyString(columnEntries[index], `matrix.columns[${index}]`, errors);
    if (next !== undefined) {
      columns.push(next);
    }
  }

  if (rows.length === 0) {
    errors.push(issue("matrix.rows", "must include at least one row label."));
  }

  if (columns.length === 0) {
    errors.push(issue("matrix.columns", "must include at least one column label."));
  }

  const values: number[][] = [];

  for (let rowIndex = 0; rowIndex < valueEntries.length; rowIndex += 1) {
    const matrixRow = valueEntries[rowIndex];
    const rowPath = `matrix.values[${rowIndex}]`;

    if (!Array.isArray(matrixRow)) {
      errors.push(issue(rowPath, "must be an array."));
      continue;
    }

    if (columns.length > 0 && matrixRow.length !== columns.length) {
      errors.push(issue(rowPath, `must contain exactly ${columns.length} values.`));
    }

    const nextRow: number[] = [];
    for (let columnIndex = 0; columnIndex < matrixRow.length; columnIndex += 1) {
      const cell = finiteNumber(matrixRow[columnIndex], `${rowPath}[${columnIndex}]`, errors);
      if (cell !== undefined) {
        nextRow.push(cell);
      }
    }

    values.push(nextRow);
  }

  if (rows.length > 0 && values.length !== rows.length) {
    errors.push(issue("matrix.values", `must contain exactly ${rows.length} row(s).`));
  }

  const unit = optionalString(input["unit"], "matrix.unit", errors);

  if (errors.length > 0) {
    return failure(errors);
  }

  return success({
    rows,
    columns,
    values,
    ...(unit !== undefined ? { unit } : {})
  });
}

function parseGaugeStatus(
  value: unknown,
  path: string,
  errors: DataShapeValidationIssue[]
): GaugeData["status"] {
  if (value === undefined) {
    return undefined;
  }

  if (value === "neutral" || value === "good" || value === "warning" || value === "critical") {
    return value;
  }

  errors.push(issue(path, "must be one of neutral|good|warning|critical when provided."));
  return undefined;
}

export function validateGauge(input: unknown): DataShapeValidationResult<GaugeData> {
  const errors: DataShapeValidationIssue[] = [];

  if (!isRecord(input)) {
    return failure([issue("gauge", "must be an object.")]);
  }

  const value = finiteNumber(input["value"], "gauge.value", errors);
  const min = finiteNumber(input["min"], "gauge.min", errors);
  const max = finiteNumber(input["max"], "gauge.max", errors);
  const target = input["target"] === undefined ? undefined : finiteNumber(input["target"], "gauge.target", errors);
  const unit = optionalString(input["unit"], "gauge.unit", errors);
  const status = parseGaugeStatus(input["status"], "gauge.status", errors);

  if (min !== undefined && max !== undefined && min >= max) {
    errors.push(issue("gauge", "requires min to be less than max."));
  }

  if (value !== undefined && min !== undefined && value < min) {
    errors.push(issue("gauge.value", "must be greater than or equal to min."));
  }

  if (value !== undefined && max !== undefined && value > max) {
    errors.push(issue("gauge.value", "must be less than or equal to max."));
  }

  if (target !== undefined && min !== undefined && target < min) {
    errors.push(issue("gauge.target", "must be greater than or equal to min."));
  }

  if (target !== undefined && max !== undefined && target > max) {
    errors.push(issue("gauge.target", "must be less than or equal to max."));
  }

  if (errors.length > 0 || value === undefined || min === undefined || max === undefined) {
    return failure(errors);
  }

  return success({
    value,
    min,
    max,
    ...(target !== undefined ? { target } : {}),
    ...(unit !== undefined ? { unit } : {}),
    ...(status !== undefined ? { status } : {})
  });
}

function parseTableMiniCell(value: unknown, path: string, errors: DataShapeValidationIssue[]): TableMiniCell | undefined {
  if (value === null || typeof value === "string") {
    return value;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  errors.push(issue(path, "must be a string, finite number, or null."));
  return undefined;
}

export function validateTableMini(input: unknown): DataShapeValidationResult<TableMiniData> {
  const errors: DataShapeValidationIssue[] = [];

  if (!isRecord(input)) {
    return failure([issue("tableMini", "must be an object.")]);
  }

  const columnsRaw = input["columns"];
  const rowsRaw = input["rows"];

  if (!Array.isArray(columnsRaw)) {
    errors.push(issue("tableMini.columns", "must be an array."));
  }

  if (!Array.isArray(rowsRaw)) {
    errors.push(issue("tableMini.rows", "must be an array."));
  }

  if (errors.length > 0) {
    return failure(errors);
  }

  const columnEntries = columnsRaw as unknown[];
  const rowEntries = rowsRaw as unknown[];

  const columns: string[] = [];

  for (let index = 0; index < columnEntries.length; index += 1) {
    const next = nonEmptyString(columnEntries[index], `tableMini.columns[${index}]`, errors);
    if (next !== undefined) {
      columns.push(next);
    }
  }

  if (columns.length === 0) {
    errors.push(issue("tableMini.columns", "must include at least one column label."));
  }

  const rows: TableMiniRow[] = [];

  for (let rowIndex = 0; rowIndex < rowEntries.length; rowIndex += 1) {
    const rowRaw = rowEntries[rowIndex];
    const rowPath = `tableMini.rows[${rowIndex}]`;

    if (!isRecord(rowRaw)) {
      errors.push(issue(rowPath, "must be an object."));
      continue;
    }

    const label = nonEmptyString(rowRaw["label"], `${rowPath}.label`, errors);
    const cellsRaw = rowRaw["cells"];

    if (!Array.isArray(cellsRaw)) {
      errors.push(issue(`${rowPath}.cells`, "must be an array."));
      continue;
    }

    if (columns.length > 0 && cellsRaw.length !== columns.length) {
      errors.push(issue(`${rowPath}.cells`, `must contain exactly ${columns.length} cell(s).`));
    }

    const cells: TableMiniCell[] = [];

    for (let cellIndex = 0; cellIndex < cellsRaw.length; cellIndex += 1) {
      const parsed = parseTableMiniCell(cellsRaw[cellIndex], `${rowPath}.cells[${cellIndex}]`, errors);
      if (parsed !== undefined || cellsRaw[cellIndex] === null) {
        cells.push(parsed ?? null);
      }
    }

    if (label !== undefined) {
      rows.push({ label, cells });
    }
  }

  if (rows.length === 0) {
    errors.push(issue("tableMini.rows", "must include at least one row."));
  }

  if (errors.length > 0) {
    return failure(errors);
  }

  return success({
    columns,
    rows
  });
}

