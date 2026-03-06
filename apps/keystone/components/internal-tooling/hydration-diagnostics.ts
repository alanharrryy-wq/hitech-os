"use client";

export interface InternalToolMountDiagnosticInput {
  readonly componentName: string;
}

declare global {
  interface Window {
    __HITECH_INTERNAL_TOOL_HYDRATION_DIAG_SEEN__?: Set<string>;
  }
}

function isDiagnosticsEnabled(): boolean {
  if (process.env["NODE_ENV"] === "production") {
    return false;
  }

  if (process.env["NEXT_PUBLIC_INTERNAL_TOOL_HYDRATION_DIAGNOSTICS"] === "1") {
    return true;
  }

  if (typeof window === "undefined") {
    return false;
  }

  const search = new URLSearchParams(window.location.search);
  return search.get("hydrationDiag") === "1";
}

function getSeenKeys(): Set<string> {
  if (typeof window === "undefined") {
    return new Set<string>();
  }

  if (!(window.__HITECH_INTERNAL_TOOL_HYDRATION_DIAG_SEEN__ instanceof Set)) {
    window.__HITECH_INTERNAL_TOOL_HYDRATION_DIAG_SEEN__ = new Set<string>();
  }

  return window.__HITECH_INTERNAL_TOOL_HYDRATION_DIAG_SEEN__;
}

export function reportInternalToolClientOnlyMount({ componentName }: InternalToolMountDiagnosticInput): void {
  if (typeof window === "undefined") {
    return;
  }

  if (!isDiagnosticsEnabled()) {
    return;
  }

  const route = `${window.location.pathname}${window.location.search}`;
  const key = `${componentName}@${route}`;
  const seenKeys = getSeenKeys();

  if (seenKeys.has(key)) {
    return;
  }

  seenKeys.add(key);
  console.info(
    `[hydration-guard] client-only mount component=${componentName} route=${route} strategy=internal-tool-boundary`
  );
}

