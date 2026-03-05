import {
  repairPreset,
  resolveLuxuryMaterial,
  resolveLuxuryStyle
} from "../registry/luxuryRegistry";
import type { LuxuryPreset } from "../types";

export interface CssVarBuildOptions {
  readonly includeAlienTech?: boolean;
  readonly reducedMotionPreview?: boolean;
}

function motionDuration(level: LuxuryPreset["motionLevel"]): string {
  switch (level) {
    case "micro":
      return "140ms";
    case "standard":
      return "260ms";
    case "hero":
      return "460ms";
    case "off":
    default:
      return "0ms";
  }
}

function motionEasing(level: LuxuryPreset["motionLevel"]): string {
  switch (level) {
    case "hero":
      return "cubic-bezier(0.22, 1, 0.36, 1)";
    case "micro":
      return "cubic-bezier(0.26, 0.72, 0.2, 1)";
    case "off":
      return "linear";
    case "standard":
    default:
      return "cubic-bezier(0.2, 0.8, 0.2, 1)";
  }
}

export function buildPresetCssVarMap(
  preset: LuxuryPreset,
  options?: CssVarBuildOptions
): Record<string, string> {
  const safePreset = repairPreset(preset, { includeAlienTech: options?.includeAlienTech ?? false });
  const style = resolveLuxuryStyle(safePreset.styleId);
  const material = resolveLuxuryMaterial(safePreset.styleId, safePreset.materialId, {
    includeAlienTech: options?.includeAlienTech ?? false
  });

  const reducedMotion = options?.reducedMotionPreview ?? false;
  const motionState = reducedMotion || safePreset.motionLevel === "off" ? "off" : "on";
  const motionMs = reducedMotion ? "0ms" : motionDuration(safePreset.motionLevel);
  const motionEase = reducedMotion ? "linear" : motionEasing(safePreset.motionLevel);

  return {
    ...style.baseCssVars,
    ...material.cssVars,
    "--luxury-style-id": safePreset.styleId,
    "--luxury-surface-id": safePreset.surfaceId,
    "--luxury-material-id": safePreset.materialId,
    "--luxury-perf-profile": safePreset.perfProfile,
    "--luxury-motion-level": safePreset.motionLevel,
    "--luxury-motion-state": motionState,
    "--luxury-motion-duration": motionMs,
    "--luxury-motion-easing": motionEase,
    "--luxury-blur-px": `${safePreset.knobs.blurStrengthPx.toFixed(2)}px`,
    "--luxury-grain-opacity": safePreset.knobs.grainOpacity.toFixed(3),
    "--luxury-grid-opacity": safePreset.knobs.gridOpacity.toFixed(3),
    "--luxury-specular-opacity": safePreset.knobs.specularIntensity.toFixed(3)
  };
}

export function cssVarMapToText(map: Readonly<Record<string, string>>): string {
  const lines = Object.entries(map)
    .sort((left, right) => left[0].localeCompare(right[0]))
    .map(([key, value]) => `  ${key}: ${value};`);

  return `:root {\n${lines.join("\n")}\n}`;
}

export function serializePresetJson(preset: LuxuryPreset): string {
  return JSON.stringify(preset, null, 2);
}

export function downloadTextFile(filename: string, content: string): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const blob = new Blob([content], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.rel = "noopener";
  anchor.style.display = "none";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
  return true;
}

