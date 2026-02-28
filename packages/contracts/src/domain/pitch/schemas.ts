import { z } from "zod";
import {
  MONTHS_PER_YEAR,
  PITCH_DOMAIN_ID,
  PITCH_ROUTE_DOUBLE_ENGINE,
  PITCH_ROUTE_HITECH_OS,
  PITCH_ROUTE_INDUSTRIAL_FLOW,
  PITCH_ROUTE_VALUATION,
  PITCH_SCREEN_ROUTES,
  PITCH_VALUATION_TABLE_HEADERS
} from "./constants.js";
import type { PitchDeck } from "./types.js";

const NonEmptyStringSchema = z.string().trim().min(1);
const NonNegativeNumberSchema = z.number().finite().nonnegative();

const PitchDoubleEngineScreenSchema = z
  .object({
    id: z.literal("double-engine"),
    route: z.literal(PITCH_ROUTE_DOUBLE_ENGINE),
    title: NonEmptyStringSchema,
    columns: z
      .object({
        left: z.array(NonEmptyStringSchema).length(5),
        right: z.array(NonEmptyStringSchema).length(6)
      })
      .strict(),
    microcopy: z
      .object({
        left: NonEmptyStringSchema,
        right: NonEmptyStringSchema
      })
      .strict(),
    implicitMessage: NonEmptyStringSchema
  })
  .strict();

const PitchIndustrialFlowKpisSchema = z
  .object({
    totalModules: z.number().int().positive(),
    monthlyModules: z.number().int().positive(),
    monthlyBillingUsd: NonNegativeNumberSchema,
    monthlyProfitUsd: NonNegativeNumberSchema,
    annualProfitUsd: NonNegativeNumberSchema,
    annualProfitCompactText: NonEmptyStringSchema
  })
  .strict()
  .superRefine((value, context) => {
    const expectedAnnual = value.monthlyProfitUsd * MONTHS_PER_YEAR;
    if (Math.abs(value.annualProfitUsd - expectedAnnual) > 0.000001) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: `annualProfitUsd must equal monthlyProfitUsd * ${MONTHS_PER_YEAR}`
      });
    }
  });

const PitchIndustrialFlowScreenSchema = z
  .object({
    id: z.literal("industrial-flow"),
    route: z.literal(PITCH_ROUTE_INDUSTRIAL_FLOW),
    title: NonEmptyStringSchema,
    kpis: PitchIndustrialFlowKpisSchema,
    cycle: z
      .object({
        months: z.number().int().positive(),
        statement: NonEmptyStringSchema
      })
      .strict(),
    microcopy: NonEmptyStringSchema
  })
  .strict()
  .superRefine((value, context) => {
    const expectedMonths = Math.ceil(value.kpis.totalModules / value.kpis.monthlyModules);
    if (value.cycle.months !== expectedMonths) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: `cycle.months must equal ceil(totalModules / monthlyModules) = ${expectedMonths}`
      });
    }
  });

const PitchHitechOsScreenSchema = z
  .object({
    id: z.literal("hitech-os"),
    route: z.literal(PITCH_ROUTE_HITECH_OS),
    title: NonEmptyStringSchema,
    bullets: z.array(NonEmptyStringSchema).length(7),
    strongPhrase: NonEmptyStringSchema
  })
  .strict();

const PitchValuationScreenSchema = z
  .object({
    id: z.literal("valuation"),
    route: z.literal(PITCH_ROUTE_VALUATION),
    title: NonEmptyStringSchema,
    blockOne: z.array(NonEmptyStringSchema).length(4),
    blockTwo: z.array(NonEmptyStringSchema).length(5),
    combinedLine: NonEmptyStringSchema,
    blockThree: z.array(NonEmptyStringSchema).length(2),
    table: z
      .object({
        headers: z.tuple([
          z.literal(PITCH_VALUATION_TABLE_HEADERS[0]),
          z.literal(PITCH_VALUATION_TABLE_HEADERS[1]),
          z.literal(PITCH_VALUATION_TABLE_HEADERS[2]),
          z.literal(PITCH_VALUATION_TABLE_HEADERS[3])
        ]),
        rows: z
          .array(
            z
              .object({
                model: NonEmptyStringSchema,
                multiple: NonEmptyStringSchema,
                risk: NonEmptyStringSchema,
                scalability: NonEmptyStringSchema
              })
              .strict()
          )
          .length(2)
      })
      .strict()
  })
  .strict();

export const PitchScreenRouteSchema = z.enum(PITCH_SCREEN_ROUTES);

export const PitchScreenSchema = z.discriminatedUnion("id", [
  PitchDoubleEngineScreenSchema,
  PitchIndustrialFlowScreenSchema,
  PitchHitechOsScreenSchema,
  PitchValuationScreenSchema
]);

export const PitchDeckSchema = z
  .object({
    domain: z.literal(PITCH_DOMAIN_ID),
    version: NonEmptyStringSchema,
    screens: z.tuple([
      PitchDoubleEngineScreenSchema,
      PitchIndustrialFlowScreenSchema,
      PitchHitechOsScreenSchema,
      PitchValuationScreenSchema
    ])
  })
  .strict();

export type PitchDeckContract = z.infer<typeof PitchDeckSchema>;

export function parsePitchDeck(input: unknown): PitchDeck {
  return PitchDeckSchema.parse(input);
}

export function safeParsePitchDeck(input: unknown) {
  return PitchDeckSchema.safeParse(input);
}
