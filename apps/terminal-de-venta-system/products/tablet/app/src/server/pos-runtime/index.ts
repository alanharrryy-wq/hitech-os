export const TABLET_RUNTIME_MODES = ["standalone", "managed", "degraded_managed"] as const;

export type TabletRuntimeMode = (typeof TABLET_RUNTIME_MODES)[number];

export type TabletRuntimeInfo = {
  mode: TabletRuntimeMode;
  rawMode: string | null;
  localSalesAllowed: true;
  pcRequiredForBasicSale: false;
  warning: string | null;
};

export function getTabletRuntimeInfo(): TabletRuntimeInfo {
  const rawMode = process.env.TABLET_RUNTIME_MODE?.trim() || null;
  if (rawMode && TABLET_RUNTIME_MODES.includes(rawMode as TabletRuntimeMode)) {
    return {
      mode: rawMode as TabletRuntimeMode,
      rawMode,
      localSalesAllowed: true,
      pcRequiredForBasicSale: false,
      warning: null
    };
  }

  return {
    mode: "standalone",
    rawMode,
    localSalesAllowed: true,
    pcRequiredForBasicSale: false,
    warning: rawMode ? `TABLET_RUNTIME_MODE desconocido (${rawMode}); usando standalone.` : null
  };
}

export function getTabletRuntimeMeta() {
  const info = getTabletRuntimeInfo();
  return {
    runtimeMode: info.mode,
    rawRuntimeMode: info.rawMode,
    localSalesAllowed: info.localSalesAllowed,
    pcRequiredForBasicSale: info.pcRequiredForBasicSale,
    warning: info.warning
  };
}
