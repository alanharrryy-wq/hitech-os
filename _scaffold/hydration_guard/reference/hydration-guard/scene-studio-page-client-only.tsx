'use client';

import * as React from 'react';
import { InternalToolClientOnlyBoundary } from './internal-tool-client-only-boundary';

type SceneStudioPageClientOnlyProps = {
  children: React.ReactNode;
};

export function SceneStudioPageClientOnly({ children }: SceneStudioPageClientOnlyProps) {
  return (
    <InternalToolClientOnlyBoundary
      componentName="SceneStudioPageClientOnly"
      strategy="scene-studio-internal-workspace-boundary"
    >
      {children}
    </InternalToolClientOnlyBoundary>
  );
}
