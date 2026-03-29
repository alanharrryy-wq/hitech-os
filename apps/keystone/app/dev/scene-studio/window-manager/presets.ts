import type { ViewportBounds, WindowLayoutEntry, WindowPreset } from "./types";

export const BUILTIN_PRESET_IDS = ["debug", "presentation", "minimal"] as const;

export type BuiltinPresetId = (typeof BUILTIN_PRESET_IDS)[number];

function createState(state: Partial<WindowLayoutEntry>): Partial<WindowLayoutEntry> {
  return {
    ...(state.x !== undefined ? { x: state.x } : {}),
    ...(state.y !== undefined ? { y: state.y } : {}),
    ...(state.w !== undefined ? { w: state.w } : {}),
    ...(state.h !== undefined ? { h: state.h } : {}),
    ...(state.z !== undefined ? { z: state.z } : {}),
    ...(state.visible !== undefined ? { visible: state.visible } : {}),
    ...(state.collapsed !== undefined ? { collapsed: state.collapsed } : {})
  };
}

export function isBuiltinPreset(presetId: string): presetId is BuiltinPresetId {
  return (BUILTIN_PRESET_IDS as readonly string[]).includes(presetId);
}

export function buildBuiltinPresets(viewport: ViewportBounds): readonly WindowPreset[] {
  const rightColumnX = Math.max(viewport.width - 430, 20);
  const tallHeight = Math.max(Math.min(viewport.height - 140, 720), 300);
  const shortHeight = Math.max(Math.min((viewport.height - 180) / 2, 360), 180);

  return [
    {
      id: "debug",
      label: "Debug",
      windows: {
        "control-room-toolbar": createState({
          x: 16,
          y: 16,
          w: 360,
          h: 280,
          z: 1100,
          visible: true,
          collapsed: false
        }),
        "scene-editor": createState({
          x: 20,
          y: 112,
          w: 500,
          h: tallHeight,
          z: 1101,
          visible: true,
          collapsed: false
        }),
        "layer-debug": createState({
          x: rightColumnX,
          y: 20,
          w: 400,
          h: shortHeight + 120,
          z: 1102,
          visible: true,
          collapsed: false
        }),
        "scene-graph": createState({
          x: rightColumnX,
          y: 170 + shortHeight,
          w: 400,
          h: shortHeight,
          z: 1103,
          visible: true,
          collapsed: false
        })
      }
    },
    {
      id: "presentation",
      label: "Presentation",
      windows: {
        "control-room-toolbar": createState({
          x: 16,
          y: 16,
          w: 340,
          h: 220,
          z: 1100,
          visible: true,
          collapsed: false
        }),
        "scene-editor": createState({
          visible: false,
          collapsed: false
        }),
        "layer-debug": createState({
          visible: false,
          collapsed: false
        }),
        "scene-graph": createState({
          x: Math.max(viewport.width - 440, 16),
          y: Math.max(viewport.height - 280, 16),
          w: 420,
          h: 240,
          z: 1101,
          visible: true,
          collapsed: false
        })
      }
    },
    {
      id: "minimal",
      label: "Minimal",
      windows: {
        "control-room-toolbar": createState({
          x: 16,
          y: 16,
          w: 320,
          h: 200,
          z: 1100,
          visible: true,
          collapsed: false
        }),
        "scene-editor": createState({
          x: 20,
          y: 92,
          w: 440,
          h: 360,
          z: 1101,
          visible: true,
          collapsed: true
        }),
        "layer-debug": createState({
          visible: false,
          collapsed: false
        }),
        "scene-graph": createState({
          visible: false,
          collapsed: false
        })
      }
    }
  ];
}

export function findBuiltinPreset(
  presetId: string,
  viewport: ViewportBounds
): WindowPreset | undefined {
  return buildBuiltinPresets(viewport).find((preset) => preset.id === presetId);
}