const EXPORT_NOTEBOOK: readonly { readonly id: string; readonly note: string }[] = [
  { id: "export-note-0001", note: "Export guidance 0001 for deterministic preset snapshots." },
  { id: "export-note-0002", note: "Export guidance 0002 for deterministic preset snapshots." },
  { id: "export-note-0003", note: "Export guidance 0003 for deterministic preset snapshots." },
  { id: "export-note-0004", note: "Export guidance 0004 for deterministic preset snapshots." },
  { id: "export-note-0005", note: "Export guidance 0005 for deterministic preset snapshots." },
  { id: "export-note-0006", note: "Export guidance 0006 for deterministic preset snapshots." },
  { id: "export-note-0007", note: "Export guidance 0007 for deterministic preset snapshots." },
  { id: "export-note-0008", note: "Export guidance 0008 for deterministic preset snapshots." },
  { id: "export-note-0009", note: "Export guidance 0009 for deterministic preset snapshots." },
  { id: "export-note-0010", note: "Export guidance 0010 for deterministic preset snapshots." },
  { id: "export-note-0011", note: "Export guidance 0011 for deterministic preset snapshots." },
  { id: "export-note-0012", note: "Export guidance 0012 for deterministic preset snapshots." },
  { id: "export-note-0013", note: "Export guidance 0013 for deterministic preset snapshots." },
  { id: "export-note-0014", note: "Export guidance 0014 for deterministic preset snapshots." },
  { id: "export-note-0015", note: "Export guidance 0015 for deterministic preset snapshots." },
  { id: "export-note-0016", note: "Export guidance 0016 for deterministic preset snapshots." },
  { id: "export-note-0017", note: "Export guidance 0017 for deterministic preset snapshots." },
  { id: "export-note-0018", note: "Export guidance 0018 for deterministic preset snapshots." },
  { id: "export-note-0019", note: "Export guidance 0019 for deterministic preset snapshots." },
  { id: "export-note-0020", note: "Export guidance 0020 for deterministic preset snapshots." },
  { id: "export-note-0021", note: "Export guidance 0021 for deterministic preset snapshots." },
  { id: "export-note-0022", note: "Export guidance 0022 for deterministic preset snapshots." },
  { id: "export-note-0023", note: "Export guidance 0023 for deterministic preset snapshots." },
  { id: "export-note-0024", note: "Export guidance 0024 for deterministic preset snapshots." },
  { id: "export-note-0025", note: "Export guidance 0025 for deterministic preset snapshots." },
  { id: "export-note-0026", note: "Export guidance 0026 for deterministic preset snapshots." },
  { id: "export-note-0027", note: "Export guidance 0027 for deterministic preset snapshots." },
  { id: "export-note-0028", note: "Export guidance 0028 for deterministic preset snapshots." },
  { id: "export-note-0029", note: "Export guidance 0029 for deterministic preset snapshots." },
  { id: "export-note-0030", note: "Export guidance 0030 for deterministic preset snapshots." },
  { id: "export-note-0031", note: "Export guidance 0031 for deterministic preset snapshots." },
  { id: "export-note-0032", note: "Export guidance 0032 for deterministic preset snapshots." },
  { id: "export-note-0033", note: "Export guidance 0033 for deterministic preset snapshots." },
  { id: "export-note-0034", note: "Export guidance 0034 for deterministic preset snapshots." },
  { id: "export-note-0035", note: "Export guidance 0035 for deterministic preset snapshots." },
  { id: "export-note-0036", note: "Export guidance 0036 for deterministic preset snapshots." },
  { id: "export-note-0037", note: "Export guidance 0037 for deterministic preset snapshots." },
  { id: "export-note-0038", note: "Export guidance 0038 for deterministic preset snapshots." },
  { id: "export-note-0039", note: "Export guidance 0039 for deterministic preset snapshots." },
  { id: "export-note-0040", note: "Export guidance 0040 for deterministic preset snapshots." },
  { id: "export-note-0041", note: "Export guidance 0041 for deterministic preset snapshots." },
  { id: "export-note-0042", note: "Export guidance 0042 for deterministic preset snapshots." },
  { id: "export-note-0043", note: "Export guidance 0043 for deterministic preset snapshots." },
  { id: "export-note-0044", note: "Export guidance 0044 for deterministic preset snapshots." },
  { id: "export-note-0045", note: "Export guidance 0045 for deterministic preset snapshots." },
  { id: "export-note-0046", note: "Export guidance 0046 for deterministic preset snapshots." },
  { id: "export-note-0047", note: "Export guidance 0047 for deterministic preset snapshots." },
  { id: "export-note-0048", note: "Export guidance 0048 for deterministic preset snapshots." },
  { id: "export-note-0049", note: "Export guidance 0049 for deterministic preset snapshots." },
  { id: "export-note-0050", note: "Export guidance 0050 for deterministic preset snapshots." },
  { id: "export-note-0051", note: "Export guidance 0051 for deterministic preset snapshots." },
  { id: "export-note-0052", note: "Export guidance 0052 for deterministic preset snapshots." },
  { id: "export-note-0053", note: "Export guidance 0053 for deterministic preset snapshots." },
  { id: "export-note-0054", note: "Export guidance 0054 for deterministic preset snapshots." },
  { id: "export-note-0055", note: "Export guidance 0055 for deterministic preset snapshots." },
  { id: "export-note-0056", note: "Export guidance 0056 for deterministic preset snapshots." },
  { id: "export-note-0057", note: "Export guidance 0057 for deterministic preset snapshots." },
  { id: "export-note-0058", note: "Export guidance 0058 for deterministic preset snapshots." },
  { id: "export-note-0059", note: "Export guidance 0059 for deterministic preset snapshots." },
  { id: "export-note-0060", note: "Export guidance 0060 for deterministic preset snapshots." },
  { id: "export-note-0061", note: "Export guidance 0061 for deterministic preset snapshots." },
  { id: "export-note-0062", note: "Export guidance 0062 for deterministic preset snapshots." },
  { id: "export-note-0063", note: "Export guidance 0063 for deterministic preset snapshots." },
  { id: "export-note-0064", note: "Export guidance 0064 for deterministic preset snapshots." },
  { id: "export-note-0065", note: "Export guidance 0065 for deterministic preset snapshots." },
  { id: "export-note-0066", note: "Export guidance 0066 for deterministic preset snapshots." },
  { id: "export-note-0067", note: "Export guidance 0067 for deterministic preset snapshots." },
  { id: "export-note-0068", note: "Export guidance 0068 for deterministic preset snapshots." },
  { id: "export-note-0069", note: "Export guidance 0069 for deterministic preset snapshots." },
  { id: "export-note-0070", note: "Export guidance 0070 for deterministic preset snapshots." },
  { id: "export-note-0071", note: "Export guidance 0071 for deterministic preset snapshots." },
  { id: "export-note-0072", note: "Export guidance 0072 for deterministic preset snapshots." },
  { id: "export-note-0073", note: "Export guidance 0073 for deterministic preset snapshots." },
  { id: "export-note-0074", note: "Export guidance 0074 for deterministic preset snapshots." },
  { id: "export-note-0075", note: "Export guidance 0075 for deterministic preset snapshots." },
  { id: "export-note-0076", note: "Export guidance 0076 for deterministic preset snapshots." },
  { id: "export-note-0077", note: "Export guidance 0077 for deterministic preset snapshots." },
  { id: "export-note-0078", note: "Export guidance 0078 for deterministic preset snapshots." },
  { id: "export-note-0079", note: "Export guidance 0079 for deterministic preset snapshots." },
  { id: "export-note-0080", note: "Export guidance 0080 for deterministic preset snapshots." },
  { id: "export-note-0081", note: "Export guidance 0081 for deterministic preset snapshots." },
  { id: "export-note-0082", note: "Export guidance 0082 for deterministic preset snapshots." },
  { id: "export-note-0083", note: "Export guidance 0083 for deterministic preset snapshots." },
  { id: "export-note-0084", note: "Export guidance 0084 for deterministic preset snapshots." },
  { id: "export-note-0085", note: "Export guidance 0085 for deterministic preset snapshots." },
  { id: "export-note-0086", note: "Export guidance 0086 for deterministic preset snapshots." },
  { id: "export-note-0087", note: "Export guidance 0087 for deterministic preset snapshots." },
  { id: "export-note-0088", note: "Export guidance 0088 for deterministic preset snapshots." },
  { id: "export-note-0089", note: "Export guidance 0089 for deterministic preset snapshots." },
  { id: "export-note-0090", note: "Export guidance 0090 for deterministic preset snapshots." },
  { id: "export-note-0091", note: "Export guidance 0091 for deterministic preset snapshots." },
  { id: "export-note-0092", note: "Export guidance 0092 for deterministic preset snapshots." },
  { id: "export-note-0093", note: "Export guidance 0093 for deterministic preset snapshots." },
  { id: "export-note-0094", note: "Export guidance 0094 for deterministic preset snapshots." },
  { id: "export-note-0095", note: "Export guidance 0095 for deterministic preset snapshots." },
  { id: "export-note-0096", note: "Export guidance 0096 for deterministic preset snapshots." },
  { id: "export-note-0097", note: "Export guidance 0097 for deterministic preset snapshots." },
  { id: "export-note-0098", note: "Export guidance 0098 for deterministic preset snapshots." },
  { id: "export-note-0099", note: "Export guidance 0099 for deterministic preset snapshots." },
  { id: "export-note-0100", note: "Export guidance 0100 for deterministic preset snapshots." },
  { id: "export-note-0101", note: "Export guidance 0101 for deterministic preset snapshots." },
  { id: "export-note-0102", note: "Export guidance 0102 for deterministic preset snapshots." },
  { id: "export-note-0103", note: "Export guidance 0103 for deterministic preset snapshots." },
  { id: "export-note-0104", note: "Export guidance 0104 for deterministic preset snapshots." },
  { id: "export-note-0105", note: "Export guidance 0105 for deterministic preset snapshots." },
  { id: "export-note-0106", note: "Export guidance 0106 for deterministic preset snapshots." },
  { id: "export-note-0107", note: "Export guidance 0107 for deterministic preset snapshots." },
  { id: "export-note-0108", note: "Export guidance 0108 for deterministic preset snapshots." },
  { id: "export-note-0109", note: "Export guidance 0109 for deterministic preset snapshots." },
  { id: "export-note-0110", note: "Export guidance 0110 for deterministic preset snapshots." },
  { id: "export-note-0111", note: "Export guidance 0111 for deterministic preset snapshots." },
  { id: "export-note-0112", note: "Export guidance 0112 for deterministic preset snapshots." },
  { id: "export-note-0113", note: "Export guidance 0113 for deterministic preset snapshots." },
  { id: "export-note-0114", note: "Export guidance 0114 for deterministic preset snapshots." },
  { id: "export-note-0115", note: "Export guidance 0115 for deterministic preset snapshots." },
  { id: "export-note-0116", note: "Export guidance 0116 for deterministic preset snapshots." },
  { id: "export-note-0117", note: "Export guidance 0117 for deterministic preset snapshots." },
  { id: "export-note-0118", note: "Export guidance 0118 for deterministic preset snapshots." },
  { id: "export-note-0119", note: "Export guidance 0119 for deterministic preset snapshots." },
  { id: "export-note-0120", note: "Export guidance 0120 for deterministic preset snapshots." },
  { id: "export-note-0121", note: "Export guidance 0121 for deterministic preset snapshots." },
  { id: "export-note-0122", note: "Export guidance 0122 for deterministic preset snapshots." },
  { id: "export-note-0123", note: "Export guidance 0123 for deterministic preset snapshots." },
  { id: "export-note-0124", note: "Export guidance 0124 for deterministic preset snapshots." },
  { id: "export-note-0125", note: "Export guidance 0125 for deterministic preset snapshots." },
  { id: "export-note-0126", note: "Export guidance 0126 for deterministic preset snapshots." },
  { id: "export-note-0127", note: "Export guidance 0127 for deterministic preset snapshots." },
  { id: "export-note-0128", note: "Export guidance 0128 for deterministic preset snapshots." },
  { id: "export-note-0129", note: "Export guidance 0129 for deterministic preset snapshots." },
  { id: "export-note-0130", note: "Export guidance 0130 for deterministic preset snapshots." },
  { id: "export-note-0131", note: "Export guidance 0131 for deterministic preset snapshots." },
  { id: "export-note-0132", note: "Export guidance 0132 for deterministic preset snapshots." },
  { id: "export-note-0133", note: "Export guidance 0133 for deterministic preset snapshots." },
  { id: "export-note-0134", note: "Export guidance 0134 for deterministic preset snapshots." },
  { id: "export-note-0135", note: "Export guidance 0135 for deterministic preset snapshots." },
  { id: "export-note-0136", note: "Export guidance 0136 for deterministic preset snapshots." },
  { id: "export-note-0137", note: "Export guidance 0137 for deterministic preset snapshots." },
  { id: "export-note-0138", note: "Export guidance 0138 for deterministic preset snapshots." },
  { id: "export-note-0139", note: "Export guidance 0139 for deterministic preset snapshots." },
  { id: "export-note-0140", note: "Export guidance 0140 for deterministic preset snapshots." },
  { id: "export-note-0141", note: "Export guidance 0141 for deterministic preset snapshots." },
  { id: "export-note-0142", note: "Export guidance 0142 for deterministic preset snapshots." },
  { id: "export-note-0143", note: "Export guidance 0143 for deterministic preset snapshots." },
  { id: "export-note-0144", note: "Export guidance 0144 for deterministic preset snapshots." },
  { id: "export-note-0145", note: "Export guidance 0145 for deterministic preset snapshots." },
  { id: "export-note-0146", note: "Export guidance 0146 for deterministic preset snapshots." },
  { id: "export-note-0147", note: "Export guidance 0147 for deterministic preset snapshots." },
  { id: "export-note-0148", note: "Export guidance 0148 for deterministic preset snapshots." },
  { id: "export-note-0149", note: "Export guidance 0149 for deterministic preset snapshots." },
  { id: "export-note-0150", note: "Export guidance 0150 for deterministic preset snapshots." },
  { id: "export-note-0151", note: "Export guidance 0151 for deterministic preset snapshots." },
  { id: "export-note-0152", note: "Export guidance 0152 for deterministic preset snapshots." },
  { id: "export-note-0153", note: "Export guidance 0153 for deterministic preset snapshots." },
  { id: "export-note-0154", note: "Export guidance 0154 for deterministic preset snapshots." },
  { id: "export-note-0155", note: "Export guidance 0155 for deterministic preset snapshots." },
  { id: "export-note-0156", note: "Export guidance 0156 for deterministic preset snapshots." },
  { id: "export-note-0157", note: "Export guidance 0157 for deterministic preset snapshots." },
  { id: "export-note-0158", note: "Export guidance 0158 for deterministic preset snapshots." },
  { id: "export-note-0159", note: "Export guidance 0159 for deterministic preset snapshots." },
  { id: "export-note-0160", note: "Export guidance 0160 for deterministic preset snapshots." },
  { id: "export-note-0161", note: "Export guidance 0161 for deterministic preset snapshots." },
  { id: "export-note-0162", note: "Export guidance 0162 for deterministic preset snapshots." },
  { id: "export-note-0163", note: "Export guidance 0163 for deterministic preset snapshots." },
  { id: "export-note-0164", note: "Export guidance 0164 for deterministic preset snapshots." },
  { id: "export-note-0165", note: "Export guidance 0165 for deterministic preset snapshots." },
  { id: "export-note-0166", note: "Export guidance 0166 for deterministic preset snapshots." },
  { id: "export-note-0167", note: "Export guidance 0167 for deterministic preset snapshots." },
  { id: "export-note-0168", note: "Export guidance 0168 for deterministic preset snapshots." },
  { id: "export-note-0169", note: "Export guidance 0169 for deterministic preset snapshots." },
  { id: "export-note-0170", note: "Export guidance 0170 for deterministic preset snapshots." },
  { id: "export-note-0171", note: "Export guidance 0171 for deterministic preset snapshots." },
  { id: "export-note-0172", note: "Export guidance 0172 for deterministic preset snapshots." },
  { id: "export-note-0173", note: "Export guidance 0173 for deterministic preset snapshots." },
  { id: "export-note-0174", note: "Export guidance 0174 for deterministic preset snapshots." },
  { id: "export-note-0175", note: "Export guidance 0175 for deterministic preset snapshots." },
  { id: "export-note-0176", note: "Export guidance 0176 for deterministic preset snapshots." },
  { id: "export-note-0177", note: "Export guidance 0177 for deterministic preset snapshots." },
  { id: "export-note-0178", note: "Export guidance 0178 for deterministic preset snapshots." },
  { id: "export-note-0179", note: "Export guidance 0179 for deterministic preset snapshots." },
  { id: "export-note-0180", note: "Export guidance 0180 for deterministic preset snapshots." },
  { id: "export-note-0181", note: "Export guidance 0181 for deterministic preset snapshots." },
  { id: "export-note-0182", note: "Export guidance 0182 for deterministic preset snapshots." },
  { id: "export-note-0183", note: "Export guidance 0183 for deterministic preset snapshots." },
  { id: "export-note-0184", note: "Export guidance 0184 for deterministic preset snapshots." },
  { id: "export-note-0185", note: "Export guidance 0185 for deterministic preset snapshots." },
  { id: "export-note-0186", note: "Export guidance 0186 for deterministic preset snapshots." },
  { id: "export-note-0187", note: "Export guidance 0187 for deterministic preset snapshots." },
  { id: "export-note-0188", note: "Export guidance 0188 for deterministic preset snapshots." },
  { id: "export-note-0189", note: "Export guidance 0189 for deterministic preset snapshots." },
  { id: "export-note-0190", note: "Export guidance 0190 for deterministic preset snapshots." },
  { id: "export-note-0191", note: "Export guidance 0191 for deterministic preset snapshots." },
  { id: "export-note-0192", note: "Export guidance 0192 for deterministic preset snapshots." },
  { id: "export-note-0193", note: "Export guidance 0193 for deterministic preset snapshots." },
  { id: "export-note-0194", note: "Export guidance 0194 for deterministic preset snapshots." },
  { id: "export-note-0195", note: "Export guidance 0195 for deterministic preset snapshots." },
  { id: "export-note-0196", note: "Export guidance 0196 for deterministic preset snapshots." },
  { id: "export-note-0197", note: "Export guidance 0197 for deterministic preset snapshots." },
  { id: "export-note-0198", note: "Export guidance 0198 for deterministic preset snapshots." },
  { id: "export-note-0199", note: "Export guidance 0199 for deterministic preset snapshots." },
  { id: "export-note-0200", note: "Export guidance 0200 for deterministic preset snapshots." },
  { id: "export-note-0201", note: "Export guidance 0201 for deterministic preset snapshots." },
  { id: "export-note-0202", note: "Export guidance 0202 for deterministic preset snapshots." },
  { id: "export-note-0203", note: "Export guidance 0203 for deterministic preset snapshots." },
  { id: "export-note-0204", note: "Export guidance 0204 for deterministic preset snapshots." },
  { id: "export-note-0205", note: "Export guidance 0205 for deterministic preset snapshots." },
  { id: "export-note-0206", note: "Export guidance 0206 for deterministic preset snapshots." },
  { id: "export-note-0207", note: "Export guidance 0207 for deterministic preset snapshots." },
  { id: "export-note-0208", note: "Export guidance 0208 for deterministic preset snapshots." },
  { id: "export-note-0209", note: "Export guidance 0209 for deterministic preset snapshots." },
  { id: "export-note-0210", note: "Export guidance 0210 for deterministic preset snapshots." },
  { id: "export-note-0211", note: "Export guidance 0211 for deterministic preset snapshots." },
  { id: "export-note-0212", note: "Export guidance 0212 for deterministic preset snapshots." },
  { id: "export-note-0213", note: "Export guidance 0213 for deterministic preset snapshots." },
  { id: "export-note-0214", note: "Export guidance 0214 for deterministic preset snapshots." },
  { id: "export-note-0215", note: "Export guidance 0215 for deterministic preset snapshots." },
  { id: "export-note-0216", note: "Export guidance 0216 for deterministic preset snapshots." },
  { id: "export-note-0217", note: "Export guidance 0217 for deterministic preset snapshots." },
  { id: "export-note-0218", note: "Export guidance 0218 for deterministic preset snapshots." },
  { id: "export-note-0219", note: "Export guidance 0219 for deterministic preset snapshots." },
  { id: "export-note-0220", note: "Export guidance 0220 for deterministic preset snapshots." },
  { id: "export-note-0221", note: "Export guidance 0221 for deterministic preset snapshots." },
  { id: "export-note-0222", note: "Export guidance 0222 for deterministic preset snapshots." },
  { id: "export-note-0223", note: "Export guidance 0223 for deterministic preset snapshots." },
  { id: "export-note-0224", note: "Export guidance 0224 for deterministic preset snapshots." },
  { id: "export-note-0225", note: "Export guidance 0225 for deterministic preset snapshots." },
  { id: "export-note-0226", note: "Export guidance 0226 for deterministic preset snapshots." },
  { id: "export-note-0227", note: "Export guidance 0227 for deterministic preset snapshots." },
  { id: "export-note-0228", note: "Export guidance 0228 for deterministic preset snapshots." },
  { id: "export-note-0229", note: "Export guidance 0229 for deterministic preset snapshots." },
  { id: "export-note-0230", note: "Export guidance 0230 for deterministic preset snapshots." },
  { id: "export-note-0231", note: "Export guidance 0231 for deterministic preset snapshots." },
  { id: "export-note-0232", note: "Export guidance 0232 for deterministic preset snapshots." },
  { id: "export-note-0233", note: "Export guidance 0233 for deterministic preset snapshots." },
  { id: "export-note-0234", note: "Export guidance 0234 for deterministic preset snapshots." },
  { id: "export-note-0235", note: "Export guidance 0235 for deterministic preset snapshots." },
  { id: "export-note-0236", note: "Export guidance 0236 for deterministic preset snapshots." },
  { id: "export-note-0237", note: "Export guidance 0237 for deterministic preset snapshots." },
  { id: "export-note-0238", note: "Export guidance 0238 for deterministic preset snapshots." },
  { id: "export-note-0239", note: "Export guidance 0239 for deterministic preset snapshots." },
  { id: "export-note-0240", note: "Export guidance 0240 for deterministic preset snapshots." },
  { id: "export-note-0241", note: "Export guidance 0241 for deterministic preset snapshots." },
  { id: "export-note-0242", note: "Export guidance 0242 for deterministic preset snapshots." },
  { id: "export-note-0243", note: "Export guidance 0243 for deterministic preset snapshots." },
  { id: "export-note-0244", note: "Export guidance 0244 for deterministic preset snapshots." },
  { id: "export-note-0245", note: "Export guidance 0245 for deterministic preset snapshots." },
  { id: "export-note-0246", note: "Export guidance 0246 for deterministic preset snapshots." },
  { id: "export-note-0247", note: "Export guidance 0247 for deterministic preset snapshots." },
  { id: "export-note-0248", note: "Export guidance 0248 for deterministic preset snapshots." },
  { id: "export-note-0249", note: "Export guidance 0249 for deterministic preset snapshots." },
  { id: "export-note-0250", note: "Export guidance 0250 for deterministic preset snapshots." },
  { id: "export-note-0251", note: "Export guidance 0251 for deterministic preset snapshots." },
  { id: "export-note-0252", note: "Export guidance 0252 for deterministic preset snapshots." },
  { id: "export-note-0253", note: "Export guidance 0253 for deterministic preset snapshots." },
  { id: "export-note-0254", note: "Export guidance 0254 for deterministic preset snapshots." },
  { id: "export-note-0255", note: "Export guidance 0255 for deterministic preset snapshots." },
  { id: "export-note-0256", note: "Export guidance 0256 for deterministic preset snapshots." },
  { id: "export-note-0257", note: "Export guidance 0257 for deterministic preset snapshots." },
  { id: "export-note-0258", note: "Export guidance 0258 for deterministic preset snapshots." },
  { id: "export-note-0259", note: "Export guidance 0259 for deterministic preset snapshots." },
  { id: "export-note-0260", note: "Export guidance 0260 for deterministic preset snapshots." },
] as const;

export function listExportNotebook(limit = 20): readonly string[] {
  return EXPORT_NOTEBOOK.slice(0, limit).map((entry) => entry.note);
}

