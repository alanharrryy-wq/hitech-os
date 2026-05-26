// PRISMA_CHART_LAB_POWER_STUDIO_V3_FINAL_INFRASTRUCTURE
// PRISMA_CHART_LAB_POWER_STUDIO_CONTROL_DECK_V1
"use client";

import type { ReactNode } from "react";
import type { LabChartControlState, LabChartControlValue, LabChartRuntimeControl } from "@/prisma-charts/chart-lab-types";

export type PowerStudioTab = "visual" | "motion" | "interaction" | "labels" | "data" | "advanced" | "code";

type ChartControlDeckProps = {
  controls: LabChartRuntimeControl[];
  values: LabChartControlState;
  activeTab?: PowerStudioTab;
  overridesCount?: number;
  codePanel?: ReactNode;
  onChange: (controlId: string, value: LabChartControlValue) => void;
  onReset: () => void;
  onResetAll: () => void;
  onCopyConfig: () => void;
};

const tabMeta: Record<PowerStudioTab, { label: string; intro: string }> = {
  visual: {
    label: "Visual",
    intro: "Paletas, intensidad, contraste, glow, densidad y apariencia general. Aquí se pinta el barrio bonito, no el Excel con corbata."
  },
  motion: {
    label: "Motion",
    intro: "Entrada, update, easing, sweep, pulse y velocidad. Movimiento sabroso sin convertirlo en feria patronal."
  },
  interaction: {
    label: "Interaction",
    intro: "Tooltips, hover spotlight, click isolate, zoom, brush, severity y guided behavior. La gráfica deja de ser postal y se vuelve juguete fino."
  },
  labels: {
    label: "Labels",
    intro: "Etiquetas, callouts, evidencia y legibilidad. Que informe sin tapizar la gráfica como poste de tianguis."
  },
  data: {
    label: "Data Feel",
    intro: "Scenario, confidence, freshness, hotspots y cómo se comunica el estado de datos sin alterar la verdad operativa."
  },
  advanced: {
    label: "Advanced",
    intro: "Controles técnicos, overrides y knobs de riesgo medio/alto. La carnicería fina va aquí, con letrero y cuchillo limpio."
  },
  code: {
    label: "Code",
    intro: "Direct ECharts patches layered after Visual Layers and before the final visibility guard."
  }
};

function asString(value: LabChartControlValue | undefined) {
  return typeof value === "string" ? value : "";
}

function asNumber(value: LabChartControlValue | undefined, fallback: number) {
  return typeof value === "number" ? value : fallback;
}

function asBoolean(value: LabChartControlValue | undefined, fallback: boolean) {
  return typeof value === "boolean" ? value : fallback;
}

function asStringArray(value: LabChartControlValue | undefined) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function controlDomId(controlId: string) {
  return `chart-control-${controlId.replace(/[^a-zA-Z0-9_-]/g, "-")}`;
}

function controlInputProps(control: LabChartRuntimeControl) {
  return {
    id: controlDomId(control.id),
    name: control.id,
    "aria-label": control.label,
    "data-control-id": control.id,
    "data-control-label": control.label,
    "data-control-type": control.type
  };
}

function inferTab(control: LabChartRuntimeControl): PowerStudioTab {
  if (control.powerTab) return control.powerTab;
  const haystack = `${control.id} ${control.label} ${control.affectedLayer} ${control.affectedOptionPath ?? ""} ${control.affectedDataTransform ?? ""}`.toLowerCase();
  if (/theme|palette|visual|intensity|contrast|glow|opacity|width|density|grid|ceiling|radius|color|style|heat/.test(haystack)) return "visual";
  if (/motion|animation|duration|easing|sweep|pulse|replay|morph/.test(haystack)) return "motion";
  if (/tooltip|hover|click|brush|zoom|stage|severity|focus|evidence|queue|legend|interaction|select/.test(haystack)) return "interaction";
  if (/label|callout|cell number|detail/.test(haystack)) return "labels";
  if (/data|scenario|confidence|fresh|stale|offline|floor|zone|hotspot|pressure|mock/.test(haystack)) return "data";
  return "advanced";
}

