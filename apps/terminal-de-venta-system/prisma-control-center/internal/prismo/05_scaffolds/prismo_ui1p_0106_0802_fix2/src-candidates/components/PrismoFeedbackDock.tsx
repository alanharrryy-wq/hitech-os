import React, { useState } from 'react';
export function PrismoFeedbackDock({ onFeedback }: { onFeedback?: (payload: {value: string; note?: string})=>Promise<void>|void }) {
  const [saved, setSaved] = useState<string | null>(null);
  async function send(value: string) { await onFeedback?.({ value }); setSaved(value); window.setTimeout(() => setSaved(null), 2400); }
  return <div className="prismo-feedback-dock" data-prismo-fx="sonner-ready">
    <button onClick={() => send('useful')}>Esto sirvió</button>
    <button onClick={() => send('not_useful')}>Esto no sirvió</button>
    <button onClick={() => send('save_reference')}>Guardar referencia</button>
    {saved ? <output className="prismo-feedback-toast">Feedback guardado: {saved.replaceAll('_',' ')}</output> : null}
  </div>;
}
