export function confidenceLabel(confidence: string) {
  const labels: Record<string, string> = {
    snapshot_real: 'real',
    audit_real: 'audit',
    movement_damage_real: 'merma',
    outbox_real: 'outbox',
    proxy_movimientos_sale: 'proxy venta',
    proxy_modelo_ticket: 'proxy ticket',
    po_vs_receipt_proxy: 'proxy fill'
  };
  return labels[confidence] ?? confidence;
}

export function formatKpiValue(card: any) {
  if (typeof card.valueMx === 'number') return `$${card.valueMx.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (typeof card.valuePct === 'number') return `${card.valuePct.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;
  if (typeof card.value === 'number') return card.value.toLocaleString('es-MX');
  return '—';
}
