import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import type { PrismaOperationalScreenModel, PrismaScreenAction, PrismaScreenSection, PrismaScreenTone } from "@/lib/ui/prisma-operational-screen-contract";
import { readyOperationalScreen } from "@/lib/ui/prisma-operational-screen-engine";
import styles from "./prisma-operational-screen.module.css";

function toneForData(tone: PrismaScreenTone | undefined) {
  return tone ?? "neutral";
}

function ScreenAction({ action }: { action: PrismaScreenAction }) {
  const tone = toneForData(action.tone);
  if (action.href && !action.disabled) {
    return <a className={styles.actionLink} data-tone={tone} href={action.href} title={action.description}>{action.label}</a>;
  }
  return <button className={styles.actionButton} data-tone={tone} type="button" disabled={action.disabled} title={action.description}>{action.label}</button>;
}

function EmptyBlock({ title, description }: { title?: string; description?: string }) {
  return (
    <div className={styles.emptyState}>
      <span className={styles.emptyPill}>estado limpio</span>
      <h3 className={styles.emptyTitle}>{title ?? "Sin datos operativos"}</h3>
      <p className={styles.emptyDescription}>{description ?? "El servicio no regreso registros para esta seccion."}</p>
    </div>
  );
}

function RenderSection({ section }: { section: PrismaScreenSection }) {
  const hasTable = Boolean(section.table?.rows.length);
  const hasItems = Boolean(section.items?.length);
  return (
    <section className={styles.sectionCard} data-kind={section.kind} data-tone={toneForData(section.tone)}>
      <div className={styles.sectionHead}>
        <span className={styles.sectionKicker}>{section.kind}</span>
        <h2 className={styles.sectionTitle}>{section.title}</h2>
        {section.subtitle ? <p className={styles.sectionSubtitle}>{section.subtitle}</p> : null}
      </div>

      {section.table ? (
        hasTable ? (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead>
                <tr>
                  {section.table.columns.map((column) => <th key={column.key} data-align={column.align ?? "left"}>{column.label}</th>)}
                </tr>
              </thead>
              <tbody>
                {section.table.rows.map((row, index) => (
                  <tr key={row.id ?? index} data-tone={toneForData(row.tone)}>
                    {section.table?.columns.map((column) => <td key={column.key} data-align={column.align ?? "left"}>{row[column.key] ?? "-"}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <EmptyBlock title={section.emptyTitle} description={section.emptyDescription} />
      ) : null}

      {!section.table && hasItems ? (
        <div className={styles.listStack}>
          {section.items?.map((item, index) => (
            <article key={`${item.title}-${index}`} className={styles.listItem} data-tone={toneForData(item.tone)}>
              <span className={styles.toneRail} data-tone={toneForData(item.tone)} aria-hidden="true" />
              <div className={styles.listHead}>
                <div>
                  <div className={styles.listTitle}>{item.title}</div>
                  {item.description ? <div className={styles.listDescription}>{item.description}</div> : null}
                  {item.meta ? <div className={styles.listMeta}>{item.meta}</div> : null}
                </div>
                {item.value ? <div className={styles.listValue}>{item.value}</div> : null}
              </div>
            </article>
          ))}
        </div>
      ) : null}

      {!section.table && !hasItems ? <EmptyBlock title={section.emptyTitle} description={section.emptyDescription} /> : null}
    </section>
  );
}

export function PrismaOperationalScreen({ model }: { model: PrismaOperationalScreenModel }) {
  const screen = readyOperationalScreen(model);
  const [primarySection, ...secondarySections] = screen.sections;
  return (
    <PrismaTabletShellUnified
      currentPath={screen.currentPath}
      title={screen.title}
      subtitle={screen.subtitle}
      kicker={screen.kicker}
      status={screen.status ? <TabletShellStatusPill tone={screen.status.tone}>{screen.status.label}</TabletShellStatusPill> : undefined}
      actions={screen.actions?.length ? <div className={styles.actionRow}>{screen.actions.map((action) => <ScreenAction key={action.label} action={action} />)}</div> : undefined}
    >
      <div className={styles.frame} data-prisma-screen-standard="01A" data-density={screen.density}>
        {screen.hero ? (
          <section className={styles.masthead}>
            <div className={styles.mastheadCopy}>
              <span className={styles.eyebrow}>{screen.hero.eyebrow}</span>
              <h2 className={styles.mastheadTitle}>{screen.hero.title}</h2>
              <p className={styles.mastheadDescription}>{screen.hero.description}</p>
            </div>
            <aside className={styles.mastheadPanel}>
              <div>
                <span className={styles.signalLabel}>senal operativa</span>
                <span className={styles.signalValue}>{screen.hero.signal?.label ?? screen.status?.label ?? "listo"}</span>
              </div>
              {screen.actions?.length ? <div className={styles.actionRow}>{screen.actions.slice(0, 2).map((action) => <ScreenAction key={`hero-${action.label}`} action={action} />)}</div> : null}
            </aside>
          </section>
        ) : null}

        <section className={styles.metricsGrid} aria-label="Metricas operativas">
          {screen.metrics.map((metric) => (
            <article key={metric.label} className={styles.metricCard} data-tone={toneForData(metric.tone)} data-emphasis={metric.emphasis ?? "secondary"}>
              <span className={styles.metricLabel}>{metric.label}</span>
              <strong className={styles.metricValue}>{metric.value}</strong>
              {metric.note ? <span className={styles.metricNote}>{metric.note}</span> : null}
            </article>
          ))}
        </section>

        <div className={styles.sectionGrid} data-single={secondarySections.length === 0 ? "true" : "false"}>
          {primarySection ? <RenderSection section={primarySection} /> : <EmptyBlock title="Sin seccion primaria" description="El modelo debe declarar al menos una seccion operativa." />}
          {secondarySections.length ? <div className={styles.listStack}>{secondarySections.map((section) => <RenderSection key={section.id} section={section} />)}</div> : null}
        </div>
      </div>
    </PrismaTabletShellUnified>
  );
}
