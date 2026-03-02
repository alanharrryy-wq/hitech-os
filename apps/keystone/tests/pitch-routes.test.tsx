import { PITCH_ROUTES, PITCH_SCREEN_ORDER, PITCH_SCREEN_TITLES } from "@hitech/contracts";
import { beforeEach, describe, expect, it } from "vitest";
import {
  ensureContainsAll,
  PITCH_CANONICAL_ROUTES,
  renderPitchRoute,
  resetNavigationMockState
} from "./_utils/pitch-test-harness";

describe("pitch route smoke", () => {
  beforeEach(() => {
    resetNavigationMockState();
  });

  it("/pitch renders index shell and canonical links", () => {
    const html = renderPitchRoute("/pitch");

    expect(html).toContain("Keystone Pitch Deck");
    expect(html).toContain("Contracts-first pitch module with deterministic screen fixtures");
    expect(html).toContain("Pantallas");
    expect(html).toContain('aria-label="Pitch navigation"');

    for (const slug of PITCH_SCREEN_ORDER) {
      expect(html).toContain(PITCH_ROUTES[slug]);
      expect(html).toContain(PITCH_SCREEN_TITLES[slug]);
    }
  });

  it("renders all canonical routes without crashing", () => {
    for (const route of PITCH_CANONICAL_ROUTES) {
      const html = renderPitchRoute(route);
      expect(html.length).toBeGreaterThan(100);
      expect(html).toContain("Keystone Pitch Deck");
      expect(html).toContain('aria-label="Pitch navigation"');
    }
  });

  it("/pitch/01-double-engine renders key heading and bullet", () => {
    const html = renderPitchRoute("/pitch/01-double-engine");
    ensureContainsAll(html, [
      "HITECH — ARQUITECTURA DE DOBLE MOTOR",
      "MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL",
      "19 módulos facturados"
    ]);
  });

  it("/pitch/02-industrial-flow renders KPI labels", () => {
    const html = renderPitchRoute("/pitch/02-industrial-flow");
    ensureContainsAll(html, [
      "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE",
      "420 módulos totales",
      "12 módulos mensuales",
      "$228k facturación mensual"
    ]);
  });

  it("/pitch/03-hitech-os renders features and strong line", () => {
    const html = renderPitchRoute("/pitch/03-hitech-os");
    ensureContainsAll(html, [
      "MOTOR 2 — HITECH OS (Infraestructura Digital)",
      "Dashboard operativo",
      "Modo Industria Farmacéutica",
      "Infraestructura digital propietaria diseñada para control de activos críticos."
    ]);
  });

  it("/pitch/04-valuation renders block headings and table headers", () => {
    const html = renderPitchRoute("/pitch/04-valuation");
    ensureContainsAll(html, [
      "ESTRUCTURA FINANCIERA + VALUACIÓN",
      "Unidad Industrial Tradicional",
      "Infraestructura Industrial + Software Propietario",
      "Estructura de Inversión",
      "Modelo",
      "Múltiplo",
      "Riesgo",
      "Escalabilidad"
    ]);
  });
});
