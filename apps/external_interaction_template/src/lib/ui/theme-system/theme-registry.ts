import { UI_THEME_IDS, UI_THEME_SPECS } from "@/lib/ui/theme-system/theme-specs";
import type {
  ReservedUiThemeId,
  ThemeSpec,
  UiThemeDefinition,
  UiThemeId
} from "@/lib/ui/theme-system/types";

export const UI_THEME_STORAGE_KEY = "hitech.external_interaction_template.ui_theme";
export const DEFAULT_UI_THEME: UiThemeId = "solstice";

export interface ReservedThemeSelectorVisibility {
  slot_01: boolean;
  slot_02: boolean;
}

export const RESERVED_THEME_SELECTOR_VISIBILITY: ReservedThemeSelectorVisibility = {
  slot_01: process.env.NEXT_PUBLIC_EIT_THEME_SLOT_01_VISIBLE === "1",
  slot_02: process.env.NEXT_PUBLIC_EIT_THEME_SLOT_02_VISIBLE === "1"
};

function isReservedUiThemeId(value: UiThemeId): value is ReservedUiThemeId {
  return value === "slot_01" || value === "slot_02";
}

export function resolveSelectorVisibility(themeId: UiThemeId): boolean {
  if (!isReservedUiThemeId(themeId)) return true;
  return RESERVED_THEME_SELECTOR_VISIBILITY[themeId];
}

export const UI_THEMES: readonly UiThemeDefinition[] = UI_THEME_IDS.map((id) => {
  const spec = UI_THEME_SPECS[id];
  return {
    id,
    labelKey: spec.meta.labelKey,
    premium: spec.meta.premium,
    reserved: spec.meta.slot === "reserved",
    selectorVisible: resolveSelectorVisibility(id)
  };
});

export const VISIBLE_UI_THEMES: readonly UiThemeDefinition[] = UI_THEMES.filter((entry) => entry.selectorVisible);

const UI_THEME_SET = new Set<UiThemeId>(UI_THEME_IDS);

export function isUiThemeId(value: unknown): value is UiThemeId {
  return typeof value === "string" && UI_THEME_SET.has(value as UiThemeId);
}

export function resolveUiThemeId(value: unknown, fallback: UiThemeId = DEFAULT_UI_THEME): UiThemeId {
  return isUiThemeId(value) ? value : fallback;
}

export function getUiThemeSpec(themeId: UiThemeId): ThemeSpec {
  return UI_THEME_SPECS[themeId];
}

export function getThemeLabelKey(themeId: UiThemeId): string {
  return getUiThemeSpec(themeId).meta.labelKey;
}

