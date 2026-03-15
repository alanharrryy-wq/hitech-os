import type { LiveSceneComposerRegistration } from "../contracts";
import type { AuthoringWorkbenchModuleDescriptor } from "./authoring-workbench-contracts";

export const AUTHORING_WORKBENCH_V1_MODULE: AuthoringWorkbenchModuleDescriptor = {
  id: "authoring-workbench-v1",
  title: "Authoring Workbench v1",
  enabledByDefault: true,
  capabilities: [
    "scene-look.update",
    "layout.move",
    "layout.resize",
    "layout.reorder",
    "widget.insert-from-prefab",
    "widget.update-props",
    "widget.update-style",
    "widget.remove",
    "selection.reset",
    "draft.discard",
    "draft.commit",
  ],
  supportedTargets: ["scene", "layout-node", "slot", "widget"],
  safeModeCompatible: true,
  advancedModeCompatible: true,
};

export function createComposerModuleRegistry(
  additionalModules: readonly AuthoringWorkbenchModuleDescriptor[] = []
): LiveSceneComposerRegistration & { readonly descriptors: readonly AuthoringWorkbenchModuleDescriptor[] } {
  const descriptors = [AUTHORING_WORKBENCH_V1_MODULE, ...additionalModules];
  return {
    modules: descriptors.map(({ id, title, enabledByDefault }) => ({ id, title, enabledByDefault })),
    descriptors,
  };
}
