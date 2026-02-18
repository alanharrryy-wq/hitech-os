import { z } from "zod";

export const HealthStatusSchema = z.enum(["ok", "degraded", "error"]);

export const HealthCheckSchema = z
  .object({
    name: z.string().min(1),
    status: HealthStatusSchema,
    message: z.string().min(1)
  })
  .strict();

export const HealthReportSchema = z
  .object({
    service: z.string().min(1),
    version: z.string().min(1),
    contractVersion: z.string().min(1),
    status: HealthStatusSchema,
    timestampUtc: z.string().datetime({ offset: true }),
    checks: z.array(HealthCheckSchema)
  })
  .strict();

export type HealthReport = z.infer<typeof HealthReportSchema>;
export type HealthCheck = z.infer<typeof HealthCheckSchema>;

export function createHealthyReport(input: {
  service: string;
  version: string;
  contractVersion: string;
  timestampUtc: string;
  checks?: string[];
}): HealthReport {
  const sortedChecks = [...(input.checks ?? ["contracts", "runtime"])].sort((left, right) =>
    left.localeCompare(right)
  );

  return {
    service: input.service,
    version: input.version,
    contractVersion: input.contractVersion,
    status: "ok",
    timestampUtc: input.timestampUtc,
    checks: sortedChecks.map((name) => ({
      name,
      status: "ok",
      message: "ok"
    }))
  };
}
