import {
  PITCH_VALUATION_ECONOMICS,
  PITCH_DECK_FIXTURE,
  PITCH_SCREEN_FIXTURES,
  type PitchDeck,
  type PitchNavigationLink,
  type PitchScreen,
  type PitchScreen01,
  type PitchScreen02,
  type PitchScreen03,
  type PitchScreen04,
  type PitchScreenSlug
} from "@hitech/contracts";

export interface PitchRouteInsight {
  readonly slug: PitchScreenSlug;
  readonly href: string;
  readonly order: number;
  readonly title: string;
  readonly anchor: string;
  readonly intent: string;
  readonly investorLearns: string;
  readonly routeBadge: string;
  readonly emphasis: "industrial" | "software" | "hybrid" | "operations";
  readonly recommended: boolean;
}

export interface PitchDeckMetaView {
  readonly deckId: string;
  readonly version: string;
  readonly locale: string;
  readonly copyLockNotice: string;
}

export interface PitchDeckViewModel {
  readonly meta: PitchDeckMetaView;
  readonly links: readonly PitchNavigationLink[];
  readonly activeSlug?: PitchScreenSlug;
  readonly indexRoutes: readonly PitchRouteInsight[];
  readonly recommendedPath: readonly PitchRouteInsight[];
  readonly progressLabel: string;
  readonly currentIndex: number;
  readonly totalScreens: number;
  readonly previous?: PitchRouteInsight;
  readonly next?: PitchRouteInsight;
  readonly spotlight: {
    readonly installedBase: string;
    readonly monthlyFlow: string;
    readonly annualUtility: string;
    readonly valuationRange: string;
  };
}

const ROUTE_INTENT: Record<PitchScreenSlug, string> = {
  "01-double-engine": "Muestra la dualidad industrial + software como arquitectura central.",
  "02-industrial-flow": "Demuestra recurrencia operativa y disciplina de flujo en piso.",
  "03-hitech-os": "Conecta capacidades digitales con control y trazabilidad premium.",
  "04-valuation": "Traduce operación + software en estructura financiera defendible.",
  "05-inventory-foundation":
    "Presenta base de inventario con controles determinísticos para ejecución.",
  "06-shipments-receiving":
    "Expone control de embarques y compuertas de calidad de punta a punta."
};

const ROUTE_LEARNINGS: Record<PitchScreenSlug, string> = {
  "01-double-engine": "La tesis no depende de una sola fuente de valor.",
  "02-industrial-flow": "Existe demanda ya operando con señales recurrentes medibles.",
  "03-hitech-os": "La plataforma crea defensibilidad por trazabilidad operativa.",
  "04-valuation": "El múltiplo mejora cuando software y flujo se integran.",
  "05-inventory-foundation": "El control documental y RBAC habilitan compliance continuo.",
  "06-shipments-receiving": "La recepción controlada reduce riesgo en momentos críticos."
};

const ROUTE_BADGES: Record<PitchScreenSlug, string> = {
  "01-double-engine": "Thesis",
  "02-industrial-flow": "Cash Engine",
  "03-hitech-os": "Digital Moat",
  "04-valuation": "Investor Math",
  "05-inventory-foundation": "Run 1",
  "06-shipments-receiving": "Run 2"
};

const ROUTE_EMPHASIS: Record<PitchScreenSlug, PitchRouteInsight["emphasis"]> = {
  "01-double-engine": "hybrid",
  "02-industrial-flow": "industrial",
  "03-hitech-os": "software",
  "04-valuation": "hybrid",
  "05-inventory-foundation": "operations",
  "06-shipments-receiving": "operations"
};

const RECOMMENDED_SLUGS: readonly PitchScreenSlug[] = [
  "01-double-engine",
  "02-industrial-flow",
  "03-hitech-os",
  "04-valuation",
  "06-shipments-receiving"
];

