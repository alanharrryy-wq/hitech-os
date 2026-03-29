"use client";

import { useEffect } from "react";

export interface SceneStudioHotkeys {
  readonly onFocusSearch: () => void;
  readonly onNewScene: () => void;
  readonly onSaveScene: () => void;
  readonly onCopyUrl: () => void;
  readonly onRunVisual: () => void;
}

export function useSceneStudioHotkeys(hotkeys: SceneStudioHotkeys): void {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const isTypingTarget =
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT" ||
        target?.isContentEditable;

      if (event.key === "/" && !isTypingTarget) {
        event.preventDefault();
        hotkeys.onFocusSearch();
        return;
      }

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        hotkeys.onSaveScene();
        return;
      }

      if (!isTypingTarget && event.key.toLowerCase() === "n") {
        event.preventDefault();
        hotkeys.onNewScene();
        return;
      }

      if (!isTypingTarget && event.key.toLowerCase() === "c") {
        event.preventDefault();
        hotkeys.onCopyUrl();
        return;
      }

      if (!isTypingTarget && event.key.toLowerCase() === "r") {
        event.preventDefault();
        hotkeys.onRunVisual();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [hotkeys]);
}
