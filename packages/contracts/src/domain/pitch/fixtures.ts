import {
  PITCH_COMPARISON_ROWS,
  PITCH_COPY_LOCK_NOTICE,
  PITCH_DECK_ID,
  PITCH_DECK_VERSION,
  PITCH_LAYER_PROFILE_HINTS,
  PITCH_LOCALE,
  PITCH_ROUTES,
  PITCH_SCREEN_ORDER,
  PITCH_SCREEN_TITLES,
  PITCH_TABLE_HEADERS
} from "./constants.js";
import {
  type PitchCopyDigest,
  type PitchDeck,
  type PitchDeckResponse,
  type PitchScreen,
  type PitchScreen01,
  type PitchScreen02,
  type PitchScreen03,
  type PitchScreen04,
  PitchCopyDigestSchema,
  PitchDeckResponseSchema,
  PitchDeckSchema,
  PitchScreenMapSchema,
  PitchScreenSchema
} from "./schemas.js";

const SCREEN_01_FIXTURE: PitchScreen01 = {
  slug: "01-double-engine",
  route: PITCH_ROUTES["01-double-engine"],
  order: 1,
  tag: "pitch.screen.01",
  title: "HITECH — ARQUITECTURA DE DOBLE MOTOR",
  leftColumn: {
    id: "screen01-engine-left",
    heading: "MOTOR 1 — INFRAESTRUCTURA INDUSTRIAL",
    bullets: [
      {
        id: "screen01-left-b01",
        text: "19 módulos facturados",
        emphasis: "positive",
        weight: "anchor"
      },
      {
        id: "screen01-left-b02",
        text: "6 módulos listos (requieren 100k)",
        emphasis: "positive",
        weight: "core"
      },
      {
        id: "screen01-left-b03",
        text: "12 módulos mensuales negociados",
        emphasis: "positive",
        weight: "core"
      },
      {
        id: "screen01-left-b04",
        text: "420 módulos instalados en SRG",
        emphasis: "positive",
        weight: "anchor"
      },
      {
        id: "screen01-left-b05",
        text: "Ciclo recurrente obligatorio de mantenimiento",
        emphasis: "critical",
        weight: "core"
      }
    ],
    microcopy: [
      {
        id: "screen01-left-m01",
        text: "Infraestructura eléctrica crítica certificada CRS + REMMt1."
      }
    ]
  },
  rightColumn: {
    id: "screen01-engine-right",
    heading: "MOTOR 2 — HITECH OS",
    bullets: [
      {
        id: "screen01-right-b01",
        text: "Plataforma digital propietaria",
        emphasis: "positive",
        weight: "anchor"
      },
      {
        id: "screen01-right-b02",
        text: "Estandarización nivel automotriz",
        emphasis: "neutral",
        weight: "core"
      },
      {
        id: "screen01-right-b03",
        text: "Trazabilidad técnica completa",
        emphasis: "neutral",
        weight: "core"
      },
      {
        id: "screen01-right-b04",
        text: "Registro calibración CRS",
        emphasis: "neutral",
        weight: "core"
      },
      {
        id: "screen01-right-b05",
        text: "Multiusuario / multirol",
        emphasis: "neutral",
        weight: "support"
      },
      {
        id: "screen01-right-b06",
        text: "Escalable a multiindustria",
        emphasis: "positive",
        weight: "core"
      }
    ],
    microcopy: [
      {
        id: "screen01-right-m01",
        text: "Nacido por necesidad operativa real."
      }
    ]
  },
  implicitMessage: {
    id: "screen01-implicit-message",
    text: "No soy proveedor. Soy sistema."
  }
};

const SCREEN_02_FIXTURE: PitchScreen02 = {
  slug: "02-industrial-flow",
  route: PITCH_ROUTES["02-industrial-flow"],
  order: 2,
  tag: "pitch.screen.02",
  title: "MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE",
  kpis: [
    {
      id: "screen02-kpi-01",
      label: "420 módulos totales",
      value: "420",
      note: "Base instalada"
    },
    {
      id: "screen02-kpi-02",
      label: "12 módulos mensuales",
      value: "12",
      note: "Flujo pactado"
    },
    {
      id: "screen02-kpi-03",
      label: "$228k facturación mensual",
      value: "$228k",
      note: "Ingreso mensual"
    },
    {
      id: "screen02-kpi-04",
      label: "$91k utilidad mensual",
      value: "$91k",
      note: "Margen operativo"
    },
    {
      id: "screen02-kpi-05",
      label: "~$1.09M utilidad anual",
      value: "~$1.09M",
      note: "Anualización"
    }
  ],
  cycleLabel: {
    id: "screen02-cycle-label",
    text: "Ciclo continuo 35 meses para cubrir total → reinicio automático."
  },
  microcopy: {
    id: "screen02-microcopy",
    text: "Mercado interno ya existente, no especulativo."
  }
};

