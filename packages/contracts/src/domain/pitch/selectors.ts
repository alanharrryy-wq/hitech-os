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
    "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"].title
  };
}

export function createPitchSlugToRouteMap(): Readonly<Record<PitchScreenSlug, string>> {
  return {
    "01-double-engine": PITCH_SCREEN_FIXTURES["01-double-engine"].route,
    "02-industrial-flow": PITCH_SCREEN_FIXTURES["02-industrial-flow"].route,
    "03-hitech-os": PITCH_SCREEN_FIXTURES["03-hitech-os"].route,
    "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"].route
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
