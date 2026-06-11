"use client";

import { useEffect, useRef } from "react";

/**
 * PRISMA Cloudglass Mist v2 · Executive Pearl background for PC.
 *
 * Layer contract:
 * PRISMA_DELAYER_01 keeps only three runtime layers:
 * B0 base image/color field
 * B1 low-opacity mist, optional texture
 * B2 readability vignette
 *
 * Removed from runtime DOM: fracture overlay, distant mist, pearl mist, hero halo, noise and scrim.
 * The visual system stays premium, but no longer stacks nine panes of glass on a cash register.
 */
export function PrismaAtmosphericBackground() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element || typeof window === "undefined") return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (reducedMotion.matches) return;

    let raf = 0;

    const syncPointer = (event: MouseEvent) => {
      window.cancelAnimationFrame(raf);
      raf = window.requestAnimationFrame(() => {
        const x = (event.clientX / Math.max(window.innerWidth, 1) - 0.5) * 2;
        const y = (event.clientY / Math.max(window.innerHeight, 1) - 0.5) * 2;

        element.style.setProperty("--prisma-bg-x", x.toFixed(4));
        element.style.setProperty("--prisma-bg-y", y.toFixed(4));
      });
    };

    window.addEventListener("mousemove", syncPointer, { passive: true });

    return () => {
      window.cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", syncPointer);
    };
  }, []);

  return (
    <div
      ref={ref}
      className="prisma-atmosphere"
      aria-hidden="true"
      data-prisma-background="client-snow-mountains-delayer-01"
      data-prisma-layer-budget="3"
    >
      <div className="prisma-bg-layer prisma-bg-base" />
      <div className="prisma-bg-layer prisma-bg-mist" />
      <div className="prisma-bg-layer prisma-bg-vignette" />
    </div>
  );
}