const SCREEN_03_FIXTURE: PitchScreen03 = {
  slug: "03-hitech-os",
  route: PITCH_ROUTES["03-hitech-os"],
  order: 3,
  tag: "pitch.screen.03",
  title: "MOTOR 2 — HITECH OS (Infraestructura Digital)",
  features: [
    {
      id: "screen03-feature-01",
      text: "Dashboard operativo",
      category: "operation"
    },
    {
      id: "screen03-feature-02",
      text: "Control activo por módulo",
      category: "operation"
    },
    {
      id: "screen03-feature-03",
      text: "Historial técnico completo",
      category: "traceability"
    },
    {
      id: "screen03-feature-04",
      text: "Calibración certificada CRS",
      category: "quality"
    },
    {
      id: "screen03-feature-05",
      text: "Alertas preventivas automáticas",
      category: "operation"
    },
    {
      id: "screen03-feature-06",
      text: "Panel cliente transparente",
      category: "visibility"
    },
    {
      id: "screen03-feature-07",
      text: "Modo Industria Farmacéutica",
      category: "vertical"
    }
  ],
  strongLine: {
    id: "screen03-strong-line",
    text: "Infraestructura digital propietaria diseñada para control de activos críticos."
  }
};

const SCREEN_04_FIXTURE: PitchScreen04 = {
  slug: "04-valuation",
  route: PITCH_ROUTES["04-valuation"],
  order: 4,
  tag: "pitch.screen.04",
  title: "ESTRUCTURA FINANCIERA + VALUACIÓN",
  blocks: [
    {
      id: "screen04-block-01",
      heading: "Unidad Industrial Tradicional",
      items: [
        {
          id: "screen04-b01-i01",
          text: "Genera flujo"
        },
        {
          id: "screen04-b01-i02",
          text: "Margen 40%"
        },
        {
          id: "screen04-b01-i03",
          text: "Valuación típica 2–3x utilidad"
        },
        {
          id: "screen04-b01-i04",
          text: "Valuación estimada: 2.5–3M"
        }
      ]
    },
    {
      id: "screen04-block-02",
      heading: "Infraestructura Industrial + Software Propietario",
      items: [
        {
          id: "screen04-b02-i01",
          text: "Flujo recurrente"
        },
        {
          id: "screen04-b02-i02",
          text: "Propiedad intelectual"
        },
        {
          id: "screen04-b02-i03",
          text: "Escalabilidad SaaS"
        },
        {
          id: "screen04-b02-i04",
          text: "Barrera técnica alta"
        },
        {
          id: "screen04-b02-i05",
          text: "Múltiplo superior"
        }
      ]
    },
    {
      id: "screen04-block-03",
      heading: "Estructura de Inversión",
      items: [],
      phase1: "$100k → 25% rendimiento → sin dilución",
      phase2: "$200k → 3–5% equity (según valuación final acordada)"
    }
  ],
  combinedValuationLine: {
    id: "screen04-combined-valuation",
    text: "Valuación combinada estimada: 4–6M"
  },
  comparison: {
    headers: [
      PITCH_TABLE_HEADERS[0],
      PITCH_TABLE_HEADERS[1],
      PITCH_TABLE_HEADERS[2],
      PITCH_TABLE_HEADERS[3]
    ],
    rows: [
      [
        PITCH_COMPARISON_ROWS[0][0],
        PITCH_COMPARISON_ROWS[0][1],
        PITCH_COMPARISON_ROWS[0][2],
        PITCH_COMPARISON_ROWS[0][3]
      ],
      [
        PITCH_COMPARISON_ROWS[1][0],
        PITCH_COMPARISON_ROWS[1][1],
        PITCH_COMPARISON_ROWS[1][2],
        PITCH_COMPARISON_ROWS[1][3]
      ]
    ]
  }
};

export const PITCH_SCREEN_FIXTURES = {
  "01-double-engine": SCREEN_01_FIXTURE,
  "02-industrial-flow": SCREEN_02_FIXTURE,
  "03-hitech-os": SCREEN_03_FIXTURE,
  "04-valuation": SCREEN_04_FIXTURE
} as const;

export const PITCH_SCREENS_FIXTURE: readonly PitchScreen[] = [
  PITCH_SCREEN_FIXTURES["01-double-engine"],
  PITCH_SCREEN_FIXTURES["02-industrial-flow"],
  PITCH_SCREEN_FIXTURES["03-hitech-os"],
  PITCH_SCREEN_FIXTURES["04-valuation"]
];

