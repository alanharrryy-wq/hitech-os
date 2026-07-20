export default function Loading() {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 32 }}>
      <section style={{ width: "min(720px, 100%)", padding: 28 }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 800 }}>PRISMA PC</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 32 }}>Preparando pantalla</h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>La interfaz está cargando sin bloquear la operación ni mostrar datos inventados.</p>
      </section>
    </main>
  );
}
