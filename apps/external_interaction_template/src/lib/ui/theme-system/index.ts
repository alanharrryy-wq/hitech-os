export { applyThemeToDocument, getThemeCssVariables } from "@/lib/ui/theme-system/css-vars";
export { getBackdropDescriptors, BACKDROP_DESCRIPTORS } from "@/lib/ui/theme-system/backdrop-descriptors";
export { UI_THEME_SPECS, UI_THEME_IDS } from "@/lib/ui/theme-system/theme-specs";
export {
  UI_THEME_STORAGE_KEY,
  DEFAULT_UI_THEME,
  UI_THEMES,
  VISIBLE_UI_THEMES,
  RESERVED_THEME_SELECTOR_VISIBILITY,
  isUiThemeId,
  resolveUiThemeId,
  getUiThemeSpec,
  getThemeLabelKey
} from "@/lib/ui/theme-system/theme-registry";
export type {
  LiveUiThemeId,
  ReservedUiThemeId,
  ThemeColorScheme,
  ThemeSpec,
  UiThemeDefinition,
  UiThemeId
} from "@/lib/ui/theme-system/types";

