import { GlassCard, InsetPanel, cn } from "@hitech/ui-kit";

export interface FeatureCardGridProps {
  readonly features: readonly string[];
  readonly className?: string;
}

export function FeatureCardGrid({ features, className }: FeatureCardGridProps) {
  return (
    <div className={cn("grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3", className)}>
      {features.map((feature, index) => (
        <GlassCard key={feature} className="p-2" tone="default" backdrop="off">
          <InsetPanel
            title={`Capacidad ${String(index + 1).padStart(2, "0")}`}
            description="MOTOR 2 — HITECH OS"
            className="min-h-[112px]"
          >
            <p className="m-0 text-sm leading-6 text-[hsl(var(--ui-text-1))]">{feature}</p>
          </InsetPanel>
        </GlassCard>
      ))}
    </div>
  );
}
