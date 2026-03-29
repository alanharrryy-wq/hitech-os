"use client";

import { createContext, useContext, useMemo, useState, type PropsWithChildren } from "react";
import type { PitchSectionContextValue } from "./types";

const PitchSectionContext = createContext<PitchSectionContextValue | null>(null);

export function PitchSectionProvider({ children }: PropsWithChildren) {
  const [activeSectionId, setActiveSectionId] = useState<string | null>(null);

  const value = useMemo<PitchSectionContextValue>(
    () => ({
      activeSectionId,
      setActiveSectionId
    }),
    [activeSectionId]
  );

  return <PitchSectionContext.Provider value={value}>{children}</PitchSectionContext.Provider>;
}

export function usePitchSectionContext() {
  const context = useContext(PitchSectionContext);

  if (!context) {
    throw new Error("usePitchSectionContext must be used within PitchSectionProvider.");
  }

  return context;
}
