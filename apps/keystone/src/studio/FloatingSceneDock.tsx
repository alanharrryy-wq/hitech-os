"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SCENE_GROUPS, allScenesFlat, type SceneItem } from "./scene-registry";

type DockPosition = { x: number; y: number };

type DockPrefs = {
  openInNewTab: boolean;
  keepQuery: boolean;
  layers: "keep" | "none" | "all";
  motion: "keep" | "off" | "on";
  layerProfile: "keep" | "neutral" | "fx";
  debug: "keep" | "0" | "1";
};

type DragState = {
  dragging: boolean;
  startX: number;
  startY: number;
  originX: number;
  originY: number;
  moved: boolean;
};

const POS_KEY = "keystone.liquidDock.pos.v1";
const OPEN_KEY = "keystone.liquidDock.open.v1";
const PIN_KEY = "keystone.liquidDock.pin.v1";
const PREFS_KEY = "keystone.liquidDock.prefs.v1";

const DEFAULT_PREFS: DockPrefs = {
  openInNewTab: false,
  keepQuery: true,
  layers: "keep",
  motion: "keep",
  layerProfile: "keep",
  debug: "keep"
};

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(value, max));
}

function readJson<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore storage restrictions
  }
}

function toQueryString(search: URLSearchParams, prefs: DockPrefs): string {
  const next = new URLSearchParams(prefs.keepQuery ? search.toString() : "");

  if (prefs.layers !== "keep") next.set("layers", prefs.layers);
  if (prefs.motion !== "keep") next.set("motion", prefs.motion);
  if (prefs.layerProfile !== "keep") next.set("layerProfile", prefs.layerProfile);
  if (prefs.debug !== "keep") next.set("debug", prefs.debug);

  const serialized = next.toString();
  return serialized.length > 0 ? `?${serialized}` : "";
}

