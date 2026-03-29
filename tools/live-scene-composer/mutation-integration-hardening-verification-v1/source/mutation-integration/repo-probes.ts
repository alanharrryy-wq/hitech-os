export interface ComposerSourceProbe {
  readonly status: "unique" | "ambiguous" | "missing";
  readonly selected?: string;
  readonly candidates: readonly string[];
}

export function describeProbe(probe: ComposerSourceProbe): string {
  return `${probe.status}:${probe.selected ?? "none"}:${probe.candidates.length}`;
}
