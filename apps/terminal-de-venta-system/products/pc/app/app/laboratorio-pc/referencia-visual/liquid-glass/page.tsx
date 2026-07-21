"use client";

import { useMemo, useState, type ReactNode } from "react";
import * as ScrollArea from "@radix-ui/react-scroll-area";
import * as Select from "@radix-ui/react-select";
import * as Tabs from "@radix-ui/react-tabs";
import * as Tooltip from "@radix-ui/react-tooltip";
import { Slot } from "@radix-ui/react-slot";
import styles from "../../../prisma-liquid-glass.module.css";

const families = [
  {
    "id": "aurora-night",
    "name": "Aurora Night",
    "label": "STORM_GRAPHITE_SHOWCASE",
    "mood": "noche, nieve y aurora cálida",
    "url": "/surface-visual-governor/liquid-glass/families/aurora-night/aurora-night.jpg"
  },
  {
    "id": "alpine-crystal",
    "name": "Alpine Crystal",
    "label": "ICE_CLEAR_REFERENCE",
    "mood": "cristal frío, aire blanco y lectura limpia",
    "url": "/surface-visual-governor/liquid-glass/families/alpine-crystal/alpine-crystal.jpg"
  },
  {
    "id": "ocean-vapor",
    "name": "Ocean Vapor",
    "label": "BLUE_LIQUID_OPERATIONAL",
    "mood": "azul líquido, vapor suave y profundidad",
    "url": "/surface-visual-governor/liquid-glass/families/ocean-vapor/ocean-vapor.jpg"
  },
  {
    "id": "fog-forest",
    "name": "Fog Forest",
    "label": "MIST_GREEN_CALM",
    "mood": "niebla orgánica, sombra verde y descanso visual",
    "url": "/surface-visual-governor/liquid-glass/families/fog-forest/fog-forest.jpg"
  }
] as const;

type Family = (typeof families)[number];
type FamilyId = Family["id"];

type GlassLinkProps = {
  href: string;
  children: ReactNode;
  primary?: boolean;
};

function GlassLink({ href, children, primary = false }: GlassLinkProps) {
  return (
    <Slot className={`${styles.glassAction} ${primary ? styles.glassActionPrimary : ""}`} data-lg-glass-panel="action-link">
      <a href={href}>{children}</a>
    </Slot>
  );
}

