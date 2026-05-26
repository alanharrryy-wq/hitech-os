// PRISMA_CHART_LAB_POWER_PRESETS_V3
export type ChartLabVisualPresetId = "crystal-ops" | "neon-control" | "forensic-paper" | "war-room" | "mobile-sharp" | "tablet-touch" | "executive-dense" | "heat-beast" | "calm-intelligence";
export type ChartLabMotionPresetId = "still" | "subtle-premium" | "sweep-scan" | "pulse-alerts" | "cinematic-morph" | "forensic-replay" | "executive-snap" | "touch-smooth";
export type ChartLabInteractionPresetId = "observe" | "explore" | "explain" | "operate" | "touch";
export type ChartLabLabelPresetId = "off" | "smart-hotspots" | "forensic-badges" | "executive-compact" | "selected-only";

export type ChartLabVisualPreset = {
  id: ChartLabVisualPresetId;
  label: string;
  mood: string;
  palette: string[];
  background: string;
  visualIntensity: number;
  contrastPunch: number;
  glowAura: number;
  labelDensity: number;
  minSeriesOpacity: number;
  minLineOpacity: number;
  minAreaOpacity: number;
  minLabelContrast: number;
};

export type ChartLabMotionPreset = {
  id: ChartLabMotionPresetId;
  label: string;
  animation: boolean;
  duration: number;
  updateDuration: number;
  easing: string;
  stagger: number;
  universalTransition: "off" | "safe" | "full";
};

export type ChartLabInteractionPreset = {
  id: ChartLabInteractionPresetId;
  label: string;
  tooltipMode: string;
  hoverSpotlight: "off" | "soft" | "strong";
  clickBehavior: "none" | "pin" | "isolate" | "drill";
  zoomMode: "off" | "inside" | "slider" | "both";
  brushMode: "off" | "select" | "compare" | "filter";
};

export const CHART_LAB_VISUAL_PRESETS: Record<ChartLabVisualPresetId, ChartLabVisualPreset> = {
  "crystal-ops": { id: "crystal-ops", label: "Crystal Ops", mood: "clean glass operational surface", palette: ["#18d7ff", "#735cff", "#ff536d", "#ffb74d"], background: "transparent", visualIntensity: 74, contrastPunch: 72, glowAura: 10, labelDensity: 62, minSeriesOpacity: 0.42, minLineOpacity: 0.52, minAreaOpacity: 0.2, minLabelContrast: 0.74 },
  "neon-control": { id: "neon-control", label: "Neon Control", mood: "high contrast cyber control room", palette: ["#20f6ff", "#8d5cff", "#ff3fb7", "#ffe66d"], background: "#050816", visualIntensity: 142, contrastPunch: 148, glowAura: 42, labelDensity: 58, minSeriesOpacity: 0.46, minLineOpacity: 0.56, minAreaOpacity: 0.22, minLabelContrast: 0.82 },
  "forensic-paper": { id: "forensic-paper", label: "Forensic Paper", mood: "audit ready, bright, legible", palette: ["#1455d9", "#00a88f", "#d97706", "#dc2626"], background: "#f7f4ed", visualIntensity: 62, contrastPunch: 88, glowAura: 0, labelDensity: 78, minSeriesOpacity: 0.5, minLineOpacity: 0.58, minAreaOpacity: 0.18, minLabelContrast: 0.92 },
  "war-room": { id: "war-room", label: "War Room", mood: "dark operational pressure", palette: ["#18d7ff", "#705cff", "#ff3366", "#ff9f4d"], background: "#061229", visualIntensity: 156, contrastPunch: 164, glowAura: 48, labelDensity: 66, minSeriesOpacity: 0.5, minLineOpacity: 0.6, minAreaOpacity: 0.24, minLabelContrast: 0.9 },
  "mobile-sharp": { id: "mobile-sharp", label: "Mobile Sharp", mood: "small screen sharpness", palette: ["#10b981", "#06b6d4", "#6366f1", "#f43f5e"], background: "transparent", visualIntensity: 86, contrastPunch: 118, glowAura: 8, labelDensity: 34, minSeriesOpacity: 0.44, minLineOpacity: 0.54, minAreaOpacity: 0.2, minLabelContrast: 0.84 },
  "tablet-touch": { id: "tablet-touch", label: "Tablet Touch", mood: "finger friendly clarity", palette: ["#06b6d4", "#8b5cf6", "#f97316", "#22c55e"], background: "transparent", visualIntensity: 94, contrastPunch: 104, glowAura: 14, labelDensity: 52, minSeriesOpacity: 0.44, minLineOpacity: 0.54, minAreaOpacity: 0.2, minLabelContrast: 0.82 },
  "executive-dense": { id: "executive-dense", label: "Executive Dense", mood: "compact high signal", palette: ["#60a5fa", "#a78bfa", "#f472b6", "#facc15"], background: "transparent", visualIntensity: 104, contrastPunch: 112, glowAura: 18, labelDensity: 82, minSeriesOpacity: 0.46, minLineOpacity: 0.56, minAreaOpacity: 0.2, minLabelContrast: 0.88 },
  "heat-beast": { id: "heat-beast", label: "Heat Beast", mood: "maximum heatmap drama", palette: ["#0b1e50", "#1167dd", "#18d7ff", "#ff3366", "#ffe98f"], background: "#040915", visualIntensity: 176, contrastPunch: 172, glowAura: 58, labelDensity: 46, minSeriesOpacity: 0.5, minLineOpacity: 0.6, minAreaOpacity: 0.24, minLabelContrast: 0.9 },
  "calm-intelligence": { id: "calm-intelligence", label: "Calm Intelligence", mood: "quiet premium signal", palette: ["#3b82f6", "#14b8a6", "#a3e635", "#f59e0b"], background: "transparent", visualIntensity: 58, contrastPunch: 64, glowAura: 4, labelDensity: 56, minSeriesOpacity: 0.4, minLineOpacity: 0.5, minAreaOpacity: 0.2, minLabelContrast: 0.78 }
};

