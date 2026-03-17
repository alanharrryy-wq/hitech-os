"use client";

import { SCENE_STUDIO_REQUEST_DIAGNOSTICS } from "../../../lib/scene-studio";
import { dispatchConsoleEvent } from "./console-core-events";
import { DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT } from "../dev-console-events";

export type DiagnosticsRequestTarget = "window" | "window+iframe" | "none";

export interface DiagnosticsRequestResult {
  readonly requestId: string;
  readonly requestedAtIso: string;
  readonly target: DiagnosticsRequestTarget;
  readonly postedToWindow: boolean;
  readonly postedToIframe: boolean;
}

export function requestConsoleDiagnostics(): DiagnosticsRequestResult {
  const requestId = `dev-console:${Date.now()}`;
  const requestAtIso = new Date().toISOString();
  const payload = {
    type: SCENE_STUDIO_REQUEST_DIAGNOSTICS,
    requestId
  } as const;

  if (typeof window === "undefined") {
    return {
      requestId,
      requestedAtIso: requestAtIso,
      target: "none",
      postedToWindow: false,
      postedToIframe: false
    };
  }

  const iframe = document.querySelector<HTMLIFrameElement>('iframe[title="Scene preview"]');
  let postedToWindow = false;
  let postedToIframe = false;

  if (typeof window.postMessage === "function") {
    window.postMessage(payload, window.location.origin);
    postedToWindow = true;
  }

  if (
    iframe?.contentWindow &&
    iframe.contentWindow !== window &&
    typeof iframe.contentWindow.postMessage === "function"
  ) {
    iframe.contentWindow.postMessage(payload, window.location.origin);
    postedToIframe = true;
  }

  dispatchConsoleEvent(DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT, {
    requestId,
    origin: "dev-console-context",
    requestedAt: requestAtIso
  });

  const target: DiagnosticsRequestTarget = postedToWindow ? (postedToIframe ? "window+iframe" : "window") : "none";

  return {
    requestId,
    requestedAtIso: requestAtIso,
    target,
    postedToWindow,
    postedToIframe
  };
}
