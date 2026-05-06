"use client";

import { CSSProperties, PointerEvent as ReactPointerEvent, useEffect, useMemo, useRef, useState } from "react";
import styles from "./prisma-studio-pro-qa.module.css";
import {
  PRISMA_REALTIME_DEFAULT_URL,
  applyPrismaRealtimePayload,
  broadcastPrismaRealtimePayload,
  buildPrismaRealtimePayload,
  connectPrismaRealtime,
  createPrismaRealtimeClientId,
  type PrismaRealtimeStatus,
  type PrismaVisualRealtimePayload,
  type PrismaVisualSurface
} from "../../src/visual-os/realtime/prisma-realtime-client";

type ControlKey = "glass" | "blur" | "glow" | "neon" | "depth" | "contrast" | "density" | "motion" | "radius" | "shadow" | "saturation" | "shine" | "grain" | "edge";
type Controls = Record<ControlKey, number>;
type DockMode = "free" | "right" | "left" | "bottom";
type LayerKey = "background" | "atmosphere" | "shell" | "surface" | "content" | "action" | "state" | "focus" | "overlay";
type WorkbenchMode = "simple" | "advanced" | "expert";
type ControlRelevance = "primary" | "secondary" | "ghost";
type LayerGuide = {
  name: string;
  plainName: string;
  intent: string;
  modifies: string[];
  doesNotTouch: string[];
  affectedSelectors: string[];
};
type ControlCopy = { label: string; help: string; relevance: ControlRelevance };
type Snapshot = { id: string; name: string; createdAt: string; surface: PrismaVisualSurface; recipeName: string; controls: Controls; score: StudioScore };
type StudioScore = { overall: number; readability: number; operation: number; premium: number; motion: number; safety: number; verdict: "READY" | "WARN" | "BLOCKED" };

type FloatingState = { x: number; y: number; width: number; height: number; dock: DockMode; minimized: boolean; surface: PrismaVisualSurface; layer: LayerKey };
type DragState = { type: "move"; startX: number; startY: number; originX: number; originY: number } | { type: "resize"; startX: number; startY: number; originWidth: number; originHeight: number };


const ROUTE_TRUTH_PACKAGE_MARKER = "PRISMA_VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM";

type PrismaRouteTruth = {
  protocol: string;
  host: string;
  realtimeUrl: string;
  realtimeHealthUrl: string;
  realtimeEventsUrl: string;
  realtimeStateUrl: string;
  tabletAppUrl: string;
  tabletPosUrl: string;
  visualOsProUrl: string;
  pcUrl: string;
  mobileUrl: string;
  surfaceUrls: Record<PrismaVisualSurface, { label: string; targetUrl: string; shortPath: string }>;
};

function getPrismaBrowserProtocol() {
  if (typeof window === "undefined") return "http:";
  return window.location.protocol === "https:" ? "https:" : "http:";
}

function getPrismaBrowserHost() {
  if (typeof window === "undefined") return "127.0.0.1";
  return window.location.hostname || "127.0.0.1";
}

function getDefaultPrismaRealtimeUrl() {
  return `${getPrismaBrowserProtocol()}//${getPrismaBrowserHost()}:4177`;
}

function buildPrismaRouteTruth(serverUrl?: string): PrismaRouteTruth {
  const protocol = getPrismaBrowserProtocol();
  const host = getPrismaBrowserHost();
  const realtimeUrl = serverUrl && serverUrl.trim() ? serverUrl.trim().replace(/\/$/, "") : getDefaultPrismaRealtimeUrl();

  return {
    protocol,
    host,
    realtimeUrl,
    realtimeHealthUrl: `${realtimeUrl}/health`,
    realtimeEventsUrl: `${realtimeUrl}/events`,
    realtimeStateUrl: `${realtimeUrl}/state`,
    tabletAppUrl: `${protocol}//${host}:3120/`,
    tabletPosUrl: `${protocol}//${host}:3120/pos`,
    visualOsProUrl: `${protocol}//${host}:3120/visual-os/pro`,
    pcUrl: `${protocol}//${host}:3130/`,
    mobileUrl: `${protocol}//${host}:3140/`,
    surfaceUrls: {
      tablet_pos: { label: "Tablet POS", targetUrl: `${protocol}//${host}:3120/pos`, shortPath: "/pos" },
      pc_backoffice: { label: "PC Backoffice", targetUrl: `${protocol}//${host}:3130/`, shortPath: ":3130/" },
      mobile_pulse: { label: "Mobile Pulse", targetUrl: `${protocol}//${host}:3140/`, shortPath: ":3140/" }
    }
  };
}

const STORAGE_KEY = "prisma.visual.studio.pro.00r00s.frame";
const CONTROL_KEY = "prisma.visual.live.controls";
const SNAPSHOT_KEY = "prisma.visual.studio.pro.00r00s.snapshots";
const RECIPE_KEY = "prisma.visual.studio.pro.00r00s.recipes";

const surfaceLabels: Record<PrismaVisualSurface, string> = {
  tablet_pos: "Tablet POS",
  pc_backoffice: "PC Backoffice",
  mobile_pulse: "Mobile Pulse"
};

const layerLabels: Record<LayerKey, string> = {
  background: "Background",
  atmosphere: "Atmosphere",
  shell: "Shell",
  surface: "Surface",
  content: "Content",
  action: "Action",
  state: "State",
  focus: "Focus",
  overlay: "Overlay"
};

