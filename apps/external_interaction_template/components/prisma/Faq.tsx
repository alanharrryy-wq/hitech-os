import { faqs } from "@/content/faq";

export function Faq() {
  return (
    <section className="section faq">
      <div>
        <div className="eyebrow">FAQ</div>
        <h2 className="large-title">Preguntas antes de que el caos pregunte por ti.</h2>
        <p className="lead">La web debe explicar lo real, lo demo y lo que sigue. PRISMA no se vende como magia, se vende como control.</p>
      </div>
      <div className="faq-list">
        {faqs.map((faq) => (
          <article className="faq-item" key={faq.question}>
            <h3>{faq.question}</h3>
            <p>{faq.answer}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
