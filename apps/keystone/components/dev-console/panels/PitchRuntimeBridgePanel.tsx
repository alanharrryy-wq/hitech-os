"use client";

import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

export function PitchRuntimeBridgePanel() {
  const { bridgeStatus, runtime, diagnostics, refreshDiagnostics, lastDiagnosticsAt } = useDevConsole();

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Bridge status</div>
        <div className={cls("metricGrid")}>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{bridgeStatus.toUpperCase()}</div>
            <div className={cls("metricLabel")}>Heartbeat</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{runtime?.enabledLayerIds.length ?? 0}</div>
            <div className={cls("metricLabel")}>Layers seen</div>
          </article>
          <article className={cls("metricCard")}>
            <div className={cls("metricValue")}>{runtime?.domAttributeCount ?? 0}</div>
            <div className={cls("metricLabel")}>DOM attrs</div>
          </article>
        </div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Route</div>
            <div className={cls("kvValue")}>{runtime?.route ?? "pending"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Query</div>
            <div className={cls("kvValue")}>{runtime?.query || "none"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Scene ready</div>
            <div className={cls("kvValue")}>{runtime?.sceneReady ?? "unknown"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Last diagnostics</div>
            <div className={cls("kvValue")}>{lastDiagnosticsAt ?? "none yet"}</div>
          </div>
        </div>

        <div>
          <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
            Ping bridge
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Raw payload</div>
        <div className={cls("cardHint")}>No more empty room. This panel now exposes the actual snapshot the console is seeing.</div>
        <pre className={cls("codeBox")}>{JSON.stringify({ bridgeStatus, runtime, diagnostics }, null, 2)}</pre>
      </section>
    </div>
  );
}
