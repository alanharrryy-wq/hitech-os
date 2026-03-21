import type {
  ModuleRuntimeSnapshot,
  MutationResult,
  SelectionState,
  WorkbenchLayoutModel,
  WorkbenchTopStrip,
} from "../contracts";

export interface WorkbenchLayoutInput {
  readonly modules: readonly ModuleRuntimeSnapshot[];
  readonly selection: SelectionState;
  readonly latestMutation?: MutationResult;
  readonly safeMode: boolean;
  readonly bridgeRoute: string;
  readonly workspaceStatus: string;
}

export function buildWorkbenchLayout(input: WorkbenchLayoutInput): WorkbenchLayoutModel {
  const topStrip: WorkbenchTopStrip = {
    safeModeLabel: input.safeMode ? "SAFE MODE" : "CONNECTED MODE",
    bridgeRoute: input.bridgeRoute,
    workspaceStatus: input.workspaceStatus,
  };

  const leftColumn = [
    "Module Registry",
    ...input.modules.map(
      (module) => `${module.id} | ${module.status} | owner=${module.owner}`,
    ),
  ];

  const centerColumn = [
    "Module Board Host",
    "Render module-owned surfaces here using explicit registration.",
    "No dock/menu/toolbar auto-contribution model is assumed.",
  ];

  const selectionLine = input.selection.current
    ? `selection=${input.selection.current.kind}:${input.selection.current.entityId}`
    : "selection=none";

  const mutationLine = input.latestMutation
    ? `mutation=${input.latestMutation.summary}`
    : "mutation=no requests";

  const rightColumn = [
    "Selection / Mutation / Inspector",
    selectionLine,
    mutationLine,
    "inspector=placeholder",
  ];

  return {
    topStrip,
    leftColumn,
    centerColumn,
    rightColumn,
  };
}
