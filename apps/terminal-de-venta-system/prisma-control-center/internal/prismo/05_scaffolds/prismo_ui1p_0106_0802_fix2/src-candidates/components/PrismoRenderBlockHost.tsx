import React from 'react';

function stableBlockKey(block: any, index: number): string {
  return [
    block?.id,
    block?.type,
    block?.title,
    index
  ].filter(Boolean).join('|').toLowerCase().replace(/[^a-z0-9|_-]+/g, '-');
}

function stableItemKey(item: any, index: number): string {
  if (typeof item === 'string') return `${item}-${index}`;
  return [
    item?.id,
    item?.key,
    item?.label,
    item?.title,
    item?.type,
    index
  ].filter(Boolean).join('|').toLowerCase().replace(/[^a-z0-9|_-]+/g, '-');
}

export function PrismoRenderBlockHost({ plan, onOpenDetail }: any) {
  const blocks = Array.isArray(plan?.blocks) ? plan.blocks : [];
  return (
    <div className="prismo-ui1p-block-host">
      {(plan?.hero || blocks.length === 0) && (
        <section className="prismo-ui1p-hero">
          <p className="eyebrow">Adaptive Intelligence Theater</p>
          <h1>{plan?.hero?.title ?? 'PRISMO listo para responder'}</h1>
          <p>{plan?.hero?.summary ?? 'Elige intención, dominio y lente; PRISMO decide la composición visual automáticamente.'}</p>
          <button onClick={onOpenDetail}>Ver detalle técnico</button>
        </section>
      )}
      <div className="prismo-ui1p-grid">
        {blocks.map((block: any, index: number) => (
          <RenderBlock key={stableBlockKey(block, index)} block={block} onOpenDetail={onOpenDetail} />
        ))}
      </div>
    </div>
  );
}

function RenderBlock({ block, onOpenDetail }: any) {
  const items = Array.isArray(block?.payload?.items) ? block.payload.items : [];
  return (
    <article className={`prismo-ui1p-card block-${block.type}`} data-render-block={block.type}>
      <div className="card-top">
        <span>{block.type?.replaceAll('_', ' ')}</span>
        <strong>{Math.round((block.confidence ?? 0.86) * 100)}%</strong>
      </div>
      <h3>{block.title}</h3>
      <p>{block.summary}</p>
      {items.length > 0 && (
        <ul>
          {items.slice(0, 5).map((item: any, index: number) => (
            <li key={stableItemKey(item, index)}>{typeof item === 'string' ? item : item.label ?? item.title ?? JSON.stringify(item)}</li>
          ))}
        </ul>
      )}
      <div className="card-actions">
        <button onClick={onOpenDetail}>Detalle</button>
        <button type="button">Usar</button>
      </div>
    </article>
  );
}
