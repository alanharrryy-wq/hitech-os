import type { ClientThemeManifest } from "@/lib/ui/shell-system/types";

export const CLIENT_THEME_MANIFEST: ClientThemeManifest = {
  defaultTheme: "solstice",
  bindings: [
    {
      id: "aurora",
      iconFamily: "set_01_nebula_midnight"
    },
    {
      id: "solstice",
      iconFamily: "set_02_pearl_mist"
    },
    {
      id: "neon",
      iconFamily: "set_03_nova_rose"
    },
    {
      id: "slot_01",
      iconFamily: "set_01_nebula_midnight"
    },
    {
      id: "slot_02",
      iconFamily: "set_03_nova_rose"
    }
  ]
};

export function resolveIconFamilyByTheme(themeId: ClientThemeManifest["bindings"][number]["id"]) {
  return CLIENT_THEME_MANIFEST.bindings.find((binding) => binding.id === themeId)?.iconFamily ?? "set_02_pearl_mist";
}

