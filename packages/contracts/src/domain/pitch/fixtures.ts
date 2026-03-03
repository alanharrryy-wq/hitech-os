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
  type PitchScreen05,
  type PitchScreen06,
  PitchCopyDigestSchema,
  PitchDeckResponseSchema,
  PitchDeckSchema,
  PitchScreenMapSchema,
  PitchScreenSchema
} from "./schemas.js";

export const unitPricePerModule = 19000;
export const profitMargin = 0.4;
export const monthlyCadenceModules = 12;
export const wedgeModules = 6;
export const tractionInvoicedModules = 19;
export const targetModules = 420;

export const stage1CashUsd = 100000;
export const stage2CashUsd = 200000;
export const stage1ConversionBoost = 0.25;

export function calcRevenue(modules: number): number {
  return modules * unitPricePerModule;
}

export function calcProfit(revenue: number): number {
  return Math.round(revenue * profitMargin);
}

export function annualize(monthlyProfit: number): number {
  return monthlyProfit * 12;
}

function formatUsdWhole(value: number): string {
  return `$${value.toLocaleString("en-US")}`;
}

function formatUsdK(value: number): string {
  const thousands = value / 1000;
  const fixed = Number.isInteger(thousands) ? `${thousands}` : thousands.toFixed(1);
  return `$${fixed}k`;
}

function formatUsdM(value: number): string {
  return `~$${(value / 1000000).toFixed(2)}M`;
}

