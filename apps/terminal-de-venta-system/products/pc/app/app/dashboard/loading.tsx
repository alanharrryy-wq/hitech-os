export default function LoadingHoy() {
  return (
    <section aria-label="Preparando Hoy" data-prisma-screen="hoy-loading" style={{ display: "grid", gap: "1rem", padding: "1rem" }}>
      <div className="hero" style={{ minHeight: 220 }}>
        <p className="kicker">HOY</p>
        <h1 className="hero-title">Preparando operación</h1>
        <p className="hero-copy">PRISMA está revisando pendientes, ventas, inventario y sincronización.</p>
      </div>
    </section>
  );
}
