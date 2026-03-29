"use client";

import * as React from "react";
import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";
import { cn } from "../../lib/cn.js";
import { mergeLayerFlags, type LayerFlags } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

export interface InsetPanelProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  readonly title?: ReactNode;
  readonly description?: ReactNode;
  readonly actions?: ReactNode;
  readonly layerOverrides?: Partial<Pick<LayerFlags, "inset.shadow" | "motion.enabled">>;
  readonly className?: string;
  readonly children?: React.ReactNode;
}

function onOff(value: boolean): "on" | "off" {
  return value ? "on" : "off";
}

export function InsetPanel({
  className,
  children,
  title,
  description,
  actions,
  layerOverrides,
  ...props
}: InsetPanelProps) {
  const layerContext = useLayerFlags();
  const merged = mergeLayerFlags(layerContext.flags, layerOverrides);

  return (
    <section
      className={cn("inset ui-inset", className)}
      data-layer-inset-shadow={onOff(merged["inset.shadow"])}
      data-layer-motion-enabled={onOff(merged["motion.enabled"])}
      {...props}
    >
      {title || description || actions ? (
        <header className="mb-3 flex items-start justify-between gap-3">
          <div>
            {title ? (
              <h3 className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-2))]">{title}</h3>
            ) : null}
            {description ? (
              <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-3))]">{description}</p>
            ) : null}
          </div>
          {actions ? <div className="shrink-0">{actions}</div> : null}
        </header>
      ) : null}
      {children}
    </section>
  );
}
