import React from 'react';

export function OpsTable({ columns, rows }: { columns: string[]; rows: string[][] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-white/10 bg-black/20">
      <table className="min-w-full text-left text-sm text-white/85">
        <thead className="bg-white/5 text-white/60">
          <tr>{columns.map((c) => <th key={c} className="px-3 py-2 font-medium">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-white/5 align-top">
              {row.map((cell, j) => <td key={j} className="px-3 py-2">{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
