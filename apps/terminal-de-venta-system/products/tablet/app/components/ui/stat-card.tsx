export function StatCard({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <section className="card">
      <div className="kicker">{label}</div>
      <div className="metric">{value}</div>
      <div className="subtle">{note}</div>
    </section>
  );
}
