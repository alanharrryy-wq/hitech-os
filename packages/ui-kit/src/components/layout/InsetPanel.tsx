import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";

import { INSET_PANEL_LAYER_IDS, LAYER_DATA_ATTR_MAP } from "../../layers/layerIds.js";
import { useLayerFlags } from "../../layers/useLayerFlags.js";

export interface InsetPanelProps extends PropsWithChildren, HTMLAttributes<HTMLDivElement> {
  readonly header?: ReactNode;
  readonly footer?: ReactNode;
}

function joinClassNames(values: readonly (string | undefined | null | false)[]): string {
  return values.filter(Boolean).join(" ");
}

export function InsetPanel({ children, className, header, footer, ...rest }: InsetPanelProps): JSX.Element {
  const resolved = useLayerFlags();

  const insetAttrs = {
    [LAYER_DATA_ATTR_MAP["inset.shadow"]]: resolved.flags["inset.shadow"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["frame.bezel"]]: resolved.flags["frame.bezel"] ? "on" : "off",
    [LAYER_DATA_ATTR_MAP["motion.enabled"]]: resolved.flags["motion.enabled"] ? "on" : "off",
  } as const;

  return (
    <section className={joinClassNames(["ui-layer-inset-panel", className])} {...insetAttrs} {...rest}>
      {resolved.flags["frame.bezel"] && INSET_PANEL_LAYER_IDS.length > 0 ? (
        <div className="ui-layer-inset-panel__bezel" aria-hidden="true" />
      ) : null}
      {resolved.flags["inset.shadow"] ? <div className="ui-layer-inset-panel__shadow" aria-hidden="true" /> : null}

      {header ? <header className="ui-layer-inset-panel__header">{header}</header> : null}
      <div className="ui-layer-inset-panel__content">{children}</div>
      {footer ? <footer className="ui-layer-inset-panel__footer">{footer}</footer> : null}
    </section>
  );
}
