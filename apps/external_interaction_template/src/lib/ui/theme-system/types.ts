export type LiveUiThemeId = "aurora" | "solstice" | "neon";
export type ReservedUiThemeId = "slot_01" | "slot_02";
export type UiThemeId = LiveUiThemeId | ReservedUiThemeId;

export type ThemeColorScheme = "light" | "dark";
export type ThemeSurfaceBlendMode = "normal" | "screen" | "multiply" | "soft-light" | "lighten" | "overlay";

export interface ThemeMeta {
  id: UiThemeId;
  labelKey: string;
  premium: boolean;
  slot: "live" | "reserved";
  selectorVisible: boolean;
  colorScheme: ThemeColorScheme;
  personality: string;
}

export interface ThemeColorTokens {
  canvas: string;
  surface: string;
  panel: string;
  elevated: string;
  text: string;
  heading: string;
  muted: string;
  subtle: string;
  border: string;
  borderStrong: string;
  accent: string;
  accentSoft: string;
  accentContrast: string;
  success: string;
  warning: string;
  danger: string;
  selectionBg: string;
  selectionText: string;
  scrollbarThumb: string;
}

export interface ThemeMaterialTokens {
  chromeBackground: string;
  chromeBorder: string;
  chromeShadow: string;
  chromeBlur: string;
  surfacePrimary: string;
  surfaceSecondary: string;
  surfaceMuted: string;
  surfaceElevated: string;
  surfaceBorder: string;
  surfaceEdge: string;
  surfaceShadow: string;
  inlineBackground: string;
  inlineBorder: string;
  overlayBackground: string;
  overlayBorder: string;
  overlayShadow: string;
}

export interface ThemeChromeTokens {
  shellHeight: string;
  shellRadius: string;
  shellPaddingInline: string;
  shellPaddingBlock: string;
  navRadius: string;
  navGap: string;
  navActiveBackground: string;
  navActiveBorder: string;
  navActiveShadow: string;
  navIdleBackground: string;
  navIdleHoverBackground: string;
  clusterBackground: string;
  clusterBorder: string;
  clusterRadius: string;
  chipBackground: string;
  chipBorder: string;
  chipText: string;
}

export interface ThemeMotionTokens {
  productiveDuration: string;
  standardDuration: string;
  expressiveDuration: string;
  productiveEasing: string;
  expressiveEasing: string;
  hoverLift: string;
  backdropCadence: {
    drift3: string;
    drift5: string;
    drift10: string;
  };
  reduced: {
    ambient: "minimal" | "off";
    expressive: "fade";
  };
}

export interface ThemeBackdropTokens {
  baseGradient: string;
  mistGradient: string;
  vignetteGradient: string;
  particleNearColor: string;
  particleFarColor: string;
  sparkleColor: string;
  noiseOpacity: string;
  blendMode: ThemeSurfaceBlendMode;
}

export interface ThemeWidgetTokens {
  controlRadius: string;
  surfaceRadius: string;
  inlineRadius: string;
  buttonPrimaryBackground: string;
  buttonPrimaryForeground: string;
  buttonPrimaryBorder: string;
  buttonPrimaryShadow: string;
  buttonSecondaryBackground: string;
  buttonSecondaryForeground: string;
  buttonSecondaryBorder: string;
  buttonSecondaryShadow: string;
  buttonGhostBackground: string;
  buttonGhostForeground: string;
  buttonGhostBorder: string;
  buttonDangerBackground: string;
  buttonDangerForeground: string;
  buttonDangerBorder: string;
  fieldBackground: string;
  fieldBorder: string;
  fieldFocusRing: string;
  pillBackground: string;
  pillBorder: string;
  pillActiveBackground: string;
  pillActiveBorder: string;
  pillActiveForeground: string;
  tableRowBackground: string;
  tableRowHover: string;
  tableDivider: string;
  modalBackground: string;
  modalBorder: string;
  modalShadow: string;
  loaderTrack: string;
  loaderBar: string;
}

export interface ThemeTypographyTokens {
  bodyFont: string;
  headingFont: string;
  monoFont: string;
  bodyWeight: string;
  headingWeight: string;
  headingTracking: string;
  displayTracking: string;
}

export interface ThemeDataVizTokens {
  series: readonly [string, string, string, string];
  grid: string;
  axis: string;
  glow: string;
  surface: string;
}

export interface ThemeSpec {
  meta: ThemeMeta;
  color: ThemeColorTokens;
  material: ThemeMaterialTokens;
  chrome: ThemeChromeTokens;
  motion: ThemeMotionTokens;
  backdrop: ThemeBackdropTokens;
  widgets: ThemeWidgetTokens;
  typography: ThemeTypographyTokens;
  dataViz: ThemeDataVizTokens;
}

export interface UiThemeDefinition {
  id: UiThemeId;
  labelKey: string;
  premium: boolean;
  reserved: boolean;
  selectorVisible: boolean;
}

