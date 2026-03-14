"use client";

import type { DevConsoleToolId } from "../types";

export const CONSOLE_ACTIVE_TOOL_STORAGE_KEY = "keystone.devConsole.activeTool";
export const CONSOLE_WINDOW_LAYOUT_STORAGE_KEY = "keystone.floatingWindow.dev-console";

const TOOL_ID_SET = new Set<DevConsoleToolId>([
  "home",
  "scene",
  "layers",
  "overlay",
  "share-look",
  "runtime",
  "actions",
  "flags",
  "perf",
  "layouts",
  "inspect-events",
  "inspect-snapshot",
  "compose-look"
]);

export function readStoredConsoleTool(fallback: DevConsoleToolId = "home"): DevConsoleToolId {
  if (typeof window === "undefined") {
    return fallback;
  }

  try {
    const raw = localStorage.getItem(CONSOLE_ACTIVE_TOOL_STORAGE_KEY);
    if (!raw) {
      return fallback;
    }
    return TOOL_ID_SET.has(raw as DevConsoleToolId) ? (raw as DevConsoleToolId) : fallback;
  } catch {
    return fallback;
  }
}

export function persistConsoleTool(tool: DevConsoleToolId): void {
  try {
    localStorage.setItem(CONSOLE_ACTIVE_TOOL_STORAGE_KEY, tool);
  } catch {
    // ignore write failures
  }
}

export function resetConsoleWindowLayout(windowId = "dev-console"): void {
  try {
    localStorage.removeItem(CONSOLE_WINDOW_LAYOUT_STORAGE_KEY);
  } catch {
    // ignore
  }

  if (typeof window === "undefined") {
    return;
  }

  window.dispatchEvent(
    new CustomEvent("hitech:floating-window:restore", {
      detail: { id: windowId }
    })
  );
}
