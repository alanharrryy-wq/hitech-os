import { site } from "@/content/site";

export function CtaBand() {
  return (
    <section className="section-tight">
      <div className="cta-final">
        <div className="eyebrow">Siguiente paso</div>
        <h2 className="large-title" style={{ marginLeft: "auto", marginRight: "auto" }}>Agenda una demo de PRISMA.</h2>
        <p>Vemos tu operación, ubicamos qué superficie necesitas primero y aterrizamos el flujo sin prometer castillos inflables con ERP adentro.</p>
        <a className="button-primary" href={site.whatsappUrl}>Pedir demo por WhatsApp</a>
      </div>
    </section>
  );
}
