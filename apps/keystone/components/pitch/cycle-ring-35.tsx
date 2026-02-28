import { cn } from "@hitech/ui-kit";

export interface CycleRing35Props {
  readonly months?: number;
  readonly className?: string;
  readonly label?: string;
}

function describeCycle(months: number): string {
  return `Ciclo continuo ${months} meses para cubrir total`;
}

export function CycleRing35({ months = 35, className, label }: CycleRing35Props) {
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const progress = 0.78;
  const dashoffset = circumference * (1 - progress);

  return (
    <figure
      className={cn(
        "m-0 inline-flex items-center gap-3 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] p-3",
        className
      )}
    >
      <svg
        viewBox="0 0 120 120"
        width="84"
        height="84"
        role="img"
        aria-label={describeCycle(months)}
      >
        <title>{describeCycle(months)}</title>
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="hsl(var(--ui-border-2))"
          strokeWidth="10"
        />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="hsl(var(--ui-accent))"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashoffset}
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="56" textAnchor="middle" fontSize="14" fill="hsl(var(--ui-text-2))">
          {months}
        </text>
        <text x="60" y="72" textAnchor="middle" fontSize="8" fill="hsl(var(--ui-text-3))">
          meses
        </text>
      </svg>
      <figcaption>
        <p className="m-0 text-sm font-medium text-[hsl(var(--ui-text-2))]">
          {label ?? "Ciclo continuo"}
        </p>
        <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-3))]">
          {describeCycle(months)} → reinicio automático.
        </p>
      </figcaption>
    </figure>
  );
}