export function FloatingSceneDock() {
  const router = useRouter();
  const pathname = usePathname() ?? "";
  const searchParams = useSearchParams();

  const dragRef = useRef<DragState>({
    dragging: false,
    startX: 0,
    startY: 0,
    originX: 0,
    originY: 0,
    moved: false
  });

  const [ready, setReady] = useState(false);
  const [open, setOpen] = useState(false);
  const [pinned, setPinned] = useState(false);
  const [position, setPosition] = useState<DockPosition>({ x: 0, y: 0 });
  const [panelSize, setPanelSize] = useState({ w: 360, h: 440 });
  const [query, setQuery] = useState("");
  const [prefs, setPrefs] = useState<DockPrefs>(DEFAULT_PREFS);

  useEffect(() => {
    const margin = 20;
    const fallback = {
      x: Math.max(margin, window.innerWidth - 72 - margin),
      y: Math.max(margin, window.innerHeight - 72 - margin)
    };

    setPosition(readJson<DockPosition>(POS_KEY, fallback));
    setOpen(readJson<boolean>(OPEN_KEY, false));
    setPinned(readJson<boolean>(PIN_KEY, false));
    setPrefs({ ...DEFAULT_PREFS, ...readJson<Partial<DockPrefs>>(PREFS_KEY, {}) });
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    writeJson(POS_KEY, position);
  }, [position, ready]);

  useEffect(() => {
    if (!ready) return;
    writeJson(OPEN_KEY, open);
  }, [open, ready]);

  useEffect(() => {
    if (!ready) return;
    writeJson(PIN_KEY, pinned);
  }, [pinned, ready]);

  useEffect(() => {
    if (!ready) return;
    writeJson(PREFS_KEY, prefs);
  }, [prefs, ready]);

  useEffect(() => {
    if (!ready) return;

    const clampToViewport = () => {
      const margin = 10;
      setPosition((prev) => ({
        x: clamp(prev.x, margin, window.innerWidth - margin),
        y: clamp(prev.y, margin, window.innerHeight - margin)
      }));

      const compact = window.innerWidth < 560;
      setPanelSize(compact ? { w: 320, h: 410 } : { w: 360, h: 440 });
    };

    clampToViewport();
    window.addEventListener("resize", clampToViewport);
    return () => window.removeEventListener("resize", clampToViewport);
  }, [ready]);

  useEffect(() => {
    if (!ready) return;

    const onMouseMove = (event: MouseEvent) => {
      if (!dragRef.current.dragging) return;

      const dx = event.clientX - dragRef.current.startX;
      const dy = event.clientY - dragRef.current.startY;
      if (Math.abs(dx) + Math.abs(dy) > 6) {
        dragRef.current.moved = true;
      }

      const margin = 10;
      setPosition({
        x: clamp(dragRef.current.originX + dx, margin, window.innerWidth - margin),
        y: clamp(dragRef.current.originY + dy, margin, window.innerHeight - margin)
      });
    };

    const onMouseUp = () => {
      dragRef.current.dragging = false;
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [ready]);

  const currentQuery = useMemo(
    () => new URLSearchParams(searchParams?.toString() ?? ""),
    [searchParams]
  );

  const filteredGroups = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return SCENE_GROUPS;

    const filtered = SCENE_GROUPS.map((group) => ({
      title: group.title,
      items: group.items.filter((item) =>
        `${item.title} ${item.id} ${item.path}`.toLowerCase().includes(q)
      )
    })).filter((group) => group.items.length > 0);

    if (filtered.length > 0) return filtered;

    return [
      {
        title: "Results",
        items: allScenesFlat().filter((item) =>
          `${item.title} ${item.id} ${item.path}`.toLowerCase().includes(q)
        )
      }
    ];
  }, [query]);

  const activeScope = pathname.startsWith("/pitch/")
    ? "Pitch"
    : pathname.startsWith("/dev/scene-studio")
      ? "Studio"
      : "App";

  const shouldShowBackToStudio = pathname !== "/dev/scene-studio";

  const startDrag = (event: React.MouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    const draggable = target.closest("[data-dock-drag='1']");
    if (!draggable) return;

    dragRef.current.dragging = true;
    dragRef.current.startX = event.clientX;
    dragRef.current.startY = event.clientY;
    dragRef.current.originX = position.x;
    dragRef.current.originY = position.y;
    dragRef.current.moved = false;
    event.preventDefault();
  };

  const centerDock = () => {
    setPosition({
      x: window.innerWidth - 74,
      y: Math.max(54, Math.floor(window.innerHeight / 2))
    });
  };

  const navigateTo = (item: SceneItem) => {
    const href = `${item.path}${toQueryString(currentQuery, prefs)}`;
    if (prefs.openInNewTab) {
      window.open(href, "_blank", "noopener,noreferrer");
    } else {
      router.push(href);
    }
    if (!pinned) {
      setOpen(false);
    }
  };

  if (!ready) return null;

  return (
    <>
      <div
        className="ksLiquidDockRoot"
        style={{ left: position.x, top: position.y }}
        onMouseDown={startDrag}
      >
        <button
          type="button"
          className={`ksLiquidDockOrb ${open ? "isOpen" : ""}`}
          aria-label={open ? "Close Scene Dock" : "Open Scene Dock"}
          onClick={() => {
            if (dragRef.current.moved) {
              dragRef.current.moved = false;
              return;
            }
            setOpen((prev) => !prev);
          }}
          data-dock-drag="1"
        >
          <span className="ksLiquidDockGlyph" aria-hidden="true">
            ◈
          </span>
          <span className="ksLiquidDockDot" aria-hidden="true" />
          <span className="ksLiquidDockPulse" aria-hidden="true" />
        </button>

        <section
          className={`ksLiquidDockPanel ${open ? "isOpen" : ""}`}
          style={{ width: panelSize.w, height: panelSize.h }}
          aria-hidden={!open}
        >
          <header className="ksLiquidDockHeader" data-dock-drag="1">
            <div className="ksLiquidDockTitle">
              <span className="ksLiquidDockChip">{activeScope}</span>
              <span className="ksLiquidDockLabel">Scene Dock</span>
            </div>
            <div className="ksLiquidDockActions">
              <button
                type="button"
                className={`ksLiquidDockMini ${pinned ? "on" : ""}`}
                onClick={() => setPinned((prev) => !prev)}
                title={pinned ? "Pinned panel" : "Pin panel"}
              >
                {pinned ? "Pinned" : "Pin"}
              </button>
              <button
                type="button"
                className="ksLiquidDockMini"
                onClick={centerDock}
                title="Center dock"
              >
                Center
              </button>
              <button
                type="button"
                className="ksLiquidDockMini danger"
                onClick={() => setOpen(false)}
                title="Collapse to orb"
              >
                ✕
              </button>
            </div>
          </header>

          <div className="ksLiquidDockBody">
            <div className="ksLiquidDockSearchRow">
              <input
                className="ksLiquidDockSearch"
                value={query}
                placeholder="Search scenes..."
                onChange={(event) => setQuery(event.currentTarget.value)}
              />
              <button type="button" className="ksLiquidDockGhost" onClick={() => setQuery("")}>
                Clear
              </button>
            </div>

            <div className="ksLiquidDockPrefs">
              <label className="ksLiquidDockToggle">
                <input
                  type="checkbox"
                  checked={prefs.openInNewTab}
                  onChange={(event) =>
                    setPrefs((prev) => ({ ...prev, openInNewTab: event.currentTarget.checked }))
                  }
                />
                <span>Open in new tab</span>
              </label>
              <label className="ksLiquidDockToggle">
                <input
                  type="checkbox"
                  checked={prefs.keepQuery}
                  onChange={(event) =>
                    setPrefs((prev) => ({ ...prev, keepQuery: event.currentTarget.checked }))
                  }
                />
                <span>Keep query params</span>
              </label>
            </div>

            <div className="ksLiquidDockSegments">
              <span className="ksLiquidDockSegLabel">Layers</span>
              {(["keep", "none", "all"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  className={`ksLiquidDockSeg ${prefs.layers === value ? "on" : ""}`}
                  onClick={() => setPrefs((prev) => ({ ...prev, layers: value }))}
                >
                  {value}
                </button>
              ))}
            </div>

            {shouldShowBackToStudio ? (
              <button
                type="button"
                className="ksLiquidDockPrimary"
                onClick={() =>
                  navigateTo({
                    id: "scene-studio",
                    title: "Scene Studio",
                    path: "/dev/scene-studio"
                  })
                }
              >
                Back to Scene Studio
              </button>
            ) : null}

            <div className="ksLiquidDockList">
              {filteredGroups.map((group) => (
                <div key={group.title} className="ksLiquidDockGroup">
                  <div className="ksLiquidDockGroupTitle">{group.title}</div>
                  <div className="ksLiquidDockGrid">
                    {group.items.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        className="ksLiquidDockScene"
                        onClick={() => navigateTo(item)}
                      >
                        <span className="ksLiquidDockSceneTitle">{item.title}</span>
                        <span className="ksLiquidDockScenePath">{item.path}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <footer className="ksLiquidDockFooter">
              <span>Liquid Glass Dock</span>
              <button
                type="button"
                className="ksLiquidDockGhost"
                onClick={() => setPrefs(DEFAULT_PREFS)}
              >
                Reset
              </button>
            </footer>
          </div>
          <div className="ksLiquidDockShine" aria-hidden="true" />
        </section>
      </div>

      <style jsx global>{`
        .ksLiquidDockRoot {
          position: fixed;
          transform: translate(-50%, -50%);
          z-index: 99999;
          user-select: none;
        }
        .ksLiquidDockOrb {
          width: 62px;
          height: 62px;
          border-radius: 999px;
          border: 1px solid rgba(255, 255, 255, 0.22);
          background:
            radial-gradient(
              120% 120% at 30% 20%,
              rgba(255, 255, 255, 0.24),
              rgba(255, 255, 255, 0) 42%
            ),
            radial-gradient(
              120% 120% at 80% 86%,
              rgba(2, 167, 202, 0.24),
              rgba(2, 167, 202, 0) 44%
            ),
            linear-gradient(135deg, rgba(2, 111, 134, 0.58), rgba(171, 123, 38, 0.46));
          box-shadow:
            0 24px 60px rgba(0, 0, 0, 0.46),
            0 10px 24px rgba(0, 0, 0, 0.24),
            inset 0 1px 0 rgba(255, 255, 255, 0.28);
          backdrop-filter: blur(13px);
          -webkit-backdrop-filter: blur(13px);
          cursor: pointer;
          display: grid;
          place-items: center;
          position: relative;
          transition:
            transform 200ms ease,
            box-shadow 200ms ease;
        }
        .ksLiquidDockOrb:hover {
          transform: scale(1.06);
        }
        .ksLiquidDockOrb:active {
          transform: scale(0.98);
        }
        .ksLiquidDockGlyph {
          color: rgba(255, 255, 255, 0.92);
          font-size: 18px;
          font-weight: 700;
          text-shadow: 0 6px 18px rgba(0, 0, 0, 0.34);
        }
        .ksLiquidDockDot {
          position: absolute;
          right: 12px;
          top: 12px;
          width: 8px;
          height: 8px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.94);
          box-shadow:
            0 0 0 2px rgba(0, 0, 0, 0.14),
            0 0 16px rgba(2, 167, 202, 0.45);
        }
        .ksLiquidDockPulse {
          position: absolute;
          inset: -10px;
          border-radius: 999px;
          background: radial-gradient(circle, rgba(2, 167, 202, 0.22), rgba(2, 167, 202, 0) 60%);
          animation: ksLiquidDockPulse 2.8s ease-in-out infinite;
          pointer-events: none;
        }
        @keyframes ksLiquidDockPulse {
          0%,
          100% {
            transform: scale(0.96);
            opacity: 0.52;
          }
          50% {
            transform: scale(1.06);
            opacity: 0.88;
          }
        }
        .ksLiquidDockPanel {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -55%) scale(0.96);
          opacity: 0;
          pointer-events: none;
          border-radius: 18px;
          border: 1px solid rgba(255, 255, 255, 0.16);
          background:
            radial-gradient(
              120% 120% at 20% 8%,
              rgba(255, 255, 255, 0.2),
              rgba(255, 255, 255, 0) 44%
            ),
            radial-gradient(
              120% 120% at 82% 92%,
              rgba(171, 123, 38, 0.16),
              rgba(171, 123, 38, 0) 45%
            ),
            linear-gradient(180deg, rgba(20, 24, 30, 0.58), rgba(12, 14, 18, 0.6));
          box-shadow:
            0 36px 100px rgba(0, 0, 0, 0.58),
            0 12px 28px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(18px) saturate(140%);
          -webkit-backdrop-filter: blur(18px) saturate(140%);
          overflow: hidden;
          transition:
            transform 250ms ease,
            opacity 230ms ease;
        }
        .ksLiquidDockPanel.isOpen {
          transform: translate(-50%, -60%) scale(1);
          opacity: 1;
          pointer-events: auto;
        }
        .ksLiquidDockHeader {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 8px;
          padding: 12px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          cursor: grab;
        }
        .ksLiquidDockHeader:active {
          cursor: grabbing;
        }
        .ksLiquidDockTitle {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .ksLiquidDockChip {
          border: 1px solid rgba(255, 255, 255, 0.14);
          border-radius: 999px;
          background: rgba(2, 111, 134, 0.2);
          color: rgba(255, 255, 255, 0.94);
          font-size: 11px;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          padding: 5px 10px;
        }
        .ksLiquidDockLabel {
          color: rgba(255, 255, 255, 0.94);
          font-size: 14px;
          font-weight: 700;
        }
        .ksLiquidDockActions {
          display: flex;
          gap: 7px;
        }
        .ksLiquidDockMini,
        .ksLiquidDockGhost,
        .ksLiquidDockSeg,
        .ksLiquidDockScene,
        .ksLiquidDockPrimary {
          cursor: pointer;
        }
        .ksLiquidDockMini {
          border: 1px solid rgba(255, 255, 255, 0.12);
          border-radius: 10px;
          padding: 6px 10px;
          font-size: 12px;
          background: rgba(255, 255, 255, 0.05);
          color: rgba(255, 255, 255, 0.9);
        }
        .ksLiquidDockMini.on {
          border-color: rgba(2, 167, 202, 0.35);
          background: rgba(2, 167, 202, 0.18);
        }
        .ksLiquidDockMini.danger {
          background: rgba(255, 255, 255, 0.03);
        }
        .ksLiquidDockBody {
          height: calc(100% - 54px);
          display: flex;
          flex-direction: column;
          gap: 10px;
          padding: 12px;
        }
        .ksLiquidDockSearchRow {
          display: flex;
          gap: 8px;
        }
        .ksLiquidDockSearch {
          flex: 1;
          height: 36px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.13);
          background: rgba(255, 255, 255, 0.06);
          color: rgba(255, 255, 255, 0.92);
          padding: 0 11px;
          outline: none;
        }
        .ksLiquidDockSearch:focus {
          border-color: rgba(2, 167, 202, 0.4);
          box-shadow: 0 0 0 3px rgba(2, 167, 202, 0.12);
        }
        .ksLiquidDockGhost {
          height: 36px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 11px;
          background: rgba(255, 255, 255, 0.05);
          color: rgba(255, 255, 255, 0.84);
          padding: 0 10px;
        }
        .ksLiquidDockPrefs {
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 14px;
          background: rgba(0, 0, 0, 0.12);
          padding: 9px 10px;
        }
        .ksLiquidDockToggle {
          display: inline-flex;
          gap: 7px;
          align-items: center;
          color: rgba(255, 255, 255, 0.88);
          font-size: 12px;
        }
        .ksLiquidDockToggle input {
          accent-color: #02a7ca;
        }
        .ksLiquidDockSegments {
          display: flex;
          gap: 6px;
          align-items: center;
          flex-wrap: wrap;
        }
        .ksLiquidDockSegLabel {
          color: rgba(255, 255, 255, 0.74);
          font-size: 11px;
          margin-right: 4px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .ksLiquidDockSeg {
          border: 1px solid rgba(255, 255, 255, 0.11);
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.05);
          color: rgba(255, 255, 255, 0.87);
          padding: 5px 9px;
          font-size: 11px;
        }
        .ksLiquidDockSeg.on {
          border-color: rgba(2, 167, 202, 0.34);
          background: rgba(2, 111, 134, 0.22);
          box-shadow: 0 0 0 3px rgba(2, 167, 202, 0.1);
        }
        .ksLiquidDockPrimary {
          width: 100%;
          border: 1px solid rgba(2, 167, 202, 0.3);
          border-radius: 13px;
          background: linear-gradient(135deg, rgba(2, 167, 202, 0.18), rgba(2, 111, 134, 0.14));
          color: rgba(255, 255, 255, 0.93);
          font-size: 13px;
          font-weight: 700;
          height: 38px;
        }
        .ksLiquidDockList {
          flex: 1;
          overflow: auto;
          padding-right: 2px;
        }
        .ksLiquidDockGroup {
          margin-bottom: 10px;
        }
        .ksLiquidDockGroupTitle {
          color: rgba(255, 255, 255, 0.85);
          font-size: 12px;
          padding: 4px 2px 7px 2px;
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .ksLiquidDockGrid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 8px;
        }
        .ksLiquidDockScene {
          display: grid;
          text-align: left;
          gap: 4px;
          border: 1px solid rgba(255, 255, 255, 0.11);
          border-radius: 15px;
          background: rgba(255, 255, 255, 0.05);
          color: rgba(255, 255, 255, 0.92);
          padding: 10px;
        }
        .ksLiquidDockSceneTitle {
          font-size: 13px;
          font-weight: 700;
        }
        .ksLiquidDockScenePath {
          font-size: 11px;
          color: rgba(255, 255, 255, 0.72);
        }
        .ksLiquidDockFooter {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
          color: rgba(255, 255, 255, 0.67);
          font-size: 11px;
          padding-top: 8px;
        }
        .ksLiquidDockShine {
          position: absolute;
          inset: -42%;
          background: linear-gradient(
            120deg,
            rgba(255, 255, 255, 0) 35%,
            rgba(255, 255, 255, 0.09) 45%,
            rgba(255, 255, 255, 0) 55%
          );
          transform: rotate(12deg);
          pointer-events: none;
          animation: ksLiquidDockShine 5.8s ease-in-out infinite;
        }
        @keyframes ksLiquidDockShine {
          0% {
            translate: -12% 0;
            opacity: 0.36;
          }
          50% {
            translate: 12% 0;
            opacity: 0.56;
          }
          100% {
            translate: -12% 0;
            opacity: 0.36;
          }
        }
      `}</style>
    </>
  );
}
