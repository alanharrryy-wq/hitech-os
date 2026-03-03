import { describe, expect, it } from "vitest";
import {
  PITCH_DECK_FIXTURE,
  PITCH_DECK_FIXTURE_LOCK,
  PITCH_DECK_RESPONSE_FIXTURE,
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES,
  PitchDeckResponseSchema,
  PitchDeckSchema,
  PitchScreenResponseSchema,
  PitchScreenSchema,
  assertPitchRoute,
  assertPitchSlug,
  buildPitchLinkModel,
  collectAllPitchTextFragments,
  containsPitchText,
  copyPitchDeck,
  copyPitchScreen,
  createPitchScreenMatrix,
  createPitchSlugToRouteMap,
  createPitchSlugToTitleMap,
  deserializePitchDeckFromJson,
  deserializePitchDeckResponseFromJson,
  ensurePitchInvariants,
  getPitchDeck,
  getPitchDeckResponse,
  getPitchDistinctBulletLines,
  getPitchDistinctHeadings,
  getPitchDistinctMicrocopyLines,
  getPitchFixtureStats,
  getPitchHeadersForValuationTable,
  getPitchRouteForSlug,
  getPitchRowsForValuationTable,
  getPitchScreenByRoute,
  getPitchScreenBySlug,
  getPitchScreenCount,
  getPitchScreenResponse,
  getPitchScreenTextList,
  isPitchScreenSlug,
  listPitchScreenSlugs,
  listPitchScreens,
  serializePitchDeckResponseToJson,
  serializePitchDeckToJson,
  summarizePitchDeck,
  summarizePitchScreen,
  validatePitchDeck,
  validatePitchDeckResponse,
  validatePitchScreen,
  validatePitchScreenMap
} from "../dist/index.js";

