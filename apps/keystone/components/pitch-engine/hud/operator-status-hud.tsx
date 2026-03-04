"use client";

import { useEffect } from "react";
import { fetchOperatorStatus } from "../api-client";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";

export function OperatorStatusHud() {
  const hud = usePitchEngineStore((state) => state.operatorHud);
  const setOperatorHud = usePitchEngineStore((state) => state.setOperatorHud);

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const next = await fetchOperatorStatus();
        if (active) {
          setOperatorHud(next);
        }
      } catch {
        // Keep stale status.
      }
    };

    void run();
    const id = window.setInterval(() => {
      void run();
    }, 10000);

    return () => {
      active = false;
      window.clearInterval(id);
    };
  }, [setOperatorHud]);

  return (
    <aside className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header>
        <p className="keystone-kicker">Operator Status HUD</p>
        <h2 className="text-lg font-semibold text-slate-100">Server / run health</h2>
      </header>

      <dl className="mt-3 grid gap-2 text-xs text-slate-300">
        <div className="rounded border border-slate-800 p-2">
          <dt className="text-slate-400">server</dt>
          <dd className="m-0 font-semibold text-slate-100">{hud.serverStatus}</dd>
        </div>
        <div className="rounded border border-slate-800 p-2">
          <dt className="text-slate-400">last run</dt>
          <dd className="m-0 font-semibold text-slate-100">{hud.lastRunStatus}</dd>
          <dd className="m-0 text-slate-400">{hud.lastRunPath ?? "n/a"}</dd>
        </div>
        <div className="rounded border border-slate-800 p-2">
          <dt className="text-slate-400">last artifact runId</dt>
          <dd className="m-0 font-semibold text-slate-100">{hud.lastArtifactRunId ?? "n/a"}</dd>
        </div>
        <div className="rounded border border-slate-800 p-2">
          <dt className="text-slate-400">last error tail</dt>
          <dd className="m-0 whitespace-pre-wrap text-rose-300">{hud.lastErrorTail ?? "none"}</dd>
        </div>
      </dl>
    </aside>
  );
}
