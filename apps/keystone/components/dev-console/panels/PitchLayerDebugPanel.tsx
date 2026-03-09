"use client";

import { useMemo } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function formatEntries(record: Readonly<Record<string, string>>): string {
  const entries = Object.entries(record);
  if (entries.length === 0) return "none";
  return entries.map(([key, value]) => `${key}=${value}`).join("\n");
}

export function PitchLayerDebugPanel() {
  const { diagnostics, bridgeStatus, refreshDiagnostics } = useDevConsole();

  const domAttributeCount = diagnostics ? Object.keys(diagnostics.domDataAttributes).length : 0;
  const layerRows = useMemo(() => {
    if (!diagnostics) return [];

    const enabled = new Set(diagnostics.enabledLayerIds);
    const missing = new Set(diagnostics.missingDataAttributes);
    const domAttributes = new Set(Object.keys(diagnostics.domDataAttributes));

    return diagnostics.enabledLayerIds.map((layerId) => {
      const domKey = Object.keys(diagnostics.domDataAttributes).find((key) => key.includes(layerId.replace(/\./g, "-")));
      return {
        layerId,
        requested: enabled.has(layerId) ? "on" : "off",
        domApplied: domKey ? diagnostics.domDataAttributes[domKey] : "0",
        missing: domKey ? "no" : Array.from(missing).some((attr) => attr.includes(layerId.replace(/\./g, "-"))) ? "yes" : "no"
      };
    });
  }, [diagnostics]);

  if (!diagnostics) {
    return (
      <div className={cls("emptyState")}>
        <div className={cls("cardTitle")}>Layer diagnostics waiting for data</div>
        <div className={cls("cardHint")}>
          The bridge is {bridgeStatus}. Trigger a scene validation and this panel will populate with requested,
          resolved, and DOM-applied layer state.
        </div>
        <div>
          <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
            Request diagnostics
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Layer summary</div>
        <div className={cls("metricGrid")}>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{diagnostics.enabledLayerIds.length}</div>
            <div className={cls("metricLabel")}>Enabled</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{domAttributeCount}</div>
            <div className={cls("metricLabel")}>DOM attrs</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{diagnostics.missingDataAttributes.length}</div>
            <div className={cls("metricLabel")}>Missing</div>
          </article>
        </div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Resolved source</div>
            <div className={cls("kvValue")}>{diagnostics.resolved.source}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Profile</div>
            <div className={cls("kvValue")}>{diagnostics.resolved.profile}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Unknown tokens</div>
            <div className={cls("kvValue")}>{diagnostics.unknownTokens.join(", ") || "none"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Ready flag</div>
            <div className={cls("kvValue")}>{diagnostics.sceneReady ?? "unknown"}</div>
          </div>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Layer rows</div>
        <div className={cls("cardHint")}>This slot is now native to the console. Later passes can enrich these rows even more without reviving the old floating panel.</div>
        <div className={cls("list")}>
          {layerRows.length > 0 ? (
            layerRows.map((row) => (
              <div key={row.layerId} className={cls("profileRow")}>
                <div className={cls("kvValue")}>{row.layerId}</div>
                <div className={cls("kvLabel")}>requested={row.requested}</div>
                <div className={cls("kvLabel")}>dom={row.domApplied}</div>
                <div className={cls("kvLabel")}>missing={row.missing}</div>
              </div>
            ))
          ) : (
            <div className={cls("emptyState")}>
              <div className={cls("cardHint")}>No enabled layers were reported by the diagnostics payload.</div>
            </div>
          )}
        </div>
        <pre className={cls("codeBox")}>{formatEntries(diagnostics.domDataAttributes)}</pre>
      </section>
    </div>
  );
}
