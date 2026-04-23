import { reportContracts } from '@/lib/i10/reporting-data';
import { ReportContractCard } from '@components/ui/report-contract-card';

export default function ContratosReportePage() {
  return (
    <main className="space-y-6">
      <section>
        <h1 className="text-2xl font-semibold text-white">Contratos de reporte</h1>
        <p className="mt-2 max-w-3xl text-sm text-white/70">Aquí se aclara quién produce cada salida, quién la consume y con qué cadencia. Menos interpretación artística, más contrato legible.</p>
      </section>
      <section className="grid gap-4 md:grid-cols-2">
        {reportContracts.map((item) => <ReportContractCard key={item.contract} item={item} />)}
      </section>
      <section className="rounded-xl border border-cyan-400/30 bg-cyan-500/10 p-4 text-sm text-cyan-50">
        Regla: un exportable puede cambiar de diseño visual, pero no debe cambiar contrato de datos sin dejar huella en `PC_I10_REPORT_CONTRACT_MATRIX`.
      </section>
    </main>
  );
}
