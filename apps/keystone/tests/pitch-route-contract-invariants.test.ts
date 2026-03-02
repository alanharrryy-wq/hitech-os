import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  buildPitchLinkModel,
  collectAllPitchTextFragments,
  getPitchDeck,
  getPitchRouteForSlug,
  PITCH_COPY_LOCK_NOTICE,
  PITCH_ROUTES,
  PITCH_ROUTE_BASE,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES
} from "@hitech/contracts";
import { describe, expect, it } from "vitest";
import { PITCH_CANONICAL_ROUTES, renderPitchRoute } from "./_utils/pitch-test-harness";

function listRouteDirectories(): readonly string[] {
  const thisDir = path.dirname(fileURLToPath(import.meta.url));
  const routeRoot = path.resolve(thisDir, "../app/pitch");
  return fs
    .readdirSync(routeRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((value) => /^\d{2}-[a-z0-9-]+$/u.test(value))
    .sort((left, right) => left.localeCompare(right));
}

describe("pitch route + contract invariants", () => {
  it("keeps route directory names aligned with contract slugs", () => {
    const routeDirectories = listRouteDirectories();
    expect(routeDirectories).toEqual(PITCH_SCREEN_ORDER);

    for (const slug of PITCH_SCREEN_ORDER) {
      const route = PITCH_ROUTES[slug];
      expect(route).toBe(`${PITCH_ROUTE_BASE}/${slug}`);
      expect(getPitchRouteForSlug(slug)).toBe(route);
    }
  });

  it("keeps canonical navigation links and titles synchronized", () => {
    const links = buildPitchLinkModel();
    expect(links).toHaveLength(PITCH_SCREEN_ORDER.length);

    for (const [index, link] of links.entries()) {
      const expectedSlug = PITCH_SCREEN_ORDER[index];
      expect(link.slug).toBe(expectedSlug);
      expect(link.href).toBe(PITCH_ROUTES[expectedSlug]);
      expect(link.title).toBe(PITCH_SCREEN_TITLES[expectedSlug]);
      expect(link.isCanonical).toBe(true);
    }
  });

  it("exposes an immutable copy-lock notice in deck meta", () => {
    const deck = getPitchDeck();
    expect(deck.meta.copyLockNotice).toBe(PITCH_COPY_LOCK_NOTICE);
    expect(deck.meta.copyLockNotice).toBe(
      "Canonical copy is contract-locked. Do not mutate strings outside contract fixtures."
    );
  });

  it("renders index + canonical screen routes as non-empty HTML payloads", () => {
    for (const route of PITCH_CANONICAL_ROUTES) {
      const html = renderPitchRoute(route);
      expect(html.length).toBeGreaterThan(100);
      expect(html).toContain("Keystone Pitch Deck");
      expect(html).toContain('aria-label="Pitch navigation"');
    }
  });

  it("retains required canonical text fragments for investor pitch", () => {
    const fragments = collectAllPitchTextFragments();
    const textIndex = new Set(fragments.map((fragment) => fragment.text));

    expect(textIndex.has("No soy proveedor. Soy sistema.")).toBe(true);
    expect(textIndex.has("Mercado interno ya existente, no especulativo.")).toBe(true);
    expect(
      textIndex.has(
        "Infraestructura digital propietaria diseñada para control de activos críticos."
      )
    ).toBe(true);
    expect(textIndex.has("Valuación combinada estimada: 4–6M")).toBe(true);
  });
});
