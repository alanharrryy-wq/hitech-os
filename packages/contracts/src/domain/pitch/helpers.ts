import { parseOrThrow } from "../../parsing.js";
import {
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_SLUGS,
  type PitchScreenSlug
} from "./constants.js";
import {
  PITCH_DECK_FIXTURE,
  PITCH_DECK_RESPONSE_FIXTURE,
  PITCH_SCREEN_FIXTURES,
  PITCH_SCREEN_MAP_FIXTURE,
  PITCH_SCREENS_FIXTURE
} from "./fixtures.js";
import {
  PitchDeckResponseSchema,
  PitchDeckSchema,
  PitchScreenMapSchema,
  PitchScreenRequestSchema,
  PitchScreenSchema,
  type PitchDeck,
  type PitchDeckResponse,
  type PitchScreen,
  type PitchScreenRequest,
  type PitchScreenResponse
} from "./schemas.js";

export function listPitchScreenSlugs(): readonly PitchScreenSlug[] {
  return PITCH_SCREEN_ORDER;
}

export function listPitchScreens(): readonly PitchScreen[] {
  return PITCH_SCREENS_FIXTURE;
}

export function isPitchScreenSlug(value: string): value is PitchScreenSlug {
  return (PITCH_SCREEN_SLUGS as readonly string[]).includes(value);
}

export function getPitchScreenBySlug(slug: PitchScreenSlug): PitchScreen {
  return PITCH_SCREEN_FIXTURES[slug];
}

export function getPitchScreenByRoute(route: string): PitchScreen | null {
  if (route === PITCH_ROUTES["01-double-engine"]) {
    return PITCH_SCREEN_FIXTURES["01-double-engine"];
  }

  if (route === PITCH_ROUTES["02-industrial-flow"]) {
    return PITCH_SCREEN_FIXTURES["02-industrial-flow"];
  }

  if (route === PITCH_ROUTES["03-hitech-os"]) {
    return PITCH_SCREEN_FIXTURES["03-hitech-os"];
  }

  if (route === PITCH_ROUTES["04-valuation"]) {
    return PITCH_SCREEN_FIXTURES["04-valuation"];
  }

  return null;
}

export function getPitchDeck(): PitchDeck {
  return PITCH_DECK_FIXTURE;
}

export function getPitchDeckResponse(): PitchDeckResponse {
  return PITCH_DECK_RESPONSE_FIXTURE;
}

export function getPitchScreenResponse(input: PitchScreenRequest): PitchScreenResponse {
  const parsed = parseOrThrow(PitchScreenRequestSchema, input, {
    resource: "pitch.screen.request",
    operation: "parse"
  });

  return {
    screen: getPitchScreenBySlug(parsed.slug)
  };
}

export function validatePitchScreen(value: unknown): PitchScreen {
  return parseOrThrow(PitchScreenSchema, value, {
    resource: "pitch.screen",
    operation: "validate"
  });
}

export function validatePitchDeck(value: unknown): PitchDeck {
  return parseOrThrow(PitchDeckSchema, value, {
    resource: "pitch.deck",
    operation: "validate"
  });
}

export function validatePitchDeckResponse(value: unknown): PitchDeckResponse {
  return parseOrThrow(PitchDeckResponseSchema, value, {
    resource: "pitch.deck.response",
    operation: "validate"
  });
}

export function validatePitchScreenMap(value: unknown): typeof PITCH_SCREEN_MAP_FIXTURE {
  return parseOrThrow(PitchScreenMapSchema, value, {
    resource: "pitch.screen.map",
    operation: "validate"
  });
}

export function getPitchRouteForSlug(slug: PitchScreenSlug): string {
  return PITCH_ROUTES[slug];
}

export function serializePitchDeckToJson(deck: PitchDeck = PITCH_DECK_FIXTURE): string {
  return JSON.stringify(deck, null, 2);
}

export function deserializePitchDeckFromJson(payload: string): PitchDeck {
  const decoded = JSON.parse(payload) as unknown;
  return validatePitchDeck(decoded);
}

export function serializePitchDeckResponseToJson(
  response: PitchDeckResponse = PITCH_DECK_RESPONSE_FIXTURE
): string {
  return JSON.stringify(response, null, 2);
}

export function deserializePitchDeckResponseFromJson(payload: string): PitchDeckResponse {
  const decoded = JSON.parse(payload) as unknown;
  return validatePitchDeckResponse(decoded);
}

export function createPitchScreenMatrix(): ReadonlyArray<{
  slug: PitchScreenSlug;
  route: string;
  order: number;
  title: string;
}> {
  return PITCH_SCREEN_ORDER.map((slug, index) => {
    const screen = PITCH_SCREEN_FIXTURES[slug];
    return {
      slug,
      route: screen.route,
      order: index + 1,
      title: screen.title
    };
  });
}

export function assertPitchSlug(input: string): PitchScreenSlug {
  if (!isPitchScreenSlug(input)) {
    throw new Error(`Invalid pitch screen slug: ${input}`);
  }

  return input;
}

