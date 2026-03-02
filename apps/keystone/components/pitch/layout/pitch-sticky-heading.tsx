import { cn } from "@hitech/ui-kit";

export interface PitchStickyHeadingProps {
  readonly label: string;
  readonly title: string;
  readonly subtitle?: string;
  readonly className?: string;
}

export function PitchStickyHeading({ label, title, subtitle, className }: PitchStickyHeadingProps) {
  return (
    <header className={cn("pitch-glass-card pitch-neon-edge grid gap-2 p-4 lg:sticky lg:top-2 lg:z-10", className)}>
      <p className="m-0 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-[color:rgba(4,18,25,0.6)]">
        {label}
      </p>
      <h3 className="m-0 text-lg font-semibold tracking-[-0.02em] text-[color:var(--pitch-ink)]">{title}</h3>
      {subtitle ? <p className="m-0 text-sm text-[color:rgba(4,18,25,0.72)]">{subtitle}</p> : null}
    </header>
  );
}
