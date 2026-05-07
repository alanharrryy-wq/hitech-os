"use client";

import { useEffect, useState } from "react";
import type { PrismaPackshotSkin } from "./pos-packshots";

const FALLBACK_SKIN: PrismaPackshotSkin = "light";

function readResolvedSkin(): PrismaPackshotSkin {
  if (typeof document === "undefined") return FALLBACK_SKIN;
  const skin = document.documentElement.dataset.prismaSkin;
  if (skin === "dark" || skin === "light") return skin;

  if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }

  return FALLBACK_SKIN;
}

export function usePrismaPackshotSkin(): PrismaPackshotSkin {
  const [skin, setSkin] = useState<PrismaPackshotSkin>(FALLBACK_SKIN);

  useEffect(() => {
    const update = () => setSkin(readResolvedSkin());
    update();

    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-prisma-skin", "data-theme"]
    });

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    media.addEventListener("change", update);
    window.addEventListener("storage", update);

    return () => {
      observer.disconnect();
      media.removeEventListener("change", update);
      window.removeEventListener("storage", update);
    };
  }, []);

  return skin;
}
