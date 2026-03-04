"use client";

import { useEffect } from "react";
import { parseOrThrow } from "@hitech/contracts";
import { BridgeEnvelopeSchema } from "../schemas";
import type { SceneRecorderSnapshot } from "../types";

export interface PreviewBridgeOptions {
  readonly allowedOrigins: readonly string[];
  readonly onSnapshot: (snapshot: SceneRecorderSnapshot) => void;
  readonly onRejected: () => void;
  readonly onOrigin: (origin: string) => void;
}

export function usePreviewBridge(options: PreviewBridgeOptions): void {
  useEffect(() => {
    const allowed = new Set(options.allowedOrigins.filter((origin) => origin.length > 0));

    const handler = (event: MessageEvent<unknown>) => {
      if (!allowed.has(event.origin)) {
        options.onRejected();
        return;
      }

      try {
        const envelope = parseOrThrow(BridgeEnvelopeSchema, event.data, {
          resource: "pitch-engine.preview-bridge",
          operation: "post-message"
        });

        options.onOrigin(event.origin);
        options.onSnapshot(envelope.payload);
      } catch {
        options.onRejected();
      }
    };

    window.addEventListener("message", handler);
    return () => {
      window.removeEventListener("message", handler);
    };
  }, [options]);
}

export function buildBridgeOriginList(extraOrigins: readonly string[]): string[] {
  const origins = new Set<string>();
  if (typeof window !== "undefined") {
    origins.add(window.location.origin);
  }

  for (const origin of extraOrigins) {
    if (origin.trim().length > 0) {
      origins.add(origin.trim());
    }
  }

  return [...origins];
}
