import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileDailyBrief } from "@/lib/prisma-app/prisma-mobile-daily-brief";
import type { PrismaMobileCommandTone } from "@/lib/prisma-app/prisma-mobile-command-center";
import styles from "./prisma-mobile-dashboard.module.css";

const briefToneClass: Record<PrismaMobileCommandTone, string> = {
  sano: styles.commandToneOk,
  revisar: styles.commandToneReview,
  urgente: styles.commandToneUrgent,
  offline: styles.commandToneOffline
};

export function PrismaMobileDailyBrief({ clientSnapshot }: { clientSnapshot: PrismaMobileClientSnapshot }) {
  const brief = buildPrismaMobileDailyBrief(clientSnapshot);
  const whatsappHref = `https://wa.me/?text=${encodeURIComponent(brief.whatsappText)}`;
  const mailHref = `mailto:?subject=${encodeURIComponent(brief.emailSubject)}&body=${encodeURIComponent(brief.emailBody)}`;

  return (
    <section className={styles.dailyBrief} aria-labelledby="prisma-mobile-daily-brief-title" data-prisma-contract={brief.contractId}>
      <header className={styles.dailyBriefHeader}>
        <div>
          <span className={styles.commandEyebrow}>Brief diario móvil</span>
          <h2 id="prisma-mobile-daily-brief-title">Resumen ejecutivo compartible</h2>
          <p>{brief.subheadline}</p>
        </div>
        <aside className={`${styles.dailyBriefStatus} ${briefToneClass[brief.riskTone]}`}>
          <span>{brief.generatedLabel}</span>
          <strong>{brief.readinessLabel}</strong>
          <small>{brief.copyHint}</small>
        </aside>
      </header>

      <div className={styles.dailyBriefShareBox} aria-label="Resumen listo para compartir">
        <div>
          <span>{brief.shareTitle}</span>
          <strong>{brief.headline}</strong>
          <p>{brief.whatsappText}</p>
        </div>
        <nav aria-label="Acciones de compartir resumen PRISMA">
          <a href={whatsappHref} target="_blank" rel="noreferrer">Enviar WhatsApp</a>
          <a href={mailHref}>Preparar correo</a>
        </nav>
      </div>

      <div className={styles.dailyBriefCardGrid} aria-label="KPIs compactos para compartir">
        {brief.cards.map((card) => (
          <article key={card.label} className={briefToneClass[card.tone]}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.detail}</small>
          </article>
        ))}
      </div>

      <div className={styles.dailyBriefSectionGrid} aria-label="Secciones del brief diario">
        {brief.sections.map((section) => (
          <article key={section.id} className={`${styles.dailyBriefSection} ${briefToneClass[section.tone]}`}>
            <span>{section.subtitle}</span>
            <h3>{section.title}</h3>
            <ul>{section.bullets.map((bullet) => <li key={bullet}>{bullet}</li>)}</ul>
          </article>
        ))}
      </div>

      <details className={styles.dailyBriefExport}>
        <summary>Ver texto exportable</summary>
        <pre>{brief.exportText}</pre>
      </details>
    </section>
  );
}
