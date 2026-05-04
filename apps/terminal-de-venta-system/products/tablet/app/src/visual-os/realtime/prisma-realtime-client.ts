export type PrismaVisualSurface = "tablet_pos" | "pc_backoffice" | "mobile_pulse";
export type PrismaRealtimeStatus = "idle" | "connecting" | "connected" | "error" | "local";

export type PrismaVisualRealtimePayload = {
  type: "prisma.visual.controls";
  sourceClientId: string;
  surface: PrismaVisualSurface;
  recipeName: string;
  controls: Record<string, number>;
  cssVars: Record<string, string>;
  liveEnabled: boolean;
  debugLayers: boolean;
  mode: string;
  layer?: string;
  studio?: string;
  score?: { overall: number; readability: number; operation: number; premium: number; motion: number; safety: number; verdict: string };
  createdAt: string;
};

export const PRISMA_REALTIME_DEFAULT_URL = "http://127.0.0.1:4177";

function clamp(value: number, min = 0, max = 100) { return Math.min(max, Math.max(min, Number.isFinite(value) ? value : min)); }

export function createPrismaRealtimeClientId(prefix = "client") {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return `prisma-${prefix}-${crypto.randomUUID()}`;
  return `prisma-${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export function controlsToCssVars(controls: Record<string, number>) {
  const glass = clamp(controls.glass ?? 70);
  const blur = clamp(controls.blur ?? 18);
  const glow = clamp(controls.glow ?? 64);
  const neon = clamp(controls.neon ?? 42);
  const depth = clamp(controls.depth ?? 70);
  const contrast = clamp(controls.contrast ?? 82);
  const density = clamp(controls.density ?? 55);
  const motion = clamp(controls.motion ?? 30);
  const radius = clamp(controls.radius ?? 72);
  const shadow = clamp(controls.shadow ?? 68);
  const saturation = clamp(controls.saturation ?? 58);
  const shine = clamp(controls.shine ?? 60);
  const grain = clamp(controls.grain ?? 14);
  const edge = clamp(controls.edge ?? 70);
  return {
    "--prisma-live-glass": `${glass}`,
    "--prisma-live-blur": `${Math.round(blur * 0.36)}px`,
    "--prisma-live-panel-alpha": `${Math.max(.38, Math.min(.94, .42 + glass / 170)).toFixed(2)}`,
    "--prisma-live-glow": `0 0 ${Math.round(14 + glow * .52)}px rgba(85,225,255,${Math.min(.78, glow / 135).toFixed(2)})`,
    "--prisma-live-neon": `0 0 ${Math.round(10 + neon * .42)}px rgba(134,92,255,${Math.min(.74, neon / 140).toFixed(2)})`,
    "--prisma-live-depth": `${depth}`,
    "--prisma-live-contrast": `${contrast}`,
    "--prisma-live-density": `${density}`,
    "--prisma-live-motion": `${motion}`,
    "--prisma-live-radius": `${Math.round(10 + radius * .24)}px`,
    "--prisma-live-shadow": `0 ${Math.round(14 + shadow * .32)}px ${Math.round(28 + depth * .72)}px rgba(0,0,0,${(.14 + shadow / 210).toFixed(2)})`,
    "--prisma-live-saturation": `${Math.round(82 + saturation * .65)}%`,
    "--prisma-live-shine": `${(shine / 100).toFixed(2)}`,
    "--prisma-live-grain": `${(grain / 100).toFixed(2)}`,
    "--prisma-live-edge": `rgba(210,245,255,${(.16 + edge / 170).toFixed(2)})`
  };
}

export function buildPrismaRealtimePayload(input: { sourceClientId: string; surface: PrismaVisualSurface; recipeName: string; controls: Record<string, number>; liveEnabled: boolean; debugLayers: boolean; mode: string; }): PrismaVisualRealtimePayload {
  return { type: "prisma.visual.controls", sourceClientId: input.sourceClientId, surface: input.surface, recipeName: input.recipeName, controls: input.controls, cssVars: controlsToCssVars(input.controls), liveEnabled: input.liveEnabled, debugLayers: input.debugLayers, mode: input.mode, createdAt: new Date().toISOString() };
}

export function applyPrismaRealtimePayload(payload: PrismaVisualRealtimePayload) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.prismaLive = payload.liveEnabled ? "on" : "off";
  root.dataset.prismaLiveDebug = payload.debugLayers ? "on" : "off";
  root.dataset.prismaVisualSurface = payload.surface;
  root.dataset.prismaRealtimeRecipe = payload.recipeName;
  if (payload.layer) root.dataset.prismaStudioLayer = payload.layer;
  Object.entries(payload.cssVars ?? {}).forEach(([key, value]) => root.style.setProperty(key, value));
}

export async function broadcastPrismaRealtimePayload(serverUrl: string, payload: PrismaVisualRealtimePayload) {
  const response = await fetch(`${serverUrl.replace(/\/$/, "")}/broadcast`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`Broadcast failed: ${response.status}`);
  return response.json();
}

export function connectPrismaRealtime(options: { serverUrl: string; clientId: string; onStatus: (status: PrismaRealtimeStatus) => void; onPayload: (payload: PrismaVisualRealtimePayload) => void; }) {
  if (typeof window === "undefined" || typeof EventSource === "undefined") { options.onStatus("local"); return () => {}; }
  const url = `${options.serverUrl.replace(/\/$/, "")}/events?clientId=${encodeURIComponent(options.clientId)}`;
  options.onStatus("connecting");
  const events = new EventSource(url);
  events.onopen = () => options.onStatus("connected");
  events.onerror = () => options.onStatus("error");
  events.addEventListener("prisma.visual.controls", (event) => {
    try { options.onPayload(JSON.parse((event as MessageEvent).data)); } catch {}
  });
  return () => events.close();
}
