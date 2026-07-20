"use client";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 32 }}>
      <section style={{ width: "min(760px, 100%)", padding: 28 }}>
        <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: ".14em", fontSize: 12, fontWeight: 900 }}>Pantalla protegida</p>
        <h1 style={{ margin: "10px 0 6px", fontSize: 32 }}>No se pudo cargar esta vista</h1>
        <p style={{ margin: 0, lineHeight: 1.6 }}>PRISMA PC muestra un estado seguro en lugar del overlay rojo de desarrollo. No se inventaron datos y la operación puede continuar.</p>
        <button onClick={reset} style={{ marginTop: 18, padding: "12px 18px", fontWeight: 800 }}>Reintentar</button>
      </section>
    </main>
  );
}
