import { z } from "zod";
import { EvidenceIdSchema, RunIdSchema, UserIdSchema } from "../brands.js";
import { IsoDateTimeSchema } from "./shared.js";

export const EvidenceKindSchema = z.enum([
  "log",
  "artifact",
  "trace",
  "screenshot",
  "report",
  "metric-snapshot"
]);

export const EvidenceMimeTypeSchema = z
  .string()
  .regex(/^[a-z0-9!#$&^_.+-]+\/[a-z0-9!#$&^_.+-]+$/i)
  .max(120);

export const EvidenceChecksumAlgorithmSchema = z.enum(["sha256", "sha512", "md5"]);

export const EvidenceChecksumSchema = z
  .object({
    algorithm: EvidenceChecksumAlgorithmSchema,
    value: z
      .string()
      .trim()
      .regex(/^[a-f0-9]{32,128}$/i)
  })
  .strict();

export const EvidenceLocationSchema = z
  .object({
    storage: z.enum(["local", "s3", "gcs", "azure", "memory"]),
    path: z.string().min(1).max(4096),
    bucket: z.string().max(128).nullable().default(null),
    region: z.string().max(64).nullable().default(null)
  })
  .strict();

export const EvidenceRefSchema = z
  .object({
    id: EvidenceIdSchema,
    runId: RunIdSchema,
    kind: EvidenceKindSchema,
    label: z.string().min(2).max(160),
    mime: EvidenceMimeTypeSchema,
    sizeBytes: z.number().int().min(0),
    createdAt: IsoDateTimeSchema,
    createdBy: UserIdSchema,
    location: EvidenceLocationSchema,
    checksum: EvidenceChecksumSchema.nullable().default(null),
    redacted: z.boolean().default(false),
    tags: z.array(z.string().min(1).max(48)).max(12).default([])
  })
  .strict();

export const EvidenceBundleSchema = z
  .object({
    runId: RunIdSchema,
    totalBytes: z.number().int().min(0),
    count: z.number().int().min(0),
    items: z.array(EvidenceRefSchema),
    generatedAt: IsoDateTimeSchema
  })
  .strict()
  .superRefine((value, ctx) => {
    const byRunIdMismatch = value.items.filter((item) => item.runId !== value.runId);
    if (byRunIdMismatch.length > 0) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["items"],
        message: "All evidence items must match bundle runId"
      });
    }

    const sum = value.items.reduce((acc, item) => acc + item.sizeBytes, 0);
    if (sum !== value.totalBytes) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["totalBytes"],
        message: "totalBytes must equal sum(items.sizeBytes)"
      });
    }

    if (value.count !== value.items.length) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["count"],
        message: "count must equal items.length"
      });
    }
  });

export type EvidenceKind = z.infer<typeof EvidenceKindSchema>;
export type EvidenceRef = z.infer<typeof EvidenceRefSchema>;
export type EvidenceBundle = z.infer<typeof EvidenceBundleSchema>;

export function isPreviewableEvidence(mime: string): boolean {
  return (
    mime.startsWith("text/") ||
    mime.startsWith("image/") ||
    mime === "application/json" ||
    mime === "application/xml"
  );
}

export function summarizeEvidenceKinds(
  items: readonly EvidenceRef[]
): Record<EvidenceKind, number> {
  const summary: Record<EvidenceKind, number> = {
    log: 0,
    artifact: 0,
    trace: 0,
    screenshot: 0,
    report: 0,
    "metric-snapshot": 0
  };

  for (const item of items) {
    summary[item.kind] += 1;
  }

  return summary;
}

export function sortEvidenceByDate(items: readonly EvidenceRef[]): EvidenceRef[] {
  return [...items].sort((left, right) => Date.parse(right.createdAt) - Date.parse(left.createdAt));
}
