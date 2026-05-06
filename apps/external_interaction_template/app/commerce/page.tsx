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

      <section
        className="page-hero"
        style={{
          paddingTop: 56,
          paddingBottom: 56,
          background: "linear-gradient(135deg, #f3f7fb 0%, #eaf2fb 50%, #f7f4ec 100%)",
          position: "relative",
          overflow: "hidden"
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(circle at 20% 30%, rgba(76, 201, 255, 0.08), transparent 40%), radial-gradient(circle at 80% 70%, rgba(215, 168, 77, 0.06), transparent 35%)",
            pointerEvents: "none"
          }}
        ></div>
        <div className="page-hero-inner two-col" style={{ alignItems: "center", gap: 32, position: "relative", zIndex: 1 }}>
          <div style={{ maxWidth: 580 }}>
            <div className="eyebrow">PRISMA COMMERCE</div>
            <h1
              className="large-title"
              style={{ fontSize: "clamp(32px, 3.7vw, 46px)", lineHeight: 1.08, marginTop: 18 }}
            >
              Venta, caja e inventario para negocios que no pueden perder el control.
            </h1>
            <p className="lead" style={{ maxWidth: 540, marginTop: 24 }}>
              Para restaurantes, tiendas, gimnasios y negocios con caja activa que necesitan vender rápido, controlar cierres y detectar descuadres antes de que se vuelvan pérdida.
            </p>

            <div
              style={{
                marginTop: 28,
                background: "rgba(255, 255, 255, 0.72)",
                border: "1px solid rgba(13, 32, 58, 0.12)",
                borderRadius: 22,
                padding: "16px 20px",
                boxShadow: "0 8px 24px rgba(17, 42, 82, 0.08)",
                color: "var(--ink)"
              }}
            >
              <strong>Cliente ideal:</strong> Restaurantes, tiendas, gimnasios y negocios con caja activa
            </div>

            <div
              style={{
                marginTop: 28,
                display: "flex",
                flexWrap: "wrap",
                gap: 10
              }}
            >
              {vertical.flow.map((step) => (
                <span
                  key={step}
                  style={{
                    padding: "8px 14px",
                    borderRadius: 999,
                    background: "rgba(255, 255, 255, 0.8)",
                    border: "1px solid rgba(13, 32, 58, 0.1)",
                    color: "var(--ink-soft)",
                    fontSize: 14,
                    fontWeight: 600,
                    display: "inline-flex",
                    alignItems: "center"
                  }}
                >
                  {step}
                </span>
              ))}
            </div>
          </div>

          <div
            className="card"
            style={{
              maxWidth: 460,
              margin: "0 auto",
              padding: 22,
              boxShadow: "0 16px 40px rgba(17, 42, 82, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8)"
            }}
          >
            <img
              src={vertical.image}
              alt="PRISMA Commerce"
              style={{
                width: "100%",
                height: "auto",
                borderRadius: 22,
                display: "block",
                filter: "saturate(0.92) contrast(0.96) brightness(0.97)"
              }}
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
