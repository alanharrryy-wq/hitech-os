import { AppShell } from "@components/layout/app-shell";

export const dynamic = "force-dynamic";

export default function BulkActionsPage() {
  return (
    <AppShell currentPath="/acciones-masivas">
      <section className="hero"><div className="hero-header"><div className="hero-copy"><div className="kicker">acciones masivas</div><h1 className="hero-title">Acciones masivas</h1><p>Esta superficie no ejecuta mutaciones hasta contar con command owner, permisos, motivo, auditoría e idempotencia verificables.</p></div></div></section>
      <section className="card">
        <div className="section-head"><div><div className="kicker">bloqueo seguro</div><h2 className="section-title">Sin operaciones masivas simuladas</h2><div className="section-copy">La lectura y revisión sí están disponibles; la escritura masiva permanece bloqueada hasta existir contrato operacional real.</div></div></div>
        <div className="inline-list"><a className="btn btn-primary" href="/data-quality">Revisar calidad de datos</a><a className="btn" href="/audit">Abrir auditoría</a></div>
      </section>
    </AppShell>
  );
}
