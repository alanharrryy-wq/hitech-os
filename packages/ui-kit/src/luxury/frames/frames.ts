export type FrameStyleId = "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";
export type FrameSurfaceId = "controlRoomHud" | "pitchSurface" | "kpiWidget";

export type FramePresetId =
  | "LIQUID_GLASS_CONTROL_ROOM_HUD"
  | "LIQUID_GLASS_PITCH_SURFACE"
  | "LIQUID_GLASS_KPI_WIDGET"
  | "GOLD_NOIR_TERMINAL_CONTROL_ROOM_HUD"
  | "GOLD_NOIR_TERMINAL_PITCH_SURFACE"
  | "GOLD_NOIR_TERMINAL_KPI_WIDGET"
  | "GRAPHITE_PRISM_ISO_CONTROL_ROOM_HUD"
  | "GRAPHITE_PRISM_ISO_PITCH_SURFACE"
  | "GRAPHITE_PRISM_ISO_KPI_WIDGET";

export interface FramePreset {
  readonly id: FramePresetId;
  readonly style: FrameStyleId;
  readonly surface: FrameSurfaceId;
  readonly signatureRows: number;
  readonly frameStyleAttr: "liquid-glass" | "gold-noir-terminal" | "graphite-prism-iso";
  readonly frameSurfaceAttr: "control-room-hud" | "pitch-surface" | "kpi-widget";
  readonly className: string;
}

const LIQUID_GLASS_SIGNATURE_CATALOG_COUNT = 1400;
const GOLD_NOIR_SIGNATURE_CATALOG_COUNT = 1400;
const GRAPHITE_PRISM_SIGNATURE_CATALOG_COUNT = 1400;

export const FRAME_PRESETS: Readonly<Record<FramePresetId, FramePreset>> = Object.freeze({
  LIQUID_GLASS_CONTROL_ROOM_HUD: {
    id: "LIQUID_GLASS_CONTROL_ROOM_HUD",
    style: "LIQUID_GLASS",
    surface: "controlRoomHud",
    signatureRows: LIQUID_GLASS_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "liquid-glass",
    frameSurfaceAttr: "control-room-hud",
    className: "ui-frame ui-frame--liquid-glass ui-frame--control-room-hud"
  },
  LIQUID_GLASS_PITCH_SURFACE: {
    id: "LIQUID_GLASS_PITCH_SURFACE",
    style: "LIQUID_GLASS",
    surface: "pitchSurface",
    signatureRows: LIQUID_GLASS_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "liquid-glass",
    frameSurfaceAttr: "pitch-surface",
    className: "ui-frame ui-frame--liquid-glass ui-frame--pitch-surface"
  },
  LIQUID_GLASS_KPI_WIDGET: {
    id: "LIQUID_GLASS_KPI_WIDGET",
    style: "LIQUID_GLASS",
    surface: "kpiWidget",
    signatureRows: LIQUID_GLASS_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "liquid-glass",
    frameSurfaceAttr: "kpi-widget",
    className: "ui-frame ui-frame--liquid-glass ui-frame--kpi-widget"
  },
  GOLD_NOIR_TERMINAL_CONTROL_ROOM_HUD: {
    id: "GOLD_NOIR_TERMINAL_CONTROL_ROOM_HUD",
    style: "GOLD_NOIR_TERMINAL",
    surface: "controlRoomHud",
    signatureRows: GOLD_NOIR_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "gold-noir-terminal",
    frameSurfaceAttr: "control-room-hud",
    className: "ui-frame ui-frame--gold-noir-terminal ui-frame--control-room-hud"
  },
  GOLD_NOIR_TERMINAL_PITCH_SURFACE: {
    id: "GOLD_NOIR_TERMINAL_PITCH_SURFACE",
    style: "GOLD_NOIR_TERMINAL",
    surface: "pitchSurface",
    signatureRows: GOLD_NOIR_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "gold-noir-terminal",
    frameSurfaceAttr: "pitch-surface",
    className: "ui-frame ui-frame--gold-noir-terminal ui-frame--pitch-surface"
  },
  GOLD_NOIR_TERMINAL_KPI_WIDGET: {
    id: "GOLD_NOIR_TERMINAL_KPI_WIDGET",
    style: "GOLD_NOIR_TERMINAL",
    surface: "kpiWidget",
    signatureRows: GOLD_NOIR_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "gold-noir-terminal",
    frameSurfaceAttr: "kpi-widget",
    className: "ui-frame ui-frame--gold-noir-terminal ui-frame--kpi-widget"
  },
  GRAPHITE_PRISM_ISO_CONTROL_ROOM_HUD: {
    id: "GRAPHITE_PRISM_ISO_CONTROL_ROOM_HUD",
    style: "GRAPHITE_PRISM_ISO",
    surface: "controlRoomHud",
    signatureRows: GRAPHITE_PRISM_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "graphite-prism-iso",
    frameSurfaceAttr: "control-room-hud",
    className: "ui-frame ui-frame--graphite-prism-iso ui-frame--control-room-hud"
  },
  GRAPHITE_PRISM_ISO_PITCH_SURFACE: {
    id: "GRAPHITE_PRISM_ISO_PITCH_SURFACE",
    style: "GRAPHITE_PRISM_ISO",
    surface: "pitchSurface",
    signatureRows: GRAPHITE_PRISM_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "graphite-prism-iso",
    frameSurfaceAttr: "pitch-surface",
    className: "ui-frame ui-frame--graphite-prism-iso ui-frame--pitch-surface"
  },
  GRAPHITE_PRISM_ISO_KPI_WIDGET: {
    id: "GRAPHITE_PRISM_ISO_KPI_WIDGET",
    style: "GRAPHITE_PRISM_ISO",
    surface: "kpiWidget",
    signatureRows: GRAPHITE_PRISM_SIGNATURE_CATALOG_COUNT,
    frameStyleAttr: "graphite-prism-iso",
    frameSurfaceAttr: "kpi-widget",
    className: "ui-frame ui-frame--graphite-prism-iso ui-frame--kpi-widget"
  }
});