const ANCHOR_BY_SLUG: Record<PitchScreenSlug, string> = {
  "01-double-engine": "double-engine",
  "02-industrial-flow": "industrial-flow",
  "03-hitech-os": "hitech-os",
  "04-valuation": "valuation",
  "05-inventory-foundation": "inventory-foundation",
  "06-shipments-receiving": "shipments-receiving"
};

function formatProgress(currentIndex: number, total: number): string {
  const safeCurrent = Math.max(1, Math.min(total, currentIndex));
  return `${safeCurrent.toString().padStart(2, "0")} / ${total.toString().padStart(2, "0")}`;
}

function asRouteInsight(link: PitchNavigationLink): PitchRouteInsight {
  return {
    slug: link.slug,
    href: link.href,
    order: link.order,
    title: link.title,
    anchor: ANCHOR_BY_SLUG[link.slug],
    intent: ROUTE_INTENT[link.slug],
    investorLearns: ROUTE_LEARNINGS[link.slug],
    routeBadge: ROUTE_BADGES[link.slug],
    emphasis: ROUTE_EMPHASIS[link.slug],
    recommended: RECOMMENDED_SLUGS.includes(link.slug)
  };
}

function computeSpotlight(screen02: PitchScreen02, screen04: PitchScreen04) {
  const installedBase = `TARGET ${PITCH_VALUATION_ECONOMICS.params.targetModules} módulos (no instalado actual)`;

  const monthlyFlow = `${PITCH_VALUATION_ECONOMICS.params.monthlyCadenceModules} módulos/mes tras cierre D30`;

  const annualUtility = screen02.kpis.find((entry) => entry.label.includes("utilidad anual"))?.label ??
    "~$1.09M utilidad anual";

  return {
    installedBase,
    monthlyFlow,
    annualUtility,
    valuationRange: screen04.combinedValuationLine.text
  };
}

function locateAdjacent(
  routes: readonly PitchRouteInsight[],
  activeSlug?: PitchScreenSlug
): { previous?: PitchRouteInsight; next?: PitchRouteInsight; currentIndex: number } {
  if (!activeSlug) {
    return {
      ...(routes[0] ? { next: routes[0] } : {}),
      currentIndex: 1
    };
  }

  const index = routes.findIndex((route) => route.slug === activeSlug);
  if (index < 0) {
    return {
      ...(routes[0] ? { next: routes[0] } : {}),
      currentIndex: 1
    };
  }

  return {
    ...(index > 0 ? { previous: routes[index - 1] } : {}),
    ...(index < routes.length - 1 ? { next: routes[index + 1] } : {}),
    currentIndex: index + 1
  };
}

export function buildPitchDeckViewModel(
  deck: PitchDeck = PITCH_DECK_FIXTURE,
  activeSlug?: PitchScreenSlug
): PitchDeckViewModel {
  const indexRoutes = deck.navigation.links.map(asRouteInsight).sort((a, b) => a.order - b.order);
  const recommendedPath = indexRoutes.filter((route) => route.recommended);
  const adjacency = locateAdjacent(indexRoutes, activeSlug);

  const screen02 = PITCH_SCREEN_FIXTURES["02-industrial-flow"];
  const screen04 = PITCH_SCREEN_FIXTURES["04-valuation"];

  return {
    meta: {
      deckId: deck.meta.deckId,
      version: deck.meta.version,
      locale: deck.meta.locale,
      copyLockNotice: deck.meta.copyLockNotice
    },
    links: deck.navigation.links,
    ...(activeSlug ? { activeSlug } : {}),
    indexRoutes,
    recommendedPath,
    progressLabel: formatProgress(adjacency.currentIndex, deck.screens.length),
    currentIndex: adjacency.currentIndex,
    totalScreens: deck.screens.length,
    ...(adjacency.previous ? { previous: adjacency.previous } : {}),
    ...(adjacency.next ? { next: adjacency.next } : {}),
    spotlight: computeSpotlight(screen02, screen04)
  };
}

