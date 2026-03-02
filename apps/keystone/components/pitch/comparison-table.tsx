import {
  GlassCard,
  InsetPanel,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  cn
} from "@hitech/ui-kit";

export interface ComparisonTableProps {
  readonly headers: readonly string[];
  readonly rows: ReadonlyArray<readonly string[]>;
  readonly className?: string;
}

export function ComparisonTable({ headers, rows, className }: ComparisonTableProps) {
  return (
    <GlassCard className={cn("p-2", className)} tone="default" backdrop="off">
      <InsetPanel title="Comparación" description="Modelo vs Múltiplo, Riesgo y Escalabilidad">
        <div className="overflow-x-auto">
          <Table className="min-w-[32rem]">
            <TableHead>
              <TableRow>
                {headers.map((header) => (
                  <TableHeaderCell key={header}>{header}</TableHeaderCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <TableCell key={`${rowIndex}:${cellIndex}`} className="align-top">
                      {cell}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
