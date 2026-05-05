import { TWIN_CAPABILITY_MANIFEST } from "@shared-kernel/data/twin-capability-manifest";
import {
  buildTwinSurfaceMap,
  createTwinCapabilityRegistry
} from "@shared-kernel/runtime/twin-capability-registry";
import { pcModuleRegistry } from "./module-registry";

export const pcTwinCapabilityRegistry = createTwinCapabilityRegistry(TWIN_CAPABILITY_MANIFEST);
export const pcTwinCapabilities = pcTwinCapabilityRegistry.bySurface("pc");
export const pcTwinCapabilityScorecard = pcTwinCapabilityRegistry.scorecard();
export const pcTwinCapabilityByModule = buildTwinSurfaceMap(TWIN_CAPABILITY_MANIFEST, "pc");

export const pcModuleTwinReadiness = pcModuleRegistry.map((module) => ({
  moduleKey: module.key,
  title: module.title,
  route: module.route,
  capabilities: pcTwinCapabilityRegistry.byModule("pc", module.key).map((capability) => capability.id)
}));