const layerGuides: Record<LayerKey, LayerGuide> = {
  background: {
    name: "Background",
    plainName: "Fondo general",
    intent: "Ajusta el ambiente visual donde viven las pantallas: color base, profundidad, textura, brillo ambiental y movimiento de fondo.",
    modifies: ["fondo", "ambiente", "textura", "brillo general", "movimiento suave"],
    doesNotTouch: ["checkout", "ventas", "stock", "tickets", "base de datos"],
    affectedSelectors: ["html", "body", "fondos radiales", "variables --prisma-live-*"],
  },
  atmosphere: {
    name: "Atmosphere",
    plainName: "Atmósfera",
    intent: "Controla neblina, brillo y sensación premium alrededor de la interfaz sin cambiar datos ni acciones.",
    modifies: ["haze", "glow", "neon", "grain", "shine"],
    doesNotTouch: ["cobro", "inventario", "rutas API", "persistencia"],
    affectedSelectors: ["aurora", "gradientes", "overlays decorativos", "variables --prisma-live-*"],
  },
  shell: {
    name: "Shell",
    plainName: "Marco / navegación",
    intent: "Ajusta la carcasa visual: navegación, topbar, sidebar, marco de la app y separación general.",
    modifies: ["marco", "nav", "topbar", "sidebar", "bordes de estructura"],
    doesNotTouch: ["acciones de venta", "sincronización", "licencias", "reportes"],
    affectedSelectors: ["shell", "topbar", "sidebar", "navigation", "layout chrome"],
  },
  surface: {
    name: "Surface",
    plainName: "Superficies / tarjetas",
    intent: "Ajusta tarjetas, paneles y superficies de lectura: transparencia, blur, sombra, radio y peso visual.",
    modifies: ["cards", "paneles", "bordes", "sombra", "radio"],
    doesNotTouch: ["cálculos", "totales", "checkout", "eventos POS"],
    affectedSelectors: ["cards", "panels", "sections", "metric cards"],
  },
  content: {
    name: "Content",
    plainName: "Contenido",
    intent: "Ajusta lectura de textos, números, densidad y jerarquía visual de contenido.",
    modifies: ["lectura", "contraste", "densidad", "jerarquía", "aire entre bloques"],
    doesNotTouch: ["origen de datos", "KPIs", "precios", "reportes"],
    affectedSelectors: ["headings", "labels", "metric values", "copy blocks"],
  },
  action: {
    name: "Action",
    plainName: "Botones / acciones",
    intent: "Ajusta cómo se ven los botones y llamadas a la acción sin tocar lo que ejecutan.",
    modifies: ["botones", "CTA", "hover", "brillo de acción", "forma"],
    doesNotTouch: ["completeSale", "payment", "cartTotal", "handlers", "API"],
    affectedSelectors: ["buttons", "CTA", "publish gate", "checkout visual emphasis"],
  },
  state: {
    name: "State",
    plainName: "Estados / alertas",
    intent: "Ajusta cómo se distinguen READY, WARN, BLOCKED, vacío, alerta y foco operativo.",
    modifies: ["badges", "alertas", "scores", "estados", "mensajes"],
    doesNotTouch: ["reglas de negocio", "validadores", "gates", "score logic"],
    affectedSelectors: ["scoreBadge", "guardrails", "status chips", "empty states"],
  },
  focus: {
    name: "Focus",
    plainName: "Foco / selección",
    intent: "Ajusta la claridad de lo seleccionado: enfoque, borde activo, glow y lectura de foco.",
    modifies: ["focus rings", "selección", "borde activo", "énfasis"],
    doesNotTouch: ["navegación real", "forms submit", "atajos", "estado persistente"],
    affectedSelectors: ["focus-visible", "active controls", "selected layer"],
  },
  overlay: {
    name: "Overlay",
    plainName: "Overlays / modales",
    intent: "Ajusta capas flotantes, modales, pop-outs y paneles de edición.",
    modifies: ["overlays", "modales", "panel Studio", "backdrop", "pop-out"],
    doesNotTouch: ["pantallas productivas", "checkout", "DB", "rutas API"],
    affectedSelectors: ["studioFrame", "modal panels", "detached pro", "floating pro"],
  },
};

