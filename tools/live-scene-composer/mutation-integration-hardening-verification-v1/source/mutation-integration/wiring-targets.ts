export type ComposerMutationSurface = "canvas" | "structure-tree" | "inspector";

export interface WiringTarget {
  readonly surface: ComposerMutationSurface;
  readonly entrypoint: string;
  readonly emitsIntent: boolean;
}

export const wiringTargets: readonly WiringTarget[] = [
  { surface: "canvas", entrypoint: "canvas-mutation-entry", emitsIntent: true },
  { surface: "structure-tree", entrypoint: "structure-tree-mutation-entry", emitsIntent: true },
  { surface: "inspector", entrypoint: "inspector-mutation-entry", emitsIntent: true }
];
