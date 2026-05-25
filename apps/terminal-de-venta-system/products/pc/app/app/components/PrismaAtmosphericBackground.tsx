"use client";

import { useEffect, useRef } from "react";

/**
 * PRISMA Cloudglass Mist v2 · Executive Pearl background for PC.
 *
 * Layer contract:
 * B0 graphite base depth
 * B1 wide base asset, intentionally less zoomed
 * B2 restrained fracture/light overlay
 * B3 distant pearl-graphite mist
 * B4 native mist/dust asset, low opacity
 * B5 procedural pearl mist veil
 * B6 soft hero halo
 * B7 fine noise veil
 * B8 vignette + readability scrim
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
      data-prisma-background="cloudglass-mist-v2-executive-pearl"
    >
      <div className="prisma-bg-layer prisma-bg-base" />
      <div className="prisma-bg-layer prisma-bg-fractures" />
      <div className="prisma-bg-layer prisma-bg-distant-mist" />
      <div className="prisma-bg-layer prisma-bg-mist" />
      <div className="prisma-bg-layer prisma-bg-pearl-mist" />
      <div className="prisma-bg-layer prisma-bg-hero-light" />
      <div className="prisma-bg-layer prisma-bg-noise" />
      <div className="prisma-bg-layer prisma-bg-vignette" />
      <div className="prisma-bg-layer prisma-bg-scrim" />
    </div>
  );
}
