import { site } from "@/content/site";

export function CtaBand() {
  return (
    <section className="section-tight">
      <div className="cta-final">
        <div className="eyebrow">Siguiente paso</div>
        <h2 className="large-title" style={{ marginLeft: "auto", marginRight: "auto" }}>Agenda una demo y aterriza tu primera superficie.</h2>
        <p>Revisamos tu operación, elegimos si arranca por Tablet, PC o Mobile, y definimos el siguiente paso sin prometer soluciones milagro.</p>
        <a className="button-primary" href={site.whatsappUrl}>Pedir demo por WhatsApp</a>
      </div>
    </section>
  );
}