const layerControlCopy: Record<LayerKey, Partial<Record<ControlKey, ControlCopy>>> = {
  background: {
    glass: { label: "Neblina del fondo", help: "Qué tan cristalino o sólido se siente el ambiente base.", relevance: "primary" },
    blur: { label: "Suavidad del fondo", help: "Desenfoque visual detrás de la interfaz.", relevance: "primary" },
    glow: { label: "Brillo ambiental", help: "Luz general alrededor de la escena.", relevance: "primary" },
    motion: { label: "Movimiento de fondo", help: "Vida visual sin marear al operador.", relevance: "primary" },
    grain: { label: "Textura del fondo", help: "Ruido fino para evitar plástico plano.", relevance: "secondary" },
    contrast: { label: "Lectura de escena", help: "Separación del fondo contra contenido real.", relevance: "secondary" },
    edge: { label: "Definición de ambiente", help: "Filo sutil entre fondo y paneles.", relevance: "secondary" },
  },
  atmosphere: {
    glow: { label: "Aura premium", help: "Intensidad del halo PRISMA.", relevance: "primary" },
    neon: { label: "Energía neón", help: "Electricidad visual en acentos vivos.", relevance: "primary" },
    shine: { label: "Brillo especular", help: "Reflejo tipo cristal pulido.", relevance: "primary" },
    saturation: { label: "Energía cromática", help: "Cuánto color se siente en la atmósfera.", relevance: "secondary" },
    grain: { label: "Polvo visual fino", help: "Textura, no mugre digital.", relevance: "secondary" },
  },
  shell: {
    density: { label: "Compacidad del marco", help: "Espacio del shell sin apretar dedos.", relevance: "primary" },
    radius: { label: "Corte del marco", help: "Redondeo de navegación y contenedores.", relevance: "primary" },
    shadow: { label: "Peso del marco", help: "Qué tan separada se siente la carcasa.", relevance: "primary" },
    edge: { label: "Borde del shell", help: "Definición de sidebar/topbar.", relevance: "primary" },
    contrast: { label: "Lectura de navegación", help: "Claridad de labels y menús.", relevance: "secondary" },
  },
  surface: {
    glass: { label: "Transparencia de tarjeta", help: "Cristal de paneles y cards.", relevance: "primary" },
    blur: { label: "Blur de tarjeta", help: "Fondo filtrado por paneles.", relevance: "primary" },
    radius: { label: "Esquinas de tarjeta", help: "Forma de cards y paneles.", relevance: "primary" },
    shadow: { label: "Sombra de tarjeta", help: "Profundidad de paneles.", relevance: "primary" },
    glow: { label: "Brillo de borde", help: "Halo de contenedores premium.", relevance: "secondary" },
    density: { label: "Aire entre tarjetas", help: "Compacto contra respirable.", relevance: "secondary" },
  },
  content: {
    contrast: { label: "Lectura de contenido", help: "Claridad de texto, total y métricas.", relevance: "primary" },
    density: { label: "Aire de contenido", help: "Espaciado entre líneas, chips y bloques.", relevance: "primary" },
    saturation: { label: "Color de contenido", help: "Fuerza cromática sin matar lectura.", relevance: "secondary" },
    glow: { label: "Énfasis de lectura", help: "Brillo suave en valores clave.", relevance: "secondary" },
  },
  action: {
    glow: { label: "Brillo CTA", help: "Qué tanto grita el botón importante.", relevance: "primary" },
    neon: { label: "Energía de acción", help: "Acento activo en botones.", relevance: "primary" },
    radius: { label: "Forma del botón", help: "Redondeo de acciones.", relevance: "primary" },
    motion: { label: "Movimiento de botón", help: "Hover/click visual sin circo.", relevance: "primary" },
    contrast: { label: "Lectura del CTA", help: "Que el botón se entienda rápido.", relevance: "primary" },
    edge: { label: "Borde de acción", help: "Filo del botón activo.", relevance: "secondary" },
  },
  state: {
    contrast: { label: "Claridad de estado", help: "READY/WARN/BLOCKED legibles.", relevance: "primary" },
    glow: { label: "Alerta visual", help: "Énfasis de badges y guardrails.", relevance: "primary" },
    edge: { label: "Borde de alerta", help: "Separación de mensajes de estado.", relevance: "primary" },
    saturation: { label: "Color de semáforo", help: "Fuerza de alertas sin teatro barato.", relevance: "secondary" },
    motion: { label: "Pulso de estado", help: "Movimiento mínimo en señales.", relevance: "secondary" },
  },
  focus: {
    edge: { label: "Anillo de foco", help: "Borde de elemento activo.", relevance: "primary" },
    glow: { label: "Halo de selección", help: "Resalta lo seleccionado.", relevance: "primary" },
    contrast: { label: "Foco legible", help: "Que la selección no se pierda.", relevance: "primary" },
    motion: { label: "Respuesta de foco", help: "Micro-movimiento de selección.", relevance: "secondary" },
  },
  overlay: {
    glass: { label: "Cristal de overlay", help: "Transparencia del panel flotante.", relevance: "primary" },
    blur: { label: "Backdrop de overlay", help: "Desenfoque detrás del panel.", relevance: "primary" },
    shadow: { label: "Peso del overlay", help: "Separación del panel sobre la app.", relevance: "primary" },
    radius: { label: "Forma del overlay", help: "Esquinas del panel flotante.", relevance: "primary" },
    shine: { label: "Reflejo de overlay", help: "Brillo del vidrio superior.", relevance: "secondary" },
  },
};

function getControlCopy(layer: LayerKey, key: ControlKey, fallbackLabel: string, fallbackHelp: string): ControlCopy {
  return layerControlCopy[layer][key] ?? { label: fallbackLabel, help: fallbackHelp, relevance: "ghost" };
}

function affectedVarsFor(layer: LayerKey, controls: Controls) {
  const vars = cssVarsFromControls(controls, layer);
  return Object.entries(vars).map(([name, value]) => ({ name, value }));
}

const presets: Record<string, Controls> = {
  "Crystal POS Angel": { glass: 86, blur: 28, glow: 70, neon: 48, depth: 84, contrast: 88, density: 56, motion: 26, radius: 82, shadow: 76, saturation: 62, shine: 78, grain: 18, edge: 84 },
  "Black Premium Blade": { glass: 78, blur: 22, glow: 82, neon: 66, depth: 90, contrast: 92, density: 54, motion: 32, radius: 70, shadow: 88, saturation: 70, shine: 72, grain: 24, edge: 92 },
  "Light Operational Glass": { glass: 48, blur: 10, glow: 30, neon: 18, depth: 50, contrast: 94, density: 64, motion: 20, radius: 58, shadow: 42, saturation: 38, shine: 38, grain: 8, edge: 54 },
  "Mobile Pulse Jewel": { glass: 72, blur: 20, glow: 62, neon: 50, depth: 68, contrast: 84, density: 72, motion: 28, radius: 86, shadow: 58, saturation: 66, shine: 64, grain: 12, edge: 66 }
};

