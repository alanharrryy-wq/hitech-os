"use client";

import { useEffect, useState } from "react";

export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined" || typeof window.matchMedia === "undefined") {
    return false;
  }

  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function useReducedMotionPreference(): boolean {
  const [reduced, setReduced] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia === "undefined") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");

    const handler = () => {
      setReduced(media.matches);
    };

    handler();

    media.addEventListener("change", handler);

    return () => {
      media.removeEventListener("change", handler);
    };
  }, []);

  return reduced;
}
