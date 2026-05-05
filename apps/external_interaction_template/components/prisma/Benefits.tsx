import { home } from "@/content/home";

export function Benefits() {
  return (
    <section className="section">
      <div className="eyebrow">Beneficios</div>
      <h2 className="large-title">Orden operativo sin vender humo con moñito.</h2>
      <div className="grid-3" style={{ marginTop: 26 }}>
        {home.benefits.map((benefit) => (
          <article className="card" key={benefit.title}>
            <h3>{benefit.title}</h3>
            <p>{benefit.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