export const PITCH_DECK_FIXTURE: PitchDeck = {
  meta: {
    deckId: PITCH_DECK_ID,
    version: PITCH_DECK_VERSION,
    locale: PITCH_LOCALE,
    copyLockNotice: PITCH_COPY_LOCK_NOTICE,
    profileHints: [
      PITCH_LAYER_PROFILE_HINTS[0],
      PITCH_LAYER_PROFILE_HINTS[1],
      PITCH_LAYER_PROFILE_HINTS[2]
    ]
  },
  navigation: {
    base: "/pitch",
    links: [
      {
        slug: "01-double-engine",
        href: PITCH_ROUTES["01-double-engine"],
        title: PITCH_SCREEN_TITLES["01-double-engine"],
        order: 1
      },
      {
        slug: "02-industrial-flow",
        href: PITCH_ROUTES["02-industrial-flow"],
        title: PITCH_SCREEN_TITLES["02-industrial-flow"],
        order: 2
      },
      {
        slug: "03-hitech-os",
        href: PITCH_ROUTES["03-hitech-os"],
        title: PITCH_SCREEN_TITLES["03-hitech-os"],
        order: 3
      },
      {
        slug: "04-valuation",
        href: PITCH_ROUTES["04-valuation"],
        title: PITCH_SCREEN_TITLES["04-valuation"],
        order: 4
      }
    ]
  },
  screens: [
    PITCH_SCREEN_FIXTURES["01-double-engine"],
    PITCH_SCREEN_FIXTURES["02-industrial-flow"],
    PITCH_SCREEN_FIXTURES["03-hitech-os"],
    PITCH_SCREEN_FIXTURES["04-valuation"]
  ]
};

function createPitchCopyDigest(deck: PitchDeck): PitchCopyDigest {
  const bulletCount = deck.screens.reduce((total, screen) => {
    if (screen.slug === "01-double-engine") {
      return total + screen.leftColumn.bullets.length + screen.rightColumn.bullets.length;
    }

    if (screen.slug === "02-industrial-flow") {
      return total + screen.kpis.length;
    }

    if (screen.slug === "03-hitech-os") {
      return total + screen.features.length;
    }

    return total + screen.blocks.reduce((innerTotal, block) => innerTotal + block.items.length, 0);
  }, 0);

  const headingCount = deck.screens.reduce((total, screen) => {
    if (screen.slug === "01-double-engine") {
      return total + 3;
    }

    if (screen.slug === "04-valuation") {
      return total + 4;
    }

    return total + 1;
  }, 0);

  return {
    deckId: deck.meta.deckId,
    screenCount: 4,
    bulletCount,
    headingCount,
    tableRowCount: 2,
    tableHeaderCount: 4
  };
}

export const PITCH_COPY_DIGEST_FIXTURE: PitchCopyDigest = createPitchCopyDigest(PITCH_DECK_FIXTURE);

export const PITCH_DECK_RESPONSE_FIXTURE: PitchDeckResponse = {
  deck: PITCH_DECK_FIXTURE,
  digest: PITCH_COPY_DIGEST_FIXTURE
};

export const PITCH_SCREEN_MAP_FIXTURE = {
  "01-double-engine": PITCH_SCREEN_FIXTURES["01-double-engine"],
  "02-industrial-flow": PITCH_SCREEN_FIXTURES["02-industrial-flow"],
  "03-hitech-os": PITCH_SCREEN_FIXTURES["03-hitech-os"],
  "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"]
} as const;

export const PITCH_SCREEN_ROUTE_INDEX = {
  [PITCH_ROUTES["01-double-engine"]]: PITCH_SCREEN_FIXTURES["01-double-engine"],
  [PITCH_ROUTES["02-industrial-flow"]]: PITCH_SCREEN_FIXTURES["02-industrial-flow"],
  [PITCH_ROUTES["03-hitech-os"]]: PITCH_SCREEN_FIXTURES["03-hitech-os"],
  [PITCH_ROUTES["04-valuation"]]: PITCH_SCREEN_FIXTURES["04-valuation"]
} as const;

export const PITCH_DECK_FIXTURE_LOCK = {
  screenOrder: [...PITCH_SCREEN_ORDER],
  titles: {
    ...PITCH_SCREEN_TITLES
  },
  routes: {
    ...PITCH_ROUTES
  }
} as const;

PitchScreenSchema.parse(SCREEN_01_FIXTURE);
PitchScreenSchema.parse(SCREEN_02_FIXTURE);
PitchScreenSchema.parse(SCREEN_03_FIXTURE);
PitchScreenSchema.parse(SCREEN_04_FIXTURE);
PitchDeckSchema.parse(PITCH_DECK_FIXTURE);
PitchScreenMapSchema.parse(PITCH_SCREEN_MAP_FIXTURE);
PitchCopyDigestSchema.parse(PITCH_COPY_DIGEST_FIXTURE);
PitchDeckResponseSchema.parse(PITCH_DECK_RESPONSE_FIXTURE);
