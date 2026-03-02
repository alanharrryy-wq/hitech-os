import type { CSSProperties, HTMLAttributes } from "react";
import type { LayerProfile } from "../layers/layerIds.js";
import { cn } from "../lib/cn.js";
import {
  brandPresenceConfig,
  resolveBrandModeEnabled,
  resolveBrandModeOpacity,
  resolveBrandSealSize,
  type BrandPresenceIntensity,
  type BrandPresenceMode
} from "./brand-presence.config.js";

const PATTERN_MARKS = [
  { top: "10%", left: "12%", scale: 0.72 },
  { top: "14%", left: "42%", scale: 0.6 },
  { top: "16%", left: "78%", scale: 0.78 },
  { top: "44%", left: "18%", scale: 0.64 },
  { top: "52%", left: "56%", scale: 0.7 },
  { top: "48%", left: "88%", scale: 0.6 },
  { top: "82%", left: "28%", scale: 0.66 },
  { top: "84%", left: "72%", scale: 0.74 }
] as const;

function PhoenixGlyph({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 128 128"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      fill="none"
    >
      <path
        d="M64 12c-5 13-12 21-21 29 5 0 10-1 14-3-8 14-17 22-31 29 12-1 20-4 28-8-6 9-13 16-23 22 11-1 20-4 28-8-1 11-4 20-10 29 8-4 13-9 15-14 3 5 8 10 16 14-6-9-9-18-10-29 8 4 17 7 28 8-10-6-17-13-23-22 8 4 16 7 28 8-14-7-23-15-31-29 4 2 9 3 14 3-9-8-16-16-22-29z"
        fill="currentColor"
      />
      <path
        d="M64 51c-8 10-12 22-12 36 0 13 4 24 12 33 8-9 12-20 12-33 0-14-4-26-12-36z"
        fill="currentColor"
      />
    </svg>
  );
}

export interface BrandPresenceLayerProps extends HTMLAttributes<HTMLDivElement> {
  readonly mode: BrandPresenceMode;
  readonly intensity?: BrandPresenceIntensity;
  readonly profile?: LayerProfile;
  readonly repeatPattern?: boolean;
}

export function BrandPresenceLayer({
  mode,
  intensity = "subtle",
  profile = "neutral",
  repeatPattern = false,
  className,
  style,
  ...props
}: BrandPresenceLayerProps) {
  if (!resolveBrandModeEnabled(mode, profile)) {
    return null;
  }

  const layerOpacity = resolveBrandModeOpacity(mode, profile, intensity);
  const sealSize = resolveBrandSealSize(intensity);

  const resolvedStyle = {
    "--hitech-brand-layer-opacity": String(layerOpacity),
    "--hitech-brand-seal-size": `${sealSize}px`,
    "--hitech-brand-header-halo-opacity": String(
      resolveBrandModeOpacity("header-mark", profile, intensity)
    ),
    "--hitech-brand-phoenix-url": `url('${brandPresenceConfig.phoenixAssetPath}')`,
    ...style
  } as CSSProperties;

  return (
    <div
      aria-hidden="true"
      className={cn(
        "ui-brand-presence",
        `ui-brand-presence--${mode}`,
        repeatPattern ? "ui-brand-presence--repeat" : null,
        className
      )}
      style={resolvedStyle}
      {...props}
    >
      <PhoenixGlyph className="ui-brand-presence__glyph" />
      {repeatPattern
        ? PATTERN_MARKS.map((mark, index) => (
            <span
              // Deterministic mark map for repeat depth background.
              key={`brand-mark-${index}`}
              className="ui-brand-presence__pattern-mark"
              style={{
                top: mark.top,
                left: mark.left,
                transform: `translate(-50%, -50%) scale(${mark.scale})`
              }}
            >
              <PhoenixGlyph className="ui-brand-presence__pattern-glyph" />
            </span>
          ))
        : null}
    </div>
  );
}
