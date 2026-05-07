import { PrismaPcInteractiveCommand } from "@components/landing/prisma-pc-interactive-command";

const painCards = [
  {
    title: "Inventario que cambia y nadie sabe por qué",
    copy: "Productos que según sí había, ajustes que nadie recuerda y conteos que llegan cuando el anaquel ya está llorando."
  },
  {
    title: "Pedidos hechos por costumbre",
    copy: "Comprar porque siempre se compra igual amarra dinero, provoca quiebres y deja mercancía dormida ocupando espacio."
  },
  {
    title: "Sucursales trabajando como islas",
    copy: "Cada tienda reporta a su modo y alguien termina juntando datos a mano, como si crecer significara sufrir más bonito."
  },
  {
    title: "Dueño sin visibilidad",
    copy: "Tu dinero se mueve aunque tú no estés ahí. PRISMA te ayuda a verlo antes de que el desorden decida por ti."
  }
];

const ecosystem = [
  {
    eyebrow: "Tablet vende",
    title: "La operación no se detiene",
    copy: "Caja, tickets, venta local, stock operativo y continuidad para que el mostrador siga respirando aunque la red se ponga payasa.",
    points: ["venta rápida", "ticket y caja", "stock local", "operación en mostrador"]
  },
  {
    eyebrow: "PC gobierna",
    title: "El control vive en backoffice",
    copy: "Catálogo, inventario, compras, recepción, reabasto, auditoría y KPIs para operar con evidencia, no con corazonadas con zapatos.",
    points: ["inventario", "compras", "reabasto", "auditoría"]
  },
  {
    eyebrow: "App móvil supervisa",
    title: "Tu negocio en la bolsa",
    copy: "Ventas, caja, alertas, inventario bajo y sucursales desde el celular, sin abrir toda la nave nodriza cada vez.",
    points: ["ventas", "alertas", "caja", "sucursales"]
  }
];

const questions = [
  "¿Qué se vendió hoy?",
  "¿Dónde se está acabando producto?",
  "¿Qué tienda necesita atención?",
  "¿Qué producto está durmiendo dinero?",
  "¿Qué pedido conviene preparar?",
  "¿Dónde se está perdiendo operación?"
];

const comparisonRows = [
  ["Creo que sí hay producto", "Existencias por SKU, tienda y ubicación"],
  ["Pídele más por si acaso", "Pedido sugerido por rotación, cobertura y quiebre"],
  ["Mándame foto del corte", "Ventas, caja y alertas desde app móvil"],
  ["Cada tienda ve cómo le hace", "Vista multi-sucursal en paralelo"],
  ["No sé quién ajustó eso", "Auditoría de movimientos sensibles"]
];

