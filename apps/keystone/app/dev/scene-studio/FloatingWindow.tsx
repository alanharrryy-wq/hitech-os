"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode
} from "react";
import { luxury } from "@hitech/ui-kit";
import { clampGeometry } from "./window-manager/clamp";
import { applySnapCandidate, computeSnapCandidate } from "./window-manager/snap";
import { useWindowManager } from "./window-manager/useWindowManager";
import type {
  SnapCandidate,
  WindowGeometry,
  WindowLayoutEntry,
  WindowRegistration
} from "./window-manager/types";

const WINDOW_STYLE: CSSProperties = {
  position: "fixed",
  overflow: "hidden",
  pointerEvents: "auto",
  isolation: "isolate"
};

const HEADER_STYLE: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: "0.5rem",
  padding: "0.5rem 0.65rem",
  borderBottom: "1px solid hsl(var(--ui-border-1))",
  background: "color-mix(in oklab, hsl(var(--ui-surface-2)) 86%, transparent)",
  cursor: "grab",
  userSelect: "none"
};

const TITLE_STYLE: CSSProperties = {
  margin: 0,
  fontSize: "0.72rem",
  letterSpacing: "0.06em",
  textTransform: "uppercase"
};

const BODY_STYLE: CSSProperties = {
  padding: "0.6rem",
  overflow: "auto",
  maxHeight: "calc(100dvh - 6rem)"
};

const BUTTON_STYLE: CSSProperties = {
  border: "1px solid hsl(var(--ui-border-2))",
  borderRadius: "8px",
  background: "hsl(var(--ui-surface-2))",
  color: "hsl(var(--ui-text-1))",
  fontSize: "0.68rem",
  padding: "0.2rem 0.45rem",
  cursor: "pointer"
};

const RESIZE_HANDLE_STYLE: CSSProperties = {
  position: "absolute",
  right: 0,
  bottom: 0,
  width: "18px",
  height: "18px",
  cursor: "nwse-resize",
  background:
    "linear-gradient(135deg, transparent 0%, transparent 45%, color-mix(in oklab, hsl(var(--ui-border-2)) 55%, transparent) 45%, color-mix(in oklab, hsl(var(--ui-border-2)) 55%, transparent) 55%, transparent 55%)"
};

interface FloatingWindowProps {
  readonly id: string;
  readonly title: string;
  readonly children: ReactNode;
  readonly defaultState?: Partial<WindowLayoutEntry>;
  readonly minWidth?: number;
  readonly minHeight?: number;
  readonly singleInstance?: boolean;
  readonly resizable?: boolean;
  readonly hideCloseButton?: boolean;
  readonly frameStyle?: "LIQUID_GLASS" | "GOLD_NOIR_TERMINAL" | "GRAPHITE_PRISM_ISO";
  readonly frameSurface?: "controlRoomHud" | "pitchSurface" | "kpiWidget";
  readonly framePerfProfile?: "quality" | "perf";
}

type InteractionMode = "drag" | "resize";

interface InteractionState {
  readonly mode: InteractionMode;
  readonly pointerId: number;
  readonly startPointerX: number;
  readonly startPointerY: number;
  readonly startRect: WindowGeometry;
  candidate: SnapCandidate | null;
}

function toGeometry(entry: WindowLayoutEntry): WindowGeometry {
  return {
    x: entry.x,
    y: entry.y,
    w: entry.w,
    h: entry.h
  };
}

function buildConstraintOptions(minWidth?: number, minHeight?: number) {
  const options: { minWidth?: number; minHeight?: number } = {};

  if (minWidth !== undefined) {
    options.minWidth = minWidth;
  }

  if (minHeight !== undefined) {
    options.minHeight = minHeight;
  }

  return options;
}

