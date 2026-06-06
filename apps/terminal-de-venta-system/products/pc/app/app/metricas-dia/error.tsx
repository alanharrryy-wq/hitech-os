"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: 32, background: "#f8fafc", color: "#172033" }}>
      <section style={{ width: "min(720px, 100%)", border: "1px solid #fecaca", borderRadius: 22, padding: 24, background: "white", boxShadow: "0 16px 44px rgba(127,29,29,.08)" }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900, color: "#b91c1c" }}>Vista protegida</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 28 }}>Estado seguro</h1>
        <p style={{ margin: 0, color: "#64748b", lineHeight: 1.6 }}>La vista se protegió contra fallos de runtime o lectura lenta. No se muestran datos falsos ni paths locales.</p>
        <button onClick={reset} style={{ marginTop: 16, border: 0, borderRadius: 999, padding: "11px 16px", background: "#0f172a", color: "white", fontWeight: 800 }}>Reintentar</button>
      </section>
    </main>
  );
}
