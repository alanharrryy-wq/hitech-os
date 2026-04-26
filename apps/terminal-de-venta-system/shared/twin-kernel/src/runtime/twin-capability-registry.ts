import type {
  TwinCapabilityDomain,
  TwinCapabilityManifest,
  TwinCapabilityScorecardRow,
  TwinSurface,
  TwinSurfaceBinding
} from "../types/capability";
import { assertTwinCapabilityRegistry, validateTwinCapabilityRegistry } from "../validation/twin-capability-validator";

export type TwinCapabilityRegistry = {
  all: TwinCapabilityManifest[];
  get(id: string): TwinCapabilityManifest | undefined;
  require(id: string): TwinCapabilityManifest;
  byDomain(domain: TwinCapabilityDomain): TwinCapabilityManifest[];
  bySurface(surface: TwinSurface): TwinCapabilityManifest[];
  byModule(surface: TwinSurface, moduleKey: string): TwinCapabilityManifest[];
  surfaceBinding(id: string, surface: TwinSurface): TwinSurfaceBinding | undefined;
  scorecard(): TwinCapabilityScorecardRow[];
  assertHealthy(): TwinCapabilityManifest[];
};

export function buildTwinCapabilityScorecard(capabilities: TwinCapabilityManifest[]): TwinCapabilityScorecardRow[] {
  return capabilities.map((capability) => {
    const pc = capability.surfaces.find((surface) => surface.surface === "pc");
    const tablet = capability.surfaces.find((surface) => surface.surface === "tablet");
    return {
      id: capability.id,
      title: capability.title,
      domain: capability.domain,
      status: capability.status,
      pcRole: pc?.role ?? "missing",
      tabletRole: tablet?.role ?? "missing",
      syncDirection: capability.syncDirection,
      requiredEventCount: capability.events.filter((eventRef) => eventRef.required).length,
      acceptanceCount: capability.acceptance.length,
      riskCount: capability.risks.length
    };
  });
}

export function buildTwinSurfaceMap(capabilities: TwinCapabilityManifest[], surface: TwinSurface): Record<string, TwinCapabilityManifest[]> {
  return capabilities.reduce<Record<string, TwinCapabilityManifest[]>>((accumulator, capability) => {
    const binding = capability.surfaces.find((entry) => entry.surface === surface);
    if (!binding) return accumulator;
    accumulator[binding.moduleKey] = accumulator[binding.moduleKey] ?? [];
    accumulator[binding.moduleKey].push(capability);
    return accumulator;
  }, {});
}

export function createTwinCapabilityRegistry(capabilities: TwinCapabilityManifest[]): TwinCapabilityRegistry {
  const safeCapabilities = assertTwinCapabilityRegistry([...capabilities]);
  const byId = new Map(safeCapabilities.map((capability) => [capability.id, capability]));

  return {
    all: safeCapabilities,
    get(id) {
      return byId.get(id);
    },
    require(id) {
      const capability = byId.get(id);
      if (!capability) {
        throw new Error(`Twin capability not found: ${id}`);
      }
      return capability;
    },
    byDomain(domain) {
      return safeCapabilities.filter((capability) => capability.domain === domain);
    },
    bySurface(surface) {
      return safeCapabilities.filter((capability) => capability.surfaces.some((entry) => entry.surface === surface));
    },
    byModule(surface, moduleKey) {
      return safeCapabilities.filter((capability) =>
        capability.surfaces.some((entry) => entry.surface === surface && entry.moduleKey === moduleKey)
      );
    },
    surfaceBinding(id, surface) {
      return byId.get(id)?.surfaces.find((entry) => entry.surface === surface);
    },
    scorecard() {
      return buildTwinCapabilityScorecard(safeCapabilities);
    },
    assertHealthy() {
      return assertTwinCapabilityRegistry(safeCapabilities);
    }
  };
}

export function explainTwinCapabilityHealth(capabilities: TwinCapabilityManifest[]): string[] {
  const result = validateTwinCapabilityRegistry(capabilities);
  if (result.ok && result.warnings.length === 0) {
    return ["Twin capability registry is valid with no warnings."];
  }
  return [
    ...result.errors.map((entry) => `ERROR ${entry.code} ${entry.capabilityId}: ${entry.message}`),
    ...result.warnings.map((entry) => `WARN ${entry.code} ${entry.capabilityId}: ${entry.message}`)
  ];
}
