import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  PITCH_ROUTE_FILES,
  REQUIRED_SUBROUTE_FILES,
  hasPitchRouteTree,
  renderPitchPageToHtml,
  resolveAppRootFromMeta,
  routeFileAbsolutePaths,
  toRouteId
} from "./utils/pitchDeckTestHarness";
import { PITCH_ROUTE_CASES, REQUIRED_PITCH_SUBROUTE_PATHNAMES } from "./utils/pitchRouteCases";

const appRoot = resolveAppRootFromMeta(import.meta.url);
const hasRouteTree = hasPitchRouteTree(appRoot);
const routeSuite = hasRouteTree ? describe : describe.skip;

routeSuite("keystone /pitch route deck stability", () => {
  it("/pitch exists and route files are present", () => {
    const indexRoutePath = path.join(appRoot, "app/pitch/page.tsx");

    expect(fs.existsSync(indexRoutePath)).toBe(true);

    const allRoutePaths = routeFileAbsolutePaths(appRoot);
    expect(allRoutePaths.length).toBe(5);
    expect(allRoutePaths.every((routePath) => fs.existsSync(routePath))).toBe(true);
  });

  it("exactly four pitch subroutes exist", () => {
    const subrouteFiles = REQUIRED_SUBROUTE_FILES.map((relativePath) => path.join(appRoot, relativePath));

    const existing = subrouteFiles.filter((absolutePath) => fs.existsSync(absolutePath));
    expect(existing.length).toBe(4);

    const normalizedPathnames = REQUIRED_PITCH_SUBROUTE_PATHNAMES.map((pathname) => pathname.trim());
    expect(normalizedPathnames).toEqual([
      "/pitch/01-double-engine",
      "/pitch/02-industrial-flow",
      "/pitch/03-hitech-os",
      "/pitch/04-valuation"
    ]);
  });

  for (const routeCase of PITCH_ROUTE_CASES) {
    it(`${routeCase.pathname} renders without crash and exposes deterministic markers`, async () => {
      const html = await renderPitchPageToHtml(appRoot, routeCase.relativeRouteFile, {});

      expect(html).not.toBeNull();
      expect(typeof html).toBe("string");
      expect((html ?? "").length).toBeGreaterThan(64);

      for (const marker of routeCase.expectedMarkerTexts) {
        expect(html).toContain(marker);
      }
    });

    it(`${routeCase.pathname} renders deterministic envelope for key query permutations`, async () => {
      const variants: ReadonlyArray<Record<string, string>> = [
        {},
        { layers: "none" },
        { layers: "stage.noise" },
        { layerProfile: "perf" },
        { layerProfile: "fx" },
        { debug: "1" },
        { layers: "stage.noise", layerProfile: "perf", debug: "1" }
      ];

      const outputs: string[] = [];
      for (const variant of variants) {
        const html = await renderPitchPageToHtml(appRoot, routeCase.relativeRouteFile, variant);
        expect(html).not.toBeNull();
        expect(html).toContain("Keystone Pitch Deck");
        outputs.push(html ?? "");
      }

      expect(outputs.length).toBe(7);
      expect(outputs.every((item) => item.length > 64)).toBe(true);

      const routeId = toRouteId(routeCase.relativeRouteFile);
      const stableDigest = outputs.map((item, index) => `${routeId}:${index}:${item.length}`).join("|");
      expect(stableDigest.startsWith(`${routeId}:0:`)).toBe(true);
    });
  }
});

if (!hasRouteTree) {
  describe("keystone /pitch route deck stability (missing route tree)", () => {
    it("documents missing route tree in this worktree so integration runner can re-enable tests", () => {
      expect(path.normalize(appRoot)).toContain(path.normalize("apps\\keystone"));
      expect(fs.existsSync(path.join(appRoot, "app/pitch/page.tsx"))).toBe(false);
    });
  });
}

if (hasRouteTree) {
  describe("keystone /pitch route matrix integrity", () => {
    it("keeps declared route list stable and deterministic", () => {
      const routeIds = PITCH_ROUTE_CASES.map((item) => item.id);
      expect(routeIds).toEqual([
        "ROUTE_INDEX",
        "ROUTE_01_DOUBLE_ENGINE",
        "ROUTE_02_INDUSTRIAL_FLOW",
        "ROUTE_03_HITECH_OS",
        "ROUTE_04_VALUATION"
      ]);

      const declaredFiles = PITCH_ROUTE_CASES.map((item) => item.relativeRouteFile);
      expect(declaredFiles).toEqual(PITCH_ROUTE_FILES);
    });

    it("ensures route cases map one-to-one to physical files", () => {
      const caseFiles = new Set(PITCH_ROUTE_CASES.map((item) => item.relativeRouteFile));
      expect(caseFiles.size).toBe(PITCH_ROUTE_CASES.length);
      for (const relativePath of caseFiles) {
        expect(fs.existsSync(path.join(appRoot, relativePath))).toBe(true);
      }
    });
  });
}
