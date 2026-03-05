"use client";

import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { createLayerFlagsQueryFromResolved, useLayerFlags } from "@hitech/ui-kit";

const BUTTON_STYLE: CSSProperties = {
  height: 32,
  padding: "0 12px",
  borderRadius: 10,
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-2) / 0.9)",
  cursor: "pointer",
  fontSize: 12
};

const URL_STYLE: CSSProperties = {
  marginTop: 10,
  width: "100%",
  borderRadius: 10,
  border: "1px solid hsl(var(--ui-border-2))",
  background: "hsl(var(--ui-surface-0) / 0.7)",
  color: "hsl(var(--ui-text-1))",
  fontSize: 11,
  padding: "8px 10px"
};

export function PitchShareLookButton() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const layerState = useLayerFlags();
  const resolved = layerState.resolved ?? layerState;
  const [copied, setCopied] = useState(false);
  const [origin, setOrigin] = useState("");

  const sharePath = useMemo(() => {
    const next = createLayerFlagsQueryFromResolved(
      resolved,
      new URLSearchParams(searchParams.toString())
    );
    const query = next.toString();
    return `${pathname}${query ? `?${query}` : ""}`;
  }, [pathname, resolved, searchParams]);

  const shareUrl = useMemo(
    () => (origin ? new URL(sharePath, origin).toString() : sharePath),
    [origin, sharePath]
  );

  useEffect(() => {
    setOrigin(window.location.origin);
  }, []);

  useEffect(() => {
    if (!copied) return;
    const timeout = window.setTimeout(() => setCopied(false), 1200);
    return () => window.clearTimeout(timeout);
  }, [copied]);

  return (
    <div>
      <button
        type="button"
        style={BUTTON_STYLE}
        onClick={() => {
          navigator.clipboard?.writeText(shareUrl).then(
            () => setCopied(true),
            () => setCopied(false)
          );
        }}
      >
        {copied ? "Copied" : "Copy current look URL"}
      </button>
      <input readOnly value={shareUrl} style={URL_STYLE} aria-label="Pitch share look URL" />
    </div>
  );
}
