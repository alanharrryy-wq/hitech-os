"use client";

import { useEffect } from "react";

type ResolvedPrismaPosSkin = "light";

const STORAGE_KEY = "prisma.pos.skin";
const FORCED_SKIN: ResolvedPrismaPosSkin = "light";

function applySkin() {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.prismaSkin = FORCED_SKIN;
  root.dataset.prismaSurface = "tablet-pos";
  root.dataset.theme = "prisma-light";
}

export function PrismaSkinSelector() {
  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, FORCED_SKIN);
    applySkin();
  }, []);

  return null;
}

export function PrismaDarkSelector() {
  return <PrismaSkinSelector />;
}
