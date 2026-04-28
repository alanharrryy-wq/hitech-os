import type { ReactNode } from "react";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import type { PrismaIconName } from "./prisma-dark-pos-data";
import styles from "./prisma-dark-pos.module.css";

type Tone = "ok" | "warn" | "danger" | "neutral";

type ShellNavItem = {
  href: string;
  label: string;
  icon: PrismaIconName;
};

const shellNavItems: ShellNavItem[] = [
  { href: "/", label: "Inicio", icon: "dashboard" },
  { href: "/sales", label: "Ventas", icon: "cart" },
  { href: "/checkout", label: "Cobro", icon: "credit-card" },
  { href: "/returns", label: "Devoluciones", icon: "receipt" },
  { href: "/stock", label: "Stock", icon: "package" },
  { href: "/shift", label: "Turno", icon: "terminal" },
  { href: "/sync", label: "Sync", icon: "chart" },
  { href: "/prisma-dark-pos-reference", label: "Referencia", icon: "sparkle" }
];

export function PrismaTabletShell({
  currentPath,
  title,
  kicker,
  subtitle,
  children,
  context,
  actions
}: {
  currentPath: string;
  title: string;
  kicker: string;
  subtitle: string;
  children: ReactNode;
  context?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className={styles.routeShell}>
      <aside className={styles.routeNavRail} aria-label="Navegación PRISMA">
        <a className={styles.routeBrand} href="/prisma-dark-pos-reference" aria-label="PRISMA Dark POS">
          <span className={styles.routeBrandMark}>
            <span />
          </span>
          <span className={styles.routeBrandText}>
            <strong>PRISMA</strong>
            <small>Dark POS</small>
          </span>
        </a>

        <nav className={styles.routeNavList}>
          {shellNavItems.map((item) => {
            const active = currentPath === item.href;
            return (
              <a key={item.href} className={active ? styles.routeNavActive : styles.routeNavItem} href={item.href}>
                <PrismaIcon name={item.icon} size={20} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>

        <div className={styles.routeTerminalCard}>
          <span className={styles.routeTerminalIcon}>
            <PrismaIcon name="terminal" size={18} />
          </span>
          <span>
            <strong>Terminal 01</strong>
            <small>En línea</small>
          </span>
        </div>
      </aside>

      <main className={styles.routeViewport}>
        <header className={styles.routeTopbar}>
          <div className={styles.routeTitleGroup}>
            <span>{kicker}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className={styles.routeTopbarRight}>
            {context}
            <button className={styles.routeTopIcon} type="button" aria-label="Tema">
              <PrismaIcon name="sun" size={19} />
            </button>
            <button className={styles.routeTopIcon} type="button" aria-label="Notificaciones">
              <PrismaIcon name="bell" size={19} />
            </button>
            <div className={styles.routeUserChip}>
              <span>AR</span>
              <strong>Administrador</strong>
            </div>
          </div>
        </header>
        {actions ? <div className={styles.routeActionBand}>{actions}</div> : null}
        <div className={styles.routeContent}>{children}</div>
      </main>
    </div>
  );
}

export function PrismaPanel({
  title,
  subtitle,
  eyebrow,
  children,
  action,
  className
}: {
  title?: string;
  subtitle?: string;
  eyebrow?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <section className={[styles.routePanel, className].filter(Boolean).join(" ")}>
      {title || subtitle || eyebrow || action ? (
        <header className={styles.routePanelHeader}>
          <div>
            {eyebrow ? <span>{eyebrow}</span> : null}
            {title ? <h2>{title}</h2> : null}
            {subtitle ? <p>{subtitle}</p> : null}
          </div>
          {action}
        </header>
      ) : null}
      {children}
    </section>
  );
}

export function PrismaKpiStrip({
  metrics
}: {
  metrics: Array<{ label: string; value: string; note: string; tone?: Tone; icon?: PrismaIconName }>;
}) {
  return (
    <section className={styles.routeKpiStrip} aria-label="Indicadores">
      {metrics.map((metric) => (
        <article key={metric.label} className={styles.routeMetricCard}>
          <div>
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <small>{metric.note}</small>
          </div>
          <span className={styles.routeMetricIcon}>
            <PrismaIcon name={metric.icon ?? "chart"} size={20} />
          </span>
        </article>
      ))}
    </section>
  );
}

export function PrismaSearchActionStrip({
  placeholder,
  primaryLabel,
  secondaryLabel
}: {
  placeholder: string;
  primaryLabel: string;
  secondaryLabel?: string;
}) {
  return (
    <div className={styles.routeSearchStrip}>
      <label className={styles.routeSearchControl}>
        <PrismaIcon name="search" size={21} />
        <input aria-label={placeholder} placeholder={placeholder} />
        <PrismaIcon name="scan" size={21} />
      </label>
      <button className={styles.routeGoldGhostButton} type="button">
        <PrismaIcon name="scan" size={20} />
        <span>{primaryLabel}</span>
      </button>
      {secondaryLabel ? (
        <button className={styles.routeDarkButton} type="button">
          <PrismaIcon name="more" size={20} />
          <span>{secondaryLabel}</span>
        </button>
      ) : null}
    </div>
  );
}

export function PrismaStatusBadge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={[styles.routeBadge, styles[`routeBadge_${tone}`]].join(" ")}>{children}</span>;
}

export function PrismaActionCard({
  title,
  description,
  meta,
  tone = "neutral",
  icon = "sparkle"
}: {
  title: string;
  description: string;
  meta?: string;
  tone?: Tone;
  icon?: PrismaIconName;
}) {
  return (
    <article className={[styles.routeActionCard, styles[`routeActionCard_${tone}`]].join(" ")}>
      <span className={styles.routeActionIcon}>
        <PrismaIcon name={icon} size={20} />
      </span>
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
      </div>
      {meta ? <small>{meta}</small> : null}
    </article>
  );
}

export function PrismaFlowList({
  items
}: {
  items: Array<{ step?: string; title: string; description: string; tone?: Tone; aside?: ReactNode }>;
}) {
  return (
    <div className={styles.routeFlowList}>
      {items.map((item, index) => (
        <article key={`${item.title}-${index}`} className={styles.routeFlowItem}>
          <span className={styles.routeFlowStep}>{item.step ?? String(index + 1).padStart(2, "0")}</span>
          <div>
            <strong>{item.title}</strong>
            <p>{item.description}</p>
          </div>
          {item.aside ? <span className={styles.routeFlowAside}>{item.aside}</span> : null}
        </article>
      ))}
    </div>
  );
}

export function PrismaPillCloud({ items, tone = "neutral" }: { items: readonly string[]; tone?: Tone }) {
  return (
    <div className={styles.routePillCloud}>
      {items.map((item) => (
        <span key={item} className={[styles.routePill, styles[`routePill_${tone}`]].join(" ")}>
          {item}
        </span>
      ))}
    </div>
  );
}

export function PrismaDataTable({
  columns,
  rows,
  emptyLabel
}: {
  columns: string[];
  rows: Array<Record<string, ReactNode>>;
  emptyLabel: string;
}) {
  if (!rows.length) {
    return <PrismaEmptyState title={emptyLabel} description="Cuando haya actividad real, esta sección se llenará automáticamente." icon="receipt" />;
  }

  return (
    <div className={styles.routeTableWrap}>
      <table className={styles.routeTable}>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column}>{row[column]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function PrismaEmptyState({
  title,
  description,
  icon = "sparkle",
  action
}: {
  title: string;
  description: string;
  icon?: PrismaIconName;
  action?: ReactNode;
}) {
  return (
    <div className={styles.routeEmptyState}>
      <span>
        <PrismaIcon name={icon} size={22} />
      </span>
      <strong>{title}</strong>
      <p>{description}</p>
      {action}
    </div>
  );
}

export function PrismaPrimaryButton({ href, children, shortcut }: { href?: string; children: ReactNode; shortcut?: string }) {
  const content = (
    <>
      <span>{children}</span>
      {shortcut ? <strong>{shortcut}</strong> : null}
    </>
  );

  if (href) {
    return (
      <a className={styles.routePrimaryButton} href={href}>
        {content}
      </a>
    );
  }

  return (
    <button className={styles.routePrimaryButton} type="button">
      {content}
    </button>
  );
}

export function PrismaSecondaryButton({ children, icon = "sparkle" }: { children: ReactNode; icon?: PrismaIconName }) {
  return (
    <button className={styles.routeSecondaryButton} type="button">
      <PrismaIcon name={icon} size={18} />
      <span>{children}</span>
    </button>
  );
}

export function PrismaTotalDisplay({
  label,
  value,
  note
}: {
  label: string;
  value: string;
  note?: string;
}) {
  return (
    <div className={styles.routeTotalDisplay}>
      <span>{label}</span>
      <strong>{value}</strong>
      {note ? <small>{note}</small> : null}
    </div>
  );
}

export function PrismaQuickProductCard({
  name,
  meta,
  price,
  signal,
  icon = "package"
}: {
  name: string;
  meta: string;
  price: string;
  signal: string;
  icon?: PrismaIconName;
}) {
  return (
    <article className={styles.routeProductTile}>
      <span className={styles.routeProductIcon}>
        <PrismaIcon name={icon} size={24} />
      </span>
      <div>
        <strong>{name}</strong>
        <small>{meta}</small>
      </div>
      <footer>
        <span>{price}</span>
        <PrismaStatusBadge tone="ok">{signal}</PrismaStatusBadge>
      </footer>
    </article>
  );
}
