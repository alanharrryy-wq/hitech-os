import type { LayerId } from "@hitech/ui-kit";

export const KNOWN_PITCH_ROUTES = [
  "/pitch",
  "/pitch/01-double-engine",
  "/pitch/02-industrial-flow",
  "/pitch/03-hitech-os",
  "/pitch/04-valuation"
] as const;

export type SceneMode = "single" | "list";

export interface SceneRecord {
  readonly id: string;
  readonly title: string;
  readonly route: string;
  readonly tags?: readonly string[];
  readonly mode: SceneMode;
  readonly layers?: readonly LayerId[];
}
