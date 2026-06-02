import React from 'react';
export function PrismoMotionSceneOrchestrator({ children, stage = 'ready' }: { children: React.ReactNode; stage?: string }) {
  return <div className="prismo-motion-scene" data-stage={stage} data-prismo-fx="motion-gsap-ready">{children}</div>;
}
