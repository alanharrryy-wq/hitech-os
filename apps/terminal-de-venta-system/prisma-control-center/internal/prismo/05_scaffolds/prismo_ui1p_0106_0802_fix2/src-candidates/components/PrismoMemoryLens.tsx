import React from 'react';
export function PrismoMemoryLens({memories=[]}:any){return <div className="prismo-ui1p-memory-lens">{memories.map((m:any)=><span key={m.id}>{m.type}: {m.title}</span>)}</div>}
