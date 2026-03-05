import type { HTMLAttributes, PropsWithChildren, ReactElement } from "react";

import { LayerDebugPanel } from "../../layers/LayerDebugPanel.js";
import { LAYER_DATA_ATTR_MAP, STAGE_LAYER_IDS } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

export interface StageProps extends PropsWithChildren, HTMLAttributes<HTMLDivElement> {
  readonly showDebugPanel?: boolean;
  readonly contentClassName?: string;
}

function joinClassNames(values: readonly (string | undefined | null | false)[]): string {
  return values.filter(Boolean).join(" ");
}

export function Stage({
  children,
  className,
  contentClassName,
  showDebugPanel = true,
  ...rest
}: StageProps): ReactElement {
  const resolved = useLayerFlags();

  const stageAttrs = {
    [LAYER_DATA_ATTR_MAP["stage.noise"]]: resolved.flags["stage.noise"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["stage.scanlines"]]: resolved.flags["stage.scanlines"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["stage.glow"]]: resolved.flags["stage.glow"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["motion.enabled"]]: resolved.flags["motion.enabled"] ? "on" : "off"
  } as const;

  return (
    <section className={joinClassNames(["ui-layer-stage", className])} {...stageAttrs} {...rest}>
      <div className="ui-layer-stage__overlay" aria-hidden="true">
        {resolved.flags["stage.noise"] ? (
          <div className="ui-layer-stage__noise" data-layer-node="stage.noise" />
        ) : null}
        {resolved.flags["stage.scanlines"] ? (
          <div className="ui-layer-stage__scanlines" data-layer-node="stage.scanlines" />
        ) : null}
        {resolved.flags["stage.glow"] ? (
          <div className="ui-layer-stage__glow" data-layer-node="stage.glow" />
        ) : null}
      </div>

      <div className={joinClassNames(["ui-layer-stage__content", contentClassName])}>
        {children}
      </div>

      {showDebugPanel && STAGE_LAYER_IDS.length > 0 ? <LayerDebugPanel /> : null}
    </section>
  );
}
