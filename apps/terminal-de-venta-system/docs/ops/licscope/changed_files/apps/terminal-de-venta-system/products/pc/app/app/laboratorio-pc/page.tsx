export const dynamic = "force-static";

const labLinks = [
  {
    title: "Referencia visual PC",
    href: "/laboratorio-pc/referencia-visual",
    detail: "Materiality Catalog, Cloudglass, recetas y contratos visuales fuera del producto cliente."
  },
  {
    title: "Liquid Glass Lab",
    href: "/laboratorio-pc/referencia-visual/liquid-glass",
    detail: "Director visual oscuro y pruebas atmosféricas centralizadas."
  },
  {
    title: "Glass Capsules Lab",
    href: "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
    detail: "Banco óptico de cápsulas oscuras, aislado del PC operativo claro."
  },
  {
    title: "Chart Lab",
    href: "/laboratorio-pc/chart-lab?preview=charts",
    detail: "Inspector de atlas, pasaportes, recetas y metadata ChartOps."
  },
  {
    title: "Dashboard Governor Lab",
    href: "/laboratorio-pc/dashboard-governor",
    detail: "Ensayo visual del dashboard, separado de /dashboard productivo."
  }
];

export default function PcLabHubPage() {
  return (
    <main
      style={{ minHeight: "100vh", padding: "52px", color: "#eef6ff", background: "linear-gradient(135deg, #06101d, #111827 56%, #030712)" }}
      data-prisma-panel="pc.laboratorio.pc.route"
      data-prisma-surface="pc"
      data-prisma-route="/laboratorio-pc"
    >
      <section style={{ maxWidth: 1120, margin: "0 auto", display: "grid", gap: 22 }}>
        <a href="/dashboard" style={{ color: "#9cc3ff", textDecoration: "none", fontWeight: 900 }}>← Volver a PC cliente</a>
        <div style={{ border: "1px solid rgba(255,255,255,.16)", borderRadius: 28, padding: 28, background: "rgba(255,255,255,.07)", boxShadow: "0 24px 80px rgba(0,0,0,.30)" }}>
          <p style={{ margin: 0, color: "#a9c7ff", textTransform: "uppercase", letterSpacing: ".16em", fontSize: 12, fontWeight: 900 }}>PRISMA PC · Laboratorio aislado</p>
          <h1 style={{ margin: "10px 0 0", fontSize: "clamp(34px, 5vw, 68px)", lineHeight: 1 }}>Interfaces oscuras centralizadas</h1>
          <p style={{ maxWidth: 780, color: "#c8d6eb", fontSize: 18, lineHeight: 1.7 }}>Este hub mantiene QA, visual labs y pruebas oscuras fuera de la navegación de cliente final. Producto claro por fuera, laboratorio eléctrico por dentro.</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
          {labLinks.map((item) => (
            <a key={item.href} href={item.href} style={{ color: "inherit", textDecoration: "none", border: "1px solid rgba(255,255,255,.14)", borderRadius: 22, padding: 20, background: "rgba(255,255,255,.06)", minHeight: 152 }}>
              <strong style={{ display: "block", fontSize: 20 }}>{item.title}</strong>
              <span style={{ display: "block", marginTop: 10, color: "#b8c7dd", lineHeight: 1.55 }}>{item.detail}</span>
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}
