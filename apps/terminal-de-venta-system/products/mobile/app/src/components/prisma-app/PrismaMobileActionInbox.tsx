import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileActionInbox } from "@/lib/prisma-app/prisma-mobile-action-inbox";
import type { PrismaMobileCommandTone } from "@/lib/prisma-app/prisma-mobile-command-center";
import styles from "./prisma-mobile-dashboard.module.css";

const inboxToneClass: Record<PrismaMobileCommandTone, string> = {
  sano: styles.commandToneOk,
  revisar: styles.commandToneReview,
  urgente: styles.commandToneUrgent,
  offline: styles.commandToneOffline
};

const areaLabel = {
  caja: "Caja",
  inventario: "Inventario",
  ventas: "Ventas",
  sucursal: "Sucursal",
  datos: "Datos",
  alertas: "Alertas"
} as const;

export function PrismaMobileActionInbox({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const inbox = buildPrismaMobileActionInbox(clientSnapshot);

  return (
    <section className={styles.actionInbox} aria-labelledby="prisma-mobile-action-inbox-title" data-prisma-contract={inbox.contractId}>
      <header className={styles.actionInboxHeader}>
        <div>
          <span className={styles.commandEyebrow}>Bandeja del dueño</span>
          <h2 id="prisma-mobile-action-inbox-title">Acciones operativas priorizadas</h2>
          <p>{inbox.summary}</p>
        </div>
        <aside className={styles.actionInboxStatus} aria-label="Estado de acciones móviles">
          <span>{inbox.generatedLabel}</span>
          <strong>{inbox.readinessLabel}</strong>
          <small>{inbox.actionCount} acciones · {inbox.urgentCount} inmediatas</small>
        </aside>
      </header>

      <div className={styles.actionInboxDigest} aria-label="Mensaje operativo listo para compartir">
        <div>
          <span>{inbox.digest.title}</span>
          <strong>{inbox.headline}</strong>
        </div>
        <p>{inbox.ownerMessage}</p>
      </div>

      <div className={styles.actionLaneGrid} aria-label="Acciones separadas por urgencia">
        {inbox.lanes.map((lane) => (
          <section key={lane.id} className={`${styles.actionLane} ${inboxToneClass[lane.tone]}`}>
            <header>
              <span>{lane.count} pendientes</span>
              <h3>{lane.title}</h3>
              <p>{lane.subtitle}</p>
            </header>
            <div>
              {lane.actions.slice(0, 4).map((action) => (
                <article key={action.id} className={`${styles.actionCard} ${inboxToneClass[action.tone]}`}>
                  <div className={styles.actionCardTopline}>
                    <span>{areaLabel[action.area]}</span>
                    <b>{action.priorityScore}</b>
                  </div>
                  <strong>{action.title}</strong>
                  <p>{action.summary}</p>
                  <ul>
                    {action.evidence.slice(0, 3).map((item) => <li key={item}>{item}</li>)}
                  </ul>
                  <footer>
                    <em>{action.owner}</em>
                    <span>{action.dueLabel}</span>
                  </footer>
                  <small>{action.recommendedAction}</small>
                </article>
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}
