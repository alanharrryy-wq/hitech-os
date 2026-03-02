"use client";

import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren } from "react";
import { cn } from "../../lib/cn.js";
import { mergeLayerFlags, type LayerFlags } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

const glassCardVariants = cva("card ui-glass-card ui-hitech-material", {
  variants: {
    backdrop: {
      off: "",
      soft: "",
      medium: ""
    },
    tone: {
      default: "",
      muted: "bg-[hsl(var(--ui-surface-2))]",
      raised: "shadow-[var(--ui-shadow-2)]"
    }
  },
  defaultVariants: {
    backdrop: "off",
    tone: "default"
  }
});

export interface GlassCardProps
  extends PropsWithChildren,
    HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof glassCardVariants> {
  readonly layerOverrides?: Partial<
    Pick<
      LayerFlags,
      | "card.blur"
      | "card.innerStroke"
      | "card.specular"
      | "card.grain"
      | "card.shadowAmbient"
      | "motion.enabled"
    >
  >;
}

function onOff(value: boolean): "on" | "off" {
  return value ? "on" : "off";
}

export function GlassCard({
  className,
  children,
  backdrop,
  tone,
  layerOverrides,
  ...props
}: GlassCardProps) {
  const layerContext = useLayerFlags();
  const merged = mergeLayerFlags(layerContext.flags, layerOverrides);

  return (
    <div
      className={cn(glassCardVariants({ backdrop, tone }), className)}
      data-backdrop={backdrop}
      data-layer-card-blur={onOff(merged["card.blur"])}
      data-layer-card-inner-stroke={onOff(merged["card.innerStroke"])}
      data-layer-card-specular={onOff(merged["card.specular"])}
      data-layer-card-grain={onOff(merged["card.grain"])}
      data-layer-card-shadow-ambient={onOff(merged["card.shadowAmbient"])}
      data-layer-motion-enabled={onOff(merged["motion.enabled"])}
      {...props}
    >
      {children}
    </div>
  );
}
