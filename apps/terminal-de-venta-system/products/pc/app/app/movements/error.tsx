"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main style={{ minHeight: "70vh", display: "grid", placeItems: "center", padding: 32 }}>
      <section style={{ width: "min(720px, 100%)", padding: 24 }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900 }}>movimientos no disponibles</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 28 }}>No pudimos cargar los movimientos</h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>No se realizó ningún cambio. Puedes intentar cargar la información nuevamente.</p>
        <button onClick={reset} style={{ marginTop: 16, padding: "11px 16px", fontWeight: 800 }}>Reintentar</button>
      </section>
    </main>
  );
}
