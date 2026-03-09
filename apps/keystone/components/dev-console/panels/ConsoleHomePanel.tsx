"use client";

import { useMemo } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useDevConsole } from "../DevConsoleContext";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function formatList(values: readonly string[], fallback: string): string {
  return values.length > 0 ? values.join(", ") : fallback;
}

function formatTimestamp(value: string | null): string {
  if (!value) return "none yet";

  try {
    return new Date(value).toLocaleString("en-US", {
      hour12: false,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  } catch {
    return value;
  }
}

export function ConsoleHomePanel() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { bindings, bridgeStatus, runtime, diagnostics, lastDiagnosticsAt, refreshDiagnostics } = useDevConsole();

  const query = searchParams.toString();
  const currentRoute = `${pathname ?? "/"}${query ? `?${query}` : ""}`;

  const metrics = useMemo(
    () => [
      { label: "Bridge", value: bridgeStatus.toUpperCase() },
      { label: "Enabled layers", value: String(runtime?.enabledLayerIds.length ?? 0) },
      { label: "Missing attrs", value: String(runtime?.missingAttributeCount ?? 0) }
    ],
    [bridgeStatus, runtime]
  );

  const bindingReady = bindings.sceneStudio ? "Connected" : "Missing";
  const requestedRoute = diagnostics ? `${diagnostics.route}${diagnostics.query}` : currentRoute;

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Control Room</div>
        <div className={cls("cardHint")}>
          Single console mode is mounted. This card tracks the real route, bridge pulse, editor binding, and current
          diagnostics health.
        </div>

        <div className={cls("metricGrid")}>
          {metrics.map((metric) => (
            <article key={metric.label} className={cls("metricCard")}>
              <div className={cls("metricValue")}>{metric.value}</div>
              <div className={cls("metricLabel")}>{metric.label}</div>
            </article>
          ))}
        </div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Current route</div>
            <div className={cls("kvValue")}>{currentRoute}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Requested route</div>
            <div className={cls("kvValue")}>{requestedRoute}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Scene editor binding</div>
            <div className={cls("kvValue")}>{bindingReady}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Scene ready</div>
            <div className={cls("kvValue")}>{runtime?.sceneReady ?? "unknown"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Layer source</div>
            <div className={cls("kvValue")}>{runtime?.source ?? "pending"}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Profile</div>
            <div className={cls("kvValue")}>{runtime?.profile ?? "pending"}</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
            Refresh diagnostics
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Snapshot digest</div>
        <div className={cls("cardHint")}>Useful when the console feels pelón and you need to know whether data is missing or simply late.</div>

        <div className={cls("kvGrid")}>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Last diagnostics</div>
            <div className={cls("kvValue")}>{formatTimestamp(lastDiagnosticsAt)}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Enabled layers</div>
            <div className={cls("kvValue")}>{formatList(runtime?.enabledLayerIds ?? [], "none")}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Unknown tokens</div>
            <div className={cls("kvValue")}>{formatList(diagnostics?.unknownTokens ?? [], "none")}</div>
          </div>
          <div className={cls("kvItem")}>
            <div className={cls("kvLabel")}>Missing DOM attrs</div>
            <div className={cls("kvValue")}>{formatList(diagnostics?.missingDataAttributes ?? [], "none")}</div>
          </div>
        </div>

        <pre className={cls("codeBox")}>
{[
  "dev-console.status",
  `bridge=${bridgeStatus}`,
  `route=${currentRoute}`,
  `binding=${bindingReady}`,
  `ready=${runtime?.sceneReady ?? "unknown"}`,
  `enabled=[${(runtime?.enabledLayerIds ?? []).join(", ")}]`,
  `missing=[${(diagnostics?.missingDataAttributes ?? []).join(", ")}]`
].join("\n")}
        </pre>
      </section>
    </div>
  );
}
