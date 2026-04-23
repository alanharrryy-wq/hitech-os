import type { ReactNode } from "react";

export function TableSimple({ columns, rows }: { columns: readonly string[]; rows: Array<Record<string, ReactNode>> }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>{columns.map((column) => <td key={column}>{row[column] ?? ""}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
