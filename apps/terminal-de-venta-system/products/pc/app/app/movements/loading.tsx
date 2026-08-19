export default function Loading() {
  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: 32 }}>
      <section style={{ width: "min(680px, 100%)", padding: 24 }} aria-busy="true" aria-live="polite">
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900 }}>movimientos</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 28 }}>Cargando movimientos</h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>Estamos preparando las entradas, salidas y ajustes disponibles.</p>
      </section>
    </main>
  );
}
