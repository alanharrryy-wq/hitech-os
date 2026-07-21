"use client";

export default function HoyError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <section style={{ padding: "1rem" }}>
      <div style={{ padding: "1rem" }}>
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
