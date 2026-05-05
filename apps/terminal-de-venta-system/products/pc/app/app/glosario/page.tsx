import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { TableSimple } from "@components/ui/table-simple";
import { i01GovernanceData } from "@/lib/i01/governance-data";

const rows = [
  { Término: "Panel administrativo de inventario", Uso: "Nombre visible del producto PC", Nota: "preferido" },
  { Término: "Terminal de venta", Uso: "Nombre visible de la gemela Tablet", Nota: "preferido" },
  { Término: "Quiebres de stock", Uso: "Alerta operativa", Nota: "preferido" },
  { Término: "Conteos físicos", Uso: "Módulo y operación", Nota: "preferido" },
  { Término: "Sync", Uso: "Contexto técnico interno", Nota: "tolerado" },
  { Término: "Barcode", Uso: "Incidencias técnicas o validación", Nota: "tolerado" },
  { Término: "SKU", Uso: "Operación comercial y técnica", Nota: "tolerado" }
];

export default function GlosarioPage() {
  return (
    <AppShell currentPath="/glosario">
      <section className="hero">
        <div className="kicker">i01</div>
        <h1 style={{ margin: 0 }}>Glosario visible es-MX</h1>
        <div className="subtle">Capa aditiva para congelar lenguaje visible antes de crecer dashboard, datos y flujos.</div>
      </section>

      <div className="grid cols-2">
        <SectionCard title="Términos guía" subtitle="Lo que sí queremos ver en pantallas, módulos y tableros.">
          <TableSimple columns={["Término", "Uso", "Nota"]} rows={rows} />
        </SectionCard>

        <SectionCard title="KPIs base" subtitle="La primera ola privilegia claridad de negocio antes que maquillaje.">
          <div className="list">
            {i01GovernanceData.kpis.map((item) => (
              <div key={item} className="list-item">{item}</div>
            ))}
          </div>
        </SectionCard>
      </div>
    </AppShell>
  );
}
