type ContractItem = {
  contract: string;
  producer: string;
  consumer: string;
  cadence: string;
  format: string;
  notes: string;
};

export function ReportContractCard({ item }: { item: ContractItem }) {
  return (
    <article className="rounded-xl border border-white/10 bg-black/20 p-4">
      <div className="text-xs uppercase tracking-wide text-cyan-200/70">{item.contract}</div>
      <div className="mt-3 text-sm text-white/80">Productor: {item.producer}</div>
      <div className="mt-1 text-sm text-white/80">Consumidor: {item.consumer}</div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full border border-white/10 px-2 py-1 text-white/70">{item.cadence}</span>
        <span className="rounded-full border border-white/10 px-2 py-1 text-white/70">{item.format}</span>
      </div>
      <p className="mt-3 text-sm text-white/65">{item.notes}</p>
    </article>
  );
}
