"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";

type Vec2 = { x: number; y: number };
type Size = { w: number; h: number };

type FloatingWindowState = {
  pos: Vec2;
  size: Size;
  z: number;
  collapsed: boolean;
};

type RestoreEventDetail = {
  id?: string | null;
};

type LegacyWindowLayoutEntry = {
  x: number;
  y: number;
  w: number;
  h: number;
  z: number;
  visible: boolean;
  collapsed: boolean;
};

export interface FloatingWindowProps {
  id: string;
  title: string;
  defaultPos?: Vec2;
  defaultSize?: Size;
  minSize?: Size;
  maxSize?: Size;
  children: React.ReactNode;
  className?: string;

  homePos?: Vec2;
  homeSize?: Size;
  initialZ?: number;
  storageNamespace?: string;
  headerRight?: React.ReactNode;
  showHomeButton?: boolean;
  resizable?: boolean;

  // Legacy compatibility props. These are intentionally accepted so existing callers keep compiling.
  defaultState?: Partial<LegacyWindowLayoutEntry>;
  minWidth?: number;
  minHeight?: number;
  singleInstance?: boolean;
  hideCloseButton?: boolean;
  frameStyle?: "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";
  frameSurface?: "controlRoomHud" | "pitchSurface" | "kpiWidget";
  framePerfProfile?: "quality" | "perf";
}

const HEADER_HEIGHT = 48;
const COLLAPSED_HEIGHT = 54;
const VIEWPORT_GUTTER = 6;
const BASE_Z = 2_000_000_000;
const MAX_Z = 2_147_483_000;

const clamp = (n: number, min: number, max: number) => Math.max(min, Math.min(max, n));

function readLS(key: string): FloatingWindowState | null {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as FloatingWindowState;
    if (!parsed?.pos || !parsed?.size) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeLS(key: string, value: FloatingWindowState) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore localStorage failures in restrictive contexts
  }
}

function getViewport() {
  if (typeof window === "undefined") return { vw: 1280, vh: 720 };
  return { vw: window.innerWidth, vh: window.innerHeight };
}

function clampState(
  prev: FloatingWindowState,
  minSize: Size,
  maxSize: Size | undefined
): Pick<FloatingWindowState, "pos" | "size"> {
  const { vw, vh } = getViewport();
  const wMax = maxSize?.w ?? vw - VIEWPORT_GUTTER * 2;
  const hMax = maxSize?.h ?? vh - VIEWPORT_GUTTER * 2;

  const w = clamp(prev.size.w, minSize.w, Math.max(minSize.w, wMax));
  const h = clamp(prev.size.h, minSize.h, Math.max(minSize.h, hMax));

  const visibleHeight = prev.collapsed ? COLLAPSED_HEIGHT : h;
  const x = clamp(prev.pos.x, VIEWPORT_GUTTER, vw - w - VIEWPORT_GUTTER);
  const y = clamp(prev.pos.y, VIEWPORT_GUTTER, vh - visibleHeight - VIEWPORT_GUTTER);

  return { pos: { x, y }, size: { w, h } };
}

