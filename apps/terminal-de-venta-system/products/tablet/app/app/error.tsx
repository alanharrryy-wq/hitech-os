"use client";

import { AppShell } from "@components/layout/app-shell";
import { InlineAlert } from "@components/ui/inline-alert";
import { SectionCard } from "@components/ui/section-card";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="es-MX">
      <body>
        <AppShell currentPath="/">
          <InlineAlert
            tone="danger"
            title="La terminal se tropezó, pero no se fue de hocico"
            description="Se disparó un error de ejecución. La idea aquí es que el operador tenga contexto y una salida limpia, no una pantalla muerta estilo película de terror."
            note={error.digest ? `digest: ${error.digest}` : "sin digest disponible"}
          />
          <SectionCard title="Qué hacer ahorita" subtitle="Secuencia corta para recuperar operación sin perder el control.">
            <div className="stack-list">
              <div className="stack-item">
                <strong>1. Reintentar el render</strong>
                <div className="subtle">Usa el botón para volver a montar la vista sin recargar todo el turno.</div>
              </div>
              <div className="stack-item">
                <strong>2. Validar sync y outbox</strong>
                <div className="subtle">Si el error vino de datos parciales, primero revisa pendientes antes de seguir cobrando.</div>
              </div>
              <div className="stack-item">
                <strong>3. Escalar si persiste</strong>
                <div className="subtle">Si vuelve a tronar, captura evidencia y manda el caso a soporte con folio del turno.</div>
              </div>
            </div>
            <div style={{ marginTop: 16 }}>
              <button className="primary-button" onClick={() => reset()}>reintentar vista</button>
            </div>
          </SectionCard>
        </AppShell>
      </body>
    </html>
  );
}
