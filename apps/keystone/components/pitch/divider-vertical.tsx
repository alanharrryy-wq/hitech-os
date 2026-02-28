import { cn } from "@hitech/ui-kit";

export interface DividerVerticalProps {
  readonly className?: string;
  readonly label?: string;
}

export function DividerVertical({ className, label }: DividerVerticalProps) {
  return (
    <div
      className={cn("relative flex w-6 items-center justify-center", className)}
      aria-hidden="true"
    >
      <span className="h-full w-px bg-[hsl(var(--ui-border-2))]" />
      {label ? (
        <span className="absolute rounded border border-[hsl(var(--ui-border-2))] bg-[hsl(var(--ui-surface-1))] px-1 py-0.5 text-[0.625rem] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
          {label}
        </span>
      ) : null}
    </div>
  );
}
