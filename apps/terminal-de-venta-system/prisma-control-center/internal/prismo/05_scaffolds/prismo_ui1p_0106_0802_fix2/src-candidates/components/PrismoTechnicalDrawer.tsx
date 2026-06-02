import React from 'react';
export function PrismoTechnicalDrawer({ open, onClose, plan }: any) {
  if (!open) return null;
  return <aside className="prismo-ui1p-drawer"><button className="close" onClick={onClose}>Cerrar</button><h2>Detalle técnico / Perito</h2><p>Evidencia, memoria, protocolos y trazabilidad bajo demanda.</p><pre>{JSON.stringify(plan?.trace ?? plan, null, 2)}</pre></aside>;
}
