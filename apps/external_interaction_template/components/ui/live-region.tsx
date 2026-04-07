"use client";

import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

export interface LiveRegionProps {
  message?: string | null;
  politeness?: "polite" | "assertive";
  atomic?: boolean;
  clearAfterMs?: number;
  className?: string;
}

export function LiveRegion({
  message,
  politeness = "polite",
  atomic = true,
  clearAfterMs,
  className
}: LiveRegionProps) {
  const [content, setContent] = useState(message ?? "");

  useEffect(() => {
    setContent(message ?? "");
  }, [message]);

  useEffect(() => {
    if (!clearAfterMs || !content) return;
    const handle = window.setTimeout(() => setContent(""), clearAfterMs);
    return () => window.clearTimeout(handle);
  }, [clearAfterMs, content]);

  return (
    <div
      aria-live={politeness}
      aria-atomic={atomic}
      className={cn("sr-only", className)}
    >
      {content}
    </div>
  );
}
