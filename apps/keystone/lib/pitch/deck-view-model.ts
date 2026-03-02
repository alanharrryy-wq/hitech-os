import {
  PITCH_DECK_FIXTURE,
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES,
  PITCH_SCREEN_FIXTURES,
  type PitchDeck,
  type PitchFeature,
  type PitchNavigationLink,
  type PitchScreen,
  type PitchScreen01,
  type PitchScreen02,
  type PitchScreen03,
  type PitchScreen04,
  type PitchScreenSlug,
  type PitchValuationBlock
} from "@hitech/contracts";

export type PitchDeckTone = "industrial" | "platform" | "valuation" | "integrated";

export interface PitchDeckIdentity {
  readonly deckId: string;
  readonly version: string;
  readonly locale: string;
  readonly copyLockNotice: string;
  readonly tone: PitchDeckTone;
  readonly shortLabel: string;
  readonly longLabel: string;
}

export interface PitchDeckProgress {
  readonly currentIndex: number;
  readonly total: number;
  readonly percent: number;
  readonly label: string;
}

export interface PitchDeckBreadcrumb {
  readonly id: string;
  readonly label: string;
  readonly href: string;
  readonly current: boolean;
}

export interface PitchRouteIntent {
  readonly slug: PitchScreenSlug;
  readonly href: string;
  readonly order: number;
  readonly title: string;
  readonly icon: PitchIconKey;
  readonly intent: string;
  readonly investorLearns: string;
  readonly recommended: boolean;
  readonly cluster: "engine" | "platform" | "economics";
  readonly anchor: string;
  readonly metricHint: string;
  readonly confidenceBand: "anchor" | "signal" | "upside";
}

export interface PitchSectionAnchor {
  readonly id: string;
  readonly label: string;
  readonly eyebrow: string;
  readonly description: string;
}

export interface PitchSparkPoint {
  readonly id: string;
  readonly x: number;
  readonly y: number;
  readonly label: string;
}

export interface PitchGaugeModel {
  readonly id: string;
  readonly label: string;
  readonly value: number;
  readonly max: number;
  readonly unit: string;
  readonly score: number;
  readonly band: "critical" | "watch" | "healthy";
}

export interface PitchDataChipModel {
  readonly id: string;
  readonly label: string;
  readonly tone: "gold" | "teal" | "cyan" | "brown" | "neutral";
  readonly emphasis: "soft" | "strong";
}

export interface PitchBadgeModel {
  readonly id: string;
  readonly text: string;
  readonly polarity: "positive" | "neutral" | "critical";
}

export interface PitchFeatureToggleModel {
  readonly id: string;
  readonly label: string;
  readonly detail: string;
  readonly featureIds: readonly string[];
}

export interface PitchComparisonScore {
  readonly id: string;
  readonly label: string;
  readonly left: number;
  readonly right: number;
  readonly delta: number;
  readonly narrative: string;
}

export interface PitchInvestmentPhases {
  readonly phase1?: string;
  readonly phase2?: string;
}

export interface PitchDoubleEngineViewModel {
  readonly screen: PitchScreen01;
  readonly leftBadges: readonly PitchBadgeModel[];
  readonly rightBadges: readonly PitchBadgeModel[];
  readonly leftGauge: PitchGaugeModel;
  readonly rightGauge: PitchGaugeModel;
  readonly duelSparkline: readonly PitchSparkPoint[];
  readonly capabilityChips: readonly PitchDataChipModel[];
  readonly sectionAnchors: readonly PitchSectionAnchor[];
}

export interface PitchIndustrialFlowViewModel {
  readonly screen: PitchScreen02;
  readonly kpiChips: readonly PitchDataChipModel[];
  readonly valueSparkline: readonly PitchSparkPoint[];
  readonly marginGauge: PitchGaugeModel;
  readonly cycleGauge: PitchGaugeModel;
  readonly sectionAnchors: readonly PitchSectionAnchor[];
}

export interface PitchHiTechOsViewModel {
  readonly screen: PitchScreen03;
  readonly featureChips: readonly PitchDataChipModel[];
  readonly capabilitySparkline: readonly PitchSparkPoint[];
  readonly reliabilityGauge: PitchGaugeModel;
  readonly toggleGroups: readonly PitchFeatureToggleModel[];
  readonly sectionAnchors: readonly PitchSectionAnchor[];
}

