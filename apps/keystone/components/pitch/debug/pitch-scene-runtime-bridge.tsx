"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { ALL_LAYERS, LAYER_DATA_ATTRIBUTES, useLayerFlags } from "@hitech/ui-kit";
import {
  buildSceneDiagnosticsPayload,
  isAllowedSceneStudioOrigin,
  SCENE_STUDIO_RESPONSE_DIAGNOSTICS,
  isDiagnosticsRequestMessage
} from "../../../lib/scene-studio";
import {
  DEV_CONSOLE_DIAGNOSTICS_EVENT,
  DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT
} from "../../dev-console/dev-console-events";
import { dispatchConsoleEvent, registerConsoleEventListener } from "../../dev-console/console-core/console-core-events";

export const BRIDGE_HEARTBEAT_MS = 5000;
const BRIDGE_MIN_PUBLISH_INTERVAL_MS = 450;

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
      // ignore font readiness failures in local dev
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
  const [, setViewportLabel] = useState("desktop");
  const lastPublishRef = useRef(0);
  const search = searchParams.toString();

  useEffect(() => {
    void waitForStableDocument();
  }, [pathname, search]);

  useEffect(() => {
    const updateViewport = () => {
      setViewportLabel(window.innerWidth < 768 ? "mobile" : window.innerWidth < 1180 ? "tablet" : "desktop");
    };

    updateViewport();
    window.addEventListener("resize", updateViewport);

    return () => {
      window.removeEventListener("resize", updateViewport);
    };
  }, []);

  const publishDiagnostics = useCallback(
    ({
      requestId,
      replyTarget,
      replyOrigin,
      force
    }: {
      requestId: string;
      replyTarget?: Window | null;
      replyOrigin?: string;
      force?: boolean;
    }) => {
      const now = Date.now();
      if (!force && now - lastPublishRef.current < BRIDGE_MIN_PUBLISH_INTERVAL_MS) {
        return;
      }
      lastPublishRef.current = now;

      const domDataAttributes = collectDomLayerAttributes();
      const missingDataAttributes = collectMissingLayerAttributes(resolved.flags);

      const payload = buildSceneDiagnosticsPayload({
        requestId,
        pathname: window.location.pathname,
        search,
        resolved,
        enabledLayerIds: enabledLayers,
        domDataAttributes,
        missingDataAttributes,
        sceneReady: document.documentElement.getAttribute("data-scene-ready"),
        userAgent: navigator.userAgent
      });

      dispatchConsoleEvent(DEV_CONSOLE_DIAGNOSTICS_EVENT, payload);

      if (replyTarget && typeof replyTarget.postMessage === "function") {
        const targetOrigin = replyOrigin && isAllowedSceneStudioOrigin(replyOrigin) ? replyOrigin : window.location.origin;
        replyTarget.postMessage(
          {
            type: SCENE_STUDIO_RESPONSE_DIAGNOSTICS,
            payload
          },
          targetOrigin
        );
      }

    },
    [enabledLayers, resolved, search]
  );

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      if (!isAllowedSceneStudioOrigin(event.origin)) {
        return;
      }

      if (!isDiagnosticsRequestMessage(event.data)) {
        return;
      }

      const replyTarget = event.source && typeof (event.source as Window).postMessage === "function"
        ? (event.source as Window)
        : window;
      publishDiagnostics({
        requestId: event.data.requestId,
        replyTarget,
        replyOrigin: event.origin,
        force: true
      });
    };

    const onDiagnosticsRequestEvent = (event: Event) => {
      const detail = (event as CustomEvent<{ requestId?: string } | undefined>).detail;
      const requestId = detail?.requestId ?? `bridge:event:${Date.now()}`;
      publishDiagnostics({
        requestId,
        force: true
      });
    };

    publishDiagnostics({
      requestId: `bridge:initial:${Date.now()}`,
      force: true
    });

    const heartbeat = window.setInterval(() => {
      publishDiagnostics({
        requestId: `bridge:heartbeat:${Date.now()}`
      });
    }, BRIDGE_HEARTBEAT_MS);

    window.addEventListener("message", onMessage);
    const disposeRequestListener = registerConsoleEventListener(
      DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT,
      onDiagnosticsRequestEvent as EventListener
    );

    return () => {
      window.clearInterval(heartbeat);
      window.removeEventListener("message", onMessage);
      disposeRequestListener();
    };
  }, [publishDiagnostics]);

  return null;
}
