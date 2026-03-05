"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SCENE_GROUPS, allScenesFlat, type SceneItem } from "./scene-registry";

type DockPos = { x: number; y: number };

const POS_KEY = "HITECH_SCENE_DOCK_POS_V1";
const OPEN_KEY = "HITECH_SCENE_DOCK_OPEN_V1";
const PIN_KEY = "HITECH_SCENE_DOCK_PIN_V1";
const PREFS_KEY = "HITECH_SCENE_DOCK_PREFS_V1";

type Prefs = {
  openInNewTab: boolean;
  keepQuery: boolean;
  layers: "keep" | "none" | "all";
  motion: "keep" | "off" | "on";
  layerProfile: "keep" | "neutral" | "fx";
  debug: "keep" | "0" | "1";
};

const DEFAULT_PREFS: Prefs = {
  openInNewTab: false,
  keepQuery: true,
  layers: "keep",
  motion: "keep",
  layerProfile: "keep",
  debug: "keep",
};

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function safeJsonParse<T>(raw: string | null, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function buildQuery(
  current: URLSearchParams,
  prefs: Prefs,
): string {
  const q = new URLSearchParams(prefs.keepQuery ? current.toString() : "");

  if (prefs.layers !== "keep") q.set("layers", prefs.layers);
  if (prefs.motion !== "keep") q.set("motion", prefs.motion);
  if (prefs.layerProfile !== "keep") q.set("layerProfile", prefs.layerProfile);
  if (prefs.debug !== "keep") q.set("debug", prefs.debug);

  const s = q.toString();
  return s ? `?${s}` : "";
}

function isTouchLike() {
  if (typeof window === "undefined") return false;
  return (
    "ontouchstart" in window ||
    (navigator.maxTouchPoints ?? 0) > 0
  );
}

export function FloatingSceneDock() {
  const router = useRouter();
  const pathname = usePathname() || "";
  const searchParams = useSearchParams();

  const rootRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{
    dragging: boolean;
    pointerId: number | null;
    startX: number;
    startY: number;
    originX: number;
    originY: number;
    moved: boolean;
  }>({
    dragging: false,
    pointerId: null,
    startX: 0,
    startY: 0,
    originX: 0,
    originY: 0,
    moved: false,
  });

  const [open, setOpen] = useState<boolean>(false);
  const [pinned, setPinned] = useState<boolean>(false);
  const [pos, setPos] = useState<DockPos>({ x: 0, y: 0 });
  const [query, setQuery] = useState("");
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS);
  const [dim, setDim] = useState({ w: 360, h: 440 });

  // init
  useEffect(() => {
    const initialOpen = safeJsonParse<boolean>(localStorage.getItem(OPEN_KEY), false);
    const initialPinned = safeJsonParse<boolean>(localStorage.getItem(PIN_KEY), false);
    const initialPrefs = safeJsonParse<Prefs>(localStorage.getItem(PREFS_KEY), DEFAULT_PREFS);
    setOpen(initialOpen);
    setPinned(initialPinned);
    setPrefs({ ...DEFAULT_PREFS, ...initialPrefs });

    // default position: bottom-right with margins
    const saved = safeJsonParse<DockPos | null>(localStorage.getItem(POS_KEY), null);
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const margin = 16;
    const fallback = {
      x: Math.max(margin, vw - 72 - margin),
      y: Math.max(margin, vh - 72 - margin),
    };
    setPos(saved ?? fallback);
  }, []);

  // persist
  useEffect(() => {
    localStorage.setItem(OPEN_KEY, JSON.stringify(open));
  }, [open]);

  useEffect(() => {
    localStorage.setItem(PIN_KEY, JSON.stringify(pinned));
  }, [pinned]);

  useEffect(() => {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
  }, [prefs]);

  // resize handling (keep in viewport)
  useEffect(() => {
    function onResize() {
      const vw = window.innerWidth;
      const vh = window.innerHeight;
      const margin = 10;
      setPos(p => ({
        x: clamp(p.x, margin, vw - margin),
        y: clamp(p.y, margin, vh - margin),
      }));
    }
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const currentQS = useMemo(() => {
    // next/navigation searchParams is readonly-ish; rebuild
    const q = new URLSearchParams(searchParams?.toString() ?? "");
    return q;
  }, [searchParams]);

  const scenes = useMemo(() => {
    const all = allScenesFlat();
    const q = query.trim().toLowerCase();
    if (!q) return SCENE_GROUPS;

    const filteredGroups = SCENE_GROUPS
      .map(g => ({
        title: g.title,
        items: g.items.filter(it => {
          const hay = `${it.title} ${it.id} ${it.path}`.toLowerCase();
          return hay.includes(q);
        }),
      }))
      .filter(g => g.items.length > 0);

    // if search hides studio link, still allow current path quick return
    return filteredGroups.length ? filteredGroups : [{ title: "Results", items: all.filter(it => `${it.title} ${it.id} ${it.path}`.toLowerCase().includes(q)) }];
  }, [query]);

  function navigateTo(item: SceneItem) {
    const qs = buildQuery(currentQS, prefs);
    const url = `${item.path}${qs}`;

    // If you are already on it, just refresh-ish (push same)
    if (!prefs.openInNewTab) {
      router.push(url);
      if (!pinned) setOpen(false);
      return;
    }

    // new tab
    window.open(url, "_blank", "noopener,noreferrer");
    if (!pinned) setOpen(false);
  }

  function centerDock() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    setPos({ x: vw - 72 - 18, y: Math.max(18, (vh / 2) - 36) });
  }

  function onPointerDown(e: React.PointerEvent) {
    // Only start drag from the orb (collapsed) or from panel header "grab" area.
    const target = e.target as HTMLElement;
    const allow = target.closest("[data-dock-drag='1']");
    if (!allow) return;

    dragRef.current.dragging = true;
    dragRef.current.pointerId = e.pointerId;
    dragRef.current.startX = e.clientX;
    dragRef.current.startY = e.clientY;
    dragRef.current.originX = pos.x;
    dragRef.current.originY = pos.y;
    dragRef.current.moved = false;

    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }

  function onPointerMove(e: React.PointerEvent) {
    if (!dragRef.current.dragging) return;
    if (dragRef.current.pointerId !== e.pointerId) return;

    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    if (Math.abs(dx) + Math.abs(dy) > 6) dragRef.current.moved = true;

    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const margin = 10;
    setPos({
      x: clamp(dragRef.current.originX + dx, margin, vw - margin),
      y: clamp(dragRef.current.originY + dy, margin, vh - margin),
    });
  }

  function onPointerUp(e: React.PointerEvent) {
    if (!dragRef.current.dragging) return;
    if (dragRef.current.pointerId !== e.pointerId) return;

    dragRef.current.dragging = false;
    dragRef.current.pointerId = null;

    localStorage.setItem(POS_KEY, JSON.stringify(pos));

    // If it was a drag, prevent accidental toggle
    // (We handle click toggle elsewhere; this stops “drag click” vibes.)
    try {
      (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId);
    } catch {
      // Pointer capture can already be released by the browser in edge cases.
    }
  }

  function toggleOpen() {
    setOpen(v => !v);
  }

  // auto-dim for tiny screens (mobile-ish)
  useEffect(() => {
    if (typeof window === "undefined") return;
    const small = window.innerWidth < 520 || isTouchLike();
    setDim({ w: small ? 320 : 360, h: small ? 420 : 440 });
  }, []);

  const showBackToStudio = pathname !== "/dev/scene-studio";
  const activeHint = pathname.startsWith("/pitch/")
    ? "Pitch"
    : pathname.startsWith("/dev/scene-studio")
      ? "Studio"
      : "App";

  return (
    <>
      <div
        ref={rootRef}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        style={{
          position: "fixed",
          left: pos.x,
          top: pos.y,
          transform: "translate(-50%, -50%)",
          zIndex: 99999,
          userSelect: "none",
        }}
      >
        {/* Orb button (always visible) */}
        <button
          type="button"
          className={`hitechDockOrb ${open ? "isOpen" : ""}`}
          aria-label={open ? "Close Scene Dock" : "Open Scene Dock"}
          onClick={() => {
            // if just dragged, ignore click
            if (dragRef.current.moved) return;
            toggleOpen();
          }}
          data-dock-drag="1"
        >
          <span className="orbIcon" aria-hidden="true">◈</span>
          <span className="orbDot" aria-hidden="true" />
          <span className="orbPulse" aria-hidden="true" />
        </button>

        {/* Panel */}
        <div
          className={`hitechDockPanel ${open ? "open" : ""}`}
          style={{ width: dim.w, height: dim.h }}
          aria-hidden={!open}
        >
          <div className="panelHeader" data-dock-drag="1">
            <div className="panelTitle">
              <div className="chip">{activeHint}</div>
              <div className="titleText">Scene Dock</div>
            </div>

            <div className="panelActions">
              <button
                type="button"
                className={`miniBtn ${pinned ? "on" : ""}`}
                title={pinned ? "Pinned (won't auto-close)" : "Pin panel"}
                onClick={() => setPinned(v => !v)}
              >
                {pinned ? "Pinned" : "Pin"}
              </button>

              <button
                type="button"
                className="miniBtn"
                title="Center dock"
                onClick={centerDock}
              >
                Center
              </button>

              <button
                type="button"
                className="miniBtn danger"
                title="Close"
                onClick={() => setOpen(false)}
              >
                ✕
              </button>
            </div>
          </div>

          <div className="panelBody">
            <div className="searchRow">
              <input
                className="searchInput"
                placeholder="Busca escena… (ej: engine, pitch, studio)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button className="ghostBtn" onClick={() => setQuery("")} title="Clear">
                Clear
              </button>
            </div>

            <div className="prefsCard">
              <div className="prefsRow">
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={prefs.openInNewTab}
                    onChange={(e) => setPrefs(p => ({ ...p, openInNewTab: e.target.checked }))}
                  />
                  <span>Open new tab</span>
                </label>

                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={prefs.keepQuery}
                    onChange={(e) => setPrefs(p => ({ ...p, keepQuery: e.target.checked }))}
                  />
                  <span>Keep query</span>
                </label>
              </div>

              <div className="segGrid">
                <div className="seg">
                  <div className="segLabel">Layers</div>
                  <div className="segBtns">
                    {(["keep","none","all"] as const).map(v => (
                      <button
                        key={v}
                        className={`segBtn ${prefs.layers === v ? "on" : ""}`}
                        onClick={() => setPrefs(p => ({ ...p, layers: v }))}
                        type="button"
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="seg">
                  <div className="segLabel">Motion</div>
                  <div className="segBtns">
                    {(["keep","off","on"] as const).map(v => (
                      <button
                        key={v}
                        className={`segBtn ${prefs.motion === v ? "on" : ""}`}
                        onClick={() => setPrefs(p => ({ ...p, motion: v }))}
                        type="button"
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="seg">
                  <div className="segLabel">Profile</div>
                  <div className="segBtns">
                    {(["keep","neutral","fx"] as const).map(v => (
                      <button
                        key={v}
                        className={`segBtn ${prefs.layerProfile === v ? "on" : ""}`}
                        onClick={() => setPrefs(p => ({ ...p, layerProfile: v }))}
                        type="button"
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="seg">
                  <div className="segLabel">Debug</div>
                  <div className="segBtns">
                    {(["keep","0","1"] as const).map(v => (
                      <button
                        key={v}
                        className={`segBtn ${prefs.debug === v ? "on" : ""}`}
                        onClick={() => setPrefs(p => ({ ...p, debug: v }))}
                        type="button"
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="hintRow">
                <span className="hintDot" />
                <span className="hintText">
                  Tip: si tu Studio abre con <b>?debug=1</b>, pon Debug=1 y Keep query=ON.
                </span>
              </div>
            </div>

            <div className="sceneList">
              {showBackToStudio && (
                <div className="quickRow">
                  <button
                    type="button"
                    className="primaryBtn"
                    onClick={() => navigateTo({ id: "scene-studio", title: "Scene Studio", path: "/dev/scene-studio" })}
                  >
                    ↩ Back to Scene Studio
                  </button>
                </div>
              )}

              {scenes.map((g) => (
                <div className="group" key={g.title}>
                  <div className="groupTitle">{g.title}</div>
                  <div className="grid">
                    {g.items.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        className="sceneBtn"
                        onClick={() => navigateTo(item)}
                      >
                        <div className="sceneTitle">{item.title}</div>
                        <div className="sceneMeta">{item.path}</div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="footerRow">
              <div className="footerLeft">
                <span className="tiny">Liquid Glass • HITECH Dock</span>
              </div>
              <div className="footerRight">
                <button
                  type="button"
                  className="ghostBtn"
                  onClick={() => setPrefs(DEFAULT_PREFS)}
                  title="Reset prefs"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* shine overlay */}
          <div className="shine" aria-hidden="true" />
        </div>
      </div>

      {/* Styles (self-contained, no deps) */}
      <style jsx global>{`
        .hitechDockOrb {
          width: 62px;
          height: 62px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.18);
          background:
            radial-gradient(120% 120% at 30% 20%, rgba(255,255,255,0.22), rgba(255,255,255,0) 40%),
            radial-gradient(120% 120% at 70% 80%, rgba(2,167,202,0.22), rgba(2,167,202,0) 42%),
            linear-gradient(135deg, rgba(2,111,134,0.55), rgba(171,123,38,0.45));
          box-shadow:
            0 18px 45px rgba(0,0,0,0.35),
            0 8px 18px rgba(0,0,0,0.20),
            inset 0 1px 0 rgba(255,255,255,0.22);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          position: relative;
          cursor: pointer;
          display: grid;
          place-items: center;
          transform: translateZ(0);
          transition: transform 220ms cubic-bezier(.2,.8,.2,1), box-shadow 220ms cubic-bezier(.2,.8,.2,1);
        }
        .hitechDockOrb:hover {
          transform: translateZ(0) scale(1.06);
          box-shadow:
            0 26px 60px rgba(0,0,0,0.42),
            0 12px 22px rgba(0,0,0,0.22),
            inset 0 1px 0 rgba(255,255,255,0.28);
        }
        .hitechDockOrb:active { transform: translateZ(0) scale(0.98); }

        .hitechDockOrb .orbIcon {
          font-size: 18px;
          font-weight: 700;
          color: rgba(255,255,255,0.92);
          text-shadow: 0 6px 18px rgba(0,0,0,0.35);
          letter-spacing: 0.06em;
        }
        .hitechDockOrb .orbDot {
          position: absolute;
          right: 12px;
          top: 12px;
          width: 9px;
          height: 9px;
          border-radius: 999px;
          background: rgba(255,255,255,0.9);
          box-shadow: 0 0 0 2px rgba(0,0,0,0.12), 0 0 18px rgba(2,167,202,0.45);
          opacity: 0.9;
        }
        .hitechDockOrb .orbPulse {
          position: absolute;
          inset: -10px;
          border-radius: 999px;
          background: radial-gradient(circle, rgba(2,167,202,0.22), rgba(2,167,202,0) 60%);
          filter: blur(2px);
          opacity: 0.75;
          animation: hitechPulse 2.6s ease-in-out infinite;
          pointer-events: none;
        }
        @keyframes hitechPulse {
          0%, 100% { transform: scale(0.96); opacity: 0.55; }
          50%      { transform: scale(1.06); opacity: 0.92; }
        }

        .hitechDockPanel {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -52%) scale(0.96);
          opacity: 0;
          pointer-events: none;
          border-radius: 18px;
          border: 1px solid rgba(255,255,255,0.16);
          background:
            radial-gradient(120% 120% at 22% 10%, rgba(255,255,255,0.20), rgba(255,255,255,0) 46%),
            radial-gradient(120% 120% at 78% 92%, rgba(171,123,38,0.16), rgba(171,123,38,0) 45%),
            linear-gradient(180deg, rgba(20,24,30,0.55), rgba(12,14,18,0.55));
          box-shadow:
            0 30px 90px rgba(0,0,0,0.55),
            0 10px 28px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.16);
          backdrop-filter: blur(18px) saturate(140%);
          -webkit-backdrop-filter: blur(18px) saturate(140%);
          overflow: hidden;
          transition:
            transform 260ms cubic-bezier(.2,.8,.2,1),
            opacity 240ms cubic-bezier(.2,.8,.2,1);
        }
        .hitechDockPanel.open {
          opacity: 1;
          pointer-events: auto;
          transform: translate(-50%, -58%) scale(1);
        }

        .shine {
          position: absolute;
          inset: -40%;
          background: linear-gradient(115deg,
            rgba(255,255,255,0) 35%,
            rgba(255,255,255,0.08) 45%,
            rgba(255,255,255,0) 55%);
          transform: rotate(12deg);
          animation: hitechShine 5.5s ease-in-out infinite;
          pointer-events: none;
        }
        @keyframes hitechShine {
          0%   { translate: -12% 0; opacity: 0.35; }
          50%  { translate: 12% 0; opacity: 0.55; }
          100% { translate: -12% 0; opacity: 0.35; }
        }

        .panelHeader {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 12px 10px 12px;
          border-bottom: 1px solid rgba(255,255,255,0.10);
          cursor: grab;
        }
        .panelHeader:active { cursor: grabbing; }
        .panelTitle { display: flex; gap: 10px; align-items: center; }
        .chip {
          font-size: 11px;
          padding: 6px 10px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.14);
          background: rgba(2,111,134,0.18);
          color: rgba(255,255,255,0.9);
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }
        .titleText {
          font-size: 14px;
          font-weight: 700;
          color: rgba(255,255,255,0.92);
          letter-spacing: 0.02em;
        }
        .panelActions { display: flex; gap: 8px; align-items: center; }

        .miniBtn {
          font-size: 12px;
          padding: 7px 10px;
          border-radius: 10px;
          border: 1px solid rgba(255,255,255,0.12);
          background: rgba(255,255,255,0.06);
          color: rgba(255,255,255,0.9);
          transition: transform 160ms cubic-bezier(.2,.8,.2,1), background 160ms ease, border-color 160ms ease;
        }
        .miniBtn:hover {
          transform: translateY(-1px);
          background: rgba(255,255,255,0.10);
          border-color: rgba(255,255,255,0.18);
        }
        .miniBtn.on {
          background: rgba(2,167,202,0.14);
          border-color: rgba(2,167,202,0.28);
        }
        .miniBtn.danger {
          background: rgba(255,255,255,0.04);
        }

        .panelBody {
          padding: 12px;
          height: calc(100% - 48px);
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .searchRow { display: flex; gap: 8px; align-items: center; }
        .searchInput {
          flex: 1;
          height: 36px;
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.12);
          background: rgba(255,255,255,0.06);
          color: rgba(255,255,255,0.92);
          padding: 0 12px;
          outline: none;
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }
        .searchInput:focus {
          border-color: rgba(2,167,202,0.36);
          box-shadow: 0 0 0 3px rgba(2,167,202,0.12), inset 0 1px 0 rgba(255,255,255,0.10);
        }

        .ghostBtn {
          height: 36px;
          padding: 0 10px;
          border-radius: 12px;
          border: 1px solid rgba(255,255,255,0.10);
          background: rgba(255,255,255,0.04);
          color: rgba(255,255,255,0.84);
          transition: transform 160ms cubic-bezier(.2,.8,.2,1), background 160ms ease;
        }
        .ghostBtn:hover { transform: translateY(-1px); background: rgba(255,255,255,0.08); }

        .prefsCard {
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.10);
          background: rgba(0,0,0,0.10);
          padding: 10px;
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }
        .prefsRow { display: flex; gap: 14px; align-items: center; justify-content: space-between; padding-bottom: 8px; }
        .toggle { display: flex; gap: 8px; align-items: center; font-size: 12px; color: rgba(255,255,255,0.86); }
        .toggle input { accent-color: #02A7CA; }

        .segGrid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 10px;
          padding-top: 6px;
        }
        .seg { border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03); padding: 8px; }
        .segLabel { font-size: 11px; color: rgba(255,255,255,0.75); padding-bottom: 6px; letter-spacing: 0.03em; }
        .segBtns { display: flex; gap: 6px; flex-wrap: wrap; }
        .segBtn {
          font-size: 11px;
          padding: 6px 8px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.10);
          background: rgba(255,255,255,0.04);
          color: rgba(255,255,255,0.86);
          transition: transform 140ms cubic-bezier(.2,.8,.2,1), background 140ms ease, border-color 140ms ease;
        }
        .segBtn:hover { transform: translateY(-1px); background: rgba(255,255,255,0.07); }
        .segBtn.on {
          background: rgba(2,111,134,0.20);
          border-color: rgba(2,167,202,0.28);
          box-shadow: 0 0 0 3px rgba(2,167,202,0.10);
        }

        .hintRow { display: flex; gap: 8px; align-items: center; padding-top: 10px; }
        .hintDot {
          width: 8px; height: 8px; border-radius: 999px;
          background: rgba(171,123,38,0.85);
          box-shadow: 0 0 18px rgba(171,123,38,0.35);
        }
        .hintText { font-size: 11px; color: rgba(255,255,255,0.78); line-height: 1.3; }

        .sceneList {
          flex: 1;
          overflow: auto;
          padding-right: 2px;
        }
        .sceneList::-webkit-scrollbar { width: 10px; }
        .sceneList::-webkit-scrollbar-thumb {
          background: rgba(255,255,255,0.08);
          border-radius: 999px;
          border: 2px solid rgba(0,0,0,0.0);
          background-clip: padding-box;
        }
        .quickRow { padding-bottom: 10px; }
        .primaryBtn {
          width: 100%;
          height: 40px;
          border-radius: 14px;
          border: 1px solid rgba(2,167,202,0.25);
          background: linear-gradient(135deg, rgba(2,167,202,0.16), rgba(2,111,134,0.12));
          color: rgba(255,255,255,0.92);
          font-weight: 700;
          letter-spacing: 0.02em;
          box-shadow: 0 12px 30px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.10);
          transition: transform 160ms cubic-bezier(.2,.8,.2,1), border-color 160ms ease;
        }
        .primaryBtn:hover { transform: translateY(-1px); border-color: rgba(2,167,202,0.34); }

        .group { padding-bottom: 10px; }
        .groupTitle {
          font-size: 12px;
          color: rgba(255,255,255,0.84);
          padding: 6px 2px 8px 2px;
          letter-spacing: 0.04em;
          text-transform: uppercase;
        }
        .grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 8px;
        }
        .sceneBtn {
          text-align: left;
          padding: 10px 10px;
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.10);
          background: rgba(255,255,255,0.04);
          color: rgba(255,255,255,0.92);
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
          transition: transform 160ms cubic-bezier(.2,.8,.2,1), background 160ms ease, border-color 160ms ease;
        }
        .sceneBtn:hover {
          transform: translateY(-1px);
          background: rgba(255,255,255,0.07);
          border-color: rgba(255,255,255,0.16);
        }
        .sceneTitle { font-size: 13px; font-weight: 700; letter-spacing: 0.01em; }
        .sceneMeta { font-size: 11px; color: rgba(255,255,255,0.70); padding-top: 4px; }

        .footerRow {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 6px;
          border-top: 1px solid rgba(255,255,255,0.08);
        }
        .tiny { font-size: 11px; color: rgba(255,255,255,0.62); }
      `}</style>
    </>
  );
}
