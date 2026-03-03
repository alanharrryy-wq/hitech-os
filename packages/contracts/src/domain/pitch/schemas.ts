import { z } from "zod";
import {
  PITCH_COMPARISON_ROWS,
  PITCH_COPY_LOCK_NOTICE,
  PITCH_DECK_ID,
  PITCH_DECK_VERSION,
  PITCH_LAYER_PROFILE_HINTS,
  PITCH_LOCALE,
  PITCH_ROUTE_BASE,
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_SLUGS,
  PITCH_TABLE_HEADERS,
  PITCH_VALIDATION_MESSAGES
} from "./constants.js";

const NonEmptyText = z.string().min(1).max(280);
const LongText = z.string().min(1).max(520);
const NumericText = z.string().min(1).max(64);

export const PitchScreenSlugSchema = z.enum(PITCH_SCREEN_SLUGS);

export const PitchRouteSchema = z
  .string()
  .min(1)
  .regex(
    /^\/pitch(\/01-double-engine|\/02-industrial-flow|\/03-hitech-os|\/04-valuation|\/05-inventory-foundation|\/06-shipments-receiving)$/
  );

export const PitchNavigationLinkSchema = z.object({
  slug: PitchScreenSlugSchema,
  href: PitchRouteSchema,
  title: LongText,
  order: z.number().int().min(1).max(6)
});

export const PitchNavigationSchema = z.object({
  base: z.literal(PITCH_ROUTE_BASE),
  links: z.array(PitchNavigationLinkSchema).length(6)
});

export const PitchBulletSchema = z.object({
  id: z.string().min(1).max(80),
  text: LongText,
  emphasis: z.enum(["neutral", "positive", "critical"]).default("neutral"),
  weight: z.enum(["support", "core", "anchor"]).default("core")
});

export const PitchMicrocopySchema = z.object({
  id: z.string().min(1).max(80),
  text: LongText
});

export const PitchEngineColumnSchema = z.object({
  id: z.string().min(1).max(80),
  heading: LongText,
  bullets: z.array(PitchBulletSchema).min(1).max(12),
  microcopy: z.array(PitchMicrocopySchema).min(1).max(4)
});

export const PitchKpiSchema = z.object({
  id: z.string().min(1).max(80),
  label: LongText,
  value: NumericText,
  note: z.string().max(120).optional()
});

export const PitchFeatureSchema = z.object({
  id: z.string().min(1).max(80),
  text: LongText,
  category: z.enum(["operation", "quality", "traceability", "visibility", "vertical"])
});

export const PitchStatusChipSchema = z.enum(["DONE", "IN_PROGRESS", "MISSING", "PENDING"]);

export const PitchRbacMatrixRowSchema = z.object({
  id: z.string().min(1).max(80),
  role: LongText,
  permissions: z.array(NonEmptyText).min(1).max(6),
  status: PitchStatusChipSchema
});

export const PitchSupplierOnboardingItemSchema = z.object({
  id: z.string().min(1).max(80),
  supplier: LongText,
  status: PitchStatusChipSchema
});

export const PitchSkuBaselineFieldSchema = z.object({
  id: z.string().min(1).max(80),
  label: LongText,
  value: NonEmptyText
});

export const PitchDocumentChecklistItemSchema = z.object({
  id: z.string().min(1).max(80),
  document: LongText,
  status: PitchStatusChipSchema
});

export const PitchShipmentPlaceholderSchema = z.object({
  id: z.string().min(1).max(80),
  label: LongText,
  value: NonEmptyText
});

export const PitchReceivingStateSchema = z.enum(["ARRIVED", "DOCS_HOLD", "RECEIVED", "QUARANTINE"]);

export const PitchValuationBlockItemSchema = z.object({
  id: z.string().min(1).max(80),
  text: LongText
});

export const PitchValuationBlockSchema = z.object({
  id: z.string().min(1).max(80),
  heading: LongText,
  items: z.array(PitchValuationBlockItemSchema).min(0).max(8),
  phase1: LongText.optional(),
  phase2: LongText.optional()
});

export const PitchComparisonHeaderSchema = z.tuple([
  z.literal(PITCH_TABLE_HEADERS[0]),
  z.literal(PITCH_TABLE_HEADERS[1]),
  z.literal(PITCH_TABLE_HEADERS[2]),
  z.literal(PITCH_TABLE_HEADERS[3])
]);

export const PitchComparisonRowSchema = z.tuple([
  NonEmptyText,
  NonEmptyText,
  NonEmptyText,
  NonEmptyText
]);

export const PitchComparisonSchema = z.object({
  headers: PitchComparisonHeaderSchema,
  rows: z.array(PitchComparisonRowSchema).length(2)
});

export const PitchDeckMetaSchema = z.object({
  deckId: z.literal(PITCH_DECK_ID),
  version: z.literal(PITCH_DECK_VERSION),
  locale: z.literal(PITCH_LOCALE),
  copyLockNotice: z.literal(PITCH_COPY_LOCK_NOTICE),
  profileHints: z.array(z.enum(PITCH_LAYER_PROFILE_HINTS)).length(3)
});

