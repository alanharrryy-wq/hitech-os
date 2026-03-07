'use client';

import * as React from 'react';

type HydrationDiagnosticsOptions = {
  componentName: string;
  strategy: string;
};

function diagnosticsEnabled(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  const searchParams = new URLSearchParams(window.location.search);
  const queryEnabled = searchParams.get('hydrationDiag') === '1';
  const envEnabled = process.env.NEXT_PUBLIC_INTERNAL_TOOL_HYDRATION_DIAGNOSTICS === '1';

  return queryEnabled || envEnabled;
}

export function useInternalToolHydrationDiagnostics({
  componentName,
  strategy,
}: HydrationDiagnosticsOptions): void {
  React.useEffect(() => {
    if (!diagnosticsEnabled()) {
      return;
    }

    const route = typeof window !== 'undefined' ? window.location.pathname : 'unknown';
    const timestamp = new Date().toISOString();

    console.info('[hydration-diag]', {
      componentName,
      route,
      strategy,
      timestamp,
    });
  }, [componentName, strategy]);
}
