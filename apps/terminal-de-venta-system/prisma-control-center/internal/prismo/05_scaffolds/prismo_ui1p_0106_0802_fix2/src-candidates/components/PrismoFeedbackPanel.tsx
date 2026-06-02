import React from 'react';

export function PrismoFeedbackPanel({ traceId, onFeedback }: { traceId?: string; onFeedback?: (kind: string) => void }) {
  return (
    <div className="prismo-feedback-panel prismo-preset-action-bar-mint-circuit" data-trace-id={traceId}>
      <span>¿Esto ayudó a decidir?</span>
      <button type="button" onClick={() => onFeedback?.('helpful')}>Esto sirvió</button>
      <button type="button" onClick={() => onFeedback?.('not_helpful')}>No sirvió</button>
      <button type="button" onClick={() => onFeedback?.('save_protocol')}>Guardar protocolo</button>
      <button type="button" onClick={() => onFeedback?.('save_reference')}>Guardar referencia</button>
    </div>
  );
}
