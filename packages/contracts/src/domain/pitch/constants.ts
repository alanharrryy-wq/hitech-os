export const PITCH_DOMAIN_ID = "pitch";
export const PITCH_DOMAIN_VERSION = "2.0.0";

export const PITCH_ROUTE_DOUBLE_ENGINE = "/pitch/01-double-engine";
export const PITCH_ROUTE_INDUSTRIAL_FLOW = "/pitch/02-industrial-flow";
export const PITCH_ROUTE_HITECH_OS = "/pitch/03-hitech-os";
export const PITCH_ROUTE_VALUATION = "/pitch/04-valuation";

export const PITCH_SCREEN_IDS = ["double-engine", "industrial-flow", "hitech-os", "valuation"] as const;
export const PITCH_SCREEN_ROUTES = [
  PITCH_ROUTE_DOUBLE_ENGINE,
  PITCH_ROUTE_INDUSTRIAL_FLOW,
  PITCH_ROUTE_HITECH_OS,
  PITCH_ROUTE_VALUATION
] as const;

export const PITCH_DOUBLE_ENGINE_TITLE = "HITECH — ARQUITECTURA DE DOBLE MOTOR";
export const PITCH_DOUBLE_ENGINE_LEFT_BULLETS = [
  "19 módulos facturados",
  "6 módulos listos (requieren 100k)",
  "12 módulos mensuales negociados",
  "420 módulos instalados en SRG",
  "Ciclo recurrente obligatorio de mantenimiento"
] as const;
export const PITCH_DOUBLE_ENGINE_LEFT_MICROCOPY = "Infraestructura eléctrica crítica certificada CRS + REMMt1.";
export const PITCH_DOUBLE_ENGINE_RIGHT_BULLETS = [
  "Plataforma digital propietaria",
  "Estandarización nivel automotriz",
  "Trazabilidad técnica completa",
  "Registro calibración CRS",
  "Multiusuario / multirol",
  "Escalable a multiindustria"
] as const;
export const PITCH_DOUBLE_ENGINE_RIGHT_MICROCOPY = "Nacido por necesidad operativa real.";
export const PITCH_DOUBLE_ENGINE_IMPLICIT_MESSAGE = "No soy proveedor. Soy sistema.";

export const PITCH_INDUSTRIAL_FLOW_TITLE = "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE";
export const PITCH_INDUSTRIAL_FLOW_TOTAL_MODULES = 420;
export const PITCH_INDUSTRIAL_FLOW_MONTHLY_MODULES = 12;
export const PITCH_INDUSTRIAL_FLOW_MONTHLY_BILLING_USD = 228000;
export const PITCH_INDUSTRIAL_FLOW_MONTHLY_PROFIT_USD = 91000;
export const PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_USD = 1092000;
export const PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_COMPACT_TEXT = "~$1.09M utilidad anual";
export const PITCH_INDUSTRIAL_FLOW_CYCLE_MONTHS = 35;
export const PITCH_INDUSTRIAL_FLOW_CYCLE_STATEMENT =
  "Ciclo continuo 35 meses para cubrir total → reinicio automático.";
export const PITCH_INDUSTRIAL_FLOW_MICROCOPY = "Mercado interno ya existente, no especulativo.";

export const PITCH_HITECH_OS_TITLE = "MOTOR 2 — HITECH OS (Infraestructura Digital)";
export const PITCH_HITECH_OS_BULLETS = [
  "Dashboard operativo",
  "Control activo por módulo",
  "Historial técnico completo",
  "Calibración certificada CRS",
  "Alertas preventivas automáticas",
  "Panel cliente transparente",
  "Modo Industria Farmacéutica"
] as const;
export const PITCH_HITECH_OS_STRONG_PHRASE =
  "Infraestructura digital propietaria diseñada para control de activos críticos.";

export const PITCH_VALUATION_TITLE = "ESTRUCTURA FINANCIERA + VALUACIÓN";
export const PITCH_VALUATION_BLOCK_ONE_LINES = [
  "Genera flujo",
  "Margen 40%",
  "Valuación típica 2–3x utilidad",
  "Valuación estimada: 2.5–3M"
] as const;
export const PITCH_VALUATION_BLOCK_TWO_LINES = [
  "Flujo recurrente",
  "Propiedad intelectual",
  "Escalabilidad SaaS",
  "Barrera técnica alta",
  "Múltiplo superior"
] as const;
export const PITCH_VALUATION_COMBINED_LINE = "Valuación combinada estimada: 4–6M";
export const PITCH_VALUATION_BLOCK_THREE_LINES = [
  "Fase 1: $100k → 25% rendimiento → sin dilución",
  "Fase 2: $200k → 3–5% equity (según valuación final acordada)"
] as const;
export const PITCH_VALUATION_TABLE_HEADERS = ["Modelo", "Múltiplo", "Riesgo", "Escalabilidad"] as const;
export const PITCH_VALUATION_TABLE_ROWS = [
  ["Industrial tradicional", "Bajo", "Medio", "Limitada"],
  ["Industrial + Software", "Alto", "Controlado", "Alta"]
] as const;

export const PITCH_LAYOUT_SPLIT_PERCENT = 50;
export const MONTHS_PER_YEAR = 12;
export const PITCH_COPY_FINGERPRINT_VERSION = "pitch-copy-fingerprint-v1";