export interface PitchScreenBaseViewModel {
  readonly slug: PitchScreenSlug;
  readonly route: string;
  readonly order: number;
  readonly title: string;
  readonly kicker: string;
  readonly thematicLabel: string;
  readonly canonicalTags: readonly string[];
}

export interface PitchScreen01ViewModel extends PitchScreenBaseViewModel {
  readonly left: {
    readonly heading: string;
    readonly bullets: readonly string[];
    readonly microcopy: readonly string[];
  };
  readonly right: {
    readonly heading: string;
    readonly bullets: readonly string[];
    readonly microcopy: readonly string[];
  };
  readonly implicitMessage: string;
  readonly derived: {
    readonly industrialCount: number;
    readonly softwareCount: number;
    readonly balancedIndex: number;
    readonly capabilityChips: readonly string[];
  };
}

export interface PitchScreen02ViewModel extends PitchScreenBaseViewModel {
  readonly kpis: ReadonlyArray<{
    readonly label: string;
    readonly value: string;
    readonly note: string;
  }>;
  readonly cycleLabel: string;
  readonly microcopy: string;
  readonly derived: {
    readonly cycleMonths: number;
    readonly monthlyModules: number;
    readonly annualizedUtilityMillions: number;
    readonly coverageChips: readonly string[];
  };
}

export interface PitchScreen03ViewModel extends PitchScreenBaseViewModel {
  readonly features: ReadonlyArray<{
    readonly text: string;
    readonly category: string;
  }>;
  readonly strongLine: string;
  readonly derived: {
    readonly byCategory: Readonly<Record<string, number>>;
    readonly capabilityChips: readonly string[];
  };
}

export interface PitchScreen04ViewModel extends PitchScreenBaseViewModel {
  readonly blocks: ReadonlyArray<{
    readonly heading: string;
    readonly items: readonly string[];
    readonly phase1?: string;
    readonly phase2?: string;
  }>;
  readonly combinedLine: string;
  readonly comparison: {
    readonly headers: readonly string[];
    readonly rows: ReadonlyArray<readonly string[]>;
  };
  readonly derived: {
    readonly panelLabels: readonly string[];
    readonly riskScale: readonly number[];
    readonly scalabilityScale: readonly number[];
  };
}

function normalizeKicker(order: number): string {
  return `PITCH SCREEN ${order.toString().padStart(2, "0")}`;
}

function normalizeThemeLabel(slug: PitchScreenSlug): string {
  if (slug === "01-double-engine") {
    return "HYBRID CORE";
  }

  if (slug === "02-industrial-flow") {
    return "INDUSTRIAL RHYTHM";
  }

  if (slug === "03-hitech-os") {
    return "DIGITAL CONTROL";
  }

  if (slug === "04-valuation") {
    return "INVESTOR CASE";
  }

  if (slug === "05-inventory-foundation") {
    return "PHARMA RUN 1";
  }

  return "PHARMA RUN 2";
}

function screenBase(screen: PitchScreen): PitchScreenBaseViewModel {
  return {
    slug: screen.slug,
    route: screen.route,
    order: screen.order,
    title: screen.title,
    kicker: normalizeKicker(screen.order),
    thematicLabel: normalizeThemeLabel(screen.slug),
    canonicalTags: [screen.slug, `screen-${screen.order.toString().padStart(2, "0")}`]
  };
}

