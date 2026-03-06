"use client";

import { useEffect, useState, type ReactNode } from "react";
import { reportInternalToolClientOnlyMount } from "./hydration-diagnostics";

export interface InternalToolClientOnlyBoundaryProps {
  readonly componentName: string;
  readonly children: ReactNode;
  readonly fallback?: ReactNode;
  readonly enabled?: boolean;
}

/**
 * Internal tooling policy:
 * form-heavy debug surfaces that can be mutated by external browser agents
 * before hydration must render behind this client-only boundary.
 */
export function InternalToolClientOnlyBoundary({
  componentName,
  children,
  fallback = null,
  enabled = true
}: InternalToolClientOnlyBoundaryProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    setMounted(true);
    reportInternalToolClientOnlyMount({ componentName });
  }, [componentName, enabled]);

  if (!enabled) {
    return <>{children}</>;
  }

  if (!mounted) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

