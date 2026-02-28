import { CANON_LAYER_IDS } from "./layerIds.js";
import { useLayerFlags } from "./useLayerFlags.js";

export interface LayerDebugPanelProps {
  readonly className?: string;
  readonly title?: string;
}

function joinClassNames(values: readonly (string | undefined | null | false)[]): string {
  return values.filter(Boolean).join(" ");
}

export function LayerDebugPanel({ className, title = "Layer Debug" }: LayerDebugPanelProps): JSX.Element | null {
  const resolved = useLayerFlags();

  if (!resolved.debugPanelEnabled) {
    return null;
  }

  return (
    <aside
      className={joinClassNames(["ui-layer-debug-panel", className])}
      data-layer-debug-panel="on"
      data-layer-source={resolved.source}
      data-layer-profile={resolved.profile}
    >
      <header className="ui-layer-debug-panel__header">
        <h3 className="ui-layer-debug-panel__title">{title}</h3>
        <p className="ui-layer-debug-panel__meta">
          source=<strong>{resolved.source}</strong> profile=<strong>{resolved.profile}</strong>
        </p>
      </header>

      <div className="ui-layer-debug-panel__query">
        <div>
          <span>layers</span>
          <code>{resolved.query.layersRaw ?? "(none)"}</code>
        </div>
        <div>
          <span>layerProfile</span>
          <code>{resolved.query.layerProfileRaw ?? "(none)"}</code>
        </div>
        <div>
          <span>debug</span>
          <code>{resolved.query.debugRaw ?? "(none)"}</code>
        </div>
      </div>

      <ul className="ui-layer-debug-panel__list">
        {CANON_LAYER_IDS.map((id) => (
          <li key={id} className="ui-layer-debug-panel__item" data-layer-enabled={resolved.flags[id] ? "on" : "off"}>
            <code>{id}</code>
            <span>{resolved.flags[id] ? "on" : "off"}</span>
          </li>
        ))}
      </ul>

      <footer className="ui-layer-debug-panel__budget">
        <p>
          expensive enabled: <strong>{resolved.budget.expensiveEnabledLayerIds.length}</strong>
        </p>
      </footer>

      {resolved.unknownLayerIds.length > 0 ? (
        <section className="ui-layer-debug-panel__unknown" aria-label="Unknown layer IDs">
          <h4>Unknown layer IDs</h4>
          <ul>
            {resolved.unknownLayerIds.map((unknown) => (
              <li key={unknown}>
                <code>{unknown}</code>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </aside>
  );
}
