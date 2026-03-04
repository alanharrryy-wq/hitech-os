import { describe, expect, it } from "vitest";
import {
  CAPABILITY_PRIORITY_ORDER,
  buildCapabilityResolverInput,
  explainCapabilityResolution,
  getCapabilityCatalogEntry,
  getCapabilityQuerySpec,
  getCapabilityRegistry,
  isCapabilityMode,
  resolveCapability,
  resolveDirectorCapability
} from "../../lib/pitch-engine/index.js";

class MemoryStorage {
  private readonly data = new Map<string, string>();

  public setItem(key: string, value: string): void {
    this.data.set(key, value);
  }

  public getItem(key: string): string | null {
    return this.data.get(key) ?? null;
  }
}

describe("capabilities", () => {
  it("registry exposes director capability with auditable metadata", () => {
    const snapshot = getCapabilityRegistry();

    expect(snapshot.schemaVersion).toBe(1);
    expect(snapshot.capabilities).toHaveLength(1);
    expect(snapshot.capabilities[0]?.capability).toBe("director");
    expect(snapshot.capabilities[0]?.defaultMode).toBe("off");
  });

  it("catalog entry contains expected mode set", () => {
    const entry = getCapabilityCatalogEntry("director");

    expect(entry.modes).toEqual(["off", "lite", "full", "debug"]);
    expect(entry.owner).toContain("pitch-engine");
  });

  it("query spec has deterministic keys", () => {
    const spec = getCapabilityQuerySpec("director");

    expect(spec.queryKey).toBe("capDirector");
    expect(spec.envKey).toBe("PITCH_CAP_DIRECTOR");
    expect(spec.storageKey).toBe("pitch.capability.director");
  });

  it("isCapabilityMode recognizes valid modes", () => {
    expect(isCapabilityMode("off")).toBe(true);
    expect(isCapabilityMode("lite")).toBe(true);
    expect(isCapabilityMode("full")).toBe(true);
    expect(isCapabilityMode("debug")).toBe(true);
  });

  it("isCapabilityMode rejects unknown values", () => {
    expect(isCapabilityMode("advanced")).toBe(false);
    expect(isCapabilityMode("")) .toBe(false);
    expect(isCapabilityMode("FULL")).toBe(false);
  });

  const priorityCases: ReadonlyArray<{
    readonly name: string;
    readonly defaults: "off" | "lite" | "full" | "debug";
    readonly env?: string;
    readonly query?: string;
    readonly storage?: string;
    readonly expectedRequested: "off" | "lite" | "full" | "debug";
    readonly expectedSource: "env" | "query" | "localStorage" | "defaults";
  }> = [
    {
      name: "uses env over all sources",
      defaults: "off",
      env: "debug",
      query: "lite",
      storage: "full",
      expectedRequested: "debug",
      expectedSource: "env"
    },
    {
      name: "uses query when env missing",
      defaults: "off",
      query: "full",
      storage: "lite",
      expectedRequested: "full",
      expectedSource: "query"
    },
    {
      name: "uses localStorage when env/query missing",
      defaults: "off",
      storage: "lite",
      expectedRequested: "lite",
      expectedSource: "localStorage"
    },
    {
      name: "uses defaults when no source present",
      defaults: "debug",
      expectedRequested: "debug",
      expectedSource: "defaults"
    },
    {
      name: "ignores invalid env and falls back to query",
      defaults: "off",
      env: "invalid",
      query: "full",
      expectedRequested: "full",
      expectedSource: "query"
    },
    {
      name: "ignores invalid query and uses localStorage",
      defaults: "off",
      query: "invalid",
      storage: "lite",
      expectedRequested: "lite",
      expectedSource: "localStorage"
    },
    {
      name: "ignores invalid localStorage and uses defaults",
      defaults: "full",
      storage: "invalid",
      expectedRequested: "full",
      expectedSource: "defaults"
    },
    {
      name: "trims env whitespace",
      defaults: "off",
      env: "  lite ",
      expectedRequested: "lite",
      expectedSource: "env"
    },
    {
      name: "trims query whitespace",
      defaults: "off",
      query: "  full  ",
      expectedRequested: "full",
      expectedSource: "query"
    },
    {
      name: "trims localStorage whitespace",
      defaults: "off",
      storage: "  debug  ",
      expectedRequested: "debug",
      expectedSource: "localStorage"
    },
    {
      name: "env off wins over query full",
      defaults: "lite",
      env: "off",
      query: "full",
      expectedRequested: "off",
      expectedSource: "env"
    },
    {
      name: "query off wins over localStorage full",
      defaults: "lite",
      query: "off",
      storage: "full",
      expectedRequested: "off",
      expectedSource: "query"
    }
  ];

  it.each(priorityCases)("$name", ({ defaults, env, query, storage, expectedRequested, expectedSource }) => {
    const memoryStorage = new MemoryStorage();
    const spec = getCapabilityQuerySpec("director");

    if (storage) {
      memoryStorage.setItem(spec.storageKey, storage);
    }

    const resolution = resolveDirectorCapability({
      defaults: {
        director: defaults
      },
      env: env
        ? {
            [spec.envKey]: env
          }
        : {},
      query: query
        ? {
            [spec.queryKey]: query
          }
        : {},
      localStorage: memoryStorage
    });

    expect(resolution.requested).toBe(expectedRequested);
    const selected = resolution.auditTrail.find((event) => event.selected);
    expect(selected?.source).toBe(expectedSource);
  });

  it("enforces production hard gate to off", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "full"
      },
      nodeEnv: "production"
    });

    expect(resolution.requested).toBe("full");
    expect(resolution.applied).toBe("off");
    expect(resolution.reasons).toContain("production-hard-gate");
  });

  it("keeps requested when not production", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "lite"
      },
      nodeEnv: "development"
    });

    expect(resolution.requested).toBe("lite");
    expect(resolution.applied).toBe("lite");
    expect(resolution.reasons).toContain("requested-equals-applied");
  });

  it("captures audit trail entries for each source in deterministic order", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "off"
      },
      env: {
        PITCH_CAP_DIRECTOR: "lite"
      },
      query: {
        capDirector: "full"
      }
    });

    const sources = resolution.auditTrail.map((event) => event.source);
    expect(sources).toEqual(["env", "query", "localStorage", "defaults"]);
  });

  it("priority order constant matches contract", () => {
    expect(CAPABILITY_PRIORITY_ORDER).toEqual(["env", "query", "localStorage", "defaults"]);
  });

  it("resolveCapability generic supports director", () => {
    const resolution = resolveCapability("director", {
      defaults: {
        director: "debug"
      }
    });

    expect(resolution.capability).toBe("director");
    expect(resolution.requested).toBe("debug");
  });

  it("buildCapabilityResolverInput fills defaults when omitted", () => {
    const input = buildCapabilityResolverInput({});

    expect(input.defaults.director).toBe("off");
  });

  it("buildCapabilityResolverInput preserves explicit values", () => {
    const storage = new MemoryStorage();
    const input = buildCapabilityResolverInput({
      defaults: { director: "lite" },
      env: { PITCH_CAP_DIRECTOR: "debug" },
      query: { capDirector: "full" },
      localStorage: storage,
      nodeEnv: "test"
    });

    expect(input.defaults.director).toBe("lite");
    expect(input.env?.PITCH_CAP_DIRECTOR).toBe("debug");
    expect((input.query as Record<string, string>)?.capDirector).toBe("full");
    expect(input.localStorage).toBe(storage);
    expect(input.nodeEnv).toBe("test");
  });

  it("explainCapabilityResolution outputs summary string", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "lite"
      }
    });

    const text = explainCapabilityResolution(resolution);

    expect(text).toContain("capability=director");
    expect(text).toContain("requested=lite");
    expect(text).toContain("applied=lite");
  });

  it("URLSearchParams query source is supported", () => {
    const params = new URLSearchParams("capDirector=debug");

    const resolution = resolveDirectorCapability({
      defaults: {
        director: "off"
      },
      query: params
    });

    expect(resolution.requested).toBe("debug");
  });

  it("invalid URLSearchParams value falls back to defaults", () => {
    const params = new URLSearchParams("capDirector=invalid");

    const resolution = resolveDirectorCapability({
      defaults: {
        director: "lite"
      },
      query: params
    });

    expect(resolution.requested).toBe("lite");
  });

  it("resolution reason records mode override in production", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "debug"
      },
      nodeEnv: "production"
    });

    expect(resolution.reasons).toContain("resolved-debug-to-off");
  });

  it("audit marks only one selected source", () => {
    const resolution = resolveDirectorCapability({
      defaults: {
        director: "off"
      },
      env: {
        PITCH_CAP_DIRECTOR: "full"
      },
      query: {
        capDirector: "lite"
      }
    });

    const selectedCount = resolution.auditTrail.filter((entry) => entry.selected).length;
    expect(selectedCount).toBe(1);
  });

  it("fallback reason stays deterministic", () => {
    const resolutionA = resolveDirectorCapability({
      defaults: {
        director: "off"
      }
    });

    const resolutionB = resolveDirectorCapability({
      defaults: {
        director: "off"
      }
    });

    expect(resolutionA.reasons).toEqual(resolutionB.reasons);
    expect(resolutionA.auditTrail).toEqual(resolutionB.auditTrail);
  });
});
