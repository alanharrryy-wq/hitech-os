import { EmptyState } from "./empty-state";
import { StatusBadge } from "./status-badge";

type DataTableCellValue = string | number | string[] | null | undefined;

type DataTableRow = Record<string, DataTableCellValue> & {
  __rowDetailTitle?: string;
  __rowDetailTone?: "ok" | "warn" | "danger";
  __rowDetailItems?: string[];
  __rowDetailJson?: string;
  __rowActionHref?: string;
  __rowActionLabel?: string;
};

function columnKey(column: string, index: number) {
  return ["column", index, column].join("-");
}

function detailItems(row: DataTableRow) {
  return Array.isArray(row.__rowDetailItems) ? row.__rowDetailItems.filter(Boolean) : [];
}

function detailTone(row: DataTableRow) {
  return row.__rowDetailTone === "danger" || row.__rowDetailTone === "warn" || row.__rowDetailTone === "ok"
    ? row.__rowDetailTone
    : "warn";
}

function renderStatusCell(printable: string, row: DataTableRow) {
  const title = typeof row.__rowDetailTitle === "string" ? row.__rowDetailTitle : "";
  const items = detailItems(row);
  if (!title && !items.length) return <StatusBadge value={printable} />;

  const href = typeof row.__rowActionHref === "string" ? row.__rowActionHref : "";
  const actionLabel = typeof row.__rowActionLabel === "string" ? row.__rowActionLabel : "Abrir detalle";
  const json = typeof row.__rowDetailJson === "string" ? row.__rowDetailJson : "";

  return (
    <details className={`status-detail status-detail-${detailTone(row)}`}>
      <summary>
        <StatusBadge value={printable} />
        <span className="status-detail-trigger">Ver detalle</span>
      </summary>
      <div className="status-detail-panel">
        {title ? <strong>{title}</strong> : null}
        {items.length ? (
          <ul>
            {items.map((item, index) => <li key={`${index}-${item.slice(0, 24)}`}>{item}</li>)}
          </ul>
        ) : null}
        {json ? (
          <details>
            <summary>Payload técnico</summary>
            <pre>{json}</pre>
          </details>
        ) : null}
        {href ? <a href={href}>{actionLabel}</a> : null}
      </div>
    </details>
  );
}

export function DataTable({
  columns,
  rows,
  emptyMessage
}: {
  columns: string[];
  rows: DataTableRow[];
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
                const printable = Array.isArray(value) ? value.join(", ") : String(value);
                const isStatus = ["Estado", "Prioridad"].includes(column);
                return <td key={columnKey(column, columnIndex)}>{isStatus ? renderStatusCell(printable, row) : printable}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
