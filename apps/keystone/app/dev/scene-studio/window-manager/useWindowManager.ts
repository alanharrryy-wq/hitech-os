"use client";

import { useContext } from "react";
import { WindowManagerContext } from "./WindowManagerProvider";
import type { WindowManagerContextValue } from "./types";

export function useWindowManager(): WindowManagerContextValue {
  const context = useContext(WindowManagerContext);

  if (!context) {
    throw new Error("useWindowManager must be used within a WindowManagerProvider.");
  }

  return context;
}