function controlDescription(control: LabChartRuntimeControl) {
  const path = control.affectedOptionPath ?? control.affectedDataTransform ?? control.affectedLayer;
  return `${path} · ${control.validation}`;
}

function rangeZone(control: LabChartRuntimeControl, value: number) {
  const min = control.min ?? 0;
  const max = control.max ?? 100;
  const span = Math.max(1, max - min);
  const ratio = (value - min) / span;
  if (ratio >= 0.82) return "insane";
  if (ratio >= 0.58) return "wild";
  return "safe";
}

function zonePercent(control: LabChartRuntimeControl, value: number) {
  const min = control.min ?? 0;
  const max = control.max ?? 100;
  return Math.max(0, Math.min(100, ((value - min) / Math.max(1, max - min)) * 100));
}

function selectedOptionLabel(control: LabChartRuntimeControl, value: LabChartControlValue | undefined) {
  if (typeof value !== "string") return "";
  return control.options?.find((option) => option.value === value)?.label ?? value;
}

function controlCurrentValue(control: LabChartRuntimeControl, values: LabChartControlState) {
  return values[control.id] ?? control.defaultValue;
}

export function ChartControlDeck({ controls, values, activeTab = "visual", overridesCount, codePanel, onChange, onCopyConfig, onReset, onResetAll }: ChartControlDeckProps) {
  const visibleControls = activeTab === "code" ? [] : controls.filter((control) => inferTab(control) === activeTab);
  const meta = tabMeta[activeTab];

  return (
    <section
      className="control-deck control-deck--power-studio"
      aria-label="Runtime chart controls"
      data-testid="chart-control-deck"
      data-power-tab={activeTab}
      data-control-count={controls.length}
      data-visible-control-count={visibleControls.length}
      data-overrides-count={overridesCount}
    >
      <div className="control-deck__toolbar control-deck__toolbar--compact">
        <div>
          <span className="eyebrow">{meta.label}</span>
          <h3>Control Summary · {visibleControls.length} live instruments</h3>
          <p>{meta.intro}</p>
        </div>
        <div className="toolbar-actions">
          <button type="button" data-action="copy-current-config" aria-label="Copy Current Config JSON" onClick={onCopyConfig}>Copy Current Config JSON</button>
          <button type="button" data-action="reset-current-chart" aria-label="Reset current chart" onClick={onReset}>Reset chart</button>
          <button type="button" data-action="reset-all-charts" aria-label="Reset all charts" onClick={onResetAll}>Reset all</button>
        </div>
      </div>

      {activeTab === "code" ? (
        <div className="code-drawers-panel" data-power-tab="code" data-control-count={controls.length} data-overrides-count={overridesCount}>
          {codePanel ?? (
            <div className="empty-power-tab">
              <strong>No Code drawers are available for this chart yet.</strong>
              <p>The visual controls stay active; direct patches remain disabled until a drawer is configured.</p>
            </div>
          )}
        </div>
      ) : visibleControls.length ? (
        <div className="control-grid control-grid--side-rail">
          {visibleControls.map((control) => {
            const current = controlCurrentValue(control, values);
            const disabled = Boolean(control.disabledReason);
            const currentNumber = asNumber(current, asNumber(control.defaultValue, 0));
            const zone = control.type === "range" || control.type === "numeric" ? rangeZone(control, currentNumber) : undefined;

            return (
              <label className={`control-card control-card--${control.type} ${disabled ? "is-disabled" : ""}`} key={control.id} data-control-risk={control.risk} data-control-zone={zone}>
                <span className="control-card__head">
                  <span>
                    <span className="control-card__title">{control.label}</span>
                    <small>{control.risk} risk · reset: {control.resetBehavior}</small>
                  </span>
                  {zone ? <strong className={`range-zone range-zone--${zone}`}>{zone}</strong> : null}
                </span>

                {control.type === "toggle" ? (
                  <span className="toggle-row">
                    <input
                      {...controlInputProps(control)}
                      type="checkbox"
                      checked={asBoolean(current, asBoolean(control.defaultValue, false))}
                      disabled={disabled}
                      onChange={(event) => onChange(control.id, event.target.checked)}
                    />
                    <span>{asBoolean(current, asBoolean(control.defaultValue, false)) ? "Enabled" : "Disabled"}</span>
                  </span>
                ) : null}

                {control.type === "range" || control.type === "numeric" ? (
                  <span className="range-control-shell">
                    <span className="range-meter" aria-hidden="true"><i style={{ width: `${zonePercent(control, currentNumber)}%` }} /></span>
                    <input
                      {...controlInputProps(control)}
                      type="range"
                      min={control.min ?? 0}
                      max={control.max ?? 100}
                      step={control.step ?? 1}
                      value={currentNumber}
                      disabled={disabled}
                      onChange={(event) => onChange(control.id, Number(event.target.value))}
                    />
                    <span className="range-row">
                      <small>{control.min ?? 0}</small>
                      <output data-control-id={control.id} data-control-output="value">{currentNumber}</output>
                      <small>{control.max ?? 100}</small>
                    </span>
                  </span>
                ) : null}

                {control.type === "select" ? (
                  <span className="select-shell">
                    <select {...controlInputProps(control)} value={asString(current)} disabled={disabled} onChange={(event) => onChange(control.id, event.target.value)}>
                      {(control.options ?? []).map((option) => (
                        <option value={option.value} key={option.value}>{option.label}</option>
                      ))}
                    </select>
                    <small>{selectedOptionLabel(control, current)}</small>
                  </span>
                ) : null}

                {control.type === "segmented" ? (
                  <span className="segmented-controls control-segment">
                    {(control.options ?? []).map((option) => (
                      <button
                        aria-pressed={asString(current) === option.value}
                        aria-label={`${control.label}: ${option.label}`}
                        data-control-option={option.value}
                        data-control-id={control.id}
                        type="button"
                        key={option.value}
                        className={asString(current) === option.value ? "is-active" : ""}
                        disabled={disabled}
                        onClick={() => onChange(control.id, option.value)}
                        data-value={String(option.value)}
                      >
                        {option.label}
                      </button>
                    ))}
                  </span>
                ) : null}

                {control.type === "chip-group" ? (
                  <span className="chip-group">
                    {(control.options ?? []).map((option) => {
                      const selected = asStringArray(current).includes(option.value);
                      return (
                        <button
                          aria-pressed={selected}
                          aria-label={`${control.label}: ${option.label}`}
                          data-control-option={option.value}
                          data-control-id={control.id}
                          type="button"
                          key={option.value}
                          className={selected ? "is-active" : ""}
                          disabled={disabled}
                          onClick={() => {
                            const currentValues = asStringArray(current);
                            const next = selected ? currentValues.filter((item) => item !== option.value) : [...currentValues, option.value];
                            onChange(control.id, next.length ? next : [option.value]);
                          }}
                        >
                          {option.label}
                        </button>
                      );
                    })}
                  </span>
                ) : null}

                {control.type === "search" ? (
                  <input
                    {...controlInputProps(control)}
                    type="search"
                    value={asString(current)}
                    disabled={disabled}
                    placeholder="Filter"
                    onChange={(event) => onChange(control.id, event.target.value)}
                  />
                ) : null}

                <small data-control-id={control.id} data-control-meta="validation">{control.disabledReason ?? controlDescription(control)}</small>
              </label>
            );
          })}
        </div>
      ) : (
        <div className="empty-power-tab">
          <strong>No {meta.label.toLowerCase()} controls for this chart yet.</strong>
          <p>Nothing fake is shown. If a knob does not map to this chart, it stays out of the way.</p>
        </div>
      )}
    </section>
  );
}
