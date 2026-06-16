"use client";

import { useEffect, useRef, useState } from "react";

type PrismaPayload = {
  type?: string;
  surface?: string;
  recipeName?: string;
  recipe?: string;
  score?: number | { overall?: number; [key: string]: unknown };
  cssVars?: Record<string, string>;
};


const PRISMA_VISUAL_ROUTE_TRUTH_PACKAGE = "PRISMA_VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM";

function getPrismaRealtimeBaseUrl() {
  if (typeof window === "undefined") return "http://127.0.0.1:4177";
  const protocol = window.location.protocol === "https:" ? "https:" : "http:";
  const host = window.location.hostname || "127.0.0.1";
  return `${protocol}//${host}:4177`;
}

function getPrismaRealtimeEventsUrl() {
  return `${getPrismaRealtimeBaseUrl()}/events`;
}

function getPrismaRealtimeStateUrl() {
  return `${getPrismaRealtimeBaseUrl()}/state`;
}

const PACKAGE_MARKER = "PRISMA_VISUAL_OS_LIVE_STATUS_TRUTH_00ZL";

function scoreValue(score: PrismaPayload["score"]): string {
  if (typeof score === "number") return String(score);
  if (score && typeof score.overall === "number") return String(score.overall);
  return "";
}

function visibleRealtimeStatus(status: string): string {
  switch (status) {
    case "idle":
      return "Realtime en espera";
    case "booting":
      return "Conectando realtime";
    case "connected":
      return "Realtime conectado";
    case "reconnecting":
      return "Reconectando realtime";
    case "payload_error":
      return "Payload visual invalido";
    case "error":
      return "Visual realtime pendiente";
    default:
      return status.replace(/_/g, " ");
  }
}

function isTabletVisualPayload(payload: PrismaPayload | null | undefined): payload is PrismaPayload {
  if (!payload || payload.type !== "prisma.visual.controls") return false;
  if (payload.surface && payload.surface !== "tablet_pos") return false;
  return true;
}

function applyPayload(payload: PrismaPayload) {
  const root = document.documentElement;

  if (payload.cssVars) {
    Object.entries(payload.cssVars).forEach(([key, value]) => {
      if (key.startsWith("--prisma-live-")) {
        root.style.setProperty(key, String(value));
      }
    });
  }

  root.dataset.prismaLive = "true";
  root.dataset.prismaPosLiveBinding = "00T";
  root.dataset.prismaPosLiveStatus = "connected";
  root.dataset.prismaPosLiveRecipe = payload.recipeName || payload.recipe || "";
  root.dataset.prismaPosLiveScore = scoreValue(payload.score);
  root.dataset.prismaVisualSurface = payload.surface || "tablet_pos";
  root.dataset.prismaVisualLiveStatusTruth = PACKAGE_MARKER;
}

export function PosLiveBinding() {
  const [status, setStatus] = useState("idle");
  const [recipe, setRecipe] = useState("Venta local disponible");
  const [score, setScore] = useState("");
  const [showDebugBadge, setShowDebugBadge] = useState(false);
  const hasRecipeRef = useRef(false);

  useEffect(() => {
    let source: EventSource | null = null;
    let closed = false;

    function markStatus(nextStatus: string) {
      if (closed) return;
      setStatus(nextStatus);
      document.documentElement.dataset.prismaPosLiveStatus = nextStatus;
    }

    function consumePayload(payload: PrismaPayload | null | undefined) {
      if (!isTabletVisualPayload(payload)) return false;
      applyPayload(payload);
      hasRecipeRef.current = true;
      markStatus("connected");
      setRecipe(payload.recipeName || payload.recipe || "Venta local disponible");
      setScore(scoreValue(payload.score));
      return true;
    }

    async function hydrateLastState() {
      try {
        const response = await fetch(getPrismaRealtimeStateUrl(), { cache: "no-store" });
        if (!response.ok) return;
        const body = await response.json();
        consumePayload(body?.lastPayload);
      } catch (error) {
        console.warn("[PRISMA 00T] state hydration skipped", error);
      }
    }

    setShowDebugBadge(
      new URLSearchParams(window.location.search).has("prismaLiveDebug") ||
      window.localStorage.getItem("prisma:live-debug") === "1"
    );

    document.documentElement.dataset.prismaLive = "true";
    document.documentElement.dataset.prismaPosLiveBinding = "00T";
    document.documentElement.dataset.prismaPosLiveStatus = "booting";
    document.documentElement.dataset.prismaVisualLiveStatusTruth = PACKAGE_MARKER;

    try {
      source = new EventSource(getPrismaRealtimeEventsUrl());

      source.onopen = () => {
        if (closed) return;
        markStatus("connected");
        void hydrateLastState();
      };

      source.onerror = () => {
        if (closed) return;
        // EventSource can report transient reconnects. Keep the last known recipe visible.
        markStatus(hasRecipeRef.current ? "reconnecting" : "error");
      };

      const handlePayloadEvent = (event: MessageEvent) => {
        try {
          consumePayload(JSON.parse(event.data) as PrismaPayload);
        } catch (error) {
          markStatus("payload_error");
          console.warn("[PRISMA 00T] payload error", error);
        }
      };

      source.addEventListener("prisma.visual.controls", handlePayloadEvent as EventListener);
      source.addEventListener("prisma.visual.status", () => {
        if (!hasRecipeRef.current) markStatus("connected");
      });

      // Keep plain message support for compatibility shims. The realtime server currently emits named events.
      source.onmessage = handlePayloadEvent;

      void hydrateLastState();
    } catch (error) {
      markStatus("error");
      console.warn("[PRISMA 00T] EventSource error", error);
    }

    return () => {
      closed = true;
      if (source) source.close();
    };
  }, []);

  if (!showDebugBadge) return null;

  return (
    <div
      data-prisma-pos-live-badge="00T"
      data-prisma-layer="debug"
      data-prisma-visual-live-status-truth="00ZL"
      style={{
        position: "fixed",
        right: 18,
        bottom: 18,
        zIndex: 10,
        display: "grid",
        gap: 2,
        minWidth: 148,
        maxWidth: 220,
        padding: "7px 10px",
        borderRadius: 18,
        border: "1px solid rgba(127, 178, 255, .34)",
        background: "linear-gradient(135deg, rgba(255,255,255,.68), rgba(229,244,255,.42))",
        color: "#1b477a",
        fontSize: 10,
        lineHeight: 1.2,
        opacity: .82,
        pointerEvents: "none",
        boxShadow: "0 16px 38px rgba(16, 74, 128, .13), inset 0 1px 0 rgba(255,255,255,.72)",
        backdropFilter: "blur(14px) saturate(1.08)",
      }}
      title={`PRISMA 00T Live POS Binding: ${status}`}
    >
      <strong style={{ letterSpacing: ".08em", color: "#0f67d6" }}>PRISMA Tablet POS</strong>
      <span>{visibleRealtimeStatus(status)}</span>
      <small style={{ opacity: .72 }}>{recipe}{score ? ` · ${score}` : ""}</small>
    </div>
  );
}

export default PosLiveBinding;
