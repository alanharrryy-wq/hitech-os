"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: 32 }}>
      <section style={{ width: "min(720px, 100%)", padding: 24 }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900 }}>Vista protegida</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 28 }}>Estado seguro</h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>La vista se protegió contra fallos de runtime o lectura lenta. No se muestran datos falsos ni paths locales.</p>
        <button onClick={reset} style={{ marginTop: 16, padding: "11px 16px", fontWeight: 800 }}>Reintentar</button>
      </section>
    </main>
  );
}
