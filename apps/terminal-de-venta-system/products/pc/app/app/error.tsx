"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#f8fafc", color: "#172033", padding: 32 }}>
      <section style={{ width: "min(760px, 100%)", border: "1px solid #fecaca", borderRadius: 24, background: "white", padding: 28, boxShadow: "0 18px 50px rgba(127, 29, 29, .08)" }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900, color: "#b91c1c" }}>Pantalla protegida</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 32 }}>No se pudo cargar esta vista</h1>
        <p style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>PRISMA PC muestra un estado seguro en lugar del overlay rojo de desarrollo. No se inventaron datos y la operación puede continuar.</p>
        <button onClick={reset} style={{ marginTop: 18, border: 0, borderRadius: 999, padding: "12px 18px", background: "#0f172a", color: "white", fontWeight: 800 }}>Reintentar</button>
      </section>
    </main>
  );
}
