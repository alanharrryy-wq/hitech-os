import React from 'react';
export function PrismoEvidenceDrawerVaul({ open, evidence = [], onClose }: { open: boolean; evidence?: any[]; onClose?: ()=>void }) {
  if (!open) return null;
  return <aside className="prismo-evidence-drawer" data-prismo-fx="vaul-ready" role="dialog" aria-label="Evidencia PRISMO">
    <button className="prismo-evidence-drawer__close" onClick={onClose}>Cerrar</button>
    <h2>Evidencia usada</h2>
    <div className="prismo-evidence-drawer__list">{evidence.slice(0, 50).map((item, index) => <article key={item.id ?? index}><strong>{item.title ?? item.type ?? `Evidencia ${index+1}`}</strong><p>{item.summary ?? item.path ?? 'Detalle disponible en trazabilidad.'}</p></article>)}</div>
  </aside>;
}
