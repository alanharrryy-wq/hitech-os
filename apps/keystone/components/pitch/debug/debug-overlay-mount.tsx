"use client";

import dynamic from "next/dynamic";
import { isPitchDebugOverlayEnabled } from "./overlay-gate";

const DebugOverlayClient = dynamic(
  () => import("./debug-overlay-client").then((module) => module.DebugOverlayClient),
  { ssr: false }
);

export function DebugOverlayMount() {
  if (!isPitchDebugOverlayEnabled()) {
    return null;
  }

  return <DebugOverlayClient />;
}
