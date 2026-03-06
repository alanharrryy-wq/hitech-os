"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { DevConsoleBindings, DevConsoleFlags, SceneStudioBinding } from "./types";

type DevConsoleContextValue = {
  bindings: DevConsoleBindings;
  setSceneStudioBinding: (binding: SceneStudioBinding | undefined) => void;

  flags: DevConsoleFlags;
  setFlags: React.Dispatch<React.SetStateAction<DevConsoleFlags>>;
  resetFlags: () => void;
};

const DEFAULT_FLAGS: DevConsoleFlags = {
  showGrid: false,
  motionEnabled: true,
  reducedMotion: false,
  showSafeAreas: false,
  showDebugLabels: false
};

const FLAGS_STORAGE_KEY = "keystone.devConsole.flags";

const DevConsoleContext = createContext<DevConsoleContextValue | null>(null);

function readFlags(): DevConsoleFlags {
  if (typeof window === "undefined") return DEFAULT_FLAGS;

  try {
    const raw = localStorage.getItem(FLAGS_STORAGE_KEY);
    if (!raw) return DEFAULT_FLAGS;
    return { ...DEFAULT_FLAGS, ...(JSON.parse(raw) as Partial<DevConsoleFlags>) };
  } catch {
    return DEFAULT_FLAGS;
  }
}

function emitFlags(flags: DevConsoleFlags) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("hitech:dev-console:flags", { detail: flags }));
}

export function DevConsoleProvider({ children }: { children: React.ReactNode }) {
  const [sceneStudioBinding, setSceneStudioBinding] = useState<SceneStudioBinding | undefined>(undefined);
  const [flags, setFlags] = useState<DevConsoleFlags>(() => readFlags());

  useEffect(() => {
    try {
      localStorage.setItem(FLAGS_STORAGE_KEY, JSON.stringify(flags));
    } catch {
      // ignore
    }

    emitFlags(flags);

    if (typeof document !== "undefined") {
      document.documentElement.dataset["devConsoleGrid"] = String(flags.showGrid);
      document.documentElement.dataset["devConsoleMotion"] = String(flags.motionEnabled);
      document.documentElement.dataset["devConsoleReducedMotion"] = String(flags.reducedMotion);
      document.documentElement.dataset["devConsoleSafeAreas"] = String(flags.showSafeAreas);
      document.documentElement.dataset["devConsoleDebugLabels"] = String(flags.showDebugLabels);
    }
  }, [flags]);

  const value = useMemo<DevConsoleContextValue>(
    () => ({
      bindings: sceneStudioBinding ? { sceneStudio: sceneStudioBinding } : {},
      setSceneStudioBinding,
      flags,
      setFlags,
      resetFlags: () => setFlags(DEFAULT_FLAGS)
    }),
    [flags, sceneStudioBinding]
  );

  return <DevConsoleContext.Provider value={value}>{children}</DevConsoleContext.Provider>;
}

export function useDevConsole() {
  const value = useContext(DevConsoleContext);
  if (!value) {
    throw new Error("useDevConsole must be used inside DevConsoleProvider");
  }
  return value;
}

export function DevConsoleSceneStudioBinding(props: SceneStudioBinding) {
  const { setSceneStudioBinding } = useDevConsole();

  useEffect(() => {
    setSceneStudioBinding(props);
    return () => setSceneStudioBinding(undefined);
  }, [props, setSceneStudioBinding]);

  return null;
}
