import type {
  ModuleBoardItem,
  ModuleRuntimeSnapshot,
} from "../../contracts";

export interface ModuleBoardModel {
  readonly title: string;
  readonly items: readonly ModuleBoardItem[];
  readonly emptyMessage: string;
}

export function buildModuleBoard(
  snapshots: readonly ModuleRuntimeSnapshot[],
): ModuleBoardModel {
  return {
    title: "Composer Module Board",
    items: snapshots.map((snapshot) => ({
      moduleId: snapshot.id,
      owner: snapshot.owner,
      status: snapshot.status,
      description: snapshot.message ?? "no diagnostics",
      message: snapshot.message,
    })),
    emptyMessage:
      snapshots.length === 0
        ? "No modules registered. Register explicit module manifests first."
        : "",
  };
}
