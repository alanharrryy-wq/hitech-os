import { z } from "zod";

export const IsoDateTimeSchema = z.string().datetime({ offset: true });

export const SeveritySchema = z.enum(["debug", "info", "warn", "error", "critical"]);

export const PaginationSchema = z
  .object({
    page: z.number().int().min(1).default(1),
    pageSize: z.number().int().min(1).max(200).default(25),
    total: z.number().int().min(0)
  })
  .strict();

export type Pagination = z.infer<typeof PaginationSchema>;

export function ensureIsoDateRange(from: string, to: string): boolean {
  return Date.parse(from) <= Date.parse(to);
}

export function nowIso(): string {
  return new Date().toISOString();
}
