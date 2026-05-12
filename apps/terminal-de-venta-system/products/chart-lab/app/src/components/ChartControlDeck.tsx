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

export function ChartControlDeck({ controls, values, onChange, onCopyConfig, onReset, onResetAll }: ChartControlDeckProps) {
  return (
    <section className="control-deck" aria-label="Runtime chart controls">
      <div className="control-deck__toolbar">
        <div>
          <span className="eyebrow">Runtime Controls</span>
          <h3>Working knobs</h3>
        </div>
        <div className="toolbar-actions">
          <button type="button" onClick={onCopyConfig}>Copy config</button>
          <button type="button" onClick={onReset}>Reset chart</button>
          <button type="button" onClick={onResetAll}>Reset all</button>
        </div>
      </div>

      <div className="control-deck__grid">
        {controls.map((control) => {
          const current = values[control.id] ?? control.defaultValue;
          const disabled = Boolean(control.disabledReason);

          return (
            <label className="runtime-control" key={control.id} data-control-type={control.type}>
              <span>{control.label}</span>
              {control.type === "toggle" ? (
                <input
                  type="checkbox"
                  checked={asBoolean(current, Boolean(control.defaultValue))}
                  disabled={disabled}
                  onChange={(event) => onChange(control.id, event.target.checked)}
                />
              ) : null}

              {control.type === "range" || control.type === "numeric" ? (
                <>
                  <input
                    type="range"
                    min={control.min ?? 0}
                    max={control.max ?? 100}
                    step={control.step ?? 1}
                    value={asNumber(current, asNumber(control.defaultValue, 0))}
                    disabled={disabled}
                    onChange={(event) => onChange(control.id, Number(event.target.value))}
                  />
                  <output>{asNumber(current, asNumber(control.defaultValue, 0))}</output>
                </>
              ) : null}

              {control.type === "select" ? (
                <select value={asString(current)} disabled={disabled} onChange={(event) => onChange(control.id, event.target.value)}>
                  {(control.options ?? []).map((option) => (
                    <option value={option.value} key={option.value}>{option.label}</option>
                  ))}
                </select>
              ) : null}

              {control.type === "segmented" ? (
                <span className="segmented-controls control-segment">
                  {(control.options ?? []).map((option) => (
                    <button
                      type="button"
                      key={option.value}
                      className={asString(current) === option.value ? "is-active" : ""}
                      disabled={disabled}
                      onClick={() => onChange(control.id, option.value)}
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
                  type="search"
                  value={asString(current)}
                  disabled={disabled}
                  placeholder="Filter"
                  onChange={(event) => onChange(control.id, event.target.value)}
                />
              ) : null}

              <small>{control.disabledReason ?? `${control.affectedLayer} · ${control.validation}`}</small>
            </label>
          );
        })}
      </div>
    </section>
  );
}
