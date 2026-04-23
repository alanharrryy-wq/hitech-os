"use client";

import { useEffect, useMemo, useState, type CSSProperties } from "react";

import { DEFAULT_UI_THEME, getBackdropDescriptors, isUiThemeId, resolveUiThemeId, type UiThemeId } from "@/lib/ui/theme-system";
import { cn } from "@/lib/utils";

type MotionMode = "full" | "reduced" | "none";

function readThemeAndMotion(): { themeId: UiThemeId; motionMode: MotionMode } {
  if (typeof document === "undefined") {
    return { themeId: DEFAULT_UI_THEME, motionMode: "full" };
  }

  const root = document.documentElement;
  const themeCandidate = root.dataset.uiTheme;
  const motionCandidate = root.dataset.uiMotion;
  const osReducedMotion = typeof window !== "undefined" && typeof window.matchMedia === "function"
    ? window.matchMedia("(prefers-reduced-motion: reduce)").matches
    : false;

  const motionMode: MotionMode =
    motionCandidate === "none"
      ? "none"
      : motionCandidate === "reduced" || osReducedMotion
        ? "reduced"
        : "full";

  return {
    themeId: isUiThemeId(themeCandidate) ? themeCandidate : DEFAULT_UI_THEME,
    motionMode
  };
}

interface NebulaOrbDescriptor {
  id: string;
  x: number;
  y: number;
  size: number;
  opacity: number;
  driftX: number;
  driftY: number;
  blur: number;
  delay: number;
  duration: number;
}

function getNebulaOrbs(themeId: UiThemeId): readonly NebulaOrbDescriptor[] {
  switch (themeId) {
    case "aurora":
      return [
        { id: "aurora-nebula-left", x: 15, y: 34, size: 42, opacity: 0.42, driftX: 42, driftY: -24, blur: 28, delay: 0, duration: 24.5 },
        { id: "aurora-nebula-right", x: 84, y: 38, size: 48, opacity: 0.4, driftX: -38, driftY: 20, blur: 34, delay: 0.6, duration: 27.5 },
        { id: "aurora-nebula-bottom", x: 52, y: 84, size: 44, opacity: 0.35, driftX: 16, driftY: -18, blur: 30, delay: 1.1, duration: 25.2 }
      ] as const;
    case "neon":
      return [
        { id: "neon-nebula-left", x: 18, y: 28, size: 44, opacity: 0.43, driftX: 34, driftY: -18, blur: 26, delay: 0.2, duration: 23.8 },
        { id: "neon-nebula-right", x: 86, y: 44, size: 52, opacity: 0.44, driftX: -44, driftY: 22, blur: 36, delay: 0.9, duration: 28.8 },
        { id: "neon-nebula-bottom", x: 54, y: 84, size: 46, opacity: 0.34, driftX: 22, driftY: -16, blur: 32, delay: 1.4, duration: 24.9 }
      ] as const;
    default:
      return [
        { id: "solstice-nebula-left", x: 14, y: 30, size: 44, opacity: 0.36, driftX: 30, driftY: -16, blur: 26, delay: 0, duration: 24.4 },
        { id: "solstice-nebula-right", x: 83, y: 42, size: 50, opacity: 0.37, driftX: -36, driftY: 18, blur: 34, delay: 0.75, duration: 28.2 },
        { id: "solstice-nebula-bottom", x: 52, y: 86, size: 48, opacity: 0.31, driftX: 20, driftY: -14, blur: 30, delay: 1.2, duration: 26.1 }
      ] as const;
  }
}

