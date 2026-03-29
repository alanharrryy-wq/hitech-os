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
import type { ReactElement } from "react";

function renderPage(element: ReactElement): string {
  return renderToStaticMarkup(element);
}

type GenericPitchPage = (input: {
  searchParams: Record<string, string | string[] | undefined>;
}) => Promise<ReactElement>;

async function importPitchPage(modulePath: string): Promise<GenericPitchPage> {
  const module = (await import(/* @vite-ignore */ modulePath)) as {
    default: GenericPitchPage;
  };
  return module.default;
}

describe("pitch route smoke", () => {
  it("/pitch/01-double-engine renders key heading and bullet", async () => {
    const html = renderPage(await PitchDoubleEnginePage({ searchParams: {} }));

    expect(html).toContain("HITECH — ARQUITECTURA DE DOBLE MOTOR");
    expect(html).toContain("MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL");
    expect(html).toContain("19 módulos facturados");
  });

  it("/pitch/02-industrial-flow renders KPI labels", async () => {
    const html = renderPage(await PitchIndustrialFlowPage({ searchParams: {} }));

    expect(html).toContain("CORE HITECH — OPERACIÓN INDUSTRIAL INSTITUCIONAL");
    expect(html).toContain("Risk Method");
    expect(html).toContain("PHA + ATS/JSA");
    expect(html).toContain("Operational Readiness Index");
  });

  it("/pitch/03-hitech-os renders features and strong line", async () => {
    const html = renderPage(await PitchHiTechOsPage({ searchParams: {} }));

    expect(html).toContain("MOTOR 2 — HITECH OS (Infraestructura Digital)");
    expect(html).toContain("Dashboard operativo");
    expect(html).toContain("Modo Industria Farmacéutica");
    expect(html).toContain(
      "Infraestructura digital propietaria diseñada para control de activos críticos."
    );
  });

  it("/pitch/04-valuation renders block headings and table headers", async () => {
    const html = renderPage(await PitchValuationPage({ searchParams: {} }));

    expect(html).toContain("ESTRUCTURA FINANCIERA + VALUACIÓN");
    expect(html).toContain("Unidad Industrial Tradicional");
    expect(html).toContain("Infraestructura Industrial + Software Propietario");
    expect(html).toContain("Estructura de Inversión");
    expect(html).toContain("Modelo");
    expect(html).toContain("Múltiplo");
    expect(html).toContain("Riesgo");
    expect(html).toContain("Escalabilidad");
  });

  it("/pitch/05-inventory-foundation imports page module and renders without throwing", async () => {
    const page = await importPitchPage("../app/pitch/05-inventory-foundation/page");
    const html = renderPage(await page({ searchParams: {} }));

    expect(html).toContain("Interactive demo controls");
    expect(html).toContain("Proceed to Shipments");
    expect(html).toContain("HOLD");
  });

  it("/pitch/06-shipments-receiving renders demo controls and deterministic transitions", async () => {
    const page = await importPitchPage("../app/pitch/06-shipments-receiving/page");
    const defaultHtml = renderPage(await page({ searchParams: {} }));

    expect(defaultHtml).toContain("Interactive demo controls");
    expect(defaultHtml).toContain("Transition timeline");
    expect(defaultHtml).toContain("Current shipmentState");
    expect(defaultHtml).toContain("ARRIVED");
    expect(defaultHtml).toContain("Advance");
  });
});
