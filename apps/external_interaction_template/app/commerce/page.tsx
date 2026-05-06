import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Footer } from "@/components/prisma/Footer";
import { Nav } from "@/components/prisma/Nav";
import { getVertical } from "@/content/verticals";
import { seo } from "@/content/seo";

export const metadata: Metadata = seo.commerce;

export default function Page() {
  const vertical = getVertical("commerce");
  if (!vertical) notFound();

  return (
    <main className="site-shell">
      <Nav />

      <section className="page-hero" style={{ paddingTop: 56, paddingBottom: 56 }}>
        <div className="page-hero-inner two-col" style={{ alignItems: "center", gap: 32 }}>
          <div style={{ maxWidth: 640 }}>
            <div className="eyebrow">PRISMA COMMERCE</div>
            <h1
              className="large-title"
              style={{ fontSize: "clamp(38px, 4.5vw, 56px)", lineHeight: 1.04, marginTop: 18 }}
            >
              Venta, caja e inventario para negocios que no pueden perder el control.
            </h1>
            <p className="lead" style={{ maxWidth: 620, marginTop: 24 }}>
              Para restaurantes, tiendas, gimnasios y negocios con caja activa que necesitan vender rápido, controlar cierres y detectar descuadres antes de que se vuelvan pérdida.
            </p>

            <div className="pill-row" style={{ marginTop: 28, gap: 12, flexWrap: "wrap" }}>
              <span className="pill" style={{ padding: "10px 16px", borderRadius: 18 }}>
                Cliente ideal: Restaurantes, tiendas, gimnasios y negocios con caja activa
              </span>
            </div>

            <div className="flow" style={{ marginTop: 28, gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 12 }}>
              {vertical.flow.map((step) => (
                <div key={step} className="flow-step" style={{ padding: 16, borderRadius: 18 }}>
                  <strong>{step}</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="card" style={{ maxWidth: 520, margin: "0 auto", padding: 22 }}>
            <img
              src={vertical.image}
              alt="PRISMA Commerce"
              style={{ width: "100%", height: "auto", borderRadius: 22, display: "block" }}
            />
          </div>
        </div>
      </section>

      <section className="section-tight" style={{ paddingTop: 40, paddingBottom: 44 }}>
        <div className="dark-band">
          <div className="eyebrow">Prioridades</div>
          <h2 className="large-title" style={{ fontSize: "clamp(26px, 3vw, 36px)", marginBottom: 24 }}>
            Vende rápido. Controla caja. Supervisa inventario.
          </h2>
          <div className="grid-3" style={{ gap: 16 }}>
            <div className="flow-step">
              <strong>Vende rápido</strong>
              <span>Procesa ventas y caja desde el punto de venta con flujo claro.</span>
            </div>
            <div className="flow-step">
              <strong>Controla caja</strong>
              <span>Registra cierres, movimientos y descuadres antes de cerrar el día.</span>
            </div>
            <div className="flow-step">
              <strong>Supervisa inventario</strong>
              <span>Monitorea existencias, alertas y stock bajo desde cualquier dispositivo.</span>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
