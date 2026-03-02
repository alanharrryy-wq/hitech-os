import Link from "next/link";
import { Badge, cn } from "@hitech/ui-kit";
import type { PitchRouteInsight } from "../../../lib/pitch/deck-view-model";
import { PitchIconByName, type PitchIconName } from "../visuals/pitch-icon-library";

const ICON_BY_SLUG: Record<PitchRouteInsight["slug"], PitchIconName> = {
  "01-double-engine": "Engine",
  "02-industrial-flow": "Flow",
  "03-hitech-os": "Chip",
  "04-valuation": "Value",
  "05-inventory-foundation": "Vault",
  "06-shipments-receiving": "Truck"
};

function emphasisClass(emphasis: PitchRouteInsight["emphasis"]): string {
  if (emphasis === "industrial") {
    return "border-[rgba(171,123,38,0.32)] bg-[linear-gradient(145deg,rgba(171,123,38,0.14),rgba(255,255,255,0.7))]";
  }

  if (emphasis === "software") {
    return "border-[rgba(2,167,202,0.36)] bg-[linear-gradient(145deg,rgba(2,167,202,0.16),rgba(255,255,255,0.72))]";
  }

  if (emphasis === "operations") {
    return "border-[rgba(2,111,134,0.34)] bg-[linear-gradient(145deg,rgba(2,111,134,0.14),rgba(255,255,255,0.73))]";
  }

  return "border-[rgba(2,111,134,0.3)] bg-[linear-gradient(145deg,rgba(171,123,38,0.13),rgba(2,167,202,0.14),rgba(255,255,255,0.72))]";
}

export interface PitchRouteCardProps {
  readonly route: PitchRouteInsight;
  readonly className?: string;
}

export function PitchRouteCard({ route, className }: PitchRouteCardProps) {
  const iconName = ICON_BY_SLUG[route.slug];

  return (
    <Link
      href={route.href}
      className={cn(
        "pitch-focus-ring pitch-glass-card pitch-neon-edge group grid gap-3 rounded-[var(--pitch-radius-lg)] p-4 no-underline transition-transform duration-200 hover:-translate-y-[2px]",
        emphasisClass(route.emphasis),
        className
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.1em] text-[color:rgba(4,18,25,0.66)]">
          <PitchIconByName name={iconName} className="h-4 w-4" />
          {route.routeBadge}
        </span>
        {route.recommended ? <Badge tone="success">Investor path</Badge> : <Badge>{route.order}</Badge>}
      </div>

      <h2 className="m-0 text-base font-semibold leading-6 text-[color:var(--pitch-ink)]">{route.title}</h2>

      <div className="grid gap-2 text-sm text-[color:rgba(4,18,25,0.74)]">
        <p className="m-0">{route.intent}</p>
        <p className="m-0 rounded-md border border-[rgba(2,111,134,0.2)] bg-[rgba(255,255,255,0.68)] px-2 py-1 text-xs font-medium">
          Investor learns: {route.investorLearns}
        </p>
      </div>
    </Link>
  );
}
