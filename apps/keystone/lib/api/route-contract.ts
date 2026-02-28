import { parseOrThrow } from "@hitech/contracts";
import { z } from "zod";

export function validateRoutePayload<TSchema extends z.ZodTypeAny>(
  schema: TSchema,
  payload: unknown,
  resource: string
): z.infer<TSchema> {
  return parseOrThrow(schema, payload, {
    resource,
    operation: "route-payload"
  });
}
