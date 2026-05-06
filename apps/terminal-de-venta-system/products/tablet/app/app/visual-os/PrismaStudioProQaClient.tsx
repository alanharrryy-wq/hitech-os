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
type Snapshot = { id: string; name: string; createdAt: string; surface: PrismaVisualSurface; recipeName: string; controls: Controls; score: StudioScore };
type StudioScore = { overall: number; readability: number; operation: number; premium: number; motion: number; safety: number; verdict: "READY" | "WARN" | "BLOCKED" };

type FloatingState = { x: number; y: number; width: number; height: number; dock: DockMode; minimized: boolean; surface: PrismaVisualSurface; layer: LayerKey };
type DragState = { type: "move"; startX: number; startY: number; originX: number; originY: number } | { type: "resize"; startX: number; startY: number; originWidth: number; originHeight: number };

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
  const [realtimeEnabled, setRealtimeEnabled] = useState(true);
  const [followRemote, setFollowRemote] = useState(true);
  const [serverUrl, setServerUrl] = useState(PRISMA_REALTIME_DEFAULT_URL);
  const [status, setStatus] = useState<PrismaRealtimeStatus>("idle");
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [recipes, setRecipes] = useState<Snapshot[]>([]);
  const [selectedSnapshotId, setSelectedSnapshotId] = useState<string>("");
  const [lastRemote, setLastRemote] = useState<PrismaVisualRealtimePayload | null>(null);
  const [copied, setCopied] = useState("");
  const dragRef = useRef<DragState | null>(null);
  const clientId = useMemo(() => createPrismaRealtimeClientId(defaultDetached ? "studio-pro-detached" : "studio-pro-floating"), [defaultDetached]);
  const broadcastTimer = useRef<number | null>(null);

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
    studio: "00R_00S"
  }), [clientId, controls, debugLayers, defaultDetached, floating.layer, floating.surface, liveEnabled, recipeName, score]);
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
  }, [blocked, controls, debugLayers, defaultDetached, exportJson, floating, liveEnabled, payload, realtimeEnabled, serverUrl]);

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
              <span>Realtime</span><strong>{status}</strong><input value={serverUrl} onChange={(event) => setServerUrl(event.target.value)} />
              <a href="/visual-os/realtime" target="_blank" rel="noreferrer">Bridge</a>
            </article>
            <article className={styles.publishPanel} data-verdict={score.verdict}>
              <span>Publish Gate</span><strong>{blocked ? "Bloqueado" : "Listo"}</strong><button type="button" onClick={publishActive}>Publicar active</button>{copied && <small>{copied}</small>}
            </article>
          </section>

          <section className={styles.toolbar} aria-label="Modo de consola">
            <label>Superficie<select value={floating.surface} onChange={(event) => setFloating((current) => ({ ...current, surface: event.target.value as PrismaVisualSurface }))}><option value="tablet_pos">Tablet POS</option><option value="pc_backoffice">PC Backoffice</option><option value="mobile_pulse">Mobile Pulse</option></select></label>
            <label>Capa<select value={floating.layer} onChange={(event) => setFloating((current) => ({ ...current, layer: event.target.value as LayerKey }))}>{Object.entries(layerLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
            <label>Receta<input value={recipeName} onChange={(event) => setRecipeName(event.target.value)} /></label>
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

          <section className={styles.controls} aria-label="Perillas visuales">
            {controlLabels.map(([key, label, help]) => <label key={key} className={styles.control} data-hot={controls[key] > 72}><span><b>{label}</b><small>{help}</small></span><input type="range" min="0" max="100" value={controls[key]} onChange={(event) => setControl(key, Number(event.target.value))} /><output>{controls[key]}</output></label>)}
          </section>

          <section className={styles.previewLab} data-prisma-layer="surface">
            <article className={styles.previewCard}><span>Preview cristal</span><strong>$146.00</strong><small>{lastRemote ? `Remoto: ${lastRemote.recipeName}` : "Local + broadcast cuando el servidor respira"}</small><button type="button">Cobrar</button></article>
            <article className={styles.layerInspector}><span>Layer inspector</span><b>{layerLabels[floating.layer]}</b><p>Los cambios se aplican como variables CSS vivas y metadata de layer. No es magia; es ingeniería con maquillaje fino.</p></article>
          </section>

          <section className={styles.snapshotLab} data-prisma-layer="content">
            <div className={styles.snapshotActions}><button type="button" onClick={() => makeSnapshot("snapshot")}>Crear snapshot</button><button type="button" onClick={() => makeSnapshot("recipe")}>Guardar receta</button></div>
            <div className={styles.snapshotList}>{snapshots.map((shot) => <button key={shot.id} type="button" data-active={selectedSnapshot?.id === shot.id} onClick={() => setSelectedSnapshotId(shot.id)}><b>{shot.name}</b><span>{shot.score.overall} · {shot.score.verdict}</span></button>)}</div>
            <div className={styles.compareBox}>{selectedSnapshot ? <><h3>Before / After</h3><p><b>Antes:</b> {selectedSnapshot.recipeName} · {selectedSnapshot.score.overall}</p><p><b>Ahora:</b> {recipeName} · {score.overall}</p><button type="button" onClick={() => loadSnapshot(selectedSnapshot)}>Cargar before</button></> : <p>Sin snapshot. Toma uno y deja evidencia, no puro “confía”.</p>}</div>
          </section>

          <section className={styles.guardrails} data-prisma-layer="state"><strong>Guardrails</strong>{guardrails.map((message) => <p key={message.text} data-level={message.level}>{message.text}</p>)}</section>
          <details className={styles.exportBox}><summary>Payload pro JSON</summary><pre suppressHydrationWarning>{exportJson}</pre></details>
        </div>
      )}
      {!defaultDetached && !floating.minimized && <button type="button" className={styles.resizeHandle} onPointerDown={beginResize} aria-label="Redimensionar consola" />}
    </section>
  );
}

