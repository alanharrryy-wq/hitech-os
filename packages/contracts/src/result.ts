import { AppError } from "./errors.js";

export interface Ok<T> {
  readonly ok: true;
  readonly value: T;
}

export interface Err<E> {
  readonly ok: false;
  readonly error: E;
}

export type Result<T, E> = Ok<T> | Err<E>;

export function ok<T>(value: T): Ok<T> {
  return { ok: true, value };
}

export function err<E>(error: E): Err<E> {
  return { ok: false, error };
}

export function isOk<T, E>(result: Result<T, E>): result is Ok<T> {
  return result.ok;
}

export function isErr<T, E>(result: Result<T, E>): result is Err<E> {
  return !result.ok;
}

export function map<T, U, E>(result: Result<T, E>, mapper: (value: T) => U): Result<U, E> {
  if (result.ok) {
    return ok(mapper(result.value));
  }
  return result;
}

export function mapErr<T, E, F>(result: Result<T, E>, mapper: (error: E) => F): Result<T, F> {
  if (result.ok) {
    return result;
  }
  return err(mapper(result.error));
}

export function andThen<T, U, E, F>(
  result: Result<T, E>,
  mapper: (value: T) => Result<U, F>
): Result<U, E | F> {
  if (result.ok) {
    return mapper(result.value);
  }
  return result;
}

export function unwrap<T, E>(result: Result<T, E>): T {
  if (result.ok) {
    return result.value;
  }

  if (result.error instanceof Error) {
    throw result.error;
  }

  throw new Error(`Attempted to unwrap Result.err: ${JSON.stringify(result.error)}`);
}

export function unwrapOr<T, E>(result: Result<T, E>, fallback: T): T {
  return result.ok ? result.value : fallback;
}

export function unwrapOrElse<T, E>(result: Result<T, E>, fallbackFactory: (error: E) => T): T {
  return result.ok ? result.value : fallbackFactory(result.error);
}

export function match<T, E, R>(
  result: Result<T, E>,
  handlers: {
    ok: (value: T) => R;
    err: (error: E) => R;
  }
): R {
  return result.ok ? handlers.ok(result.value) : handlers.err(result.error);
}

export function fromThrowable<T, E>(
  operation: () => T,
  mapError: (error: unknown) => E
): Result<T, E> {
  try {
    return ok(operation());
  } catch (error) {
    return err(mapError(error));
  }
}

export async function fromThrowableAsync<T, E>(
  operation: () => Promise<T>,
  mapError: (error: unknown) => E
): Promise<Result<T, E>> {
  try {
    return ok(await operation());
  } catch (error) {
    return err(mapError(error));
  }
}

export function tap<T, E>(
  result: Result<T, E>,
  callback: (result: Result<T, E>) => void
): Result<T, E> {
  callback(result);
  return result;
}

export function all<T, E>(results: readonly Result<T, E>[]): Result<readonly T[], E> {
  const values: T[] = [];

  for (const result of results) {
    if (!result.ok) {
      return result;
    }
    values.push(result.value);
  }

  return ok(values);
}

export function partition<T, E>(
  results: readonly Result<T, E>[]
): {
  readonly oks: readonly T[];
  readonly errs: readonly E[];
} {
  const oks: T[] = [];
  const errs: E[] = [];

  for (const result of results) {
    if (result.ok) {
      oks.push(result.value);
    } else {
      errs.push(result.error);
    }
  }

  return {
    oks,
    errs
  };
}

export function toPromise<T, E>(result: Result<T, E>): Promise<T> {
  if (result.ok) {
    return Promise.resolve(result.value);
  }

  if (result.error instanceof Error) {
    return Promise.reject(result.error);
  }

  return Promise.reject(
    new Error(`Result error is not an Error instance: ${JSON.stringify(result.error)}`)
  );
}

export function toAppErrorResult<T>(value: T): Result<T, AppError> {
  return ok(value);
}
