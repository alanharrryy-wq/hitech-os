export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <section className="empty-state">
      <div className="empty-state-badge">sin bronca nueva</div>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <div className="subtle">{description}</div>
    </section>
  );
}
