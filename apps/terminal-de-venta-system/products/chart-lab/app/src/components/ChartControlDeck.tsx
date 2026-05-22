// PRISMA_PEARL_EXECUTIVE_CONTROL_DECK_V1
// PRISMA_THEME_BUTTON_DATA_VALUE_V1
"use client";

import type { LabChartControlState, LabChartControlValue, LabChartRuntimeControl } from "@/prisma-charts/chart-lab-types";

type ChartControlDeckProps = {
  controls: LabChartRuntimeControl[];
  values: LabChartControlState;
  onChange: (controlId: string, value: LabChartControlValue) => void;
  onReset: () => void;
  onResetAll: () => void;
  onCopyConfig: () => void;
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

// PRISMA_CAUSAL_FLOW_PREMIUM_PATCH_V2: stable labels and selectors for Playwright + premium controls.
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

// PRISMA_KNOBS_AUDIT_INJECTION_V2: stable knob selectors for audit, QA, and product hardening.
export function ChartControlDeck({ controls, values, onChange, onCopyConfig, onReset, onResetAll }: ChartControlDeckProps) {
  return (
    <section className="control-deck" aria-label="Runtime chart controls" data-testid="chart-control-deck" data-luxury-ui="pearl-executive" data-control-count={controls.length}>
      <div className="control-deck__toolbar">
        <div>
          <span className="eyebrow">Runtime Controls</span>
          <h3>Control instruments</h3>
        </div>
        <div className="toolbar-actions">
          <button type="button" data-action="copy-current-config" aria-label="Copy Current Config JSON" onClick={onCopyConfig}>Copy Current Config JSON</button>
          <button type="button" data-action="reset-current-chart" aria-label="Reset current chart" onClick={onReset}>Reset current chart</button>
          <button type="button" data-action="reset-all-charts" aria-label="Reset all charts" onClick={onResetAll}>Reset all</button>
        </div>
      </div>

      <div className="control-deck__grid">
        {controls.map((control) => {
          const current = values[control.id] ?? control.defaultValue;
          const disabled = Boolean(control.disabledReason);

          return (
            <label className="runtime-control" key={control.id} data-control-type={control.type} data-control-id={control.id} data-control-label={control.label}>
              <span>{control.label}</span>
              {control.type === "toggle" ? (
                <input
                  {...controlInputProps(control)}
                  type="checkbox"
                  checked={asBoolean(current, Boolean(control.defaultValue))}
                  disabled={disabled}
                  onChange={(event) => onChange(control.id, event.target.checked)}
                />
              ) : null}

              {control.type === "range" || control.type === "numeric" ? (
                <>
                  <input
                    {...controlInputProps(control)}
                    type="range"
                    min={control.min ?? 0}
                    max={control.max ?? 100}
                    step={control.step ?? 1}
                    value={asNumber(current, asNumber(control.defaultValue, 0))}
                    disabled={disabled}
                    onChange={(event) => onChange(control.id, Number(event.target.value))}
                  />
                  <output data-control-id={control.id} data-control-output="value">{asNumber(current, asNumber(control.defaultValue, 0))}</output>
                </>
              ) : null}

              {control.type === "select" ? (
                <select {...controlInputProps(control)} value={asString(current)} disabled={disabled} onChange={(event) => onChange(control.id, event.target.value)}>
                  {(control.options ?? []).map((option) => (
                    <option value={option.value} key={option.value}>{option.label}</option>
                  ))}
                </select>
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
                     data-value={String(option.value)}>
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

              <small data-control-id={control.id} data-control-meta="validation">{control.disabledReason ?? `${control.affectedLayer} · ${control.validation}`}</small>
            </label>
          );
        })}
      </div>
    </section>
  );
}
