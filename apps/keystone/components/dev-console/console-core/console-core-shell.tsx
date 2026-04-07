"use client";

import { useMemo } from "react";
import { FloatingWindow } from "../../../app/dev/scene-studio/FloatingWindow";
import {
  FLOATING_WINDOW_DRAG_HANDLE_ATTR,
  FLOATING_WINDOW_NO_DRAG_ATTR
} from "../../../app/dev/scene-studio/floating-window-drag-policy";
import type { DevConsoleToolDefinition, DevConsoleToolId } from "../types";
import styles from "../dev-console.module.css";

const cls = (name: string) => styles[name] ?? "";

export interface ConsoleCoreShellProps {
  readonly registry: readonly DevConsoleToolDefinition[];
  readonly activeTool: DevConsoleToolDefinition;
  readonly statusLabel: string;
  readonly statusTitle: string;
  readonly statusLine: string;
  readonly diagnosticsLabel: string;
  readonly onSelectTool: (toolId: DevConsoleToolId) => void;
  readonly onRefreshRuntime: () => void;
  readonly onResetPosition: () => void;
  readonly onGoHome: () => void;
  readonly onClearState: () => void;
}

function domainPrefix(domain: DevConsoleToolDefinition["domain"]): string {
  if (domain === "inspect") return "INSP";
  if (domain === "compose") return "CMP";
  return "CORE";
}

export function ConsoleCoreShell({
  registry,
  activeTool,
  statusLabel,
  statusTitle,
  statusLine,
  diagnosticsLabel,
  onSelectTool,
  onRefreshRuntime,
  onResetPosition,
  onGoHome,
  onClearState
}: ConsoleCoreShellProps) {
  const grouped = useMemo(
    () => ({
      core: registry.filter((tool) => tool.domain === "core"),
      inspect: registry.filter((tool) => tool.domain === "inspect"),
      compose: registry.filter((tool) => tool.domain === "compose")
    }),
    [registry]
  );

  const dragHandleAttr = { [FLOATING_WINDOW_DRAG_HANDLE_ATTR]: "true" } as const;
  const noDragAttr = { [FLOATING_WINDOW_NO_DRAG_ATTR]: "true" } as const;

  return (
    <FloatingWindow
      id="dev-console"
      title="HITECH Dev Console"
      defaultPos={{ x: 20, y: 20 }}
      defaultSize={{ w: 980, h: 760 }}
      minSize={{ w: 760, h: 420 }}
    >
      <div className={cls("root")}>
        <div className={cls("rail")} {...noDragAttr}>
          {(["core", "inspect", "compose"] as const).map((domain) => {
            const tools = grouped[domain];
            if (tools.length === 0) {
              return null;
            }
            return (
              <div key={domain}>
                <div className={cls("cardHint")} style={{ padding: "8px 4px 4px", fontSize: 10, opacity: 0.9 }}>
                  {domainPrefix(domain)}
                </div>
                {tools.map((tool) => {
                  const isActive = tool.id === activeTool.id;
                  return (
                    <button
                      key={tool.id}
                      type="button"
                      className={`${cls("railButton")} ${isActive ? cls("railButtonActive") : ""}`}
                      onClick={() => onSelectTool(tool.id)}
                      title={`${tool.label} (${domainPrefix(tool.domain)})`}
                    >
                      <span className={cls("railButtonText")}>{tool.shortLabel}</span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>

        <div className={cls("main")}>
          <div className={cls("topBar")} {...dragHandleAttr}>
            <div className={cls("topBarTitleBlock")}>
              <div className={cls("topBarTitle")}>{activeTool.label}</div>
              <div className={cls("topBarDescription")}>{activeTool.description}</div>
              <div className={cls("cardHint")} title={statusTitle}>
                {statusLabel} · {statusLine}
              </div>
            </div>

            <div className={cls("topBarActions")} {...noDragAttr}>
              <button type="button" className={cls("button")} onClick={onRefreshRuntime}>
                Refresh Runtime
              </button>
              <button type="button" className={cls("button")} onClick={onResetPosition}>
                Reset Position
              </button>
              <button type="button" className={cls("button")} onClick={onGoHome}>
                Go Home
              </button>
              <button type="button" className={`${cls("button")} ${cls("buttonDanger")}`} onClick={onClearState}>
                Clear Console State
              </button>
            </div>
          </div>

          <div className={cls("content")} {...noDragAttr}>
            {activeTool.render()}
          </div>
        </div>
      </div>
    </FloatingWindow>
  );
}