export function FloatingWindow({
  id,
  title,
  defaultPos = { x: 24, y: 24 },
  defaultSize = { w: 420, h: 520 },
  minSize = { w: 280, h: 180 },
  maxSize,
  children,
  className,
  homePos,
  homeSize,
  initialZ = BASE_Z,
  storageNamespace = "keystone.floatingWindow",
  headerRight,
  showHomeButton = true,
  resizable = true,
  defaultState,
  minWidth,
  minHeight
}: FloatingWindowProps) {
  const compatDefaultPos = {
    x: defaultState?.x ?? defaultPos.x,
    y: defaultState?.y ?? defaultPos.y
  };
  const compatDefaultSize = {
    w: defaultState?.w ?? defaultSize.w,
    h: defaultState?.h ?? defaultSize.h
  };
  const compatMinSize = {
    w: minSize.w > 0 ? minSize.w : 280,
    h: minSize.h > 0 ? minSize.h : 180
  };

  if (typeof minWidth === "number") {
    compatMinSize.w = Math.max(compatMinSize.w, minWidth);
  }

  if (typeof minHeight === "number") {
    compatMinSize.h = Math.max(compatMinSize.h, minHeight);
  }

  const resolvedHomePos = homePos ?? compatDefaultPos;
  const resolvedHomeSize = homeSize ?? compatDefaultSize;
  const resolvedInitialZ = defaultState?.z ?? initialZ;
  const resolvedInitialCollapsed = defaultState?.collapsed ?? false;
  const storageKey = useMemo(() => `${storageNamespace}.${id}`, [id, storageNamespace]);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const [state, setState] = useState<FloatingWindowState>(() => {
    const saved = typeof window !== "undefined" ? readLS(storageKey) : null;
    return (
      saved ?? {
        pos: compatDefaultPos,
        size: compatDefaultSize,
        z: resolvedInitialZ,
        collapsed: resolvedInitialCollapsed
      }
    );
  });

  const stateRef = useRef(state);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    setState((prev) => {
      const next = clampState(prev, compatMinSize, maxSize);
      if (
        next.pos.x === prev.pos.x &&
        next.pos.y === prev.pos.y &&
        next.size.w === prev.size.w &&
        next.size.h === prev.size.h
      ) {
        return prev;
      }
      return { ...prev, ...next };
    });
  }, [compatMinSize, maxSize]);

  useEffect(() => {
    writeLS(storageKey, state);
  }, [storageKey, state]);

  useEffect(() => {
    const onResize = () => {
      setState((prev) => {
        const next = clampState(prev, compatMinSize, maxSize);
        if (
          next.pos.x === prev.pos.x &&
          next.pos.y === prev.pos.y &&
          next.size.w === prev.size.w &&
          next.size.h === prev.size.h
        ) {
          return prev;
        }
        return { ...prev, ...next };
      });
    };

    window.addEventListener("resize", onResize, { passive: true });
    return () => window.removeEventListener("resize", onResize);
  }, [compatMinSize, maxSize]);

  useEffect(() => {
    const onRestore = (event: Event) => {
      const detail = (event as CustomEvent<RestoreEventDetail>).detail;
      if (detail?.id && detail.id !== id) return;

      const saved = readLS(storageKey);
      const next = saved ?? {
        pos: resolvedHomePos,
        size: resolvedHomeSize,
        z: Math.max(stateRef.current.z, resolvedInitialZ),
        collapsed: false
      };

      setState((prev) => ({
        ...prev,
        ...next,
        z: Math.max(next.z ?? prev.z, prev.z)
      }));
    };

    window.addEventListener("hitech:floating-window:restore", onRestore as EventListener);
    return () => window.removeEventListener("hitech:floating-window:restore", onRestore as EventListener);
  }, [id, resolvedHomePos, resolvedHomeSize, resolvedInitialZ, storageKey]);

  const bringToFront = () => {
    setState((prev) => ({
      ...prev,
      z: Math.min(MAX_Z, Math.max(prev.z + 1, BASE_Z + (Date.now() % 100_000)))
    }));
  };

  const resetToHome = () => {
    setState((prev) => ({
      ...prev,
      pos: resolvedHomePos,
      size: resolvedHomeSize,
      collapsed: false,
      z: Math.min(MAX_Z, Math.max(prev.z + 1, BASE_Z + (Date.now() % 100_000)))
    }));
  };

  const startDrag = (e: React.PointerEvent) => {
    if (e.button !== 0) return;

    bringToFront();

    const startPointer = { x: e.clientX, y: e.clientY };
    const startPos = { ...stateRef.current.pos };
    const startState = { ...stateRef.current };

    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);

    const onMove = (ev: PointerEvent) => {
      const dx = ev.clientX - startPointer.x;
      const dy = ev.clientY - startPointer.y;
      const { vw, vh } = getViewport();
      const visibleHeight = startState.collapsed ? COLLAPSED_HEIGHT : startState.size.h;

      const x = clamp(startPos.x + dx, VIEWPORT_GUTTER, vw - startState.size.w - VIEWPORT_GUTTER);
      const y = clamp(startPos.y + dy, VIEWPORT_GUTTER, vh - visibleHeight - VIEWPORT_GUTTER);

      setState((prev) => ({ ...prev, pos: { x, y } }));
    };

    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("pointerup", onUp, { passive: true });
    window.addEventListener("pointercancel", onUp, { passive: true });
  };

  const startResize = (e: React.PointerEvent) => {
    if (!resizable || stateRef.current.collapsed) return;
    if (e.button !== 0) return;

    bringToFront();

    const startPointer = { x: e.clientX, y: e.clientY };
    const startState = { ...stateRef.current };

    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);

    const onMove = (ev: PointerEvent) => {
      const dx = ev.clientX - startPointer.x;
      const dy = ev.clientY - startPointer.y;
      const { vw, vh } = getViewport();

      const wMax = maxSize?.w ?? vw - VIEWPORT_GUTTER * 2;
      const hMax = maxSize?.h ?? vh - VIEWPORT_GUTTER * 2;

      const w = clamp(startState.size.w + dx, compatMinSize.w, Math.max(compatMinSize.w, wMax));
      const h = clamp(startState.size.h + dy, compatMinSize.h, Math.max(compatMinSize.h, hMax));

      setState((prev) => ({ ...prev, size: { w, h } }));
    };

    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      window.removeEventListener("pointercancel", onUp);
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    window.addEventListener("pointerup", onUp, { passive: true });
    window.addEventListener("pointercancel", onUp, { passive: true });
  };

  const toggleCollapsed = () => {
    setState((prev) => ({ ...prev, collapsed: !prev.collapsed }));
  };

  const shellStyle: React.CSSProperties = {
    position: "fixed",
    left: 0,
    top: 0,
    transform: `translate3d(${state.pos.x}px, ${state.pos.y}px, 0)`,
    width: `${state.size.w}px`,
    height: state.collapsed ? `${COLLAPSED_HEIGHT}px` : `${state.size.h}px`,
    zIndex: state.z,
    borderRadius: 14,
    border: "1px solid hsl(var(--ui-border-2))",
    background: "hsl(var(--ui-surface-1) / 0.96)",
    boxShadow: "var(--ui-shadow-2)",
    overflow: "hidden",
    pointerEvents: "auto",
    backdropFilter: "blur(8px)"
  };

  const headerStyle: React.CSSProperties = {
    height: HEADER_HEIGHT,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 10,
    padding: "0 12px",
    borderBottom: "1px solid hsl(var(--ui-border-1))",
    cursor: "grab",
    userSelect: "none",
    touchAction: "none"
  };

  const titleStyle: React.CSSProperties = {
    fontSize: 13,
    opacity: 0.95,
    fontWeight: 650,
    letterSpacing: "0.2px",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis"
  };

  const btnStyle: React.CSSProperties = {
    height: 30,
    minWidth: 30,
    padding: "0 10px",
    borderRadius: 10,
    border: "1px solid hsl(var(--ui-border-2))",
    background: "hsl(var(--ui-surface-2) / 0.9)",
    color: "hsl(var(--ui-text-1))",
    cursor: "pointer",
    fontSize: 12
  };

  const bodyStyle: React.CSSProperties = {
    height: state.collapsed ? 0 : `calc(100% - ${HEADER_HEIGHT}px)`,
    overflow: "auto",
    padding: 12,
    pointerEvents: "auto"
  };

  const resizeHandleStyle: React.CSSProperties = {
    position: "absolute",
    right: 6,
    bottom: 6,
    width: 18,
    height: 18,
    borderRadius: 6,
    border: "1px solid hsl(var(--ui-border-2))",
    background: "hsl(var(--ui-surface-2) / 0.85)",
    cursor: "nwse-resize",
    touchAction: "none",
    display: state.collapsed || !resizable ? "none" : "block"
  };

  return (
    <div
      ref={rootRef}
      style={shellStyle}
      className={className}
      onPointerDown={bringToFront}
      aria-label={`FloatingWindow:${id}`}
    >
      <div style={headerStyle} onPointerDown={startDrag}>
        <div style={titleStyle} title={title}>
          {title}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {headerRight}

          {showHomeButton ? (
            <button
              type="button"
              style={btnStyle}
              onClick={(event) => {
                event.stopPropagation();
                resetToHome();
              }}
              title="Home position"
            >
              Home
            </button>
          ) : null}

          <button
            type="button"
            style={btnStyle}
            onClick={(event) => {
              event.stopPropagation();
              toggleCollapsed();
            }}
            title={state.collapsed ? "Expand" : "Collapse"}
          >
            {state.collapsed ? "Expand" : "Collapse"}
          </button>
        </div>
      </div>

      <div style={bodyStyle}>{children}</div>

      <div style={resizeHandleStyle} onPointerDown={startResize} title="Resize" />
    </div>
  );
}
