import { EmptyState } from "./empty-state";
import { StatusBadge } from "./status-badge";

export function DataTable({
  columns,
  rows,
  emptyMessage
}: {
  columns: string[];
  rows: Array<Record<string, string | number>>;
  emptyMessage: string;
}) {
  if (rows.length === 0) {
    return <EmptyState title="Aún no hay eventos consolidados." description={emptyMessage} />;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => {
                const value = row[column] ?? "";
                const printable = String(value);
                const isStatus = ["Estado", "Prioridad"].includes(column);
                return <td key={column}>{isStatus ? <StatusBadge value={printable} /> : printable}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
