"use client";

import { useMemo } from "react";
import { usePitchEngineStore } from "./state/use-pitch-engine-store";

const MODE_OPTIONS = ["off", "lite", "full", "debug"] as const;

export function CapabilityPanel() {
  const capability = usePitchEngineStore((state) => state.capabilityStatus);
  const updateCapabilityMode = usePitchEngineStore((state) => state.updateCapabilityMode);
  const reducedMotionApplied = usePitchEngineStore((state) => state.reducedMotionApplied);

  const degradeText = useMemo(
    () => (capability.degradeReasons.length > 0 ? capability.degradeReasons.join(", ") : "none"),
    [capability.degradeReasons]
  );

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-2">
        <p className="keystone-kicker">Capabilities</p>
        <h2 className="text-lg font-semibold text-slate-100">Requested vs applied mode</h2>
      </header>

      {reducedMotionApplied ? (
        <div className="mb-3 rounded border border-amber-600 bg-amber-900/30 px-2 py-1 text-xs text-amber-200">
          Reduced motion applied: preview jumps directly to final state for safe diagnostics.
        </div>
      ) : null}

      <div className="grid gap-2 md:grid-cols-2">
        <label className="grid gap-1 text-xs text-slate-300">
          Requested mode
          <select
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={capability.requestedMode}
            onChange={(event) => {
              updateCapabilityMode(event.target.value as "off" | "lite" | "full" | "debug", {
                debug: capability.debugTokenPresent
              });
            }}
          >
            {MODE_OPTIONS.map((mode) => (
              <option key={mode} value={mode}>
                {mode}
              </option>
            ))}
          </select>
        </label>

        <div className="rounded border border-slate-800 bg-slate-900/40 p-2 text-xs text-slate-300">
          <p className="m-0">Applied mode: {capability.appliedMode}</p>
          <p className="m-0">Degrade reasons: {degradeText}</p>
          <p className="m-0">Route allowed: {String(capability.isRouteAllowed)}</p>
          <p className="m-0">API allowed: {String(capability.isApiAllowed)}</p>
        </div>
      </div>
    </section>
  );
}
