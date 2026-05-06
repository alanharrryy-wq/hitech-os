import type { Metadata } from "next";
import { CtaBand } from "@/components/prisma/CtaBand";
import { Footer } from "@/components/prisma/Footer";
import { Nav } from "@/components/prisma/Nav";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "Contacto | PRISMA",
  description: "Agenda una demo de PRISMA para tu negocio."
};

export default function ContactPage() {
  return (
    <main className="site-shell">
      <Nav />
      <section className="page-hero">
        <div className="page-hero-inner">
          <div className="eyebrow">Contacto</div>
          <h1 className="large-title">Hablemos de tu operación y la primera superficie a activar.</h1>
          <p className="lead">Cuéntanos tu giro, cuántos puntos de venta tienes y qué necesitas controlar primero: ventas, caja, inventario, órdenes o alertas.</p>
          <div className="hero-actions">
            <a className="button-primary" href={site.whatsappUrl}>Solicitar demo</a>
            <a className="button-secondary" href={`mailto:${site.email}`}>{site.email}</a>
          </div>
        </div>
      </section>
      <CtaBand />
      <Footer />
    </main>
  );
}
