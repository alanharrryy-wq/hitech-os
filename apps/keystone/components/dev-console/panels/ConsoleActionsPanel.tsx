"use client";

import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

function emit(name: string, detail?: unknown) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(name, { detail }));
}

export function ConsoleActionsPanel() {
  return (
    <div className={cls("card")}>
      <div className={cls("cardTitle")}>Quick Actions</div>
      <div className={cls("cardHint")}>
        Event-based hooks. Existing or future modules can subscribe without direct imports.
      </div>

      <div className={cls("topBarActions")}>
        <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:export-scene")}>
          Export Scene
        </button>

        <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:snapshot")}>
          Snapshot
        </button>

        <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:toggle-grid")}>
          Emit Grid Toggle
        </button>

        <button type="button" className={cls("button")} onClick={() => emit("hitech:dev-console:reset-overlays")}>
          Reset Overlays
        </button>
      </div>

      <div className={cls("codeBox")}>
        {
          "Events emitted:\n- hitech:dev-console:export-scene\n- hitech:dev-console:snapshot\n- hitech:dev-console:toggle-grid\n- hitech:dev-console:reset-overlays"
        }
      </div>
    </div>
  );
}
