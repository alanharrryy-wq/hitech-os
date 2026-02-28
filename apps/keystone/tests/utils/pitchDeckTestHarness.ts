import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

export const PITCH_ROUTE_FILES = Object.freeze([
  "app/pitch/page.tsx",
  "app/pitch/01-double-engine/page.tsx",
  "app/pitch/02-industrial-flow/page.tsx",
  "app/pitch/03-hitech-os/page.tsx",
  "app/pitch/04-valuation/page.tsx"
]);

export const REQUIRED_SUBROUTE_FILES = Object.freeze([
  "app/pitch/01-double-engine/page.tsx",
  "app/pitch/02-industrial-flow/page.tsx",
  "app/pitch/03-hitech-os/page.tsx",
  "app/pitch/04-valuation/page.tsx"
]);

export const ALL_LAYERS = Object.freeze([
  "stage.haze",
  "stage.vignette",
  "stage.noise",
  "stage.scanlines",
  "stage.horizon",
  "frame.bezel",
  "card.blur",
  "card.innerStroke",
  "card.specular",
  "card.grain",
  "card.shadowAmbient",
  "inset.shadow",
  "motion.enabled"
]);

export type LayerId = (typeof ALL_LAYERS)[number];

export type LayerProfile = "neutral" | "fx" | "perf";

export interface LayerFlags {
  readonly [key: string]: boolean;
}

export interface ResolvedLayerLike {
  readonly flags: Record<string, boolean>;
  readonly profile: string;
  readonly source: string;
  readonly debug: boolean;
  readonly raw?: Record<string, unknown>;
}

export interface LayerSearchParams {
  readonly layers?: string | string[] | undefined;
  readonly layerProfile?: string | string[] | undefined;
  readonly debug?: string | string[] | undefined;
}

export interface ExpectedLayerState {
  readonly source: "layers" | "profile" | "default";
  readonly profile: LayerProfile;
  readonly debug: boolean;
  readonly flags: Record<LayerId, boolean>;
}

export interface RenderedLayerMarkup {
  readonly html: string;
  readonly attrs: Readonly<Record<string, "on" | "off">>;
}

export interface KeystoneRuntime {
  readonly available: boolean;
  readonly reason: string;
  readonly appRoot: string | null;
  readonly uiKitModulePath: string | null;
  readonly resolveLayerFlags: ((searchParams: Record<string, string | string[] | undefined>) => unknown) | null;
  readonly LayerFlagsProvider: unknown;
  readonly Stage: unknown;
  readonly GlassCard: unknown;
  readonly LayerDebugPanel: unknown;
}

const PROFILE_PRESETS: Readonly<Record<LayerProfile, readonly LayerId[]>> = Object.freeze({
  neutral: [],
  fx: [
    "stage.haze",
    "stage.vignette",
    "stage.horizon",
    "stage.noise",
    "card.innerStroke",
    "card.shadowAmbient",
    "card.specular",
    "card.grain",
    "inset.shadow"
  ],
  perf: ["stage.vignette", "card.innerStroke"]
});

const LAYER_SET: ReadonlySet<string> = new Set(ALL_LAYERS);

const LAYER_DATA_ATTR_MAP: Readonly<Record<LayerId, string>> = Object.freeze({
  "stage.haze": "data-layer-stage-haze",
  "stage.vignette": "data-layer-stage-vignette",
  "stage.noise": "data-layer-stage-noise",
  "stage.scanlines": "data-layer-stage-scanlines",
  "stage.horizon": "data-layer-stage-horizon",
  "frame.bezel": "data-layer-frame-bezel",
  "card.blur": "data-layer-card-blur",
  "card.innerStroke": "data-layer-card-inner-stroke",
  "card.specular": "data-layer-card-specular",
  "card.grain": "data-layer-card-grain",
  "card.shadowAmbient": "data-layer-card-shadow-ambient",
  "inset.shadow": "data-layer-inset-shadow",
  "motion.enabled": "data-layer-motion-enabled"
});

function normalizePath(value: string): string {
  return value.split(path.sep).join("/");
}

