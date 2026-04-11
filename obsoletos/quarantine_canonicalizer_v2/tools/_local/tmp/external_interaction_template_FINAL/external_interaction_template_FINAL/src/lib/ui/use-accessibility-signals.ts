"use client";

import { useEffect, useMemo, useState } from "react";

import type { UiContrastPreference, UiMotionPreference } from "@/lib/ui/runtime";

export interface AccessibilitySignals {
  ready: boolean;
  prefersReducedMotion: boolean;
  prefersMoreContrast: boolean;
  prefersMaxContrast: boolean;
  motion: UiMotionPreference;
  contrast: UiContrastPreference;
}

function createInitialState(): AccessibilitySignals {
  return {
    ready: false,
    prefersReducedMotion: false,
    prefersMoreContrast: false,
    prefersMaxContrast: false,
    motion: "full",
    contrast: "normal"
  };
}

function readSignals(): AccessibilitySignals {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return { ...createInitialState(), ready: true };
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches || window.matchMedia("(update: slow)").matches;
  const prefersMoreContrast = window.matchMedia("(prefers-contrast: more)").matches;
  const forcedColors = window.matchMedia("(forced-colors: active)").matches;
  const prefersMaxContrast = forcedColors;

  return {
    ready: true,
    prefersReducedMotion,
    prefersMoreContrast,
    prefersMaxContrast,
    motion: prefersReducedMotion ? "reduced" : "full",
    contrast: prefersMaxContrast ? "max" : prefersMoreContrast ? "more" : "normal"
  };
}

function subscribe(query: MediaQueryList, callback: () => void): () => void {
  if (typeof query.addEventListener === "function") {
    query.addEventListener("change", callback);
    return () => query.removeEventListener("change", callback);
  }

  query.addListener(callback);
  return () => query.removeListener(callback);
}

export function useAccessibilitySignals(): AccessibilitySignals {
  const [state, setState] = useState<AccessibilitySignals>(createInitialState);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      setState({ ...createInitialState(), ready: true });
      return;
    }

    const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const moreContrastQuery = window.matchMedia("(prefers-contrast: more)");
    const forcedColorsQuery = window.matchMedia("(forced-colors: active)");
    const updateSlowQuery = window.matchMedia("(update: slow)");

    const sync = () => setState(readSignals());
    sync();

    const unsubscribers = [
      subscribe(reducedMotionQuery, sync),
      subscribe(moreContrastQuery, sync),
      subscribe(forcedColorsQuery, sync),
      subscribe(updateSlowQuery, sync)
    ];

    return () => {
      for (const unsubscribe of unsubscribers) unsubscribe();
    };
  }, []);

  return useMemo(() => state, [state]);
}
