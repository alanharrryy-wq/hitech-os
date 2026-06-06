export default function Loading() {
  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: 32, background: "#f8fafc", color: "#172033" }}>
      <section style={{ width: "min(680px, 100%)", border: "1px solid #dbe3ef", borderRadius: 22, padding: 24, background: "white", boxShadow: "0 16px 44px rgba(15,23,42,.08)" }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900, color: "#2563eb" }}>PRISMA PC</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 28 }}>Cargando vista segura</h1>
        <p style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>Si la base local tarda, la pantalla debe caer en estado honesto sin overlay rojo.</p>
      </section>
    </main>
  );
}
