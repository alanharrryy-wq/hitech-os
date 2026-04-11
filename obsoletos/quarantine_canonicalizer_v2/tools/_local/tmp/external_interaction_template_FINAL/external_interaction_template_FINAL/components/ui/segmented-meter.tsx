import { cn } from "@/lib/utils";

export interface SegmentedMeterProps {
  segments: number;
  active: number;
  label?: string;
  className?: string;
}

export function SegmentedMeter({ segments, active, label, className }: SegmentedMeterProps) {
  const safeSegments = Math.max(1, segments);
  const safeActive = Math.min(Math.max(active, 0), safeSegments);

  return (
    <div className={className} aria-label={label} role="progressbar" aria-valuemin={0} aria-valuemax={safeSegments} aria-valuenow={safeActive}>
      <div className="mb-2 flex items-center justify-between text-[11px] uppercase tracking-[0.16em] text-muted">
        <span>{label ?? "Progress"}</span>
        <span>{safeActive}/{safeSegments}</span>
      </div>
      <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${safeSegments}, minmax(0, 1fr))` }}>
        {Array.from({ length: safeSegments }).map((_, index) => (
          <div key={index} className={cn("h-2 rounded-full border border-white/8", index < safeActive ? "bg-accent/70" : "bg-white/7")} />
        ))}
      </div>
    </div>
  );
}
