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
  const { flags, setFlags, resetFlags } = useDevConsole();

  return (
    <div className={cls("card")}>
      <div className={cls("cardTitle")}>Runtime Flags</div>
      <div className={cls("cardHint")}>
        These flags are persisted and broadcast via custom events so future modules can subscribe without coupling.
      </div>

      <ToggleRow
        label="Grid"
        hint="Visual alignment helper for slide composition."
        value={flags.showGrid}
        onToggle={() => toggleFlag(setFlags, "showGrid")}
      />

      <ToggleRow
        label="Motion"
        hint="Global motion intent. Modules can honor this to reduce GPU churn."
        value={flags.motionEnabled}
        onToggle={() => toggleFlag(setFlags, "motionEnabled")}
      />

      <ToggleRow
        label="Reduced Motion"
        hint="Force calmer behavior for heavy scenes and perf-sensitive sessions."
        value={flags.reducedMotion}
        onToggle={() => toggleFlag(setFlags, "reducedMotion")}
      />

      <ToggleRow
        label="Safe Areas"
        hint="Overlay margins / framing boundaries for presentation polish."
        value={flags.showSafeAreas}
        onToggle={() => toggleFlag(setFlags, "showSafeAreas")}
      />

      <ToggleRow
        label="Debug Labels"
        hint="Show semantic markers for components, layers, and slots."
        value={flags.showDebugLabels}
        onToggle={() => toggleFlag(setFlags, "showDebugLabels")}
      />

      <div className={cls("topBarActions")}>
        <button type="button" className={cls("button")} onClick={resetFlags}>
          Reset Flags
        </button>
      </div>
    </div>
  );
}
