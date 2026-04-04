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

export interface FloatingWindowProps {
  id: string;
  title: string;
  defaultPos?: Vec2;
  defaultSize?: Size;
  homePos?: Vec2;
  homeSize?: Size;
  minSize?: Size;
  maxSize?: Size;
  minWidth?: number;
  minHeight?: number;
  initialZ?: number;
  hideCloseButton?: boolean;
  frameStyle?: "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";
  framePerfProfile?: "quality" | "perf";
  headerRight?: React.ReactNode;
  defaultState?: {
    x: number;
    y: number;
    w: number;
    h: number;
    z?: number;
    collapsed?: boolean;
    visible?: boolean;
  };
  children: React.ReactNode;
  className?: string;
}

const HEADER_HEIGHT = 48;
const COLLAPSED_HEIGHT = 54;
const VIEWPORT_GUTTER = 6;

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
  homePos,
  homeSize,
  minSize = { w: 280, h: 180 },
  maxSize,
  minWidth,
  minHeight,
  initialZ,
  hideCloseButton,
  frameStyle,
  framePerfProfile,
  headerRight,
  defaultState,
  children,
  className
}: FloatingWindowProps) {
  // Legacy API compatibility (frame styling is intentionally handled by CSS vars elsewhere).
  void hideCloseButton;
  void frameStyle;
  void framePerfProfile;

  const resolvedDefaultPos = defaultState ? { x: defaultState.x, y: defaultState.y } : defaultPos;
  const resolvedDefaultSize = defaultState ? { w: defaultState.w, h: defaultState.h } : defaultSize;
  const resolvedMinSize = useMemo<Size>(
    () => ({
      w: Math.max(minSize.w, minWidth ?? 0),
      h: Math.max(minSize.h, minHeight ?? 0)
    }),
    [minHeight, minSize.h, minSize.w, minWidth]
  );

  const storageKey = useMemo(() => `keystone.floatingWindow.${id}`, [id]);
  const rootRef = useRef<HTMLDivElement | null>(null);

  const [state, setState] = useState<FloatingWindowState>(() => {
    const saved = typeof window !== "undefined" ? readLS(storageKey) : null;
    return (
      saved ?? {
        pos: resolvedDefaultPos,
        size: resolvedDefaultSize,
        z: defaultState?.z ?? initialZ ?? 1000,
        collapsed: defaultState?.collapsed ?? false
      }
    );
  });
  const stateRef = useRef(state);

  useEffect(() => {
    stateRef.current = state;
  }, [state]);

  useEffect(() => {
    setState((prev) => {
      const next = clampState(prev, resolvedMinSize, maxSize);
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
  }, [maxSize, resolvedMinSize]);

  useEffect(() => {
    writeLS(storageKey, state);
  }, [storageKey, state]);

  useEffect(() => {
    const onResize = () => {
      setState((prev) => {
        const next = clampState(prev, resolvedMinSize, maxSize);
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
  }, [maxSize, resolvedMinSize]);

  const bringToFront = () => {
    setState((prev) => ({
      ...prev,
      z: Math.max(prev.z + 1, Date.now() % 2147483000)
    }));
  };

  const startDrag = (e: React.PointerEvent) => {
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
    if (stateRef.current.collapsed) return;
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

      const w = clamp(startState.size.w + dx, resolvedMinSize.w, Math.max(resolvedMinSize.w, wMax));
      const h = clamp(startState.size.h + dy, resolvedMinSize.h, Math.max(resolvedMinSize.h, hMax));

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

  const goHome = () => {
    if (!homePos && !homeSize) return;

    setState((prev) => ({
      ...prev,
      pos: homePos ?? prev.pos,
      size: homeSize ?? prev.size,
      collapsed: false
    }));
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
    display: state.collapsed ? "none" : "block"
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
        {headerRight ? <div style={{ display: "flex", alignItems: "center" }}>{headerRight}</div> : null}
        <div style={{ display: "flex", gap: 8 }}>
          {homePos || homeSize ? (
            <button
              type="button"
              style={btnStyle}
              onClick={(event) => {
                event.stopPropagation();
                goHome();
              }}
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
