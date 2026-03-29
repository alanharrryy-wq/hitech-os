import { cn } from "@hitech/ui-kit";

export interface PitchComparisonMeterProps {
  readonly leftLabel: string;
  readonly rightLabel: string;
  readonly leftValue: number;
  readonly rightValue: number;
  readonly className?: string;
}

function percent(value: number, total: number): number {
  if (total <= 0) {
    return 50;
  }

  return Math.round((value / total) * 100);
}

export function PitchComparisonMeter({
  leftLabel,
  rightLabel,
  leftValue,
  rightValue,
  className
}: PitchComparisonMeterProps) {
  const total = leftValue + rightValue;
  const left = percent(leftValue, total);
  const right = 100 - left;

  return (
    <article className={cn("pitch-glass-card pitch-neon-edge grid gap-2 p-3", className)}>
      <div className="flex items-center justify-between gap-2 text-xs font-semibold text-[color:rgba(4,18,25,0.72)]">
        <span>{leftLabel}</span>
        <span>{rightLabel}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[rgba(4,18,25,0.08)]">
        <span className="block h-full bg-[linear-gradient(90deg,#026F86,#02A7CA)]" style={{ width: `${left}%` }} />
      </div>
      <div className="flex items-center justify-between gap-2 text-xs">
        <span className="font-semibold text-[color:#026F86]">{left}%</span>
        <span className="font-semibold text-[color:#553E13]">{right}%</span>
      </div>
    </article>
  );
}
