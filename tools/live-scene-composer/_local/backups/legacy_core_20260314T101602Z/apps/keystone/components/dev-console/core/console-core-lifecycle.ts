"use client";

import { useEffect, useState } from "react";
import { createConsoleCoreLogger } from "./console-core-logger";

const logger = createConsoleCoreLogger("Lifecycle");
const SINGLETON_MAP: Record<string, boolean> = {};

export function useConsoleCoreSingleton(key: string): boolean {
  const [allowed, setAllowed] = useState(false);

  useEffect(() => {
    if (SINGLETON_MAP[key]) {
      logger.warn("Prevented duplicate console mount", { key });
      setAllowed(false);
      return;
    }

    SINGLETON_MAP[key] = true;
    setAllowed(true);

    return () => {
      SINGLETON_MAP[key] = false;
    };
  }, [key]);

  return allowed;
}
