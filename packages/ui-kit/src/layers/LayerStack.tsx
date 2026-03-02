"use client";

import type { PropsWithChildren } from "react";
import { LayerDebugPanel } from "./LayerDebugPanel.js";
import { LayerFlagsProvider } from "./LayerFlagsProvider.js";
import { shouldRenderLayerDebugPanel, type ResolvedLayerFlags } from "./resolveLayerFlags.js";

export interface LayerStackProps extends PropsWithChildren {
  readonly flags: ResolvedLayerFlags;
  readonly includeDebugPanel?: boolean;
}

export function LayerStack({ flags, includeDebugPanel = true, children }: LayerStackProps) {
  const showDebugPanel = includeDebugPanel && shouldRenderLayerDebugPanel(flags);

  return (
    <LayerFlagsProvider initialResolved={flags}>
      {children}
      {showDebugPanel ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
