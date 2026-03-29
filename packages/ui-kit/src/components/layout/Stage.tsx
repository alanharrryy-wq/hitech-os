"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren } from "react";
import { cn } from "../../lib/cn.js";
import { type FxOverlayOptions, normalizeFxOverlays } from "../../lib/fx.js";
import { mergeLayerFlags, type LayerFlags } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

const stageVariants = cva("stage ui-stage", {
  variants: {
    density: {
      default: "",
      compact: "",
      comfortable: ""
    }
  },
  defaultVariants: {
    density: "default"
  }
});

export interface StageProps
  extends PropsWithChildren,
    HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof stageVariants> {
  readonly fx?: FxOverlayOptions;
  readonly layerOverrides?: Partial<
    Pick<
      LayerFlags,
      | "stage.haze"
      | "stage.vignette"
      | "stage.noise"
      | "stage.scanlines"
      | "stage.horizon"
      | "frame.bezel"
      | "motion.enabled"
    >
  >;
  readonly className?: string;
  readonly children?: React.ReactNode;
}

function onOff(value: boolean): "on" | "off" {
  return value ? "on" : "off";
}

function mapFxToLayerOverrides(fx?: FxOverlayOptions): Partial<LayerFlags> | undefined {
  if (!fx) {
    return undefined;
  }

  const normalized = normalizeFxOverlays(fx);
  return {
    "stage.noise": normalized.noise,
    "stage.scanlines": normalized.scanline,
    "stage.haze": normalized.haze,
    "stage.vignette": normalized.vignette
  };
}

export function Stage({ className, children, density, fx, layerOverrides, ...props }: StageProps) {
  const layerContext = useLayerFlags();
  const merged = mergeLayerFlags(layerContext.flags, {
    ...(mapFxToLayerOverrides(fx) ?? {}),
    ...(layerOverrides ?? {})
  });

  return (
    <div
      className={cn(stageVariants({ density }), className)}
      data-layer-stage-haze={onOff(merged["stage.haze"])}
      data-layer-stage-vignette={onOff(merged["stage.vignette"])}
      data-layer-stage-noise={onOff(merged["stage.noise"])}
      data-layer-stage-scanlines={onOff(merged["stage.scanlines"])}
      data-layer-stage-horizon={onOff(merged["stage.horizon"])}
      data-layer-frame-bezel={onOff(merged["frame.bezel"])}
      data-layer-motion-enabled={onOff(merged["motion.enabled"])}
      {...props}
    >
      <div className="stage-overlays" aria-hidden>
        <div className="noise" aria-hidden="true" />
        <div className="scanlines" aria-hidden="true" />
        <div className="haze" aria-hidden="true" />
        <div className="vignette" aria-hidden="true" />
        <div className="horizon" aria-hidden="true" />
        <div className="frame-bezel" aria-hidden="true" />
      </div>
      <div className="ui-stage__content stage-content">{children}</div>
    </div>
  );
}
