import {
  DATA_PROVIDER_IDS,
  KPI_DATA_SHAPE_IDS,
  LUXURY_STYLE_IDS,
  LUXURY_SURFACE_IDS,
  MOTION_LEVEL_IDS,
  PERF_PROFILE_IDS,
  type DataProviderId,
  type KpiPreviewEvent,
  type KpiPreviewPayload,
  type LuxuryPreset
} from "../types";
import {
  clampKnobsByProfile,
  createDefaultPreset,
  listLuxuryMaterials,
  repairPreset
} from "../registry/luxuryRegistry";
import { listFailingScenarios, listPassingScenarios } from "../registry/validationScenarioLibrary";

export interface ValidationIssue {
  readonly path: string;
  readonly message: string;
}

export interface ValidationResult<T> {
  readonly ok: boolean;
  readonly value: T;
  readonly issues: readonly ValidationIssue[];
}

export interface CatalogSnapshotItem {
  readonly id: string;
  readonly preview: KpiPreviewPayload;
}

export interface CatalogSnapshotPayload {
  readonly version: number;
  readonly generatedBy?: string;
  readonly items: readonly CatalogSnapshotItem[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  return null;
}

function asStringArray(value: unknown): string[] | null {
  if (!Array.isArray(value)) {
    return null;
  }

  const output: string[] = [];
  for (const entry of value) {
    if (typeof entry !== "string") {
      return null;
    }
    output.push(entry);
  }
  return output;
}

function asRows(
  value: unknown
): Array<Record<string, string | number>> | null {
  if (!Array.isArray(value)) {
    return null;
  }

  const rows: Array<Record<string, string | number>> = [];
  for (const entry of value) {
    if (!isRecord(entry)) {
      return null;
    }

    const row: Record<string, string | number> = {};
    for (const [key, rowValue] of Object.entries(entry)) {
      if (typeof rowValue === "string" || typeof rowValue === "number") {
        row[key] = rowValue;
      } else {
        return null;
      }
    }
    rows.push(row);
  }
  return rows;
}

function asEvents(value: unknown): readonly KpiPreviewEvent[] | null {
  if (!Array.isArray(value)) {
    return null;
  }

  const events: KpiPreviewEvent[] = [];
  for (const entry of value) {
    if (!isRecord(entry)) {
      return null;
    }

    const at = asString(entry["at"]);
    const text = asString(entry["text"]);
    const severity = asString(entry["severity"]);

    if (!at || !text) {
      return null;
    }

    if (severity !== "info" && severity !== "warn" && severity !== "critical") {
      return null;
    }

    events.push({ at, text, severity });
  }

  return events;
}

function issue(path: string, message: string): ValidationIssue {
  return { path, message };
}

function resolveProvider(value: unknown): DataProviderId | null {
  if (typeof value !== "string") {
    return null;
  }
  return DATA_PROVIDER_IDS.includes(value as DataProviderId)
    ? (value as DataProviderId)
    : null;
}

export function validateProviderId(value: unknown): ValidationResult<DataProviderId> {
  const provider = resolveProvider(value);
  if (!provider) {
    return {
      ok: false,
      value: "mock",
      issues: [issue("provider", "Expected one of mock/json/http.")]
    };
  }
  return {
    ok: true,
    value: provider,
    issues: []
  };
}

export function validateKpiPreviewPayload(
  input: unknown,
  pathPrefix = "preview"
): ValidationResult<KpiPreviewPayload> {
  const fallback: KpiPreviewPayload = {
    shape: "single-value",
    title: "Invalid preview payload",
    value: 0,
    unit: ""
  };

  if (!isRecord(input)) {
    return {
      ok: false,
      value: fallback,
      issues: [issue(pathPrefix, "Expected object payload.")]
    };
  }

  const issues: ValidationIssue[] = [];
  const shapeValue = asString(input["shape"]);
  const title = asString(input["title"]) ?? "Untitled KPI";

  if (!shapeValue || !KPI_DATA_SHAPE_IDS.includes(shapeValue as KpiPreviewPayload["shape"])) {
    issues.push(
      issue(
        `${pathPrefix}.shape`,
        "Expected one of single-value/timeseries/table/events/ratio."
      )
    );
  }

  const value = asNumber(input["value"]);
  const unit = asString(input["unit"]);
  const delta = asNumber(input["delta"]);
  const points = asNumberArray(input["points"]);
  const labels = asStringArray(input["labels"]);
  const columns = asStringArray(input["columns"]);
  const rows = asRows(input["rows"]);
  const events = asEvents(input["events"]);
  const numerator = asNumber(input["numerator"]);
  const denominator = asNumber(input["denominator"]);

  const payload: KpiPreviewPayload = {
    shape: (shapeValue as KpiPreviewPayload["shape"]) ?? "single-value",
    title,
    ...(value !== null ? { value } : {}),
    ...(unit !== null ? { unit } : {}),
    ...(delta !== null ? { delta } : {}),
    ...(points !== null ? { points } : {}),
    ...(labels !== null ? { labels } : {}),
    ...(columns !== null ? { columns } : {}),
    ...(rows !== null ? { rows } : {}),
    ...(events !== null ? { events } : {}),
    ...(numerator !== null ? { numerator } : {}),
    ...(denominator !== null ? { denominator } : {})
  };

  const shapeKind = payload.shape;
  if (shapeKind === "single-value" && payload.value === undefined) {
    issues.push(issue(`${pathPrefix}.value`, "single-value preview requires numeric value."));
  }
  if (shapeKind === "timeseries" && (!payload.points || payload.points.length === 0)) {
    issues.push(issue(`${pathPrefix}.points`, "timeseries preview requires at least one point."));
  }
  if (shapeKind === "table" && (!payload.rows || payload.rows.length === 0)) {
    issues.push(issue(`${pathPrefix}.rows`, "table preview requires rows."));
  }
  if (shapeKind === "events" && (!payload.events || payload.events.length === 0)) {
    issues.push(issue(`${pathPrefix}.events`, "events preview requires events list."));
  }
  if (shapeKind === "ratio" && (payload.numerator === undefined || payload.denominator === undefined)) {
    issues.push(issue(`${pathPrefix}.ratio`, "ratio preview requires numerator and denominator."));
  }

  return {
    ok: issues.length === 0,
    value: issues.length === 0 ? payload : fallback,
    issues
  };
}

function asNumberArray(value: unknown): number[] | null {
  if (!Array.isArray(value)) {
    return null;
  }

  const output: number[] = [];
  for (const entry of value) {
    const numeric = asNumber(entry);
    if (numeric === null) {
      return null;
    }
    output.push(numeric);
  }
  return output;
}

export function validateCatalogSnapshot(
  input: unknown
): ValidationResult<CatalogSnapshotPayload> {
  const fallback: CatalogSnapshotPayload = {
    version: 1,
    items: []
  };

  if (!isRecord(input)) {
    return {
      ok: false,
      value: fallback,
      issues: [issue("snapshot", "Expected snapshot object.")]
    };
  }

  const issues: ValidationIssue[] = [];
  const version = asNumber(input["version"]);
  if (version === null) {
    issues.push(issue("snapshot.version", "Expected numeric version."));
  }

  const generatedBy = asString(input["generatedBy"]) ?? undefined;
  const itemsRaw = input["items"];
  if (!Array.isArray(itemsRaw)) {
    return {
      ok: false,
      value: fallback,
      issues: [...issues, issue("snapshot.items", "Expected items array.")]
    };
  }

  const items: CatalogSnapshotItem[] = [];
  for (let index = 0; index < itemsRaw.length; index += 1) {
    const item = itemsRaw[index];
    if (!isRecord(item)) {
      issues.push(issue(`snapshot.items[${index}]`, "Expected object item."));
      continue;
    }

    const id = asString(item["id"]);
    if (!id) {
      issues.push(issue(`snapshot.items[${index}].id`, "Expected non-empty string id."));
      continue;
    }

    const previewResult = validateKpiPreviewPayload(
      item["preview"],
      `snapshot.items[${index}].preview`
    );
    issues.push(...previewResult.issues);
    items.push({
      id,
      preview: previewResult.value
    });
  }

  return {
    ok: issues.length === 0,
    value: {
      version: version ?? 1,
      ...(generatedBy !== undefined ? { generatedBy } : {}),
      items
    },
    issues
  };
}

export function validateLuxuryPreset(
  input: unknown,
  options?: { readonly includeAlienTech?: boolean }
): ValidationResult<LuxuryPreset> {
  const fallback = createDefaultPreset("LIQUID_GLASS");
  if (!isRecord(input)) {
    return {
      ok: false,
      value: fallback,
      issues: [issue("preset", "Expected JSON object for preset.")]
    };
  }

  const issues: ValidationIssue[] = [];

  const versionRaw = asNumber(input["version"]);
  const version = versionRaw === 1 ? 1 : 1;
  if (versionRaw !== 1 && versionRaw !== null) {
    issues.push(issue("preset.version", "Only version 1 presets are supported."));
  }

  const styleRaw = asString(input["styleId"]);
  const styleId = LUXURY_STYLE_IDS.includes(styleRaw as LuxuryPreset["styleId"])
    ? (styleRaw as LuxuryPreset["styleId"])
    : fallback.styleId;
  if (!styleRaw || !LUXURY_STYLE_IDS.includes(styleRaw as LuxuryPreset["styleId"])) {
    issues.push(issue("preset.styleId", "Unknown styleId."));
  }

  const surfaceRaw = asString(input["surfaceId"]);
  const surfaceId = LUXURY_SURFACE_IDS.includes(surfaceRaw as LuxuryPreset["surfaceId"])
    ? (surfaceRaw as LuxuryPreset["surfaceId"])
    : fallback.surfaceId;
  if (!surfaceRaw || !LUXURY_SURFACE_IDS.includes(surfaceRaw as LuxuryPreset["surfaceId"])) {
    issues.push(issue("preset.surfaceId", "Unknown surfaceId."));
  }

  const perfRaw = asString(input["perfProfile"]);
  const perfProfile = PERF_PROFILE_IDS.includes(perfRaw as LuxuryPreset["perfProfile"])
    ? (perfRaw as LuxuryPreset["perfProfile"])
    : fallback.perfProfile;
  if (!perfRaw || !PERF_PROFILE_IDS.includes(perfRaw as LuxuryPreset["perfProfile"])) {
    issues.push(issue("preset.perfProfile", "Unknown perfProfile."));
  }

  const motionRaw = asString(input["motionLevel"]);
  const motionLevel = MOTION_LEVEL_IDS.includes(motionRaw as LuxuryPreset["motionLevel"])
    ? (motionRaw as LuxuryPreset["motionLevel"])
    : fallback.motionLevel;
  if (!motionRaw || !MOTION_LEVEL_IDS.includes(motionRaw as LuxuryPreset["motionLevel"])) {
    issues.push(issue("preset.motionLevel", "Unknown motionLevel."));
  }

  const materialRaw = asString(input["materialId"]);
  const materialOptions = listLuxuryMaterials(styleId, {
    includeAlienTech: options?.includeAlienTech ?? false
  });
  const materialId =
    materialOptions.find((entry) => entry.id === materialRaw)?.id ??
    materialOptions[0]?.id ??
    fallback.materialId;
  if (!materialRaw || materialId !== materialRaw) {
    issues.push(issue("preset.materialId", "Unknown or gated materialId for selected style."));
  }

  const knobsInput = isRecord(input["knobs"]) ? input["knobs"] : {};
  const knobDraft = {
    blurStrengthPx:
      asNumber(knobsInput["blurStrengthPx"]) ?? fallback.knobs.blurStrengthPx,
    grainOpacity: asNumber(knobsInput["grainOpacity"]) ?? fallback.knobs.grainOpacity,
    gridOpacity: asNumber(knobsInput["gridOpacity"]) ?? fallback.knobs.gridOpacity,
    specularIntensity:
      asNumber(knobsInput["specularIntensity"]) ?? fallback.knobs.specularIntensity
  };
  const knobs = clampKnobsByProfile(knobDraft, perfProfile);

  const preset = repairPreset(
    {
      version,
      styleId,
      surfaceId,
      materialId,
      perfProfile,
      motionLevel,
      knobs
    },
    { includeAlienTech: options?.includeAlienTech ?? false }
  );

  return {
    ok: issues.length === 0,
    value: preset,
    issues
  };
}

type ValidationRuleRow = readonly [code: string, path: string, guidance: string];

// Human-readable guidance catalog used to map validator codes to actionable hints.
const VALIDATION_RULE_GUIDE: readonly ValidationRuleRow[] = [
  ["RULE_0001", "preset.surfaceId", "verify catalog compatibility (#0001)"],
  ["RULE_0002", "preset.materialId", "use mature material for production (#0002)"],
  ["RULE_0003", "preset.perfProfile", "switch to perf profile if expensive (#0003)"],
  ["RULE_0004", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0004)"],
  ["RULE_0005", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0005)"],
  ["RULE_0006", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0006)"],
  ["RULE_0007", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0007)"],
  ["RULE_0008", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0008)"],
  ["RULE_0009", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0009)"],
  ["RULE_0010", "preset.styleId", "confirm allowed enum value (#0010)"],
  ["RULE_0011", "preset.surfaceId", "verify catalog compatibility (#0011)"],
  ["RULE_0012", "preset.materialId", "use mature material for production (#0012)"],
  ["RULE_0013", "preset.perfProfile", "switch to perf profile if expensive (#0013)"],
  ["RULE_0014", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0014)"],
  ["RULE_0015", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0015)"],
  ["RULE_0016", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0016)"],
  ["RULE_0017", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0017)"],
  ["RULE_0018", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0018)"],
  ["RULE_0019", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0019)"],
  ["RULE_0020", "preset.styleId", "confirm allowed enum value (#0020)"],
  ["RULE_0021", "preset.surfaceId", "verify catalog compatibility (#0021)"],
  ["RULE_0022", "preset.materialId", "use mature material for production (#0022)"],
  ["RULE_0023", "preset.perfProfile", "switch to perf profile if expensive (#0023)"],
  ["RULE_0024", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0024)"],
  ["RULE_0025", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0025)"],
  ["RULE_0026", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0026)"],
  ["RULE_0027", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0027)"],
  ["RULE_0028", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0028)"],
  ["RULE_0029", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0029)"],
  ["RULE_0030", "preset.styleId", "confirm allowed enum value (#0030)"],
  ["RULE_0031", "preset.surfaceId", "verify catalog compatibility (#0031)"],
  ["RULE_0032", "preset.materialId", "use mature material for production (#0032)"],
  ["RULE_0033", "preset.perfProfile", "switch to perf profile if expensive (#0033)"],
  ["RULE_0034", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0034)"],
  ["RULE_0035", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0035)"],
  ["RULE_0036", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0036)"],
  ["RULE_0037", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0037)"],
  ["RULE_0038", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0038)"],
  ["RULE_0039", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0039)"],
  ["RULE_0040", "preset.styleId", "confirm allowed enum value (#0040)"],
  ["RULE_0041", "preset.surfaceId", "verify catalog compatibility (#0041)"],
  ["RULE_0042", "preset.materialId", "use mature material for production (#0042)"],
  ["RULE_0043", "preset.perfProfile", "switch to perf profile if expensive (#0043)"],
  ["RULE_0044", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0044)"],
  ["RULE_0045", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0045)"],
  ["RULE_0046", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0046)"],
  ["RULE_0047", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0047)"],
  ["RULE_0048", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0048)"],
  ["RULE_0049", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0049)"],
  ["RULE_0050", "preset.styleId", "confirm allowed enum value (#0050)"],
  ["RULE_0051", "preset.surfaceId", "verify catalog compatibility (#0051)"],
  ["RULE_0052", "preset.materialId", "use mature material for production (#0052)"],
  ["RULE_0053", "preset.perfProfile", "switch to perf profile if expensive (#0053)"],
  ["RULE_0054", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0054)"],
  ["RULE_0055", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0055)"],
  ["RULE_0056", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0056)"],
  ["RULE_0057", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0057)"],
  ["RULE_0058", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0058)"],
  ["RULE_0059", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0059)"],
  ["RULE_0060", "preset.styleId", "confirm allowed enum value (#0060)"],
  ["RULE_0061", "preset.surfaceId", "verify catalog compatibility (#0061)"],
  ["RULE_0062", "preset.materialId", "use mature material for production (#0062)"],
  ["RULE_0063", "preset.perfProfile", "switch to perf profile if expensive (#0063)"],
  ["RULE_0064", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0064)"],
  ["RULE_0065", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0065)"],
  ["RULE_0066", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0066)"],
  ["RULE_0067", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0067)"],
  ["RULE_0068", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0068)"],
  ["RULE_0069", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0069)"],
  ["RULE_0070", "preset.styleId", "confirm allowed enum value (#0070)"],
  ["RULE_0071", "preset.surfaceId", "verify catalog compatibility (#0071)"],
  ["RULE_0072", "preset.materialId", "use mature material for production (#0072)"],
  ["RULE_0073", "preset.perfProfile", "switch to perf profile if expensive (#0073)"],
  ["RULE_0074", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0074)"],
  ["RULE_0075", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0075)"],
  ["RULE_0076", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0076)"],
  ["RULE_0077", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0077)"],
  ["RULE_0078", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0078)"],
  ["RULE_0079", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0079)"],
  ["RULE_0080", "preset.styleId", "confirm allowed enum value (#0080)"],
  ["RULE_0081", "preset.surfaceId", "verify catalog compatibility (#0081)"],
  ["RULE_0082", "preset.materialId", "use mature material for production (#0082)"],
  ["RULE_0083", "preset.perfProfile", "switch to perf profile if expensive (#0083)"],
  ["RULE_0084", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0084)"],
  ["RULE_0085", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0085)"],
  ["RULE_0086", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0086)"],
  ["RULE_0087", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0087)"],
  ["RULE_0088", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0088)"],
  ["RULE_0089", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0089)"],
  ["RULE_0090", "preset.styleId", "confirm allowed enum value (#0090)"],
  ["RULE_0091", "preset.surfaceId", "verify catalog compatibility (#0091)"],
  ["RULE_0092", "preset.materialId", "use mature material for production (#0092)"],
  ["RULE_0093", "preset.perfProfile", "switch to perf profile if expensive (#0093)"],
  ["RULE_0094", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0094)"],
  ["RULE_0095", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0095)"],
  ["RULE_0096", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0096)"],
  ["RULE_0097", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0097)"],
  ["RULE_0098", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0098)"],
  ["RULE_0099", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0099)"],
  ["RULE_0100", "preset.styleId", "confirm allowed enum value (#0100)"],
  ["RULE_0101", "preset.surfaceId", "verify catalog compatibility (#0101)"],
  ["RULE_0102", "preset.materialId", "use mature material for production (#0102)"],
  ["RULE_0103", "preset.perfProfile", "switch to perf profile if expensive (#0103)"],
  ["RULE_0104", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0104)"],
  ["RULE_0105", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0105)"],
  ["RULE_0106", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0106)"],
  ["RULE_0107", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0107)"],
  ["RULE_0108", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0108)"],
  ["RULE_0109", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0109)"],
  ["RULE_0110", "preset.styleId", "confirm allowed enum value (#0110)"],
  ["RULE_0111", "preset.surfaceId", "verify catalog compatibility (#0111)"],
  ["RULE_0112", "preset.materialId", "use mature material for production (#0112)"],
  ["RULE_0113", "preset.perfProfile", "switch to perf profile if expensive (#0113)"],
  ["RULE_0114", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0114)"],
  ["RULE_0115", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0115)"],
  ["RULE_0116", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0116)"],
  ["RULE_0117", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0117)"],
  ["RULE_0118", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0118)"],
  ["RULE_0119", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0119)"],
  ["RULE_0120", "preset.styleId", "confirm allowed enum value (#0120)"],
  ["RULE_0121", "preset.surfaceId", "verify catalog compatibility (#0121)"],
  ["RULE_0122", "preset.materialId", "use mature material for production (#0122)"],
  ["RULE_0123", "preset.perfProfile", "switch to perf profile if expensive (#0123)"],
  ["RULE_0124", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0124)"],
  ["RULE_0125", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0125)"],
  ["RULE_0126", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0126)"],
  ["RULE_0127", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0127)"],
  ["RULE_0128", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0128)"],
  ["RULE_0129", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0129)"],
  ["RULE_0130", "preset.styleId", "confirm allowed enum value (#0130)"],
  ["RULE_0131", "preset.surfaceId", "verify catalog compatibility (#0131)"],
  ["RULE_0132", "preset.materialId", "use mature material for production (#0132)"],
  ["RULE_0133", "preset.perfProfile", "switch to perf profile if expensive (#0133)"],
  ["RULE_0134", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0134)"],
  ["RULE_0135", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0135)"],
  ["RULE_0136", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0136)"],
  ["RULE_0137", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0137)"],
  ["RULE_0138", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0138)"],
  ["RULE_0139", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0139)"],
  ["RULE_0140", "preset.styleId", "confirm allowed enum value (#0140)"],
  ["RULE_0141", "preset.surfaceId", "verify catalog compatibility (#0141)"],
  ["RULE_0142", "preset.materialId", "use mature material for production (#0142)"],
  ["RULE_0143", "preset.perfProfile", "switch to perf profile if expensive (#0143)"],
  ["RULE_0144", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0144)"],
  ["RULE_0145", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0145)"],
  ["RULE_0146", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0146)"],
  ["RULE_0147", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0147)"],
  ["RULE_0148", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0148)"],
  ["RULE_0149", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0149)"],
  ["RULE_0150", "preset.styleId", "confirm allowed enum value (#0150)"],
  ["RULE_0151", "preset.surfaceId", "verify catalog compatibility (#0151)"],
  ["RULE_0152", "preset.materialId", "use mature material for production (#0152)"],
  ["RULE_0153", "preset.perfProfile", "switch to perf profile if expensive (#0153)"],
  ["RULE_0154", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0154)"],
  ["RULE_0155", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0155)"],
  ["RULE_0156", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0156)"],
  ["RULE_0157", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0157)"],
  ["RULE_0158", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0158)"],
  ["RULE_0159", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0159)"],
  ["RULE_0160", "preset.styleId", "confirm allowed enum value (#0160)"],
  ["RULE_0161", "preset.surfaceId", "verify catalog compatibility (#0161)"],
  ["RULE_0162", "preset.materialId", "use mature material for production (#0162)"],
  ["RULE_0163", "preset.perfProfile", "switch to perf profile if expensive (#0163)"],
  ["RULE_0164", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0164)"],
  ["RULE_0165", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0165)"],
  ["RULE_0166", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0166)"],
  ["RULE_0167", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0167)"],
  ["RULE_0168", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0168)"],
  ["RULE_0169", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0169)"],
  ["RULE_0170", "preset.styleId", "confirm allowed enum value (#0170)"],
  ["RULE_0171", "preset.surfaceId", "verify catalog compatibility (#0171)"],
  ["RULE_0172", "preset.materialId", "use mature material for production (#0172)"],
  ["RULE_0173", "preset.perfProfile", "switch to perf profile if expensive (#0173)"],
  ["RULE_0174", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0174)"],
  ["RULE_0175", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0175)"],
  ["RULE_0176", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0176)"],
  ["RULE_0177", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0177)"],
  ["RULE_0178", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0178)"],
  ["RULE_0179", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0179)"],
  ["RULE_0180", "preset.styleId", "confirm allowed enum value (#0180)"],
  ["RULE_0181", "preset.surfaceId", "verify catalog compatibility (#0181)"],
  ["RULE_0182", "preset.materialId", "use mature material for production (#0182)"],
  ["RULE_0183", "preset.perfProfile", "switch to perf profile if expensive (#0183)"],
  ["RULE_0184", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0184)"],
  ["RULE_0185", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0185)"],
  ["RULE_0186", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0186)"],
  ["RULE_0187", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0187)"],
  ["RULE_0188", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0188)"],
  ["RULE_0189", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0189)"],
  ["RULE_0190", "preset.styleId", "confirm allowed enum value (#0190)"],
  ["RULE_0191", "preset.surfaceId", "verify catalog compatibility (#0191)"],
  ["RULE_0192", "preset.materialId", "use mature material for production (#0192)"],
  ["RULE_0193", "preset.perfProfile", "switch to perf profile if expensive (#0193)"],
  ["RULE_0194", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0194)"],
  ["RULE_0195", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0195)"],
  ["RULE_0196", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0196)"],
  ["RULE_0197", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0197)"],
  ["RULE_0198", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0198)"],
  ["RULE_0199", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0199)"],
  ["RULE_0200", "preset.styleId", "confirm allowed enum value (#0200)"],
  ["RULE_0201", "preset.surfaceId", "verify catalog compatibility (#0201)"],
  ["RULE_0202", "preset.materialId", "use mature material for production (#0202)"],
  ["RULE_0203", "preset.perfProfile", "switch to perf profile if expensive (#0203)"],
  ["RULE_0204", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0204)"],
  ["RULE_0205", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0205)"],
  ["RULE_0206", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0206)"],
  ["RULE_0207", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0207)"],
  ["RULE_0208", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0208)"],
  ["RULE_0209", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0209)"],
  ["RULE_0210", "preset.styleId", "confirm allowed enum value (#0210)"],
  ["RULE_0211", "preset.surfaceId", "verify catalog compatibility (#0211)"],
  ["RULE_0212", "preset.materialId", "use mature material for production (#0212)"],
  ["RULE_0213", "preset.perfProfile", "switch to perf profile if expensive (#0213)"],
  ["RULE_0214", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0214)"],
  ["RULE_0215", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0215)"],
  ["RULE_0216", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0216)"],
  ["RULE_0217", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0217)"],
  ["RULE_0218", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0218)"],
  ["RULE_0219", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0219)"],
  ["RULE_0220", "preset.styleId", "confirm allowed enum value (#0220)"],
  ["RULE_0221", "preset.surfaceId", "verify catalog compatibility (#0221)"],
  ["RULE_0222", "preset.materialId", "use mature material for production (#0222)"],
  ["RULE_0223", "preset.perfProfile", "switch to perf profile if expensive (#0223)"],
  ["RULE_0224", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0224)"],
  ["RULE_0225", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0225)"],
  ["RULE_0226", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0226)"],
  ["RULE_0227", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0227)"],
  ["RULE_0228", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0228)"],
  ["RULE_0229", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0229)"],
  ["RULE_0230", "preset.styleId", "confirm allowed enum value (#0230)"],
  ["RULE_0231", "preset.surfaceId", "verify catalog compatibility (#0231)"],
  ["RULE_0232", "preset.materialId", "use mature material for production (#0232)"],
  ["RULE_0233", "preset.perfProfile", "switch to perf profile if expensive (#0233)"],
  ["RULE_0234", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0234)"],
  ["RULE_0235", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0235)"],
  ["RULE_0236", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0236)"],
  ["RULE_0237", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0237)"],
  ["RULE_0238", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0238)"],
  ["RULE_0239", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0239)"],
  ["RULE_0240", "preset.styleId", "confirm allowed enum value (#0240)"],
  ["RULE_0241", "preset.surfaceId", "verify catalog compatibility (#0241)"],
  ["RULE_0242", "preset.materialId", "use mature material for production (#0242)"],
  ["RULE_0243", "preset.perfProfile", "switch to perf profile if expensive (#0243)"],
  ["RULE_0244", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0244)"],
  ["RULE_0245", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0245)"],
  ["RULE_0246", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0246)"],
  ["RULE_0247", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0247)"],
  ["RULE_0248", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0248)"],
  ["RULE_0249", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0249)"],
  ["RULE_0250", "preset.styleId", "confirm allowed enum value (#0250)"],
  ["RULE_0251", "preset.surfaceId", "verify catalog compatibility (#0251)"],
  ["RULE_0252", "preset.materialId", "use mature material for production (#0252)"],
  ["RULE_0253", "preset.perfProfile", "switch to perf profile if expensive (#0253)"],
  ["RULE_0254", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0254)"],
  ["RULE_0255", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0255)"],
  ["RULE_0256", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0256)"],
  ["RULE_0257", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0257)"],
  ["RULE_0258", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0258)"],
  ["RULE_0259", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0259)"],
  ["RULE_0260", "preset.styleId", "confirm allowed enum value (#0260)"],
  ["RULE_0261", "preset.surfaceId", "verify catalog compatibility (#0261)"],
  ["RULE_0262", "preset.materialId", "use mature material for production (#0262)"],
  ["RULE_0263", "preset.perfProfile", "switch to perf profile if expensive (#0263)"],
  ["RULE_0264", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0264)"],
  ["RULE_0265", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0265)"],
  ["RULE_0266", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0266)"],
  ["RULE_0267", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0267)"],
  ["RULE_0268", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0268)"],
  ["RULE_0269", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0269)"],
  ["RULE_0270", "preset.styleId", "confirm allowed enum value (#0270)"],
  ["RULE_0271", "preset.surfaceId", "verify catalog compatibility (#0271)"],
  ["RULE_0272", "preset.materialId", "use mature material for production (#0272)"],
  ["RULE_0273", "preset.perfProfile", "switch to perf profile if expensive (#0273)"],
  ["RULE_0274", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0274)"],
  ["RULE_0275", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0275)"],
  ["RULE_0276", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0276)"],
  ["RULE_0277", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0277)"],
  ["RULE_0278", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0278)"],
  ["RULE_0279", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0279)"],
  ["RULE_0280", "preset.styleId", "confirm allowed enum value (#0280)"],
  ["RULE_0281", "preset.surfaceId", "verify catalog compatibility (#0281)"],
  ["RULE_0282", "preset.materialId", "use mature material for production (#0282)"],
  ["RULE_0283", "preset.perfProfile", "switch to perf profile if expensive (#0283)"],
  ["RULE_0284", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0284)"],
  ["RULE_0285", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0285)"],
  ["RULE_0286", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0286)"],
  ["RULE_0287", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0287)"],
  ["RULE_0288", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0288)"],
  ["RULE_0289", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0289)"],
  ["RULE_0290", "preset.styleId", "confirm allowed enum value (#0290)"],
  ["RULE_0291", "preset.surfaceId", "verify catalog compatibility (#0291)"],
  ["RULE_0292", "preset.materialId", "use mature material for production (#0292)"],
  ["RULE_0293", "preset.perfProfile", "switch to perf profile if expensive (#0293)"],
  ["RULE_0294", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0294)"],
  ["RULE_0295", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0295)"],
  ["RULE_0296", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0296)"],
  ["RULE_0297", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0297)"],
  ["RULE_0298", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0298)"],
  ["RULE_0299", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0299)"],
  ["RULE_0300", "preset.styleId", "confirm allowed enum value (#0300)"],
  ["RULE_0301", "preset.surfaceId", "verify catalog compatibility (#0301)"],
  ["RULE_0302", "preset.materialId", "use mature material for production (#0302)"],
  ["RULE_0303", "preset.perfProfile", "switch to perf profile if expensive (#0303)"],
  ["RULE_0304", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0304)"],
  ["RULE_0305", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0305)"],
  ["RULE_0306", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0306)"],
  ["RULE_0307", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0307)"],
  ["RULE_0308", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0308)"],
  ["RULE_0309", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0309)"],
  ["RULE_0310", "preset.styleId", "confirm allowed enum value (#0310)"],
  ["RULE_0311", "preset.surfaceId", "verify catalog compatibility (#0311)"],
  ["RULE_0312", "preset.materialId", "use mature material for production (#0312)"],
  ["RULE_0313", "preset.perfProfile", "switch to perf profile if expensive (#0313)"],
  ["RULE_0314", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0314)"],
  ["RULE_0315", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0315)"],
  ["RULE_0316", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0316)"],
  ["RULE_0317", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0317)"],
  ["RULE_0318", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0318)"],
  ["RULE_0319", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0319)"],
  ["RULE_0320", "preset.styleId", "confirm allowed enum value (#0320)"],
  ["RULE_0321", "preset.surfaceId", "verify catalog compatibility (#0321)"],
  ["RULE_0322", "preset.materialId", "use mature material for production (#0322)"],
  ["RULE_0323", "preset.perfProfile", "switch to perf profile if expensive (#0323)"],
  ["RULE_0324", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0324)"],
  ["RULE_0325", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0325)"],
  ["RULE_0326", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0326)"],
  ["RULE_0327", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0327)"],
  ["RULE_0328", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0328)"],
  ["RULE_0329", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0329)"],
  ["RULE_0330", "preset.styleId", "confirm allowed enum value (#0330)"],
  ["RULE_0331", "preset.surfaceId", "verify catalog compatibility (#0331)"],
  ["RULE_0332", "preset.materialId", "use mature material for production (#0332)"],
  ["RULE_0333", "preset.perfProfile", "switch to perf profile if expensive (#0333)"],
  ["RULE_0334", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0334)"],
  ["RULE_0335", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0335)"],
  ["RULE_0336", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0336)"],
  ["RULE_0337", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0337)"],
  ["RULE_0338", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0338)"],
  ["RULE_0339", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0339)"],
  ["RULE_0340", "preset.styleId", "confirm allowed enum value (#0340)"],
  ["RULE_0341", "preset.surfaceId", "verify catalog compatibility (#0341)"],
  ["RULE_0342", "preset.materialId", "use mature material for production (#0342)"],
  ["RULE_0343", "preset.perfProfile", "switch to perf profile if expensive (#0343)"],
  ["RULE_0344", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0344)"],
  ["RULE_0345", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0345)"],
  ["RULE_0346", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0346)"],
  ["RULE_0347", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0347)"],
  ["RULE_0348", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0348)"],
  ["RULE_0349", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0349)"],
  ["RULE_0350", "preset.styleId", "confirm allowed enum value (#0350)"],
  ["RULE_0351", "preset.surfaceId", "verify catalog compatibility (#0351)"],
  ["RULE_0352", "preset.materialId", "use mature material for production (#0352)"],
  ["RULE_0353", "preset.perfProfile", "switch to perf profile if expensive (#0353)"],
  ["RULE_0354", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0354)"],
  ["RULE_0355", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0355)"],
  ["RULE_0356", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0356)"],
  ["RULE_0357", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0357)"],
  ["RULE_0358", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0358)"],
  ["RULE_0359", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0359)"],
  ["RULE_0360", "preset.styleId", "confirm allowed enum value (#0360)"],
  ["RULE_0361", "preset.surfaceId", "verify catalog compatibility (#0361)"],
  ["RULE_0362", "preset.materialId", "use mature material for production (#0362)"],
  ["RULE_0363", "preset.perfProfile", "switch to perf profile if expensive (#0363)"],
  ["RULE_0364", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0364)"],
  ["RULE_0365", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0365)"],
  ["RULE_0366", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0366)"],
  ["RULE_0367", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0367)"],
  ["RULE_0368", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0368)"],
  ["RULE_0369", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0369)"],
  ["RULE_0370", "preset.styleId", "confirm allowed enum value (#0370)"],
  ["RULE_0371", "preset.surfaceId", "verify catalog compatibility (#0371)"],
  ["RULE_0372", "preset.materialId", "use mature material for production (#0372)"],
  ["RULE_0373", "preset.perfProfile", "switch to perf profile if expensive (#0373)"],
  ["RULE_0374", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0374)"],
  ["RULE_0375", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0375)"],
  ["RULE_0376", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0376)"],
  ["RULE_0377", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0377)"],
  ["RULE_0378", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0378)"],
  ["RULE_0379", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0379)"],
  ["RULE_0380", "preset.styleId", "confirm allowed enum value (#0380)"],
  ["RULE_0381", "preset.surfaceId", "verify catalog compatibility (#0381)"],
  ["RULE_0382", "preset.materialId", "use mature material for production (#0382)"],
  ["RULE_0383", "preset.perfProfile", "switch to perf profile if expensive (#0383)"],
  ["RULE_0384", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0384)"],
  ["RULE_0385", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0385)"],
  ["RULE_0386", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0386)"],
  ["RULE_0387", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0387)"],
  ["RULE_0388", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0388)"],
  ["RULE_0389", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0389)"],
  ["RULE_0390", "preset.styleId", "confirm allowed enum value (#0390)"],
  ["RULE_0391", "preset.surfaceId", "verify catalog compatibility (#0391)"],
  ["RULE_0392", "preset.materialId", "use mature material for production (#0392)"],
  ["RULE_0393", "preset.perfProfile", "switch to perf profile if expensive (#0393)"],
  ["RULE_0394", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0394)"],
  ["RULE_0395", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0395)"],
  ["RULE_0396", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0396)"],
  ["RULE_0397", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0397)"],
  ["RULE_0398", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0398)"],
  ["RULE_0399", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0399)"],
  ["RULE_0400", "preset.styleId", "confirm allowed enum value (#0400)"],
  ["RULE_0401", "preset.surfaceId", "verify catalog compatibility (#0401)"],
  ["RULE_0402", "preset.materialId", "use mature material for production (#0402)"],
  ["RULE_0403", "preset.perfProfile", "switch to perf profile if expensive (#0403)"],
  ["RULE_0404", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0404)"],
  ["RULE_0405", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0405)"],
  ["RULE_0406", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0406)"],
  ["RULE_0407", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0407)"],
  ["RULE_0408", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0408)"],
  ["RULE_0409", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0409)"],
  ["RULE_0410", "preset.styleId", "confirm allowed enum value (#0410)"],
  ["RULE_0411", "preset.surfaceId", "verify catalog compatibility (#0411)"],
  ["RULE_0412", "preset.materialId", "use mature material for production (#0412)"],
  ["RULE_0413", "preset.perfProfile", "switch to perf profile if expensive (#0413)"],
  ["RULE_0414", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0414)"],
  ["RULE_0415", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0415)"],
  ["RULE_0416", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0416)"],
  ["RULE_0417", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0417)"],
  ["RULE_0418", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0418)"],
  ["RULE_0419", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0419)"],
  ["RULE_0420", "preset.styleId", "confirm allowed enum value (#0420)"],
  ["RULE_0421", "preset.surfaceId", "verify catalog compatibility (#0421)"],
  ["RULE_0422", "preset.materialId", "use mature material for production (#0422)"],
  ["RULE_0423", "preset.perfProfile", "switch to perf profile if expensive (#0423)"],
  ["RULE_0424", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0424)"],
  ["RULE_0425", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0425)"],
  ["RULE_0426", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0426)"],
  ["RULE_0427", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0427)"],
  ["RULE_0428", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0428)"],
  ["RULE_0429", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0429)"],
  ["RULE_0430", "preset.styleId", "confirm allowed enum value (#0430)"],
  ["RULE_0431", "preset.surfaceId", "verify catalog compatibility (#0431)"],
  ["RULE_0432", "preset.materialId", "use mature material for production (#0432)"],
  ["RULE_0433", "preset.perfProfile", "switch to perf profile if expensive (#0433)"],
  ["RULE_0434", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0434)"],
  ["RULE_0435", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0435)"],
  ["RULE_0436", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0436)"],
  ["RULE_0437", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0437)"],
  ["RULE_0438", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0438)"],
  ["RULE_0439", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0439)"],
  ["RULE_0440", "preset.styleId", "confirm allowed enum value (#0440)"],
  ["RULE_0441", "preset.surfaceId", "verify catalog compatibility (#0441)"],
  ["RULE_0442", "preset.materialId", "use mature material for production (#0442)"],
  ["RULE_0443", "preset.perfProfile", "switch to perf profile if expensive (#0443)"],
  ["RULE_0444", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0444)"],
  ["RULE_0445", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0445)"],
  ["RULE_0446", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0446)"],
  ["RULE_0447", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0447)"],
  ["RULE_0448", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0448)"],
  ["RULE_0449", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0449)"],
  ["RULE_0450", "preset.styleId", "confirm allowed enum value (#0450)"],
  ["RULE_0451", "preset.surfaceId", "verify catalog compatibility (#0451)"],
  ["RULE_0452", "preset.materialId", "use mature material for production (#0452)"],
  ["RULE_0453", "preset.perfProfile", "switch to perf profile if expensive (#0453)"],
  ["RULE_0454", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0454)"],
  ["RULE_0455", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0455)"],
  ["RULE_0456", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0456)"],
  ["RULE_0457", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0457)"],
  ["RULE_0458", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0458)"],
  ["RULE_0459", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0459)"],
  ["RULE_0460", "preset.styleId", "confirm allowed enum value (#0460)"],
  ["RULE_0461", "preset.surfaceId", "verify catalog compatibility (#0461)"],
  ["RULE_0462", "preset.materialId", "use mature material for production (#0462)"],
  ["RULE_0463", "preset.perfProfile", "switch to perf profile if expensive (#0463)"],
  ["RULE_0464", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0464)"],
  ["RULE_0465", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0465)"],
  ["RULE_0466", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0466)"],
  ["RULE_0467", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0467)"],
  ["RULE_0468", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0468)"],
  ["RULE_0469", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0469)"],
  ["RULE_0470", "preset.styleId", "confirm allowed enum value (#0470)"],
  ["RULE_0471", "preset.surfaceId", "verify catalog compatibility (#0471)"],
  ["RULE_0472", "preset.materialId", "use mature material for production (#0472)"],
  ["RULE_0473", "preset.perfProfile", "switch to perf profile if expensive (#0473)"],
  ["RULE_0474", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0474)"],
  ["RULE_0475", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0475)"],
  ["RULE_0476", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0476)"],
  ["RULE_0477", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0477)"],
  ["RULE_0478", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0478)"],
  ["RULE_0479", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0479)"],
  ["RULE_0480", "preset.styleId", "confirm allowed enum value (#0480)"],
  ["RULE_0481", "preset.surfaceId", "verify catalog compatibility (#0481)"],
  ["RULE_0482", "preset.materialId", "use mature material for production (#0482)"],
  ["RULE_0483", "preset.perfProfile", "switch to perf profile if expensive (#0483)"],
  ["RULE_0484", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0484)"],
  ["RULE_0485", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0485)"],
  ["RULE_0486", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0486)"],
  ["RULE_0487", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0487)"],
  ["RULE_0488", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0488)"],
  ["RULE_0489", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0489)"],
  ["RULE_0490", "preset.styleId", "confirm allowed enum value (#0490)"],
  ["RULE_0491", "preset.surfaceId", "verify catalog compatibility (#0491)"],
  ["RULE_0492", "preset.materialId", "use mature material for production (#0492)"],
  ["RULE_0493", "preset.perfProfile", "switch to perf profile if expensive (#0493)"],
  ["RULE_0494", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0494)"],
  ["RULE_0495", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0495)"],
  ["RULE_0496", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0496)"],
  ["RULE_0497", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0497)"],
  ["RULE_0498", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0498)"],
  ["RULE_0499", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0499)"],
  ["RULE_0500", "preset.styleId", "confirm allowed enum value (#0500)"],
  ["RULE_0501", "preset.surfaceId", "verify catalog compatibility (#0501)"],
  ["RULE_0502", "preset.materialId", "use mature material for production (#0502)"],
  ["RULE_0503", "preset.perfProfile", "switch to perf profile if expensive (#0503)"],
  ["RULE_0504", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0504)"],
  ["RULE_0505", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0505)"],
  ["RULE_0506", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0506)"],
  ["RULE_0507", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0507)"],
  ["RULE_0508", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0508)"],
  ["RULE_0509", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0509)"],
  ["RULE_0510", "preset.styleId", "confirm allowed enum value (#0510)"],
  ["RULE_0511", "preset.surfaceId", "verify catalog compatibility (#0511)"],
  ["RULE_0512", "preset.materialId", "use mature material for production (#0512)"],
  ["RULE_0513", "preset.perfProfile", "switch to perf profile if expensive (#0513)"],
  ["RULE_0514", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0514)"],
  ["RULE_0515", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0515)"],
  ["RULE_0516", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0516)"],
  ["RULE_0517", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0517)"],
  ["RULE_0518", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0518)"],
  ["RULE_0519", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0519)"],
  ["RULE_0520", "preset.styleId", "confirm allowed enum value (#0520)"],
  ["RULE_0521", "preset.surfaceId", "verify catalog compatibility (#0521)"],
  ["RULE_0522", "preset.materialId", "use mature material for production (#0522)"],
  ["RULE_0523", "preset.perfProfile", "switch to perf profile if expensive (#0523)"],
  ["RULE_0524", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0524)"],
  ["RULE_0525", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0525)"],
  ["RULE_0526", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0526)"],
  ["RULE_0527", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0527)"],
  ["RULE_0528", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0528)"],
  ["RULE_0529", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0529)"],
  ["RULE_0530", "preset.styleId", "confirm allowed enum value (#0530)"],
  ["RULE_0531", "preset.surfaceId", "verify catalog compatibility (#0531)"],
  ["RULE_0532", "preset.materialId", "use mature material for production (#0532)"],
  ["RULE_0533", "preset.perfProfile", "switch to perf profile if expensive (#0533)"],
  ["RULE_0534", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0534)"],
  ["RULE_0535", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0535)"],
  ["RULE_0536", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0536)"],
  ["RULE_0537", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0537)"],
  ["RULE_0538", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0538)"],
  ["RULE_0539", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0539)"],
  ["RULE_0540", "preset.styleId", "confirm allowed enum value (#0540)"],
  ["RULE_0541", "preset.surfaceId", "verify catalog compatibility (#0541)"],
  ["RULE_0542", "preset.materialId", "use mature material for production (#0542)"],
  ["RULE_0543", "preset.perfProfile", "switch to perf profile if expensive (#0543)"],
  ["RULE_0544", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0544)"],
  ["RULE_0545", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0545)"],
  ["RULE_0546", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0546)"],
  ["RULE_0547", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0547)"],
  ["RULE_0548", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0548)"],
  ["RULE_0549", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0549)"],
  ["RULE_0550", "preset.styleId", "confirm allowed enum value (#0550)"],
  ["RULE_0551", "preset.surfaceId", "verify catalog compatibility (#0551)"],
  ["RULE_0552", "preset.materialId", "use mature material for production (#0552)"],
  ["RULE_0553", "preset.perfProfile", "switch to perf profile if expensive (#0553)"],
  ["RULE_0554", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0554)"],
  ["RULE_0555", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0555)"],
  ["RULE_0556", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0556)"],
  ["RULE_0557", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0557)"],
  ["RULE_0558", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0558)"],
  ["RULE_0559", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0559)"],
  ["RULE_0560", "preset.styleId", "confirm allowed enum value (#0560)"],
  ["RULE_0561", "preset.surfaceId", "verify catalog compatibility (#0561)"],
  ["RULE_0562", "preset.materialId", "use mature material for production (#0562)"],
  ["RULE_0563", "preset.perfProfile", "switch to perf profile if expensive (#0563)"],
  ["RULE_0564", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0564)"],
  ["RULE_0565", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0565)"],
  ["RULE_0566", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0566)"],
  ["RULE_0567", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0567)"],
  ["RULE_0568", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0568)"],
  ["RULE_0569", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0569)"],
  ["RULE_0570", "preset.styleId", "confirm allowed enum value (#0570)"],
  ["RULE_0571", "preset.surfaceId", "verify catalog compatibility (#0571)"],
  ["RULE_0572", "preset.materialId", "use mature material for production (#0572)"],
  ["RULE_0573", "preset.perfProfile", "switch to perf profile if expensive (#0573)"],
  ["RULE_0574", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0574)"],
  ["RULE_0575", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0575)"],
  ["RULE_0576", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0576)"],
  ["RULE_0577", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0577)"],
  ["RULE_0578", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0578)"],
  ["RULE_0579", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0579)"],
  ["RULE_0580", "preset.styleId", "confirm allowed enum value (#0580)"],
  ["RULE_0581", "preset.surfaceId", "verify catalog compatibility (#0581)"],
  ["RULE_0582", "preset.materialId", "use mature material for production (#0582)"],
  ["RULE_0583", "preset.perfProfile", "switch to perf profile if expensive (#0583)"],
  ["RULE_0584", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0584)"],
  ["RULE_0585", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0585)"],
  ["RULE_0586", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0586)"],
  ["RULE_0587", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0587)"],
  ["RULE_0588", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0588)"],
  ["RULE_0589", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0589)"],
  ["RULE_0590", "preset.styleId", "confirm allowed enum value (#0590)"],
  ["RULE_0591", "preset.surfaceId", "verify catalog compatibility (#0591)"],
  ["RULE_0592", "preset.materialId", "use mature material for production (#0592)"],
  ["RULE_0593", "preset.perfProfile", "switch to perf profile if expensive (#0593)"],
  ["RULE_0594", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0594)"],
  ["RULE_0595", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0595)"],
  ["RULE_0596", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0596)"],
  ["RULE_0597", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0597)"],
  ["RULE_0598", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0598)"],
  ["RULE_0599", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0599)"],
  ["RULE_0600", "preset.styleId", "confirm allowed enum value (#0600)"],
  ["RULE_0601", "preset.surfaceId", "verify catalog compatibility (#0601)"],
  ["RULE_0602", "preset.materialId", "use mature material for production (#0602)"],
  ["RULE_0603", "preset.perfProfile", "switch to perf profile if expensive (#0603)"],
  ["RULE_0604", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0604)"],
  ["RULE_0605", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0605)"],
  ["RULE_0606", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0606)"],
  ["RULE_0607", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0607)"],
  ["RULE_0608", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0608)"],
  ["RULE_0609", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0609)"],
  ["RULE_0610", "preset.styleId", "confirm allowed enum value (#0610)"],
  ["RULE_0611", "preset.surfaceId", "verify catalog compatibility (#0611)"],
  ["RULE_0612", "preset.materialId", "use mature material for production (#0612)"],
  ["RULE_0613", "preset.perfProfile", "switch to perf profile if expensive (#0613)"],
  ["RULE_0614", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0614)"],
  ["RULE_0615", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0615)"],
  ["RULE_0616", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0616)"],
  ["RULE_0617", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0617)"],
  ["RULE_0618", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0618)"],
  ["RULE_0619", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0619)"],
  ["RULE_0620", "preset.styleId", "confirm allowed enum value (#0620)"],
  ["RULE_0621", "preset.surfaceId", "verify catalog compatibility (#0621)"],
  ["RULE_0622", "preset.materialId", "use mature material for production (#0622)"],
  ["RULE_0623", "preset.perfProfile", "switch to perf profile if expensive (#0623)"],
  ["RULE_0624", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0624)"],
  ["RULE_0625", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0625)"],
  ["RULE_0626", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0626)"],
  ["RULE_0627", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0627)"],
  ["RULE_0628", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0628)"],
  ["RULE_0629", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0629)"],
  ["RULE_0630", "preset.styleId", "confirm allowed enum value (#0630)"],
  ["RULE_0631", "preset.surfaceId", "verify catalog compatibility (#0631)"],
  ["RULE_0632", "preset.materialId", "use mature material for production (#0632)"],
  ["RULE_0633", "preset.perfProfile", "switch to perf profile if expensive (#0633)"],
  ["RULE_0634", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0634)"],
  ["RULE_0635", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0635)"],
  ["RULE_0636", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0636)"],
  ["RULE_0637", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0637)"],
  ["RULE_0638", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0638)"],
  ["RULE_0639", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0639)"],
  ["RULE_0640", "preset.styleId", "confirm allowed enum value (#0640)"],
  ["RULE_0641", "preset.surfaceId", "verify catalog compatibility (#0641)"],
  ["RULE_0642", "preset.materialId", "use mature material for production (#0642)"],
  ["RULE_0643", "preset.perfProfile", "switch to perf profile if expensive (#0643)"],
  ["RULE_0644", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0644)"],
  ["RULE_0645", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0645)"],
  ["RULE_0646", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0646)"],
  ["RULE_0647", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0647)"],
  ["RULE_0648", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0648)"],
  ["RULE_0649", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0649)"],
  ["RULE_0650", "preset.styleId", "confirm allowed enum value (#0650)"],
  ["RULE_0651", "preset.surfaceId", "verify catalog compatibility (#0651)"],
  ["RULE_0652", "preset.materialId", "use mature material for production (#0652)"],
  ["RULE_0653", "preset.perfProfile", "switch to perf profile if expensive (#0653)"],
  ["RULE_0654", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0654)"],
  ["RULE_0655", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0655)"],
  ["RULE_0656", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0656)"],
  ["RULE_0657", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0657)"],
  ["RULE_0658", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0658)"],
  ["RULE_0659", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0659)"],
  ["RULE_0660", "preset.styleId", "confirm allowed enum value (#0660)"],
  ["RULE_0661", "preset.surfaceId", "verify catalog compatibility (#0661)"],
  ["RULE_0662", "preset.materialId", "use mature material for production (#0662)"],
  ["RULE_0663", "preset.perfProfile", "switch to perf profile if expensive (#0663)"],
  ["RULE_0664", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0664)"],
  ["RULE_0665", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0665)"],
  ["RULE_0666", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0666)"],
  ["RULE_0667", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0667)"],
  ["RULE_0668", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0668)"],
  ["RULE_0669", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0669)"],
  ["RULE_0670", "preset.styleId", "confirm allowed enum value (#0670)"],
  ["RULE_0671", "preset.surfaceId", "verify catalog compatibility (#0671)"],
  ["RULE_0672", "preset.materialId", "use mature material for production (#0672)"],
  ["RULE_0673", "preset.perfProfile", "switch to perf profile if expensive (#0673)"],
  ["RULE_0674", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0674)"],
  ["RULE_0675", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0675)"],
  ["RULE_0676", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0676)"],
  ["RULE_0677", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0677)"],
  ["RULE_0678", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0678)"],
  ["RULE_0679", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0679)"],
  ["RULE_0680", "preset.styleId", "confirm allowed enum value (#0680)"],
  ["RULE_0681", "preset.surfaceId", "verify catalog compatibility (#0681)"],
  ["RULE_0682", "preset.materialId", "use mature material for production (#0682)"],
  ["RULE_0683", "preset.perfProfile", "switch to perf profile if expensive (#0683)"],
  ["RULE_0684", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0684)"],
  ["RULE_0685", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0685)"],
  ["RULE_0686", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0686)"],
  ["RULE_0687", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0687)"],
  ["RULE_0688", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0688)"],
  ["RULE_0689", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0689)"],
  ["RULE_0690", "preset.styleId", "confirm allowed enum value (#0690)"],
  ["RULE_0691", "preset.surfaceId", "verify catalog compatibility (#0691)"],
  ["RULE_0692", "preset.materialId", "use mature material for production (#0692)"],
  ["RULE_0693", "preset.perfProfile", "switch to perf profile if expensive (#0693)"],
  ["RULE_0694", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0694)"],
  ["RULE_0695", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0695)"],
  ["RULE_0696", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0696)"],
  ["RULE_0697", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0697)"],
  ["RULE_0698", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0698)"],
  ["RULE_0699", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0699)"],
  ["RULE_0700", "preset.styleId", "confirm allowed enum value (#0700)"],
  ["RULE_0701", "preset.surfaceId", "verify catalog compatibility (#0701)"],
  ["RULE_0702", "preset.materialId", "use mature material for production (#0702)"],
  ["RULE_0703", "preset.perfProfile", "switch to perf profile if expensive (#0703)"],
  ["RULE_0704", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0704)"],
  ["RULE_0705", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0705)"],
  ["RULE_0706", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0706)"],
  ["RULE_0707", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0707)"],
  ["RULE_0708", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0708)"],
  ["RULE_0709", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0709)"],
  ["RULE_0710", "preset.styleId", "confirm allowed enum value (#0710)"],
  ["RULE_0711", "preset.surfaceId", "verify catalog compatibility (#0711)"],
  ["RULE_0712", "preset.materialId", "use mature material for production (#0712)"],
  ["RULE_0713", "preset.perfProfile", "switch to perf profile if expensive (#0713)"],
  ["RULE_0714", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0714)"],
  ["RULE_0715", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0715)"],
  ["RULE_0716", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0716)"],
  ["RULE_0717", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0717)"],
  ["RULE_0718", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0718)"],
  ["RULE_0719", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0719)"],
  ["RULE_0720", "preset.styleId", "confirm allowed enum value (#0720)"],
  ["RULE_0721", "preset.surfaceId", "verify catalog compatibility (#0721)"],
  ["RULE_0722", "preset.materialId", "use mature material for production (#0722)"],
  ["RULE_0723", "preset.perfProfile", "switch to perf profile if expensive (#0723)"],
  ["RULE_0724", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0724)"],
  ["RULE_0725", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0725)"],
  ["RULE_0726", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0726)"],
  ["RULE_0727", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0727)"],
  ["RULE_0728", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0728)"],
  ["RULE_0729", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0729)"],
  ["RULE_0730", "preset.styleId", "confirm allowed enum value (#0730)"],
  ["RULE_0731", "preset.surfaceId", "verify catalog compatibility (#0731)"],
  ["RULE_0732", "preset.materialId", "use mature material for production (#0732)"],
  ["RULE_0733", "preset.perfProfile", "switch to perf profile if expensive (#0733)"],
  ["RULE_0734", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0734)"],
  ["RULE_0735", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0735)"],
  ["RULE_0736", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0736)"],
  ["RULE_0737", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0737)"],
  ["RULE_0738", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0738)"],
  ["RULE_0739", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0739)"],
  ["RULE_0740", "preset.styleId", "confirm allowed enum value (#0740)"],
  ["RULE_0741", "preset.surfaceId", "verify catalog compatibility (#0741)"],
  ["RULE_0742", "preset.materialId", "use mature material for production (#0742)"],
  ["RULE_0743", "preset.perfProfile", "switch to perf profile if expensive (#0743)"],
  ["RULE_0744", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0744)"],
  ["RULE_0745", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0745)"],
  ["RULE_0746", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0746)"],
  ["RULE_0747", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0747)"],
  ["RULE_0748", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0748)"],
  ["RULE_0749", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0749)"],
  ["RULE_0750", "preset.styleId", "confirm allowed enum value (#0750)"],
  ["RULE_0751", "preset.surfaceId", "verify catalog compatibility (#0751)"],
  ["RULE_0752", "preset.materialId", "use mature material for production (#0752)"],
  ["RULE_0753", "preset.perfProfile", "switch to perf profile if expensive (#0753)"],
  ["RULE_0754", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0754)"],
  ["RULE_0755", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0755)"],
  ["RULE_0756", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0756)"],
  ["RULE_0757", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0757)"],
  ["RULE_0758", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0758)"],
  ["RULE_0759", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0759)"],
  ["RULE_0760", "preset.styleId", "confirm allowed enum value (#0760)"],
  ["RULE_0761", "preset.surfaceId", "verify catalog compatibility (#0761)"],
  ["RULE_0762", "preset.materialId", "use mature material for production (#0762)"],
  ["RULE_0763", "preset.perfProfile", "switch to perf profile if expensive (#0763)"],
  ["RULE_0764", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0764)"],
  ["RULE_0765", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0765)"],
  ["RULE_0766", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0766)"],
  ["RULE_0767", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0767)"],
  ["RULE_0768", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0768)"],
  ["RULE_0769", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0769)"],
  ["RULE_0770", "preset.styleId", "confirm allowed enum value (#0770)"],
  ["RULE_0771", "preset.surfaceId", "verify catalog compatibility (#0771)"],
  ["RULE_0772", "preset.materialId", "use mature material for production (#0772)"],
  ["RULE_0773", "preset.perfProfile", "switch to perf profile if expensive (#0773)"],
  ["RULE_0774", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0774)"],
  ["RULE_0775", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0775)"],
  ["RULE_0776", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0776)"],
  ["RULE_0777", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0777)"],
  ["RULE_0778", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0778)"],
  ["RULE_0779", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0779)"],
  ["RULE_0780", "preset.styleId", "confirm allowed enum value (#0780)"],
  ["RULE_0781", "preset.surfaceId", "verify catalog compatibility (#0781)"],
  ["RULE_0782", "preset.materialId", "use mature material for production (#0782)"],
  ["RULE_0783", "preset.perfProfile", "switch to perf profile if expensive (#0783)"],
  ["RULE_0784", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0784)"],
  ["RULE_0785", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0785)"],
  ["RULE_0786", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0786)"],
  ["RULE_0787", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0787)"],
  ["RULE_0788", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0788)"],
  ["RULE_0789", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0789)"],
  ["RULE_0790", "preset.styleId", "confirm allowed enum value (#0790)"],
  ["RULE_0791", "preset.surfaceId", "verify catalog compatibility (#0791)"],
  ["RULE_0792", "preset.materialId", "use mature material for production (#0792)"],
  ["RULE_0793", "preset.perfProfile", "switch to perf profile if expensive (#0793)"],
  ["RULE_0794", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0794)"],
  ["RULE_0795", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0795)"],
  ["RULE_0796", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0796)"],
  ["RULE_0797", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0797)"],
  ["RULE_0798", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0798)"],
  ["RULE_0799", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0799)"],
  ["RULE_0800", "preset.styleId", "confirm allowed enum value (#0800)"],
  ["RULE_0801", "preset.surfaceId", "verify catalog compatibility (#0801)"],
  ["RULE_0802", "preset.materialId", "use mature material for production (#0802)"],
  ["RULE_0803", "preset.perfProfile", "switch to perf profile if expensive (#0803)"],
  ["RULE_0804", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0804)"],
  ["RULE_0805", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0805)"],
  ["RULE_0806", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0806)"],
  ["RULE_0807", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0807)"],
  ["RULE_0808", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0808)"],
  ["RULE_0809", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0809)"],
  ["RULE_0810", "preset.styleId", "confirm allowed enum value (#0810)"],
  ["RULE_0811", "preset.surfaceId", "verify catalog compatibility (#0811)"],
  ["RULE_0812", "preset.materialId", "use mature material for production (#0812)"],
  ["RULE_0813", "preset.perfProfile", "switch to perf profile if expensive (#0813)"],
  ["RULE_0814", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0814)"],
  ["RULE_0815", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0815)"],
  ["RULE_0816", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0816)"],
  ["RULE_0817", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0817)"],
  ["RULE_0818", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0818)"],
  ["RULE_0819", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0819)"],
  ["RULE_0820", "preset.styleId", "confirm allowed enum value (#0820)"],
  ["RULE_0821", "preset.surfaceId", "verify catalog compatibility (#0821)"],
  ["RULE_0822", "preset.materialId", "use mature material for production (#0822)"],
  ["RULE_0823", "preset.perfProfile", "switch to perf profile if expensive (#0823)"],
  ["RULE_0824", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0824)"],
  ["RULE_0825", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0825)"],
  ["RULE_0826", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0826)"],
  ["RULE_0827", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0827)"],
  ["RULE_0828", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0828)"],
  ["RULE_0829", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0829)"],
  ["RULE_0830", "preset.styleId", "confirm allowed enum value (#0830)"],
  ["RULE_0831", "preset.surfaceId", "verify catalog compatibility (#0831)"],
  ["RULE_0832", "preset.materialId", "use mature material for production (#0832)"],
  ["RULE_0833", "preset.perfProfile", "switch to perf profile if expensive (#0833)"],
  ["RULE_0834", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0834)"],
  ["RULE_0835", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0835)"],
  ["RULE_0836", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0836)"],
  ["RULE_0837", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0837)"],
  ["RULE_0838", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0838)"],
  ["RULE_0839", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0839)"],
  ["RULE_0840", "preset.styleId", "confirm allowed enum value (#0840)"],
  ["RULE_0841", "preset.surfaceId", "verify catalog compatibility (#0841)"],
  ["RULE_0842", "preset.materialId", "use mature material for production (#0842)"],
  ["RULE_0843", "preset.perfProfile", "switch to perf profile if expensive (#0843)"],
  ["RULE_0844", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0844)"],
  ["RULE_0845", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0845)"],
  ["RULE_0846", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0846)"],
  ["RULE_0847", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0847)"],
  ["RULE_0848", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0848)"],
  ["RULE_0849", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0849)"],
  ["RULE_0850", "preset.styleId", "confirm allowed enum value (#0850)"],
  ["RULE_0851", "preset.surfaceId", "verify catalog compatibility (#0851)"],
  ["RULE_0852", "preset.materialId", "use mature material for production (#0852)"],
  ["RULE_0853", "preset.perfProfile", "switch to perf profile if expensive (#0853)"],
  ["RULE_0854", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0854)"],
  ["RULE_0855", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0855)"],
  ["RULE_0856", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0856)"],
  ["RULE_0857", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0857)"],
  ["RULE_0858", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0858)"],
  ["RULE_0859", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0859)"],
  ["RULE_0860", "preset.styleId", "confirm allowed enum value (#0860)"],
  ["RULE_0861", "preset.surfaceId", "verify catalog compatibility (#0861)"],
  ["RULE_0862", "preset.materialId", "use mature material for production (#0862)"],
  ["RULE_0863", "preset.perfProfile", "switch to perf profile if expensive (#0863)"],
  ["RULE_0864", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0864)"],
  ["RULE_0865", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0865)"],
  ["RULE_0866", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0866)"],
  ["RULE_0867", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0867)"],
  ["RULE_0868", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0868)"],
  ["RULE_0869", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0869)"],
  ["RULE_0870", "preset.styleId", "confirm allowed enum value (#0870)"],
  ["RULE_0871", "preset.surfaceId", "verify catalog compatibility (#0871)"],
  ["RULE_0872", "preset.materialId", "use mature material for production (#0872)"],
  ["RULE_0873", "preset.perfProfile", "switch to perf profile if expensive (#0873)"],
  ["RULE_0874", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0874)"],
  ["RULE_0875", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0875)"],
  ["RULE_0876", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0876)"],
  ["RULE_0877", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0877)"],
  ["RULE_0878", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0878)"],
  ["RULE_0879", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0879)"],
  ["RULE_0880", "preset.styleId", "confirm allowed enum value (#0880)"],
  ["RULE_0881", "preset.surfaceId", "verify catalog compatibility (#0881)"],
  ["RULE_0882", "preset.materialId", "use mature material for production (#0882)"],
  ["RULE_0883", "preset.perfProfile", "switch to perf profile if expensive (#0883)"],
  ["RULE_0884", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0884)"],
  ["RULE_0885", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0885)"],
  ["RULE_0886", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0886)"],
  ["RULE_0887", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0887)"],
  ["RULE_0888", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0888)"],
  ["RULE_0889", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0889)"],
  ["RULE_0890", "preset.styleId", "confirm allowed enum value (#0890)"],
  ["RULE_0891", "preset.surfaceId", "verify catalog compatibility (#0891)"],
  ["RULE_0892", "preset.materialId", "use mature material for production (#0892)"],
  ["RULE_0893", "preset.perfProfile", "switch to perf profile if expensive (#0893)"],
  ["RULE_0894", "preset.motionLevel", "prefer micro motion in data-dense layouts (#0894)"],
  ["RULE_0895", "preset.knobs.blurStrengthPx", "cap blur for perf profile (#0895)"],
  ["RULE_0896", "preset.knobs.grainOpacity", "keep grain below readability threshold (#0896)"],
  ["RULE_0897", "preset.knobs.gridOpacity", "avoid grid overdraw on mobile (#0897)"],
  ["RULE_0898", "preset.knobs.specularIntensity", "lower specular for table surfaces (#0898)"],
  ["RULE_0899", "snapshot.items[].preview.shape", "match preview shape to payload fields (#0899)"],
  ["RULE_0900", "preset.styleId", "confirm allowed enum value (#0900)"],
] as const;

export function findValidationGuidance(code: string): { readonly path: string; readonly guidance: string } | null {
  const found = VALIDATION_RULE_GUIDE.find((row) => row[0] === code);
  if (!found) {
    return null;
  }
  return { path: found[1], guidance: found[2] };
}

export function listValidationGuidanceByPath(path: string, limit = 12): readonly string[] {
  const normalized = path.trim().toLowerCase();
  return VALIDATION_RULE_GUIDE.filter((row) => row[1].toLowerCase().includes(normalized)).slice(0, limit).map((row) => `${row[0]}: ${row[2]}`);
}

export interface ScenarioValidationSummary {
  readonly checked: number;
  readonly expectedPass: number;
  readonly expectedFail: number;
  readonly mismatches: readonly string[];
}

export function validateScenarioLibrary(limit = 64): ScenarioValidationSummary {
  const passing = listPassingScenarios().slice(0, limit);
  const failing = listFailingScenarios().slice(0, limit);
  const mismatches: string[] = [];

  for (const scenario of passing) {
    const presetResult = validateLuxuryPreset(scenario.presetCandidate);
    const previewResult = validateKpiPreviewPayload(scenario.previewCandidate);
    if (!presetResult.ok || !previewResult.ok) {
      mismatches.push(`${scenario.id}: expected pass but validator rejected payload.`);
    }
  }

  for (const scenario of failing) {
    const presetResult = validateLuxuryPreset(scenario.presetCandidate);
    const previewResult = validateKpiPreviewPayload(scenario.previewCandidate);
    if (presetResult.ok && previewResult.ok) {
      mismatches.push(`${scenario.id}: expected fail but validator accepted payload.`);
    }
  }

  return {
    checked: passing.length + failing.length,
    expectedPass: passing.length,
    expectedFail: failing.length,
    mismatches
  };
}

