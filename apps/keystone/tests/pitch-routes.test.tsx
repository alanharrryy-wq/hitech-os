import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

vi.mock("next/navigation", () => {
  return {
    useRouter: () => ({
      replace: vi.fn()
    }),
    usePathname: () => "/pitch",
    useSearchParams: () => new URLSearchParams("")
  };
});

import PitchDoubleEnginePage from "../app/pitch/01-double-engine/page";
import PitchIndustrialFlowPage from "../app/pitch/02-industrial-flow/page";
import PitchHiTechOsPage from "../app/pitch/03-hitech-os/page";
import PitchValuationPage from "../app/pitch/04-valuation/page";

async function renderPage(
  elementOrPromise:
    | ReturnType<typeof PitchDoubleEnginePage>
    | ReturnType<typeof PitchIndustrialFlowPage>
    | ReturnType<typeof PitchHiTechOsPage>
    | ReturnType<typeof PitchValuationPage>
): Promise<string> {
  return renderToStaticMarkup(await elementOrPromise);
}

describe("pitch route smoke", () => {
  it("/pitch/01-double-engine renders key heading and bullet", async () => {
    const html = await renderPage(PitchDoubleEnginePage({ searchParams: {} }));

    expect(html).toContain("HITECH — ARQUITECTURA DE DOBLE MOTOR");
    expect(html).toContain("MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL");
    expect(html).toContain("19 módulos facturados");
  });

  it("/pitch/02-industrial-flow renders KPI labels", async () => {
    const html = await renderPage(PitchIndustrialFlowPage({ searchParams: {} }));

    expect(html).toContain("MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE");
    expect(html).toContain("420 módulos totales");
    expect(html).toContain("12 módulos mensuales");
    expect(html).toContain("$228k facturación mensual");
  });

  it("/pitch/03-hitech-os renders features and strong line", async () => {
    const html = await renderPage(PitchHiTechOsPage({ searchParams: {} }));

    expect(html).toContain("MOTOR 2 — HITECH OS (Infraestructura Digital)");
    expect(html).toContain("Dashboard operativo");
    expect(html).toContain("Modo Industria Farmacéutica");
    expect(html).toContain(
      "Infraestructura digital propietaria diseñada para control de activos críticos."
    );
  });

  it("/pitch/04-valuation renders block headings and table headers", async () => {
    const html = await renderPage(PitchValuationPage({ searchParams: {} }));

    expect(html).toContain("ESTRUCTURA FINANCIERA + VALUACIÓN");
    expect(html).toContain("Unidad Industrial Tradicional");
    expect(html).toContain("Infraestructura Industrial + Software Propietario");
    expect(html).toContain("Estructura de Inversión");
    expect(html).toContain("Modelo");
    expect(html).toContain("Múltiplo");
    expect(html).toContain("Riesgo");
    expect(html).toContain("Escalabilidad");
  });
});
