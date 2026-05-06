import type { ReactNode } from "react";
import { notFound } from "next/navigation";
import { getVertical } from "@/content/verticals";
import { CtaBand } from "./CtaBand";

type IconMap = Record<string, ReactNode>;

const surfaceIcons: IconMap = {
  Tablet: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="3" width="16" height="18" rx="3" />
      <path d="M8 19h8" />
      <path d="M9 7h6" />
    </svg>
  ),
  PC: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="12" rx="2" />
      <path d="M8 20h8" />
      <path d="M12 16v4" />
      <path d="M7 9h4" />
      <path d="M14 9h3" />
    </svg>
  ),
  Mobile: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="7" y="2" width="10" height="20" rx="3" />
      <path d="M10 6h4" />
      <circle cx="12" cy="18" r="1" />
    </svg>
  ),
  Core: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 3v3" />
      <path d="M12 18v3" />
      <path d="M3 12h3" />
      <path d="M18 12h3" />
      <path d="M5.6 5.6l2.1 2.1" />
      <path d="M16.3 16.3l2.1 2.1" />
      <path d="M18.4 5.6l-2.1 2.1" />
      <path d="M7.7 16.3l-2.1 2.1" />
    </svg>
  ),
  Control: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 8l6-4 6 4v5a6 6 0 0 1-12 0V8Z" />
      <path d="M9.5 12.5l1.6 1.6 3.4-3.6" />
    </svg>
  ),
};

const proofIcons: IconMap = {
  decision: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  ),
  alert: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 16v-5a6 6 0 0 0-12 0v5l-1.5 1.5h15L18 16Z" />
      <path d="M10 20h4" />
      <path d="M12 7v5" />
    </svg>
  ),
  responsible: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="8" r="3" />
      <path d="M5.5 20a6.5 6.5 0 0 1 13 0" />
    </svg>
  ),
  audit: (
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 3h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
      <path d="M9 8h6" />
      <path d="M9 12h6" />
      <path d="M9 16h3" />
    </svg>
  ),
};

const intelIcons: IconMap = {
  audience: proofIcons.responsible,
  flow: surfaceIcons.Core,
  signal: proofIcons.alert,
};


const verticalFlavors = {
  commerce: {
    spineTitle: "Venta, caja e inventario conectados.",
    spineIntro: "Tablet vende → PC concilia → Mobile avisa → Core registra → Commerce cierra.",
    proofTitle: "Cada venta termina con evidencia.",
    proofBadge: "Caja al día",
    signalText: "Venta → caja → corte",
    telemetry: {
      live: "Venta en vivo",
      alert: "Stock bajo",
      audit: "Corte listo",
      decision: "Ticket generado",
    },
    roles: {
      tablet: "Vende",
      pc: "Concilia",
      mobile: "Avisa",
      core: "Registra",
      control: "Cierra",
    },
    proof: [
      { title: "Ticket generado", detail: "Cada venta queda ligada a caja, producto y responsable.", icon: "decision" },
      { title: "Caja trazable", detail: "Cobros, cortes y movimientos quedan listos para revisar.", icon: "audit" },
      { title: "Inventario movido", detail: "El stock cambia con la operación, no con capturas sueltas.", icon: "alert" },
      { title: "Reporte diario", detail: "Ventas y cortes quedan resumidos para decidir rápido.", icon: "responsible" },
    ],
  },
  industrial: {
    spineTitle: "Activos, lecturas y mantenimiento bajo control.",
    spineIntro: "Tablet registra → PC analiza → Mobile alerta → Core normaliza → Industrial evidencia.",
    proofTitle: "No pasa si no deja evidencia técnica.",
    proofBadge: "Rango vigilado",
    signalText: "Lectura → alerta → mantenimiento",
    telemetry: {
      live: "Lectura activa",
      alert: "Rango crítico",
      audit: "Bitácora lista",
      decision: "Mantenimiento claro",
    },
    roles: {
      tablet: "Registra",
      pc: "Analiza",
      mobile: "Alerta",
      core: "Normaliza",
      control: "Evidencia",
    },
    proof: [
      { title: "Ficha de activo", detail: "Equipo, ubicación y responsable quedan identificados.", icon: "audit" },
      { title: "Lectura técnica", detail: "Valores y rangos quedan visibles antes de fallar.", icon: "alert" },
      { title: "Mantenimiento", detail: "Acciones técnicas quedan ligadas a fecha y responsable.", icon: "responsible" },
      { title: "Foto de evidencia", detail: "La operación técnica queda comprobable.", icon: "decision" },
    ],
  },
  field: {
    spineTitle: "Órdenes de trabajo que sí regresan con prueba.",
    spineIntro: "Tablet asigna → PC coordina → Mobile reporta → Core sincroniza → Field cierra.",
    proofTitle: "Trabajo cerrado solo con evidencia.",
    proofBadge: "Ruta activa",
    signalText: "Orden → checklist → cierre",
    telemetry: {
      live: "Ruta en curso",
      alert: "Orden pendiente",
      audit: "Checklist completo",
      decision: "Cierre validado",
    },
    roles: {
      tablet: "Asigna",
      pc: "Coordina",
      mobile: "Reporta",
      core: "Sincroniza",
      control: "Cierra",
    },
    proof: [
      { title: "Orden asignada", detail: "Cada trabajo inicia con responsable y estado claro.", icon: "responsible" },
      { title: "Checklist completo", detail: "Las tareas quedan marcadas con avance real.", icon: "decision" },
      { title: "Evidencia capturada", detail: "Fotos, notas o firmas acompañan el cierre.", icon: "audit" },
      { title: "Sincronización", detail: "El equipo en campo reporta sin perseguir mensajes.", icon: "alert" },
    ],
  },
  control: {
    spineTitle: "Una cadena de comando conectada.",
    spineIntro: "Tablet captura → PC analiza → Mobile avisa → Core normaliza → Control consolida.",
    proofTitle: "No entra si no deja prueba.",
    proofBadge: "Control activo",
    signalText: "Alerta → decisión → auditoría",
    telemetry: {
      live: "En vivo",
      alert: "Alerta crítica",
      audit: "Auditoría activa",
      decision: "Decisión clara",
    },
    roles: {
      tablet: "Captura",
      pc: "Analiza",
      mobile: "Avisa",
      core: "Normaliza",
      control: "Consolida",
    },
    proof: [
      { title: "Resumen diario", detail: "Ventas, caja y alertas listas para revisar.", icon: "decision" },
      { title: "Alertas críticas", detail: "Señales claras antes de que el problema crezca.", icon: "alert" },
      { title: "Responsable visible", detail: "Cada acción queda ligada a alguien.", icon: "responsible" },
      { title: "Auditoría de cambios", detail: "Historial para decidir sin perseguir capturas.", icon: "audit" },
    ],
  },
} satisfies Record<string, {
  spineTitle: string;
  spineIntro: string;
  proofTitle: string;
  proofBadge: string;
  signalText: string;
  telemetry: {
    live: string;
    alert: string;
    audit: string;
    decision: string;
  };
  roles: {
    tablet: string;
    pc: string;
    mobile: string;
    core: string;
    control: string;
  };
  proof: Array<{
    title: string;
    detail: string;
    icon: keyof typeof proofIcons;
  }>;
}>;

