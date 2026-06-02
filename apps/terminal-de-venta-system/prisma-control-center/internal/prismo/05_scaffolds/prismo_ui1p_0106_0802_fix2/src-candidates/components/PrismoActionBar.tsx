import React from 'react';
export function PrismoActionBar({actions=[]}:any){return <div className="prismo-ui1p-actionbar">{actions.map((a:any)=><button key={a.id}>{a.label}</button>)}</div>}
