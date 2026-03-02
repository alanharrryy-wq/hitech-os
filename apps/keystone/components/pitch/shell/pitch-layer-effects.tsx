"use client";

import { useLayerFlags, cn } from "@hitech/ui-kit";

export interface PitchLayerEffectsProps {
  readonly children: React.ReactNode;
  readonly className?: string;
}

export function PitchLayerEffects({ children, className }: PitchLayerEffectsProps) {
  const { flags } = useLayerFlags();

  return (
    <div
      className={cn(
        "relative",
        flags["motion.enabled"] ? "motion-safe:animate-[pitchRise_280ms_ease-out]" : undefined,
        flags["card.shadowAmbient"] ? "drop-shadow-[0_18px_38px_rgba(2,111,134,0.18)]" : undefined,
        flags["card.specular"] ? "before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:bg-[linear-gradient(120deg,rgba(255,255,255,0.28),transparent)]" : undefined,
        className
      )}
      data-pitch-layer-motion={flags["motion.enabled"] ? "on" : "off"}
      data-pitch-layer-specular={flags["card.specular"] ? "on" : "off"}
      data-pitch-layer-shadow-ambient={flags["card.shadowAmbient"] ? "on" : "off"}
    >
      {children}
    </div>
  );
}
