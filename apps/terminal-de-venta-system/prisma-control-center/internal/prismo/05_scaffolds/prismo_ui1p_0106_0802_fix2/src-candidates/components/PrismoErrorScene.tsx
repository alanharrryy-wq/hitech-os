import React from 'react';
export function PrismoErrorScene({error,onRetry}:any){return <section className="prismo-ui1p-error"><h1>No se pudo renderizar la escena</h1><p>{error}</p><button onClick={onRetry}>Reintentar</button></section>}