export const CHART_LAB_MOTION_PRESETS: Record<ChartLabMotionPresetId, ChartLabMotionPreset> = {
  still: { id: "still", label: "Still", animation: false, duration: 0, updateDuration: 0, easing: "linear", stagger: 0, universalTransition: "off" },
  "subtle-premium": { id: "subtle-premium", label: "Subtle Premium", animation: true, duration: 700, updateDuration: 800, easing: "cubicOut", stagger: 25, universalTransition: "safe" },
  "sweep-scan": { id: "sweep-scan", label: "Sweep Scan", animation: true, duration: 1100, updateDuration: 1200, easing: "quarticOut", stagger: 55, universalTransition: "safe" },
  "pulse-alerts": { id: "pulse-alerts", label: "Pulse Alerts", animation: true, duration: 1250, updateDuration: 1400, easing: "elasticOut", stagger: 40, universalTransition: "safe" },
  "cinematic-morph": { id: "cinematic-morph", label: "Cinematic Morph", animation: true, duration: 1600, updateDuration: 1900, easing: "cubicInOut", stagger: 80, universalTransition: "full" },
  "forensic-replay": { id: "forensic-replay", label: "Forensic Replay", animation: true, duration: 2200, updateDuration: 2600, easing: "linear", stagger: 110, universalTransition: "safe" },
  "executive-snap": { id: "executive-snap", label: "Executive Snap", animation: true, duration: 360, updateDuration: 440, easing: "cubicOut", stagger: 12, universalTransition: "off" },
  "touch-smooth": { id: "touch-smooth", label: "Touch Smooth", animation: true, duration: 760, updateDuration: 860, easing: "cubicOut", stagger: 22, universalTransition: "safe" }
};

export const CHART_LAB_INTERACTION_PRESETS: Record<ChartLabInteractionPresetId, ChartLabInteractionPreset> = {
  observe: { id: "observe", label: "Observe", tooltipMode: "simple", hoverSpotlight: "soft", clickBehavior: "none", zoomMode: "off", brushMode: "off" },
  explore: { id: "explore", label: "Explore", tooltipMode: "rich", hoverSpotlight: "strong", clickBehavior: "pin", zoomMode: "both", brushMode: "compare" },
  explain: { id: "explain", label: "Explain", tooltipMode: "forensic", hoverSpotlight: "strong", clickBehavior: "isolate", zoomMode: "inside", brushMode: "select" },
  operate: { id: "operate", label: "Operate", tooltipMode: "executive", hoverSpotlight: "strong", clickBehavior: "drill", zoomMode: "both", brushMode: "filter" },
  touch: { id: "touch", label: "Touch", tooltipMode: "touch", hoverSpotlight: "soft", clickBehavior: "pin", zoomMode: "inside", brushMode: "off" }
};

export const CHART_LAB_LABEL_PRESETS: Record<ChartLabLabelPresetId, { id: ChartLabLabelPresetId; label: string; mode: string; density: number }> = {
  off: { id: "off", label: "Off", mode: "off", density: 0 },
  "smart-hotspots": { id: "smart-hotspots", label: "Smart Hotspots", mode: "hotspots", density: 48 },
  "forensic-badges": { id: "forensic-badges", label: "Forensic Badges", mode: "badges", density: 74 },
  "executive-compact": { id: "executive-compact", label: "Executive Compact", mode: "compact", density: 56 },
  "selected-only": { id: "selected-only", label: "Selected Only", mode: "selected", density: 24 }
};

export function resolveChartLabVisualPreset(id: string): ChartLabVisualPreset {
  return CHART_LAB_VISUAL_PRESETS[id as ChartLabVisualPresetId] ?? CHART_LAB_VISUAL_PRESETS["crystal-ops"];
}

export function getVisualPresetVisibilityFloor(presetId: string) {
  const preset = resolveChartLabVisualPreset(presetId);
  return {
    minSeriesOpacity: preset.minSeriesOpacity,
    minLineOpacity: preset.minLineOpacity,
    minAreaOpacity: preset.minAreaOpacity,
    minLabelContrast: preset.minLabelContrast
  };
}

export function resolveChartLabMotionPreset(id: string): ChartLabMotionPreset {
  return CHART_LAB_MOTION_PRESETS[id as ChartLabMotionPresetId] ?? CHART_LAB_MOTION_PRESETS["subtle-premium"];
}

export function resolveChartLabInteractionPreset(id: string): ChartLabInteractionPreset {
  return CHART_LAB_INTERACTION_PRESETS[id as ChartLabInteractionPresetId] ?? CHART_LAB_INTERACTION_PRESETS.explore;
}
