import { Badge, cn } from "@hitech/ui-kit";
import type { PitchNavigationLink, PitchScreenSlug } from "@hitech/contracts";

export interface PitchRailNavItemProps {
  readonly link: PitchNavigationLink;
  readonly activeSlug?: PitchScreenSlug;
  readonly progressCurrent: number;
  readonly className?: string;
}

function isComplete(order: number, current: number): boolean {
  return order < current;
}

export function PitchRailNavItem({
  link,
  activeSlug,
  progressCurrent,
  className
}: PitchRailNavItemProps) {
  const active = link.slug === activeSlug;
  const complete = isComplete(link.order, progressCurrent);

  return (
    <article
      className={cn(
        "pitch-rail-static-card pitch-focus-ring pitch-glass-card pitch-neon-edge inline-flex min-w-[14rem] flex-col gap-2 rounded-[var(--pitch-radius-md)] p-3",
        active
          ? "border-[rgba(2,167,202,0.55)] shadow-[0_14px_26px_rgba(2,167,202,0.18)]"
          : "hover:-translate-y-[1px] hover:shadow-[0_10px_18px_rgba(2,111,134,0.12)]",
        className
      )}
      aria-current={active ? "page" : undefined}
      aria-disabled="true"
      tabIndex={0}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[color:rgba(4,18,25,0.6)]">
          {link.order.toString().padStart(2, "0")}
        </span>
        {active ? (
          <Badge tone="accent">Current</Badge>
        ) : complete ? (
          <Badge tone="success">Seen</Badge>
        ) : (
          <Badge>Pending</Badge>
        )}
      </div>
      <p className="m-0 text-sm font-semibold leading-5 text-[color:var(--pitch-ink)]">{link.title}</p>
    </article>
  );
}
