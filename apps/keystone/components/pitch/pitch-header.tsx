import { Badge, Separator, cn } from "@hitech/ui-kit";
import type { PitchHeaderModel } from "./types";

export interface PitchHeaderProps {
  readonly model: PitchHeaderModel;
  readonly className?: string;
}

export function PitchHeader({ model, className }: PitchHeaderProps) {
  return (
    <header className={cn("grid gap-2", className)}>
      <div className="flex flex-wrap items-center gap-2">
        {model.eyebrow ? <Badge>{model.eyebrow}</Badge> : null}
        {model.orderLabel ? <Badge tone="accent">{model.orderLabel}</Badge> : null}
      </div>
      <h1 className="m-0 text-2xl font-semibold leading-tight tracking-[-0.02em] text-[hsl(var(--ui-text-1))]">
        {model.title}
      </h1>
      {model.subtitle ? (
        <p className="m-0 text-sm text-[hsl(var(--ui-text-3))]">{model.subtitle}</p>
      ) : null}
      <Separator className="mt-2" />
    </header>
  );
}
