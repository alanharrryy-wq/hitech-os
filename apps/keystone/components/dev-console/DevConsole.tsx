"use client";

import { useMemo, useState } from "react";
import { FloatingWindow } from "../../app/dev/scene-studio/FloatingWindow";
import { useDevConsole } from "./DevConsoleContext";
import { buildDevConsoleRegistry } from "./DevConsoleRegistry";
import type { DevConsoleToolId } from "./types";
import styles from "./dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";
const ACTIVE_TOOL_STORAGE_KEY = "keystone.devConsole.activeTool";

function readActiveTool(): DevConsoleToolId {
  if (typeof window === "undefined") return "home";

  try {
    const raw = localStorage.getItem(ACTIVE_TOOL_STORAGE_KEY);
    switch (raw) {
      case "home":
      case "scene":
      case "layers":
      case "overlay":
      case "share-look":
      case "runtime":
      case "actions":
      case "flags":
      case "perf":
      case "layouts":
        return raw;
      default:
        return "home";
    }
  } catch {
    return "home";
  }
}

export function DevConsole() {
  const { bindings, flags, setFlags } = useDevConsole();
  const [activeTool, setActiveTool] = useState<DevConsoleToolId>(() => readActiveTool());

  const registry = useMemo(
    () =>
      buildDevConsoleRegistry({
        bindings,
        activeTool,
        setActiveTool,
        flags,
        setFlags
      }),
    [activeTool, bindings, flags, setFlags]
  );

  const active = registry.find((item) => item.id === activeTool) ?? registry[0];
  if (!active) {
    return null;
  }

  const persistActiveTool = (tool: DevConsoleToolId) => {
    setActiveTool(tool);

    try {
      localStorage.setItem(ACTIVE_TOOL_STORAGE_KEY, tool);
    } catch {
      // ignore
    }
  };

  const resetConsoleLayout = () => {
    try {
      localStorage.removeItem("keystone.floatingWindow.dev-console");
    } catch {
      // ignore
    }

    window.dispatchEvent(
      new CustomEvent("hitech:floating-window:restore", {
        detail: { id: "dev-console" }
      })
    );
  };

  const clearConsoleStorage = () => {
    const keys = [
      "keystone.floatingWindow.dev-console",
      "keystone.devConsole.activeTool",
      "keystone.devConsole.flags",
      "keystone.devConsole.layoutProfiles"
    ];

    try {
      keys.forEach((key) => localStorage.removeItem(key));
    } catch {
      // ignore
    }

    persistActiveTool("home");
    setFlags({
      showGrid: false,
      motionEnabled: true,
      reducedMotion: false,
      showSafeAreas: false,
      showDebugLabels: false
    });

    window.dispatchEvent(
      new CustomEvent("hitech:floating-window:restore", {
        detail: { id: "dev-console" }
      })
    );
  };

  return (
    <FloatingWindow
      id="dev-console"
      title="HITECH Dev Console"
      defaultPos={{ x: 20, y: 20 }}
      defaultSize={{ w: 980, h: 760 }}
      homePos={{ x: 20, y: 20 }}
      homeSize={{ w: 980, h: 760 }}
      minSize={{ w: 760, h: 420 }}
      initialZ={2_100_000_000}
      headerRight={<div style={{ fontSize: 11, opacity: 0.82, whiteSpace: "nowrap" }}>Single Console Mode</div>}
    >
      <div className={cls("root")}>
        <div className={cls("rail")}>
          {registry.map((tool) => {
            const isActive = tool.id === active.id;
            return (
              <button
                key={tool.id}
                type="button"
                className={`${cls("railButton")} ${isActive ? cls("railButtonActive") : ""}`}
                onClick={() => persistActiveTool(tool.id)}
                title={tool.label}
              >
                <span className={cls("railButtonText")}>{tool.shortLabel}</span>
              </button>
            );
          })}
        </div>

        <div className={cls("main")}>
          <div className={cls("topBar")}>
            <div className={cls("topBarTitleBlock")}>
              <div className={cls("topBarTitle")}>{active.label}</div>
              <div className={cls("topBarDescription")}>{active.description}</div>
            </div>

            <div className={cls("topBarActions")}>
              <button type="button" className={cls("button")} onClick={resetConsoleLayout}>
                Reset Position
              </button>

              <button type="button" className={cls("button")} onClick={() => persistActiveTool("home")}>
                Go Home
              </button>

              <button
                type="button"
                className={`${cls("button")} ${cls("buttonDanger")}`}
                onClick={clearConsoleStorage}
              >
                Clear Console State
              </button>
            </div>
          </div>

          <div className={cls("content")}>{active.render()}</div>
        </div>
      </div>
    </FloatingWindow>
  );
}
