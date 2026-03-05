"use client";

import type { CSSProperties } from "react";
import { useWindowManager } from "./useWindowManager";

const OVERLAY_STYLE: CSSProperties = {
  position: "fixed",
  borderRadius: "12px",
  border: "1px solid color-mix(in oklab, #02a7ca 50%, white)",
  background: "color-mix(in oklab, #02a7ca 18%, transparent)",
  boxShadow: "inset 0 0 0 1px color-mix(in oklab, #02a7ca 35%, transparent)",
  pointerEvents: "none",
  zIndex: 2147483620
};

export function SnapPreviewOverlay() {
  const { state } = useWindowManager();
  const candidate = state.snapPreview;

  if (!candidate) {
    return null;
  }

  return (
    <div
      aria-hidden="true"
      style={{
        ...OVERLAY_STYLE,
        left: `${candidate.x}px`,
        top: `${candidate.y}px`,
        width: `${candidate.w}px`,
        height: `${candidate.h}px`
      }}
    />
  );
}
