"use client";

export default function HoyError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <section style={{ padding: "1rem" }}>
      <div style={{ border: "1px solid rgba(220, 38, 38, 0.35)", borderRadius: "1rem", padding: "1rem", background: "rgba(254, 242, 242, 0.95)" }}>
        <p style={{ margin: 0, fontWeight: 900 }}>No se pudo cargar Hoy</p>
        <p style={{ margin: "0.35rem 0 0" }}>
          La lectura principal no está disponible. Puedes reintentar o revisar el detalle técnico.
        </p>
        <details style={{ marginTop: "0.75rem" }}>
          <summary>Ver detalle técnico</summary>
          <pre style={{ whiteSpace: "pre-wrap" }}>{error.message}</pre>
        </details>
        <button type="button" onClick={reset} style={{ marginTop: "0.75rem" }}>
          Reintentar
        </button>
      </div>
    </section>
  );
}
