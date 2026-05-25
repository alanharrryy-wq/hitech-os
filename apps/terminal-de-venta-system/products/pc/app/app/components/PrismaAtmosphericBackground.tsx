"use client";

import { useEffect, useRef } from "react";

/**
 * PRISMA Cloudglass atmospheric background for the PC interface.
 *
 * Layer contract:
 * 1. Base graphite cloudglass image.
 * 2. Fractures / light overlay with alpha.
 * 3. Mist / dust overlay with alpha.
 * 4. Readability scrim.
 * 5. UI content above this component.
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

        element.style.setProperty("--prisma-mx", x.toFixed(4));
        element.style.setProperty("--prisma-my", y.toFixed(4));
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
      data-prisma-background="fractured-graphite-cloudglass"
    >
      <div className="prisma-bg-layer prisma-bg-base" />
      <div className="prisma-bg-layer prisma-bg-fractures" />
      <div className="prisma-bg-layer prisma-bg-mist" />
      <div className="prisma-bg-layer prisma-bg-scrim" />
    </div>
  );
}
