import { describe, expect, it } from "vitest";
import {
  buildPitchLinkModel,
  collectAllPitchTextFragments,
  copyPitchDeck,
  createPitchSlugToRouteMap,
  createPitchSlugToTitleMap,
  deserializePitchDeckFromJson,
  getPitchDeck,
  getPitchDeckResponse,
  getPitchRouteForSlug,
  getPitchScreenByRoute,
  listPitchScreenSlugs,
  PITCH_COPY_LOCK_NOTICE,
  PITCH_ROUTES,
  PITCH_ROUTE_BASE,
  PITCH_SCREEN_NUMBERS,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES,
  serializePitchDeckToJson,
  validatePitchDeck
} from "../dist/index.js";

function parseSlugOrdinal(slug: string): number {
  const [prefix] = slug.split("-", 1);
  return Number(prefix);
}

describe("pitch copy-lock + canonical guardrails", () => {
  it("keeps copy-lock notice exact across deck helpers", () => {
    const deck = getPitchDeck();
    const response = getPitchDeckResponse();

    expect(PITCH_COPY_LOCK_NOTICE).toBe(
      "Canonical copy is contract-locked. Do not mutate strings outside contract fixtures."
    );
    expect(deck.meta.copyLockNotice).toBe(PITCH_COPY_LOCK_NOTICE);
    expect(response.deck.meta.copyLockNotice).toBe(PITCH_COPY_LOCK_NOTICE);

    const serialized = serializePitchDeckToJson();
    const roundTripped = deserializePitchDeckFromJson(serialized);
    expect(roundTripped.meta.copyLockNotice).toBe(PITCH_COPY_LOCK_NOTICE);
  });

  it("keeps slug order and numeric ordinals contiguous and deterministic", () => {
    const slugs = listPitchScreenSlugs();
    expect(slugs).toEqual(PITCH_SCREEN_ORDER);

    const ordinals = slugs.map(parseSlugOrdinal);
    expect(ordinals).toEqual([1, 2, 3, 4]);

    for (const slug of slugs) {
      expect(PITCH_SCREEN_NUMBERS[slug]).toBe(parseSlugOrdinal(slug));
      expect(PITCH_ROUTES[slug]).toBe(`${PITCH_ROUTE_BASE}/${slug}`);
    }
  });

  it("keeps canonical route and title maps in sync with navigation model", () => {
    const routeMap = createPitchSlugToRouteMap();
    const titleMap = createPitchSlugToTitleMap();
    const links = buildPitchLinkModel();

    expect(links).toHaveLength(PITCH_SCREEN_ORDER.length);

    for (const [index, link] of links.entries()) {
      const slug = PITCH_SCREEN_ORDER[index];
      expect(link.slug).toBe(slug);
      expect(link.isCanonical).toBe(true);
      expect(link.href).toBe(routeMap[slug]);
      expect(link.href).toBe(PITCH_ROUTES[slug]);
      expect(link.title).toBe(titleMap[slug]);
      expect(link.title).toBe(PITCH_SCREEN_TITLES[slug]);
      expect(getPitchRouteForSlug(slug)).toBe(PITCH_ROUTES[slug]);
      expect(getPitchScreenByRoute(link.href)?.slug).toBe(slug);
    }
  });

  it("rejects copy-lock notice mutations through schema validation", () => {
    const mutated = copyPitchDeck();
    mutated.meta.copyLockNotice =
      "Canonical copy is contract locked. Do not mutate strings outside fixtures.";

    expect(() => validatePitchDeck(mutated)).toThrow();
  });

  it("contains required immutable copy fragments and excludes common drift variants", () => {
    const fragments = collectAllPitchTextFragments().map((entry) => entry.text);
    const index = new Set(fragments);

    expect(index.has("No soy proveedor. Soy sistema.")).toBe(true);
    expect(index.has("Mercado interno ya existente, no especulativo.")).toBe(true);
    expect(
      index.has("Infraestructura digital propietaria diseñada para control de activos críticos.")
    ).toBe(true);
    expect(index.has("Valuación combinada estimada: 4–6M")).toBe(true);

    expect(index.has("No soy proveedor, soy sistema.")).toBe(false);
    expect(index.has("Mercado interno existente, no especulativo.")).toBe(false);
    expect(index.has("Valuación combinada estimada: 4-6M")).toBe(false);
  });
});
