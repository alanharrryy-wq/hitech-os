import type { HTMLAttributes, PropsWithChildren } from "react";

import { GLASS_CARD_LAYER_IDS, LAYER_DATA_ATTR_MAP } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

export interface GlassCardProps extends PropsWithChildren, HTMLAttributes<HTMLDivElement> {
  readonly contentClassName?: string;
}

function joinClassNames(values: readonly (string | undefined | null | false)[]): string {
  return values.filter(Boolean).join(" ");
}

export function GlassCard({ children, className, contentClassName, ...rest }: GlassCardProps): JSX.Element {
  const resolved = useLayerFlags();

  const cardAttrs = {
    [LAYER_DATA_ATTR_MAP["card.innerStroke"]]: resolved.flags["card.innerStroke"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["card.specular"]]: resolved.flags["card.specular"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["card.grain"]]: resolved.flags["card.grain"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["card.blur"]]: resolved.flags["card.blur"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["motion.enabled"]]: resolved.flags["motion.enabled"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["frame.bezel"]]: resolved.flags["frame.bezel"] ? "on" : "off",
  } as const;

  return (
    <article className={joinClassNames(["ui-layer-glass-card", className])} {...cardAttrs} {...rest}>
      {resolved.flags["card.innerStroke"] ? <div className="ui-layer-glass-card__inner-stroke" aria-hidden="true" /> : null}
      {resolved.flags["card.specular"] ? <div className="ui-layer-glass-card__specular" aria-hidden="true" /> : null}
      {resolved.flags["card.grain"] ? <div className="ui-layer-glass-card__grain" aria-hidden="true" /> : null}
      {resolved.flags["frame.bezel"] && GLASS_CARD_LAYER_IDS.length > 0 ? (
        <div className="ui-layer-glass-card__bezel" aria-hidden="true" />
      ) : null}
      <div className={joinClassNames(["ui-layer-glass-card__content", contentClassName])}>{children}</div>
    </article>
  );
}
