"use client";

import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import { buildGovernanceReport } from "../_luxury/governance";
import {
  LUXURY_SURFACES,
  VISUAL_BOUNDS,
  clampKnobsByProfile,
  createDefaultPreset,
  listPresetGalleryByStyle,
  listSurfaceRecipesForStyle,
  listLuxuryMaterials,
  listLuxuryStyles,
  repairPreset,
  resolveLuxuryMaterial,
  resolveLuxuryStyle
} from "../_luxury/registry/luxuryRegistry";
import type { LuxuryPreset, MotionLevel, PerfProfile, SurfaceId, VisualKnobId } from "../_luxury/types";
import { copyTextToClipboard } from "../_luxury/tools/clipboard";
import {
  buildPresetCssVarMap,
  cssVarMapToText,
  downloadTextFile,
  serializePresetJson
} from "../_luxury/tools/presetExport";
import { parsePresetText } from "../_luxury/tools/presetImport";

const MOTION_OPTIONS: readonly MotionLevel[] = ["micro", "standard", "hero", "off"];
const PERF_OPTIONS: readonly PerfProfile[] = ["default", "perf"];

function isPresetEqual(left: LuxuryPreset, right: LuxuryPreset): boolean {
  return (
    left.version === right.version &&
    left.styleId === right.styleId &&
    left.surfaceId === right.surfaceId &&
    left.materialId === right.materialId &&
    left.perfProfile === right.perfProfile &&
    left.motionLevel === right.motionLevel &&
    left.knobs.blurStrengthPx === right.knobs.blurStrengthPx &&
    left.knobs.grainOpacity === right.knobs.grainOpacity &&
    left.knobs.gridOpacity === right.knobs.gridOpacity &&
    left.knobs.specularIntensity === right.knobs.specularIntensity
  );
}

function describePerfCost(materialId: string): string {
  if (materialId.includes("quantum") || materialId.includes("auric") || materialId.includes("fractal")) {
    return "high";
  }
  if (materialId.includes("deep") || materialId.includes("ember") || materialId.includes("slate")) {
    return "medium";
  }
  return "low";
}

function renderSurface(surfaceId: SurfaceId) {
  switch (surfaceId) {
    case "tableDense":
      return (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left", padding: "6px 8px" }}>Owner</th>
              <th style={{ textAlign: "right", padding: "6px 8px" }}>SLA</th>
              <th style={{ textAlign: "right", padding: "6px 8px" }}>Risk</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: "6px 8px" }}>B_tooling</td>
              <td style={{ textAlign: "right", padding: "6px 8px" }}>2h</td>
              <td style={{ textAlign: "right", padding: "6px 8px" }}>1</td>
            </tr>
            <tr>
              <td style={{ padding: "6px 8px" }}>D_validation</td>
              <td style={{ textAlign: "right", padding: "6px 8px" }}>45m</td>
              <td style={{ textAlign: "right", padding: "6px 8px" }}>2</td>
            </tr>
          </tbody>
        </table>
      );
    case "drawer":
      return (
        <div style={{ display: "grid", gap: 8 }}>
          <button type="button" className="styleLabPreviewButton">
            Approve Preset
          </button>
          <button type="button" className="styleLabPreviewButton">
            Export Snapshot
          </button>
          <button type="button" className="styleLabPreviewButton">
            Open KPI Supermarket
          </button>
        </div>
      );
    case "rail":
      return (
        <div style={{ display: "grid", gap: 8 }}>
          <div className="styleLabChip">Motion</div>
          <div className="styleLabChip">Glow</div>
          <div className="styleLabChip">Gold</div>
        </div>
      );
    case "popover":
      return (
        <div style={{ maxWidth: 260 }}>
          <p style={{ margin: 0, fontWeight: 600 }}>Popover Surface</p>
          <p style={{ margin: "6px 0 0", fontSize: 12 }}>
            This branch previews bounded visual values before applying to production surfaces.
          </p>
        </div>
      );
    case "controlRoomHud":
      return (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 8 }}>
          <div className="styleLabMetric">
            <span>QPS</span>
            <strong>148</strong>
          </div>
          <div className="styleLabMetric">
            <span>Latency</span>
            <strong>214ms</strong>
          </div>
          <div className="styleLabMetric">
            <span>Drift</span>
            <strong>1.4%</strong>
          </div>
        </div>
      );
    case "kpiWidget":
      return (
        <div style={{ display: "grid", gap: 6 }}>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.8 }}>KPI Widget</p>
          <p style={{ margin: 0, fontSize: 30, fontWeight: 700, lineHeight: 1 }}>92.4%</p>
          <p style={{ margin: 0, fontSize: 11, opacity: 0.75 }}>Outcome confidence ↑ 2.1%</p>
        </div>
      );
    case "pitchPanel":
      return (
        <div style={{ display: "grid", gap: 8 }}>
          <h3 style={{ margin: 0, fontSize: 16 }}>Pitch Panel</h3>
          <p style={{ margin: 0, fontSize: 13 }}>
            Executive-grade storytelling surface tuned for readability and deterministic render.
          </p>
        </div>
      );
    case "pitchCard":
    default:
      return (
        <div style={{ display: "grid", gap: 6 }}>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.8 }}>Pitch Card</p>
          <p style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>Luxury Style Lab</p>
          <p style={{ margin: 0, fontSize: 12 }}>Preset preview bound to this subtree only.</p>
        </div>
      );
  }
}

