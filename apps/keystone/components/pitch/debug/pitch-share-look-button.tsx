"use client";

import { useState } from "react";
import { createShareableLayerUrl, useLayerFlags } from "@hitech/ui-kit";

export function PitchShareLookButton() {
  const { resolved } = useLayerFlags();
  const [copied, setCopied] = useState(false);

  if (process.env["NODE_ENV"] === "production" || !resolved.debug) {
    return null;
  }

  const handleShareLook = async () => {
    if (typeof window === "undefined" || typeof navigator === "undefined" || !navigator.clipboard) {
      return;
    }

    const url = createShareableLayerUrl(resolved, {
      origin: window.location.origin,
      pathname: window.location.pathname,
      search: window.location.search
    });

    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  return (
    <button
      type="button"
      className="fixed right-4 top-4 z-[2147483639] rounded-full border border-[color:var(--pitch-border)] bg-[color:color-mix(in_oklab,var(--pitch-panel)_82%,transparent)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-[color:var(--pitch-ink)] shadow-[var(--pitch-shadow-sm)] backdrop-blur-sm"
      onClick={handleShareLook}
      aria-label="Copy Share Look URL"
      data-pitch-share-look
    >
      {copied ? "Copied" : "Share Look"}
    </button>
  );
}
