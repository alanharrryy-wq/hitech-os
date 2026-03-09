"use client";

import React from "react";
import styles from "../dev-console.module.css";
import { useDevConsole } from "../DevConsoleContext";
import type { DevConsoleFlags } from "../types";

const cls = (name: string) => styles[name] ?? "";

type ToggleRowProps = {
  label: string;
  hint: string;
  value: boolean;
  onToggle: () => void;
};

function ToggleRow({ label, hint, value, onToggle }: ToggleRowProps) {
  return (
    <div className={cls("toggleRow")}>
      <div className={cls("toggleText")}>
        <div className={cls("toggleLabel")}>{label}</div>
        <div className={cls("toggleHint")}>{hint}</div>
      </div>

      <button type="button" className={cls("toggleButton")} onClick={onToggle}>
        {value ? "ON" : "OFF"}
      </button>
    </div>
  );
}

function toggleFlag<K extends keyof DevConsoleFlags>(
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>,
  key: K
) {
  setFlags((prev) => ({ ...prev, [key]: !prev[key] }));
}

export function ConsoleFlagsPanel() {
  const { flags, setFlags, resetFlags, bridgeStatus, runtime } = useDevConsole();

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Runtime flags</div>
        <div className={cls("cardHint")}>
          Persisted, mirrored to document datasets, and ready for any module that wants to subscribe without hard coupling.
        </div>

        <ToggleRow
          label="Grid"
          hint="Visual alignment helper for dense scenes and layout checks."
          value={flags.showGrid}
          onToggle={() => toggleFlag(setFlags, "showGrid")}
        />
        <ToggleRow
          label="Motion"
          hint="Global intent for transitions and animated flourishes."
          value={flags.motionEnabled}
          onToggle={() => toggleFlag(setFlags, "motionEnabled")}
        />
        <ToggleRow
          label="Reduced motion"
          hint="Force calmer behavior when the browser starts sweating."
          value={flags.reducedMotion}
          onToggle={() => toggleFlag(setFlags, "reducedMotion")}
        />
        <ToggleRow
          label="Safe areas"
          hint="Frame boundaries and presentation guards."
          value={flags.showSafeAreas}
          onToggle={() => toggleFlag(setFlags, "showSafeAreas")}
        />
        <ToggleRow
          label="Debug labels"
          hint="Semantic labels for quick provenance tracing."
          value={flags.showDebugLabels}
          onToggle={() => toggleFlag(setFlags, "showDebugLabels")}
        />

        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={resetFlags}>
            Reset Flags
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>Broadcast digest</div>
        <div className={cls("metricGrid")}>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{bridgeStatus.toUpperCase()}</div>
            <div className={cls("metricLabel")}>Bridge</div>
          </div>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{runtime?.enabledLayerIds.length ?? 0}</div>
            <div className={cls("metricLabel")}>Layers</div>
          </div>
          <div className={cls("metricCard")}>
            <div className={cls("metricValue")}>{Object.values(flags).filter(Boolean).length}</div>
            <div className={cls("metricLabel")}>Enabled flags</div>
          </div>
        </div>

        <pre className={cls("codeBox")}>
{JSON.stringify(
  {
    datasets: {
      devConsoleGrid: String(flags.showGrid),
      devConsoleMotion: String(flags.motionEnabled),
      devConsoleReducedMotion: String(flags.reducedMotion),
      devConsoleSafeAreas: String(flags.showSafeAreas),
      devConsoleDebugLabels: String(flags.showDebugLabels)
    },
    event: "hitech:dev-console:flags"
  },
  null,
  2
)}
        </pre>
      </section>
    </div>
  );
}
