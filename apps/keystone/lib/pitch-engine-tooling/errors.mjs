export class ToolingError extends Error {
  constructor(message, code = "TOOLING_ERROR", context = undefined) {
    super(message)
    this.name = "ToolingError"
    this.code = code
    this.context = context
  }
}

export class ValidationError extends ToolingError {
  constructor(message, context = undefined) {
    super(message, "VALIDATION_ERROR", context)
    this.name = "ValidationError"
  }
}

export class InvariantError extends ToolingError {
  constructor(message, context = undefined) {
    super(message, "INVARIANT_ERROR", context)
    this.name = "InvariantError"
  }
}

export class OwnershipError extends ToolingError {
  constructor(message, context = undefined) {
    super(message, "OWNERSHIP_ERROR", context)
    this.name = "OwnershipError"
  }
}

export class ExternalDependencyError extends ToolingError {
  constructor(message, context = undefined) {
    super(message, "EXTERNAL_DEPENDENCY_ERROR", context)
    this.name = "ExternalDependencyError"
  }
}

export function serializeError(error) {
  if (!error) {
    return {
      name: "UnknownError",
      message: "Unknown error",
      stack: ""
    }
  }

  const anyError = error
  return {
    name: typeof anyError.name === "string" ? anyError.name : "Error",
    message: typeof anyError.message === "string" ? anyError.message : String(anyError),
    code: typeof anyError.code === "string" ? anyError.code : undefined,
    context: anyError.context,
    stack: typeof anyError.stack === "string" ? anyError.stack : ""
  }
}

export function asToolingError(error, fallbackCode = "TOOLING_ERROR") {
  if (error instanceof ToolingError) {
    return error
  }

  if (error instanceof Error) {
    return new ToolingError(error.message, fallbackCode, {
      stack: error.stack
    })
  }

  return new ToolingError(String(error), fallbackCode)
}
