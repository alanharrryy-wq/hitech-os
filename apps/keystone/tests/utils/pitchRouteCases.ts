export interface PitchRouteCase {
  readonly id: string;
  readonly pathname: string;
  readonly relativeRouteFile: string;
  readonly expectedMarkerTexts: readonly string[];
}

export const PITCH_ROUTE_CASES: readonly PitchRouteCase[] = [
  {
    id: "ROUTE_INDEX",
    pathname: "/pitch",
    relativeRouteFile: "app/pitch/page.tsx",
    expectedMarkerTexts: [
      "Keystone Pitch Deck",
      "Contracts-first pitch module with deterministic screen fixtures",
      "Pantallas"
    ]
  },
  {
    id: "ROUTE_01_DOUBLE_ENGINE",
    pathname: "/pitch/01-double-engine",
    relativeRouteFile: "app/pitch/01-double-engine/page.tsx",
    expectedMarkerTexts: [
      "HITECH — ARQUITECTURA DE DOBLE MOTOR",
      "MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL",
      "19 módulos facturados"
    ]
  },
  {
    id: "ROUTE_02_INDUSTRIAL_FLOW",
    pathname: "/pitch/02-industrial-flow",
    relativeRouteFile: "app/pitch/02-industrial-flow/page.tsx",
    expectedMarkerTexts: [
      "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE",
      "420 módulos totales",
      "$228k facturación mensual"
    ]
  },
  {
    id: "ROUTE_03_HITECH_OS",
    pathname: "/pitch/03-hitech-os",
    relativeRouteFile: "app/pitch/03-hitech-os/page.tsx",
    expectedMarkerTexts: [
      "MOTOR 2 — HITECH OS (Infraestructura Digital)",
      "Dashboard operativo",
      "Infraestructura digital propietaria"
    ]
  },
  {
    id: "ROUTE_04_VALUATION",
    pathname: "/pitch/04-valuation",
    relativeRouteFile: "app/pitch/04-valuation/page.tsx",
    expectedMarkerTexts: [
      "ESTRUCTURA FINANCIERA + VALUACIÓN",
      "Estructura de Inversión",
      "Modelo"
    ]
  }
];

export const REQUIRED_PITCH_SUBROUTE_PATHNAMES = Object.freeze([
  "/pitch/01-double-engine",
  "/pitch/02-industrial-flow",
  "/pitch/03-hitech-os",
  "/pitch/04-valuation"
]);
