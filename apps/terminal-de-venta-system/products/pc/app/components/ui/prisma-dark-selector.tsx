"use client";

import { useEffect } from "react";

const STORAGE_KEY = "prisma.pc.skin";
const FORCED_SKIN = "light" as const;

function applySkin() {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.prismaSkin = FORCED_SKIN;
  root.dataset.prismaSurface = "pc-backoffice";
  root.dataset.theme = "prisma-light";
  root.dataset.prismaSkinPreference = FORCED_SKIN;
}

export function PrismaDarkSelector() {
  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, FORCED_SKIN);
    applySkin();
  }, []);

  return null;
}
