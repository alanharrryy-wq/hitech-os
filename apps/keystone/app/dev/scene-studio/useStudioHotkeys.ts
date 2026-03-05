"use client";

import { useEffect } from "react";
import { useWindowManager } from "./window-manager/useWindowManager";

function isTextInputTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) {
    return false;
  }

  if (target.isContentEditable) {
    return true;
  }

  const tag = target.tagName.toLowerCase();
  return tag === "input" || tag === "textarea" || tag === "select";
}

export function useStudioHotkeys() {
  const { panicReset, toggleWindow } = useWindowManager();

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (isTextInputTarget(event.target)) {
        return;
      }

      const key = event.key.toLowerCase();

      if (event.shiftKey && !event.ctrlKey && !event.metaKey && key === "r") {
        event.preventDefault();
        panicReset();
        return;
      }

      if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) {
        return;
      }

      if (key === "e") {
        event.preventDefault();
        toggleWindow("scene-editor");
        return;
      }

      if (key === "l") {
        event.preventDefault();
        toggleWindow("layer-debug");
        return;
      }

      if (key === "g") {
        event.preventDefault();
        toggleWindow("scene-graph");
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [panicReset, toggleWindow]);
}