describe("pitch contracts valid fixtures", () => {
  it("validates pitch deck fixture", () => {
    const parsed = PitchDeckSchema.parse(PITCH_DECK_FIXTURE);
    expect(parsed.meta.deckId).toBe("hitech-pitch-terraform-v1");
    expect(parsed.screens.length).toBe(6);
    expect(parsed.navigation.links.length).toBe(6);
  });

  it("validates pitch deck response fixture", () => {
    const parsed = PitchDeckResponseSchema.parse(PITCH_DECK_RESPONSE_FIXTURE);
    expect(parsed.digest.screenCount).toBe(6);
    expect(parsed.digest.tableHeaderCount).toBe(4);
    expect(parsed.digest.tableRowCount).toBe(2);
  });

  it("validates each screen by slug", () => {
    for (const slug of PITCH_SCREEN_ORDER) {
      const screen = getPitchScreenBySlug(slug);
      const parsed = PitchScreenSchema.parse(screen);
      expect(parsed.slug).toBe(slug);
      expect(parsed.route).toBe(PITCH_ROUTES[slug]);
    }
  });

  it("validates helper outputs remain deterministic", () => {
    expect(listPitchScreenSlugs()).toEqual(PITCH_SCREEN_ORDER);
    expect(listPitchScreens().length).toBe(6);
    expect(getPitchScreenCount()).toBe(6);

    const matrix = createPitchScreenMatrix();
    expect(matrix).toHaveLength(6);
    expect(matrix[0]?.slug).toBe("01-double-engine");
    expect(matrix[1]?.slug).toBe("02-industrial-flow");
    expect(matrix[2]?.slug).toBe("03-hitech-os");
    expect(matrix[3]?.slug).toBe("04-valuation");
    expect(matrix[4]?.slug).toBe("05-inventory-foundation");
    expect(matrix[5]?.slug).toBe("06-shipments-receiving");
  });

  it("supports route and slug assertion helpers", () => {
    expect(assertPitchSlug("01-double-engine")).toBe("01-double-engine");
    expect(assertPitchRoute("/pitch/03-hitech-os")).toBe("03-hitech-os");
    expect(assertPitchRoute("/pitch/05-inventory-foundation")).toBe("05-inventory-foundation");
    expect(assertPitchRoute("/pitch/06-shipments-receiving")).toBe("06-shipments-receiving");

    expect(() => assertPitchSlug("invalid")).toThrow();
    expect(() => assertPitchRoute("/pitch/invalid")).toThrow();
  });

  it("produces canonical link model and maps", () => {
    const links = buildPitchLinkModel();
    expect(links).toHaveLength(6);
    for (const link of links) {
      expect(link.isCanonical).toBe(true);
      expect(link.href).toBe(PITCH_ROUTES[link.slug]);
    }

    const slugToTitle = createPitchSlugToTitleMap();
    const slugToRoute = createPitchSlugToRouteMap();

    expect(slugToTitle["01-double-engine"]).toBe(PITCH_SCREEN_TITLES["01-double-engine"]);
    expect(slugToTitle["04-valuation"]).toBe(PITCH_SCREEN_TITLES["04-valuation"]);
    expect(slugToRoute["01-double-engine"]).toBe("/pitch/01-double-engine");
    expect(slugToRoute["04-valuation"]).toBe("/pitch/04-valuation");
    expect(Object.values(slugToRoute)).toContain("/pitch/05-inventory-foundation");
    expect(Object.values(slugToRoute)).toContain("/pitch/06-shipments-receiving");
  });

  it("serializes and deserializes deck without drift", () => {
    const payload = serializePitchDeckToJson();
    const decoded = deserializePitchDeckFromJson(payload);

    expect(decoded.meta.deckId).toBe(PITCH_DECK_FIXTURE.meta.deckId);
    expect(decoded.screens[0].slug).toBe("01-double-engine");
    expect(decoded.screens[3].slug).toBe("04-valuation");

    const responsePayload = serializePitchDeckResponseToJson();
    const responseDecoded = deserializePitchDeckResponseFromJson(responsePayload);

    expect(responseDecoded.digest.screenCount).toBe(6);
    expect(responseDecoded.deck.screens[2].slug).toBe("03-hitech-os");
    expect(responseDecoded.deck.screens[4]?.slug).toBe("05-inventory-foundation");
    expect(responseDecoded.deck.screens[5]?.slug).toBe("06-shipments-receiving");
  });

  it("provides typed screen response helper", () => {
    const response = getPitchScreenResponse({ slug: "02-industrial-flow" });
    const parsed = PitchScreenResponseSchema.parse(response);

    expect(parsed.screen.slug).toBe("02-industrial-flow");
    expect(parsed.screen.title).toBe("MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE");
  });

  it("keeps lock constants aligned with fixture", () => {
    expect(PITCH_DECK_FIXTURE_LOCK.screenOrder).toEqual(PITCH_SCREEN_ORDER);
    expect(PITCH_DECK_FIXTURE_LOCK.routes["03-hitech-os"]).toBe(PITCH_ROUTES["03-hitech-os"]);
    expect(PITCH_DECK_FIXTURE_LOCK.titles["04-valuation"]).toBe(
      PITCH_SCREEN_TITLES["04-valuation"]
    );
  });

  it("exposes text index and coverage helpers", () => {
    const headings = getPitchDistinctHeadings();
    const bullets = getPitchDistinctBulletLines();
    const microcopy = getPitchDistinctMicrocopyLines();
    const fragments = collectAllPitchTextFragments();

    expect(headings).toContain("MOTOR 2 — HITECH OS");
    expect(bullets).toContain("Escalable a multiindustria");
    expect(microcopy).toContain("No soy proveedor. Soy sistema.");
    expect(fragments.length).toBeGreaterThan(40);
  });

  it("returns table headers and rows for valuation", () => {
    const headers = getPitchHeadersForValuationTable();
    const rows = getPitchRowsForValuationTable();

    expect(headers).toEqual(["Modelo", "Múltiplo", "Riesgo", "Escalabilidad"]);
    expect(rows).toHaveLength(2);
    expect(rows[0]?.[0]).toBe("Industrial tradicional");
    expect(rows[1]?.[0]).toBe("Industrial + Software");
  });

  it("provides fixture stats and screen summaries", () => {
    const stats = getPitchFixtureStats();
    const screenSummary = summarizePitchScreen("01-double-engine");
    const deckSummary = summarizePitchDeck();

    expect(stats.screenCount).toBe(6);
    expect(stats.bulletLikeCount).toBeGreaterThan(20);
    expect(screenSummary.route).toBe("/pitch/01-double-engine");
    expect(screenSummary.fragmentCount).toBeGreaterThan(10);
    expect(deckSummary.screenCount).toBe(6);
    expect(deckSummary.totalTextFragments).toBeGreaterThan(40);
  });

  it("contains required canonical lines", () => {
    expect(containsPitchText("01-double-engine", "19 módulos facturados")).toBe(true);
    expect(
      containsPitchText("02-industrial-flow", "Mercado interno ya existente, no especulativo.")
    ).toBe(true);
    expect(
      containsPitchText(
        "03-hitech-os",
        "Infraestructura digital propietaria diseñada para control de activos críticos."
      )
    ).toBe(true);
    expect(
      containsPitchText(
        "04-valuation",
        "SAFE/Convertible con cap 4–6M anclado a escenario post-cierre 12/mes"
      )
    ).toBe(true);
    expect(containsPitchText("05-inventory-foundation", "RBAC matrix snapshot")).toBe(true);
    expect(
      containsPitchText("06-shipments-receiving", "Next gate: QA RELEASE (RUN3, not implemented)")
    ).toBe(true);
  });
});

