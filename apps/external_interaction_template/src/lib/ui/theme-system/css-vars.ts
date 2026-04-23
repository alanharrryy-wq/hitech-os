import { getUiThemeSpec } from "@/lib/ui/theme-system/theme-registry";
import type { ThemeSpec, UiThemeId } from "@/lib/ui/theme-system/types";

type ThemeCssVars = Record<string, string>;

function toThemeCssVars(spec: ThemeSpec): ThemeCssVars {
  const vars: ThemeCssVars = {
    "--color-canvas": spec.color.canvas,
    "--color-surface": spec.color.surface,
    "--color-panel": spec.color.panel,
    "--color-elevated": spec.color.elevated,
    "--color-accent": spec.color.accent,
    "--color-success": spec.color.success,
    "--color-warning": spec.color.warning,
    "--color-danger": spec.color.danger,
    "--color-heading": spec.color.heading,
    "--color-text": spec.color.text,
    "--color-muted": spec.color.muted,
    "--color-subtle": spec.color.subtle,
    "--color-border": spec.color.border,
    "--color-border-strong": spec.color.borderStrong,

    "--theme-selection-bg": spec.color.selectionBg,
    "--theme-selection-text": spec.color.selectionText,
    "--theme-scrollbar-thumb": spec.color.scrollbarThumb,
    "--theme-accent-soft": spec.color.accentSoft,
    "--theme-accent-contrast": spec.color.accentContrast,

    "--theme-chrome-bg": spec.material.chromeBackground,
    "--theme-chrome-border": spec.material.chromeBorder,
    "--theme-chrome-shadow": spec.material.chromeShadow,
    "--theme-chrome-blur": spec.material.chromeBlur,
    "--theme-surface-primary": spec.material.surfacePrimary,
    "--theme-surface-secondary": spec.material.surfaceSecondary,
    "--theme-surface-muted": spec.material.surfaceMuted,
    "--theme-surface-elevated": spec.material.surfaceElevated,
    "--theme-surface-border": spec.material.surfaceBorder,
    "--theme-surface-edge": spec.material.surfaceEdge,
    "--theme-surface-shadow": spec.material.surfaceShadow,
    "--theme-inline-bg": spec.material.inlineBackground,
    "--theme-inline-border": spec.material.inlineBorder,
    "--theme-overlay-bg": spec.material.overlayBackground,
    "--theme-overlay-border": spec.material.overlayBorder,
    "--theme-overlay-shadow": spec.material.overlayShadow,

    "--theme-shell-height": spec.chrome.shellHeight,
    "--theme-shell-radius": spec.chrome.shellRadius,
    "--theme-shell-padding-inline": spec.chrome.shellPaddingInline,
    "--theme-shell-padding-block": spec.chrome.shellPaddingBlock,
    "--theme-nav-radius": spec.chrome.navRadius,
    "--theme-nav-gap": spec.chrome.navGap,
    "--theme-nav-active-bg": spec.chrome.navActiveBackground,
    "--theme-nav-active-border": spec.chrome.navActiveBorder,
    "--theme-nav-active-shadow": spec.chrome.navActiveShadow,
    "--theme-nav-idle-bg": spec.chrome.navIdleBackground,
    "--theme-nav-idle-hover-bg": spec.chrome.navIdleHoverBackground,
    "--theme-cluster-bg": spec.chrome.clusterBackground,
    "--theme-cluster-border": spec.chrome.clusterBorder,
    "--theme-cluster-radius": spec.chrome.clusterRadius,
    "--theme-chip-bg": spec.chrome.chipBackground,
    "--theme-chip-border": spec.chrome.chipBorder,
    "--theme-chip-text": spec.chrome.chipText,

    "--motion-fast": spec.motion.productiveDuration,
    "--motion-base": spec.motion.standardDuration,
    "--motion-slow": spec.motion.expressiveDuration,
    "--motion-ease-standard": spec.motion.productiveEasing,
    "--motion-ease-expressive": spec.motion.expressiveEasing,
    "--theme-hover-lift": spec.motion.hoverLift,
    "--theme-cadence-3": spec.motion.backdropCadence.drift3,
    "--theme-cadence-5": spec.motion.backdropCadence.drift5,
    "--theme-cadence-10": spec.motion.backdropCadence.drift10,
    "--theme-reduced-ambient": spec.motion.reduced.ambient,

    "--theme-backdrop-base": spec.backdrop.baseGradient,
    "--theme-backdrop-mist": spec.backdrop.mistGradient,
    "--theme-backdrop-vignette": spec.backdrop.vignetteGradient,
    "--theme-backdrop-particle-near": spec.backdrop.particleNearColor,
    "--theme-backdrop-particle-far": spec.backdrop.particleFarColor,
    "--theme-backdrop-sparkle": spec.backdrop.sparkleColor,
    "--theme-backdrop-noise-opacity": spec.backdrop.noiseOpacity,
    "--theme-backdrop-blend-mode": spec.backdrop.blendMode,

    "--theme-radius-control": spec.widgets.controlRadius,
    "--theme-radius-surface": spec.widgets.surfaceRadius,
    "--theme-radius-inline": spec.widgets.inlineRadius,
    "--theme-button-primary-bg": spec.widgets.buttonPrimaryBackground,
    "--theme-button-primary-fg": spec.widgets.buttonPrimaryForeground,
    "--theme-button-primary-border": spec.widgets.buttonPrimaryBorder,
    "--theme-button-primary-shadow": spec.widgets.buttonPrimaryShadow,
    "--theme-button-secondary-bg": spec.widgets.buttonSecondaryBackground,
    "--theme-button-secondary-fg": spec.widgets.buttonSecondaryForeground,
    "--theme-button-secondary-border": spec.widgets.buttonSecondaryBorder,
    "--theme-button-secondary-shadow": spec.widgets.buttonSecondaryShadow,
    "--theme-button-ghost-bg": spec.widgets.buttonGhostBackground,
    "--theme-button-ghost-fg": spec.widgets.buttonGhostForeground,
    "--theme-button-ghost-border": spec.widgets.buttonGhostBorder,
    "--theme-button-danger-bg": spec.widgets.buttonDangerBackground,
    "--theme-button-danger-fg": spec.widgets.buttonDangerForeground,
    "--theme-button-danger-border": spec.widgets.buttonDangerBorder,
    "--theme-field-bg": spec.widgets.fieldBackground,
    "--theme-field-border": spec.widgets.fieldBorder,
    "--theme-field-focus-ring": spec.widgets.fieldFocusRing,
    "--theme-pill-bg": spec.widgets.pillBackground,
    "--theme-pill-border": spec.widgets.pillBorder,
    "--theme-pill-active-bg": spec.widgets.pillActiveBackground,
    "--theme-pill-active-border": spec.widgets.pillActiveBorder,
    "--theme-pill-active-fg": spec.widgets.pillActiveForeground,
    "--theme-table-row-bg": spec.widgets.tableRowBackground,
    "--theme-table-row-hover": spec.widgets.tableRowHover,
    "--theme-table-divider": spec.widgets.tableDivider,
    "--theme-modal-bg": spec.widgets.modalBackground,
    "--theme-modal-border": spec.widgets.modalBorder,
    "--theme-modal-shadow": spec.widgets.modalShadow,
    "--theme-loader-track": spec.widgets.loaderTrack,
    "--theme-loader-bar": spec.widgets.loaderBar,

    "--theme-font-body": spec.typography.bodyFont,
    "--theme-font-heading": spec.typography.headingFont,
    "--theme-font-mono": spec.typography.monoFont,
    "--theme-font-body-weight": spec.typography.bodyWeight,
    "--theme-font-heading-weight": spec.typography.headingWeight,
    "--theme-font-heading-tracking": spec.typography.headingTracking,
    "--theme-font-display-tracking": spec.typography.displayTracking,

    "--theme-chart-series-1": spec.dataViz.series[0],
    "--theme-chart-series-2": spec.dataViz.series[1],
    "--theme-chart-series-3": spec.dataViz.series[2],
    "--theme-chart-series-4": spec.dataViz.series[3],
    "--theme-chart-grid": spec.dataViz.grid,
    "--theme-chart-axis": spec.dataViz.axis,
    "--theme-chart-glow": spec.dataViz.glow,
    "--theme-chart-surface": spec.dataViz.surface
  };

  return vars;
}

const themeCssCache = new Map<UiThemeId, ThemeCssVars>();

export function getThemeCssVariables(themeId: UiThemeId): ThemeCssVars {
  const cached = themeCssCache.get(themeId);
  if (cached) return cached;

  const vars = toThemeCssVars(getUiThemeSpec(themeId));
  themeCssCache.set(themeId, vars);
  return vars;
}

export function applyThemeToDocument(themeId: UiThemeId): void {
  if (typeof document === "undefined") return;

  const root = document.documentElement;
  const body = document.body;
  const spec = getUiThemeSpec(themeId);
  const vars = getThemeCssVariables(themeId);

  root.dataset.uiTheme = themeId;
  root.style.colorScheme = spec.meta.colorScheme;
  if (body) {
    body.dataset.uiTheme = themeId;
  }

  for (const [name, value] of Object.entries(vars)) {
    root.style.setProperty(name, value);
  }
}