function repoRootFromMetaUrl(metaUrl: string): string {
  const filePath = fileURLToPath(metaUrl);
  const normalized = path.resolve(filePath);

  let cursor = path.dirname(normalized);
  while (true) {
    const packageJson = path.join(cursor, "package.json");
    const appsDir = path.join(cursor, "apps");
    const packagesDir = path.join(cursor, "packages");

    if (fs.existsSync(packageJson) && fs.existsSync(appsDir) && fs.existsSync(packagesDir)) {
      return cursor;
    }

    const parent = path.dirname(cursor);
    if (parent === cursor) {
      break;
    }
    cursor = parent;
  }

  return path.resolve(path.join(path.dirname(normalized), "..", "..", ".."));
}

export function resolveAppRootFromMeta(metaUrl: string): string {
  const repoRoot = repoRootFromMetaUrl(metaUrl);
  return path.join(repoRoot, "apps", "keystone");
}

export function routeFileAbsolutePaths(appRoot: string): string[] {
  return PITCH_ROUTE_FILES.map((relativePath) => path.join(appRoot, relativePath));
}

export function hasPitchRouteTree(appRoot: string): boolean {
  for (const relativePath of PITCH_ROUTE_FILES) {
    const absolutePath = path.join(appRoot, relativePath);
    if (!fs.existsSync(absolutePath)) {
      return false;
    }
  }
  return true;
}

