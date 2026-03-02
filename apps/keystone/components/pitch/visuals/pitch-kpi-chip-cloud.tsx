import { cn } from "@hitech/ui-kit";
import { PitchDataChip } from "../layout/pitch-data-chip";

export interface PitchKpiChipCloudProps {
  readonly items: ReadonlyArray<{
    readonly label: string;
    readonly value?: string;
    readonly tone?: "gold" | "teal" | "cyan" | "brown" | "neutral";
  }>;
  readonly className?: string;
}

export function PitchKpiChipCloud({ items, className }: PitchKpiChipCloudProps) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      {items.map((item) => (
        <PitchDataChip
          key={`${item.label}-${item.value ?? "none"}`}
          label={item.label}
          {...(item.value ? { value: item.value } : {})}
          {...(item.tone ? { tone: item.tone } : {})}
        />
      ))}
    </div>
  );
}
