import { EmptyState } from "./empty-state";
import { StatusBadge } from "./status-badge";

function columnKey(column: string, index: number) {
  return ["column", index, column].join("-");
}

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
            {columns.map((column, columnIndex) => (
              <th key={columnKey(column, columnIndex)}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column, columnIndex) => {
                const value = row[column] ?? "";
                const printable = String(value);
                const isStatus = ["Estado", "Prioridad"].includes(column);
                return <td key={columnKey(column, columnIndex)}>{isStatus ? <StatusBadge value={printable} /> : printable}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
