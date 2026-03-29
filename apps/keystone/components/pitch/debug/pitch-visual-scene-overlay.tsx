"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { useLayerFlags } from "@hitech/ui-kit";

function resolveViewportLabel(width: number): "desktop" | "mobile" {
  return width < 768 ? "mobile" : "desktop";
}

export function PitchVisualSceneOverlay() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { enabledLayers, resolved } = useLayerFlags();
  const [viewportWidth, setViewportWidth] = useState<number>(0);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const onResize = () => {
      setViewportWidth(window.innerWidth);
    };

    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
    };
  }, []);

  const canonicalQuery = useMemo(() => {
    const params = new URLSearchParams(searchParams.toString());
    const ordered = new URLSearchParams();
    const priorityKeys = ["layers", "layerProfile", "motion", "debug"];
    const consumed = new Set<string>();

    for (const key of priorityKeys) {
      consumed.add(key);
      for (const value of params.getAll(key)) {
        ordered.append(key, value);
      }
    }

    for (const key of [...new Set(params.keys())]
      .filter((key) => !consumed.has(key))
      .sort((left, right) => left.localeCompare(right))) {
      for (const value of params.getAll(key)) {
        ordered.append(key, value);
      }
    }

    return ordered.toString();
  }, [searchParams]);

  const viewportLabel = resolveViewportLabel(viewportWidth);
  const scenePath = canonicalQuery.length > 0 ? `${pathname}?${canonicalQuery}` : pathname;

  return (
    <aside
      className="fixed left-4 top-4 z-[2147483639] w-[min(420px,calc(100vw-2rem))] rounded-xl border border-[color:var(--pitch-border)] bg-[color:color-mix(in_oklab,var(--pitch-panel)_88%,transparent)] p-3 text-xs text-[color:var(--pitch-ink)] shadow-[var(--pitch-shadow-sm)] backdrop-blur-sm"
      aria-label="Pitch visual scene overlay"
    >
      <p className="m-0 font-semibold uppercase tracking-[0.1em] text-[color:var(--pitch-muted)]">Visual Scene</p>
      <p className="m-0 mt-1 break-all font-mono text-[11px] leading-relaxed">{scenePath}</p>
      <p className="m-0 mt-2 text-[11px]">
        viewport={viewportLabel} ({viewportWidth || 0}px) source={resolved.source} profile={resolved.profile} layers=
        {enabledLayers.length}
      </p>
    </aside>
  );
}
