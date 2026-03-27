"use client";

import { useEffect, useState } from "react";
import { PitchLayerDevToolsClientOnly } from "./pitch-layer-dev-tools-client-only";

export interface PitchDevConsoleMountProps {
  readonly visible: boolean;
}

const DEV_CONSOLE_STORAGE_KEY = "keystone.pitch.devConsole.enabled";

export function PitchDevConsoleMount({ visible }: PitchDevConsoleMountProps) {
  const [enabled, setEnabled] = useState(visible);

  useEffect(() => {
    if (!visible) {
      setEnabled(false);
      return;
    }

    try {
      const stored = window.localStorage.getItem(DEV_CONSOLE_STORAGE_KEY);
      if (stored === "0") {
        setEnabled(false);
        return;
      }
      if (stored === "1") {
        setEnabled(true);
        return;
      }
    } catch {
      // ignore storage errors
    }

    setEnabled(true);
  }, [visible]);

  const toggle = () => {
    const next = !enabled;
    setEnabled(next);
    try {
      window.localStorage.setItem(DEV_CONSOLE_STORAGE_KEY, next ? "1" : "0");
    } catch {
      // ignore storage errors
    }
  };

  if (!visible) {
    return null;
  }

  return (
    <>
      <button
        type="button"
        onClick={toggle}
        className="fixed bottom-4 right-4 z-[120] rounded-full border border-[rgba(2,111,134,0.34)] bg-[linear-gradient(165deg,rgba(255,255,255,0.92),rgba(236,246,255,0.72))] px-3 py-1.5 text-xs font-semibold text-[color:#0f406a] shadow-[0_12px_24px_rgba(4,18,25,0.18)] backdrop-blur-md transition hover:border-[rgba(2,111,134,0.5)]"
        aria-pressed={enabled}
        aria-label={enabled ? "Deshabilitar consola" : "Habilitar consola"}
      >
        {enabled ? "Consola: ON" : "Consola: OFF"}
      </button>
      <PitchLayerDevToolsClientOnly visible={enabled} />
    </>
  );
}
