import React from 'react';
export function PrismoResizableTheater({ composer, theater, detail }: { composer: React.ReactNode; theater: React.ReactNode; detail?: React.ReactNode }) {
  return <div className="prismo-resizable-theater" data-prismo-fx="resizable-panels-ready">
    <aside className="prismo-resizable-theater__composer">{composer}</aside>
    <main className="prismo-resizable-theater__stage">{theater}</main>
    {detail ? <section className="prismo-resizable-theater__detail">{detail}</section> : null}
  </div>;
}
