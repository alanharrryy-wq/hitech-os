export default function Loading() {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#f6f8fc", color: "#172033", padding: 32 }}>
      <section style={{ width: "min(720px, 100%)", border: "1px solid #dbe3ef", borderRadius: 24, background: "white", padding: 28, boxShadow: "0 18px 50px rgba(17, 24, 39, .08)" }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 800, color: "#2563eb" }}>PRISMA PC</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 32 }}>Preparando pantalla</h1>
        <p style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>La interfaz está cargando sin bloquear la operación ni mostrar datos inventados.</p>
      </section>
    </main>
  );
}