export function FloatingWindow({
  id,
  title,
  children,
  defaultState,
  minWidth,
  minHeight,
  singleInstance = true,
  resizable = true,
  hideCloseButton = false,
  frameStyle = "GRAPHITE_PRISM_ISO",
  frameSurface = "controlRoomHud",
  framePerfProfile = "quality"
}: FloatingWindowProps) {
  const {
    state,
    registerWindow,
    unregisterWindow,
    bringToFront,
    commitWindowState,
    setWindowCollapsed,
    setWindowVisible,
    setSnapPreview,
    clearSnapPreview
  } = useWindowManager();

  const entry = state.windows[id];
  const [draftEntry, setDraftEntry] = useState<WindowLayoutEntry | null>(entry ?? null);
  const interactionRef = useRef<InteractionState | null>(null);
  const [isInteracting, setIsInteracting] = useState(false);
  const constraintOptions = useMemo(
    () => buildConstraintOptions(minWidth, minHeight),
    [minHeight, minWidth]
  );
  const frame = useMemo(
    () =>
      luxury.applyFrameToSubtree({
        style: frameStyle,
        surface: frameSurface,
        perfProfile: framePerfProfile
      }),
    [framePerfProfile, frameStyle, frameSurface]
  );

  useEffect(() => {
    const registration: WindowRegistration = {
      id,
      title,
      singleInstance,
      ...(defaultState !== undefined ? { defaultState } : {}),
      ...(minWidth !== undefined ? { minWidth } : {}),
      ...(minHeight !== undefined ? { minHeight } : {})
    };

    registerWindow(registration);

    return () => {
      unregisterWindow(id);
    };
  }, [defaultState, id, minHeight, minWidth, registerWindow, singleInstance, title, unregisterWindow]);

  useEffect(() => {
    if (!entry) {
      return;
    }

    if (!isInteracting) {
      setDraftEntry(entry);
    }
  }, [entry, isInteracting]);

  const finishInteraction = useCallback(
    (pointerId?: number) => {
      if (pointerId !== undefined && interactionRef.current && interactionRef.current.pointerId !== pointerId) {
        return;
      }

      const interaction = interactionRef.current;
      interactionRef.current = null;
      setIsInteracting(false);

      if (!entry || !draftEntry) {
        clearSnapPreview();
        return;
      }

      const activeGeometry = toGeometry(draftEntry);
      const finalGeometry = interaction?.candidate
        ? applySnapCandidate(interaction.candidate, state.viewport, constraintOptions)
        : clampGeometry(activeGeometry, state.viewport, constraintOptions);

      commitWindowState(id, finalGeometry);
      clearSnapPreview();
    },
    [clearSnapPreview, commitWindowState, draftEntry, entry, id, minHeight, minWidth, state.viewport]
  );

  const onPointerMove = useCallback(
    (event: PointerEvent) => {
      const interaction = interactionRef.current;
      if (!interaction || !entry) {
        return;
      }

      if (event.pointerId !== interaction.pointerId) {
        return;
      }

      const deltaX = event.clientX - interaction.startPointerX;
      const deltaY = event.clientY - interaction.startPointerY;

      if (interaction.mode === "resize") {
        const resized = clampGeometry(
          {
            x: interaction.startRect.x,
            y: interaction.startRect.y,
            w: interaction.startRect.w + deltaX,
            h: interaction.startRect.h + deltaY
          },
          state.viewport,
          constraintOptions
        );

        setDraftEntry((previous) => (previous ? { ...previous, ...resized } : previous));
        interaction.candidate = null;
        setSnapPreview(null);
        return;
      }

      const moved: WindowGeometry = {
        x: interaction.startRect.x + deltaX,
        y: interaction.startRect.y + deltaY,
        w: interaction.startRect.w,
        h: interaction.startRect.h
      };

      setDraftEntry((previous) => (previous ? { ...previous, ...moved } : previous));

      const candidate = computeSnapCandidate({
        rect: moved,
        pointer: {
          x: event.clientX,
          y: event.clientY
        },
        viewport: state.viewport,
        disableSnap: event.altKey,
        forceGrid: event.shiftKey
      });

      interaction.candidate = candidate;
      setSnapPreview(candidate);
    },
    [constraintOptions, entry, setSnapPreview, state.viewport]
  );

  const onPointerUp = useCallback(
    (event: PointerEvent) => {
      finishInteraction(event.pointerId);
    },
    [finishInteraction]
  );

  useEffect(() => {
    if (!isInteracting) {
      return;
    }

    const cancel = (event: PointerEvent) => {
      finishInteraction(event.pointerId);
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
    window.addEventListener("pointercancel", cancel);

    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      window.removeEventListener("pointercancel", cancel);
    };
  }, [finishInteraction, isInteracting, onPointerMove, onPointerUp]);

  const startInteraction = useCallback(
    (event: ReactPointerEvent<HTMLElement>, mode: InteractionMode) => {
      if (!entry || !draftEntry) {
        return;
      }

      if (event.button !== 0) {
        return;
      }

      event.preventDefault();
      event.stopPropagation();

      bringToFront(id);
      setIsInteracting(true);

      interactionRef.current = {
        mode,
        pointerId: event.pointerId,
        startPointerX: event.clientX,
        startPointerY: event.clientY,
        startRect: toGeometry(draftEntry),
        candidate: null
      };

      event.currentTarget.setPointerCapture(event.pointerId);
    },
    [bringToFront, draftEntry, entry, id]
  );

  const onClose = useCallback(() => {
    setWindowVisible(id, false);
  }, [id, setWindowVisible]);

  const onToggleCollapsed = useCallback(() => {
    if (!entry) {
      return;
    }

    setWindowCollapsed(id, !entry.collapsed);
  }, [entry, id, setWindowCollapsed]);

  const activeEntry = draftEntry ?? entry;

  if (!activeEntry || !entry || !entry.visible) {
    return null;
  }

  return (
    <section
      aria-label={title}
      onPointerDown={() => bringToFront(id)}
      className={frame.wrapper.className}
      {...frame.wrapper.attrs}
      style={{
        ...WINDOW_STYLE,
        ...frame.wrapper.style,
        left: `${activeEntry.x}px`,
        top: `${activeEntry.y}px`,
        width: `${activeEntry.w}px`,
        zIndex: activeEntry.z,
        userSelect: isInteracting ? "none" : "auto"
      }}
      data-window-id={id}
    >
      <header style={{ ...HEADER_STYLE, cursor: isInteracting ? "grabbing" : "grab" }}>
        <div style={{ flex: 1 }} onPointerDown={(event) => startInteraction(event, "drag")}>
          <h3 style={TITLE_STYLE}>{title}</h3>
        </div>
        <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
          <button type="button" style={BUTTON_STYLE} onClick={onToggleCollapsed}>
            {entry.collapsed ? "Expand" : "Collapse"}
          </button>
          {hideCloseButton ? null : (
            <button type="button" style={BUTTON_STYLE} onClick={onClose}>
              Hide
            </button>
          )}
        </div>
      </header>

      {entry.collapsed ? null : (
        <div
          {...frame.contentAttrs}
          style={{
            ...BODY_STYLE,
            height: `${Math.max(activeEntry.h - 52, 60)}px`
          }}
        >
          {children}
        </div>
      )}

      {!entry.collapsed && resizable ? (
        <div role="presentation" style={RESIZE_HANDLE_STYLE} onPointerDown={(event) => startInteraction(event, "resize")} />
      ) : null}
    </section>
  );
}
