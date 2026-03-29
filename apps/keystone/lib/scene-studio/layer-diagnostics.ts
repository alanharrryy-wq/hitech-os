import { LAYER_DATA_ATTRIBUTES, type LayerId } from "@hitech/ui-kit";
import { buildLayerDomResolution } from "../pitch/layer-resolution";
import type { SceneDiagnosticsPayload } from "./scene-bridge";

export interface LayerDiagnosticsRow {
  readonly layerId: LayerId;
  readonly attribute: string;
  readonly requested: boolean;
  readonly domApplied: boolean;
  readonly missing: boolean;
}

export interface LayerDiagnosticsSummary {
  readonly enabledCount: number;
  readonly domAppliedCount: number;
  readonly missingCount: number;
  readonly rows: readonly LayerDiagnosticsRow[];
}

export function buildLayerDiagnosticsSummary(
  diagnostics: SceneDiagnosticsPayload | null | undefined
): LayerDiagnosticsSummary {
  if (!diagnostics) {
    return {
      enabledCount: 0,
      domAppliedCount: 0,
      missingCount: 0,
      rows: []
    };
  }

  const domResolution = buildLayerDomResolution(diagnostics.resolved, diagnostics.domDataAttributes);
  const missing = new Set(diagnostics.missingDataAttributes);

  const rows = domResolution
    .filter((entry) => diagnostics.enabledLayerIds.includes(entry.layerId))
    .map((entry) => ({
      layerId: entry.layerId,
      attribute: entry.attribute,
      requested: Boolean(diagnostics.resolved.flags[entry.layerId]),
      domApplied: entry.enabled,
      missing: missing.has(entry.attribute) || diagnostics.domDataAttributes[LAYER_DATA_ATTRIBUTES[entry.layerId]] !== "1"
    }));

  return {
    enabledCount: diagnostics.enabledLayerIds.length,
    domAppliedCount: rows.filter((row) => row.domApplied).length,
    missingCount: rows.filter((row) => row.missing).length,
    rows
  };
}