export interface PitchValuationViewModel {
  readonly screen: PitchScreen04;
  readonly valuationBlocks: readonly PitchValuationBlock[];
  readonly expansionSparkline: readonly PitchSparkPoint[];
  readonly riskGauge: PitchGaugeModel;
  readonly scalabilityGauge: PitchGaugeModel;
  readonly comparisonScores: readonly PitchComparisonScore[];
  readonly phases: PitchInvestmentPhases;
  readonly sectionAnchors: readonly PitchSectionAnchor[];
}

export interface PitchDeckViewModel {
  readonly deck: PitchDeck;
  readonly identity: PitchDeckIdentity;
  readonly routes: readonly PitchRouteIntent[];
  readonly screens: {
    readonly "01-double-engine": PitchDoubleEngineViewModel;
    readonly "02-industrial-flow": PitchIndustrialFlowViewModel;
    readonly "03-hitech-os": PitchHiTechOsViewModel;
    readonly "04-valuation": PitchValuationViewModel;
  };
}

export type PitchIconKey =
  | "compass"
  | "engine"
  | "factory"
  | "network"
  | "shield"
  | "currency"
  | "layers"
  | "pulse"
  | "radar"
  | "timeline"
  | "target"
  | "bridge"
  | "sunburst"
  | "spectrum"
  | "chart"
  | "control";

const BRAND_COLORS = {
  gold: "#AB7B26",
  deepTeal: "#026F86",
  cyan: "#02A7CA",
  brown: "#553E13"
} as const;

const ROUTE_INTENT_TEXT: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine": "Presenta el acople entre infraestructura crítica y plataforma propietaria.",
  "02-industrial-flow":
    "Demuestra recurrencia operativa, captura de margen y capacidad de reinversión.",
  "03-hitech-os":
    "Muestra control digital, trazabilidad y operación lista para exigencia farmacéutica.",
  "04-valuation": "Conecta operación + software con expansión de múltiplo y estructura de inversión."
};

const ROUTE_INVESTOR_LEARNS: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine":
    "Por qué el modelo crea barrera industrial y software en el mismo activo.",
  "02-industrial-flow": "Cómo el flujo mensual se traduce en utilidad anual predecible.",
  "03-hitech-os":
    "Qué capacidades soportan control de activos críticos y compliance operativo.",
  "04-valuation": "Dónde ocurre la expansión de valor y cómo se estructura el retorno."
};

const ROUTE_METRIC_HINT: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine": "Módulos activos + capacidades de plataforma",
  "02-industrial-flow": "Utilidad mensual, anualización y cobertura",
  "03-hitech-os": "Cobertura funcional por categoría",
  "04-valuation": "Múltiplo, riesgo y escalabilidad"
};

const ROUTE_CLUSTERS: Readonly<Record<PitchScreenSlug, "engine" | "platform" | "economics">> = {
  "01-double-engine": "engine",
  "02-industrial-flow": "engine",
  "03-hitech-os": "platform",
  "04-valuation": "economics"
};

const ROUTE_ICON: Readonly<Record<PitchScreenSlug, PitchIconKey>> = {
  "01-double-engine": "engine",
  "02-industrial-flow": "factory",
  "03-hitech-os": "network",
  "04-valuation": "chart"
};

const ROUTE_ANCHOR: Readonly<Record<PitchScreenSlug, string>> = {
  "01-double-engine": "double-engine",
  "02-industrial-flow": "industrial-flow",
  "03-hitech-os": "hitech-os",
  "04-valuation": "valuation"
};

const ROUTE_CONFIDENCE: Readonly<Record<PitchScreenSlug, "anchor" | "signal" | "upside">> = {
  "01-double-engine": "anchor",
  "02-industrial-flow": "anchor",
  "03-hitech-os": "signal",
  "04-valuation": "upside"
};