export const PITCH_VALUATION_ECONOMICS = {
  params: {
    unitPricePerModule,
    profitMargin,
    monthlyCadenceModules,
    wedgeModules,
    tractionInvoicedModules,
    targetModules
  },
  derived: {
    monthlyRevenue: calcRevenue(monthlyCadenceModules),
    monthlyProfit: calcProfit(calcRevenue(monthlyCadenceModules)),
    annualProfit: annualize(calcProfit(calcRevenue(monthlyCadenceModules))),
    wedgeRevenue: calcRevenue(wedgeModules),
    wedgeProfit: calcProfit(calcRevenue(wedgeModules))
  },
  deal: {
    stage1CashUsd,
    stage2CashUsd,
    totalCashUsd: stage1CashUsd + stage2CashUsd,
    stage1EffectiveUsd: Math.round(stage1CashUsd * (1 + stage1ConversionBoost)),
    totalEffectiveUsd: Math.round(stage1CashUsd * (1 + stage1ConversionBoost)) + stage2CashUsd,
    capRangeUsd: {
      low: 4000000,
      high: 6000000
    }
  }
} as const;

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
        text: `TARGET ${targetModules} módulos en SRG`,
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
      label: `TARGET ${targetModules} módulos`,
      value: `${targetModules}`,
      note: "Meta de cobertura"
    },
    {
      id: "screen02-kpi-02",
      label: `${monthlyCadenceModules} módulos mensuales`,
      value: `${monthlyCadenceModules}`,
      note: "Flujo pactado"
    },
    {
      id: "screen02-kpi-03",
      label: `${formatUsdK(PITCH_VALUATION_ECONOMICS.derived.monthlyRevenue)} facturación mensual`,
      value: formatUsdK(PITCH_VALUATION_ECONOMICS.derived.monthlyRevenue),
      note: "Ingreso mensual"
    },
    {
      id: "screen02-kpi-04",
      label: `${formatUsdK(PITCH_VALUATION_ECONOMICS.derived.monthlyProfit)} utilidad mensual`,
      value: formatUsdK(PITCH_VALUATION_ECONOMICS.derived.monthlyProfit),
      note: "Margen operativo"
    },
    {
      id: "screen02-kpi-05",
      label: `${formatUsdM(PITCH_VALUATION_ECONOMICS.derived.annualProfit)} utilidad anual`,
      value: formatUsdM(PITCH_VALUATION_ECONOMICS.derived.annualProfit),
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
          text: `Ingreso mensual @${monthlyCadenceModules}/mes: ${formatUsdWhole(PITCH_VALUATION_ECONOMICS.derived.monthlyRevenue)}`
        },
        {
          id: "screen04-b01-i02",
          text: `Utilidad mensual @${Math.round(profitMargin * 100)}%: ${formatUsdWhole(PITCH_VALUATION_ECONOMICS.derived.monthlyProfit)}`
        },
        {
          id: "screen04-b01-i03",
          text: `Utilidad anualizada: ${formatUsdWhole(PITCH_VALUATION_ECONOMICS.derived.annualProfit)}`
        },
        {
          id: "screen04-b01-i04",
          text: "Valuación base industrial: disciplina de flujo comprobada"
        }
      ]
    },
    {
      id: "screen04-block-02",
      heading: "Infraestructura Industrial + Software Propietario",
      items: [
        {
          id: "screen04-b02-i01",
          text: `Wedge ${wedgeModules} módulos (30 días): ${formatUsdWhole(PITCH_VALUATION_ECONOMICS.derived.wedgeRevenue)} ingreso`
        },
        {
          id: "screen04-b02-i02",
          text: `Utilidad wedge @${Math.round(profitMargin * 100)}%: ${formatUsdWhole(PITCH_VALUATION_ECONOMICS.derived.wedgeProfit)}`
        },
        {
          id: "screen04-b02-i03",
          text: `Tras entrega se habilita acuerdo de ${monthlyCadenceModules}/mes`
        },
        {
          id: "screen04-b02-i04",
          text: `TARGET ${targetModules} módulos (objetivo de despliegue)`
        },
        {
          id: "screen04-b02-i05",
          text: "Software + operación incrementan defendibilidad del múltiplo"
        }
      ]
    },
    {
      id: "screen04-block-03",
      heading: "Estructura de Inversión",
      items: [
        {
          id: "screen04-b03-i01",
          text: `Etapa 1: ${formatUsdK(stage1CashUsd)} hoy -> entregar ${wedgeModules} módulos (30 días)`
        },
        {
          id: "screen04-b03-i02",
          text: "Trigger Etapa 2: entrega + factura SRG (día 30)"
        },
        {
          id: "screen04-b03-i03",
          text: `Etapa 2: +${formatUsdK(stage2CashUsd)} -> ejecutar rampa ${monthlyCadenceModules} módulos/mes`
        },
        {
          id: "screen04-b03-i04",
          text: `Si Etapa 2: Tramo 1 convierte con +25% (${formatUsdK(stage1CashUsd)}->${formatUsdK(PITCH_VALUATION_ECONOMICS.deal.stage1EffectiveUsd)} efectivo)`
        },
        {
          id: "screen04-b03-i05",
          text: `Total cash: ${formatUsdK(PITCH_VALUATION_ECONOMICS.deal.totalCashUsd)} | Total efectivo equity: ${formatUsdK(PITCH_VALUATION_ECONOMICS.deal.totalEffectiveUsd)}`
        },
        {
          id: "screen04-b03-i06",
          text: "Instrumento: SAFE/Convertible con cap 4–6M (post-cierre 12/mes)"
        }
      ],
      phase1: `Etapa 1: ${formatUsdK(stage1CashUsd)} -> ejecución wedge y factura en D30`,
      phase2: `Etapa 2: +${formatUsdK(stage2CashUsd)} -> despliegue recurrente y opción equity`
    }
  ],
  combinedValuationLine: {
    id: "screen04-combined-valuation",
    text: "SAFE/Convertible con cap 4–6M anclado a escenario post-cierre 12/mes"
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

export const SCREEN_05_FIXTURE: PitchScreen05 = {
  slug: "05-inventory-foundation",
  route: PITCH_ROUTES["05-inventory-foundation"],
  order: 5,
  tag: "pitch.screen.05",
  title: "RUN 1 - INVENTORY FOUNDATION (RBAC + SUPPLIERS + SKU + DOCUMENT VAULT)",
  foundationStatus: {
    id: "screen05-foundation-status",
    heading: "Foundation status",
    kpis: [
      {
        id: "screen05-kpi-01",
        label: "RBAC profiles defined",
        value: "4",
        note: "Admin, Ops, QA, Finance"
      },
      {
        id: "screen05-kpi-02",
        label: "Suppliers pre-registered",
        value: "3",
        note: "Tier-1 baseline"
      },
      {
        id: "screen05-kpi-03",
        label: "SKU templates loaded",
        value: "24",
        note: "Initial import batch"
      },
      {
        id: "screen05-kpi-04",
        label: "Vault document sets",
        value: "5",
        note: "Mandatory compliance pack"
      }
    ],
    rbacMatrixSnapshot: {
      id: "screen05-rbac-matrix",
      heading: "RBAC matrix snapshot",
      rows: [
        {
          id: "screen05-rbac-row-01",
          role: "Warehouse Operator",
          permissions: ["receive.shipment", "scan.sku", "view.stock"],
          status: "DONE"
        },
        {
          id: "screen05-rbac-row-02",
          role: "Quality Inspector",
          permissions: ["inspect.lot", "set.quarantine", "release.qa"],
          status: "IN_PROGRESS"
        },
        {
          id: "screen05-rbac-row-03",
          role: "Procurement Lead",
          permissions: ["approve.supplier", "link.po", "view.documents"],
          status: "PENDING"
        }
      ]
    },
    supplierOnboardingStatus: {
      id: "screen05-supplier-onboarding",
      heading: "Supplier onboarding status",
      suppliers: [
        {
          id: "screen05-supplier-01",
          supplier: "SUP-MX-ALPHA",
          status: "DONE"
        },
        {
          id: "screen05-supplier-02",
          supplier: "SUP-US-BETA",
          status: "IN_PROGRESS"
        },
        {
          id: "screen05-supplier-03",
          supplier: "SUP-CN-GAMMA",
          status: "MISSING"
        }
      ]
    }
  },
  productsSkuBaseline: {
    id: "screen05-products-sku",
    heading: "Products & SKU baseline",
    fields: [
      {
        id: "screen05-sku-field-01",
        label: "SKU",
        value: "SKU-BASE-0001"
      },
      {
        id: "screen05-sku-field-02",
        label: "Barcode",
        value: "7501234500012"
      },
      {
        id: "screen05-sku-field-03",
        label: "Traceability Batch ID",
        value: "LOT-FOUND-001"
      },
      {
        id: "screen05-sku-field-04",
        label: "Traceability Serial ID",
        value: "SER-FOUND-0001"
      }
    ]
  },
  documentVaultBaseline: {
    id: "screen05-document-vault",
    heading: "Document vault baseline",
    requiredDocs: [
      {
        id: "screen05-doc-01",
        document: "Commercial Invoice",
        status: "DONE"
      },
      {
        id: "screen05-doc-02",
        document: "Packing List",
        status: "DONE"
      },
      {
        id: "screen05-doc-03",
        document: "Certificate of Origin",
        status: "IN_PROGRESS"
      },
      {
        id: "screen05-doc-04",
        document: "HS Classification Sheet",
        status: "PENDING"
      },
      {
        id: "screen05-doc-05",
        document: "Import Permit",
        status: "MISSING"
      }
    ]
  }
};

export const SCREEN_06_FIXTURE: PitchScreen06 = {
  slug: "06-shipments-receiving",
  route: PITCH_ROUTES["06-shipments-receiving"],
  order: 6,
  tag: "pitch.screen.06",
  title: "RUN 2 - IMPORT SHIPMENTS (CUSTOMS PACK + RECEIVING -> QUARANTINE)",
  shipmentControlBoard: {
    id: "screen06-shipment-control",
    heading: "Shipment control board",
    placeholders: [
      {
        id: "screen06-placeholder-awb",
        label: "AWB / BL",
        value: "AWB-BL-PENDING"
      },
      {
        id: "screen06-placeholder-eta",
        label: "ETA",
        value: "ETA-TBD"
      },
      {
        id: "screen06-placeholder-ata",
        label: "ATA",
        value: "ATA-TBD"
      },
      {
        id: "screen06-placeholder-incoterm",
        label: "Incoterm",
        value: "INCOTERM-TBD"
      },
      {
        id: "screen06-placeholder-port",
        label: "Receiving port",
        value: "PORT-TBD"
      }
    ],
    customsPackCompleteness: {
      id: "screen06-customs-pack",
      text: "Customs pack completeness",
      status: "IN_PROGRESS"
    }
  },
  receivingFlow: {
    id: "screen06-receiving-flow",
    heading: "Receiving flow",
    states: [
      {
        id: "screen06-flow-01",
        code: "ARRIVED",
        note: "Shipment arrived to bonded warehouse",
        order: 1
      },
      {
        id: "screen06-flow-02",
        code: "DOCS_HOLD",
        note: "Customs documents under verification",
        order: 2
      },
      {
        id: "screen06-flow-03",
        code: "RECEIVED",
        note: "Physical count and lot scan completed",
        order: 3
      },
      {
        id: "screen06-flow-04",
        code: "QUARANTINE",
        note: "Inventory isolated pending QA decision",
        order: 4
      }
    ]
  },
  mismatchHandling: {
    id: "screen06-mismatch",
    heading: "Mismatch handling",
    qtyLotMismatch: "Qty/lot mismatch triggers deviation record placeholder.",
    deviationPlaceholder: "Deviation ticket: DEV-TBD"
  },
  nextGate: {
    id: "screen06-next-gate",
    text: "Next gate: QA RELEASE (RUN3, not implemented)"
  }
};

export const PITCH_SCREEN_FIXTURES = {
  "01-double-engine": SCREEN_01_FIXTURE,
  "02-industrial-flow": SCREEN_02_FIXTURE,
  "03-hitech-os": SCREEN_03_FIXTURE,
  "04-valuation": SCREEN_04_FIXTURE,
  "05-inventory-foundation": SCREEN_05_FIXTURE,
  "06-shipments-receiving": SCREEN_06_FIXTURE
} as const;

export const PITCH_SCREENS_FIXTURE: readonly PitchScreen[] = [
  PITCH_SCREEN_FIXTURES["01-double-engine"],
  PITCH_SCREEN_FIXTURES["02-industrial-flow"],
  PITCH_SCREEN_FIXTURES["03-hitech-os"],
  PITCH_SCREEN_FIXTURES["04-valuation"],
  PITCH_SCREEN_FIXTURES["05-inventory-foundation"],
  PITCH_SCREEN_FIXTURES["06-shipments-receiving"]
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
      },
      {
        slug: "05-inventory-foundation",
        href: PITCH_ROUTES["05-inventory-foundation"],
        title: PITCH_SCREEN_TITLES["05-inventory-foundation"],
        order: 5
      },
      {
        slug: "06-shipments-receiving",
        href: PITCH_ROUTES["06-shipments-receiving"],
        title: PITCH_SCREEN_TITLES["06-shipments-receiving"],
        order: 6
      }
    ]
  },
  screens: [
    PITCH_SCREEN_FIXTURES["01-double-engine"],
    PITCH_SCREEN_FIXTURES["02-industrial-flow"],
    PITCH_SCREEN_FIXTURES["03-hitech-os"],
    PITCH_SCREEN_FIXTURES["04-valuation"],
    PITCH_SCREEN_FIXTURES["05-inventory-foundation"],
    PITCH_SCREEN_FIXTURES["06-shipments-receiving"]
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

    if (screen.slug === "04-valuation") {
      return (
        total + screen.blocks.reduce((innerTotal, block) => innerTotal + block.items.length, 0)
      );
    }

    if (screen.slug === "05-inventory-foundation") {
      return (
        total +
        screen.foundationStatus.kpis.length +
        screen.foundationStatus.rbacMatrixSnapshot.rows.length +
        screen.foundationStatus.supplierOnboardingStatus.suppliers.length +
        screen.documentVaultBaseline.requiredDocs.length
      );
    }

    return total + screen.receivingFlow.states.length + 2;
  }, 0);

  const headingCount = deck.screens.reduce((total, screen) => {
    if (screen.slug === "01-double-engine") {
      return total + 3;
    }

    if (screen.slug === "04-valuation") {
      return total + 4;
    }

    if (screen.slug === "05-inventory-foundation") {
      return total + 6;
    }

    if (screen.slug === "06-shipments-receiving") {
      return total + 4;
    }

    return total + 1;
  }, 0);

  return {
    deckId: deck.meta.deckId,
    screenCount: 6,
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
  "04-valuation": PITCH_SCREEN_FIXTURES["04-valuation"],
  "05-inventory-foundation": PITCH_SCREEN_FIXTURES["05-inventory-foundation"],
  "06-shipments-receiving": PITCH_SCREEN_FIXTURES["06-shipments-receiving"]
} as const;