export function StyleLabClient() {
  const [allowAlienTech, setAllowAlienTech] = useState(false);
  const [reducedMotionPreview, setReducedMotionPreview] = useState(false);
  const [preset, setPreset] = useState<LuxuryPreset>(() => createDefaultPreset("LIQUID_GLASS"));
  const [importText, setImportText] = useState("");
  const [importErrors, setImportErrors] = useState<string[]>([]);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    setPreset((previous) => {
      const repaired = repairPreset(previous, { includeAlienTech: allowAlienTech });
      return isPresetEqual(previous, repaired) ? previous : repaired;
    });
  }, [allowAlienTech]);

  useEffect(() => {
    if (!notice) {
      return;
    }
    const timer = window.setTimeout(() => setNotice(null), 2400);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const styleOptions = useMemo(() => listLuxuryStyles(), []);
  const materialOptions = useMemo(
    () => listLuxuryMaterials(preset.styleId, { includeAlienTech: allowAlienTech }),
    [allowAlienTech, preset.styleId]
  );
  const galleryPresets = useMemo(
    () => listPresetGalleryByStyle(preset.styleId, 24),
    [preset.styleId]
  );
  const surfaceRecipes = useMemo(
    () => listSurfaceRecipesForStyle(preset.styleId, preset.surfaceId, 10),
    [preset.styleId, preset.surfaceId]
  );

  const styleDef = useMemo(() => resolveLuxuryStyle(preset.styleId), [preset.styleId]);
  const materialDef = useMemo(
    () =>
      resolveLuxuryMaterial(preset.styleId, preset.materialId, {
        includeAlienTech: allowAlienTech
      }),
    [allowAlienTech, preset.materialId, preset.styleId]
  );

  const governance = useMemo(
    () =>
      buildGovernanceReport({
        preset,
        style: styleDef,
        material: materialDef
      }),
    [materialDef, preset, styleDef]
  );

  const cssVars = useMemo(
    () =>
      buildPresetCssVarMap(preset, {
        includeAlienTech: allowAlienTech,
        reducedMotionPreview
      }),
    [allowAlienTech, preset, reducedMotionPreview]
  );

  const cssText = useMemo(() => cssVarMapToText(cssVars), [cssVars]);
  const presetJson = useMemo(() => serializePresetJson(preset), [preset]);
  const styleVars = useMemo(() => cssVars as CSSProperties, [cssVars]);

  const knobMax = useMemo(
    () => ({
      blurStrengthPx:
        preset.perfProfile === "perf"
          ? VISUAL_BOUNDS.blurStrengthPx.perfMax
          : VISUAL_BOUNDS.blurStrengthPx.max,
      grainOpacity:
        preset.perfProfile === "perf"
          ? VISUAL_BOUNDS.grainOpacity.perfMax
          : VISUAL_BOUNDS.grainOpacity.max,
      gridOpacity:
        preset.perfProfile === "perf"
          ? VISUAL_BOUNDS.gridOpacity.perfMax
          : VISUAL_BOUNDS.gridOpacity.max,
      specularIntensity:
        preset.perfProfile === "perf"
          ? VISUAL_BOUNDS.specularIntensity.perfMax
          : VISUAL_BOUNDS.specularIntensity.max
    }),
    [preset.perfProfile]
  );

  const setKnob = useCallback((id: VisualKnobId, value: number) => {
    setPreset((previous) => ({
      ...previous,
      knobs: clampKnobsByProfile(
        {
          ...previous.knobs,
          [id]: value
        },
        previous.perfProfile
      )
    }));
  }, []);

  const setPerfProfile = useCallback((next: PerfProfile) => {
    setPreset((previous) => ({
      ...previous,
      perfProfile: next,
      knobs: clampKnobsByProfile(previous.knobs, next)
    }));
  }, []);

  const setMotionLevel = useCallback((next: MotionLevel) => {
    setPreset((previous) => ({ ...previous, motionLevel: next }));
  }, []);

  const setStyle = useCallback(
    (nextStyleId: LuxuryPreset["styleId"]) => {
      setPreset((previous) => {
        const defaults = createDefaultPreset(nextStyleId);
        const allowed = listLuxuryMaterials(nextStyleId, {
          includeAlienTech: allowAlienTech
        }).map((entry) => entry.id);
        const nextMaterialId = allowed.includes(previous.materialId)
          ? previous.materialId
          : defaults.materialId;

        return repairPreset(
          {
            ...previous,
            styleId: nextStyleId,
            materialId: nextMaterialId
          },
          { includeAlienTech: allowAlienTech }
        );
      });
    },
    [allowAlienTech]
  );

  const onCopyCss = useCallback(async () => {
    const result = await copyTextToClipboard(cssText, "CSS vars");
    setNotice(result.message);
  }, [cssText]);

  const onExportJson = useCallback(() => {
    const filename = `style-lab-preset.${preset.styleId.toLowerCase()}.json`;
    downloadTextFile(filename, presetJson);
    setNotice(`Preset exported as ${filename}.`);
  }, [preset.styleId, presetJson]);

  const onImportPreset = useCallback(() => {
    const result = parsePresetText(importText, { includeAlienTech: allowAlienTech });
    if (!result.ok) {
      setImportErrors(result.issues.map((entry) => `${entry.path}: ${entry.message}`));
      setNotice("Preset import failed. Review validation errors.");
      return;
    }

    setImportErrors([]);
    setPreset(result.preset);
    setNotice("Preset imported and applied to preview subtree.");
  }, [allowAlienTech, importText]);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "1.5rem 1.2rem 2rem",
        background:
          "radial-gradient(1200px 650px at -10% -10%, hsl(var(--ui-accent) / 0.11), transparent 55%), hsl(var(--ui-bg))"
      }}
    >
      <section
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          display: "grid",
          gap: 14
        }}
      >
        <header
          style={{
            border: "1px solid hsl(var(--ui-border-1))",
            borderRadius: 16,
            padding: "1rem",
            background: "hsl(var(--ui-surface-1) / 0.88)"
          }}
        >
          <p className="keystone-kicker">Dev · Luxury Workbench</p>
          <h1 style={{ margin: "0.25rem 0 0", fontSize: "clamp(1.3rem, 2.8vw, 1.9rem)" }}>
            Style Lab
          </h1>
          <p style={{ margin: "0.6rem 0 0", color: "hsl(var(--ui-text-2))" }}>
            Switch styles, surfaces, materials, and bounded visual knobs. Export/import presets and
            watch governance budgets in real time.
          </p>
        </header>

        <section
          style={{
            display: "grid",
            gap: 14,
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))"
          }}
        >
          <aside
            style={{
              border: "1px solid hsl(var(--ui-border-1))",
              borderRadius: 16,
              padding: "0.95rem",
              background: "hsl(var(--ui-surface-1) / 0.9)",
              display: "grid",
              gap: 12
            }}
          >
            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>Style</span>
              <select
                value={preset.styleId}
                onChange={(event) => setStyle(event.currentTarget.value as LuxuryPreset["styleId"])}
                className="rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] px-2 py-2 text-sm"
              >
                {styleOptions.map((style) => (
                  <option key={style.id} value={style.id}>
                    {style.id} · {style.label}
                  </option>
                ))}
              </select>
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>Surface</span>
              <select
                value={preset.surfaceId}
                onChange={(event) =>
                  setPreset((previous) => ({
                    ...previous,
                    surfaceId: event.currentTarget.value as SurfaceId
                  }))
                }
                className="rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] px-2 py-2 text-sm"
              >
                {LUXURY_SURFACES.map((surface) => (
                  <option key={surface.id} value={surface.id}>
                    {surface.id}
                  </option>
                ))}
              </select>
            </label>

            <label style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>Material</span>
              <select
                value={preset.materialId}
                onChange={(event) =>
                  setPreset((previous) =>
                    repairPreset(
                      {
                        ...previous,
                        materialId: event.currentTarget.value
                      },
                      { includeAlienTech: allowAlienTech }
                    )
                  )
                }
                className="rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] px-2 py-2 text-sm"
              >
                {materialOptions.map((material) => (
                  <option key={material.id} value={material.id}>
                    {material.label} · {material.maturity} · {material.perfCost}
                  </option>
                ))}
              </select>
            </label>

            <div style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>PerfProfile</span>
              <div style={{ display: "flex", gap: 6 }}>
                {PERF_OPTIONS.map((profile) => (
                  <button
                    key={profile}
                    type="button"
                    onClick={() => setPerfProfile(profile)}
                    className={`rounded-full border px-3 py-1 text-xs ${
                      preset.perfProfile === profile
                        ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent)/0.2)]"
                        : "border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))]"
                    }`}
                  >
                    {profile}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gap: 6 }}>
              <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>MotionLevel</span>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {MOTION_OPTIONS.map((motion) => (
                  <button
                    key={motion}
                    type="button"
                    onClick={() => setMotionLevel(motion)}
                    className={`rounded-full border px-3 py-1 text-xs ${
                      preset.motionLevel === motion
                        ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent)/0.2)]"
                        : "border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))]"
                    }`}
                  >
                    {motion}
                  </button>
                ))}
              </div>
            </div>

            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <input
                type="checkbox"
                checked={reducedMotionPreview}
                onChange={(event) => setReducedMotionPreview(event.currentTarget.checked)}
              />
              Reduced-motion preview
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <input
                type="checkbox"
                checked={allowAlienTech}
                onChange={(event) => setAllowAlienTech(event.currentTarget.checked)}
              />
              Enable Alien Tech materials (OFF by default)
            </label>

            <div style={{ display: "grid", gap: 8 }}>
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Visual knobs (bounded + perf-gated)
              </p>

              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 11 }}>Blur strength ({preset.knobs.blurStrengthPx.toFixed(1)}px)</span>
                <input
                  type="range"
                  min={VISUAL_BOUNDS.blurStrengthPx.min}
                  max={knobMax.blurStrengthPx}
                  step={0.1}
                  value={preset.knobs.blurStrengthPx}
                  onChange={(event) => setKnob("blurStrengthPx", Number(event.currentTarget.value))}
                />
              </label>

              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 11 }}>Grain opacity ({preset.knobs.grainOpacity.toFixed(3)})</span>
                <input
                  type="range"
                  min={VISUAL_BOUNDS.grainOpacity.min}
                  max={knobMax.grainOpacity}
                  step={0.005}
                  value={preset.knobs.grainOpacity}
                  onChange={(event) => setKnob("grainOpacity", Number(event.currentTarget.value))}
                />
              </label>

              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 11 }}>Grid opacity ({preset.knobs.gridOpacity.toFixed(3)})</span>
                <input
                  type="range"
                  min={VISUAL_BOUNDS.gridOpacity.min}
                  max={knobMax.gridOpacity}
                  step={0.005}
                  value={preset.knobs.gridOpacity}
                  onChange={(event) => setKnob("gridOpacity", Number(event.currentTarget.value))}
                />
              </label>

              <label style={{ display: "grid", gap: 4 }}>
                <span style={{ fontSize: 11 }}>
                  Specular intensity ({preset.knobs.specularIntensity.toFixed(3)})
                </span>
                <input
                  type="range"
                  min={VISUAL_BOUNDS.specularIntensity.min}
                  max={knobMax.specularIntensity}
                  step={0.01}
                  value={preset.knobs.specularIntensity}
                  onChange={(event) => setKnob("specularIntensity", Number(event.currentTarget.value))}
                />
              </label>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button type="button" className="styleLabActionButton" onClick={onCopyCss}>
                Copy CSS vars
              </button>
              <button type="button" className="styleLabActionButton" onClick={onExportJson}>
                Export preset JSON
              </button>
            </div>

            <div style={{ display: "grid", gap: 6 }}>
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Preset gallery quick picks ({galleryPresets.length})
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 6 }}>
                {galleryPresets.map((entry, index) => (
                  <button
                    key={`${entry.materialId}-${index}`}
                    type="button"
                    className="styleLabActionButton"
                    onClick={() =>
                      setPreset(
                        repairPreset(
                          {
                            ...entry,
                            surfaceId: preset.surfaceId
                          },
                          { includeAlienTech: allowAlienTech }
                        )
                      )
                    }
                  >
                    {entry.materialId}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gap: 6 }}>
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Surface recipes for {preset.surfaceId}
              </p>
              <ul style={{ margin: 0, paddingLeft: "1rem", display: "grid", gap: 3 }}>
                {surfaceRecipes.map((recipe) => (
                  <li key={recipe.id} style={{ fontSize: 11 }}>
                    {recipe.materialId} · blur {recipe.blurStrengthPx.toFixed(1)} · spec {recipe.specularIntensity.toFixed(2)}
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ display: "grid", gap: 6 }}>
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Import preset JSON
              </p>
              <textarea
                value={importText}
                onChange={(event) => setImportText(event.currentTarget.value)}
                rows={5}
                placeholder='{"version":1,"styleId":"LIQUID_GLASS",...}'
                className="rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2))] p-2 text-xs"
              />
              <button type="button" className="styleLabActionButton" onClick={onImportPreset}>
                Apply imported preset
              </button>
              {importErrors.length > 0 ? (
                <div
                  style={{
                    border: "1px solid hsl(var(--ui-border-1))",
                    borderRadius: 10,
                    padding: "0.5rem",
                    background: "hsl(var(--ui-surface-2))"
                  }}
                >
                  {importErrors.map((entry) => (
                    <p key={entry} style={{ margin: "0 0 4px", fontSize: 11, color: "#d66262" }}>
                      {entry}
                    </p>
                  ))}
                </div>
              ) : null}
            </div>
          </aside>

          <section
            style={{
              border: "1px solid hsl(var(--ui-border-1))",
              borderRadius: 16,
              padding: "1rem",
              background: "hsl(var(--ui-surface-1) / 0.92)",
              display: "grid",
              gap: 12
            }}
          >
            <div style={{ display: "grid", gap: 8 }}>
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Governance (display-only)
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 8 }}>
                <div className="styleLabBudgetCard">
                  <p>GlowBudget</p>
                  <meter max={governance.glow.max} value={governance.glow.value} />
                  <span>
                    {governance.glow.value}/{governance.glow.max} · {governance.glow.hint}
                  </span>
                </div>
                <div className="styleLabBudgetCard">
                  <p>MotionBudget</p>
                  <meter max={governance.motion.max} value={governance.motion.value} />
                  <span>{governance.motion.hint}</span>
                </div>
                <div className="styleLabBudgetCard">
                  <p>Gold usage</p>
                  <meter max={governance.goldUsage.max} value={governance.goldUsage.value} />
                  <span>{governance.goldUsage.hint}</span>
                </div>
              </div>
              {governance.warnings.length > 0 ? (
                <div className="styleLabWarning">
                  {governance.warnings.map((warning) => (
                    <p key={warning}>{warning}</p>
                  ))}
                </div>
              ) : null}
            </div>

            <section style={styleVars}>
              <div className={`styleLabPreview ${reducedMotionPreview ? "reduced" : ""}`}>
                <div className="styleLabPreviewGrid" />
                <div className="styleLabPreviewGrain" />
                <div className="styleLabPreviewSpecular" />
                <div className="styleLabPreviewBody">{renderSurface(preset.surfaceId)}</div>
              </div>
            </section>

            <section
              style={{
                border: "1px solid hsl(var(--ui-border-1))",
                borderRadius: 12,
                padding: "0.7rem",
                background: "hsl(var(--ui-surface-2))",
                display: "grid",
                gap: 6
              }}
            >
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Active preset summary
              </p>
              <p style={{ margin: 0, fontSize: 12 }}>
                {styleDef.label} · {materialDef.label} · perf={preset.perfProfile} · motion=
                {preset.motionLevel} · materialCost={describePerfCost(materialDef.id)}
              </p>
              <pre
                style={{
                  margin: 0,
                  maxHeight: 180,
                  overflow: "auto",
                  fontSize: 11,
                  padding: "0.6rem",
                  borderRadius: 8,
                  background: "hsl(var(--ui-surface-1))"
                }}
              >
                {presetJson}
              </pre>
              <pre
                style={{
                  margin: 0,
                  maxHeight: 200,
                  overflow: "auto",
                  fontSize: 11,
                  padding: "0.6rem",
                  borderRadius: 8,
                  background: "hsl(var(--ui-surface-1))"
                }}
              >
                {cssText}
              </pre>
            </section>
          </section>
        </section>
      </section>

      {notice ? (
        <div className="styleLabToast" role="status">
          {notice}
        </div>
      ) : null}

      <style jsx>{`
        .styleLabPreview {
          position: relative;
          overflow: hidden;
          border-radius: var(--luxury-radius);
          border: 1px solid var(--luxury-border);
          color: var(--luxury-text);
          background: var(--luxury-bg);
          min-height: 320px;
          box-shadow: var(--luxury-shadow);
          padding: 1rem;
          transition:
            transform var(--luxury-motion-duration) var(--luxury-motion-easing),
            box-shadow var(--luxury-motion-duration) var(--luxury-motion-easing);
          transform: translateY(0);
        }
        .styleLabPreview:hover {
          transform: translateY(-2px);
        }
        .styleLabPreview.reduced {
          transition: none;
        }
        .styleLabPreviewBody {
          position: relative;
          z-index: 4;
          border-radius: calc(var(--luxury-radius) - 4px);
          border: 1px solid var(--luxury-border);
          background: var(--luxury-surface);
          backdrop-filter: blur(var(--luxury-blur-px));
          -webkit-backdrop-filter: blur(var(--luxury-blur-px));
          padding: 1rem;
          min-height: 250px;
        }
        .styleLabPreviewGrid {
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(
              to right,
              color-mix(in srgb, var(--luxury-grid-color) 65%, transparent) 1px,
              transparent 1px
            ),
            linear-gradient(
              to bottom,
              color-mix(in srgb, var(--luxury-grid-color) 65%, transparent) 1px,
              transparent 1px
            );
          background-size: 20px 20px;
          opacity: var(--luxury-grid-opacity);
          z-index: 1;
          pointer-events: none;
        }
        .styleLabPreviewGrain {
          position: absolute;
          inset: 0;
          background-image: radial-gradient(var(--luxury-grain-color) 0.8px, transparent 0.8px);
          background-size: 3px 3px;
          opacity: var(--luxury-grain-opacity);
          z-index: 2;
          pointer-events: none;
        }
        .styleLabPreviewSpecular {
          position: absolute;
          inset: -30% -10% auto -10%;
          height: 160px;
          z-index: 3;
          pointer-events: none;
          background: var(--luxury-highlight);
          opacity: var(--luxury-specular-opacity);
          transform: rotate(6deg);
          animation: styleLabSpecularDrift var(--luxury-motion-duration) var(--luxury-motion-easing) infinite;
        }
        .styleLabPreview.reduced .styleLabPreviewSpecular {
          animation: none;
        }
        .styleLabMetric {
          border: 1px solid var(--luxury-border);
          border-radius: 12px;
          padding: 10px;
          display: grid;
          gap: 4px;
          background: color-mix(in srgb, var(--luxury-surface) 80%, transparent);
        }
        .styleLabMetric span {
          font-size: 11px;
          color: var(--luxury-muted);
        }
        .styleLabMetric strong {
          font-size: 18px;
          line-height: 1;
        }
        .styleLabChip {
          border: 1px solid var(--luxury-border);
          border-radius: 999px;
          padding: 6px 10px;
          font-size: 11px;
          display: inline-flex;
          width: fit-content;
          background: color-mix(in srgb, var(--luxury-surface) 75%, transparent);
        }
        .styleLabPreviewButton {
          border: 1px solid var(--luxury-border);
          border-radius: 10px;
          background: var(--luxury-surface);
          color: var(--luxury-text);
          padding: 0.55rem 0.75rem;
          text-align: left;
          font-size: 12px;
          cursor: pointer;
        }
        .styleLabBudgetCard {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 10px;
          padding: 8px;
          display: grid;
          gap: 6px;
          background: hsl(var(--ui-surface-2));
        }
        .styleLabBudgetCard p {
          margin: 0;
          font-size: 11px;
          color: hsl(var(--ui-text-2));
        }
        .styleLabBudgetCard meter {
          width: 100%;
        }
        .styleLabBudgetCard span {
          font-size: 11px;
          color: hsl(var(--ui-text-2));
        }
        .styleLabWarning {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 10px;
          padding: 8px;
          background: color-mix(in srgb, hsl(var(--ui-surface-2)) 80%, #f8d4af 20%);
          display: grid;
          gap: 4px;
        }
        .styleLabWarning p {
          margin: 0;
          font-size: 11px;
          color: #8d4b0f;
        }
        .styleLabActionButton {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 999px;
          background: hsl(var(--ui-surface-2));
          color: hsl(var(--ui-text-1));
          font-size: 12px;
          padding: 6px 12px;
          cursor: pointer;
        }
        .styleLabToast {
          position: fixed;
          right: 12px;
          bottom: 12px;
          z-index: 70;
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 10px;
          background: hsl(var(--ui-surface-1));
          padding: 8px 12px;
          font-size: 12px;
          box-shadow: var(--ui-shadow-2);
        }
        @keyframes styleLabSpecularDrift {
          0% {
            transform: translateX(-14%) rotate(6deg);
          }
          50% {
            transform: translateX(12%) rotate(6deg);
          }
          100% {
            transform: translateX(-14%) rotate(6deg);
          }
        }
      `}</style>
    </main>
  );
}