export function PrismaBusinessOverview() {
  return (
    <div className="prisma-home" data-prisma-page="business-overview">
      <section className="prisma-home-hero prisma-home-hero-media" aria-labelledby="prisma-home-title">
        <div className="prisma-home-hero-copy">
          <img className="prisma-home-inline-logo" src="/brand/prisma-logo-official.png" alt="PRISMA" />
          <div className="prisma-home-kicker">Sistema inteligente de gestión operativa</div>
          <h1 id="prisma-home-title">Controla tus tiendas sin perseguir libretas, audios y capturas.</h1>
          <p>
            PRISMA conecta venta, inventario, compras y supervisión en un solo sistema. Vende desde Tablet,
            gobierna desde PC y supervisa desde la app móvil.
          </p>
          <div className="prisma-home-actions" aria-label="Acciones principales">
            <a href="#control-en-vivo" className="prisma-home-primary">Probar control en vivo</a>
            <a href="#ecosistema" className="prisma-home-secondary">Explorar capacidades</a>
          </div>
          <div className="prisma-home-proof" aria-label="Capacidades destacadas">
            <span>Multi-sucursal</span>
            <span>Reabasto inteligente</span>
            <span>Auditoría operativa</span>
          </div>
        </div>

        <figure className="prisma-home-media-card prisma-home-main-poster">
          <img src="/landing/prisma-home-hero-commercial.png" alt="PRISMA conectado en Tablet, PC y app móvil" />
        </figure>
      </section>

      <section className="prisma-home-section prisma-home-pain" aria-labelledby="prisma-pain-title">
        <div className="prisma-section-heading">
          <span className="prisma-home-kicker">El desmadre que PRISMA ordena</span>
          <h2 id="prisma-pain-title">Vender no es el problema. El riesgo es operar a ciegas.</h2>
          <p>Una tienda se aguanta con presencia. Varias tiendas necesitan control real, porque el caos también abre sucursales.</p>
        </div>
        <div className="prisma-pain-grid">
          {painCards.map((item) => (
            <article className="prisma-pain-card" key={item.title}>
              <div className="prisma-card-dot" />
              <h3>{item.title}</h3>
              <p>{item.copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="prisma-home-section prisma-home-ecosystem-section" id="ecosistema" aria-labelledby="prisma-ecosystem-title">
        <div className="prisma-section-heading prisma-section-heading-center">
          <span className="prisma-home-kicker">Tres piezas. Un solo control.</span>
          <h2 id="prisma-ecosystem-title">Tablet vende. PC gobierna. App móvil supervisa.</h2>
          <p>PRISMA no es una app suelta. Es una forma de ordenar venta, control y supervisión sin convertir el negocio en sopa de cables.</p>
        </div>
        <div className="prisma-ecosystem-grid">
          {ecosystem.map((item) => (
            <article className="prisma-ecosystem-card" key={item.eyebrow}>
              <span>{item.eyebrow}</span>
              <h3>{item.title}</h3>
              <p>{item.copy}</p>
              <div className="prisma-mini-tags">
                {item.points.map((point) => <b key={point}>{point}</b>)}
              </div>
            </article>
          ))}
        </div>
      </section>

      <PrismaPcInteractiveCommand />

      <section className="prisma-home-section prisma-media-showcase" aria-labelledby="prisma-media-title">
        <div className="prisma-section-heading prisma-section-heading-center">
          <span className="prisma-home-kicker">Venta, control y supervisión visual</span>
          <h2 id="prisma-media-title">La operación se entiende en segundos, no después de tres juntas y un café triste.</h2>
        </div>
        <div className="prisma-media-grid">
          <figure className="prisma-home-media-card">
            <img src="/landing/prisma-pos-vende-con-orden.png" alt="PRISMA Tablet vendiendo con orden" />
            <figcaption>Tablet para venta rápida, inventario claro y cobro ágil.</figcaption>
          </figure>
          <figure className="prisma-home-media-card">
            <img src="/landing/prisma-pc-controla-operacion.png" alt="PRISMA PC controlando la operación" />
            <figcaption>PC para reportes, caja, inventario y visión del negocio.</figcaption>
          </figure>
        </div>
      </section>

      <section className="prisma-home-section prisma-split" aria-labelledby="prisma-multistore-title">
        <div>
          <span className="prisma-home-kicker">Varias tiendas. Una sola vista.</span>
          <h2 id="prisma-multistore-title">Cuando operas varios puntos de venta, preguntar “¿cómo vamos?” ya no alcanza.</h2>
          <p>
            PRISMA te ayuda a comparar ventas, inventario, alertas y desempeño por sucursal sin perseguir capturas de WhatsApp
            como cobrador de tanda digital.
          </p>
          <ul className="prisma-check-list">
            <li>Ventas por sucursal, caja, usuario o periodo.</li>
            <li>Productos agotados, críticos o sobrados por tienda.</li>
            <li>Pedidos sugeridos según rotación y cobertura.</li>
            <li>Sucursales con mejor y peor desempeño operativo.</li>
          </ul>
        </div>
        <figure className="prisma-home-media-card prisma-multistore-photo">
          <img src="/landing/prisma-multisucursal-control-total.png" alt="PRISMA ventas e inventario en paralelo por sucursal" />
        </figure>
      </section>

      <section className="prisma-home-section prisma-split prisma-split-reverse" aria-labelledby="prisma-replenishment-title">
        <img className="prisma-panel-asset" src="/landing/prisma-smart-replenishment.svg" alt="Visual conceptual de reabasto inteligente" />
        <div>
          <span className="prisma-home-kicker">Pedidos más inteligentes</span>
          <h2 id="prisma-replenishment-title">Compra con datos, no con nervios.</h2>
          <p>
            PRISMA puede leer ventas, existencias, rotación y cobertura para ayudarte a pedir lo que toca, cuando toca.
            Menos compras a ciegas. Menos quiebres. Menos dinero dormido en anaquel.
          </p>
          <ul className="prisma-check-list">
            <li>Detecta quiebres antes de perder ventas.</li>
            <li>Evita sobreinventario que amarra capital.</li>
            <li>Convierte patrones de venta en sugerencias de pedido.</li>
            <li>Prioriza proveedores según necesidad real.</li>
          </ul>
        </div>
      </section>

      <section className="prisma-home-section prisma-questions" aria-labelledby="prisma-questions-title">
        <div className="prisma-section-heading prisma-section-heading-center">
          <span className="prisma-home-kicker">Lo que antes preguntabas por WhatsApp</span>
          <h2 id="prisma-questions-title">PRISMA te lo muestra antes de que se vuelva incendio.</h2>
        </div>
        <div className="prisma-question-grid">
          {questions.map((question) => <div className="prisma-question" key={question}>{question}</div>)}
        </div>
      </section>

      <section className="prisma-home-section prisma-before-after prisma-before-after-story" aria-labelledby="prisma-before-title">
        <div className="prisma-section-heading prisma-section-heading-center">
          <span className="prisma-home-kicker">Antes vs con PRISMA</span>
          <h2 id="prisma-before-title">Deja de adivinar. Controla ventas, stock y alertas antes de que te cuesten dinero.</h2>
          <p className="prisma-section-lead">
            La diferencia no es trabajar más duro. Es dejar de administrar como detective cansado y empezar a ver la operación completa.
          </p>
        </div>
        <div className="prisma-compare-flow" aria-label="Comparativo antes y con PRISMA">
          {comparisonRows.map(([before, after], index) => (
            <article className="prisma-compare-step" key={before}>
              <div className="prisma-compare-number">{String(index + 1).padStart(2, "0")}</div>
              <div className="prisma-compare-before"><span>Antes</span><p>{before}</p></div>
              <div className="prisma-compare-arrow" aria-hidden="true">→</div>
              <div className="prisma-compare-after"><span>Con PRISMA</span><p>{after}</p></div>
            </article>
          ))}
        </div>
      </section>

      <section className="prisma-home-final" aria-labelledby="prisma-final-title">
        <div className="prisma-final-glow" />
        <img src="/brand/prisma-logo-official.png" alt="PRISMA" />
        <div>
          <span className="prisma-home-kicker">Tu operación ya está hablando. PRISMA la traduce.</span>
          <h2 id="prisma-final-title">Toma el control antes de que el desorden te cobre factura.</h2>
          <p>
            Cobrar es apenas el timbre de la tienda. PRISMA te enseña qué se movió, qué falta, quién tocó qué
            y dónde se está fugando la operación antes de que el negocio empiece a pedir rescate.
          </p>
          <a href="/dashboard" className="prisma-home-primary">Ver dashboard operativo</a>
        </div>
      </section>
    </div>
  );
}