export function VerticalPage({ slug }: { slug: string }) {
  const vertical = getVertical(slug);
  if (!vertical) notFound();
  const verticalSlug = vertical.slug as string;

  const isControl = vertical.slug === "control";
  const flavor = verticalFlavors[vertical.slug] ?? verticalFlavors.control;

  const surfaces = [
    { name: "Tablet", role: flavor.roles.tablet, description: vertical.surfaces.tablet },
    { name: "PC", role: flavor.roles.pc, description: vertical.surfaces.pc },
    { name: "Mobile", role: flavor.roles.mobile, description: vertical.surfaces.mobile },
    { name: "Core", role: flavor.roles.core, description: vertical.surfaces.core },
    { name: "Control", role: flavor.roles.control, description: vertical.surfaces.control },
  ];

  const proofCards = flavor.proof.map((item) => ({
    title: item.title,
    detail: item.detail,
    icon: proofIcons[item.icon] ?? proofIcons.decision,
  }));


  if (verticalSlug === "industrial") {
    const industrialProof = [
      {
        title: "Ficha de activo",
        detail: "Equipo, ubicación y responsable quedan identificados.",
        icon: proofIcons.audit,
      },
      {
        title: "Lectura técnica",
        detail: "Rangos, mediciones y variaciones quedan visibles antes de fallar.",
        icon: proofIcons.alert,
      },
      {
        title: "Mantenimiento",
        detail: "Acciones técnicas quedan ligadas a fecha, evidencia y responsable.",
        icon: proofIcons.responsible,
      },
      {
        title: "Foto de evidencia",
        detail: "La operación técnica queda comprobable sin perseguir capturas.",
        icon: proofIcons.decision,
      },
    ];

    return (
      <>
        <section className="industrial-v2-page">
          <div className="industrial-v2-hero">
            <div className="industrial-v2-copy">
              <p className="industrial-v2-eyebrow">PRISMA INDUSTRIAL</p>
              <h1>{vertical.headline}</h1>
              <p>{vertical.promise}</p>

              <div className="industrial-v2-specs" aria-label="Resumen industrial">
                <div>
                  <span>Activos</span>
                  <strong>controlados</strong>
                  <small>{vertical.audience}</small>
                </div>
                <div>
                  <span>Flujo técnico</span>
                  <strong>{vertical.flow.slice(0, 3).join(" → ")}</strong>
                  <small>{vertical.flow.slice(3).join(" → ")}</small>
                </div>
                <div>
                  <span>Evidencia</span>
                  <strong>lectura · rango · mantenimiento</strong>
                  <small>bitácora lista para auditoría</small>
                </div>
              </div>
            </div>

            <div className="industrial-v2-stage" aria-label={`PRISMA ${vertical.name}`}>
              <div className="industrial-v2-frame">
                <img src={vertical.image} alt={`Pantalla de PRISMA ${vertical.name}`} />
                <span className="industrial-v2-tag tag-a">Lectura activa</span>
                <span className="industrial-v2-tag tag-b">Rango crítico</span>
                <span className="industrial-v2-tag tag-c">Bitácora lista</span>
              </div>

              <div className="industrial-v2-meters">
                <div>
                  <span>24</span>
                  <small>activos</small>
                </div>
                <div>
                  <span>156</span>
                  <small>lecturas</small>
                </div>
                <div>
                  <span>08</span>
                  <small>pendientes</small>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="industrial-v2-board">
          <div className="industrial-v2-board-head">
            <p className="industrial-v2-eyebrow">SUPERFICIES</p>
            <h2>Del activo a la evidencia técnica.</h2>
            <p>Tablet registra lecturas, PC analiza rangos, Mobile alerta, Core normaliza y Control deja trazabilidad.</p>
          </div>

          <div className="industrial-v2-process" aria-label="Flujo industrial PRISMA">
            {surfaces.map((surface, index) => (
              <article className="industrial-v2-process-item" key={surface.name}>
                <div className="industrial-v2-process-icon">
                  {surfaceIcons[surface.name] ?? surfaceIcons.Core}
                </div>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h3>{surface.name}</h3>
                <b>{surface.role}</b>
                <p>{surface.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="industrial-v2-proof">
          <div className="industrial-v2-proof-card">
            <div className="industrial-v2-proof-head">
              <p className="industrial-v2-eyebrow">BITÁCORA TÉCNICA</p>
              <h2>No pasa si no deja evidencia.</h2>
              <span>Rango vigilado</span>
            </div>

            <div className="industrial-v2-log">
              {industrialProof.map((item, index) => (
                <article key={item.title}>
                  <span className="industrial-v2-log-number">{String(index + 1).padStart(2, "0")}</span>
                  <span className="industrial-v2-log-icon">{item.icon}</span>
                  <div>
                    <h3>{item.title}</h3>
                    <p>{item.detail}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <CtaBand />

        <style>{`
          .industrial-v2-page {
            position: relative;
            overflow: hidden;
            padding: clamp(4.5rem, 7vw, 7.5rem) 1.5rem clamp(3rem, 5vw, 5rem);
            background:
              linear-gradient(115deg, rgba(15,23,42,0.045) 0 1px, transparent 1px 92px),
              linear-gradient(25deg, rgba(251,191,36,0.055) 0 1px, transparent 1px 120px),
              radial-gradient(circle at 78% 18%, rgba(251,191,36,0.16), transparent 34rem),
              linear-gradient(180deg, #fbfcff 0%, #edf2f7 100%);
            color: #0b1224;
          }

          .industrial-v2-hero {
            max-width: 1360px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: minmax(360px, 0.68fr) minmax(620px, 1.32fr);
            gap: clamp(2.5rem, 5vw, 5.5rem);
            align-items: center;
          }

          .industrial-v2-eyebrow {
            margin: 0 0 1rem;
            color: #b7791f;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.74rem;
            font-weight: 950;
          }

          .industrial-v2-copy h1 {
            margin: 0;
            max-width: 640px;
            font-size: clamp(3.35rem, 5.6vw, 6.8rem);
            line-height: 0.9;
            letter-spacing: -0.065em;
            font-weight: 950;
          }

          .industrial-v2-copy > p:not(.industrial-v2-eyebrow) {
            max-width: 620px;
            margin: 1.35rem 0 0;
            color: #405066;
            font-size: clamp(1.05rem, 1.2vw, 1.25rem);
            line-height: 1.75;
          }

          .industrial-v2-specs {
            margin-top: 2rem;
            display: grid;
            gap: 0.75rem;
            max-width: 620px;
          }

          .industrial-v2-specs div {
            padding: 1rem 1.1rem;
            border-radius: 1rem;
            background: rgba(255,255,255,0.74);
            border: 1px solid rgba(251,191,36,0.24);
            box-shadow: 0 16px 35px rgba(15,23,42,0.07), inset 4px 0 0 rgba(251,191,36,0.32);
          }

          .industrial-v2-specs span {
            display: block;
            color: #b7791f;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.68rem;
            font-weight: 950;
          }

          .industrial-v2-specs strong {
            display: block;
            margin-top: 0.25rem;
            color: #0f172a;
            font-size: 1rem;
            line-height: 1.35;
          }

          .industrial-v2-specs small {
            display: block;
            margin-top: 0.25rem;
            color: #475569;
            line-height: 1.45;
          }

          .industrial-v2-stage {
            position: relative;
            display: grid;
            place-items: center;
          }

          .industrial-v2-frame {
            position: relative;
            width: min(100%, 900px);
            padding: 1rem;
            border-radius: 2rem;
            background:
              linear-gradient(145deg, rgba(8,12,18,0.98), rgba(18,24,33,0.98)),
              radial-gradient(circle at 60% 0%, rgba(251,191,36,0.22), transparent 45%);
            border: 1px solid rgba(251,191,36,0.28);
            box-shadow: 0 64px 150px rgba(15,23,42,0.42), 0 0 100px rgba(251,191,36,0.18);
            animation: industrialV2Float 7s ease-in-out infinite;
          }

          .industrial-v2-frame img {
            display: block;
            width: 100%;
            border-radius: 1.35rem;
            box-shadow: 0 20px 65px rgba(0,0,0,0.45);
          }

          .industrial-v2-tag {
            position: absolute;
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.65rem 0.85rem;
            background: rgba(10,14,20,0.84);
            border: 1px solid rgba(251,191,36,0.28);
            color: #fde68a;
            font-size: 0.78rem;
            font-weight: 900;
            box-shadow: 0 16px 35px rgba(15,23,42,0.28);
          }

          .tag-a { top: 8%; left: 5%; }
          .tag-b { top: 14%; right: -2%; }
          .tag-c { bottom: 10%; left: -3%; }

          .industrial-v2-meters {
            position: relative;
            z-index: 2;
            width: min(92%, 760px);
            margin: -1.2rem auto 0;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.8rem;
            padding: 0.8rem;
            border-radius: 1.35rem;
            background: linear-gradient(180deg, rgba(8,12,18,0.9), rgba(17,24,39,0.78));
            border: 1px solid rgba(251,191,36,0.25);
            box-shadow: 0 24px 70px rgba(15,23,42,0.22);
          }

          .industrial-v2-meters div {
            padding: 0.85rem 1rem;
            border-radius: 0.95rem;
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(148,163,184,0.14);
          }

          .industrial-v2-meters span {
            display: block;
            color: #ffffff;
            font-size: 2rem;
            font-weight: 950;
            line-height: 1;
          }

          .industrial-v2-meters small {
            color: #fbbf24;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.66rem;
            font-weight: 900;
          }

          .industrial-v2-board {
            padding: clamp(4.5rem, 7vw, 7rem) 1.5rem;
            background:
              linear-gradient(115deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 84px),
              radial-gradient(circle at 76% 0%, rgba(251,191,36,0.14), transparent 30rem),
              linear-gradient(180deg, #101827 0%, #111827 100%);
            color: #f8fafc;
          }

          .industrial-v2-board-head {
            max-width: 1280px;
            margin: 0 auto 2rem;
            display: grid;
            grid-template-columns: minmax(0, 0.8fr) minmax(280px, 0.7fr);
            gap: 2rem;
            align-items: end;
          }

          .industrial-v2-board-head h2,
          .industrial-v2-proof-head h2 {
            margin: 0;
            max-width: 760px;
            color: #ffffff;
            font-size: clamp(2.7rem, 4.8vw, 5.8rem);
            line-height: 0.92;
            letter-spacing: -0.065em;
            font-weight: 950;
          }

          .industrial-v2-board-head > p {
            color: rgba(226,232,240,0.76);
            line-height: 1.8;
          }

          .industrial-v2-process {
            max-width: 1280px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.85rem;
            padding: 1.1rem;
            border-radius: 1.2rem;
            background:
              linear-gradient(180deg, rgba(15,23,42,0.9), rgba(17,24,39,0.76));
            border: 1px solid rgba(251,191,36,0.25);
            box-shadow: 0 36px 90px rgba(0,0,0,0.22);
          }

          .industrial-v2-process-item {
            position: relative;
            min-height: 15rem;
            padding: 1rem;
            border-radius: 0.85rem;
            background: rgba(15,23,42,0.48);
            border: 1px solid rgba(148,163,184,0.16);
            transition: transform 180ms ease, border-color 180ms ease;
          }

          .industrial-v2-process-item:hover {
            transform: translateY(-6px);
            border-color: rgba(251,191,36,0.38);
          }

          .industrial-v2-process-item:last-child {
            border-color: rgba(251,191,36,0.62);
            background: linear-gradient(180deg, rgba(251,191,36,0.16), rgba(15,23,42,0.72));
          }

          .industrial-v2-process-icon {
            display: grid;
            place-items: center;
            width: 3rem;
            height: 3rem;
            border-radius: 0.9rem;
            color: #fbbf24;
            background: rgba(251,191,36,0.12);
            border: 1px solid rgba(251,191,36,0.25);
          }

          .industrial-v2-process-icon svg {
            width: 1.35rem;
            height: 1.35rem;
          }

          .industrial-v2-process-item > span {
            position: absolute;
            right: 1rem;
            top: 1rem;
            color: #fbbf24;
            font-weight: 950;
          }

          .industrial-v2-process-item h3 {
            margin: 1.25rem 0 0.25rem;
            color: #ffffff;
          }

          .industrial-v2-process-item b {
            display: block;
            color: #fbbf24;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.7rem;
            margin-bottom: 0.75rem;
          }

          .industrial-v2-process-item p {
            margin: 0;
            color: rgba(226,232,240,0.75);
            line-height: 1.6;
            font-size: 0.9rem;
          }

          .industrial-v2-proof {
            padding: clamp(4.5rem, 7vw, 7rem) 1.5rem;
            background:
              radial-gradient(circle at 78% 0%, rgba(251,191,36,0.12), transparent 28rem),
              linear-gradient(180deg, #111827 0%, #e8f1fb 100%);
          }

          .industrial-v2-proof-card {
            position: relative;
            overflow: hidden;
            max-width: 1280px;
            margin: 0 auto;
            padding: clamp(2.5rem, 4.5vw, 4.5rem);
            border-radius: 1.2rem;
            background:
              radial-gradient(circle at 86% 12%, rgba(251,191,36,0.22), transparent 28rem),
              linear-gradient(135deg, #080f19 0%, #171b22 52%, #2a2114 100%);
            border: 1px solid rgba(251,191,36,0.24);
            box-shadow: 0 42px 105px rgba(15,23,42,0.24);
            color: #ffffff;
          }

          .industrial-v2-proof-card::before {
            content: "TECHNICAL EVIDENCE LOG";
            position: absolute;
            right: 2rem;
            bottom: 1.35rem;
            color: rgba(251,191,36,0.15);
            font-size: clamp(1.8rem, 4vw, 4.8rem);
            letter-spacing: 0.08em;
            font-weight: 950;
            pointer-events: none;
          }

          .industrial-v2-proof-head {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 1.5rem;
            align-items: start;
            margin-bottom: 2.5rem;
          }

          .industrial-v2-proof-head span {
            justify-self: end;
            border-radius: 999px;
            padding: 0.72rem 1rem;
            color: #fde68a;
            background: rgba(251,191,36,0.11);
            border: 1px solid rgba(251,191,36,0.3);
            font-weight: 900;
          }

          .industrial-v2-log {
            position: relative;
            z-index: 1;
            display: grid;
            gap: 0.85rem;
          }

          .industrial-v2-log article {
            display: grid;
            grid-template-columns: 3rem 3rem minmax(0, 1fr);
            gap: 0.9rem;
            align-items: center;
            padding: 1rem 1.1rem;
            border-radius: 0.75rem;
            background: linear-gradient(90deg, rgba(251,191,36,0.08), rgba(255,255,255,0.025));
            border: 1px solid rgba(251,191,36,0.16);
          }

          .industrial-v2-log-number {
            color: #fbbf24;
            font-weight: 950;
          }

          .industrial-v2-log-icon {
            display: grid;
            place-items: center;
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 0.85rem;
            color: #fde68a;
            background: rgba(251,191,36,0.11);
            border: 1px solid rgba(251,191,36,0.22);
          }

          .industrial-v2-log-icon svg {
            width: 1.15rem;
            height: 1.15rem;
          }

          .industrial-v2-log h3 {
            margin: 0 0 0.2rem;
            color: #ffffff;
          }

          .industrial-v2-log p {
            margin: 0;
            color: rgba(226,232,240,0.78);
            line-height: 1.55;
          }

          @keyframes industrialV2Float {
            0%, 100% { transform: translateY(0) rotateX(1deg) rotateY(-3deg); }
            50% { transform: translateY(-10px) rotateX(1deg) rotateY(-2deg); }
          }

          @media (max-width: 1180px) {
            .industrial-v2-hero,
            .industrial-v2-board-head,
            .industrial-v2-proof-head {
              grid-template-columns: 1fr;
            }

            .industrial-v2-process {
              grid-template-columns: 1fr;
            }

            .industrial-v2-frame {
              animation: none;
            }
          }

          @media (max-width: 760px) {
            .industrial-v2-page,
            .industrial-v2-board,
            .industrial-v2-proof {
              padding-left: 1rem;
              padding-right: 1rem;
            }

            .industrial-v2-copy h1,
            .industrial-v2-board-head h2,
            .industrial-v2-proof-head h2 {
              font-size: clamp(2.65rem, 11vw, 4rem);
            }

            .industrial-v2-meters {
              grid-template-columns: 1fr;
            }

            .industrial-v2-tag {
              position: relative;
              inset: auto;
              margin: 0.4rem 0.25rem 0 0;
            }

            .industrial-v2-frame {
              display: flex;
              flex-wrap: wrap;
            }

            .industrial-v2-frame img {
              flex-basis: 100%;
            }

            .industrial-v2-log article {
              grid-template-columns: 2.5rem minmax(0, 1fr);
            }

            .industrial-v2-log-number {
              display: none;
            }
          }

          @media (prefers-reduced-motion: reduce) {
            .industrial-v2-frame {
              animation: none !important;
            }

            .industrial-v2-process-item {
              transition: none !important;
            }
          }
  
        /* Industrial V2 final composition tuning */
        .industrial-v2-hero {
          grid-template-columns: minmax(460px, 0.78fr) minmax(600px, 1.22fr) !important;
          gap: clamp(3rem, 5vw, 5.75rem) !important;
        }

        .industrial-v2-copy h1 {
          max-width: 760px !important;
          font-size: clamp(3.15rem, 4.65vw, 5.85rem) !important;
          line-height: 0.94 !important;
          letter-spacing: -0.058em !important;
          text-wrap: balance;
        }

        .industrial-v2-copy > p:not(.industrial-v2-eyebrow) {
          max-width: 680px !important;
          font-size: clamp(1.08rem, 1.25vw, 1.28rem) !important;
        }

        .industrial-v2-specs {
          max-width: 680px !important;
        }

        .industrial-v2-stage {
          transform: translateX(0.5rem);
        }

        .industrial-v2-frame {
          width: min(104%, 960px) !important;
        }

        .industrial-v2-board-head {
          grid-template-columns: minmax(0, 1fr) !important;
          gap: 1rem !important;
          margin-bottom: 2.4rem !important;
        }

        .industrial-v2-board-head h2 {
          max-width: 820px !important;
          font-size: clamp(2.9rem, 4.35vw, 5.25rem) !important;
          line-height: 0.94 !important;
        }

        .industrial-v2-board-head > p {
          max-width: 760px !important;
          margin: 0 !important;
          font-size: 1.05rem !important;
        }

        .industrial-v2-process {
          grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
          gap: 1rem !important;
          padding: 1.25rem !important;
        }

        .industrial-v2-process-item {
          min-height: 16.5rem !important;
          padding: 1.15rem !important;
        }

        .industrial-v2-process-item h3 {
          font-size: 1.12rem !important;
        }

        .industrial-v2-process-item p {
          font-size: 0.94rem !important;
          line-height: 1.68 !important;
        }

        .industrial-v2-process-item:last-child {
          transform: translateY(-0.25rem);
          box-shadow:
            0 0 0 1px rgba(251,191,36,0.18) inset,
            0 22px 60px rgba(251,191,36,0.08);
        }

        .industrial-v2-proof-head {
          grid-template-columns: minmax(0, 1fr) auto !important;
          align-items: start !important;
        }

        .industrial-v2-proof-head h2 {
          max-width: 760px !important;
          text-align: left !important;
          font-size: clamp(2.65rem, 4vw, 4.7rem) !important;
          line-height: 0.96 !important;
        }

        .industrial-v2-log article {
          padding: 1.1rem 1.2rem !important;
        }

        @media (max-width: 1180px) {
          .industrial-v2-hero {
            grid-template-columns: 1fr !important;
          }

          .industrial-v2-stage {
            transform: none !important;
          }

          .industrial-v2-copy h1 {
            max-width: 900px !important;
          }

          .industrial-v2-process {
            grid-template-columns: 1fr !important;
          }

          .industrial-v2-process-item {
            min-height: auto !important;
          }
        }

        @media (max-width: 760px) {
          .industrial-v2-copy h1 {
            font-size: clamp(2.75rem, 11vw, 4rem) !important;
          }

          .industrial-v2-board-head h2,
          .industrial-v2-proof-head h2 {
            font-size: clamp(2.35rem, 10vw, 3.5rem) !important;
          }

          .industrial-v2-proof-head {
            grid-template-columns: 1fr !important;
          }
        }

      `}</style>
      </>
    );
  }


  return (
    <>
      <section className={`vertical-product-page vertical-${vertical.slug}${isControl ? " control-mode" : ""}`}>
        <div className="vertical-ambient" aria-hidden="true" />

        <div className="vertical-hero">
          <div className="hero-copy">
            <p className="eyebrow">PRISMA {vertical.name}</p>
            <h1>{vertical.headline}</h1>
            <p className="hero-lead">{vertical.promise}</p>

            <div className="intel-rail" aria-label="Datos principales del vertical">
              <div className="intel-entry">
                <span className="intel-icon">{intelIcons.audience}</span>
                <span>
                  <b>Para quién</b>
                  <small>{vertical.audience}</small>
                </span>
              </div>

              <div className="intel-entry intel-entry-wide">
                <span className="intel-icon">{intelIcons.flow}</span>
                <span>
                  <b>Flujo {vertical.name}</b>
                  <small>{vertical.flow.join(" → ")}</small>
                </span>
              </div>

              <div className="intel-entry">
                <span className="intel-icon">{intelIcons.signal}</span>
                <span>
                  <b>Señales clave</b>
                  <small>{flavor.signalText}</small>
                </span>
              </div>
            </div>
          </div>

          <div className="product-stage" aria-label={`Vista de producto PRISMA ${vertical.name}`}>
            <div className="stage-orbit" aria-hidden="true" />
            <div className="dashboard-console">
              <img src={vertical.image} alt={`Pantalla de PRISMA ${vertical.name}`} />
              <div className="console-scan" aria-hidden="true" />
              <div className="telemetry telemetry-live">
                <span className="telemetry-dot" />
                <b>{flavor.telemetry.live}</b>
              </div>
              <div className="telemetry telemetry-alert">
                <span className="telemetry-dot warning" />
                <b>{flavor.telemetry.alert}</b>
              </div>
              <div className="telemetry telemetry-audit">
                <span className="telemetry-dot gold" />
                <b>{flavor.telemetry.audit}</b>
              </div>
              <div className="telemetry telemetry-decision">
                <span className="telemetry-dot ok" />
                <b>{flavor.telemetry.decision}</b>
              </div>
            </div>
          </div>

        </div>
      </section>

      <section className={`command-section command-${vertical.slug}`}>
        <div className="command-header">
          <div>
            <p className="eyebrow">Superficies</p>
            <h2>{flavor.spineTitle}</h2>
          </div>
          <p>{flavor.spineIntro}</p>
        </div>


        <div className="command-spine" aria-label="Cadena operativa PRISMA">
          <div className="spine-line" aria-hidden="true" />
          <div className="spine-signal" aria-hidden="true" />

          {surfaces.map((surface, index) => {
            const isFinal = surface.name === "Control";
            return (
              <article className={`command-node${isFinal ? " command-node-final" : ""}`} key={surface.name}>
                <div className="node-top">
                  <span className="node-number">{String(index + 1).padStart(2, "0")}</span>
                  <span className="node-icon">{surfaceIcons[surface.name] ?? surfaceIcons.Core}</span>
                </div>
                <div>
                  <p className="node-role">{surface.role}</p>
                  <h3>{surface.name}</h3>
                  <p>{surface.description}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className={`proof-section proof-final-section proof-${vertical.slug}`}>
        <div className="proof-final-console">
          <div className="proof-final-glow" aria-hidden="true" />

          <div className="proof-final-heading">
            <p className="eyebrow">Aceptación</p>
            <h2>{flavor.proofTitle}</h2>
            <span>{flavor.proofBadge}</span>
          </div>

          <div className="proof-final-log" aria-label="Evidencia operativa">
            {proofCards.map((card, index) => (
              <article className="proof-final-row" key={card.title}>
                <span className="proof-final-index">{String(index + 1).padStart(2, "0")}</span>
                <span className="proof-final-icon">{card.icon}</span>
                <span className="proof-final-copy">
                  <b>{card.title}</b>
                  <small>{card.detail}</small>
                </span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <CtaBand />

      <style>{`
        .vertical-product-page {
          position: relative;
          overflow: hidden;
          padding: clamp(4.75rem, 7vw, 7.5rem) 1.5rem clamp(3.5rem, 6vw, 5.5rem);
          background:
            radial-gradient(circle at 78% 18%, rgba(37, 99, 235, 0.18), transparent 34rem),
            radial-gradient(circle at 16% 78%, rgba(125, 211, 252, 0.14), transparent 30rem),
            linear-gradient(180deg, #f9fcff 0%, #edf5ff 100%);
          color: #0f172a;
        }

        .vertical-product-page::before {
          content: "";
          position: absolute;
          inset: 0;
          background:
            linear-gradient(115deg, transparent 0%, rgba(255,255,255,0.9) 35%, transparent 62%),
            radial-gradient(circle at 60% 48%, rgba(255,255,255,0.65), transparent 30rem);
          opacity: 0.9;
          pointer-events: none;
        }

        .vertical-ambient {
          position: absolute;
          inset: -12% -8%;
          background:
            radial-gradient(circle at 70% 24%, rgba(37, 99, 235, 0.16), transparent 35rem),
            radial-gradient(circle at 28% 74%, rgba(59, 130, 246, 0.13), transparent 28rem);
          filter: blur(4px);
          animation: prismaVerticalAmbient 16s ease-in-out infinite alternate;
          pointer-events: none;
        }

        .vertical-hero {
          position: relative;
          z-index: 1;
          max-width: 1360px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: minmax(380px, 0.72fr) minmax(560px, 1.28fr);
          gap: clamp(2.5rem, 5vw, 5.5rem);
          align-items: center;
        }

        .hero-copy {
          min-width: 0;
        }

        .eyebrow {
          margin: 0 0 1rem;
          text-transform: uppercase;
          letter-spacing: 0.22em;
          color: #2563eb;
          font-size: 0.76rem;
          line-height: 1;
          font-weight: 950;
        }

        .hero-copy h1 {
          max-width: 620px;
          margin: 0;
          color: #081225;
          font-size: clamp(3.15rem, 5vw, 6.05rem);
          line-height: 0.93;
          letter-spacing: -0.065em;
          font-weight: 950;
          text-wrap: balance;
        }

        .hero-lead {
          max-width: 640px;
          margin: 1.35rem 0 0;
          color: #42526a;
          font-size: clamp(1.05rem, 1.25vw, 1.26rem);
          line-height: 1.75;
        }

        .intel-rail {
          margin-top: 1.8rem;
          display: grid;
          grid-template-columns: 1fr;
          gap: 0.72rem;
          max-width: 620px;
        }

        .intel-entry {
          position: relative;
          display: grid;
          grid-template-columns: 2.8rem minmax(0, 1fr);
          gap: 0.95rem;
          align-items: start;
          padding: 0.95rem 1rem;
          border-radius: 1.1rem;
          border: 1px solid rgba(37, 99, 235, 0.13);
          background: rgba(255, 255, 255, 0.72);
          box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
          backdrop-filter: blur(14px);
        }

        .intel-entry:nth-child(2) {
          margin-left: 1.15rem;
        }

        .intel-entry:nth-child(3) {
          margin-left: 2.3rem;
        }

        .intel-entry::before {
          content: "";
          position: absolute;
          left: -1.15rem;
          top: 50%;
          width: 1.15rem;
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(37,99,235,0.35));
        }

        .intel-entry:first-child::before {
          display: none;
        }

        .intel-icon {
          display: grid;
          place-items: center;
          width: 2.55rem;
          height: 2.55rem;
          border-radius: 0.9rem;
          color: #2563eb;
          background:
            radial-gradient(circle at 35% 22%, rgba(255,255,255,0.96), transparent 42%),
            linear-gradient(180deg, #dbeafe, #eff6ff);
          border: 1px solid rgba(37, 99, 235, 0.16);
          box-shadow: 0 10px 20px rgba(37,99,235,0.08);
        }

        .intel-icon svg {
          width: 1.2rem;
          height: 1.2rem;
        }

        .intel-entry b {
          display: block;
          margin-bottom: 0.28rem;
          color: #2563eb;
          text-transform: uppercase;
          letter-spacing: 0.13em;
          font-size: 0.68rem;
          line-height: 1.25;
        }

        .intel-entry small {
          display: block;
          color: #334155;
          font-size: 0.88rem;
          line-height: 1.56;
          overflow-wrap: anywhere;
        }

        .product-stage {
          position: relative;
          min-height: clamp(430px, 43vw, 680px);
          display: grid;
          place-items: center;
          perspective: 1200px;
          min-width: 0;
        }

        .stage-orbit {
          position: absolute;
          width: min(86%, 760px);
          aspect-ratio: 1.28;
          border-radius: 999px;
          background:
            radial-gradient(circle, rgba(37, 99, 235, 0.2), transparent 63%),
            radial-gradient(circle at 75% 30%, rgba(251, 191, 36, 0.13), transparent 34%);
          filter: blur(18px);
          opacity: 0.95;
          animation: prismaVerticalGlowPulse 7s ease-in-out infinite;
        }

        .dashboard-console {
          position: relative;
          isolation: isolate;
          width: min(108%, 940px);
          transform: rotateX(2deg) rotateY(-4deg);
          padding: clamp(0.8rem, 1.4vw, 1.1rem);
          border-radius: clamp(1.3rem, 2vw, 2.2rem);
          background:
            linear-gradient(145deg, rgba(15, 23, 42, 0.98), rgba(5, 14, 31, 0.98)),
            radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.18), transparent 45%);
          border: 1px solid rgba(148, 163, 184, 0.24);
          box-shadow:
            0 58px 140px rgba(15, 23, 42, 0.32),
            0 0 0 1px rgba(255, 255, 255, 0.04) inset,
            0 0 80px rgba(37, 99, 235, 0.2);
          animation: prismaVerticalFloat 7s ease-in-out infinite;
        }

        .dashboard-console::before {
          content: "";
          position: absolute;
          inset: -1px;
          border-radius: inherit;
          padding: 1px;
          background: linear-gradient(125deg, rgba(96,165,250,0.5), transparent 28%, rgba(251,191,36,0.22), transparent 72%);
          mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
          -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
          mask-composite: exclude;
          -webkit-mask-composite: xor;
          pointer-events: none;
        }

        .dashboard-console img {
          position: relative;
          z-index: 1;
          display: block;
          width: 100%;
          height: auto;
          border-radius: clamp(0.95rem, 1.4vw, 1.5rem);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.42);
        }

        .console-scan {
          position: absolute;
          z-index: 2;
          inset: 1rem;
          border-radius: 1.2rem;
          background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.2), transparent);
          transform: translateX(-120%);
          opacity: 0.45;
          animation: prismaVerticalScan 5.8s ease-in-out infinite;
          pointer-events: none;
        }

        .telemetry {
          position: absolute;
          z-index: 3;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          max-width: min(13rem, 42vw);
          padding: 0.62rem 0.78rem;
          border-radius: 999px;
          background: rgba(8, 16, 32, 0.82);
          border: 1px solid rgba(96, 165, 250, 0.24);
          color: #eaf4ff;
          box-shadow: 0 16px 38px rgba(15, 23, 42, 0.28);
          backdrop-filter: blur(14px);
          font-size: 0.78rem;
          white-space: nowrap;
          pointer-events: none;
          animation: prismaVerticalTelemetry 4.4s ease-in-out infinite;
        }

        .telemetry b {
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .telemetry-live { top: 8%; left: 5%; }
        .telemetry-alert { bottom: 12%; left: -3%; animation-delay: 0.7s; }
        .telemetry-audit { top: 17%; right: -2%; animation-delay: 1.2s; }
        .telemetry-decision { bottom: 9%; right: 6%; animation-delay: 1.7s; }

        .telemetry-dot {
          width: 0.58rem;
          height: 0.58rem;
          border-radius: 999px;
          background: #38bdf8;
          box-shadow: 0 0 18px rgba(56, 189, 248, 0.8);
          flex: 0 0 auto;
        }

        .telemetry-dot.warning {
          background: #60a5fa;
          box-shadow: 0 0 18px rgba(96, 165, 250, 0.8);
        }

        .telemetry-dot.gold {
          background: #fbbf24;
          box-shadow: 0 0 18px rgba(251, 191, 36, 0.7);
        }

        .telemetry-dot.ok {
          background: #22c55e;
          box-shadow: 0 0 18px rgba(34, 197, 94, 0.65);
        }

        .command-section {
          position: relative;
          padding: clamp(4.5rem, 7vw, 7rem) 1.5rem;
          background:
            radial-gradient(circle at 80% 10%, rgba(37,99,235,0.08), transparent 28rem),
            linear-gradient(180deg, #f7fbff 0%, #edf4fc 100%);
          color: #0f172a;
        }

        .command-header {
          max-width: 1280px;
          margin: 0 auto 2.8rem;
          display: grid;
          grid-template-columns: minmax(0, 0.85fr) minmax(280px, 0.75fr);
          gap: 2rem;
          align-items: end;
        }

        .command-header h2,
        .proof-heading h2 {
          margin: 0;
          color: #0b1224;
          font-size: clamp(2.4rem, 4.4vw, 5.15rem);
          line-height: 0.94;
          letter-spacing: -0.065em;
          font-weight: 950;
          text-wrap: balance;
        }

        .command-header p {
          margin: 0;
          color: #475569;
          font-size: 1.02rem;
          line-height: 1.8;
        }

        .command-spine {
          position: relative;
          max-width: 1280px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 0;
          padding: 2.35rem 1.45rem 1.55rem;
          border-radius: 2rem;
          background:
            linear-gradient(180deg, rgba(255,255,255,0.82), rgba(255,255,255,0.56));
          border: 1px solid rgba(37, 99, 235, 0.13);
          box-shadow: 0 36px 90px rgba(15, 23, 42, 0.09);
          overflow: hidden;
        }

        .spine-line {
          position: absolute;
          z-index: 0;
          left: 7%;
          right: 7%;
          top: 4.55rem;
          height: 3px;
          background: linear-gradient(90deg, rgba(37,99,235,0.22), rgba(37,99,235,0.88), rgba(251,191,36,0.62));
          box-shadow: 0 0 26px rgba(37, 99, 235, 0.24);
        }

        .spine-signal {
          position: absolute;
          z-index: 2;
          top: calc(4.55rem - 0.32rem);
          left: 7%;
          width: 0.72rem;
          height: 0.72rem;
          border-radius: 999px;
          background: #2563eb;
          box-shadow: 0 0 0 8px rgba(37, 99, 235, 0.13), 0 0 24px rgba(37, 99, 235, 0.75);
          animation: prismaVerticalSignal 7s ease-in-out infinite;
        }

        .command-node {
          position: relative;
          z-index: 1;
          min-height: 14rem;
          display: flex;
          flex-direction: column;
          gap: 1.1rem;
          padding: 0.9rem 0.85rem 1rem;
          border-radius: 1.05rem;
          background: rgba(255, 255, 255, 0.32);
          border: 1px solid rgba(37, 99, 235, 0.08);
          transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, background 180ms ease;
        }

        .command-node:hover {
          transform: translateY(-6px);
          border-color: rgba(37, 99, 235, 0.28);
          background: rgba(255,255,255,0.58);
          box-shadow: 0 24px 52px rgba(37, 99, 235, 0.16);
        }

        .command-node:not(:last-child)::after {
          content: "→";
          position: absolute;
          z-index: 3;
          top: 3.08rem;
          right: -0.55rem;
          color: rgba(37, 99, 235, 0.78);
          font-size: 1.15rem;
          font-weight: 950;
          text-shadow: 0 0 18px rgba(37, 99, 235, 0.35);
          pointer-events: none;
        }

        .command-node-final {
          background: linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,251,235,0.72));
          border-color: rgba(251, 191, 36, 0.55);
          box-shadow: 0 0 0 1px rgba(251, 191, 36, 0.12) inset;
        }

        .command-node-final::after {
          display: none;
        }

        .node-top {
          position: relative;
          z-index: 3;
          display: flex;
          align-items: center;
          justify-content: space-between;
          min-height: 3.35rem;
        }

        .node-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 2rem;
          height: 2rem;
          border-radius: 999px;
          color: #2563eb;
          background: rgba(219, 234, 254, 0.94);
          border: 1px solid rgba(37, 99, 235, 0.22);
          font-weight: 900;
          font-size: 0.78rem;
        }

        .node-icon {
          display: grid;
          place-items: center;
          width: 3.25rem;
          height: 3.25rem;
          border-radius: 1rem;
          color: #2563eb;
          background:
            radial-gradient(circle at 35% 25%, rgba(255,255,255,0.95), transparent 42%),
            linear-gradient(180deg, #dbeafe, #eff6ff);
          border: 1px solid rgba(37, 99, 235, 0.14);
          box-shadow: 0 12px 25px rgba(37, 99, 235, 0.1);
        }

        .command-node-final .node-icon {
          color: #b7791f;
          background: linear-gradient(180deg, rgba(254, 243, 199, 0.96), rgba(255, 251, 235, 0.76));
          border-color: rgba(251, 191, 36, 0.36);
        }

        .node-icon svg {
          width: 1.5rem;
          height: 1.5rem;
        }

        .node-role {
          margin: 0 0 0.38rem;
          color: #2563eb;
          font-size: 0.74rem;
          font-weight: 950;
          letter-spacing: 0.1em;
          text-transform: uppercase;
        }

        .command-node h3 {
          margin: 0 0 0.8rem;
          color: #0f172a;
          font-size: 1.05rem;
          letter-spacing: -0.02em;
        }

        .command-node p:last-child {
          margin: 0;
          color: #475569;
          font-size: 0.88rem;
          line-height: 1.62;
        }

        .proof-section {
          padding: clamp(4.5rem, 7vw, 7rem) 1.5rem;
          background:
            radial-gradient(circle at 78% 0%, rgba(37,99,235,0.13), transparent 28rem),
            linear-gradient(180deg, #edf4fc 0%, #e8f1fb 100%);
        }

        .proof-console {
          position: relative;
          overflow: hidden;
          max-width: 1280px;
          margin: 0 auto;
          padding: clamp(2.4rem, 4.4vw, 4.4rem);
          border-radius: 2rem;
          background:
            radial-gradient(circle at 86% 12%, rgba(37, 99, 235, 0.3), transparent 28rem),
            linear-gradient(135deg, #07111f 0%, #111c30 55%, #14284a 100%);
          border: 1px solid rgba(148, 163, 184, 0.18);
          box-shadow: 0 42px 105px rgba(15, 23, 42, 0.24);
          color: #f8fbff;
          animation: prismaVerticalProofGlow 7s ease-in-out infinite;
        }

        .proof-glow {
          position: absolute;
          inset: auto -10% -35% 30%;
          height: 55%;
          background: radial-gradient(circle, rgba(37, 99, 235, 0.24), transparent 70%);
          pointer-events: none;
        }

        .proof-heading {
          position: relative;
          z-index: 1;
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 1.5rem;
          align-items: start;
          margin-bottom: 2.6rem;
        }

        .proof-heading > div {
          max-width: 780px;
        }

        .proof-heading h2 {
          max-width: 780px;
          color: white;
          font-size: clamp(2.35rem, 3.8vw, 4.85rem);
        }

        .proof-heading span {
          justify-self: end;
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          padding: 0.7rem 0.95rem;
          background: rgba(37, 99, 235, 0.16);
          color: #bfdbfe;
          border: 1px solid rgba(96, 165, 250, 0.22);
          font-weight: 900;
          font-size: 0.84rem;
          white-space: nowrap;
        }

        .proof-log {
          position: relative;
          z-index: 1;
          display: grid;
          gap: 0.85rem;
        }

        .proof-log::before {
          content: "";
          position: absolute;
          left: 1.65rem;
          top: 1.3rem;
          bottom: 1.3rem;
          width: 1px;
          background: linear-gradient(180deg, rgba(96,165,250,0.8), rgba(251,191,36,0.34));
        }

        .proof-row {
          position: relative;
          min-width: 0;
          display: grid;
          grid-template-columns: 3.4rem 3rem minmax(0, 1fr);
          gap: 0.9rem;
          align-items: center;
          padding: 1rem 1rem;
          border-radius: 1.1rem;
          background: linear-gradient(90deg, rgba(255,255,255,0.07), rgba(255,255,255,0.035));
          border: 1px solid rgba(148, 163, 184, 0.16);
          transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
        }

        .proof-row:hover {
          transform: translateX(6px);
          border-color: rgba(96, 165, 250, 0.3);
          background: linear-gradient(90deg, rgba(37,99,235,0.16), rgba(255,255,255,0.04));
        }

        .proof-index {
          color: #60a5fa;
          font-weight: 900;
          font-size: 0.78rem;
        }

        .proof-icon {
          display: grid;
          place-items: center;
          width: 2.5rem;
          height: 2.5rem;
          border-radius: 0.9rem;
          color: #93c5fd;
          background: rgba(37, 99, 235, 0.15);
          border: 1px solid rgba(96, 165, 250, 0.2);
        }

        .proof-icon svg {
          width: 1.15rem;
          height: 1.15rem;
        }

        .proof-copy {
          min-width: 0;
        }

        .proof-copy b {
          display: block;
          margin-bottom: 0.22rem;
          color: #ffffff;
          font-size: 1rem;
        }

        .proof-copy small {
          display: block;
          color: rgba(226, 232, 240, 0.78);
          font-size: 0.92rem;
          line-height: 1.55;
          overflow-wrap: anywhere;
        }

        @keyframes prismaVerticalAmbient {
          from { transform: translate3d(-2%, -1%, 0) scale(1); }
          to { transform: translate3d(2%, 1%, 0) scale(1.04); }
        }

        @keyframes prismaVerticalGlowPulse {
          0%, 100% { opacity: 0.65; transform: scale(0.98); }
          50% { opacity: 1; transform: scale(1.04); }
        }

        @keyframes prismaVerticalFloat {
          0%, 100% { transform: translateY(0) rotateX(2deg) rotateY(-4deg); }
          50% { transform: translateY(-10px) rotateX(2deg) rotateY(-3deg); }
        }

        @keyframes prismaVerticalScan {
          0%, 30% { transform: translateX(-120%); opacity: 0; }
          45% { opacity: 0.5; }
          70%, 100% { transform: translateX(120%); opacity: 0; }
        }

        @keyframes prismaVerticalTelemetry {
          0%, 100% { transform: translateY(0); opacity: 0.88; }
          50% { transform: translateY(-4px); opacity: 1; }
        }

        @keyframes prismaVerticalSignal {
          0% { transform: translateX(0); }
          100% { transform: translateX(calc(100vw - 15rem)); }
        }

        @keyframes prismaVerticalProofGlow {
          0%, 100% { box-shadow: 0 42px 105px rgba(15, 23, 42, 0.24), 0 0 0 rgba(37, 99, 235, 0); }
          50% { box-shadow: 0 42px 105px rgba(15, 23, 42, 0.24), 0 0 55px rgba(37, 99, 235, 0.14); }
        }

        @media (max-width: 1180px) {
          .vertical-hero {
            grid-template-columns: 1fr;
          }

          .hero-copy h1 {
            max-width: 860px;
          }

          .intel-rail {
            max-width: 860px;
          }

          .intel-entry:nth-child(2),
          .intel-entry:nth-child(3) {
            margin-left: 0;
          }

          .intel-entry::before {
            display: none;
          }

          .product-stage {
            min-height: auto;
            justify-items: center;
          }

          .dashboard-console {
            width: min(100%, 820px);
          }

          .telemetry-live { top: 8%; left: 4%; }
          .telemetry-alert { bottom: 12%; left: 4%; }
          .telemetry-audit { top: 14%; right: 4%; }
          .telemetry-decision { bottom: 10%; right: 4%; }

          .command-spine {
            grid-template-columns: 1fr;
            gap: 0.75rem;
            padding-left: 1.2rem;
          }

          .spine-line {
            left: 3.35rem;
            right: auto;
            top: 2rem;
            bottom: 2rem;
            width: 2px;
            height: auto;
          }

          .spine-signal {
            top: 2rem;
            left: calc(3.35rem - 0.35rem);
            animation-name: prismaVerticalSignalY;
          }

          .command-node {
            min-height: auto;
            padding: 1rem 1rem 1rem 4.25rem;
          }

          .command-node:not(:last-child)::after {
            content: "↓";
            top: auto;
            right: auto;
            left: 1.43rem;
            bottom: -0.75rem;
          }

          .node-top {
            position: absolute;
            left: 0.85rem;
            top: 1rem;
            flex-direction: column;
            justify-content: flex-start;
            gap: 0.55rem;
          }

          @keyframes prismaVerticalSignalY {
            0% { transform: translateY(0); }
            100% { transform: translateY(calc(100% + 22rem)); }
          }
        }

        @media (max-width: 760px) {
          .vertical-product-page,
          .command-section,
          .proof-section {
            padding-left: 1rem;
            padding-right: 1rem;
          }

          .vertical-hero {
            gap: 2.2rem;
          }

          .hero-copy h1 {
            font-size: clamp(2.9rem, 12vw, 4.15rem);
            line-height: 0.93;
          }

          .hero-lead {
            font-size: 1rem;
          }

          .dashboard-console {
            width: 100%;
            transform: none;
            overflow: hidden;
            animation: prismaVerticalFloatSmall 7s ease-in-out infinite;
          }

          .telemetry {
            position: relative;
            inset: auto;
            max-width: 100%;
            white-space: normal;
            margin: 0.45rem 0.25rem 0 0;
            font-size: 0.74rem;
          }

          .dashboard-console {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
          }

          .dashboard-console img,
          .console-scan {
            flex-basis: 100%;
          }

          .command-header,
          .proof-heading {
            grid-template-columns: 1fr;
          }

          .command-header h2,
          .proof-heading h2 {
            font-size: clamp(2.25rem, 10vw, 3.65rem);
          }

          .proof-heading span {
            justify-self: start;
          }

          .proof-console {
            border-radius: 1.45rem;
            padding: 1.2rem;
          }

          .proof-row {
            grid-template-columns: 2.4rem minmax(0, 1fr);
          }

          .proof-index {
            display: none;
          }
        }

        @keyframes prismaVerticalFloatSmall {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-7px); }
        }


        /* Proof console alignment fix: make it read like an evidence log, not a centered poster */
        .proof-heading {
          display: grid !important;
          grid-template-columns: minmax(0, 1fr) auto !important;
          align-items: start !important;
          justify-content: stretch !important;
          gap: 1.5rem !important;
          margin-bottom: 2.25rem !important;
        }

        .proof-heading > div {
          max-width: 720px !important;
          justify-self: start !important;
        }

        .proof-heading .eyebrow {
          margin-bottom: 1rem !important;
        }

        .proof-heading h2 {
          max-width: 720px !important;
          margin: 0 !important;
          text-align: left !important;
          font-size: clamp(2.6rem, 4.2vw, 4.65rem) !important;
          line-height: 0.95 !important;
          letter-spacing: -0.06em !important;
        }

        .proof-heading span {
          justify-self: end !important;
          align-self: start !important;
          margin-top: 0.4rem !important;
        }

        .proof-log {
          max-width: 100% !important;
          margin-top: 0 !important;
        }

        .proof-row {
          padding: 1.05rem 1.15rem !important;
        }

        .proof-log::before {
          left: 1.85rem !important;
        }

        @media (max-width: 760px) {
          .proof-heading {
            grid-template-columns: 1fr !important;
          }

          .proof-heading h2 {
            font-size: clamp(2.25rem, 10vw, 3.5rem) !important;
          }

          .proof-heading span {
            justify-self: start !important;
            margin-top: 0 !important;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .vertical-ambient,
          .stage-orbit,
          .dashboard-console,
          .console-scan,
          .telemetry,
          .spine-signal,
          .proof-console {
            animation: none !important;
          }

          .command-node,
          .proof-row {
            transition: none !important;
          }
        }

        /* FINAL proof console override */
        .proof-section .proof-console .proof-heading {
          display: grid !important;
          grid-template-columns: minmax(0, 1fr) auto !important;
          align-items: start !important;
          gap: 1.5rem !important;
          margin-bottom: 2.4rem !important;
        }

        .proof-section .proof-console .proof-heading > div {
          max-width: 760px !important;
          justify-self: start !important;
          text-align: left !important;
        }

        .proof-section .proof-console .proof-heading .eyebrow {
          display: block !important;
          margin: 0 0 1rem !important;
          text-align: left !important;
        }

        .proof-section .proof-console .proof-heading h2 {
          max-width: 760px !important;
          margin: 0 !important;
          text-align: left !important;
          font-size: clamp(2.55rem, 4vw, 4.55rem) !important;
          line-height: 0.96 !important;
          letter-spacing: -0.058em !important;
        }

        .proof-section .proof-console .proof-heading span {
          justify-self: end !important;
          align-self: start !important;
          margin-top: 0.4rem !important;
        }

        .proof-section .proof-console .proof-log {
          margin-top: 0 !important;
        }

        @media (max-width: 760px) {
          .proof-section .proof-console .proof-heading {
            grid-template-columns: 1fr !important;
          }

          .proof-section .proof-console .proof-heading span {
            justify-self: start !important;
            margin-top: 0 !important;
          }
        }


        /* Final isolated proof console: no old proof-* layout interference */
        .proof-final-section {
          padding: clamp(4.5rem, 7vw, 7rem) 1.5rem;
          background:
            radial-gradient(circle at 78% 0%, rgba(37,99,235,0.13), transparent 28rem),
            linear-gradient(180deg, #edf4fc 0%, #e8f1fb 100%);
        }

        .proof-final-console {
          position: relative;
          overflow: hidden;
          max-width: 1280px;
          margin: 0 auto;
          padding: clamp(2.5rem, 4.5vw, 4.5rem);
          border-radius: 2rem;
          background:
            radial-gradient(circle at 86% 12%, rgba(37, 99, 235, 0.3), transparent 28rem),
            linear-gradient(135deg, #07111f 0%, #111c30 55%, #14284a 100%);
          border: 1px solid rgba(148, 163, 184, 0.18);
          box-shadow: 0 42px 105px rgba(15, 23, 42, 0.24);
          color: #f8fbff;
          animation: prismaVerticalProofGlow 7s ease-in-out infinite;
        }

        .proof-final-glow {
          position: absolute;
          inset: auto -10% -35% 30%;
          height: 55%;
          background: radial-gradient(circle, rgba(37, 99, 235, 0.24), transparent 70%);
          pointer-events: none;
        }

        .proof-final-heading {
          position: relative;
          z-index: 1;
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 1.5rem;
          align-items: start;
          margin-bottom: 2.55rem;
        }

        .proof-final-heading > div {
          max-width: 760px;
          text-align: left;
        }

        .proof-final-heading .eyebrow {
          display: block;
          margin: 0 0 1rem;
          text-align: left;
        }

        .proof-final-heading h2 {
          max-width: 760px;
          margin: 0;
          color: #ffffff;
          text-align: left;
          font-size: clamp(2.6rem, 4.05vw, 4.7rem);
          line-height: 0.96;
          letter-spacing: -0.06em;
          font-weight: 950;
          text-wrap: balance;
        }

        .proof-final-badge {
          justify-self: end;
          align-self: start;
          display: inline-flex;
          align-items: center;
          border-radius: 999px;
          padding: 0.72rem 1rem;
          background: rgba(37, 99, 235, 0.16);
          color: #bfdbfe;
          border: 1px solid rgba(96, 165, 250, 0.22);
          font-weight: 900;
          font-size: 0.84rem;
          white-space: nowrap;
        }

        .proof-final-log {
          position: relative;
          z-index: 1;
          display: grid;
          gap: 0.85rem;
        }

        .proof-final-log::before {
          content: "";
          position: absolute;
          left: 1.65rem;
          top: 1.3rem;
          bottom: 1.3rem;
          width: 1px;
          background: linear-gradient(180deg, rgba(96,165,250,0.8), rgba(251,191,36,0.34));
        }

        .proof-final-row {
          position: relative;
          min-width: 0;
          display: grid;
          grid-template-columns: 3.4rem 3rem minmax(0, 1fr);
          gap: 0.9rem;
          align-items: center;
          padding: 1.05rem 1.15rem;
          border-radius: 1.1rem;
          background: linear-gradient(90deg, rgba(255,255,255,0.07), rgba(255,255,255,0.035));
          border: 1px solid rgba(148, 163, 184, 0.16);
          transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
        }

        .proof-final-row:hover {
          transform: translateX(6px);
          border-color: rgba(96, 165, 250, 0.3);
          background: linear-gradient(90deg, rgba(37,99,235,0.16), rgba(255,255,255,0.04));
        }

        .proof-final-index {
          color: #60a5fa;
          font-weight: 900;
          font-size: 0.78rem;
        }

        .proof-final-icon {
          display: grid;
          place-items: center;
          width: 2.5rem;
          height: 2.5rem;
          border-radius: 0.9rem;
          color: #93c5fd;
          background: rgba(37, 99, 235, 0.15);
          border: 1px solid rgba(96, 165, 250, 0.2);
        }

        .proof-final-icon svg {
          width: 1.15rem;
          height: 1.15rem;
        }

        .proof-final-copy {
          min-width: 0;
        }

        .proof-final-copy b {
          display: block;
          margin-bottom: 0.22rem;
          color: #ffffff;
          font-size: 1rem;
        }

        .proof-final-copy small {
          display: block;
          color: rgba(226, 232, 240, 0.78);
          font-size: 0.92rem;
          line-height: 1.55;
          overflow-wrap: anywhere;
        }

        @media (max-width: 760px) {
          .proof-final-console {
            border-radius: 1.45rem;
            padding: 1.2rem;
          }

          .proof-final-heading {
            grid-template-columns: 1fr;
          }

          .proof-final-heading h2 {
            font-size: clamp(2.25rem, 10vw, 3.5rem);
          }

          .proof-final-badge {
            justify-self: start;
          }

          .proof-final-row {
            grid-template-columns: 2.4rem minmax(0, 1fr);
          }

          .proof-final-index {
            display: none;
          }
        }


        /* Per-vertical personality pass */
        .vertical-commerce .dashboard-console,
        .command-commerce .command-node-final,
        .proof-commerce .proof-final-console {
          --vertical-accent: #2563eb;
        }

        .vertical-industrial .dashboard-console {
          box-shadow:
            0 58px 140px rgba(15, 23, 42, 0.38),
            0 0 0 1px rgba(251, 191, 36, 0.1) inset,
            0 0 95px rgba(251, 191, 36, 0.18);
        }

        .vertical-industrial .telemetry-dot.gold,
        .command-industrial .command-node-final .node-icon {
          color: #b7791f;
        }

        .command-industrial .spine-line {
          background: linear-gradient(90deg, rgba(37,99,235,0.2), rgba(251,191,36,0.72), rgba(37,99,235,0.54));
        }

        .proof-industrial .proof-final-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(251, 191, 36, 0.18), transparent 28rem),
            linear-gradient(135deg, #080f19 0%, #141a25 52%, #1f2937 100%);
        }

        .vertical-field .dashboard-console {
          box-shadow:
            0 58px 140px rgba(15, 23, 42, 0.28),
            0 0 0 1px rgba(34, 197, 94, 0.08) inset,
            0 0 95px rgba(14, 165, 233, 0.18);
        }

        .command-field .spine-line {
          background: linear-gradient(90deg, rgba(37,99,235,0.2), rgba(14,165,233,0.76), rgba(34,197,94,0.54));
        }

        .proof-field .proof-final-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(14, 165, 233, 0.24), transparent 28rem),
            linear-gradient(135deg, #07111f 0%, #102235 55%, #123047 100%);
        }

        .vertical-commerce .product-stage {
          min-height: clamp(390px, 40vw, 620px);
        }

        .vertical-field .intel-entry,
        .vertical-commerce .intel-entry {
          border-radius: 1.35rem;
        }

        .command-commerce .command-node-final {
          border-color: rgba(37, 99, 235, 0.38);
          background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(239,246,255,0.78));
        }

        .command-field .command-node-final {
          border-color: rgba(14, 165, 233, 0.36);
          background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(236,254,255,0.72));
        }

        .command-industrial .command-node-final {
          border-color: rgba(251, 191, 36, 0.58);
        }


        /* Strong per-vertical visual personality layer */
        .vertical-commerce {
          background:
            radial-gradient(circle at 74% 20%, rgba(37,99,235,0.22), transparent 34rem),
            radial-gradient(circle at 18% 78%, rgba(147,197,253,0.20), transparent 28rem),
            linear-gradient(180deg, #fbfdff 0%, #edf6ff 100%);
        }

        .vertical-commerce .dashboard-console {
          box-shadow:
            0 56px 135px rgba(37, 99, 235, 0.20),
            0 0 0 1px rgba(37,99,235,0.08) inset,
            0 0 90px rgba(59, 130, 246, 0.22);
        }

        .command-commerce .command-spine {
          background:
            linear-gradient(180deg, rgba(255,255,255,0.88), rgba(239,246,255,0.64)),
            radial-gradient(circle at 15% 20%, rgba(37,99,235,0.10), transparent 22rem);
        }

        .command-commerce .spine-line {
          background: linear-gradient(90deg, rgba(37,99,235,0.18), rgba(37,99,235,0.95), rgba(14,165,233,0.58));
        }

        .command-commerce .command-node-final {
          border-color: rgba(37, 99, 235, 0.42);
          background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(239,246,255,0.78));
        }

        .proof-commerce .proof-final-console,
        .proof-commerce .proof-console {
          background:
            radial-gradient(circle at 84% 12%, rgba(37,99,235,0.34), transparent 28rem),
            linear-gradient(135deg, #08111f 0%, #10264a 55%, #143b75 100%);
        }

        .vertical-industrial {
          background:
            radial-gradient(circle at 76% 18%, rgba(251,191,36,0.18), transparent 34rem),
            radial-gradient(circle at 16% 72%, rgba(37,99,235,0.14), transparent 30rem),
            linear-gradient(180deg, #f9fbff 0%, #eef3f8 100%);
        }

        .vertical-industrial .dashboard-console {
          background:
            linear-gradient(145deg, rgba(10, 14, 20, 0.98), rgba(18, 24, 33, 0.98)),
            radial-gradient(circle at 62% 0%, rgba(251,191,36,0.20), transparent 45%);
          box-shadow:
            0 62px 150px rgba(15, 23, 42, 0.40),
            0 0 0 1px rgba(251,191,36,0.12) inset,
            0 0 95px rgba(251,191,36,0.20);
        }

        .vertical-industrial .telemetry {
          border-color: rgba(251,191,36,0.28);
        }

        .command-industrial .command-spine {
          background:
            linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,251,235,0.48)),
            radial-gradient(circle at 90% 20%, rgba(251,191,36,0.15), transparent 20rem);
        }

        .command-industrial .spine-line {
          background: linear-gradient(90deg, rgba(37,99,235,0.22), rgba(251,191,36,0.82), rgba(37,99,235,0.56));
        }

        .command-industrial .command-node-final,
        .command-industrial .command-node-final .node-icon {
          border-color: rgba(251,191,36,0.62);
        }

        .proof-industrial .proof-final-console,
        .proof-industrial .proof-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(251,191,36,0.22), transparent 28rem),
            linear-gradient(135deg, #080f19 0%, #171b22 52%, #2a2114 100%);
        }

        .vertical-field {
          background:
            radial-gradient(circle at 76% 20%, rgba(14,165,233,0.20), transparent 34rem),
            radial-gradient(circle at 14% 76%, rgba(34,197,94,0.12), transparent 28rem),
            linear-gradient(180deg, #fbfdff 0%, #ecfeff 100%);
        }

        .vertical-field .dashboard-console {
          box-shadow:
            0 58px 140px rgba(15, 23, 42, 0.27),
            0 0 0 1px rgba(14,165,233,0.10) inset,
            0 0 92px rgba(14,165,233,0.22);
        }

        .command-field .command-spine {
          background:
            linear-gradient(180deg, rgba(255,255,255,0.86), rgba(236,254,255,0.56)),
            radial-gradient(circle at 70% 20%, rgba(14,165,233,0.13), transparent 22rem);
        }

        .command-field .spine-line {
          background: linear-gradient(90deg, rgba(37,99,235,0.18), rgba(14,165,233,0.85), rgba(34,197,94,0.58));
        }

        .command-field .command-node-final {
          border-color: rgba(14,165,233,0.44);
          background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(236,254,255,0.74));
        }

        .proof-field .proof-final-console,
        .proof-field .proof-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(14,165,233,0.25), transparent 28rem),
            linear-gradient(135deg, #07111f 0%, #102235 55%, #123047 100%);
        }

        .vertical-control {
          background:
            radial-gradient(circle at 78% 18%, rgba(37,99,235,0.18), transparent 34rem),
            radial-gradient(circle at 16% 78%, rgba(125,211,252,0.14), transparent 30rem),
            linear-gradient(180deg, #f9fcff 0%, #edf5ff 100%);
        }

        .vertical-control .dashboard-console {
          box-shadow:
            0 62px 150px rgba(15, 23, 42, 0.34),
            0 0 0 1px rgba(255,255,255,0.04) inset,
            0 0 94px rgba(37,99,235,0.22);
        }

        .command-control .command-node-final {
          border-color: rgba(251,191,36,0.55);
        }

        .proof-control .proof-final-console,
        .proof-control .proof-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(37,99,235,0.30), transparent 28rem),
            linear-gradient(135deg, #07111f 0%, #111c30 55%, #14284a 100%);
        }

        /* Layout flavor: make each vertical feel less cloned */
        .vertical-industrial .hero-copy h1 {
          letter-spacing: -0.055em;
        }

        .vertical-commerce .hero-copy h1,
        .vertical-field .hero-copy h1 {
          max-width: 700px;
        }

        .vertical-industrial .intel-entry {
          background: rgba(255, 255, 255, 0.62);
          border-color: rgba(251,191,36,0.18);
        }

        .vertical-field .intel-entry {
          border-radius: 1.45rem;
          border-color: rgba(14,165,233,0.18);
        }

        .vertical-commerce .intel-entry {
          border-radius: 1.25rem;
        }

        .command-industrial .node-role,
        .vertical-industrial .intel-entry b {
          color: #b7791f;
        }

        .command-field .node-role,
        .vertical-field .intel-entry b {
          color: #0284c7;
        }

        .command-commerce .node-role,
        .vertical-commerce .intel-entry b {
          color: #2563eb;
        }

        .command-control .node-role,
        .vertical-control .intel-entry b {
          color: #2563eb;
        }

        .proof-industrial .proof-final-badge,
        .proof-industrial .proof-heading span {
          color: #fde68a;
          border-color: rgba(251,191,36,0.28);
          background: rgba(251,191,36,0.10);
        }

        .proof-field .proof-final-badge,
        .proof-field .proof-heading span {
          color: #bae6fd;
          border-color: rgba(14,165,233,0.30);
          background: rgba(14,165,233,0.12);
        }

        .proof-commerce .proof-final-badge,
        .proof-commerce .proof-heading span {
          color: #bfdbfe;
          border-color: rgba(37,99,235,0.28);
          background: rgba(37,99,235,0.14);
        }


        /* INDUSTRIAL visual pass: técnico, robusto, activos, lecturas y evidencia */
        .vertical-industrial {
          background:
            linear-gradient(115deg, rgba(15,23,42,0.045) 0 1px, transparent 1px 90px),
            linear-gradient(25deg, rgba(251,191,36,0.055) 0 1px, transparent 1px 120px),
            radial-gradient(circle at 78% 18%, rgba(251, 191, 36, 0.18), transparent 34rem),
            radial-gradient(circle at 16% 74%, rgba(37, 99, 235, 0.14), transparent 30rem),
            linear-gradient(180deg, #f9fbff 0%, #edf2f7 100%);
        }

        .vertical-industrial .vertical-hero {
          grid-template-columns: minmax(390px, 0.66fr) minmax(600px, 1.34fr);
        }

        .vertical-industrial .eyebrow {
          color: #b7791f;
        }

        .vertical-industrial .hero-copy h1 {
          max-width: 670px;
          color: #0a1220;
          letter-spacing: -0.06em;
        }

        .vertical-industrial .hero-lead {
          color: #334155;
          max-width: 680px;
        }

        .vertical-industrial .intel-entry {
          border-color: rgba(251, 191, 36, 0.22);
          background:
            linear-gradient(180deg, rgba(255,255,255,0.76), rgba(255,251,235,0.56));
          box-shadow:
            0 16px 38px rgba(15,23,42,0.08),
            inset 4px 0 0 rgba(251,191,36,0.35);
        }

        .vertical-industrial .intel-entry b {
          color: #b7791f;
        }

        .vertical-industrial .intel-icon {
          color: #b7791f;
          background:
            radial-gradient(circle at 35% 22%, rgba(255,255,255,0.96), transparent 42%),
            linear-gradient(180deg, rgba(254,243,199,0.98), rgba(255,251,235,0.78));
          border-color: rgba(251,191,36,0.3);
        }

        .vertical-industrial .product-stage {
          min-height: clamp(460px, 45vw, 720px);
        }

        .vertical-industrial .stage-orbit {
          background:
            radial-gradient(circle, rgba(251,191,36,0.20), transparent 62%),
            radial-gradient(circle at 62% 35%, rgba(37,99,235,0.16), transparent 42%);
        }

        .vertical-industrial .dashboard-console {
          width: min(110%, 980px);
          background:
            linear-gradient(145deg, rgba(8, 12, 18, 0.98), rgba(18, 24, 33, 0.98)),
            radial-gradient(circle at 62% 0%, rgba(251,191,36,0.22), transparent 45%);
          border-color: rgba(251,191,36,0.28);
          box-shadow:
            0 66px 155px rgba(15, 23, 42, 0.44),
            0 0 0 1px rgba(251,191,36,0.13) inset,
            0 0 110px rgba(251,191,36,0.20);
        }

        .vertical-industrial .dashboard-console::before {
          background: linear-gradient(125deg, rgba(251,191,36,0.55), transparent 28%, rgba(96,165,250,0.24), transparent 72%);
        }

        .vertical-industrial .telemetry {
          background: rgba(10, 14, 20, 0.84);
          border-color: rgba(251,191,36,0.30);
          box-shadow:
            0 16px 38px rgba(15, 23, 42, 0.34),
            0 0 24px rgba(251,191,36,0.10);
        }

        .vertical-industrial .telemetry-dot {
          background: #fbbf24;
          box-shadow: 0 0 18px rgba(251,191,36,0.74);
        }

        .command-industrial {
          background:
            linear-gradient(115deg, rgba(255,255,255,0.04) 0 1px, transparent 1px 84px),
            radial-gradient(circle at 76% 0%, rgba(251,191,36,0.14), transparent 30rem),
            linear-gradient(180deg, #101827 0%, #111827 100%);
          color: #f8fafc;
        }

        .command-industrial .eyebrow {
          color: #fbbf24;
        }

        .command-industrial .command-header h2 {
          color: #ffffff;
        }

        .command-industrial .command-header p {
          color: rgba(226,232,240,0.76);
        }

        .command-industrial .command-spine {
          background:
            linear-gradient(180deg, rgba(15,23,42,0.88), rgba(17,24,39,0.76)),
            radial-gradient(circle at 88% 20%, rgba(251,191,36,0.16), transparent 22rem);
          border-color: rgba(251,191,36,0.25);
          box-shadow:
            0 36px 90px rgba(0,0,0,0.22),
            inset 0 0 0 1px rgba(255,255,255,0.035);
        }

        .command-industrial .spine-line {
          background: linear-gradient(90deg, rgba(96,165,250,0.22), rgba(251,191,36,0.88), rgba(96,165,250,0.58));
          box-shadow: 0 0 30px rgba(251,191,36,0.24);
        }

        .command-industrial .spine-signal {
          background: #fbbf24;
          box-shadow:
            0 0 0 8px rgba(251,191,36,0.13),
            0 0 26px rgba(251,191,36,0.78);
        }

        .command-industrial .command-node {
          background: rgba(15, 23, 42, 0.44);
          border-color: rgba(148,163,184,0.16);
        }

        .command-industrial .command-node:hover {
          background: rgba(15, 23, 42, 0.68);
          border-color: rgba(251,191,36,0.34);
          box-shadow: 0 24px 58px rgba(0,0,0,0.26);
        }

        .command-industrial .command-node h3 {
          color: #ffffff;
        }

        .command-industrial .command-node p:last-child {
          color: rgba(226,232,240,0.74);
        }

        .command-industrial .node-role {
          color: #fbbf24;
        }

        .command-industrial .node-number {
          color: #fbbf24;
          background: rgba(251,191,36,0.12);
          border-color: rgba(251,191,36,0.30);
        }

        .command-industrial .node-icon {
          color: #fbbf24;
          background:
            radial-gradient(circle at 35% 25%, rgba(255,255,255,0.12), transparent 42%),
            linear-gradient(180deg, rgba(251,191,36,0.16), rgba(15,23,42,0.76));
          border-color: rgba(251,191,36,0.28);
          box-shadow: 0 12px 28px rgba(251,191,36,0.08);
        }

        .command-industrial .command-node-final {
          background:
            linear-gradient(180deg, rgba(251,191,36,0.16), rgba(15,23,42,0.72));
          border-color: rgba(251,191,36,0.58);
          box-shadow:
            0 0 0 1px rgba(251,191,36,0.12) inset,
            0 20px 60px rgba(251,191,36,0.08);
        }

        .proof-industrial {
          background:
            radial-gradient(circle at 78% 0%, rgba(251,191,36,0.12), transparent 28rem),
            linear-gradient(180deg, #111827 0%, #e8f1fb 100%);
        }

        .proof-industrial .proof-final-console,
        .proof-industrial .proof-console {
          background:
            radial-gradient(circle at 86% 12%, rgba(251,191,36,0.22), transparent 28rem),
            radial-gradient(circle at 18% 80%, rgba(37,99,235,0.12), transparent 24rem),
            linear-gradient(135deg, #080f19 0%, #171b22 52%, #2a2114 100%);
          border-color: rgba(251,191,36,0.22);
        }

        .proof-industrial .proof-final-badge,
        .proof-industrial .proof-heading span {
          color: #fde68a;
          border-color: rgba(251,191,36,0.30);
          background: rgba(251,191,36,0.11);
        }

        .proof-industrial .proof-final-icon,
        .proof-industrial .proof-icon {
          color: #fde68a;
          background: rgba(251,191,36,0.11);
          border-color: rgba(251,191,36,0.22);
        }

        .proof-industrial .proof-final-index,
        .proof-industrial .proof-index {
          color: #fbbf24;
        }

        @media (max-width: 1180px) {
          .vertical-industrial .vertical-hero {
            grid-template-columns: 1fr;
          }

          .vertical-industrial .dashboard-console {
            width: min(100%, 860px);
          }
        }


        /* INDUSTRIAL structural pass: not just color, actual industrial product composition */
        .vertical-industrial .product-stage {
          align-items: center;
          grid-template-rows: auto auto;
          gap: 1rem;
        }

        .vertical-industrial .dashboard-console {
          transform: rotateX(1deg) rotateY(-3deg) scale(1.04);
        }

        .industrial-telemetry-board {
          position: relative;
          z-index: 2;
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.8rem;
          width: min(92%, 780px);
          margin: -1.4rem auto 0;
          padding: 0.8rem;
          border-radius: 1.35rem;
          background:
            linear-gradient(180deg, rgba(8,12,18,0.88), rgba(17,24,39,0.78)),
            radial-gradient(circle at 82% 0%, rgba(251,191,36,0.18), transparent 18rem);
          border: 1px solid rgba(251,191,36,0.26);
          box-shadow:
            0 24px 70px rgba(15,23,42,0.22),
            inset 0 0 0 1px rgba(255,255,255,0.04);
          backdrop-filter: blur(16px);
        }

        .industrial-meter {
          position: relative;
          overflow: hidden;
          min-height: 5.5rem;
          padding: 0.9rem 1rem;
          border-radius: 1rem;
          background:
            linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.025));
          border: 1px solid rgba(148,163,184,0.16);
        }

        .industrial-meter::before {
          content: "";
          position: absolute;
          left: 0;
          right: 0;
          bottom: 0;
          height: 3px;
          background: linear-gradient(90deg, rgba(96,165,250,0.2), rgba(96,165,250,0.85));
        }

        .industrial-meter-hot::before {
          background: linear-gradient(90deg, rgba(239,68,68,0.25), rgba(251,191,36,0.9));
        }

        .industrial-meter-gold::before {
          background: linear-gradient(90deg, rgba(251,191,36,0.25), rgba(251,191,36,0.95));
        }

        .industrial-meter span {
          display: block;
          color: #fbbf24;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          font-weight: 950;
          font-size: 0.66rem;
        }

        .industrial-meter strong {
          display: block;
          margin-top: 0.25rem;
          color: #ffffff;
          font-size: 2rem;
          line-height: 1;
          letter-spacing: -0.05em;
        }

        .industrial-meter small {
          display: block;
          margin-top: 0.2rem;
          color: rgba(226,232,240,0.72);
          font-size: 0.78rem;
        }

        .command-industrial .command-header {
          align-items: start;
        }

        .command-industrial .command-header h2 {
          max-width: 760px;
        }

        .industrial-board-labels {
          max-width: 1280px;
          margin: -1rem auto 1.25rem;
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.8rem;
        }

        .industrial-board-labels div {
          position: relative;
          overflow: hidden;
          padding: 1rem 1.15rem;
          border-radius: 1rem;
          background:
            linear-gradient(180deg, rgba(15,23,42,0.82), rgba(17,24,39,0.64));
          border: 1px solid rgba(251,191,36,0.22);
          box-shadow: inset 0 0 0 1px rgba(255,255,255,0.035);
        }

        .industrial-board-labels div::after {
          content: "";
          position: absolute;
          right: -2rem;
          top: -2rem;
          width: 6rem;
          height: 6rem;
          border-radius: 999px;
          background: rgba(251,191,36,0.08);
        }

        .industrial-board-labels span {
          display: block;
          color: #fbbf24;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          font-size: 0.68rem;
          font-weight: 950;
        }

        .industrial-board-labels strong {
          display: block;
          margin-top: 0.35rem;
          color: #f8fafc;
          font-size: 1rem;
          line-height: 1.35;
        }

        .command-industrial .command-spine {
          border-radius: 1.2rem;
          padding-top: 3rem;
        }

        .command-industrial .command-spine::before {
          content: "ASSET CONTROL BOARD";
          position: absolute;
          left: 1.45rem;
          top: 1rem;
          color: rgba(251,191,36,0.72);
          font-size: 0.68rem;
          letter-spacing: 0.18em;
          font-weight: 950;
        }

        .command-industrial .command-node {
          border-radius: 0.75rem;
          min-height: 13rem;
        }

        .command-industrial .command-node::before {
          content: "";
          position: absolute;
          inset: 0.65rem auto auto 0.65rem;
          width: 0.42rem;
          height: 0.42rem;
          border-radius: 999px;
          background: #fbbf24;
          box-shadow: 0 0 14px rgba(251,191,36,0.75);
        }

        .command-industrial .node-top {
          padding-top: 0.4rem;
        }

        .proof-industrial .proof-final-console,
        .proof-industrial .proof-console {
          border-radius: 1.1rem;
        }

        .proof-industrial .proof-final-console::before,
        .proof-industrial .proof-console::before {
          content: "TECHNICAL EVIDENCE LOG";
          position: absolute;
          right: 2rem;
          bottom: 1.35rem;
          color: rgba(251,191,36,0.18);
          font-size: clamp(1.8rem, 4vw, 4.8rem);
          letter-spacing: 0.08em;
          font-weight: 950;
          pointer-events: none;
        }

        .proof-industrial .proof-final-row,
        .proof-industrial .proof-row {
          border-radius: 0.7rem;
          background:
            linear-gradient(90deg, rgba(251,191,36,0.075), rgba(255,255,255,0.025));
        }

        @media (max-width: 1180px) {
          .industrial-telemetry-board,
          .industrial-board-labels {
            grid-template-columns: 1fr;
          }

          .vertical-industrial .dashboard-console {
            transform: none;
          }

          .industrial-telemetry-board {
            margin-top: 0.5rem;
          }
        }


        /* Industrial V2 final composition tuning */
        .industrial-v2-hero {
          grid-template-columns: minmax(460px, 0.78fr) minmax(600px, 1.22fr) !important;
          gap: clamp(3rem, 5vw, 5.75rem) !important;
        }

        .industrial-v2-copy h1 {
          max-width: 760px !important;
          font-size: clamp(3.15rem, 4.65vw, 5.85rem) !important;
          line-height: 0.94 !important;
          letter-spacing: -0.058em !important;
          text-wrap: balance;
        }

        .industrial-v2-copy > p:not(.industrial-v2-eyebrow) {
          max-width: 680px !important;
          font-size: clamp(1.08rem, 1.25vw, 1.28rem) !important;
        }

        .industrial-v2-specs {
          max-width: 680px !important;
        }

        .industrial-v2-stage {
          transform: translateX(0.5rem);
        }

        .industrial-v2-frame {
          width: min(104%, 960px) !important;
        }

        .industrial-v2-board-head {
          grid-template-columns: minmax(0, 1fr) !important;
          gap: 1rem !important;
          margin-bottom: 2.4rem !important;
        }

        .industrial-v2-board-head h2 {
          max-width: 820px !important;
          font-size: clamp(2.9rem, 4.35vw, 5.25rem) !important;
          line-height: 0.94 !important;
        }

        .industrial-v2-board-head > p {
          max-width: 760px !important;
          margin: 0 !important;
          font-size: 1.05rem !important;
        }

        .industrial-v2-process {
          grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
          gap: 1rem !important;
          padding: 1.25rem !important;
        }

        .industrial-v2-process-item {
          min-height: 16.5rem !important;
          padding: 1.15rem !important;
        }

        .industrial-v2-process-item h3 {
          font-size: 1.12rem !important;
        }

        .industrial-v2-process-item p {
          font-size: 0.94rem !important;
          line-height: 1.68 !important;
        }

        .industrial-v2-process-item:last-child {
          transform: translateY(-0.25rem);
          box-shadow:
            0 0 0 1px rgba(251,191,36,0.18) inset,
            0 22px 60px rgba(251,191,36,0.08);
        }

        .industrial-v2-proof-head {
          grid-template-columns: minmax(0, 1fr) auto !important;
          align-items: start !important;
        }

        .industrial-v2-proof-head h2 {
          max-width: 760px !important;
          text-align: left !important;
          font-size: clamp(2.65rem, 4vw, 4.7rem) !important;
          line-height: 0.96 !important;
        }

        .industrial-v2-log article {
          padding: 1.1rem 1.2rem !important;
        }

        @media (max-width: 1180px) {
          .industrial-v2-hero {
            grid-template-columns: 1fr !important;
          }

          .industrial-v2-stage {
            transform: none !important;
          }

          .industrial-v2-copy h1 {
            max-width: 900px !important;
          }

          .industrial-v2-process {
            grid-template-columns: 1fr !important;
          }

          .industrial-v2-process-item {
            min-height: auto !important;
          }
        }

        @media (max-width: 760px) {
          .industrial-v2-copy h1 {
            font-size: clamp(2.75rem, 11vw, 4rem) !important;
          }

          .industrial-v2-board-head h2,
          .industrial-v2-proof-head h2 {
            font-size: clamp(2.35rem, 10vw, 3.5rem) !important;
          }

          .industrial-v2-proof-head {
            grid-template-columns: 1fr !important;
          }
        }

      `}</style>
    </>
  );
}
