export type AppErrorCode =
  | "VALIDATION_ERROR"
  | "NOT_FOUND"
  | "UNAUTHORIZED"
  | "CONFLICT"
  | "RATE_LIMIT"
  | "INTERNAL_ERROR";

export interface AppErrorContext {
  readonly resource?: string;
  readonly operation?: string;
  readonly details?: Record<string, unknown>;
  readonly cause?: unknown;
}

export class AppError extends Error {
  public readonly code: AppErrorCode;
  public readonly status: number;
  public readonly details: Record<string, unknown>;

  public constructor(
    code: AppErrorCode,
    message: string,
    status: number,
    context: AppErrorContext = {}
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.status = status;
    this.details = {
      resource: context.resource,
      operation: context.operation,
      ...(context.details ?? {})
    };

    if (context.cause instanceof Error) {
      (this as Error & { cause?: Error }).cause = context.cause;
    }
  }

  public toJSON(): {
    code: AppErrorCode;
    name: string;
    message: string;
    status: number;
    details: Record<string, unknown>;
  } {
    return {
      code: this.code,
      name: this.name,
      message: this.message,
      status: this.status,
      details: this.details
    };
  }
}

export class ValidationError extends AppError {
  public constructor(message: string, context: AppErrorContext = {}) {
    super("VALIDATION_ERROR", message, 400, context);
  }
}

export class NotFoundError extends AppError {
  public constructor(message: string, context: AppErrorContext = {}) {
    super("NOT_FOUND", message, 404, context);
  }
}

export class UnauthorizedError extends AppError {
  public constructor(message: string, context: AppErrorContext = {}) {
    super("UNAUTHORIZED", message, 401, context);
  }
}

export class ConflictError extends AppError {
  public constructor(message: string, context: AppErrorContext = {}) {
    super("CONFLICT", message, 409, context);
  }
}

export class RateLimitError extends AppError {
  public readonly retryAfterSeconds: number;

  public constructor(message: string, retryAfterSeconds = 60, context: AppErrorContext = {}) {
    super("RATE_LIMIT", message, 429, {
      ...context,
      details: {
        retryAfterSeconds,
        ...(context.details ?? {})
      }
    });
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

export function isAppError(input: unknown): input is AppError {
  return input instanceof AppError;
}
