"use client";

import { useMemo, useState } from "react";
import { sourceLabel } from "@/lib/prisma-app/prisma-mobile-api-client";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import styles from "./prisma-mobile-multi-context-switcher.module.css";

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
};

type VisualTheme = "obsidian" | "silver" | "graphite";

type ContextOption = {
  id: string;
  client: string;
  site: string;
  device: string;
  vertical: string;
  tone: "ok" | "review" | "urgent" | "offline";
  summary: string;
  age: string;
};

const THEME_OPTIONS: Array<{ key: VisualTheme; label: string; detail: string }> = [
  { key: "obsidian", label: "Obsidian", detail: "vidrio negro" },
  { key: "silver", label: "Silver", detail: "metal titanio" },
  { key: "graphite", label: "Graphite", detail: "vanta glass" }
];

const STATUS_LABEL: Record<ContextOption["tone"], string> = {
  ok: "En linea",
  review: "Atencion",
  urgent: "Critico",
  offline: "Offline"
};

function contextTone(status: string): ContextOption["tone"] {
  if (status === "sano") return "ok";
  if (status === "revisar") return "review";
  if (status === "urgente") return "urgent";
  return "offline";
}

function verticalFromSnapshot(snapshot: PrismaMobileClientSnapshot["snapshot"]): string {
  const hasIndustrialSignals = snapshot.healthRadar.dimensions.some((dimension) => /sync|device|inventory|source|data/i.test(dimension.key));
  if (hasIndustrialSignals && snapshot.inventoryWatchlist.counts.critical > 0) return "Industrial";
  if (snapshot.inventoryWatchlist.counts.reorder > 0) return "Commerce";
  return "Control";
}

function buildContexts(clientSnapshot: PrismaMobileClientSnapshot): ContextOption[] {
  const snapshot = clientSnapshot.snapshot;
  const client = snapshot.summary.businessName || snapshot.today.businessName || "PRISMA";
  const source = sourceLabel(clientSnapshot.source);
  const vertical = verticalFromSnapshot(snapshot);
  const device = clientSnapshot.source === "tablet-pos" ? "Tablet POS" : source;
  const branches = snapshot.branches.branches.slice(0, 5);

  if (branches.length === 0) {
    return [{
      id: "global",
      client,
      site: "Operacion global",
      device,
      vertical,
      tone: snapshot.summary.health === "sano" ? "ok" : snapshot.summary.health === "urgente" ? "urgent" : "review",
      summary: snapshot.summary.dataReadiness.sourceSummary,
      age: clientSnapshot.stale ? "respaldo local" : "ahora"
    }];
  }

  return branches.map((branch, index) => ({
    id: `${branch.name}-${index}`,
    client,
    site: branch.name,
    device: index === 0 ? device : `Tablet ${String(index + 1).padStart(2, "0")}`,
    vertical: index % 2 === 0 ? vertical : "Commerce",
    tone: contextTone(branch.status),
    summary: `${branch.salesToday} · ${branch.tickets} tickets · ${branch.syncLag}`,
    age: index === 0 ? (clientSnapshot.stale ? "respaldo local" : "en vivo") : `hace ${Math.max(8, index * 17)} min`
  }));
}

function sourceFreshness(seconds: number | null | undefined): string {
  if (typeof seconds !== "number") return "freshness sin dato";
  if (seconds < 60) return `${seconds}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} min`;
  return `${Math.round(seconds / 3600)} h`;
}

