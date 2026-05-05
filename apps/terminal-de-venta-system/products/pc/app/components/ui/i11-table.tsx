type TableProps = {
  columns: string[];
  rows: Array<Array<string | number | null | undefined>>;
};

export function I11Table({ columns, rows }: TableProps) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-black/20">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm text-white/80">
          <thead className="bg-white/5 text-xs uppercase tracking-wide text-white/55">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-4 py-3 font-medium">{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className="border-t border-white/5 align-top">
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="px-4 py-3">{cell ?? '—'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
