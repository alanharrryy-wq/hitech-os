import styles from "./prisma-eit-public-sober-shell.module.css";

const publicSignals = [
  { label: "Public status", value: "Sober", tone: "ready" },
  { label: "Runtime role", value: "EIT/Web", tone: "neutral" },
  { label: "Governor mode", value: "Reference safe", tone: "ready" },
  { label: "Visual budget", value: "Low drama", tone: "neutral" },
];

const rules = [
  "Public readability first: message, CTA and trust copy win over effects.",
  "Atmosphere Engine is allowed only as low-intensity mineral/light field.",
  "No WebGL, no Pixi vapor, no heavy blur, no dark storm active background.",
  "This route is an isolated validation surface; it does not rewrite the live public page.",
];

export default function PrismaEitPublicSoberSurfacePage() {
  return (
    <main className={styles.shell} data-prisma-surface="eit-web" data-prisma-pilot="11_eit_web_public_sober_shell">
      <section className={styles.hero}>
        <p className={styles.eyebrow}>PRISMA Surface Visual Governor · Pilot 11</p>
        <h1>EIT/Web Public Sober Shell</h1>
        <p className={styles.lead}>
          Public-facing reference surface for a calm, trustworthy and readable PRISMA web experience.
          This is a governed preview route, not a destructive rewrite of the public homepage.
        </p>
        <div className={styles.actions}>
          <a href="/" className={styles.primaryAction}>Return to public root</a>
          <a href="/surface-governor-public-sober" className={styles.secondaryAction}>Reference route</a>
        </div>
      </section>

      <section className={styles.signalGrid} aria-label="Surface signals">
        {publicSignals.map((item) => (
          <article className={styles.signalCard} data-tone={item.tone} key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </section>

      <section className={styles.contractPanel}>
        <div>
          <p className={styles.eyebrow}>Safety contract</p>
          <h2>Calm public surface, governed by budget</h2>
        </div>
        <ul>
          {rules.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
