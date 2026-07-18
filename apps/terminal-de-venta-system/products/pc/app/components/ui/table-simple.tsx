export function TableSimple({
  columns,
  rows,
  emptyMessage = "No hay filas para mostrar en esta lectura."
}: {
  columns: readonly string[];
  rows: Array<Record<string, string | number>>;
  emptyMessage?: string;
}) {
  return (
    <div
      className="table-wrap pc-foundation-table"
      data-prisma-component="TableSimple"
      data-row-count={rows.length}
      data-state={rows.length > 0 ? "populated" : "empty"}
    >
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column} scope="col">{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length > 0 ? (
            rows.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={column}>{String(row[column] ?? "")}</td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td className="pc-foundation-table__empty" colSpan={Math.max(columns.length, 1)}>
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