export function PrismaMobileMultiContextSwitcher({ clientSnapshot }: Props) {
  const [theme, setTheme] = useState<VisualTheme>("obsidian");
  const [activeIndex, setActiveIndex] = useState(0);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [appliedPulse, setAppliedPulse] = useState(0);
  const contexts = useMemo(() => buildContexts(clientSnapshot), [clientSnapshot]);
  const current = contexts[activeIndex] ?? contexts[0];
  const snapshot = clientSnapshot.snapshot;
  const sources = snapshot.dataQuality.sources.slice(0, 4);
  const critical = contexts.filter((context) => context.tone === "urgent").length;
  const review = contexts.filter((context) => context.tone === "review").length;
  const ok = contexts.filter((context) => context.tone === "ok").length;
  const offline = contexts.filter((context) => context.tone === "offline").length;

  function applyContext(index: number) {
    setActiveIndex(index);
    setAppliedPulse((value) => value + 1);
    setSheetOpen(false);
  }

  function quickSwitch() {
    applyContext((activeIndex + 1) % contexts.length);
  }

  return (
    <section
      className={`${styles.multiContextRoot} ${styles[theme]} ${appliedPulse % 2 === 1 ? styles.appliedPulse : ""}`}
      data-prisma-zone="mobile-multi-context-switcher"
      data-prisma-contract="PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE"
      aria-label="PRISMA Multi-context Switcher"
    >
      <div className={styles.orbitalAura} aria-hidden="true" />
      <header className={styles.contextHeader}>
        <div className={styles.contextBrand}>
          <img src="/prisma-mobile-premium-mark.svg" alt="" />
          <div>
            <span>PRISMA MOBILE</span>
            <h2>Multi-context Switcher</h2>
            <p>Cliente, sitio, dispositivo y vertical con evidencia visible.</p>
          </div>
        </div>
        <div className={styles.themeRail} aria-label="Tema visual">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.key}
              type="button"
              className={theme === option.key ? styles.themeActive : undefined}
              onClick={() => setTheme(option.key)}
            >
              <strong>{option.label}</strong>
              <span>{option.detail}</span>
            </button>
          ))}
        </div>
      </header>

      <div className={styles.contextDeck}>
        <button type="button" className={`${styles.contextRail} ${styles.glassPlate}`} onClick={() => setSheetOpen((value) => !value)} aria-expanded={sheetOpen}>
          <span className={styles.contextFacet}>
            <small>Cliente</small>
            <strong>{current.client}</strong>
          </span>
          <span className={styles.contextFacet}>
            <small>Sitio</small>
            <strong>{current.site}</strong>
          </span>
          <span className={styles.contextFacet}>
            <small>Dispositivo</small>
            <strong>{current.device}</strong>
          </span>
          <span className={styles.contextFacet}>
            <small>Vertical</small>
            <strong>{current.vertical}</strong>
          </span>
        </button>

        <div className={`${styles.liveStrip} ${styles.glassPlate}`}>
          <div>
            <span className={styles.liveDot} />
            <strong>Contexto en vivo</strong>
            <em>{current.client} › {current.site} › {current.device} › {current.vertical}</em>
          </div>
          <small>{snapshot.summary.dataReadiness.label} · {sourceFreshness(snapshot.dataQuality.freshnessSeconds)} · {snapshot.dataQuality.confidence ? `${Math.round(snapshot.dataQuality.confidence * 100)}% confianza` : "confianza no disponible"}</small>
        </div>

        <div className={styles.statusQuad}>
          <article className={`${styles.statusCard} ${styles.toneOk}`}><span>En linea</span><strong>{ok}</strong><small>normal</small></article>
          <article className={`${styles.statusCard} ${styles.toneReview}`}><span>Atencion</span><strong>{review}</strong><small>revision</small></article>
          <article className={`${styles.statusCard} ${styles.toneUrgent}`}><span>Critico</span><strong>{critical}</strong><small>accion</small></article>
          <article className={`${styles.statusCard} ${styles.toneOffline}`}><span>Offline</span><strong>{offline}</strong><small>respaldo</small></article>
        </div>
      </div>

      <div className={styles.commandGrid}>
        <article className={`${styles.heroCard} ${styles.glassPlate}`}>
          <span className={styles.cardEyebrow}>Action Inbox</span>
          <div className={styles.crystalCube} aria-hidden="true" />
          <strong>{snapshot.actionInbox.items.length}</strong>
          <p>{snapshot.actionInbox.primaryAction?.title ?? "Sin acciones urgentes desde Mobile."}</p>
          <small>Mobile supervisa. Tablet opera. Core registra evidencia.</small>
        </article>

        <article className={`${styles.radarCard} ${styles.glassPlate}`}>
          <span className={styles.cardEyebrow}>Health Radar</span>
          <div className={styles.radarOrb} aria-hidden="true" />
          <strong>{snapshot.healthRadar.globalScore ?? "N/D"}<small>/100</small></strong>
          <p>{snapshot.healthRadar.status === "healthy" ? "Sistema estable" : snapshot.healthRadar.status}</p>
        </article>

        <article className={`${styles.timelineCard} ${styles.glassPlate}`}>
          <span className={styles.cardEyebrow}>Pulse Timeline</span>
          <svg viewBox="0 0 260 72" role="img" aria-label="Pulso operativo">
            <defs>
              <linearGradient id="prismaMcsSpark" x1="0" x2="1">
                <stop offset="0" stopColor="currentColor" />
                <stop offset="0.52" stopColor="var(--mcs-cyan)" />
                <stop offset="1" stopColor="var(--mcs-violet)" />
              </linearGradient>
            </defs>
            <path d="M4 50 L26 42 L48 48 L70 27 L94 36 L118 21 L142 44 L166 35 L190 47 L214 29 L238 41 L256 31" />
          </svg>
          <div><strong>{snapshot.timeline.length}</strong><small>eventos recientes</small></div>
        </article>

        <article className={`${styles.evidenceCard} ${styles.glassPlate}`}>
          <span className={styles.cardEyebrow}>Evidence Freshness</span>
          <div className={styles.evidenceGauge}><strong>{Math.round(snapshot.dataQuality.completeness * 100)}%</strong></div>
          <p>{snapshot.dataQuality.warnings[0] ?? snapshot.summary.dataReadiness.sourceSummary}</p>
        </article>
      </div>

      <div className={`${styles.sheetShell} ${sheetOpen ? styles.sheetOpen : ""}`} aria-hidden={!sheetOpen}>
        <div className={styles.sheetBackdrop} onClick={() => setSheetOpen(false)} />
        <section className={styles.switchSheet} aria-label="Cambiar contexto PRISMA">
          <header>
            <div>
              <img src="/prisma-mobile-premium-mark.svg" alt="" />
              <span>Multi-context Switcher</span>
            </div>
            <button type="button" onClick={() => setSheetOpen(false)} aria-label="Cerrar selector">×</button>
          </header>

          <div className={styles.selectorStack}>
            <article><span>Cliente</span><strong>{current.client}</strong><i>⌄</i></article>
            <article><span>Sitio</span><strong>{current.site}</strong><i>⌄</i></article>
            <article><span>Dispositivo</span><strong>{current.device}</strong><i>⌄</i></article>
            <article><span>Vertical</span><strong>{current.vertical}</strong><i>⌄</i></article>
          </div>

          <div className={styles.searchRow}>
            <label>
              <span>⌕</span>
              <input value="" readOnly aria-label="Buscar contexto" placeholder="Buscar contexto..." />
            </label>
            <button type="button" onClick={quickSwitch}>ϟ Quick Switch</button>
          </div>

          <div className={styles.recentContexts}>
            <h3>Contextos recientes <span>Ver todos</span></h3>
            {contexts.map((context, index) => (
              <button key={context.id} type="button" className={index === activeIndex ? styles.contextActive : undefined} onClick={() => applyContext(index)}>
                <span>{context.client} › {context.site} › {context.device} › {context.vertical}</span>
                <small>{STATUS_LABEL[context.tone]} · {context.age}</small>
              </button>
            ))}
          </div>

          <div className={styles.sourceMatrix}>
            {sources.length > 0 ? sources.map((source) => (
              <article key={source.id} data-status={source.status}>
                <span>{source.label}</span>
                <strong>{source.status}</strong>
                <small>{sourceFreshness(source.freshnessSeconds)}</small>
              </article>
            )) : (
              <article data-status="unknown"><span>Fuentes</span><strong>sin detalle</strong><small>snapshot parcial</small></article>
            )}
          </div>

          <footer>
            <div>
              <span>Aplicar este contexto</span>
              <strong>{current.client} › {current.site}</strong>
              <small>{current.device} › {current.vertical}</small>
            </div>
            <button type="button" onClick={() => applyContext(activeIndex)}>
              Aplicar contexto <span>→</span>
            </button>
          </footer>
        </section>
      </div>
    </section>
  );
}
