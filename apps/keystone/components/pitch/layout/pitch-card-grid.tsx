import { cn } from "@hitech/ui-kit";

export interface PitchCardGridProps {
  readonly columns?: 1 | 2 | 3 | 4;
  readonly className?: string;
  readonly children: React.ReactNode;
}

function gridClass(columns: PitchCardGridProps["columns"]): string {
  if (columns === 1) {
    return "grid-cols-1";
  }

  if (columns === 2) {
    return "grid-cols-1 md:grid-cols-2";
  }

  if (columns === 4) {
    return "grid-cols-1 md:grid-cols-2 xl:grid-cols-4";
  }

  return "grid-cols-1 md:grid-cols-2 xl:grid-cols-3";
}

export function PitchCardGrid({ columns = 3, className, children }: PitchCardGridProps) {
  return <div className={cn("grid gap-3", gridClass(columns), className)}>{children}</div>;
}

export interface PitchCardGridItemProps {
  readonly title: string;
  readonly description?: string;
  readonly kicker?: string;
  readonly className?: string;
  readonly children?: React.ReactNode;
  readonly tone?: "neutral" | "teal" | "gold" | "cyan" | "dark";
}

function toneClass(tone: PitchCardGridItemProps["tone"]): string {
  if (tone === "teal") {
    return "border-[rgba(2,111,134,0.3)] bg-[linear-gradient(160deg,rgba(2,111,134,0.08),rgba(2,111,134,0.03))]";
  }

  if (tone === "gold") {
    return "border-[rgba(171,123,38,0.3)] bg-[linear-gradient(160deg,rgba(171,123,38,0.12),rgba(171,123,38,0.03))]";
  }

  if (tone === "cyan") {
    return "border-[rgba(2,167,202,0.34)] bg-[linear-gradient(160deg,rgba(2,167,202,0.11),rgba(2,167,202,0.03))]";
  }

  if (tone === "dark") {
    return "border-[rgba(2,167,202,0.4)] bg-[linear-gradient(160deg,rgba(4,18,25,0.9),rgba(2,56,68,0.8))] text-white";
  }

  return "border-[rgba(2,111,134,0.2)] bg-[linear-gradient(160deg,rgba(255,255,255,0.95),rgba(255,255,255,0.72))]";
}

export function PitchCardGridItem({
  title,
  description,
  kicker,
  className,
  children,
  tone = "neutral"
}: PitchCardGridItemProps) {
  return (
    <article className={cn("pitch-glass-card pitch-neon-edge grid gap-2 p-3", toneClass(tone), className)}>
      {kicker ? (
        <p className="m-0 text-[0.65rem] font-semibold uppercase tracking-[0.11em] text-[color:rgba(4,18,25,0.62)]">
          {kicker}
        </p>
      ) : null}
      <h3 className="m-0 text-sm font-semibold text-[color:currentColor]">{title}</h3>
      {description ? (
        <p className="m-0 text-xs leading-5 text-[color:rgba(4,18,25,0.7)] dark:text-[rgba(255,255,255,0.78)]">
          {description}
        </p>
      ) : null}
      {children ? <div className="mt-1 grid gap-2">{children}</div> : null}
    </article>
  );
}
