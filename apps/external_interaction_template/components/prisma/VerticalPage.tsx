import { notFound } from "next/navigation";
import { getVertical } from "@/content/verticals";
import { CtaBand } from "./CtaBand";

export function VerticalPage({ slug }: { slug: string }) {
  const vertical = getVertical(slug);
  if (!vertical) notFound();

  return (
    <>
      <section className="page-hero">
        <div className="page-hero-inner two-col">
          <div>
            <div className="eyebrow">PRISMA {vertical.name}</div>
            <h1 className="large-title">{vertical.headline}</h1>
            <p className="lead">{vertical.promise}</p>
            <ul className="check-list">
              <li><strong>Cliente ideal:</strong>&nbsp;{vertical.audience}</li>
              <li><strong>Flujo madre:</strong>&nbsp;{vertical.flow.join(" -> ")}</li>
            </ul>
          </div>
          <div className="card">
            <img src={vertical.image} alt={`PRISMA ${vertical.name}`} style={{ borderRadius: 22 }} />
          </div>
        </div>
      </section>
      <section className="section">
        <div className="eyebrow">Superficies</div>
        <h2 className="large-title">Qué hace cada app en {vertical.name}.</h2>
        <table className="spec-table">
          <tbody>
            <tr><th>Tablet</th><td>{vertical.surfaces.tablet}</td></tr>
            <tr><th>PC</th><td>{vertical.surfaces.pc}</td></tr>
            <tr><th>Mobile</th><td>{vertical.surfaces.mobile}</td></tr>
            <tr><th>Core</th><td>{vertical.surfaces.core}</td></tr>
            <tr><th>Control</th><td>{vertical.surfaces.control}</td></tr>
          </tbody>
        </table>
      </section>
      <section className="section-tight">
        <div className="dark-band">
          <div className="eyebrow">Aceptación</div>
          <h2 className="large-title">No entra si no deja prueba.</h2>
          <div className="grid-4">
            {vertical.proof.map((item) => (
              <div className="flow-step" key={item}><strong>{item}</strong><span>Debe ser visible, trazable o auditable.</span></div>
            ))}
          </div>
        </div>
      </section>
      <CtaBand />
    </>
  );
}
