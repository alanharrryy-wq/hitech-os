"use client";

import {
  AppError,
  NotFoundError,
  UnauthorizedError,
  ConflictError,
  RateLimitError,
  parseOrThrow
} from "@hitech/contracts";
import { z } from "zod";

function toHttpError(status: number, path: string): AppError {
  if (status === 401) {
    return new UnauthorizedError(`Unauthorized request to ${path}`);
  }

  if (status === 404) {
    return new NotFoundError(`Resource not found at ${path}`);
  }

  if (status === 409) {
    return new ConflictError(`Conflict while requesting ${path}`);
  }

  if (status === 429) {
    return new RateLimitError(`Rate limit reached for ${path}`);
  }

  return new AppError("INTERNAL_ERROR", `Request failed for ${path} with status ${status}`, status);
}

export async function fetchContract<TSchema extends z.ZodTypeAny>(input: {
  readonly path: string;
  readonly schema: TSchema;
  readonly init?: RequestInit;
  readonly resource: string;
}): Promise<z.infer<TSchema>> {
  const response = await fetch(input.path, {
    ...input.init,
    headers: {
      "content-type": "application/json",
      ...(input.init?.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw toHttpError(response.status, input.path);
  }

  const json = (await response.json()) as unknown;

  return parseOrThrow(input.schema, json, {
    resource: input.resource,
    operation: "client-fetch"
  });
}