export const FRAME_PRESET_BY_SURFACE: Readonly<Record<FrameSurfaceId, FramePresetId>> = Object.freeze({
  controlRoomHud: "LIQUID_GLASS_CONTROL_ROOM_HUD",
  pitchSurface: "GOLD_NOIR_TERMINAL_PITCH_SURFACE",
  kpiWidget: "GRAPHITE_PRISM_ISO_KPI_WIDGET"
});

export const FRAME_SIGNATURE_CATALOG_COUNTS = Object.freeze({
  liquidGlass: LIQUID_GLASS_SIGNATURE_CATALOG_COUNT,
  goldNoir: GOLD_NOIR_SIGNATURE_CATALOG_COUNT,
  graphitePrism: GRAPHITE_PRISM_SIGNATURE_CATALOG_COUNT
});

const PRESET_LOOKUP = new Map<`${FrameStyleId}:${FrameSurfaceId}`, FramePresetId>([
  ["LIQUID_GLASS:controlRoomHud", "LIQUID_GLASS_CONTROL_ROOM_HUD"],
  ["LIQUID_GLASS:pitchSurface", "LIQUID_GLASS_PITCH_SURFACE"],
  ["LIQUID_GLASS:kpiWidget", "LIQUID_GLASS_KPI_WIDGET"],
  ["GOLD_NOIR_TERMINAL:controlRoomHud", "GOLD_NOIR_TERMINAL_CONTROL_ROOM_HUD"],
  ["GOLD_NOIR_TERMINAL:pitchSurface", "GOLD_NOIR_TERMINAL_PITCH_SURFACE"],
  ["GOLD_NOIR_TERMINAL:kpiWidget", "GOLD_NOIR_TERMINAL_KPI_WIDGET"],
  ["GRAPHITE_PRISM_ISO:controlRoomHud", "GRAPHITE_PRISM_ISO_CONTROL_ROOM_HUD"],
  ["GRAPHITE_PRISM_ISO:pitchSurface", "GRAPHITE_PRISM_ISO_PITCH_SURFACE"],
  ["GRAPHITE_PRISM_ISO:kpiWidget", "GRAPHITE_PRISM_ISO_KPI_WIDGET"]
]);

export function getFramePreset(id: FramePresetId): FramePreset {
  return FRAME_PRESETS[id];
}

export function resolveFramePresetId(style: FrameStyleId, surface: FrameSurfaceId): FramePresetId {
  const key = `${style}:${surface}` as const;
  const presetId = PRESET_LOOKUP.get(key);

  if (!presetId) {
    throw new Error(`Missing frame preset for ${style}/${surface}`);
  }

  return presetId;
}

export function resolveFramePreset(style: FrameStyleId, surface: FrameSurfaceId): FramePreset {
  return getFramePreset(resolveFramePresetId(style, surface));
}
