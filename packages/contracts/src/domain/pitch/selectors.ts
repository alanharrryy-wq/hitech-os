import { PITCH_SCREEN_ORDER, type PitchScreenSlug } from "./constants.js";
import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "./fixtures.js";
import type { PitchDeckSummary, PitchScreenSummary, PitchTextFragment } from "./types.js";

export function collectPitchTextFragments(slug: PitchScreenSlug): readonly PitchTextFragment[] {
  const screen = PITCH_SCREEN_FIXTURES[slug];

  if (screen.slug === "01-double-engine") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      {
        id: `${slug}:left-heading`,
        text: screen.leftColumn.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.leftColumn.bullets.map((bullet) => ({
        id: bullet.id,
        text: bullet.text,
        scope: "bullet" as const,
        screenSlug: slug
      })),
      ...screen.leftColumn.microcopy.map((entry) => ({
        id: entry.id,
        text: entry.text,
        scope: "microcopy" as const,
        screenSlug: slug
      })),
      {
        id: `${slug}:right-heading`,
        text: screen.rightColumn.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.rightColumn.bullets.map((bullet) => ({
        id: bullet.id,
        text: bullet.text,
        scope: "bullet" as const,
        screenSlug: slug
      })),
      ...screen.rightColumn.microcopy.map((entry) => ({
        id: entry.id,
        text: entry.text,
        scope: "microcopy" as const,
        screenSlug: slug
      })),
      {
        id: screen.implicitMessage.id,
        text: screen.implicitMessage.text,
        scope: "strong-line",
        screenSlug: slug
      }
    ];
  }

  if (screen.slug === "02-industrial-flow") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      ...screen.kpis.map((kpi) => ({
        id: kpi.id,
        text: `${kpi.label} ${kpi.value}`,
        scope: "kpi" as const,
        screenSlug: slug
      })),
      {
        id: screen.cycleLabel.id,
        text: screen.cycleLabel.text,
        scope: "microcopy",
        screenSlug: slug
      },
      {
        id: screen.microcopy.id,
        text: screen.microcopy.text,
        scope: "microcopy",
        screenSlug: slug
      }
    ];
  }

  if (screen.slug === "03-hitech-os") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      ...screen.features.map((feature) => ({
        id: feature.id,
        text: feature.text,
        scope: "bullet" as const,
        screenSlug: slug
      })),
      {
        id: screen.strongLine.id,
        text: screen.strongLine.text,
        scope: "strong-line",
        screenSlug: slug
      }
    ];
  }

  if (screen.slug === "04-valuation") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      ...screen.blocks.flatMap((block) => {
        const blockFragments: PitchTextFragment[] = [
          {
            id: `${block.id}:heading`,
            text: block.heading,
            scope: "heading",
            screenSlug: slug
          },
          ...block.items.map((item) => ({
            id: item.id,
            text: item.text,
            scope: "bullet" as const,
            screenSlug: slug
          }))
        ];

        if (block.phase1) {
          blockFragments.push({
            id: `${block.id}:phase1`,
            text: block.phase1,
            scope: "phase",
            screenSlug: slug
          });
        }

        if (block.phase2) {
          blockFragments.push({
            id: `${block.id}:phase2`,
            text: block.phase2,
            scope: "phase",
            screenSlug: slug
          });
        }

        return blockFragments;
      }),
      {
        id: screen.combinedValuationLine.id,
        text: screen.combinedValuationLine.text,
        scope: "strong-line",
        screenSlug: slug
      },
      ...screen.comparison.headers.map((header, index) => ({
        id: `${slug}:header:${index}`,
        text: header,
        scope: "table-header" as const,
        screenSlug: slug
      })),
      ...screen.comparison.rows.flatMap((row, rowIndex) =>
        row.map((cell, cellIndex) => ({
          id: `${slug}:cell:${rowIndex}:${cellIndex}`,
          text: cell,
          scope: "table-cell" as const,
          screenSlug: slug
        }))
      )
    ];
  }

  if (screen.slug === "05-inventory-foundation") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      {
        id: screen.foundationStatus.id,
        text: screen.foundationStatus.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.foundationStatus.kpis.map((kpi) => ({
        id: kpi.id,
        text: `${kpi.label} ${kpi.value}`,
        scope: "kpi" as const,
        screenSlug: slug
      })),
      {
        id: screen.foundationStatus.rbacMatrixSnapshot.id,
        text: screen.foundationStatus.rbacMatrixSnapshot.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.foundationStatus.rbacMatrixSnapshot.rows.flatMap((row) => [
        {
          id: row.id,
          text: row.role,
          scope: "bullet" as const,
          screenSlug: slug
        },
        ...row.permissions.map((permission, index) => ({
          id: `${row.id}:permission:${index}`,
          text: permission,
          scope: "bullet" as const,
          screenSlug: slug
        })),
        {
          id: `${row.id}:status`,
          text: row.status,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ]),
      {
        id: screen.foundationStatus.supplierOnboardingStatus.id,
        text: screen.foundationStatus.supplierOnboardingStatus.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.foundationStatus.supplierOnboardingStatus.suppliers.flatMap((supplier) => [
        {
          id: supplier.id,
          text: supplier.supplier,
          scope: "bullet" as const,
          screenSlug: slug
        },
        {
          id: `${supplier.id}:status`,
          text: supplier.status,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ]),
      {
        id: screen.productsSkuBaseline.id,
        text: screen.productsSkuBaseline.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.productsSkuBaseline.fields.flatMap((field) => [
        {
          id: `${field.id}:label`,
          text: field.label,
          scope: "bullet" as const,
          screenSlug: slug
        },
        {
          id: `${field.id}:value`,
          text: field.value,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ]),
      {
        id: screen.documentVaultBaseline.id,
        text: screen.documentVaultBaseline.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.documentVaultBaseline.requiredDocs.flatMap((doc) => [
        {
          id: doc.id,
          text: doc.document,
          scope: "bullet" as const,
          screenSlug: slug
        },
        {
          id: `${doc.id}:status`,
          text: doc.status,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ])
    ];
  }

  if (screen.slug === "06-shipments-receiving") {
    return [
      {
        id: `${slug}:title`,
        text: screen.title,
        scope: "title",
        screenSlug: slug
      },
      {
        id: screen.shipmentControlBoard.id,
        text: screen.shipmentControlBoard.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.shipmentControlBoard.placeholders.flatMap((placeholder) => [
        {
          id: `${placeholder.id}:label`,
          text: placeholder.label,
          scope: "bullet" as const,
          screenSlug: slug
        },
        {
          id: `${placeholder.id}:value`,
          text: placeholder.value,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ]),
      {
        id: screen.shipmentControlBoard.customsPackCompleteness.id,
        text: screen.shipmentControlBoard.customsPackCompleteness.text,
        scope: "microcopy",
        screenSlug: slug
      },
      {
        id: `${screen.shipmentControlBoard.customsPackCompleteness.id}:status`,
        text: screen.shipmentControlBoard.customsPackCompleteness.status,
        scope: "microcopy",
        screenSlug: slug
      },
      {
        id: screen.receivingFlow.id,
        text: screen.receivingFlow.heading,
        scope: "heading",
        screenSlug: slug
      },
      ...screen.receivingFlow.states.flatMap((state) => [
        {
          id: `${state.id}:code`,
          text: state.code,
          scope: "bullet" as const,
          screenSlug: slug
        },
        {
          id: `${state.id}:note`,
          text: state.note,
          scope: "microcopy" as const,
          screenSlug: slug
        }
      ]),
      {
        id: screen.mismatchHandling.id,
        text: screen.mismatchHandling.heading,
        scope: "heading",
        screenSlug: slug
      },
      {
        id: `${screen.mismatchHandling.id}:qty-lot`,
        text: screen.mismatchHandling.qtyLotMismatch,
        scope: "bullet",
        screenSlug: slug
      },
      {
        id: `${screen.mismatchHandling.id}:deviation`,
        text: screen.mismatchHandling.deviationPlaceholder,
        scope: "microcopy",
        screenSlug: slug
      },
      {
        id: screen.nextGate.id,
        text: screen.nextGate.text,
        scope: "microcopy",
        screenSlug: slug
      }
    ];
  }

  const unreachable: never = screen;
  throw new Error(`Unhandled pitch screen slug: ${(unreachable as { slug: string }).slug}`);
}

export function collectAllPitchTextFragments(): readonly PitchTextFragment[] {
  return PITCH_SCREEN_ORDER.flatMap((slug) => collectPitchTextFragments(slug));
}

export function summarizePitchScreen(slug: PitchScreenSlug): PitchScreenSummary {
  const screen = PITCH_SCREEN_FIXTURES[slug];
  return {
    slug,
    route: screen.route,
    order: screen.order,
    title: screen.title,
    fragmentCount: collectPitchTextFragments(slug).length
  };
}

export function summarizePitchDeck(): PitchDeckSummary {
  const screens = PITCH_SCREEN_ORDER.map((slug) => summarizePitchScreen(slug));
  const allFragments = collectAllPitchTextFragments();
  const bulletLikeCount = allFragments.filter(
    (fragment) =>
      fragment.scope === "bullet" ||
      fragment.scope === "kpi" ||
      fragment.scope === "phase" ||
      fragment.scope === "table-cell"
  ).length;

  return {
    deckId: PITCH_DECK_FIXTURE.meta.deckId,
    version: PITCH_DECK_FIXTURE.meta.version,
    locale: PITCH_DECK_FIXTURE.meta.locale,
    screenCount: screens.length,
    bulletLikeCount,
    totalTextFragments: allFragments.length
  };
}

export function findPitchTextExact(value: string): readonly PitchTextFragment[] {
  return collectAllPitchTextFragments().filter((fragment) => fragment.text === value);
}

export function assertPitchTextExists(value: string): void {
  const matches = findPitchTextExact(value);
  if (matches.length === 0) {
    throw new Error(`Pitch text not found: ${value}`);
  }
}

export function createPitchSlugToTitleMap(): Readonly<Record<PitchScreenSlug, string>> {
  return {
    "01-double-engine": PITCH_SCREEN_FIXTURES["01-double-engine"].title,
    "02-industrial-flow": PITCH_SCREEN_FIXTURES["02-industrial-flow"].title,
    "03-hitech-os": PITCH_SCREEN_FIXTURES["03-hitech-os"].title,
    "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"].title,
    "05-inventory-foundation": PITCH_SCREEN_FIXTURES["05-inventory-foundation"].title,
    "06-shipments-receiving": PITCH_SCREEN_FIXTURES["06-shipments-receiving"].title
  };
}

export function createPitchSlugToRouteMap(): Readonly<Record<PitchScreenSlug, string>> {
  return {
    "01-double-engine": PITCH_SCREEN_FIXTURES["01-double-engine"].route,
    "02-industrial-flow": PITCH_SCREEN_FIXTURES["02-industrial-flow"].route,
    "03-hitech-os": PITCH_SCREEN_FIXTURES["03-hitech-os"].route,
    "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"].route,
    "05-inventory-foundation": PITCH_SCREEN_FIXTURES["05-inventory-foundation"].route,
    "06-shipments-receiving": PITCH_SCREEN_FIXTURES["06-shipments-receiving"].route
  };
}

export function getPitchDistinctHeadings(): readonly string[] {
  const headings = new Set<string>();

  for (const slug of PITCH_SCREEN_ORDER) {
    const screen = PITCH_SCREEN_FIXTURES[slug];
    headings.add(screen.title);

    if (screen.slug === "01-double-engine") {
      headings.add(screen.leftColumn.heading);
      headings.add(screen.rightColumn.heading);
    }

    if (screen.slug === "04-valuation") {
      for (const block of screen.blocks) {
        headings.add(block.heading);
      }
    }

    if (screen.slug === "05-inventory-foundation") {
      headings.add(screen.foundationStatus.heading);
      headings.add(screen.foundationStatus.rbacMatrixSnapshot.heading);
      headings.add(screen.foundationStatus.supplierOnboardingStatus.heading);
      headings.add(screen.productsSkuBaseline.heading);
      headings.add(screen.documentVaultBaseline.heading);
    }

    if (screen.slug === "06-shipments-receiving") {
      headings.add(screen.shipmentControlBoard.heading);
      headings.add(screen.receivingFlow.heading);
      headings.add(screen.mismatchHandling.heading);
    }
  }

  return [...headings];
}

export function getPitchDistinctBulletLines(): readonly string[] {
  const lines = new Set<string>();

  for (const slug of PITCH_SCREEN_ORDER) {
    const screen = PITCH_SCREEN_FIXTURES[slug];
    if (screen.slug === "01-double-engine") {
      for (const bullet of screen.leftColumn.bullets) {
        lines.add(bullet.text);
      }
      for (const bullet of screen.rightColumn.bullets) {
        lines.add(bullet.text);
      }
    }

    if (screen.slug === "02-industrial-flow") {
      for (const kpi of screen.kpis) {
        lines.add(kpi.label);
      }
    }

    if (screen.slug === "03-hitech-os") {
      for (const feature of screen.features) {
        lines.add(feature.text);
      }
    }

    if (screen.slug === "04-valuation") {
      for (const block of screen.blocks) {
        for (const item of block.items) {
          lines.add(item.text);
        }
        if (block.phase1) {
          lines.add(block.phase1);
        }
        if (block.phase2) {
          lines.add(block.phase2);
        }
      }

      for (const row of screen.comparison.rows) {
        for (const cell of row) {
          lines.add(cell);
        }
      }
    }

    if (screen.slug === "05-inventory-foundation") {
      for (const kpi of screen.foundationStatus.kpis) {
        lines.add(kpi.label);
      }

      for (const row of screen.foundationStatus.rbacMatrixSnapshot.rows) {
        lines.add(row.role);
        for (const permission of row.permissions) {
          lines.add(permission);
        }
      }

      for (const supplier of screen.foundationStatus.supplierOnboardingStatus.suppliers) {
        lines.add(supplier.supplier);
      }

      for (const field of screen.productsSkuBaseline.fields) {
        lines.add(field.label);
      }

      for (const doc of screen.documentVaultBaseline.requiredDocs) {
        lines.add(doc.document);
      }
    }

    if (screen.slug === "06-shipments-receiving") {
      for (const placeholder of screen.shipmentControlBoard.placeholders) {
        lines.add(placeholder.label);
      }

      for (const state of screen.receivingFlow.states) {
        lines.add(state.code);
      }

      lines.add(screen.mismatchHandling.qtyLotMismatch);
    }
  }

  return [...lines];
}

export function getPitchDistinctMicrocopyLines(): readonly string[] {
  const lines = new Set<string>();

  for (const slug of PITCH_SCREEN_ORDER) {
    const screen = PITCH_SCREEN_FIXTURES[slug];

    if (screen.slug === "01-double-engine") {
      for (const line of screen.leftColumn.microcopy) {
        lines.add(line.text);
      }
      for (const line of screen.rightColumn.microcopy) {
        lines.add(line.text);
      }
      lines.add(screen.implicitMessage.text);
    }

    if (screen.slug === "02-industrial-flow") {
      lines.add(screen.cycleLabel.text);
      lines.add(screen.microcopy.text);
    }

    if (screen.slug === "03-hitech-os") {
      lines.add(screen.strongLine.text);
    }

    if (screen.slug === "04-valuation") {
      lines.add(screen.combinedValuationLine.text);
    }

    if (screen.slug === "05-inventory-foundation") {
      for (const kpi of screen.foundationStatus.kpis) {
        lines.add(kpi.value);
      }

      for (const row of screen.foundationStatus.rbacMatrixSnapshot.rows) {
        lines.add(row.status);
      }

      for (const supplier of screen.foundationStatus.supplierOnboardingStatus.suppliers) {
        lines.add(supplier.status);
      }

      for (const field of screen.productsSkuBaseline.fields) {
        lines.add(field.value);
      }

      for (const doc of screen.documentVaultBaseline.requiredDocs) {
        lines.add(doc.status);
      }
    }

    if (screen.slug === "06-shipments-receiving") {
      for (const placeholder of screen.shipmentControlBoard.placeholders) {
        lines.add(placeholder.value);
      }

      lines.add(screen.shipmentControlBoard.customsPackCompleteness.text);
      lines.add(screen.shipmentControlBoard.customsPackCompleteness.status);

      for (const state of screen.receivingFlow.states) {
        lines.add(state.note);
      }

      lines.add(screen.mismatchHandling.deviationPlaceholder);
      lines.add(screen.nextGate.text);
    }
  }

  return [...lines];
}

export function getPitchHeadersForValuationTable(): readonly string[] {
  const valuation = PITCH_SCREEN_FIXTURES["04-valuation"];
  return [...valuation.comparison.headers];
}

export function getPitchRowsForValuationTable(): readonly (readonly string[])[] {
  const valuation = PITCH_SCREEN_FIXTURES["04-valuation"];
  return valuation.comparison.rows.map((row) => [...row]);
}
