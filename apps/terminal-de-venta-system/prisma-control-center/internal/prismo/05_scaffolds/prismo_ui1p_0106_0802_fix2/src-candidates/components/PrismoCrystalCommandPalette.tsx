import React, { useMemo, useState } from 'react';
export type CommandItem = { id: string; label: string; group?: string; payload?: unknown };
export function PrismoCrystalCommandPalette({ items = [], onPick }: { items?: CommandItem[]; onPick?: (item: CommandItem)=>void }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => items.filter((item) => item.label.toLowerCase().includes(query.toLowerCase())).slice(0, 12), [items, query]);
  return (
    <div className="prismo-command-palette" data-prismo-fx="cmdk-ready">
      <button className="prismo-command-palette__trigger" onClick={() => setOpen(true)}>Comandos rápidos</button>
      {open ? <div className="prismo-command-palette__overlay" role="dialog" aria-label="Comandos PRISMO">
        <div className="prismo-command-palette__shell">
          <input autoFocus placeholder="Buscar protocolo, memoria, evidencia o pregunta…" value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === 'Escape') setOpen(false); }} />
          <div className="prismo-command-palette__items">
            {filtered.map((item) => <button key={item.id} onClick={() => { onPick?.(item); setOpen(false); }}><span>{item.label}</span><small>{item.group ?? 'PRISMO'}</small></button>)}
          </div>
          <button className="prismo-command-palette__close" onClick={() => setOpen(false)}>Cerrar</button>
        </div>
      </div> : null}
    </div>
  );
}
