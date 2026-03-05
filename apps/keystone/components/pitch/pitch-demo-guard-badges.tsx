"use client";

import { Badge } from "@hitech/ui-kit";
import type { DemoGuardIndicators } from "../../lib/pitch/demo-state";

const GUARD_LABELS: Record<keyof DemoGuardIndicators, string> = {
  docs_complete: "docs_complete",
  temp_excursion: "temp_excursion",
  supplier_status: "supplier_status",
  role_gating: "role_gating"
};

export interface PitchDemoGuardBadgesProps {
  readonly guards: DemoGuardIndicators;
}

export function PitchDemoGuardBadges({ guards }: PitchDemoGuardBadgesProps) {
  const entries = Object.entries(guards) as ReadonlyArray<[keyof DemoGuardIndicators, boolean]>;

  return (
    <div className="flex flex-wrap gap-2">
      {entries.map(([key, passed]) => (
        <Badge key={key} tone={passed ? "success" : "danger"}>
          {GUARD_LABELS[key]}: {passed ? "pass" : "fail"}
        </Badge>
      ))}
    </div>
  );
}
