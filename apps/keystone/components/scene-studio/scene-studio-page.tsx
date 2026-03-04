"use client";

import { useState } from "react";
import { SceneStudioTimelineTab } from "../pitch-engine/timeline/scene-studio-timeline-tab";
import type { SceneStudioSceneRef } from "../pitch-engine/types";
import { SceneStudioHelpPanel } from "./scene-studio-help-panel";

export interface SceneStudioPageProps {
  readonly scenes: SceneStudioSceneRef[];
}

export function SceneStudioPage({ scenes }: SceneStudioPageProps) {
  const [tab, setTab] = useState<"scenes" | "timeline">("scenes");

  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 py-6 text-slate-100">
      <header className="mb-4 rounded-lg border border-slate-700 bg-slate-950/40 p-4">
        <p className="keystone-kicker">Scene Studio</p>
        <h1 className="text-2xl font-semibold">Studio + Timeline Tab</h1>

        <div className="mt-3 flex gap-2">
          <button
            className={`rounded px-3 py-1 text-xs font-semibold ${
              tab === "scenes" ? "bg-cyan-700 text-white" : "bg-slate-800 text-slate-300"
            }`}
            type="button"
            onClick={() => {
              setTab("scenes");
            }}
          >
            Scenes
          </button>

          <button
            className={`rounded px-3 py-1 text-xs font-semibold ${
              tab === "timeline" ? "bg-cyan-700 text-white" : "bg-slate-800 text-slate-300"
            }`}
            type="button"
            onClick={() => {
              setTab("timeline");
            }}
          >
            Timeline
          </button>
        </div>
      </header>

      <div className="grid gap-4 xl:grid-cols-[3fr,1fr]">
        <main className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
          {tab === "scenes" ? (
            <>
              <h2 className="text-lg font-semibold text-slate-100">Scenes</h2>
              <ul className="m-0 mt-3 grid gap-2 list-none p-0 md:grid-cols-2">
                {scenes.map((scene) => (
                  <li key={scene.id} className="rounded border border-slate-800 bg-slate-900/40 p-3">
                    <p className="m-0 text-sm font-semibold text-slate-100">{scene.name}</p>
                    <p className="m-0 text-xs text-slate-400">{scene.route}</p>
                    <p className="mt-1 text-xs text-slate-300">{scene.summary}</p>
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <>
              <h2 className="text-lg font-semibold text-slate-100">Timeline</h2>
              <p className="text-xs text-slate-400">
                Timeline tab uses the same Scene Studio scene list as source-of-truth.
              </p>
              <SceneStudioTimelineTab scenes={scenes} />
            </>
          )}
        </main>

        <SceneStudioHelpPanel />
      </div>
    </div>
  );
}
