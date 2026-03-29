'use client';

import * as React from 'react';
import { useInternalToolHydrationDiagnostics } from './use-internal-tool-hydration-diagnostics';

type InternalToolClientOnlyBoundaryProps = {
  children: React.ReactNode;
  componentName?: string;
  strategy?: string;
  fallback?: React.ReactNode;
};

export function InternalToolClientOnlyBoundary({
  children,
  componentName = 'InternalToolClientOnlyBoundary',
  strategy = 'narrow-client-only-boundary',
  fallback = null,
}: InternalToolClientOnlyBoundaryProps) {
  const [mounted, setMounted] = React.useState(false);

  useInternalToolHydrationDiagnostics({
    componentName,
    strategy,
  });

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
