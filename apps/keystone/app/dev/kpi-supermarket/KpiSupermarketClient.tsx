"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type CSSProperties
} from "react";
import { buildGovernanceReport } from "../_luxury/governance";
import { listDiagnosticHints, useKpiDataSpine } from "../_luxury/dataSpine";
import {
  KPI_CATALOG,
  listIntentOptions,
  listMaturityOptions,
  listPerfCostOptions,
  listShapeOptions
} from "../_luxury/registry/kpiRegistry";
import {
  LUXURY_SURFACES,
  createDefaultPreset,
  listLuxuryMaterials,
  listLuxuryStyles,
  repairPreset,
  resolveLuxuryMaterial,
  resolveLuxuryStyle
} from "../_luxury/registry/luxuryRegistry";
import type {
  DataProviderId,
  KpiDataShape,
  KpiIntent,
  KpiPreviewPayload,
  LuxuryPreset,
  Maturity,
  MotionLevel,
  PerfCost
} from "../_luxury/types";
import { copyTextToClipboard } from "../_luxury/tools/clipboard";
import { downloadCatalogSnapshot } from "../_luxury/tools/catalogSnapshot";
import {
  buildPresetCssVarMap,
  cssVarMapToText
} from "../_luxury/tools/presetExport";
import {
  readLocalStorageJson,
  writeLocalStorageJson
} from "../_luxury/tools/localStorageSafe";

const SHORTLIST_KEY = "keystone.dev.kpi-supermarket.shortlist.v1";
const MAX_TILE_RESULTS = 72;
const PERF_OPTIONS: readonly LuxuryPreset["perfProfile"][] = ["default", "perf"];
const MOTION_OPTIONS: readonly MotionLevel[] = ["micro", "standard", "hero", "off"];
const PROVIDER_OPTIONS: readonly DataProviderId[] = ["mock", "json", "http"];

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === "string");
}

