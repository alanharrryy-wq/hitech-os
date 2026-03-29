"use client";

import { useEffect, useMemo, useState } from "react";
import type { PerfProfile } from "../types.js";

export interface ReducedMotionConfig {
  readonly perfProfile?: PerfProfile | undefined;
  readonly forceReducedMotion?: boolean | undefined;
}

export interface ReducedMotionState {
  readonly reducedMotion: boolean;
  readonly allowMicroMotion: boolean;
  readonly allowShimmer: boolean;
  readonly transitionMs: number;
}

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia === "undefined") {
    return false;
  }

  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function useReducedMotion(config: ReducedMotionConfig = {}): ReducedMotionState {
  const [systemReducedMotion, setSystemReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia === "undefined") {
      return;
    }

    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => {
      setSystemReducedMotion(query.matches);
    };

    update();
    query.addEventListener("change", update);

    return () => {
      query.removeEventListener("change", update);
    };
  }, []);

  return useMemo(() => {
    const perfProfile = config.perfProfile ?? "balanced";
    const reducedMotion = config.forceReducedMotion || systemReducedMotion || perfProfile === "performance";

    return {
      reducedMotion,
      allowMicroMotion: !reducedMotion,
      allowShimmer: !reducedMotion && perfProfile === "quality",
      transitionMs: reducedMotion ? 0 : perfProfile === "quality" ? 180 : 120
    };
  }, [config.forceReducedMotion, config.perfProfile, systemReducedMotion]);
}