const FEATURE_CATEGORY_STORIES: Readonly<Record<PitchFeature["category"], string>> = {
  operation: "Operación activa y respuesta en tiempo de ejecución.",
  quality: "Calidad certificable para auditorías técnicas.",
  traceability: "Historial consultable de punta a punta.",
  visibility: "Transparencia para cliente y stakeholders.",
  vertical: "Adaptación por industria de alta exigencia."
};

const INVESTOR_PATH: readonly PitchScreenSlug[] = [
  "01-double-engine",
  "02-industrial-flow",
  "03-hitech-os",
  "04-valuation"
];

const SECTION_ANCHORS: Readonly<Record<PitchScreenSlug, readonly PitchSectionAnchor[]>> = {
  "01-double-engine": [
    {
      id: "duality-overview",
      label: "Visión dual",
      eyebrow: "Contexto",
      description: "Relación entre infraestructura física y capa digital propietaria."
    },
    {
      id: "duality-capabilities",
      label: "Capacidades",
      eyebrow: "Detalle",
      description: "Comparación de fortalezas operativas vs plataforma."
    },
    {
      id: "duality-positioning",
      label: "Posicionamiento",
      eyebrow: "Mensaje",
      description: "Síntesis del diferencial estratégico del modelo."
    }
  ],
  "02-industrial-flow": [
    {
      id: "flow-kpis",
      label: "KPIs",
      eyebrow: "Rendimiento",
      description: "Indicadores de base instalada, facturación y utilidad."
    },
    {
      id: "flow-cycle",
      label: "Ciclo",
      eyebrow: "Continuidad",
      description: "Cobertura de 35 meses y reinicio operativo."
    },
    {
      id: "flow-unit-economics",
      label: "Economía unitaria",
      eyebrow: "Margen",
      description: "Relación entre ingreso mensual y utilidad mensual."
    }
  ],
  "03-hitech-os": [
    {
      id: "platform-capabilities",
      label: "Capacidades",
      eyebrow: "Plataforma",
      description: "Mapa funcional de operación, calidad y trazabilidad."
    },
    {
      id: "platform-control",
      label: "Control",
      eyebrow: "Interacción",
      description: "Controles para estado de módulos y alertas preventivas."
    },
    {
      id: "platform-story",
      label: "Historia",
      eyebrow: "Narrativa",
      description: "Evolución de una solución operativa a activo digital escalable."
    }
  ],
  "04-valuation": [
    {
      id: "valuation-structure",
      label: "Estructura",
      eyebrow: "Modelo",
      description: "Comparativa entre unidad tradicional y versión integrada."
    },
    {
      id: "valuation-expansion",
      label: "Expansión",
      eyebrow: "Múltiplo",
      description: "Lectura de expansión de valor por software e IP."
    },
    {
      id: "valuation-investment",
      label: "Inversión",
      eyebrow: "Fases",
      description: "Fases de inversión y retorno esperado sin romper continuidad."
    }
  ]
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function toInteger(input: string): number {
  const normalized = input.replace(/[^0-9.-]/g, "");
  const parsed = Number.parseFloat(normalized);
  if (Number.isFinite(parsed)) {
    return parsed;
  }

  return 0;
}

function asPercent(value: number, max: number): number {
  if (max <= 0) {
    return 0;
  }

  return clamp(Math.round((value / max) * 100), 0, 100);
}

function numericBand(score: number): "critical" | "watch" | "healthy" {
  if (score >= 70) {
    return "healthy";
  }

  if (score >= 45) {
    return "watch";
  }

  return "critical";
}

function createRouteIntents(links: readonly PitchNavigationLink[]): readonly PitchRouteIntent[] {
  return links.map((link) => ({
    slug: link.slug,
    href: link.href,
    order: link.order,
    title: link.title,
    icon: ROUTE_ICON[link.slug],
    intent: ROUTE_INTENT_TEXT[link.slug],
    investorLearns: ROUTE_INVESTOR_LEARNS[link.slug],
    recommended: INVESTOR_PATH.indexOf(link.slug) === link.order - 1,
    cluster: ROUTE_CLUSTERS[link.slug],
    anchor: ROUTE_ANCHOR[link.slug],
    metricHint: ROUTE_METRIC_HINT[link.slug],
    confidenceBand: ROUTE_CONFIDENCE[link.slug]
  }));
}
