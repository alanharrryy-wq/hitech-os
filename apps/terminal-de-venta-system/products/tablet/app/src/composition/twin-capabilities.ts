import { TWIN_CAPABILITY_MANIFEST } from "@shared-kernel/data/twin-capability-manifest";
import {
  buildTwinSurfaceMap,
  createTwinCapabilityRegistry
} from "@shared-kernel/runtime/twin-capability-registry";
import { tabletModuleRegistry } from "./module-registry";

export const tabletTwinCapabilityRegistry = createTwinCapabilityRegistry(TWIN_CAPABILITY_MANIFEST);
export const tabletTwinCapabilities = tabletTwinCapabilityRegistry.bySurface("tablet");
export const tabletTwinCapabilityScorecard = tabletTwinCapabilityRegistry.scorecard();
export const tabletTwinCapabilityByModule = buildTwinSurfaceMap(TWIN_CAPABILITY_MANIFEST, "tablet");

export const tabletModuleTwinReadiness = tabletModuleRegistry.map((module) => ({
  moduleKey: module.key,
  title: module.title,
  route: module.route,
  capabilities: tabletTwinCapabilityRegistry.byModule("tablet", module.key).map((capability) => capability.id)
}));