describe("pitch contracts invalid fixtures", () => {
  it("fails when deck screen order drifts", () => {
    const copy = copyPitchDeck();
    const first = copy.screens[0];
    const second = copy.screens[1];

    copy.screens[0] = second;
    copy.screens[1] = first;

    expect(() => validatePitchDeck(copy)).toThrow();
  });

  it("fails when route does not match slug", () => {
    const copy = copyPitchDeck();
    copy.navigation.links[0] = {
      ...copy.navigation.links[0],
      href: "/pitch/04-valuation"
    };

    expect(() => validatePitchDeck(copy)).toThrow();
  });

  it("fails when canonical copy line is mutated", () => {
    const screen = copyPitchScreen("01-double-engine");
    screen.implicitMessage.text = "No soy proveedor, soy plataforma";

    expect(() => validatePitchScreen(screen)).toThrow();
  });

  it("fails when valuation headers change", () => {
    const screen = copyPitchScreen("04-valuation");
    screen.comparison.headers[0] = "Tipo";

    expect(() => validatePitchScreen(screen)).toThrow();
  });

  it("fails when valuation rows change", () => {
    const screen = copyPitchScreen("04-valuation");
    screen.comparison.rows[1][3] = "Media";

    expect(() => validatePitchScreen(screen)).toThrow();
  });

  it("fails when response digest shape breaks", () => {
    const response = getPitchDeckResponse();
    const invalid = {
      ...response,
      digest: {
        ...response.digest,
        screenCount: 5
      }
    };

    expect(() => validatePitchDeckResponse(invalid)).toThrow();
  });

  it("fails when screen map has invalid payload", () => {
    const invalidMap = {
      "01-double-engine": getPitchScreenBySlug("01-double-engine"),
      "02-industrial-flow": getPitchScreenBySlug("02-industrial-flow"),
      "03-hitech-os": getPitchScreenBySlug("03-hitech-os"),
      "04-valuation": {
        ...getPitchScreenBySlug("04-valuation"),
        title: "ESTRUCTURA FINANCIERA"
      }
    };

    expect(() => validatePitchScreenMap(invalidMap)).toThrow();
  });

  it("fails when route lookup receives unknown route", () => {
    expect(getPitchScreenByRoute("/pitch/99-unknown")).toBeNull();
  });

  it("rejects invariant violations", () => {
    const copy = copyPitchDeck();
    copy.screens[2] = {
      ...copy.screens[2],
      route: "/pitch/02-industrial-flow"
    };

    expect(() => ensurePitchInvariants(copy)).toThrow();
  });

  it("guards helper-level canonical APIs", () => {
    expect(isPitchScreenSlug("03-hitech-os")).toBe(true);
    expect(isPitchScreenSlug("03-hitech-os-v2")).toBe(false);

    const deck = getPitchDeck();
    expect(deck.navigation.base).toBe("/pitch");

    const route = getPitchRouteForSlug("04-valuation");
    expect(route).toBe("/pitch/04-valuation");

    const lines = getPitchScreenTextList("04-valuation");
    expect(lines).toContain("Modelo");
  });
});
