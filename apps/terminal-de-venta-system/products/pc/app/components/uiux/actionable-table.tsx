import { DataTable } from "@components/backoffice/data-table";

export function ActionableTable({
  title,
  subtitle,
  columns,
  rows,
  emptyMessage = "No hay pendientes para esta vista."
}: {
  title: string;
  subtitle: string;
  columns: string[];
  rows: Array<Record<string, string | number>>;
  emptyMessage?: string;
}) {
  const hasActionColumn = columns.some((column) => column.toLowerCase().includes("acción") || column.toLowerCase().includes("hacer"));
  const safeColumns = hasActionColumn ? columns : [...columns, "Qué hacer"];
  const safeRows = hasActionColumn ? rows : rows.map((row) => ({ ...row, "Qué hacer": row["Qué hacer"] ?? row.action ?? "Revisar" }));

  return (
    <section className="card" data-prisma-component="ActionableTable" data-action-column={hasActionColumn ? "present" : "auto-added"}>
      <div className="section-head">
        <div>
          <div className="kicker">detalle operativo</div>
          <h2 className="section-title">{title}</h2>
          <div className="section-copy">{subtitle}</div>
        </div>
      </div>
      <DataTable columns={safeColumns} rows={safeRows} emptyMessage={emptyMessage} />
    </section>
  );
}
