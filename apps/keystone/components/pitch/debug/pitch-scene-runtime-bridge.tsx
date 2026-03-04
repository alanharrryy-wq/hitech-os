"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES, useLayerFlags } from "@hitech/ui-kit";
import {
  buildSceneDiagnosticsPayload,
  SCENE_STUDIO_RESPONSE_DIAGNOSTICS,
  isDiagnosticsRequestMessage
} from "../../../lib/scene-studio";

function collectDomLayerAttributes(): Record<string, string> {
  const attributes: Record<string, string> = {};
  const html = document.documentElement;

  for (const attribute of html.getAttributeNames()) {
    if (!attribute.startsWith("data-layer-")) {
      continue;
    }

    const value = html.getAttribute(attribute);
    if (value !== null) {
      attributes[attribute] = value;
    }
  }

  return attributes;
}

function collectMissingLayerAttributes(flags: ReturnType<typeof useLayerFlags>["flags"]): string[] {
  const html = document.documentElement;
  const missing: string[] = [];

  for (const layerId of ALL_LAYERS) {
    if (!flags[layerId]) {
      continue;
    }

    const attr = LAYER_DATA_ATTRIBUTES[layerId];
    if (html.getAttribute(attr) !== "1") {
      missing.push(attr);
    }
  }

  return missing;
}

async function waitForStableDocument(): Promise<void> {
  const html = document.documentElement;
  html.setAttribute("data-scene-ready", "0");

  const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
  if (fonts?.ready) {
    try {
      await fonts.ready;
    } catch {
      // Ignore fonts failure in local dev; deterministic tests still wait for ready marker.
    }
  }

  for (let attempt = 0; attempt < 24; attempt += 1) {
    const animations = typeof document.getAnimations === "function" ? document.getAnimations() : [];
    const running = animations.some((animation) => animation.playState === "running");
    if (!running) {
      break;
    }

    await new Promise<void>((resolve) => {
      window.requestAnimationFrame(() => resolve());
    });
  }

  await new Promise<void>((resolve) => {
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => resolve());
    });
  });

  html.setAttribute("data-scene-ready", "1");
}

export function PitchSceneRuntimeBridge() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { resolved, enabledLayers } = useLayerFlags();
  const [viewportLabel, setViewportLabel] = useState("desktop");

  useEffect(() => {
    void waitForStableDocument();
  }, [pathname, searchParams]);

  useEffect(() => {
    const updateViewport = () => {
      setViewportLabel(window.innerWidth < 768 ? "mobile" : window.innerWidth < 1180 ? "tablet" : "desktop");
    };

    updateViewport();
    window.addEventListener("resize", updateViewport);
    return () => window.removeEventListener("resize", updateViewport);
  }, []);

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) {
        return;
      }

      if (!isDiagnosticsRequestMessage(event.data)) {
        return;
      }

      if (!event.source || typeof (event.source as Window).postMessage !== "function") {
        return;
      }

      const domDataAttributes = collectDomLayerAttributes();
      const missingDataAttributes = collectMissingLayerAttributes(resolved.flags);

      const payload = buildSceneDiagnosticsPayload({
        requestId: event.data.requestId,
        pathname: window.location.pathname,
        search: searchParams.toString(),
        resolved,
        enabledLayerIds: enabledLayers,
        domDataAttributes,
        missingDataAttributes,
        sceneReady: document.documentElement.getAttribute("data-scene-ready"),
        userAgent: navigator.userAgent
      });

      (event.source as Window).postMessage(
        {
          type: SCENE_STUDIO_RESPONSE_DIAGNOSTICS,
          payload
        },
        event.origin
      );
    };

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [enabledLayers, resolved, searchParams]);

  const overlayEnabled =
    process.env["NODE_ENV"] !== "production" &&
    (searchParams.get("sceneOverlay") === "1" || searchParams.get("debug") === "1");

  const overlayText = useMemo(() => {
    return `scene=${pathname}?${searchParams.toString()} source=${resolved.source} profile=${resolved.profile} enabled=${enabledLayers.length} viewport=${viewportLabel}`;
  }, [enabledLayers.length, pathname, resolved.profile, resolved.source, searchParams, viewportLabel]);

  if (!overlayEnabled) {
    return null;
  }

  return (
    <aside
      className="fixed bottom-4 left-1/2 z-[2147483645] w-[min(92vw,980px)] -translate-x-1/2 rounded border border-[color:var(--pitch-border)] bg-[color:color-mix(in_oklab,var(--pitch-panel)_84%,transparent)] px-3 py-2 text-[11px] tracking-[0.04em] text-[color:var(--pitch-ink)] shadow-[var(--pitch-shadow-sm)] backdrop-blur-sm"
      aria-label="Scene runtime overlay"
    >
      {overlayText}
    </aside>
  );
}
