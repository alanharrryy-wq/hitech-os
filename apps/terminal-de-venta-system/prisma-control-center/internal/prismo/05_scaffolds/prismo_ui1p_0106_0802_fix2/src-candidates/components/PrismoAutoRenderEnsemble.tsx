import React, { useMemo } from 'react';
import { PrismoRenderBlockHost } from './PrismoRenderBlockHost';

type RenderPlan = {
  hero?: any;
  blocks?: any[];
  [key: string]: any;
};

function stableBlockId(block: any, index: number): string {
  const raw = [
    block?.id,
    block?.type,
    block?.title,
    block?.summary,
    index
  ].filter(Boolean).join('|');

  return raw
    .toLowerCase()
    .replace(/[^a-z0-9|_-]+/g, '-')
    .slice(0, 120) || `prismo-block-${index}`;
}

export function PrismoAutoRenderEnsemble({ renderPlan, onOpenDetail }: { renderPlan: RenderPlan; onOpenDetail?: () => void }) {
  const normalizedPlan = useMemo(() => {
    const blocks = Array.isArray(renderPlan?.blocks) ? renderPlan.blocks : [];
    const ordered = [...blocks]
      .map((block, index) => ({ ...block, id: block?.id ?? stableBlockId(block, index) }))
      .sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0));

    return {
      ...renderPlan,
      blocks: ordered,
      autoRender: true
    };
  }, [renderPlan]);

  return (
    <section className="prismo-auto-render-ensemble prismo-preset-refrigerant-emerald-theater" data-auto-render="ensemble">
      <PrismoRenderBlockHost plan={normalizedPlan} onOpenDetail={onOpenDetail} />
    </section>
  );
}
