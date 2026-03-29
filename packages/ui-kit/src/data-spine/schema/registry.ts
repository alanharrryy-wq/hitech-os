import type { DataShapeId, DataShapeValidationResult, DataShapeValidator } from "../types.js";
import {
  DataShapeGuardError,
  validateBreakdown,
  validateGauge,
  validateMatrix,
  validateTableMini,
  validateTimeSeries
} from "./guards.js";

const validators = new Map<DataShapeId, DataShapeValidator<unknown>>();

function assertShapeId(shapeId: DataShapeId): void {
  if (typeof shapeId !== "string" || shapeId.trim().length === 0) {
    throw new Error("Data shape id must be a non-empty string.");
  }
}

function registerDefaults(): void {
  if (validators.size > 0) {
    return;
  }

  validators.set("timeSeries", validateTimeSeries);
  validators.set("breakdown", validateBreakdown);
  validators.set("matrix", validateMatrix);
  validators.set("gauge", validateGauge);
  validators.set("tableMini", validateTableMini);
}

registerDefaults();

export function registerDataShape<TData>(
  shapeId: DataShapeId,
  validator: DataShapeValidator<TData>
): void {
  assertShapeId(shapeId);
  validators.set(shapeId, validator as DataShapeValidator<unknown>);
}

export function listRegisteredDataShapes(): readonly DataShapeId[] {
  return Array.from(validators.keys()).sort((left, right) => left.localeCompare(right));
}

export function safeValidateDataShape<TData = unknown>(
  shapeId: DataShapeId,
  input: unknown
): DataShapeValidationResult<TData> {
  assertShapeId(shapeId);

  const validator = validators.get(shapeId);
  if (validator === undefined) {
    return {
      ok: false,
      errors: [{ path: String(shapeId), message: `is not registered in the data-shape registry.` }]
    };
  }

  return validator(input) as DataShapeValidationResult<TData>;
}

export function validateDataShape<TData = unknown>(shapeId: DataShapeId, input: unknown): TData {
  const result = safeValidateDataShape<TData>(shapeId, input);

  if (!result.ok) {
    throw new DataShapeGuardError(shapeId, result.errors);
  }

  return result.value;
}

