"use client";

import { useEffect, useState } from "react";

type PrismaPayload = {
  type?: string;
  surface?: string;
  recipeName?: string;
  recipe?: string;
  score?: number | { overall?: number; [key: string]: unknown };
  cssVars?: Record<string, string>;
};

const EVENTS_URL = "http://127.0.0.1:4177/events";

function scoreValue(score: PrismaPayload["score"]): string {
  if (typeof score === "number") return String(score);
  if (score && typeof score.overall === "number") return String(score.overall);
  return "";
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
}

export function PosLiveBinding() {
  const [status, setStatus] = useState("idle");
  const [recipe, setRecipe] = useState("sin receta");
  const [score, setScore] = useState("");

  useEffect(() => {
    let source: EventSource | null = null;
    let closed = false;

    document.documentElement.dataset.prismaLive = "true";
    document.documentElement.dataset.prismaPosLiveBinding = "00T";
    document.documentElement.dataset.prismaPosLiveStatus = "booting";

    try {
      source = new EventSource(EVENTS_URL);

      source.onopen = () => {
        if (closed) return;
        setStatus("connected");
        document.documentElement.dataset.prismaPosLiveStatus = "connected";
      };

      source.onerror = () => {
        if (closed) return;
        setStatus("error");
        document.documentElement.dataset.prismaPosLiveStatus = "error";
      };

      source.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as PrismaPayload;
          if (payload.type !== "prisma.visual.controls") return;
          if (payload.surface && payload.surface !== "tablet_pos") return;

          applyPayload(payload);
          setStatus("connected");
          setRecipe(payload.recipeName || payload.recipe || "sin receta");
          setScore(scoreValue(payload.score));
        } catch (error) {
          setStatus("payload_error");
          document.documentElement.dataset.prismaPosLiveStatus = "payload_error";
          console.warn("[PRISMA 00T] payload error", error);
        }
      };
    } catch (error) {
      setStatus("error");
      document.documentElement.dataset.prismaPosLiveStatus = "error";
      console.warn("[PRISMA 00T] EventSource error", error);
    }

    return () => {
      closed = true;
      if (source) source.close();
    };
  }, []);

  return (
    <div
      data-prisma-pos-live-badge="00T"
      data-prisma-layer="debug"
      style={{
        position: "fixed",
        right: 12,
        bottom: 12,
        zIndex: 20,
        display: "grid",
        gap: 2,
        minWidth: 160,
        maxWidth: 240,
        padding: "8px 10px",
        borderRadius: 14,
        border: "1px solid rgba(139,236,255,.35)",
        background: "rgba(8,14,28,.66)",
        color: "#f3fbff",
        fontSize: 11,
        lineHeight: 1.2,
        pointerEvents: "none",
        boxShadow: "0 12px 28px rgba(0,0,0,.28)",
        backdropFilter: "blur(8px)",
      }}
      title={`PRISMA 00T Live POS Binding: ${status}`}
    >
      <strong style={{ letterSpacing: ".08em" }}>00T Live</strong>
      <span>{status}</span>
      <small style={{ opacity: .72 }}>{recipe}{score ? ` · ${score}` : ""}</small>
    </div>
  );
}

export default PosLiveBinding;
