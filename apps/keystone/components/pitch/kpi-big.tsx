import { cn } from "@hitech/ui-kit";

export interface KpiBigProps {
  readonly label: string;
  readonly value: string;
  readonly note?: string;
  readonly className?: string;
}

export function KpiBig({ label, value, note, className }: KpiBigProps) {
  return (
    <article
      className={cn(
        "rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-4",
        className
      )}
    >
      <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
        {label}
      </p>
      <p className="m-0 mt-2 text-3xl font-semibold leading-none tracking-[-0.02em] text-[hsl(var(--ui-text-1))]">
        {value}
      </p>
      {note ? <p className="m-0 mt-2 text-xs text-[hsl(var(--ui-text-3))]">{note}</p> : null}
    </article>
  );
}