export const PitchScreenBaseSchema = z.object({
  slug: PitchScreenSlugSchema,
  route: PitchRouteSchema,
  order: z.number().int().min(1).max(6),
  title: LongText,
  tag: z.string().min(1).max(80)
});

export const PitchScreen01Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("01-double-engine"),
  route: z.literal(PITCH_ROUTES["01-double-engine"]),
  order: z.literal(1),
  title: z.literal("HITECH — ARQUITECTURA DE DOBLE MOTOR"),
  leftColumn: PitchEngineColumnSchema,
  rightColumn: PitchEngineColumnSchema,
  implicitMessage: z.object({
    id: z.string().min(1).max(80),
    text: z.literal("No soy proveedor. Soy sistema.")
  })
});

export const PitchScreen02Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("02-industrial-flow"),
  route: z.literal(PITCH_ROUTES["02-industrial-flow"]),
  order: z.literal(2),
  title: z.literal("MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE"),
  kpis: z.array(PitchKpiSchema).length(5),
  cycleLabel: z.object({
    id: z.string().min(1).max(80),
    text: z.literal("Ciclo continuo 35 meses para cubrir total → reinicio automático.")
  }),
  microcopy: z.object({
    id: z.string().min(1).max(80),
    text: z.literal("Mercado interno ya existente, no especulativo.")
  })
});

export const PitchScreen03Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("03-hitech-os"),
  route: z.literal(PITCH_ROUTES["03-hitech-os"]),
  order: z.literal(3),
  title: z.literal("MOTOR 2 — HITECH OS (Infraestructura Digital)"),
  features: z.array(PitchFeatureSchema).length(7),
  strongLine: z.object({
    id: z.string().min(1).max(80),
    text: z.literal(
      "Infraestructura digital propietaria diseñada para control de activos críticos."
    )
  })
});

export const PitchScreen04Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("04-valuation"),
  route: z.literal(PITCH_ROUTES["04-valuation"]),
  order: z.literal(4),
  title: z.literal("ESTRUCTURA FINANCIERA + VALUACIÓN"),
  blocks: z.array(PitchValuationBlockSchema).length(3),
  combinedValuationLine: z.object({
    id: z.string().min(1).max(80),
    text: z.literal("SAFE/Convertible con cap 4–6M anclado a escenario post-cierre 12/mes")
  }),
  comparison: PitchComparisonSchema.refine((value) => {
    const [rowA, rowB] = value.rows;
    if (!rowA || !rowB) {
      return false;
    }
    return (
      rowA[0] === PITCH_COMPARISON_ROWS[0][0] &&
      rowA[1] === PITCH_COMPARISON_ROWS[0][1] &&
      rowA[2] === PITCH_COMPARISON_ROWS[0][2] &&
      rowA[3] === PITCH_COMPARISON_ROWS[0][3] &&
      rowB[0] === PITCH_COMPARISON_ROWS[1][0] &&
      rowB[1] === PITCH_COMPARISON_ROWS[1][1] &&
      rowB[2] === PITCH_COMPARISON_ROWS[1][2] &&
      rowB[3] === PITCH_COMPARISON_ROWS[1][3]
    );
  }, "Comparison rows must match canonical source")
});

export const PitchScreen05Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("05-inventory-foundation"),
  route: z.literal(PITCH_ROUTES["05-inventory-foundation"]),
  order: z.literal(5),
  title: z.literal("RUN 1 - INVENTORY FOUNDATION (RBAC + SUPPLIERS + SKU + DOCUMENT VAULT)"),
  foundationStatus: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    kpis: z.array(PitchKpiSchema).length(4),
    rbacMatrixSnapshot: z.object({
      id: z.string().min(1).max(80),
      heading: LongText,
      rows: z.array(PitchRbacMatrixRowSchema).length(3)
    }),
    supplierOnboardingStatus: z.object({
      id: z.string().min(1).max(80),
      heading: LongText,
      suppliers: z.array(PitchSupplierOnboardingItemSchema).length(3)
    })
  }),
  productsSkuBaseline: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    fields: z.array(PitchSkuBaselineFieldSchema).length(4)
  }),
  documentVaultBaseline: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    requiredDocs: z.array(PitchDocumentChecklistItemSchema).length(5)
  })
});