export function normalizeParam(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

export function createAllFlagsOff(): Record<LayerId, boolean> {
  const flags = {} as Record<LayerId, boolean>;
  for (const layerId of ALL_LAYERS) {
    flags[layerId] = false;
  }
  return flags;
}

export function createAllFlagsOn(): Record<LayerId, boolean> {
  const flags = {} as Record<LayerId, boolean>;
  for (const layerId of ALL_LAYERS) {
    flags[layerId] = true;
  }
  return flags;
}

function createFlagsFromEnabled(enabled: readonly LayerId[]): Record<LayerId, boolean> {
  const flags = createAllFlagsOff();
  for (const layerId of enabled) {
    flags[layerId] = true;
  }
  return flags;
}

function normalizeProfile(raw: string | undefined): LayerProfile | undefined {
  if (raw === "neutral" || raw === "fx" || raw === "perf") {
    return raw;
  }
  return undefined;
}

function parseLayerTokenList(rawLayers: string): LayerId[] {
  const tokens = rawLayers
    .split(",")
    .map((token) => token.trim())
    .filter((token) => token.length > 0);

  const ordered: LayerId[] = [];
  const seen = new Set<string>();

  for (const token of tokens) {
    if (!LAYER_SET.has(token)) {
      continue;
    }
    if (seen.has(token)) {
      continue;
    }
    seen.add(token);
    ordered.push(token as LayerId);
  }

  ordered.sort((left, right) => ALL_LAYERS.indexOf(left) - ALL_LAYERS.indexOf(right));
  return ordered;
}

export function resolveExpectedLayerState(params: LayerSearchParams): ExpectedLayerState {
  const rawLayers = normalizeParam(params.layers)?.trim();
  const normalizedLayers = rawLayers && rawLayers.length > 0 ? rawLayers : undefined;
  const rawProfile = normalizeParam(params.layerProfile);
  const rawDebug = normalizeParam(params.debug);

  const profile = normalizeProfile(rawProfile) ?? "neutral";
  const debug = rawDebug === "1";

  if (normalizedLayers != null) {
    if (normalizedLayers === "none") {
      return {
        source: "layers",
        profile,
        debug,
        flags: createAllFlagsOff()
      };
    }

    if (normalizedLayers === "all") {
      return {
        source: "layers",
        profile,
        debug,
        flags: createAllFlagsOn()
      };
    }

    return {
      source: "layers",
      profile,
      debug,
      flags: createFlagsFromEnabled(parseLayerTokenList(normalizedLayers))
    };
  }

  const normalizedProfile = normalizeProfile(rawProfile);
  if (normalizedProfile != null) {
    return {
      source: "profile",
      profile: normalizedProfile,
      debug,
      flags: createFlagsFromEnabled(PROFILE_PRESETS[normalizedProfile])
    };
  }

  return {
    source: "default",
    profile: "neutral",
    debug,
    flags: createAllFlagsOff()
  };
}

export function stableFlagSignature(flags: Record<string, boolean>): string {
  const chunks: string[] = [];
  for (const layerId of ALL_LAYERS) {
    chunks.push(`${layerId}:${flags[layerId] ? "1" : "0"}`);
  }
  return chunks.join("|");
}

export function extractDataLayerAttrs(html: string): Record<string, "on" | "off"> {
  const result: Record<string, "on" | "off"> = {};
  const attrPattern = /\s(data-layer-[a-z0-9-]+)="(on|off)"/g;

  let match: RegExpExecArray | null = null;
  while (true) {
    match = attrPattern.exec(html);
    if (match == null) {
      break;
    }
    result[match[1]] = match[2] as "on" | "off";
  }

  return result;
}

export function expectedAttrOnOff(state: ExpectedLayerState, layerId: LayerId): "on" | "off" {
  return state.flags[layerId] ? "on" : "off";
}

export function listAllKnownDataAttrs(): readonly string[] {
  return ALL_LAYERS.map((layerId) => LAYER_DATA_ATTR_MAP[layerId]);
}

export async function loadKeystoneRuntime(metaUrl: string): Promise<KeystoneRuntime> {
  const appRoot = resolveAppRootFromMeta(metaUrl);

  if (!hasPitchRouteTree(appRoot)) {
    return {
      available: false,
      reason: `missing pitch route tree under ${normalizePath(appRoot)}`,
      appRoot,
      uiKitModulePath: null,
      resolveLayerFlags: null,
      LayerFlagsProvider: null,
      Stage: null,
      GlassCard: null,
      LayerDebugPanel: null
    };
  }

  const repoRoot = path.dirname(path.dirname(appRoot));

  const moduleCandidates = [
    path.join(repoRoot, "packages", "ui-kit", "src", "index.ts"),
    path.join(repoRoot, "packages", "ui-kit", "src", "index.tsx")
  ];

  for (const modulePath of moduleCandidates) {
    if (!fs.existsSync(modulePath)) {
      continue;
    }

    try {
      const namespace = (await import(pathToFileURL(modulePath).href)) as Record<string, unknown>;
      const resolveLayerFlags = namespace.resolveLayerFlags;
      const LayerFlagsProvider = namespace.LayerFlagsProvider;
      const Stage = namespace.Stage;
      const GlassCard = namespace.GlassCard;
      const LayerDebugPanel = namespace.LayerDebugPanel;

      if (
        typeof resolveLayerFlags !== "function" ||
        typeof LayerFlagsProvider !== "function" ||
        typeof Stage !== "function" ||
        typeof GlassCard !== "function" ||
        typeof LayerDebugPanel !== "function"
      ) {
        continue;
      }

      return {
        available: true,
        reason: "",
        appRoot,
        uiKitModulePath: normalizePath(path.relative(repoRoot, modulePath)),
        resolveLayerFlags: resolveLayerFlags as (searchParams: Record<string, string | string[] | undefined>) => unknown,
        LayerFlagsProvider,
        Stage,
        GlassCard,
        LayerDebugPanel
      };
    } catch {
      continue;
    }
  }

  return {
    available: false,
    reason: "unable to import ui-kit runtime exports for layer tests",
    appRoot,
    uiKitModulePath: null,
    resolveLayerFlags: null,
    LayerFlagsProvider: null,
    Stage: null,
    GlassCard: null,
    LayerDebugPanel: null
  };
}

export async function importPitchPageModule(
  appRoot: string,
  relativeRouteFile: string
): Promise<unknown | null> {
  const absolutePath = path.join(appRoot, relativeRouteFile);
  if (!fs.existsSync(absolutePath)) {
    return null;
  }

  try {
    const namespace = (await import(pathToFileURL(absolutePath).href)) as Record<string, unknown>;
    return namespace.default ?? null;
  } catch {
    return null;
  }
}

export async function renderPitchPageToHtml(
  appRoot: string,
  relativeRouteFile: string,
  searchParams: Record<string, string | string[] | undefined>
): Promise<string | null> {
  const pageExport = await importPitchPageModule(appRoot, relativeRouteFile);
  if (typeof pageExport !== "function") {
    return null;
  }

  try {
    const output = pageExport({ searchParams });
    const awaited = output != null && typeof (output as Promise<unknown>).then === "function" ? await output : output;
    return renderToStaticMarkup(awaited as Parameters<typeof renderToStaticMarkup>[0]);
  } catch {
    return null;
  }
}

export function toRouteId(relativeRouteFile: string): string {
  return relativeRouteFile
    .replace(/^app\//, "")
    .replace(/\/page\.tsx$/, "")
    .replace(/[\/]/g, "-");
}