export default function LiquidGlassReferenceRoomPage() {
  const [activeId, setActiveId] = useState<FamilyId>("aurora-night");
  const active = useMemo(() => families.find((family) => family.id === activeId) ?? families[0], [activeId]);

  const handleFamilyChange = (value: string) => setActiveId(value as FamilyId);

  return (
    <main
      className={styles.surface}
      data-prisma-panel="pc.liquid-glass-reference"
      data-prisma-surface="pc"
      data-prisma-route="/laboratorio-pc/referencia-visual/liquid-glass"
      data-route="/laboratorio-pc/referencia-visual/liquid-glass"
    >
      <Tooltip.Provider delayDuration={120} skipDelayDuration={80}>
        <Tabs.Root value={activeId} onValueChange={handleFamilyChange} className={styles.tabsRoot}>
          <ScrollArea.Root className={styles.shellScroller} type="scroll">
            <ScrollArea.Viewport className={styles.shellViewport}>
              <div className={styles.shellContent}>
                <header className={styles.directorTopbar} data-lg-glass-panel="topbar">
                  <div className={styles.brand}>
                    <span className={styles.brandMark}>LG</span>
                    <span className={styles.brandText}>
                      <strong>Aurora Director Cut</strong>
                      <span>Radix ScrollArea · Tabs · Select · Tooltip · Slot · OGL aura</span>
                    </span>
                  </div>

                  <div className={styles.controlCluster} aria-label="Controles del piloto">
                    <Select.Root value={activeId} onValueChange={handleFamilyChange}>
                      <Select.Trigger asChild aria-label="Cambiar familia Liquid Glass">
                        <div className={styles.familySelectTrigger} data-lg-glass-panel="family-select">
                          <Select.Value placeholder="Familia" />
                          <Select.Icon className={styles.selectIcon}>⌄</Select.Icon>
                        </div>
                      </Select.Trigger>
                      <Select.Portal>
                        <Select.Content className={styles.selectContent} position="popper" sideOffset={10}>
                          <Select.Viewport className={styles.selectViewport}>
                            {families.map((family) => (
                              <Select.Item className={styles.selectItem} value={family.id} key={family.id}>
                                <Select.ItemText>{family.name}</Select.ItemText>
                              </Select.Item>
                            ))}
                          </Select.Viewport>
                        </Select.Content>
                      </Select.Portal>
                    </Select.Root>

                    <div className={styles.status} aria-label="Estado del piloto" data-lg-glass-panel="status">
                      <span className={styles.liveDot} aria-hidden="true" />
                      <span>
                        <strong>{active.name}</strong>
                        <span>{active.label}</span>
                      </span>
                    </div>
                  </div>
                </header>

                <section className={styles.directorHero} aria-labelledby="liquid-title" data-lg-glass-panel="hero">
                  <div className={styles.directorBackdrop} aria-hidden="true" />

                  <div className={styles.heroCopy}>
                    <p className={styles.kicker}>SURFACE VISUAL GOVERNOR · FAMILY DIRECTOR</p>
                    <h1 id="liquid-title" className={styles.directorTitle}>
                      <span>{active.name}</span>
                      <span>manda</span>
                    </h1>
                    <p className={styles.lead}>
                      Esta versión usa ScrollArea para que el fondo se quede quieto, Tabs/Select para cambiar familia sin botones globales azules, Tooltip para explicar intención visual, Slot para acciones semánticas y OGL como aura ligera, no como circo WebGL.
                    </p>

                    <Tabs.List className={styles.directorPills} aria-label="Selector de familias Liquid Glass">
                      {families.map((family) => {
                        return (
                          <Tooltip.Root key={family.id}>
                            <Tabs.Trigger asChild value={family.id}>
                              <Tooltip.Trigger asChild>
                                <span
                                  className={styles.familyPill}
                                  data-lg-glass-panel="family-pill"
                                  data-lg-family={family.id}
                                >
                                  <span>{family.label}</span>
                                  <strong>{family.name}</strong>
                                </span>
                              </Tooltip.Trigger>
                            </Tabs.Trigger>
                            <Tooltip.Portal>
                              <Tooltip.Content className={styles.tooltipContent} side="top" sideOffset={10}>
                                {family.mood}
                                <Tooltip.Arrow className={styles.tooltipArrow} />
                              </Tooltip.Content>
                            </Tooltip.Portal>
                          </Tooltip.Root>
                        );
                      })}
                    </Tabs.List>

                    <div className={styles.actions} aria-label="Contratos del piloto">
                      <GlassLink href="/surface-visual-governor/liquid-glass/latest/index.json" primary>Manifest latest</GlassLink>
                      <GlassLink href="/surface-visual-governor/liquid-glass/latest/route-budget.liquid-glass.pilot-20.json">Route budget</GlassLink>
                      <GlassLink href="/laboratorio-pc/referencia-visual">Volver</GlassLink>
                    </div>
                  </div>

                  <aside className={styles.directorPoster} aria-label={`Familia activa ${active.name}`}>
                    <div className={styles.posterImage} />
                    <div className={styles.posterGlass} data-lg-glass-panel="poster-glass">
                      <p className={styles.eyebrow}>{active.label}</p>
                      <h2>{active.name}</h2>
                      <p>{active.mood}</p>
                      <code>{active.url}</code>
                    </div>
                  </aside>
                </section>

                <section className={styles.familyBoard} aria-label="Familias del Governor">
                  {families.map((family) => {
                    return (
                      <article
                        className={styles.familyCard}
                        data-active={family.id === active.id ? "true" : "false"}
                        data-lg-glass-panel="family-card"
                        key={family.id}
                      >
                        <div className={styles.familyImage} aria-hidden="true" />
                        <div className={styles.familyInfo}>
                          <p className={styles.eyebrow}>{family.label}</p>
                          <h2>{family.name}</h2>
                          <p>{family.mood}</p>
                          <span
                            className={styles.familyCardAction}
                            data-lg-glass-panel="card-action"
                            role="button"
                            tabIndex={0}
                            aria-pressed={family.id === active.id}
                            onClick={() => setActiveId(family.id)}
                            onKeyDown={(event) => {
                              if (event.key === "Enter" || event.key === " ") {
                                event.preventDefault();
                                setActiveId(family.id);
                              }
                            }}
                          >
                            Usar familia
                          </span>
                        </div>
                      </article>
                    );
                  })}
                </section>

                <section className={styles.warningBand} aria-label="Reglas del Governor" data-lg-glass-panel="warning-band">
                  <h2>Gate anti-desmadre visual</h2>
                  <p>
                    Este Director Cut es showcase de referencia. Puede verse sabroso, pero no se embarra en operación diaria sin gate: POS, Checkout y Tablet productiva siguen bloqueados. DB y deploy ni se tocan.
                  </p>
                  <div className={styles.codeList}>
                    <code>Default family: aurora-night</code>
                    <code>Allowed route: /referencia-visual/liquid-glass</code>
                    <code>Forbidden: POS · Checkout · Tablet productiva · DB · deploy</code>
                    <code>Mode: Radix + OGL reference, no package.json changes</code>
                  </div>
                </section>
              </div>
            </ScrollArea.Viewport>
            <ScrollArea.Scrollbar className={styles.scrollbar} orientation="vertical">
              <ScrollArea.Thumb className={styles.scrollThumb} />
            </ScrollArea.Scrollbar>
          </ScrollArea.Root>
        </Tabs.Root>
      </Tooltip.Provider>
    </main>
  );
}
