import React from 'react';
// Blueprint: replace native select with Radix Select in production if Radix exists in target app.
export type PrismoLiquidOption = { id: string; label: string; description?: string; icon?: React.ReactNode };
export function PrismoLiquidSelect({ label, value, options, onChange, hint }: { label: string; value: string; options: PrismoLiquidOption[]; onChange: (v:string)=>void; hint?: string }) {
  return (
    <label className="prismo-liquid-select" data-prismo-fx="radix-ready">
      <span className="prismo-liquid-select__label">{label}</span>
      <select className="prismo-liquid-select__control" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
      </select>
      {hint ? <small className="prismo-liquid-select__hint">{hint}</small> : null}
    </label>
  );
}
