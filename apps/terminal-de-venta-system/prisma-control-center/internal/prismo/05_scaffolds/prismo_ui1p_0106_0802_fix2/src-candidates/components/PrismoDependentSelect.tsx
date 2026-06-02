import React from 'react';
export function PrismoDependentSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (v:string)=>void }) {
  return <label className="prismo-ui1p-select"><span>{label}</span><select value={value} onChange={(e)=>onChange(e.target.value)}>{options.map((o)=><option key={o} value={o}>{o.replaceAll('_',' ')}</option>)}</select></label>;
}