export function assertPitchRoute(input: string): PitchScreenSlug {
  const slug = PITCH_SCREEN_ORDER.find((candidate) => PITCH_ROUTES[candidate] === input);
  if (!slug) {
    throw new Error(`Invalid pitch route: ${input}`);
  }

  return slug;
}

export function buildPitchLinkModel() {
  return PITCH_DECK_FIXTURE.navigation.links.map((link) => ({
    ...link,
    isCanonical: link.href === PITCH_ROUTES[link.slug]
  }));
}

export function copyPitchScreen(slug: PitchScreenSlug): PitchScreen {
  const screen = getPitchScreenBySlug(slug);
  return JSON.parse(JSON.stringify(screen)) as PitchScreen;
}

export function copyPitchDeck(): PitchDeck {
  return JSON.parse(JSON.stringify(PITCH_DECK_FIXTURE)) as PitchDeck;
}

export function ensurePitchInvariants(deck: PitchDeck): PitchDeck {
  const parsed = validatePitchDeck(deck);
  const order = parsed.screens.map((screen) => screen.slug);

  for (let index = 0; index < PITCH_SCREEN_ORDER.length; index += 1) {
    if (order[index] !== PITCH_SCREEN_ORDER[index]) {
      throw new Error("Pitch screen order invariant violated.");
    }
  }

  return parsed;
}

export function getPitchScreenTextList(slug: PitchScreenSlug): readonly string[] {
  const screen = getPitchScreenBySlug(slug);

  if (screen.slug === "01-double-engine") {
    return [
      screen.title,
      screen.leftColumn.heading,
      ...screen.leftColumn.bullets.map((entry) => entry.text),
      ...screen.leftColumn.microcopy.map((entry) => entry.text),
      screen.rightColumn.heading,
      ...screen.rightColumn.bullets.map((entry) => entry.text),
      ...screen.rightColumn.microcopy.map((entry) => entry.text),
      screen.implicitMessage.text
    ];
  }

  if (screen.slug === "02-industrial-flow") {
    return [
      screen.title,
      ...screen.kpis.map((entry) => entry.label),
      screen.cycleLabel.text,
      screen.microcopy.text
    ];
  }

  if (screen.slug === "03-hitech-os") {
    return [screen.title, ...screen.features.map((entry) => entry.text), screen.strongLine.text];
  }

  return [
    screen.title,
    ...screen.blocks.flatMap((block) => [block.heading, ...block.items.map((entry) => entry.text)]),
    screen.blocks[2]?.phase1 ?? "",
    screen.blocks[2]?.phase2 ?? "",
    screen.combinedValuationLine.text,
    ...screen.comparison.headers,
    ...screen.comparison.rows.flatMap((row) => row)
  ];
}

export function containsPitchText(slug: PitchScreenSlug, needle: string): boolean {
  return getPitchScreenTextList(slug).some((line) => line === needle);
}

export function getPitchRouteIndex(): Readonly<Record<string, PitchScreen>> {
  return {
    [PITCH_ROUTES["01-double-engine"]]: PITCH_SCREEN_FIXTURES["01-double-engine"],
    [PITCH_ROUTES["02-industrial-flow"]]: PITCH_SCREEN_FIXTURES["02-industrial-flow"],
    [PITCH_ROUTES["03-hitech-os"]]: PITCH_SCREEN_FIXTURES["03-hitech-os"],
    [PITCH_ROUTES["04-valuation"]]: PITCH_SCREEN_FIXTURES["04-valuation"]
  };
}

export function getPitchScreenCount(): number {
  return PITCH_SCREENS_FIXTURE.length;
}

export function getPitchFixtureStats(): {
  screenCount: number;
  titleCount: number;
  routeCount: number;
  microcopyCount: number;
  bulletLikeCount: number;
} {
  const microcopyCount =
    SCREEN01_MICROCOPY_COUNT +
    1 +
    1; /* screen02 microcopy + screen03 strong line treated as microcopy-like */

  return {
    screenCount: PITCH_SCREENS_FIXTURE.length,
    titleCount: PITCH_SCREENS_FIXTURE.length,
    routeCount: PITCH_SCREENS_FIXTURE.length,
    microcopyCount,
    bulletLikeCount: estimatePitchBulletLikeCount()
  };
}

const SCREEN01_MICROCOPY_COUNT =
  PITCH_SCREEN_FIXTURES["01-double-engine"].leftColumn.microcopy.length +
  PITCH_SCREEN_FIXTURES["01-double-engine"].rightColumn.microcopy.length;

function estimatePitchBulletLikeCount(): number {
  return (
    PITCH_SCREEN_FIXTURES["01-double-engine"].leftColumn.bullets.length +
    PITCH_SCREEN_FIXTURES["01-double-engine"].rightColumn.bullets.length +
    PITCH_SCREEN_FIXTURES["02-industrial-flow"].kpis.length +
    PITCH_SCREEN_FIXTURES["03-hitech-os"].features.length +
    PITCH_SCREEN_FIXTURES["04-valuation"].blocks.reduce((sum, block) => sum + block.items.length, 0)
  );
}

export const PITCH_DECK_JSON_FIXTURE = serializePitchDeckToJson();
export const PITCH_DECK_RESPONSE_JSON_FIXTURE = serializePitchDeckResponseToJson();