export const PitchScreen06Schema = PitchScreenBaseSchema.extend({
  slug: z.literal("06-shipments-receiving"),
  route: z.literal(PITCH_ROUTES["06-shipments-receiving"]),
  order: z.literal(6),
  title: z.literal("RUN 2 - IMPORT SHIPMENTS (CUSTOMS PACK + RECEIVING -> QUARANTINE)"),
  shipmentControlBoard: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    placeholders: z.array(PitchShipmentPlaceholderSchema).length(5),
    customsPackCompleteness: z.object({
      id: z.string().min(1).max(80),
      text: LongText,
      status: PitchStatusChipSchema
    })
  }),
  receivingFlow: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    states: z
      .array(
        z.object({
          id: z.string().min(1).max(80),
          code: PitchReceivingStateSchema,
          note: LongText,
          order: z.number().int().min(1).max(4)
        })
      )
      .length(4)
  }),
  mismatchHandling: z.object({
    id: z.string().min(1).max(80),
    heading: LongText,
    qtyLotMismatch: LongText,
    deviationPlaceholder: LongText
  }),
  nextGate: z.object({
    id: z.string().min(1).max(80),
    text: z.literal("Next gate: QA RELEASE (RUN3, not implemented)")
  })
});

export const PitchScreenSchema = z.discriminatedUnion("slug", [
  PitchScreen01Schema,
  PitchScreen02Schema,
  PitchScreen03Schema,
  PitchScreen04Schema,
  PitchScreen05Schema,
  PitchScreen06Schema
]);

export const PitchDeckSchema = z
  .object({
    meta: PitchDeckMetaSchema,
    navigation: PitchNavigationSchema,
    screens: z.tuple([
      PitchScreen01Schema,
      PitchScreen02Schema,
      PitchScreen03Schema,
      PitchScreen04Schema,
      PitchScreen05Schema,
      PitchScreen06Schema
    ])
  })
  .superRefine((deck, ctx) => {
    const slugs = deck.screens.map((screen) => screen.slug);
    const canonical = [...PITCH_SCREEN_ORDER];

    if (new Set(slugs).size !== deck.screens.length) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: PITCH_VALIDATION_MESSAGES.duplicatedSlug,
        path: ["screens"]
      });
    }

    for (let index = 0; index < canonical.length; index += 1) {
      const expectedSlug = canonical[index];
      const actualSlug = slugs[index];
      if (actualSlug !== expectedSlug) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: PITCH_VALIDATION_MESSAGES.invalidOrder,
          path: ["screens", index, "slug"]
        });
      }
    }

    for (const link of deck.navigation.links) {
      if (PITCH_ROUTES[link.slug] !== link.href) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: PITCH_VALIDATION_MESSAGES.routeMismatch,
          path: ["navigation", "links"]
        });
      }
    }
  });

export const PitchScreenMapSchema = z.object({
  "01-double-engine": PitchScreen01Schema,
  "02-industrial-flow": PitchScreen02Schema,
  "03-hitech-os": PitchScreen03Schema,
  "04-valuation": PitchScreen04Schema,
  "05-inventory-foundation": PitchScreen05Schema,
  "06-shipments-receiving": PitchScreen06Schema
});

export const PitchCopyDigestSchema = z.object({
  deckId: z.literal(PITCH_DECK_ID),
  screenCount: z.literal(6),
  bulletCount: z.number().int().min(20).max(60),
  headingCount: z.number().int().min(8).max(24),
  tableRowCount: z.literal(2),
  tableHeaderCount: z.literal(4)
});

export const PitchScreenRequestSchema = z.object({
  slug: PitchScreenSlugSchema
});

export const PitchScreenResponseSchema = z.object({
  screen: PitchScreenSchema
});

export const PitchDeckResponseSchema = z.object({
  deck: PitchDeckSchema,
  digest: PitchCopyDigestSchema
});

export type PitchScreen01 = z.infer<typeof PitchScreen01Schema>;
export type PitchScreen02 = z.infer<typeof PitchScreen02Schema>;
export type PitchScreen03 = z.infer<typeof PitchScreen03Schema>;
export type PitchScreen04 = z.infer<typeof PitchScreen04Schema>;
export type PitchScreen05 = z.infer<typeof PitchScreen05Schema>;
export type PitchScreen06 = z.infer<typeof PitchScreen06Schema>;
export type PitchScreen = z.infer<typeof PitchScreenSchema>;
export type PitchDeck = z.infer<typeof PitchDeckSchema>;
export type PitchScreenMap = z.infer<typeof PitchScreenMapSchema>;
export type PitchCopyDigest = z.infer<typeof PitchCopyDigestSchema>;
export type PitchScreenRequest = z.infer<typeof PitchScreenRequestSchema>;
export type PitchScreenResponse = z.infer<typeof PitchScreenResponseSchema>;
export type PitchDeckResponse = z.infer<typeof PitchDeckResponseSchema>;
export type PitchNavigation = z.infer<typeof PitchNavigationSchema>;
export type PitchNavigationLink = z.infer<typeof PitchNavigationLinkSchema>;
export type PitchBullet = z.infer<typeof PitchBulletSchema>;
export type PitchMicrocopy = z.infer<typeof PitchMicrocopySchema>;
export type PitchEngineColumn = z.infer<typeof PitchEngineColumnSchema>;
export type PitchKpi = z.infer<typeof PitchKpiSchema>;
export type PitchFeature = z.infer<typeof PitchFeatureSchema>;
export type PitchValuationBlock = z.infer<typeof PitchValuationBlockSchema>;