export function AmbientBackdrop() {
  const [{ themeId, motionMode }, setThemeState] = useState(() => readThemeAndMotion());

  useEffect(() => {
    const sync = () => setThemeState(readThemeAndMotion());
    sync();

    const onThemeChange = () => sync();
    const onMotionChange = () => sync();

    window.addEventListener("ui-theme-change", onThemeChange as EventListener);
    window.addEventListener("ui-motion-change", onMotionChange as EventListener);

    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-ui-theme", "data-ui-motion"]
    });

    let media: MediaQueryList | null = null;
    const onMedia = () => sync();
    if (typeof window.matchMedia === "function") {
      media = window.matchMedia("(prefers-reduced-motion: reduce)");
      if (typeof media.addEventListener === "function") {
        media.addEventListener("change", onMedia);
      } else {
        media.addListener(onMedia);
      }
    }

    return () => {
      window.removeEventListener("ui-theme-change", onThemeChange as EventListener);
      window.removeEventListener("ui-motion-change", onMotionChange as EventListener);
      observer.disconnect();
      if (media) {
        if (typeof media.removeEventListener === "function") {
          media.removeEventListener("change", onMedia);
        } else {
          media.removeListener(onMedia);
        }
      }
    };
  }, []);

  const descriptors = useMemo(() => getBackdropDescriptors(resolveUiThemeId(themeId)), [themeId]);
  const nebulaOrbs = useMemo(() => getNebulaOrbs(resolveUiThemeId(themeId)), [themeId]);

  const reduced = motionMode === "reduced";
  const staticOnly = motionMode === "none";

  return (
    <div aria-hidden className={cn("ambient-root", reduced && "ambient-root-reduced", staticOnly && "ambient-root-static")}>
      <div className="ambient-base" />
      <div className="ambient-mist" />

      <div className="ambient-layer ambient-layer-nebula">
        {nebulaOrbs.map((orb) => (
          <span
            key={orb.id}
            className="ambient-nebula"
            style={
              {
                "--ambient-x": `${orb.x}%`,
                "--ambient-y": `${orb.y}%`,
                "--ambient-size": `${orb.size}rem`,
                "--ambient-opacity": orb.opacity,
                "--ambient-dx": `${orb.driftX}px`,
                "--ambient-dy": `${orb.driftY}px`,
                "--ambient-blur": `${orb.blur}px`,
                "--ambient-delay": `${orb.delay}s`,
                "--ambient-duration": `${orb.duration}s`
              } as CSSProperties
            }
          />
        ))}
      </div>

      <div className="ambient-layer ambient-layer-far">
        {descriptors.farParticles.map((particle) => (
          <span
            key={particle.id}
            className="ambient-particle ambient-particle-far"
            style={
              {
                "--ambient-x": `${particle.x}%`,
                "--ambient-y": `${particle.y}%`,
                "--ambient-size": `${particle.size}rem`,
                "--ambient-opacity": particle.opacity,
                "--ambient-dx": `${particle.driftX}px`,
                "--ambient-dy": `${particle.driftY}px`,
                "--ambient-blur": `${particle.blur}px`,
                "--ambient-delay": `${particle.delay}s`,
                "--ambient-duration":
                  particle.cadenceBand === 3
                    ? "var(--theme-cadence-3)"
                    : particle.cadenceBand === 5
                      ? "var(--theme-cadence-5)"
                      : "var(--theme-cadence-10)"
              } as CSSProperties
            }
          />
        ))}
      </div>

      <div className="ambient-layer ambient-layer-near">
        {descriptors.nearParticles.map((particle) => (
          <span
            key={particle.id}
            className="ambient-particle ambient-particle-near"
            style={
              {
                "--ambient-x": `${particle.x}%`,
                "--ambient-y": `${particle.y}%`,
                "--ambient-size": `${particle.size}rem`,
                "--ambient-opacity": particle.opacity,
                "--ambient-dx": `${particle.driftX}px`,
                "--ambient-dy": `${particle.driftY}px`,
                "--ambient-blur": `${particle.blur}px`,
                "--ambient-delay": `${particle.delay}s`,
                "--ambient-duration":
                  particle.cadenceBand === 3
                    ? "var(--theme-cadence-3)"
                    : particle.cadenceBand === 5
                      ? "var(--theme-cadence-5)"
                      : "var(--theme-cadence-10)"
              } as CSSProperties
            }
          />
        ))}
      </div>

      <div className="ambient-layer ambient-layer-sparkle">
        {descriptors.sparkles.map((sparkle) => (
          <span
            key={sparkle.id}
            className="ambient-sparkle"
            style={
              {
                "--ambient-x": `${sparkle.x}%`,
                "--ambient-y": `${sparkle.y}%`,
                "--ambient-size": `${sparkle.size}rem`,
                "--ambient-opacity": sparkle.opacity,
                "--ambient-delay": `${sparkle.delay}s`,
                "--ambient-duration":
                  sparkle.cadenceBand === 5 ? "var(--theme-cadence-5)" : "var(--theme-cadence-10)"
              } as CSSProperties
            }
          />
        ))}
      </div>

      <div className="ambient-noise" />
      <div className="ambient-vignette" />
    </div>
  );
}
