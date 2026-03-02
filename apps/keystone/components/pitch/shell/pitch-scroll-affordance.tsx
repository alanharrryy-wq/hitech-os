"use client";

import { useEffect, useMemo, useState } from "react";
import { cn } from "@hitech/ui-kit";

function supportsMotionPreference(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export interface PitchScrollAffordanceProps {
  readonly targetId?: string;
  readonly className?: string;
}

export function PitchScrollAffordance({ targetId, className }: PitchScrollAffordanceProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY < 120);
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const motion = useMemo(() => supportsMotionPreference(), []);

  const onClick = () => {
    if (targetId) {
      const element = document.getElementById(targetId);
      if (element) {
        element.scrollIntoView({ behavior: motion ? "smooth" : "auto", block: "start" });
        return;
      }
    }

    window.scrollTo({ top: window.innerHeight * 0.8, behavior: motion ? "smooth" : "auto" });
  };

  if (!visible) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "pitch-focus-ring pitch-scroll-affordance inline-flex h-10 items-center gap-2 px-3 text-xs font-semibold",
        className
      )}
      aria-label="Scroll to content"
    >
      <span>Scroll</span>
      <span aria-hidden>↓</span>
    </button>
  );
}
