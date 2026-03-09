"use client";

import { useEffect, useMemo, useState } from "react";
import { FloatingWindow } from "../../app/dev/scene-studio/FloatingWindow";
import {
  FLOATING_WINDOW_DRAG_HANDLE_ATTR,
  FLOATING_WINDOW_NO_DRAG_ATTR
} from "../../app/dev/scene-studio/floating-window-drag-policy";
import { useDevConsole } from "./DevConsoleContext";
import { buildDevConsoleRegistry } from "./DevConsoleRegistry";
import type { DevConsoleBridgeStatus, DevConsoleToolId } from "./types";
import styles from "./dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";
const ACTIVE_TOOL_STORAGE_KEY = "keystone.devConsole.activeTool";

let __HITECH_DEV_CONSOLE_SINGLETON__ = false;

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

function bridgeTone(status: DevConsoleBridgeStatus) {
  switch (status) {
    case "live":
      return { label: "Bridge live", title: "Diagnostics stream healthy" };
    case "stale":
      return { label: "Bridge stale", title: "Diagnostics stopped updating" };
    case "booting":
      return { label: "Bridge booting", title: "Waiting for first diagnostics heartbeat" };
    case "offline":
      return { label: "Bridge offline", title: "Runtime bridge not detected" };
    default:
      return { label: "Bridge idle", title: "No diagnostics yet" };
  }
}

export function DevConsole() {
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    if (__HITECH_DEV_CONSOLE_SINGLETON__) {
      console.warn("HITECH DevConsole: prevented duplicate mount");
      setAllowed(false);
      return;
    }

    __HITECH_DEV_CONSOLE_SINGLETON__ = true;
    setAllowed(true);

    return () => {
      __HITECH_DEV_CONSOLE_SINGLETON__ = false;
    };
  }, []);

  if (!allowed) {
    return null;
  }

  return <ActualDevConsole />;
}

function ActualDevConsole() {
  const { bindings, flags, setFlags, runtime, bridgeStatus, lastDiagnosticsAt, refreshDiagnostics } = useDevConsole();
  const [activeTool, setActiveTool] = useState<DevConsoleToolId>("home");

  useEffect(() => {
    setActiveTool(readActiveTool());
  }, []);

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

  const dragHandleAttr = { [FLOATING_WINDOW_DRAG_HANDLE_ATTR]: "true" } as const;
  const noDragAttr = { [FLOATING_WINDOW_NO_DRAG_ATTR]: "true" } as const;

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
      ACTIVE_TOOL_STORAGE_KEY,
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
      motionEnabled: false,
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

  const bridgeMeta = bridgeTone(bridgeStatus);
  const runtimeSummary = runtime
    ? `${runtime.route}${runtime.query ? runtime.query : ""}`
    : "No runtime snapshot yet";

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
      headerRight={
        <div style={{ fontSize: 11, opacity: 0.82, whiteSpace: "nowrap" }}>
          {runtime?.diagnosticsAvailable ? "Runtime synced" : "Runtime awaiting first snapshot"}
        </div>
      }
    >
      <div className={cls("root")}>
        <div className={cls("rail")} {...noDragAttr}>
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
          <div className={cls("topBar")} {...dragHandleAttr}>
            <div className={cls("topBarTitleBlock")}>
              <div className={cls("topBarTitle")}>{active.label}</div>
              <div className={cls("topBarDescription")}>{active.description}</div>
              <div className={cls("cardHint")} title={bridgeMeta.title}>
                {bridgeMeta.label} · {runtimeSummary}
                {lastDiagnosticsAt ? ` · ${lastDiagnosticsAt}` : ""}
              </div>
            </div>

            <div className={cls("topBarActions")} {...noDragAttr}>
              <button type="button" className={cls("button")} onClick={() => refreshDiagnostics()}>
                Refresh Runtime
              </button>

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

          <div className={cls("content")} {...noDragAttr}>
            {active.render()}
          </div>
        </div>
      </div>
    </FloatingWindow>
  );
}