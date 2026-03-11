"use client";

import { useDevConsole } from "../../DevConsoleContext";
import type {
  SceneLookBackground,
  SceneLookCardStyle,
  SceneLookDensity,
  SceneLookMotion,
  SceneLookStageStyle
} from "../../look/scene-look-model";
import styles from "../../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function SelectRow<T extends string>({
  label,
  value,
  options,
  onChange
}: {
  readonly label: string;
  readonly value: T;
  readonly options: readonly T[];
  readonly onChange: (next: T) => void;
}) {
  return (
    <label className={cls("kvItem")}>
      <div className={cls("kvLabel")}>{label}</div>
      <select className={cls("select")} value={value} onChange={(event) => onChange(event.currentTarget.value as T)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function ToggleRow({
  label,
  value,
  onToggle
}: {
  readonly label: string;
  readonly value: boolean;
  readonly onToggle: () => void;
}) {
  return (
    <div className={cls("toggleRow")}>
      <div className={cls("toggleLabel")}>{label}</div>
      <button type="button" className={cls("toggleButton")} onClick={onToggle}>
        {value ? "ON" : "OFF"}
      </button>
    </div>
  );
}

export function ComposeSceneLookPanel() {
  const { sceneLookModel, updateSceneLookModel, replaceSceneLookModel } = useDevConsole();

  return (
    <div className={cls("split")}>
      <section className={cls("card")}>
        <div className={cls("cardTitle")}>SceneLookModel controls</div>
        <div className={cls("cardHint")}>
          ComposeConsole mutates presentation through a single canonical model to avoid state fragmentation.
        </div>

        <div className={cls("kvGrid")}>
          <SelectRow<SceneLookBackground>
            label="Background"
            value={sceneLookModel.background}
            options={["neutral", "gradient", "cinematic"]}
            onChange={(next) => updateSceneLookModel({ background: next })}
          />
          <SelectRow<SceneLookStageStyle>
            label="Stage style"
            value={sceneLookModel.stageStyle}
            options={["default", "cinematic", "minimal"]}
            onChange={(next) => updateSceneLookModel({ stageStyle: next })}
          />
          <SelectRow<SceneLookCardStyle>
            label="Card style"
            value={sceneLookModel.cardStyle}
            options={["default", "glass", "solid"]}
            onChange={(next) => updateSceneLookModel({ cardStyle: next })}
          />
          <SelectRow<SceneLookMotion>
            label="Motion"
            value={sceneLookModel.motion}
            options={["off", "on", "reduced"]}
            onChange={(next) => updateSceneLookModel({ motion: next })}
          />
          <SelectRow<SceneLookDensity>
            label="Density"
            value={sceneLookModel.density}
            options={["comfortable", "compact"]}
            onChange={(next) => updateSceneLookModel({ density: next })}
          />
        </div>

        <ToggleRow
          label="Overlay: Grid"
          value={sceneLookModel.overlays.grid}
          onToggle={() => updateSceneLookModel({ overlays: { grid: !sceneLookModel.overlays.grid } })}
        />
        <ToggleRow
          label="Overlay: Safe Areas"
          value={sceneLookModel.overlays.safeAreas}
          onToggle={() => updateSceneLookModel({ overlays: { safeAreas: !sceneLookModel.overlays.safeAreas } })}
        />
        <ToggleRow
          label="Overlay: Debug Labels"
          value={sceneLookModel.overlays.debugLabels}
          onToggle={() => updateSceneLookModel({ overlays: { debugLabels: !sceneLookModel.overlays.debugLabels } })}
        />

        <ToggleRow
          label="FX: Bloom"
          value={sceneLookModel.visualEffects.bloom}
          onToggle={() => updateSceneLookModel({ visualEffects: { bloom: !sceneLookModel.visualEffects.bloom } })}
        />
        <ToggleRow
          label="FX: Grain"
          value={sceneLookModel.visualEffects.grain}
          onToggle={() => updateSceneLookModel({ visualEffects: { grain: !sceneLookModel.visualEffects.grain } })}
        />
        <ToggleRow
          label="FX: Vignette"
          value={sceneLookModel.visualEffects.vignette}
          onToggle={() =>
            updateSceneLookModel({ visualEffects: { vignette: !sceneLookModel.visualEffects.vignette } })
          }
        />

        <div className={cls("topBarActions")}>
          <button type="button" className={cls("button")} onClick={() => replaceSceneLookModel()}>
            Reset SceneLookModel
          </button>
        </div>
      </section>

      <section className={cls("card")}>
        <div className={cls("cardTitle")}>SceneLookModel snapshot</div>
        <pre className={cls("codeBox")}>{JSON.stringify(sceneLookModel, null, 2)}</pre>
      </section>
    </div>
  );
}
