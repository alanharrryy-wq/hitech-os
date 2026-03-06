export interface FxOverlayOptions {
  readonly noise?: boolean;
  readonly scanline?: boolean;
  readonly haze?: boolean;
  readonly vignette?: boolean;
  readonly floating?: boolean;
}

export const FX_OVERLAYS_DISABLED: Required<FxOverlayOptions> = Object.freeze({
  noise: false,
  scanline: false,
  haze: false,
  vignette: false,
  floating: false
});

export function normalizeFxOverlays(options?: FxOverlayOptions): Required<FxOverlayOptions> {
  return {
    ...FX_OVERLAYS_DISABLED,
    ...(options ?? {})
  };
}

export function hasAnyFxOverlay(options?: FxOverlayOptions): boolean {
  const normalized = normalizeFxOverlays(options);
  return (
    normalized.noise ||
    normalized.scanline ||
    normalized.haze ||
    normalized.vignette ||
    normalized.floating
  );
}
