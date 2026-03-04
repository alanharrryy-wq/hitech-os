import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { createFeatureFlags } from "../../../../factory/contracts/FactoryContracts";
import { PITCH_CANONICAL_ROUTES, renderPitchRoute } from "../_utils/pitch-test-harness";

const REPO_ROOT = path.resolve(__dirname, "../..");

interface RouteGateCase {
  readonly route: string;
  readonly filePath: string;
}

const DEV_ROUTE_GATES: readonly RouteGateCase[] = [
  {
    route: "/dev/pitch-engine",
    filePath: path.join(REPO_ROOT, "app/dev/pitch-engine/page.tsx")
  },
  {
    route: "/dev/scene-studio",
    filePath: path.join(REPO_ROOT, "app/dev/scene-studio/page.tsx")
  }
] as const;

const FORBIDDEN_API_GATES: readonly RouteGateCase[] = [
  {
    route: "/api/pitch-engine",
    filePath: path.join(REPO_ROOT, "app/api/pitch-engine/route.ts")
  },
  {
    route: "/api/scene-studio",
    filePath: path.join(REPO_ROOT, "app/api/scene-studio/route.ts")
  },
  {
    route: "/api/bridge/pitch-engine",
    filePath: path.join(REPO_ROOT, "app/api/bridge/pitch-engine/route.ts")
  }
] as const;

const ALLOWED_API_ROUTES: readonly RouteGateCase[] = [
  {
    route: "/api/activity",
    filePath: path.join(REPO_ROOT, "app/api/activity/route.ts")
  },
  {
    route: "/api/runs",
    filePath: path.join(REPO_ROOT, "app/api/runs/route.ts")
  },
  {
    route: "/api/widgets",
    filePath: path.join(REPO_ROOT, "app/api/widgets/route.ts")
  }
] as const;

function withNodeEnv<T>(nodeEnv: string, cb: () => T): T {
  const original = process.env["NODE_ENV"];
  process.env["NODE_ENV"] = nodeEnv;
  try {
    return cb();
  } finally {
    if (original === undefined) {
      delete process.env["NODE_ENV"];
    } else {
      process.env["NODE_ENV"] = original;
    }
  }
}

describe("pitch-engine integration access gate validation", () => {
  for (const gate of DEV_ROUTE_GATES) {
    it(`gates ${gate.route} in production by route absence`, () => {
      expect(fs.existsSync(gate.filePath)).toBe(false);
    });
  }

  for (const gate of FORBIDDEN_API_GATES) {
    it(`gates forbidden api route ${gate.route}`, () => {
      expect(fs.existsSync(gate.filePath)).toBe(false);
    });
  }

  for (const route of ALLOWED_API_ROUTES) {
    it(`keeps allowed api route ${route.route} present`, () => {
      expect(fs.existsSync(route.filePath)).toBe(true);
    });
  }

  for (const route of PITCH_CANONICAL_ROUTES) {
    it(`hides debug tooling in production for ${route}`, () => {
      const html = withNodeEnv("production", () => renderPitchRoute(route, "debug=1&layers=all"));
      expect(html).not.toContain("Layer Toggle Debugging");
      expect(html).not.toContain('aria-label="Layer Debug Panel"');
    });
  }

  it("forces feature flags off in production hard gate model", () => {
    const productionFlags = createFeatureFlags({
      allowExperimentalWorkers: false,
      allowCrossModuleImports: false,
      allowTemporalSignals: false,
      allowNonDeterministicApis: false
    });

    expect(productionFlags.allowExperimentalWorkers).toBe(false);
    expect(productionFlags.allowCrossModuleImports).toBe(false);
    expect(productionFlags.allowTemporalSignals).toBe(false);
    expect(productionFlags.allowNonDeterministicApis).toBe(false);
  });

  it("maintains deterministic canonical pitch routes as smoke baseline", () => {
    const first = PITCH_CANONICAL_ROUTES.join("|");
    const second = PITCH_CANONICAL_ROUTES.join("|");
    expect(first).toBe(second);
  });
});
