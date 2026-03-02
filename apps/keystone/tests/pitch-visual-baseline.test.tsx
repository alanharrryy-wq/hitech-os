import { PITCH_ROUTES } from "@hitech/contracts";
import { describe, expect, it } from "vitest";
import {
  countInHtml,
  ensureContainsAll,
  normalizeHtml,
  renderPitchRoute
} from "./_utils/pitch-test-harness";

describe("pitch visual baseline sanity", () => {
  it("keeps index route structure and navigation labels", () => {
    const html = renderPitchRoute("/pitch");

    expect(countInHtml(html, 'aria-label="Pitch navigation"')).toBe(1);
    ensureContainsAll(html, [
      "Keystone Pitch Deck",
      "Contracts-first pitch module with deterministic screen fixtures",
      "Pantallas",
      "Selecciona una ruta de pitch"
    ]);

    for (const route of Object.values(PITCH_ROUTES)) {
      expect(html).toContain(route);
    }
  });

  it("keeps screen 01 structure with expected critical panels", () => {
    const html = normalizeHtml(renderPitchRoute("/pitch/01-double-engine"));

    ensureContainsAll(html, [
      "PITCH SCREEN 1",
      "HITECH — ARQUITECTURA DE DOBLE MOTOR",
      "MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL",
      "MOTOR 2 — HITECH OS",
      "Mensaje implícito",
      "Posicionamiento estratégico"
    ]);

    expect(countInHtml(html, "Actual")).toBe(1);
    expect(countInHtml(html, 'aria-label="Pitch navigation"')).toBe(1);
  });

  it("keeps screen 02 structure with KPI and cycle blocks", () => {
    const html = normalizeHtml(renderPitchRoute("/pitch/02-industrial-flow"));

    ensureContainsAll(html, [
      "PITCH SCREEN 2",
      "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE",
      "KPIs operativos",
      "Ciclo de cobertura",
      "Ritmo",
      "35 meses"
    ]);

    expect(countInHtml(html, "Actual")).toBe(1);
    expect(countInHtml(html, 'aria-label="Pitch navigation"')).toBe(1);
  });

  it("keeps screen 03 structure with platform features and strategic line", () => {
    const html = normalizeHtml(renderPitchRoute("/pitch/03-hitech-os"));

    ensureContainsAll(html, [
      "PITCH SCREEN 3",
      "MOTOR 2 — HITECH OS (Infraestructura Digital)",
      "Capacidades de plataforma",
      "Línea estratégica",
      "Enfoque de control de activos críticos"
    ]);

    expect(countInHtml(html, "Actual")).toBe(1);
    expect(countInHtml(html, 'aria-label="Pitch navigation"')).toBe(1);
  });

  it("keeps screen 04 structure with valuation sections and comparison table labels", () => {
    const html = normalizeHtml(renderPitchRoute("/pitch/04-valuation"));

    ensureContainsAll(html, [
      "PITCH SCREEN 4",
      "ESTRUCTURA FINANCIERA + VALUACIÓN",
      "Valuación combinada",
      "Comparación",
      "Modelo",
      "Múltiplo",
      "Riesgo",
      "Escalabilidad"
    ]);

    expect(countInHtml(html, "Actual")).toBe(1);
    expect(countInHtml(html, 'aria-label="Pitch navigation"')).toBe(1);
  });
});