export function buildScreen01ViewModel(screen: PitchScreen01 = PITCH_SCREEN_FIXTURES["01-double-engine"]): PitchScreen01ViewModel {
  const leftBullets = screen.leftColumn.bullets.map((entry) => entry.text);
  const rightBullets = screen.rightColumn.bullets.map((entry) => entry.text);

  return {
    ...screenBase(screen),
    left: {
      heading: screen.leftColumn.heading,
      bullets: leftBullets,
      microcopy: screen.leftColumn.microcopy.map((entry) => entry.text)
    },
    right: {
      heading: screen.rightColumn.heading,
      bullets: rightBullets,
      microcopy: screen.rightColumn.microcopy.map((entry) => entry.text)
    },
    implicitMessage: screen.implicitMessage.text,
    derived: {
      industrialCount: leftBullets.length,
      softwareCount: rightBullets.length,
      balancedIndex: Math.round((leftBullets.length / rightBullets.length) * 100),
      capabilityChips: [
        "Control de activos",
        "Calibración CRS",
        "Flujo recurrente",
        "Escala multiindustria",
        "Trazabilidad técnica"
      ]
    }
  };
}

function parseNumeric(value: string): number {
  const cleaned = value.replaceAll(/[^\d.]/g, "");
  const parsed = Number.parseFloat(cleaned);
  if (Number.isNaN(parsed)) {
    return 0;
  }

  return parsed;
}

export function buildScreen02ViewModel(screen: PitchScreen02 = PITCH_SCREEN_FIXTURES["02-industrial-flow"]): PitchScreen02ViewModel {
  const monthlyModulesLabel = screen.kpis.find((entry) => entry.label.includes("12 módulos"));
  const annualUtilityLabel = screen.kpis.find((entry) => entry.label.includes("utilidad anual"));

  const monthlyModules = monthlyModulesLabel ? parseNumeric(monthlyModulesLabel.value) : 12;
  const annualizedMillions = annualUtilityLabel ? parseNumeric(annualUtilityLabel.value) / 1000000 : 1.09;

  return {
    ...screenBase(screen),
    kpis: screen.kpis.map((entry) => ({
      label: entry.label,
      value: entry.value,
      note: entry.note ?? ""
    })),
    cycleLabel: screen.cycleLabel.text,
    microcopy: screen.microcopy.text,
    derived: {
      cycleMonths: 35,
      monthlyModules,
      annualizedUtilityMillions: Number.parseFloat(annualizedMillions.toFixed(2)),
      coverageChips: [
        "Mercado interno activo",
        "Cobertura 35 meses",
        "Mantenimiento obligatorio",
        "Flujo negociado",
        "Utilidad anualizable"
      ]
    }
  };
}

export function buildScreen03ViewModel(screen: PitchScreen03 = PITCH_SCREEN_FIXTURES["03-hitech-os"]): PitchScreen03ViewModel {
  const featureRows = screen.features.map((entry) => ({
    text: entry.text,
    category: entry.category
  }));

  const byCategory = featureRows.reduce<Record<string, number>>((acc, feature) => {
    acc[feature.category] = (acc[feature.category] ?? 0) + 1;
    return acc;
  }, {});

  return {
    ...screenBase(screen),
    features: featureRows,
    strongLine: screen.strongLine.text,
    derived: {
      byCategory,
      capabilityChips: [
        "Dashboard operativo",
        "Historial completo",
        "Alertas automáticas",
        "Visibilidad cliente",
        "Modo farmacéutico"
      ]
    }
  };
}

export function buildScreen04ViewModel(screen: PitchScreen04 = PITCH_SCREEN_FIXTURES["04-valuation"]): PitchScreen04ViewModel {
  return {
    ...screenBase(screen),
    blocks: screen.blocks.map((block) => ({
      heading: block.heading,
      items: block.items.map((entry) => entry.text),
      ...(block.phase1 ? { phase1: block.phase1 } : {}),
      ...(block.phase2 ? { phase2: block.phase2 } : {})
    })),
    combinedLine: screen.combinedValuationLine.text,
    comparison: {
      headers: screen.comparison.headers,
      rows: screen.comparison.rows
    },
    derived: {
      panelLabels: [
        "Tradicional",
        "Industrial + Software",
        "Estructura de inversión"
      ],
      riskScale: [58, 36],
      scalabilityScale: [42, 89]
    }
  };
}
