"use client";

import type { LabChartRenderProps } from "../chart-lab-types";

export function ExampleFutureChart({ entry, density, size }: LabChartRenderProps) {
  return (
    <section className={`future-chart future-chart--${density} future-chart--${size}`} aria-label={entry.title}>
      <div className="future-chart__rail" aria-hidden="true">
        <span />
        <span />
        <span />
        <span />
      </div>
      <div>
        <p>{entry.shortName}</p>
        <h3>{entry.title}</h3>
        <strong>Registered extension pattern</strong>
        <small>
          Add one component, one mock provider, one registry entry, and optionally one visual recipe. The lab shell does not need to change.
        </small>
      </div>
    </section>
  );
}