export const PITCH_SCREEN_ROUTE_INDEX = {
  [PITCH_ROUTES["01-double-engine"]]: PITCH_SCREEN_FIXTURES["01-double-engine"],
  [PITCH_ROUTES["02-industrial-flow"]]: PITCH_SCREEN_FIXTURES["02-industrial-flow"],
  [PITCH_ROUTES["03-hitech-os"]]: PITCH_SCREEN_FIXTURES["03-hitech-os"],
  [PITCH_ROUTES["04-valuation"]]: PITCH_SCREEN_FIXTURES["04-valuation"],
  [PITCH_ROUTES["05-inventory-foundation"]]: PITCH_SCREEN_FIXTURES["05-inventory-foundation"],
  [PITCH_ROUTES["06-shipments-receiving"]]: PITCH_SCREEN_FIXTURES["06-shipments-receiving"]
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
PitchScreenSchema.parse(SCREEN_05_FIXTURE);
PitchScreenSchema.parse(SCREEN_06_FIXTURE);
PitchDeckSchema.parse(PITCH_DECK_FIXTURE);
PitchScreenMapSchema.parse(PITCH_SCREEN_MAP_FIXTURE);
PitchCopyDigestSchema.parse(PITCH_COPY_DIGEST_FIXTURE);
PitchDeckResponseSchema.parse(PITCH_DECK_RESPONSE_FIXTURE);