function renderPreviewPayload(payload: KpiPreviewPayload) {
  switch (payload.shape) {
    case "table":
      return (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr>
              {(payload.columns ?? []).map((column) => (
                <th key={column} style={{ textAlign: "left", padding: "6px 8px" }}>
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(payload.rows ?? []).map((row, index) => (
              <tr key={`${index}`}>
                {(payload.columns ?? []).map((column) => (
                  <td key={`${index}-${column}`} style={{ padding: "6px 8px" }}>
                    {String(row[column] ?? "-")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    case "events":
      return (
        <div style={{ display: "grid", gap: 6 }}>
          {(payload.events ?? []).map((event) => (
            <div key={`${event.at}-${event.text}`} className="kpiEventRow">
              <span>{event.at}</span>
              <span>{event.text}</span>
              <span>{event.severity}</span>
            </div>
          ))}
        </div>
      );
    case "ratio":
      return (
        <div style={{ display: "grid", gap: 8 }}>
          <p style={{ margin: 0, fontSize: 28, fontWeight: 700 }}>
            {payload.value ?? 0}
            {payload.unit ?? ""}
          </p>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.8 }}>
            {payload.numerator ?? 0} / {payload.denominator ?? 0}
          </p>
        </div>
      );
    case "timeseries":
      return (
        <div style={{ display: "grid", gap: 8 }}>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.85 }}>{payload.labels?.join(" · ")}</p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: `repeat(${payload.points?.length ?? 1}, minmax(0, 1fr))`,
              alignItems: "end",
              gap: 6,
              minHeight: 80
            }}
          >
            {(payload.points ?? []).map((point, index) => (
              <div
                key={`${index}`}
                style={{
                  borderRadius: 6,
                  background: "color-mix(in srgb, var(--luxury-accent) 70%, transparent)",
                  height: `${Math.max(8, Math.min(100, point))}%`
                }}
              />
            ))}
          </div>
        </div>
      );
    case "single-value":
    default:
      return (
        <div style={{ display: "grid", gap: 6 }}>
          <p style={{ margin: 0, fontSize: 30, fontWeight: 700, lineHeight: 1 }}>
            {payload.value ?? 0}
            {payload.unit ?? ""}
          </p>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.82 }}>
            delta {payload.delta !== undefined ? payload.delta.toFixed(1) : "0.0"}%
          </p>
          {(payload.points ?? []).length > 0 ? (
            <p style={{ margin: 0, fontSize: 11, opacity: 0.74 }}>
              trend: {(payload.points ?? []).join(" · ")}
            </p>
          ) : null}
        </div>
      );
  }
}

export function KpiSupermarketClient() {
  const [allowAlienTech, setAllowAlienTech] = useState(false);
  const [styleFilter, setStyleFilter] = useState<"all" | LuxuryPreset["styleId"]>("all");
  const [maturityFilter, setMaturityFilter] = useState<"all" | Maturity>("all");
  const [perfCostFilter, setPerfCostFilter] = useState<"all" | PerfCost>("all");
  const [intentFilter, setIntentFilter] = useState<"all" | KpiIntent>("all");
  const [shapeFilter, setShapeFilter] = useState<"all" | KpiDataShape>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [dataProvider, setDataProvider] = useState<DataProviderId>("mock");
  const [shortlist, setShortlist] = useState<string[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [previewPreset, setPreviewPreset] = useState<LuxuryPreset>(() =>
    createDefaultPreset("LIQUID_GLASS")
  );

  useEffect(() => {
    const saved = readLocalStorageJson<string[]>(SHORTLIST_KEY, [], isStringArray);
    setShortlist(saved);
  }, []);

  useEffect(() => {
    writeLocalStorageJson(SHORTLIST_KEY, shortlist);
  }, [shortlist]);

  useEffect(() => {
    if (!notice) {
      return;
    }
    const timer = window.setTimeout(() => setNotice(null), 2600);
    return () => window.clearTimeout(timer);
  }, [notice]);

  useEffect(() => {
    setPreviewPreset((previous) => {
      const repaired = repairPreset(previous, { includeAlienTech: allowAlienTech });
      return repaired;
    });
  }, [allowAlienTech]);

  const filteredCatalog = useMemo(() => {
    return KPI_CATALOG.filter((item) => {
      if (!allowAlienTech && item.maturity === "Alien Tech") {
        return false;
      }
      if (styleFilter !== "all" && !item.styles.includes(styleFilter)) {
        return false;
      }
      if (maturityFilter !== "all" && item.maturity !== maturityFilter) {
        return false;
      }
      if (perfCostFilter !== "all" && item.perfCost !== perfCostFilter) {
        return false;
      }
      if (intentFilter !== "all" && !item.intents.includes(intentFilter)) {
        return false;
      }
      if (shapeFilter !== "all" && !item.dataShapes.includes(shapeFilter)) {
        return false;
      }
      return true;
    });
  }, [allowAlienTech, intentFilter, maturityFilter, perfCostFilter, shapeFilter, styleFilter]);

  useEffect(() => {
    if (filteredCatalog.length === 0) {
      setSelectedId(null);
      return;
    }
    if (!selectedId || !filteredCatalog.some((item) => item.id === selectedId)) {
      const firstItem = filteredCatalog[0];
      if (firstItem) {
        setSelectedId(firstItem.id);
      }
    }
  }, [filteredCatalog, selectedId]);

  const selectedItem = useMemo(
    () => filteredCatalog.find((entry) => entry.id === selectedId) ?? null,
    [filteredCatalog, selectedId]
  );
  const visibleCatalog = useMemo(
    () => filteredCatalog.slice(0, MAX_TILE_RESULTS),
    [filteredCatalog]
  );

  useEffect(() => {
    if (!selectedItem) {
      return;
    }
    if (!selectedItem.styles.includes(previewPreset.styleId)) {
      setPreviewPreset(createDefaultPreset(selectedItem.styles[0] ?? "LIQUID_GLASS"));
    }
  }, [previewPreset.styleId, selectedItem]);

  const styleOptions = useMemo(() => listLuxuryStyles(), []);
  const materialOptions = useMemo(
    () =>
      listLuxuryMaterials(previewPreset.styleId, {
        includeAlienTech: allowAlienTech
      }),
    [allowAlienTech, previewPreset.styleId]
  );
  const styleDef = useMemo(() => resolveLuxuryStyle(previewPreset.styleId), [previewPreset.styleId]);
  const materialDef = useMemo(
    () =>
      resolveLuxuryMaterial(previewPreset.styleId, previewPreset.materialId, {
        includeAlienTech: allowAlienTech
      }),
    [allowAlienTech, previewPreset.materialId, previewPreset.styleId]
  );
  const governance = useMemo(
    () =>
      buildGovernanceReport({
        preset: previewPreset,
        style: styleDef,
        material: materialDef
      }),
    [materialDef, previewPreset, styleDef]
  );
  const previewVars = useMemo(
    () =>
      buildPresetCssVarMap(previewPreset, {
        includeAlienTech: allowAlienTech
      }),
    [allowAlienTech, previewPreset]
  );
  const previewStyle = useMemo(() => previewVars as CSSProperties, [previewVars]);
  const previewCssText = useMemo(() => cssVarMapToText(previewVars), [previewVars]);

  const dataSpine = useKpiDataSpine({ provider: dataProvider, item: selectedItem });
  const previewPayload = dataSpine.payload ?? selectedItem?.previewMock ?? null;
  const providerHints = useMemo(
    () =>
      listDiagnosticHints(dataProvider, undefined, 5).map(
        (hint) => `${hint.signal}: ${hint.recommendation}`
      ),
    [dataProvider]
  );

  const onCopySnippet = useCallback(async () => {
    if (!selectedItem) {
      return;
    }
    const result = await copyTextToClipboard(selectedItem.snippet, "Usage snippet");
    setNotice(result.message);
  }, [selectedItem]);

  const onAddToShortlist = useCallback(() => {
    if (!selectedItem) {
      return;
    }
    setShortlist((previous) => {
      if (previous.includes(selectedItem.id)) {
        return previous;
      }
      return [...previous, selectedItem.id];
    });
    setNotice(`${selectedItem.title} added to shortlist.`);
  }, [selectedItem]);

  const onExportCatalog = useCallback(() => {
    const success = downloadCatalogSnapshot(KPI_CATALOG);
    setNotice(success ? "Catalog snapshot exported." : "Catalog snapshot export failed.");
  }, []);

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "1.5rem 1.2rem 2rem",
        background:
          "radial-gradient(900px 560px at 100% -10%, hsl(var(--ui-accent) / 0.12), transparent 54%), hsl(var(--ui-bg))"
      }}
    >
      <section style={{ maxWidth: 1260, margin: "0 auto", display: "grid", gap: 14 }}>
        <header
          style={{
            border: "1px solid hsl(var(--ui-border-1))",
            borderRadius: 16,
            padding: "1rem",
            background: "hsl(var(--ui-surface-1) / 0.9)",
            display: "grid",
            gap: 8
          }}
        >
          <p className="keystone-kicker">Dev · Luxury Workbench</p>
          <h1 style={{ margin: "0.2rem 0 0", fontSize: "clamp(1.3rem, 2.8vw, 1.95rem)" }}>
            KPI Supermarket
          </h1>
          <p style={{ margin: 0, color: "hsl(var(--ui-text-2))" }}>
            Browse KPI widgets as a curated catalog with maturity/perf metadata, data-shape filters,
            and live Data Spine preview.
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" className="kpiActionBtn" onClick={onExportCatalog}>
              Export catalog snapshot
            </button>
            <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <input
                type="checkbox"
                checked={allowAlienTech}
                onChange={(event) => setAllowAlienTech(event.currentTarget.checked)}
              />
              Enable Alien Tech (OFF by default)
            </label>
            <span style={{ fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
              Shortlist: {shortlist.length}
            </span>
          </div>
        </header>

        <section
          style={{
            display: "grid",
            gap: 14,
            gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))"
          }}
        >
          <section
            style={{
              border: "1px solid hsl(var(--ui-border-1))",
              borderRadius: 16,
              padding: "0.9rem",
              background: "hsl(var(--ui-surface-1) / 0.9)",
              display: "grid",
              gap: 10
            }}
          >
            <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))" }}>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                Style
                <select
                  value={styleFilter}
                  onChange={(event) => setStyleFilter(event.currentTarget.value as "all" | LuxuryPreset["styleId"])}
                  className="kpiSelect"
                >
                  <option value="all">all</option>
                  {styleOptions.map((style) => (
                    <option key={style.id} value={style.id}>
                      {style.id}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                Maturity
                <select
                  value={maturityFilter}
                  onChange={(event) => setMaturityFilter(event.currentTarget.value as "all" | Maturity)}
                  className="kpiSelect"
                >
                  <option value="all">all</option>
                  {listMaturityOptions().map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                Perf Cost
                <select
                  value={perfCostFilter}
                  onChange={(event) => setPerfCostFilter(event.currentTarget.value as "all" | PerfCost)}
                  className="kpiSelect"
                >
                  <option value="all">all</option>
                  {listPerfCostOptions().map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                Intent
                <select
                  value={intentFilter}
                  onChange={(event) => setIntentFilter(event.currentTarget.value as "all" | KpiIntent)}
                  className="kpiSelect"
                >
                  <option value="all">all</option>
                  {listIntentOptions().map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                Data shape
                <select
                  value={shapeFilter}
                  onChange={(event) => setShapeFilter(event.currentTarget.value as "all" | KpiDataShape)}
                  className="kpiSelect"
                >
                  <option value="all">all</option>
                  {listShapeOptions().map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))" }}>
              {visibleCatalog.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  className={`kpiTile ${selectedId === item.id ? "selected" : ""}`}
                >
                  <div className="kpiThumb">{item.thumbnail}</div>
                  <div style={{ display: "grid", gap: 4 }}>
                    <strong style={{ fontSize: 14, textAlign: "left" }}>{item.title}</strong>
                    <span style={{ fontSize: 11, textAlign: "left", opacity: 0.84 }}>{item.summary}</span>
                  </div>
                  <p style={{ margin: 0, fontSize: 11, textAlign: "left" }}>maturity: {item.maturity}</p>
                  <p style={{ margin: 0, fontSize: 11, textAlign: "left" }}>perfCost: {item.perfCost}</p>
                  <p style={{ margin: 0, fontSize: 11, textAlign: "left" }}>
                    shapes: {item.dataShapes.join(", ")}
                  </p>
                  <p style={{ margin: 0, fontSize: 11, textAlign: "left" }}>
                    surfaces: {item.surfaces.join(", ")}
                  </p>
                  <p style={{ margin: 0, fontSize: 11, textAlign: "left" }}>
                    tags: {item.tags.join(", ")}
                  </p>
                </button>
              ))}
              {filteredCatalog.length === 0 ? (
                <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                  No KPI entries match current filters.
                </p>
              ) : null}
              {filteredCatalog.length > visibleCatalog.length ? (
                <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                  Showing first {visibleCatalog.length} of {filteredCatalog.length} entries. Refine filters to narrow results.
                </p>
              ) : null}
            </div>
          </section>

          <aside
            style={{
              border: "1px solid hsl(var(--ui-border-1))",
              borderRadius: 16,
              padding: "0.9rem",
              background: "hsl(var(--ui-surface-1) / 0.92)",
              display: "grid",
              gap: 10,
              alignContent: "start"
            }}
          >
            {selectedItem ? (
              <>
                <header style={{ display: "grid", gap: 4 }}>
                  <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                    Detail drawer
                  </p>
                  <h2 style={{ margin: 0, fontSize: 18 }}>{selectedItem.title}</h2>
                  <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                    {selectedItem.summary}
                  </p>
                </header>

                <div style={{ display: "grid", gap: 6, gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
                  <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                    Style
                    <select
                      value={previewPreset.styleId}
                      onChange={(event) =>
                        setPreviewPreset((previous) =>
                          repairPreset(
                            {
                              ...previous,
                              styleId: event.currentTarget.value as LuxuryPreset["styleId"]
                            },
                            { includeAlienTech: allowAlienTech }
                          )
                        )
                      }
                      className="kpiSelect"
                    >
                      {styleOptions.map((style) => (
                        <option
                          key={style.id}
                          value={style.id}
                          disabled={!selectedItem.styles.includes(style.id)}
                        >
                          {style.id}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                    Surface
                    <select
                      value={previewPreset.surfaceId}
                      onChange={(event) =>
                        setPreviewPreset((previous) => ({
                          ...previous,
                          surfaceId: event.currentTarget.value as LuxuryPreset["surfaceId"]
                        }))
                      }
                      className="kpiSelect"
                    >
                      {LUXURY_SURFACES.map((surface) => (
                        <option
                          key={surface.id}
                          value={surface.id}
                          disabled={!selectedItem.surfaces.includes(surface.id)}
                        >
                          {surface.id}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                  Material
                  <select
                    value={previewPreset.materialId}
                    onChange={(event) =>
                      setPreviewPreset((previous) =>
                        repairPreset(
                          {
                            ...previous,
                            materialId: event.currentTarget.value
                          },
                          { includeAlienTech: allowAlienTech }
                        )
                      )
                    }
                    className="kpiSelect"
                  >
                    {materialOptions.map((material) => (
                      <option key={material.id} value={material.id}>
                        {material.label} · {material.maturity}
                      </option>
                    ))}
                  </select>
                </label>

                <div style={{ display: "grid", gap: 6 }}>
                  <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                    Perf + Motion
                  </p>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {PERF_OPTIONS.map((profile) => (
                      <button
                        key={profile}
                        type="button"
                        className={`kpiPill ${previewPreset.perfProfile === profile ? "on" : ""}`}
                        onClick={() =>
                          setPreviewPreset((previous) => ({
                            ...previous,
                            perfProfile: profile
                          }))
                        }
                      >
                        {profile}
                      </button>
                    ))}
                    {MOTION_OPTIONS.map((motion) => (
                      <button
                        key={motion}
                        type="button"
                        className={`kpiPill ${previewPreset.motionLevel === motion ? "on" : ""}`}
                        onClick={() =>
                          setPreviewPreset((previous) => ({
                            ...previous,
                            motionLevel: motion
                          }))
                        }
                      >
                        {motion}
                      </button>
                    ))}
                  </div>
                </div>

                <label style={{ display: "grid", gap: 4, fontSize: 12 }}>
                  Data provider (Data Spine)
                  <select
                    value={dataProvider}
                    onChange={(event) => setDataProvider(event.currentTarget.value as DataProviderId)}
                    className="kpiSelect"
                  >
                    {PROVIDER_OPTIONS.map((provider) => (
                      <option key={provider} value={provider}>
                        {provider}
                      </option>
                    ))}
                  </select>
                </label>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button type="button" className="kpiActionBtn" onClick={onCopySnippet}>
                    Copy usage snippet
                  </button>
                  <button type="button" className="kpiActionBtn" onClick={onAddToShortlist}>
                    Add to shortlist
                  </button>
                </div>

                <div style={{ display: "grid", gap: 8 }}>
                  <div className="kpiBudget">
                    <p>GlowBudget: {governance.glow.value}/100</p>
                    <meter max={100} value={governance.glow.value} />
                  </div>
                  <div className="kpiBudget">
                    <p>MotionBudget: {governance.motion.value}/100</p>
                    <meter max={100} value={governance.motion.value} />
                  </div>
                  <div className="kpiBudget">
                    <p>Gold usage: {governance.goldUsage.value}/100</p>
                    <meter max={100} value={governance.goldUsage.value} />
                  </div>
                  {governance.warnings.map((warning) => (
                    <p key={warning} style={{ margin: 0, fontSize: 11, color: "#8d4b0f" }}>
                      {warning}
                    </p>
                  ))}
                </div>

                <section style={previewStyle}>
                  <div className="kpiPreviewShell">
                    <p style={{ margin: 0, fontSize: 12, opacity: 0.8 }}>
                      provider: {dataProvider} ({dataSpine.source})
                    </p>
                    <h3 style={{ margin: "0.2rem 0 0", fontSize: 16 }}>
                      {previewPayload?.title ?? selectedItem.title}
                    </h3>
                    {dataSpine.isLoading ? (
                      <p style={{ margin: 0, fontSize: 12 }}>Loading Data Spine payload...</p>
                    ) : previewPayload ? (
                      renderPreviewPayload(previewPayload)
                    ) : (
                      <p style={{ margin: 0, fontSize: 12 }}>No preview payload.</p>
                    )}
                    {dataSpine.errorMessage ? (
                      <p style={{ margin: 0, fontSize: 11, color: "#cb5c5c" }}>{dataSpine.errorMessage}</p>
                    ) : null}
                    {providerHints.length > 0 ? (
                      <ul style={{ margin: "0.35rem 0 0", paddingLeft: "1rem", display: "grid", gap: 2 }}>
                        {providerHints.map((hint) => (
                          <li key={hint} style={{ fontSize: 11 }}>
                            {hint}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                </section>

                <pre className="kpiPre">{selectedItem.snippet}</pre>
                <pre className="kpiPre">{previewCssText}</pre>
              </>
            ) : (
              <p style={{ margin: 0, fontSize: 12, color: "hsl(var(--ui-text-2))" }}>
                Select a KPI tile to open detail drawer.
              </p>
            )}
          </aside>
        </section>
      </section>

      {notice ? (
        <div className="kpiToast" role="status">
          {notice}
        </div>
      ) : null}

      <style jsx>{`
        .kpiSelect {
          border-radius: 10px;
          border: 1px solid hsl(var(--ui-border-1));
          background: hsl(var(--ui-surface-2));
          color: hsl(var(--ui-text-1));
          padding: 7px 8px;
          font-size: 12px;
        }
        .kpiTile {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 14px;
          padding: 10px;
          display: grid;
          gap: 5px;
          text-align: left;
          background: hsl(var(--ui-surface-2));
          color: hsl(var(--ui-text-1));
          cursor: pointer;
        }
        .kpiTile.selected {
          border-color: hsl(var(--ui-accent));
          box-shadow: 0 0 0 2px hsl(var(--ui-accent) / 0.22);
        }
        .kpiThumb {
          width: 34px;
          height: 34px;
          border-radius: 9px;
          border: 1px solid hsl(var(--ui-border-1));
          display: grid;
          place-items: center;
          font-size: 16px;
          background: linear-gradient(150deg, hsl(var(--ui-surface-1)), hsl(var(--ui-surface-3)));
        }
        .kpiPill {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 999px;
          padding: 4px 10px;
          font-size: 11px;
          background: hsl(var(--ui-surface-2));
          color: hsl(var(--ui-text-1));
          cursor: pointer;
        }
        .kpiPill.on {
          border-color: hsl(var(--ui-accent));
          background: hsl(var(--ui-accent) / 0.18);
        }
        .kpiActionBtn {
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 999px;
          background: hsl(var(--ui-surface-2));
          color: hsl(var(--ui-text-1));
          padding: 6px 12px;
          font-size: 12px;
          cursor: pointer;
        }
        .kpiBudget {
          display: grid;
          gap: 3px;
        }
        .kpiBudget p {
          margin: 0;
          font-size: 11px;
          color: hsl(var(--ui-text-2));
        }
        .kpiBudget meter {
          width: 100%;
        }
        .kpiPreviewShell {
          border-radius: var(--luxury-radius);
          border: 1px solid var(--luxury-border);
          background: var(--luxury-surface);
          color: var(--luxury-text);
          box-shadow: var(--luxury-shadow);
          padding: 0.8rem;
          display: grid;
          gap: 7px;
          backdrop-filter: blur(var(--luxury-blur-px));
          -webkit-backdrop-filter: blur(var(--luxury-blur-px));
        }
        .kpiEventRow {
          display: grid;
          grid-template-columns: 52px minmax(0, 1fr) 62px;
          gap: 6px;
          font-size: 11px;
          border: 1px solid color-mix(in srgb, var(--luxury-border) 65%, transparent);
          border-radius: 8px;
          padding: 6px 8px;
        }
        .kpiPre {
          margin: 0;
          border: 1px solid hsl(var(--ui-border-1));
          border-radius: 10px;
          background: hsl(var(--ui-surface-2));
          max-height: 110px;
          overflow: auto;
          padding: 8px;
          font-size: 11px;
        }
        .kpiToast {
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
      `}</style>
    </main>
  );
}
