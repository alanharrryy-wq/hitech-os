export function DataStateCard({ title, note }: { title: string; note: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-4">
      <h3 className="text-sm font-semibold text-white">{title}</h3>
      <p className="mt-1 text-xs text-white/70">{note}</p>
    </div>
  );
}
