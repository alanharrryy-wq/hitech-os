import Link from "next/link";

export default function MobileHomePage() {
  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24 }}>
      <section style={{ maxWidth: 720, display: "grid", gap: 16, textAlign: "center" }}>
        <p style={{ margin: 0, letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--prisma-accent-gold)", fontWeight: 800 }}>PRISMA App</p>
        <h1 style={{ margin: 0, fontSize: "clamp(40px, 8vw, 82px)", lineHeight: 0.96 }}>Tu negocio al día, desde tu celular.</h1>
        <p style={{ margin: 0, color: "var(--prisma-text-secondary)", lineHeight: 1.7 }}>
          Consulta ventas, caja, inventario, alertas y sincronización desde fuentes conectadas de PRISMA.
        </p>
        <Link href="/prisma-app" style={{ justifySelf: "center", padding: "12px 18px", borderRadius: 999, background: "var(--prisma-gold-gradient)", color: "var(--prisma-text-on-gold)", fontWeight: 900 }}>Abrir PRISMA App</Link>
      </section>
    </main>
  );
}