const initialControls: Controls = presets["Crystal POS Angel"];
const initialFloatingState: FloatingState = { x: 22, y: 18, width: 610, height: 850, dock: "right", minimized: false, surface: "tablet_pos", layer: "action" };

const controlLabels: Array<[ControlKey, string, string]> = [
  ["glass", "Glass", "Transparencia de cristal operativo"],
  ["blur", "Blur", "Desenfoque de planos y overlays"],
  ["glow", "Glow", "Luz ambiental y énfasis premium"],
  ["neon", "Neón", "Electricidad PRISMA en acciones"],
  ["depth", "Profundidad", "Separación entre capas"],
  ["contrast", "Contraste", "Lectura de precio, total y estado"],
  ["density", "Densidad", "Aire útil contra compactación"],
  ["motion", "Motion", "Movimiento vivo sin marear"],
  ["radius", "Radius", "Corte del vidrio y tarjetas"],
  ["shadow", "Sombra", "Peso visual y jerarquía"],
  ["saturation", "Saturación", "Energía cromática"],
  ["shine", "Shine", "Brillo especular de cristal"],
  ["grain", "Grain", "Textura fina anti-plástico barato"],
  ["edge", "Edge", "Borde pulido y filo visual"]
];

function clamp(value: number, min = 0, max = 100) { return Math.min(max, Math.max(min, Number.isFinite(value) ? value : min)); }
function clampPx(value: number, min: number, max: number) { return Math.min(max, Math.max(min, Number.isFinite(value) ? value : min)); }
function uid(prefix: string) { return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`; }

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try { const raw = window.localStorage.getItem(key); return raw ? { ...fallback, ...JSON.parse(raw) } : fallback; } catch { return fallback; }
}
function readArray<T>(key: string): T[] {
  if (typeof window === "undefined") return [];
  try { const raw = window.localStorage.getItem(key); return raw ? JSON.parse(raw) : []; } catch { return []; }
}
function saveArray<T>(key: string, value: T[]) { try { window.localStorage.setItem(key, JSON.stringify(value)); } catch {} }

function computeScore(controls: Controls, surface: PrismaVisualSurface): StudioScore {
  const readability = Math.round((controls.contrast * 0.65) + ((100 - Math.max(0, controls.blur - 38)) * 0.2) + ((100 - Math.max(0, controls.neon - 58)) * 0.15));
  const operationBase = surface === "tablet_pos" ? 78 : surface === "pc_backoffice" ? 72 : 74;
  const operation = Math.round(operationBase + (controls.density > 30 && controls.density < 78 ? 10 : -8) + (controls.motion < 58 ? 8 : -10));
  const premium = Math.round((controls.glass + controls.depth + controls.shadow + controls.shine + controls.edge) / 5);
  const motion = Math.round(100 - Math.max(0, controls.motion - 34) * 1.15);
  const safety = Math.round((readability * 0.55) + (operation * 0.35) + (motion * 0.1));
  const overall = Math.max(0, Math.min(100, Math.round((readability * 0.28) + (operation * 0.25) + (premium * 0.26) + (motion * 0.1) + (safety * 0.11))));
  const verdict = readability < 58 || operation < 55 || safety < 58 ? "BLOCKED" : overall < 78 ? "WARN" : "READY";
  return { overall, readability, operation, premium, motion, safety, verdict };
}

function guardrailMessages(controls: Controls, surface: PrismaVisualSurface) {
  const messages: Array<{ level: "ok" | "warn" | "block"; text: string }> = [];
  if (controls.blur > 72 && controls.contrast < 66) messages.push({ level: "block", text: "Blur alto con contraste medio/bajo: el total se vuelve fantasma caro." });
  if (surface === "tablet_pos" && controls.density < 34) messages.push({ level: "block", text: "Tablet POS no acepta densidad de duende: los dedos reales necesitan espacio." });
  if (surface === "tablet_pos" && controls.motion > 64) messages.push({ level: "warn", text: "Motion alto en caja: bonito, pero el cajero no vino a ver fuegos artificiales." });
  if (controls.neon > 78 && controls.glow > 72) messages.push({ level: "warn", text: "Neón + glow altos: lujo o feria, depende del contraste. Vigílalo." });
  if (controls.grain > 55) messages.push({ level: "warn", text: "Grain alto puede ensuciar superficies limpias." });
  if (!messages.length) messages.push({ level: "ok", text: "Sin bloqueos. Cristal pulido, no pecera embrujada." });
  return messages;
}

function cssVarsFromControls(controls: Controls, layer: LayerKey) {
  const blurPx = Math.round(controls.blur * 0.36);
  const alpha = Math.max(0.38, Math.min(0.92, 0.42 + controls.glass / 170));
  const glowAlpha = Math.min(0.78, controls.glow / 135);
  const neonAlpha = Math.min(0.74, controls.neon / 140);
  const radiusPx = Math.round(10 + controls.radius * 0.24);
  return {
    "--prisma-live-blur": `${blurPx}px`,
    "--prisma-live-panel-alpha": alpha.toFixed(2),
    "--prisma-live-glow": `0 0 ${Math.round(14 + controls.glow * 0.52)}px rgba(85, 225, 255, ${glowAlpha.toFixed(2)})`,
    "--prisma-live-neon": `0 0 ${Math.round(10 + controls.neon * 0.42)}px rgba(134, 92, 255, ${neonAlpha.toFixed(2)})`,
    "--prisma-live-shadow": `0 ${Math.round(14 + controls.shadow * 0.32)}px ${Math.round(28 + controls.depth * 0.72)}px rgba(0, 0, 0, ${(0.14 + controls.shadow / 210).toFixed(2)})`,
    "--prisma-live-radius": `${radiusPx}px`,
    "--prisma-live-saturation": `${Math.round(82 + controls.saturation * 0.65)}%`,
    "--prisma-live-shine": `${(controls.shine / 100).toFixed(2)}`,
    "--prisma-live-grain": `${(controls.grain / 100).toFixed(2)}`,
    "--prisma-live-edge": `rgba(210, 245, 255, ${(0.16 + controls.edge / 170).toFixed(2)})`,
    "--prisma-live-layer": layer
  };
}

function applyExtraVars(controls: Controls, layer: LayerKey) {
  const root = document.documentElement;
  const vars = cssVarsFromControls(controls, layer);
  Object.entries(vars).forEach(([key, value]) => root.style.setProperty(key, String(value)));
  root.dataset.prismaStudioPro = "00R_00S";
  root.dataset.prismaStudioLayer = layer;
}

export default function PrismaStudioProQaClient({ defaultDetached = false }: { defaultDetached?: boolean }) {
  const [controls, setControls] = useState<Controls>(initialControls);
  const [floating, setFloating] = useState<FloatingState>(() => ({ ...initialFloatingState, dock: defaultDetached ? "free" : "right", width: defaultDetached ? 980 : 610, height: defaultDetached ? 900 : 850 }));
  const [presetName, setPresetName] = useState("Crystal POS Angel");
  const [recipeName, setRecipeName] = useState("CRYSTAL_POS_ANGEL_LIVE_v01");
  const [liveEnabled, setLiveEnabled] = useState(true);
  const [debugLayers, setDebugLayers] = useState(false);
  const [workbenchMode, setWorkbenchMode] = useState<WorkbenchMode>("simple");
  const [realtimeEnabled, setRealtimeEnabled] = useState(true);
  const [followRemote, setFollowRemote] = useState(true);
  const [serverUrl, setServerUrl] = useState(() => getDefaultPrismaRealtimeUrl());
  const [status, setStatus] = useState<PrismaRealtimeStatus>("idle");
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [recipes, setRecipes] = useState<Snapshot[]>([]);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<string>("");
  const [lastRemote, setLastRemote] = useState<PrismaVisualRealtimePayload | null>(null);
  const [copied, setCopied] = useState("");
  const dragRef = useRef<DragState | null>(null);
  const clientId = useMemo(() => createPrismaRealtimeClientId(defaultDetached ? "studio-pro-detached" : "studio-pro-floating"), [defaultDetached]);
  const broadcastTimer = useRef<number | null>(null);
  const routeTruth = useMemo(() => buildPrismaRouteTruth(serverUrl), [serverUrl]);

  useEffect(() => {
    setFloating((current) => readJson(STORAGE_KEY, current));
    setSnapshots(readArray<Snapshot>(SNAPSHOT_KEY));
    setRecipes(readArray<Snapshot>(RECIPE_KEY));
    try {
      const raw = window.localStorage.getItem(CONTROL_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.controls) setControls((current) => ({ ...current, ...parsed.controls }));
      if (parsed?.surface) setFloating((current) => ({ ...current, surface: parsed.surface }));
      if (parsed?.recipeName) setRecipeName(parsed.recipeName);
    } catch {}
  }, []);

  const score = useMemo(() => computeScore(controls, floating.surface), [controls, floating.surface]);
  const guardrails = useMemo(() => guardrailMessages(controls, floating.surface), [controls, floating.surface]);
  const blocked = score.verdict === "BLOCKED" || guardrails.some((message) => message.level === "block");
  const selectedSnapshot = snapshots.find((snapshot) => snapshot.id === selectedSnapshotId) ?? snapshots[0] ?? null;
  const payload = useMemo(() => ({
    ...buildPrismaRealtimePayload({
      sourceClientId: clientId,
      surface: floating.surface,
      recipeName,
      controls,
      liveEnabled,
      debugLayers,
      mode: defaultDetached ? "detached-pro" : "floating-pro"
    }),
    layer: floating.layer,
    score,
    studio: "00R_00S",
    editorMode: workbenchMode
  }), [clientId, controls, debugLayers, defaultDetached, floating.layer, floating.surface, liveEnabled, recipeName, score, workbenchMode]);
  const layerGuide = layerGuides[floating.layer];
  const affectedCssVars = useMemo(() => affectedVarsFor(floating.layer, controls), [controls, floating.layer]);
  const primaryControls = useMemo(() => controlLabels.filter(([key]) => getControlCopy(floating.layer, key, "", "").relevance === "primary").map(([key]) => key), [floating.layer]);
  const exportJson = useMemo(() => JSON.stringify(payload, null, 2), [payload]);

  useEffect(() => {
    if (!realtimeEnabled) { setStatus("local"); return; }
    const disconnect = connectPrismaRealtime({
      serverUrl,
      clientId,
      onStatus: setStatus,
      onPayload: (incoming) => {
        setLastRemote(incoming);
        if (!followRemote || incoming.sourceClientId === clientId) return;
        if (incoming.controls) setControls((current) => ({ ...current, ...incoming.controls } as Controls));
        if (incoming.surface) setFloating((current) => ({ ...current, surface: incoming.surface }));
        if (incoming.recipeName) setRecipeName(incoming.recipeName);
        applyPrismaRealtimePayload(incoming);
      }
    });
    return disconnect;
  }, [clientId, followRemote, realtimeEnabled, serverUrl]);

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.prismaLive = liveEnabled ? "on" : "off";
    root.dataset.prismaLiveDebug = debugLayers ? "on" : "off";
    root.dataset.prismaStudioMode = defaultDetached ? "detached-pro" : "floating-pro";
    root.dataset.prismaVisualSurface = floating.surface;
    root.dataset.prismaVosFocusedLayer = floating.layer;
    root.dataset.prismaVosEditorMode = workbenchMode;
    root.dataset.prismaVosLayerFocusPackage = "PRISMA_VISUAL_OS_PRO_LAYER_FOCUS_00ZK";
    root.dataset.prismaVisualLiveStatusTruth = "PRISMA_VISUAL_OS_LIVE_STATUS_TRUTH_00ZL";
    if (liveEnabled && !blocked) {
      applyPrismaRealtimePayload(payload);
      applyExtraVars(controls, floating.layer);
    }
    try {
      window.localStorage.setItem(CONTROL_KEY, exportJson);
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(floating));
    } catch {}
    if (realtimeEnabled && liveEnabled && !blocked) {
      if (broadcastTimer.current) window.clearTimeout(broadcastTimer.current);
      broadcastTimer.current = window.setTimeout(() => {
        broadcastPrismaRealtimePayload(serverUrl, payload).catch(() => setStatus("local"));
      }, 80);
    }
    return () => { if (broadcastTimer.current) window.clearTimeout(broadcastTimer.current); };
  }, [blocked, controls, debugLayers, defaultDetached, exportJson, floating, liveEnabled, payload, realtimeEnabled, serverUrl, workbenchMode]);

  useEffect(() => {
    function onMove(event: PointerEvent) {
      const drag = dragRef.current;
      if (!drag) return;
      if (drag.type === "move") {
        setFloating((current) => ({ ...current, dock: "free", x: clampPx(drag.originX + event.clientX - drag.startX, 6, Math.max(6, window.innerWidth - current.width - 6)), y: clampPx(drag.originY + event.clientY - drag.startY, 6, Math.max(6, window.innerHeight - 72)) }));
      } else {
        setFloating((current) => ({ ...current, dock: "free", width: clampPx(drag.originWidth + event.clientX - drag.startX, 420, Math.min(1160, window.innerWidth - 20)), height: clampPx(drag.originHeight + event.clientY - drag.startY, 520, Math.min(980, window.innerHeight - 20)) }));
      }
    }
    function onUp() { dragRef.current = null; }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => { window.removeEventListener("pointermove", onMove); window.removeEventListener("pointerup", onUp); };
  }, []);

  function setControl(key: ControlKey, value: number) { setControls((current) => ({ ...current, [key]: clamp(value) })); }
  function applyPreset(name: string) { setPresetName(name); setControls(presets[name]); setRecipeName(name.toUpperCase().replace(/[^A-Z0-9]+/g, "_") + "_v01"); }
  function beginMove(event: ReactPointerEvent<HTMLElement>) { if (defaultDetached) return; event.currentTarget.setPointerCapture?.(event.pointerId); dragRef.current = { type: "move", startX: event.clientX, startY: event.clientY, originX: floating.x, originY: floating.y }; }
  function beginResize(event: ReactPointerEvent<HTMLButtonElement>) { if (defaultDetached) return; event.preventDefault(); event.currentTarget.setPointerCapture?.(event.pointerId); dragRef.current = { type: "resize", startX: event.clientX, startY: event.clientY, originWidth: floating.width, originHeight: floating.height }; }
  function openDetached() { window.open("/visual-os/detached", "prisma-studio-pro", "width=1040,height=940,menubar=no,toolbar=no,location=no,status=no"); }
  function reset() { setControls(initialControls); setFloating({ ...initialFloatingState, dock: defaultDetached ? "free" : "right", width: defaultDetached ? 980 : 610, height: defaultDetached ? 900 : 850 }); setPresetName("Crystal POS Angel"); setRecipeName("CRYSTAL_POS_ANGEL_LIVE_v01"); setDebugLayers(false); setLiveEnabled(true); setRealtimeEnabled(true); setFollowRemote(true); setCopied(""); }
  async function copyJson(label = "JSON copiado") { await navigator.clipboard?.writeText(exportJson); setCopied(label); window.setTimeout(() => setCopied(""), 1600); }
  function makeSnapshot(type: "snapshot" | "recipe") {
    const item: Snapshot = { id: uid(type), name: `${type === "recipe" ? recipeName : "Snapshot"} · ${new Date().toLocaleTimeString()}`, createdAt: new Date().toISOString(), surface: floating.surface, recipeName, controls, score };
    if (type === "recipe") { const next = [item, ...recipes].slice(0, 12); setRecipes(next); saveArray(RECIPE_KEY, next); }
    else { const next = [item, ...snapshots].slice(0, 10); setSnapshots(next); setSelectedSnapshotId(item.id); saveArray(SNAPSHOT_KEY, next); }
  }
  function loadSnapshot(item: Snapshot) { setControls(item.controls); setRecipeName(item.recipeName); setFloating((current) => ({ ...current, surface: item.surface })); }
  function publishActive() {
    if (blocked) { setCopied("Bloqueado por QA"); return; }
    try { window.localStorage.setItem("prisma.visual.published.active.00r00s", exportJson); setCopied("Publicado local"); } catch { setCopied("No se pudo publicar"); }
    window.setTimeout(() => setCopied(""), 1600);
  }

  const frameStyle: CSSProperties = defaultDetached
    ? { width: "min(1120px, calc(100vw - 24px))", minHeight: "calc(100vh - 24px)" }
    : floating.dock === "right" ? { right: 18, top: 18, width: floating.width, height: "calc(100vh - 36px)" }
    : floating.dock === "left" ? { left: 18, top: 18, width: floating.width, height: "calc(100vh - 36px)" }
    : floating.dock === "bottom" ? { left: 18, right: 18, bottom: 18, width: "auto", height: Math.min(floating.height, 620) }
    : { left: floating.x, top: floating.y, width: floating.width, height: floating.height };

  return (
    <section className={`${styles.studioFrame} ${floating.minimized ? styles.isMinimized : ""} ${defaultDetached ? styles.isDetached : ""}`} style={frameStyle} data-prisma-layer="overlay" data-prisma-studio-pro="00R_00S">
      <div className={styles.aurora} aria-hidden="true" />
      <header className={styles.topbar} onPointerDown={beginMove} data-prisma-layer="shell">
        <div>
          <p>00R/00S · Studio Pro + QA</p>
          <strong>{surfaceLabels[floating.surface]} · {layerLabels[floating.layer]}</strong>
        </div>
        <div className={styles.scoreBadge} data-verdict={score.verdict}><span>{score.verdict}</span><b>{score.overall}</b></div>
        <div className={styles.windowActions}>
          {!defaultDetached && <button type="button" onClick={() => setFloating((current) => ({ ...current, minimized: !current.minimized }))}>{floating.minimized ? "Abrir" : "Min"}</button>}
          {!defaultDetached && <button type="button" onClick={openDetached}>Pop-out</button>}
          <button type="button" onClick={reset}>Reset</button>
        </div>
      </header>
      {!floating.minimized && (
        <div className={styles.body}>
          <section className={styles.commandDeck} data-prisma-layer="surface">
            <article className={styles.connectionPanel} data-status={status}>
              <span>Realtime</span><strong>{status === "error" ? "error: revisa 4177" : status}</strong><input value={serverUrl} onChange={(event) => setServerUrl(event.target.value)} />
              <a href="/visual-os/realtime" target="_blank" rel="noreferrer">Bridge</a>
              <div className={styles.routeTruthPanel} data-prisma-vos-route-truth={ROUTE_TRUTH_PACKAGE_MARKER}>
                <small>Host activo: <b>{routeTruth.host}</b></small>
                <small>Tablet app: <code>/</code></small>
                <small>Tablet POS real: <code>{routeTruth.surfaceUrls.tablet_pos.shortPath}</code></small>
                <small>Studio Pro: <code>/visual-os/pro</code></small>
                <small>Realtime health: <code>{routeTruth.realtimeHealthUrl}</code></small>
              </div>
            </article>
            <article className={styles.publishPanel} data-verdict={score.verdict}>
              <span>Publish Gate</span><strong>{blocked ? "Bloqueado" : "Listo"}</strong><button type="button" onClick={publishActive}>Publicar active</button>{copied && <small>{copied}</small>}
            </article>
          </section>

          <section className={styles.toolbar} aria-label="Modo de consola">
            <label>Superficie<select value={floating.surface} onChange={(event) => setFloating((current) => ({ ...current, surface: event.target.value as PrismaVisualSurface }))}><option value="tablet_pos">Tablet POS</option><option value="pc_backoffice">PC Backoffice</option><option value="mobile_pulse">Mobile Pulse</option></select></label>
            <label>Capa<select value={floating.layer} onChange={(event) => setFloating((current) => ({ ...current, layer: event.target.value as LayerKey }))}>{Object.entries(layerLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
            <label>Modo anti-pendejos<select value={workbenchMode} onChange={(event) => setWorkbenchMode(event.target.value as WorkbenchMode)}><option value="simple">Simple: solo lo importante</option><option value="advanced">Avanzado: todo con contexto</option><option value="expert">Experto: JSON + tokens</option></select></label>
            <label className={styles.recipeField}>Receta<input value={recipeName} onChange={(event) => setRecipeName(event.target.value)} /></label>
          </section>

          <section className={styles.surfaceStatus} aria-label="Estado de superficies Visual OS">
            {(Object.entries(surfaceLabels) as Array<[PrismaVisualSurface, string]>).map(([surface, label]) => {
              const selected = floating.surface === surface;
              const remoteMatch = lastRemote?.surface === surface;
              const liveOk = status !== "error" && (remoteMatch || selected);
              const liveLabel = status === "error" ? "realtime sin conexión" : selected ? status : remoteMatch ? "recibió payload" : "no confirmado";
              return <button key={surface} type="button" data-active={selected} data-live={liveOk} data-realtime-status={status} onClick={() => setFloating((current) => ({ ...current, surface }))}><b>{label}</b><span>{liveLabel}</span></button>;
            })}
          </section>

          <section className={styles.scopeBanner} data-prisma-layer="focus" aria-live="polite">
            <div><span>Editando ahora</span><strong>{surfaceLabels[floating.surface]} → {layerGuide.plainName}</strong><p>{layerGuide.intent}</p></div>
            <div><span>Sí modifica</span><p>{layerGuide.modifies.join(" · ")}</p></div>
            <div><span>No toca</span><p>{layerGuide.doesNotTouch.join(" · ")}</p></div>
          </section>

          {!defaultDetached && <nav className={styles.dockbar} aria-label="Posición de consola">{(["free", "left", "right", "bottom"] as DockMode[]).map((mode) => <button key={mode} type="button" data-active={floating.dock === mode} onClick={() => setFloating((current) => ({ ...current, dock: mode }))}>{mode}</button>)}</nav>}

          <section className={styles.liveSwitches} data-prisma-layer="action">
            <button type="button" data-active={liveEnabled} onClick={() => setLiveEnabled((value) => !value)}>{liveEnabled ? "Live activo" : "Live pausado"}</button>
            <button type="button" data-active={realtimeEnabled} onClick={() => setRealtimeEnabled((value) => !value)}>{realtimeEnabled ? "Realtime on" : "Solo local"}</button>
            <button type="button" data-active={followRemote} onClick={() => setFollowRemote((value) => !value)}>{followRemote ? "Sigue remoto" : "Ignora remoto"}</button>
            <button type="button" data-active={debugLayers} onClick={() => setDebugLayers((value) => !value)}>{debugLayers ? "Debug on" : "Debug layers"}</button>
            <button type="button" onClick={() => copyJson()}>Copiar JSON</button>
          </section>

          <section className={styles.presetMixer} data-prisma-layer="surface">
            {Object.keys(presets).map((name) => <button key={name} type="button" data-active={presetName === name} onClick={() => applyPreset(name)}><b>{name}</b><span>{name.includes("Crystal") ? "vidrio angelical" : name.includes("Black") ? "navaja premium" : name.includes("Light") ? "operativo claro" : "pulso móvil"}</span></button>)}
          </section>

          <section className={styles.scoreGrid} data-prisma-layer="state">
            {(["readability", "operation", "premium", "motion", "safety"] as const).map((key) => <article key={key}><span>{key}</span><b>{score[key]}</b><meter min="0" max="100" value={score[key]} /></article>)}
          </section>

          <section className={styles.controlsHeader} aria-label="Resumen de perillas por capa">
            <div><span>Perillas principales</span><strong>{primaryControls.length ? primaryControls.join(" · ") : "ninguna"}</strong></div>
            <p>Las perillas fantasma siguen visibles en modo avanzado para contexto, pero en simple no estorban. La capa activa manda, no el buffet de controles.</p>
          </section>

          <section className={styles.controls} aria-label={`Perillas visuales para ${layerGuide.plainName}`}>
            {controlLabels.map(([key, label, help]) => {
              const copy = getControlCopy(floating.layer, key, label, help);
              const hiddenInSimple = workbenchMode === "simple" && copy.relevance === "ghost";
              return <label key={key} className={`${styles.control} ${hiddenInSimple ? styles.controlHiddenSimple : ""}`} data-hot={controls[key] > 72} data-relevance={copy.relevance}><span><b>{copy.label}</b><small>{copy.help}</small><em>{copy.relevance === "primary" ? "Principal de capa" : copy.relevance === "secondary" ? "Apoyo" : "Fantasma / indirecta"}</em></span><input type="range" min="0" max="100" value={controls[key]} disabled={hiddenInSimple} onChange={(event) => setControl(key, Number(event.target.value))} /><output>{controls[key]}</output></label>;
            })}
          </section>

          <section className={styles.previewLab} data-prisma-layer="surface">
            <article className={styles.layerFocusMap} aria-label="Mapa de capas con foco anti-pendejos">
              {(Object.entries(layerGuides) as Array<[LayerKey, LayerGuide]>).map(([key, guide]) => <button key={key} type="button" data-active={floating.layer === key} data-ghost={floating.layer !== key} onClick={() => setFloating((current) => ({ ...current, layer: key }))}><span>{guide.plainName}</span><small>{floating.layer === key ? "sólida / editando" : "fantasma"}</small></button>)}
            </article>
            <article className={styles.previewCard}><span>Preview cristal</span><strong>$146.00</strong><small>{lastRemote ? `Remoto: ${lastRemote.recipeName}` : "Local + broadcast cuando el servidor respira"}</small><button type="button">Cobrar</button></article>
            <article className={styles.layerInspector}><span>Layer inspector</span><b>{layerGuide.plainName}</b><p>{layerGuide.intent}</p><ul>{affectedCssVars.slice(0, workbenchMode === "expert" ? affectedCssVars.length : 6).map((item) => <li key={item.name}><code>{item.name}</code><span>{item.value}</span></li>)}</ul></article>
          </section>

          <section className={styles.snapshotLab} data-prisma-layer="content">
            <div className={styles.snapshotActions}><button type="button" onClick={() => makeSnapshot("snapshot")}>Crear snapshot</button><button type="button" onClick={() => makeSnapshot("recipe")}>Guardar receta</button></div>
            <div className={styles.snapshotList}>{snapshots.map((shot) => <button key={shot.id} type="button" data-active={selectedSnapshot?.id === shot.id} onClick={() => setSelectedSnapshotId(shot.id)}><b>{shot.name}</b><span>{shot.score.overall} · {shot.score.verdict}</span></button>)}</div>
            <div className={styles.compareBox}>{selectedSnapshot ? <><h3>Before / After</h3><p><b>Antes:</b> {selectedSnapshot.recipeName} · {selectedSnapshot.score.overall}</p><p><b>Ahora:</b> {recipeName} · {score.overall}</p><button type="button" onClick={() => loadSnapshot(selectedSnapshot)}>Cargar before</button></> : <p>Sin snapshot. Toma uno y deja evidencia, no puro “confía”.</p>}</div>
          </section>

          <section className={styles.guardrails} data-prisma-layer="state"><strong>Guardrails</strong>{guardrails.map((message) => <p key={message.text} data-level={message.level}>{message.text}</p>)}</section>
          {workbenchMode !== "simple" && <details className={styles.exportBox} open={workbenchMode === "expert"}><summary>Payload pro JSON</summary><pre suppressHydrationWarning>{exportJson}</pre></details>}
        </div>
      )}
      {!defaultDetached && !floating.minimized && <button type="button" className={styles.resizeHandle} onPointerDown={beginResize} aria-label="Redimensionar consola" />}
    </section>
  );
}

