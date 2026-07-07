// PRISMA TABDEV1 TABLET ORIGINAL LAB SURFACE
// Uses the real Tablet shell as the development home for the portable TABLET LAB capsule.
// Dependency-free: no new npm, no CDN, no lockfile changes.
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletGenericSurfaceV2 } from "@components/tablet-visual-v2";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";
import styles from "./TabletLabCapsule.module.css";

const cards = [
  { k: "01", tag: "LICENCIA", title: "Asignar licencia", body: "Elige cliente y plan desde catálogo. Límites y módulos vienen gobernados.", items: ["Cliente", "Plan", "Módulos", "Confirmación"] },
  { k: "02", tag: "PLANES", title: "Catálogo de planes", body: "Tipos disponibles, límites y módulos incluidos para validar el flujo visual antes de tocar Tablet real.", items: ["Starter", "Pro", "Enterprise", "Governed"] },
  { k: "03", tag: "BRIDGE", title: "License Admin Bridge", body: "Puente conceptual para activate, refresh y revoke sin exponer credenciales ni acoplar UI a dependencias externas.", items: ["Activate", "Refresh", "Revoke", "Audit"] },
  { k: "04", tag: "MESA", title: "Mesa de licencias", body: "Asignaciones preparadas con folio LIC y contrato CTR en una maqueta portable de laboratorio.", items: ["LIC-YYYY-000001", "CTR-YYYY-000001", "Prepared", "Cloud-ready"] },
  { k: "05", tag: "REGLAS", title: "Reglas", body: "La cápsula vive dentro del shell original de Tablet como TSX local, CSS Module namespaced y cero dependencias nuevas.", items: ["Dependency-free", "Namespaced", "Rollbackable", "Tablet-safe"] },
  { k: "06", tag: "SALIDA", title: "Resultado", body: "Superficie aislada para desarrollar Tablet Light Cloudglass antes de migrar una piel a superficies reales.", items: ["Lab first", "Mesh first", "Original shell", "No fake green"] },
];

export const dynamic = "force-dynamic";

export const metadata = {
  title: "TABLET LAB - PRISMA Tablet",
  description: "Laboratorio visual aislado dentro del shell original de PRISMA Tablet."
};

function pendingCount(snapshot: Awaited<ReturnType<typeof getTabletRuntimeSnapshot>>) {
  return snapshot.connection.pendingEvents + snapshot.connection.failedEvents + snapshot.connection.conflictEvents;
}

export default async function TabletLabPage() {
  const snapshot = await getTabletRuntimeSnapshot(readRuntimeSnapshotInput());
  const pending = pendingCount(snapshot);

  return (
    <PrismaTabletShellUnified
      currentPath="/tablet-lab"
      title="Tablet Lab"
      subtitle="Cápsula portable ahora montada en el shell original de Tablet para desarrollar la piel clara sin tocar POS real."
      kicker="PRISMA Tablet Original"
      runtimeSnapshot={snapshot}
      visualSurface="tablet-lab"
      visualPreset="PRISMA_TABLET_LIGHT_CLOUDGLASS_LAB_0707"
      status={
        <TabletShellStatusPill tone={pending > 0 ? "warn" : "ok"}>
          {pending > 0 ? `${pending} pendiente(s)` : "LAB aislado"}
        </TabletShellStatusPill>
      }
    >
      <TabletGenericSurfaceV2
        routeId="/tablet-lab"
        title="Laboratorio visual Tablet"
        description="Zona aislada para evolucionar Tablet Light Cloudglass con el chrome real de Tablet, sin dependencias nuevas y sin tocar la operación de venta."
        statusLabel="Tablet-safe"
        metrics={[
          { label: "Modo", value: "LAB", detail: "Aislado" },
          { label: "Shell", value: "Original", detail: "Tablet" },
          { label: "Deps", value: "0", detail: "nuevas" }
        ]}
      >
        <main className={styles.labCanvas} data-tablet-lab-capsule="true" aria-label="PRISMA TABLET LAB Capsule">
          <section className={styles.hero}>
            <span className={styles.kicker}>TABLET LAB</span>
            <h2>Cápsula portable basada en Entitlements</h2>
            <p>Laboratorio visual montado en Tablet original para preparar una piel clara Tablet Light Cloudglass sin tocar POS, checkout, carrito, dependencias, lockfiles, puertos ni Prisma.</p>
            <div className={styles.rail} aria-label="Portability checks">
              <span>Shell original</span>
              <span>TSX local</span>
              <span>CSS Module</span>
              <span>Sin npm nuevo</span>
              <span>Rollback listo</span>
            </div>
          </section>

          <section className={styles.grid} aria-label="Tablet Lab cards">
            {cards.map((card) => (
              <article className={styles.card} key={card.k} data-tablet-lab-card={card.k}>
                <div className={styles.cardTopline}><span>{card.k}</span><strong>{card.tag}</strong></div>
                <h3>{card.title}</h3>
                <p>{card.body}</p>
                <div className={styles.chipRow}>{card.items.map((item) => (<span key={item}>{item}</span>))}</div>
              </article>
            ))}
          </section>

          <section className={styles.sentinel} data-portability="tablet-original-ready">
            <strong>Portability Gate</strong>
            <span>Esta surface ya vive en el shell original de Tablet y sigue sin depender de Entitlements renderer, npm, CDN ni assets obligatorios raros.</span>
          </section>
        </main>
      </TabletGenericSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
