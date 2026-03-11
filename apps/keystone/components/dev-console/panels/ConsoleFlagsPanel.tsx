"use client";

import styles from "../dev-console.module.css";
import { useDevConsole } from "../DevConsoleContext";
import type { SceneLookModel, SceneLookModelPatch } from "../look/scene-look-model";

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

function toggleOverlay(
  updateSceneLookModel: (
    patch: SceneLookModelPatch | ((previous: SceneLookModel) => SceneLookModelPatch)
  ) => void,
  key: keyof SceneLookModel["overlays"],
  value: boolean
) {
  if (key === "grid") {
    updateSceneLookModel({ overlays: { grid: !value } });
    return;
  }
  if (key === "safeAreas") {
    updateSceneLookModel({ overlays: { safeAreas: !value } });
    return;
  }
  updateSceneLookModel({ overlays: { debugLabels: !value } });
}

export function ConsoleFlagsPanel() {
  const { flags, sceneLookModel, updateSceneLookModel, resetFlags, bridgeStatus, runtime } = useDevConsole();

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
          onToggle={() => toggleOverlay(updateSceneLookModel, "grid", sceneLookModel.overlays.grid)}
        />
        <ToggleRow
          label="Motion"
          hint="Global intent for transitions and animated flourishes."
          value={flags.motionEnabled}
          onToggle={() => updateSceneLookModel({ motion: sceneLookModel.motion === "on" ? "off" : "on" })}
        />
        <ToggleRow
          label="Reduced motion"
          hint="Force calmer behavior when the browser starts sweating."
          value={flags.reducedMotion}
          onToggle={() =>
            updateSceneLookModel({ motion: sceneLookModel.motion === "reduced" ? "off" : "reduced" })
          }
        />
        <ToggleRow
          label="Safe areas"
          hint="Frame boundaries and presentation guards."
          value={flags.showSafeAreas}
          onToggle={() => toggleOverlay(updateSceneLookModel, "safeAreas", sceneLookModel.overlays.safeAreas)}
        />
        <ToggleRow
          label="Debug labels"
          hint="Semantic labels for quick provenance tracing."
          value={flags.showDebugLabels}
          onToggle={() => toggleOverlay(updateSceneLookModel, "debugLabels", sceneLookModel.overlays.debugLabels)}
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
