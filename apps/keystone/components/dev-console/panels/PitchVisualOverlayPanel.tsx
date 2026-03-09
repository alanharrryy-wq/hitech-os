"use client";

import { useMemo } from "react";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

export function PitchVisualOverlayPanel() {
  const { flags, diagnostics, bridgeStatus, runtime } = useDevConsole();

  const overlayRows = useMemo(
    () => [
      {
        label: "Grid overlay",
        status: flags.showGrid ? "armed" : "standby",
        hint: "Uses the shared console flag so visual alignment helpers stay decoupled from the shell."
      },
      {
        label: "Safe areas",
        status: flags.showSafeAreas ? "armed" : "standby",
        hint: "Presentation framing guides can subscribe without importing the panel directly."
      },
      {
        label: "Debug labels",
        status: flags.showDebugLabels ? "armed" : "standby",
        hint: "Semantic labels are useful when the scene feels crowded and layer provenance gets fuzzy."
      },
      {
        label: "DOM layer paint",
        status: (diagnostics?.missingDataAttributes.length ?? 0) > 0 ? "attention" : "clean",
        hint: "Derived from diagnostics rather than a separate overlay runtime, so there is one source of truth."
      }
    ],
    [diagnostics?.missingDataAttributes.length, flags.showDebugLabels, flags.showGrid, flags.showSafeAreas]
  );

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Overlay control room</div>
        <div className={cls("cardHint")}>
          This slot is now a first-class console panel. It reflects overlay intent and diagnostics health without
          reviving the old floating visual layer widget.
        </div>

        <div className={cls("metricGrid")}>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{bridgeStatus.toUpperCase()}</div>
            <div className={cls("metricLabel")}>Bridge</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{runtime?.domAttributeCount ?? 0}</div>
            <div className={cls("metricLabel")}>DOM attrs</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{diagnostics?.missingDataAttributes.length ?? 0}</div>
            <div className={cls("metricLabel")}>Missing attrs</div>
          </article>
        </div>

        <div className={cls("list")}>
          {overlayRows.map((row) => (
            <div key={row.label} className={cls("kvItem")}>
              <div className={cls("kvLabel")}>{row.label}</div>
              <div className={cls("kvValue")}>{row.status}</div>
              <div className={cls("cardHint")}>{row.hint}</div>
            </div>
          ))}
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Overlay digest</div>
        <div className={cls("cardHint")}>
          Quick readout of what a future paint layer or guide system should care about.
        </div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Route</div>
            <div className={cls("kvValue")}>{runtime?.route ?? "pending"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Profile</div>
            <div className={cls("kvValue")}>{runtime?.profile ?? "pending"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Scene ready</div>
            <div className={cls("kvValue")}>{runtime?.sceneReady ?? "unknown"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Enabled layers</div>
            <div className={cls("kvValue")}>{runtime?.enabledLayerIds.join(", ") || "none"}</div>
          </div>
        </div>

        <pre className={cls("codeBox")}>
{JSON.stringify(
  {
    overlayFlags: {
      showGrid: flags.showGrid,
      showSafeAreas: flags.showSafeAreas,
      showDebugLabels: flags.showDebugLabels
    },
    runtime: runtime
      ? {
          route: runtime.route,
          profile: runtime.profile,
          domAttributeCount: runtime.domAttributeCount,
          missingAttributeCount: runtime.missingAttributeCount
        }
      : null,
    missing: diagnostics?.missingDataAttributes ?? []
  },
  null,
  2
)}
        </pre>
      </section>
    </div>
  );
}
