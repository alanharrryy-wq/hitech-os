import type {
  CustomsDocumentRequirement,
  PortRiskProfile,
  ReceivingIncoterm,
  ShipmentControlBoardFields,
  ShipmentManifestProfile
} from "./types";

export const RECEIVING_DEFAULT_FIELDS: ShipmentControlBoardFields = {
  awbBl: "AWB-BL-PENDING",
  eta: "2026-03-04T11:30:00Z",
  ata: "",
  incoterm: "DAP",
  carrier: "Polar Bridge Logistics",
  port: "MXMEX",
  quantityDeclared: 1200,
  quantityReceived: 1200,
  lotDeclared: "LOT-R2-0001",
  lotReceived: "LOT-R2-0001",
  temperatureExcursion: false
};

export const RECEIVING_INCOTERM_RISK: Readonly<Record<ReceivingIncoterm, number>> = {
  EXW: 24,
  FCA: 18,
  CPT: 14,
  CIP: 12,
  DAP: 9,
  DDP: 7
};

export const CUSTOMS_PACK_BASELINE: readonly CustomsDocumentRequirement[] = [
  {
    id: "doc-commercial-invoice",
    label: "Commercial Invoice",
    critical: true,
    owner: "finance",
    status: "present",
    expiryDate: "2026-12-02",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-packing-list",
    label: "Packing List",
    critical: true,
    owner: "logistics",
    status: "present",
    expiryDate: "2026-12-02",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-import-permit",
    label: "Import Permit",
    critical: true,
    owner: "qa",
    status: "missing",
    expiryDate: "2026-07-05",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-coa",
    label: "Certificate of Analysis",
    critical: true,
    owner: "qa",
    status: "present",
    expiryDate: "2026-11-10",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-temperature-report",
    label: "Temperature Report",
    critical: true,
    owner: "qa",
    status: "in-progress",
    expiryDate: "2026-10-18",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-hs-classification",
    label: "HS Classification Sheet",
    critical: true,
    owner: "broker",
    status: "present",
    expiryDate: "2026-08-13",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-certificate-origin",
    label: "Certificate of Origin",
    critical: true,
    owner: "broker",
    status: "present",
    expiryDate: "2026-09-01",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-bill-lading",
    label: "Bill of Lading",
    critical: false,
    owner: "logistics",
    status: "present",
    expiryDate: "2026-06-26",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-air-waybill",
    label: "Air Waybill",
    critical: false,
    owner: "logistics",
    status: "present",
    expiryDate: "2026-06-26",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-insurance-certificate",
    label: "Insurance Certificate",
    critical: false,
    owner: "finance",
    status: "present",
    expiryDate: "2026-05-24",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-dangerous-goods",
    label: "Dangerous Goods Declaration",
    critical: false,
    owner: "broker",
    status: "in-progress",
    expiryDate: "2026-09-21",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  },
  {
    id: "doc-customs-broker-auth",
    label: "Customs Broker Authorization",
    critical: true,
    owner: "broker",
    status: "present",
    expiryDate: "2026-11-29",
    guidance: [
      "Validate against broker packet and import declaration.",
      "Confirm link to shipment lot and quantity references.",
      "Escalate to customs lead if unresolved after 2 hours."
    ]
  }
];

export const PORT_RISK_PROFILES: readonly PortRiskProfile[] = [
  {
    port: "MXMEX",
    country: "Mexico",
    customsCongestion: 23,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Primary bonded lane with high refrigeration reliability."
  },
  {
    port: "MXVER",
    country: "Mexico",
    customsCongestion: 37,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Seasonal congestion around customs shift changes."
  },
  {
    port: "USLAX",
    country: "United States",
    customsCongestion: 41,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "High throughput with predictable dwell windows."
  },
  {
    port: "USIAH",
    country: "United States",
    customsCongestion: 26,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Strong pharma corridor and broker automation."
  },
  {
    port: "DEHAM",
    country: "Germany",
    customsCongestion: 29,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Stable lane with calibrated reefer monitoring."
  },
  {
    port: "INBOM",
    country: "India",
    customsCongestion: 44,
    coldChainReliability: 72,
    strikeAlert: true,
    note: "Strike advisory impacts weekend clearance windows."
  },
  {
    port: "BRSSZ",
    country: "Brazil",
    customsCongestion: 52,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Customs variability requires full pre-arrival docs."
  },
  {
    port: "IEORK",
    country: "Ireland",
    customsCongestion: 19,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Low congestion GDP-certified route."
  },
  {
    port: "KRPUS",
    country: "South Korea",
    customsCongestion: 27,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Strong cold chain handoff performance."
  },
  {
    port: "SGSIN",
    country: "Singapore",
    customsCongestion: 18,
    coldChainReliability: 96,
    strikeAlert: false,
    note: "Best-in-class pharma corridor with tight dwell times."
  },
  {
    port: "MXME11",
    country: "Mexico",
    customsCongestion: 34,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "MXVE12",
    country: "Mexico",
    customsCongestion: 49,
    coldChainReliability: 78,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "USLA13",
    country: "United States",
    customsCongestion: 54,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "USIA14",
    country: "United States",
    customsCongestion: 26,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "DEHA15",
    country: "Germany",
    customsCongestion: 30,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "INBO16",
    country: "India",
    customsCongestion: 46,
    coldChainReliability: 65,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "BRSS17",
    country: "Brazil",
    customsCongestion: 55,
    coldChainReliability: 67,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "IEOR18",
    country: "Ireland",
    customsCongestion: 23,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "KRPU19",
    country: "South Korea",
    customsCongestion: 32,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "SGSI20",
    country: "Singapore",
    customsCongestion: 24,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "MXME21",
    country: "Mexico",
    customsCongestion: 30,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "MXVE22",
    country: "Mexico",
    customsCongestion: 45,
    coldChainReliability: 77,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "USLA23",
    country: "United States",
    customsCongestion: 50,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "USIA24",
    country: "United States",
    customsCongestion: 36,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "DEHA25",
    country: "Germany",
    customsCongestion: 40,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "INBO26",
    country: "India",
    customsCongestion: 56,
    coldChainReliability: 64,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "BRSS27",
    country: "Brazil",
    customsCongestion: 65,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "IEOR28",
    country: "Ireland",
    customsCongestion: 19,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "KRPU29",
    country: "South Korea",
    customsCongestion: 28,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "SGSI30",
    country: "Singapore",
    customsCongestion: 20,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "MXME31",
    country: "Mexico",
    customsCongestion: 26,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "MXVE32",
    country: "Mexico",
    customsCongestion: 41,
    coldChainReliability: 76,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "USLA33",
    country: "United States",
    customsCongestion: 46,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "USIA34",
    country: "United States",
    customsCongestion: 32,
    coldChainReliability: 81,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "DEHA35",
    country: "Germany",
    customsCongestion: 36,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "INBO36",
    country: "India",
    customsCongestion: 52,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "BRSS37",
    country: "Brazil",
    customsCongestion: 61,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "IEOR38",
    country: "Ireland",
    customsCongestion: 29,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "KRPU39",
    country: "South Korea",
    customsCongestion: 38,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "SGSI40",
    country: "Singapore",
    customsCongestion: 30,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "MXME41",
    country: "Mexico",
    customsCongestion: 36,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "MXVE42",
    country: "Mexico",
    customsCongestion: 37,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "USLA43",
    country: "United States",
    customsCongestion: 42,
    coldChainReliability: 79,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "USIA44",
    country: "United States",
    customsCongestion: 28,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "DEHA45",
    country: "Germany",
    customsCongestion: 32,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "INBO46",
    country: "India",
    customsCongestion: 48,
    coldChainReliability: 71,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "BRSS47",
    country: "Brazil",
    customsCongestion: 57,
    coldChainReliability: 73,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "IEOR48",
    country: "Ireland",
    customsCongestion: 25,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "KRPU49",
    country: "South Korea",
    customsCongestion: 34,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "SGSI50",
    country: "Singapore",
    customsCongestion: 26,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "MXME51",
    country: "Mexico",
    customsCongestion: 32,
    coldChainReliability: 86,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "MXVE52",
    country: "Mexico",
    customsCongestion: 47,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "USLA53",
    country: "United States",
    customsCongestion: 52,
    coldChainReliability: 78,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "USIA54",
    country: "United States",
    customsCongestion: 38,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "DEHA55",
    country: "Germany",
    customsCongestion: 42,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "INBO56",
    country: "India",
    customsCongestion: 44,
    coldChainReliability: 70,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "BRSS57",
    country: "Brazil",
    customsCongestion: 53,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "IEOR58",
    country: "Ireland",
    customsCongestion: 21,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "KRPU59",
    country: "South Korea",
    customsCongestion: 30,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "SGSI60",
    country: "Singapore",
    customsCongestion: 22,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "MXME61",
    country: "Mexico",
    customsCongestion: 28,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "MXVE62",
    country: "Mexico",
    customsCongestion: 43,
    coldChainReliability: 73,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "USLA63",
    country: "United States",
    customsCongestion: 48,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "USIA64",
    country: "United States",
    customsCongestion: 34,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "DEHA65",
    country: "Germany",
    customsCongestion: 38,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "INBO66",
    country: "India",
    customsCongestion: 54,
    coldChainReliability: 69,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "BRSS67",
    country: "Brazil",
    customsCongestion: 63,
    coldChainReliability: 71,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "IEOR68",
    country: "Ireland",
    customsCongestion: 31,
    coldChainReliability: 89,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "KRPU69",
    country: "South Korea",
    customsCongestion: 40,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "SGSI70",
    country: "Singapore",
    customsCongestion: 18,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "MXME71",
    country: "Mexico",
    customsCongestion: 24,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "MXVE72",
    country: "Mexico",
    customsCongestion: 39,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "USLA73",
    country: "United States",
    customsCongestion: 44,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "USIA74",
    country: "United States",
    customsCongestion: 30,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "DEHA75",
    country: "Germany",
    customsCongestion: 34,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "INBO76",
    country: "India",
    customsCongestion: 50,
    coldChainReliability: 68,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "BRSS77",
    country: "Brazil",
    customsCongestion: 59,
    coldChainReliability: 70,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "IEOR78",
    country: "Ireland",
    customsCongestion: 27,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "KRPU79",
    country: "South Korea",
    customsCongestion: 36,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "SGSI80",
    country: "Singapore",
    customsCongestion: 28,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "MXME81",
    country: "Mexico",
    customsCongestion: 34,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "MXVE82",
    country: "Mexico",
    customsCongestion: 49,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "USLA83",
    country: "United States",
    customsCongestion: 54,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "USIA84",
    country: "United States",
    customsCongestion: 26,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "DEHA85",
    country: "Germany",
    customsCongestion: 30,
    coldChainReliability: 86,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "INBO86",
    country: "India",
    customsCongestion: 46,
    coldChainReliability: 67,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "BRSS87",
    country: "Brazil",
    customsCongestion: 55,
    coldChainReliability: 69,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "IEOR88",
    country: "Ireland",
    customsCongestion: 23,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "KRPU89",
    country: "South Korea",
    customsCongestion: 32,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "SGSI90",
    country: "Singapore",
    customsCongestion: 24,
    coldChainReliability: 96,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "MXME91",
    country: "Mexico",
    customsCongestion: 30,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "MXVE92",
    country: "Mexico",
    customsCongestion: 45,
    coldChainReliability: 79,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "USLA93",
    country: "United States",
    customsCongestion: 50,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "USIA94",
    country: "United States",
    customsCongestion: 36,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "DEHA95",
    country: "Germany",
    customsCongestion: 40,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "INBO96",
    country: "India",
    customsCongestion: 56,
    coldChainReliability: 66,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "BRSS97",
    country: "Brazil",
    customsCongestion: 65,
    coldChainReliability: 68,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "IEOR98",
    country: "Ireland",
    customsCongestion: 19,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "KRPU99",
    country: "South Korea",
    customsCongestion: 28,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "SGSI100",
    country: "Singapore",
    customsCongestion: 20,
    coldChainReliability: 95,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "MXME101",
    country: "Mexico",
    customsCongestion: 26,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "MXVE102",
    country: "Mexico",
    customsCongestion: 41,
    coldChainReliability: 78,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "USLA103",
    country: "United States",
    customsCongestion: 46,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "USIA104",
    country: "United States",
    customsCongestion: 32,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "DEHA105",
    country: "Germany",
    customsCongestion: 36,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "INBO106",
    country: "India",
    customsCongestion: 52,
    coldChainReliability: 65,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "BRSS107",
    country: "Brazil",
    customsCongestion: 61,
    coldChainReliability: 67,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "IEOR108",
    country: "Ireland",
    customsCongestion: 29,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "KRPU109",
    country: "South Korea",
    customsCongestion: 38,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "SGSI110",
    country: "Singapore",
    customsCongestion: 30,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "MXME111",
    country: "Mexico",
    customsCongestion: 36,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "MXVE112",
    country: "Mexico",
    customsCongestion: 37,
    coldChainReliability: 77,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "USLA113",
    country: "United States",
    customsCongestion: 42,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "USIA114",
    country: "United States",
    customsCongestion: 28,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "DEHA115",
    country: "Germany",
    customsCongestion: 32,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "INBO116",
    country: "India",
    customsCongestion: 48,
    coldChainReliability: 64,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "BRSS117",
    country: "Brazil",
    customsCongestion: 57,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "IEOR118",
    country: "Ireland",
    customsCongestion: 25,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "KRPU119",
    country: "South Korea",
    customsCongestion: 34,
    coldChainReliability: 87,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "SGSI120",
    country: "Singapore",
    customsCongestion: 26,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "MXME121",
    country: "Mexico",
    customsCongestion: 32,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "MXVE122",
    country: "Mexico",
    customsCongestion: 47,
    coldChainReliability: 76,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "USLA123",
    country: "United States",
    customsCongestion: 52,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "USIA124",
    country: "United States",
    customsCongestion: 38,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "DEHA125",
    country: "Germany",
    customsCongestion: 42,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "INBO126",
    country: "India",
    customsCongestion: 44,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "BRSS127",
    country: "Brazil",
    customsCongestion: 53,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "IEOR128",
    country: "Ireland",
    customsCongestion: 21,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "KRPU129",
    country: "South Korea",
    customsCongestion: 30,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "SGSI130",
    country: "Singapore",
    customsCongestion: 22,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "MXME131",
    country: "Mexico",
    customsCongestion: 28,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "MXVE132",
    country: "Mexico",
    customsCongestion: 43,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "USLA133",
    country: "United States",
    customsCongestion: 48,
    coldChainReliability: 79,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "USIA134",
    country: "United States",
    customsCongestion: 34,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "DEHA135",
    country: "Germany",
    customsCongestion: 38,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "INBO136",
    country: "India",
    customsCongestion: 54,
    coldChainReliability: 71,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "BRSS137",
    country: "Brazil",
    customsCongestion: 63,
    coldChainReliability: 73,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "IEOR138",
    country: "Ireland",
    customsCongestion: 31,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "KRPU139",
    country: "South Korea",
    customsCongestion: 40,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "SGSI140",
    country: "Singapore",
    customsCongestion: 18,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "MXME141",
    country: "Mexico",
    customsCongestion: 24,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "MXVE142",
    country: "Mexico",
    customsCongestion: 39,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "USLA143",
    country: "United States",
    customsCongestion: 44,
    coldChainReliability: 78,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "USIA144",
    country: "United States",
    customsCongestion: 30,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "DEHA145",
    country: "Germany",
    customsCongestion: 34,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "INBO146",
    country: "India",
    customsCongestion: 50,
    coldChainReliability: 70,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "BRSS147",
    country: "Brazil",
    customsCongestion: 59,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "IEOR148",
    country: "Ireland",
    customsCongestion: 27,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "KRPU149",
    country: "South Korea",
    customsCongestion: 36,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "SGSI150",
    country: "Singapore",
    customsCongestion: 28,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "MXME151",
    country: "Mexico",
    customsCongestion: 34,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "MXVE152",
    country: "Mexico",
    customsCongestion: 49,
    coldChainReliability: 73,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "USLA153",
    country: "United States",
    customsCongestion: 54,
    coldChainReliability: 86,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "USIA154",
    country: "United States",
    customsCongestion: 26,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "DEHA155",
    country: "Germany",
    customsCongestion: 30,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "INBO156",
    country: "India",
    customsCongestion: 46,
    coldChainReliability: 69,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "BRSS157",
    country: "Brazil",
    customsCongestion: 55,
    coldChainReliability: 71,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "IEOR158",
    country: "Ireland",
    customsCongestion: 23,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "KRPU159",
    country: "South Korea",
    customsCongestion: 32,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "SGSI160",
    country: "Singapore",
    customsCongestion: 24,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "MXME161",
    country: "Mexico",
    customsCongestion: 30,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "MXVE162",
    country: "Mexico",
    customsCongestion: 45,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "USLA163",
    country: "United States",
    customsCongestion: 50,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "USIA164",
    country: "United States",
    customsCongestion: 36,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "DEHA165",
    country: "Germany",
    customsCongestion: 40,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "INBO166",
    country: "India",
    customsCongestion: 56,
    coldChainReliability: 68,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "BRSS167",
    country: "Brazil",
    customsCongestion: 65,
    coldChainReliability: 70,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "IEOR168",
    country: "Ireland",
    customsCongestion: 19,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "KRPU169",
    country: "South Korea",
    customsCongestion: 28,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "SGSI170",
    country: "Singapore",
    customsCongestion: 20,
    coldChainReliability: 88,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "MXME171",
    country: "Mexico",
    customsCongestion: 26,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "MXVE172",
    country: "Mexico",
    customsCongestion: 41,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "USLA173",
    country: "United States",
    customsCongestion: 46,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "USIA174",
    country: "United States",
    customsCongestion: 32,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "DEHA175",
    country: "Germany",
    customsCongestion: 36,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "INBO176",
    country: "India",
    customsCongestion: 52,
    coldChainReliability: 67,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "BRSS177",
    country: "Brazil",
    customsCongestion: 61,
    coldChainReliability: 69,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "IEOR178",
    country: "Ireland",
    customsCongestion: 29,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "KRPU179",
    country: "South Korea",
    customsCongestion: 38,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "SGSI180",
    country: "Singapore",
    customsCongestion: 30,
    coldChainReliability: 96,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "MXME181",
    country: "Mexico",
    customsCongestion: 36,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "MXVE182",
    country: "Mexico",
    customsCongestion: 37,
    coldChainReliability: 79,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "USLA183",
    country: "United States",
    customsCongestion: 42,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "USIA184",
    country: "United States",
    customsCongestion: 28,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "DEHA185",
    country: "Germany",
    customsCongestion: 32,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "INBO186",
    country: "India",
    customsCongestion: 48,
    coldChainReliability: 66,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "BRSS187",
    country: "Brazil",
    customsCongestion: 57,
    coldChainReliability: 68,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "IEOR188",
    country: "Ireland",
    customsCongestion: 25,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "KRPU189",
    country: "South Korea",
    customsCongestion: 34,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "SGSI190",
    country: "Singapore",
    customsCongestion: 26,
    coldChainReliability: 95,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "MXME191",
    country: "Mexico",
    customsCongestion: 32,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "MXVE192",
    country: "Mexico",
    customsCongestion: 47,
    coldChainReliability: 78,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "USLA193",
    country: "United States",
    customsCongestion: 52,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "USIA194",
    country: "United States",
    customsCongestion: 38,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "DEHA195",
    country: "Germany",
    customsCongestion: 42,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "INBO196",
    country: "India",
    customsCongestion: 44,
    coldChainReliability: 65,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "BRSS197",
    country: "Brazil",
    customsCongestion: 53,
    coldChainReliability: 67,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "IEOR198",
    country: "Ireland",
    customsCongestion: 21,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "KRPU199",
    country: "South Korea",
    customsCongestion: 30,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "SGSI200",
    country: "Singapore",
    customsCongestion: 22,
    coldChainReliability: 94,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "MXME201",
    country: "Mexico",
    customsCongestion: 28,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "MXVE202",
    country: "Mexico",
    customsCongestion: 43,
    coldChainReliability: 77,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "USLA203",
    country: "United States",
    customsCongestion: 48,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "USIA204",
    country: "United States",
    customsCongestion: 34,
    coldChainReliability: 82,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "DEHA205",
    country: "Germany",
    customsCongestion: 38,
    coldChainReliability: 83,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "INBO206",
    country: "India",
    customsCongestion: 54,
    coldChainReliability: 64,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "BRSS207",
    country: "Brazil",
    customsCongestion: 63,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "IEOR208",
    country: "Ireland",
    customsCongestion: 31,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "KRPU209",
    country: "South Korea",
    customsCongestion: 40,
    coldChainReliability: 87,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "SGSI210",
    country: "Singapore",
    customsCongestion: 18,
    coldChainReliability: 93,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "MXME211",
    country: "Mexico",
    customsCongestion: 24,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "MXVE212",
    country: "Mexico",
    customsCongestion: 39,
    coldChainReliability: 76,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "USLA213",
    country: "United States",
    customsCongestion: 44,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "USIA214",
    country: "United States",
    customsCongestion: 30,
    coldChainReliability: 81,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "DEHA215",
    country: "Germany",
    customsCongestion: 34,
    coldChainReliability: 82,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "INBO216",
    country: "India",
    customsCongestion: 50,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "BRSS217",
    country: "Brazil",
    customsCongestion: 59,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "IEOR218",
    country: "Ireland",
    customsCongestion: 27,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "KRPU219",
    country: "South Korea",
    customsCongestion: 36,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "SGSI220",
    country: "Singapore",
    customsCongestion: 28,
    coldChainReliability: 92,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "MXME221",
    country: "Mexico",
    customsCongestion: 34,
    coldChainReliability: 87,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "MXVE222",
    country: "Mexico",
    customsCongestion: 49,
    coldChainReliability: 75,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "USLA223",
    country: "United States",
    customsCongestion: 54,
    coldChainReliability: 79,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "USIA224",
    country: "United States",
    customsCongestion: 26,
    coldChainReliability: 80,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "DEHA225",
    country: "Germany",
    customsCongestion: 30,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "INBO226",
    country: "India",
    customsCongestion: 46,
    coldChainReliability: 71,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "BRSS227",
    country: "Brazil",
    customsCongestion: 55,
    coldChainReliability: 73,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "IEOR228",
    country: "Ireland",
    customsCongestion: 23,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  },
  {
    port: "KRPU229",
    country: "South Korea",
    customsCongestion: 32,
    coldChainReliability: 85,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 02 risk planning."
  },
  {
    port: "SGSI230",
    country: "Singapore",
    customsCongestion: 24,
    coldChainReliability: 91,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 03 risk planning."
  },
  {
    port: "MXME231",
    country: "Mexico",
    customsCongestion: 30,
    coldChainReliability: 86,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 04 risk planning."
  },
  {
    port: "MXVE232",
    country: "Mexico",
    customsCongestion: 45,
    coldChainReliability: 74,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 05 risk planning."
  },
  {
    port: "USLA233",
    country: "United States",
    customsCongestion: 50,
    coldChainReliability: 78,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 06 risk planning."
  },
  {
    port: "USIA234",
    country: "United States",
    customsCongestion: 36,
    coldChainReliability: 88,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 07 risk planning."
  },
  {
    port: "DEHA235",
    country: "Germany",
    customsCongestion: 40,
    coldChainReliability: 89,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 08 risk planning."
  },
  {
    port: "INBO236",
    country: "India",
    customsCongestion: 56,
    coldChainReliability: 70,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 09 risk planning."
  },
  {
    port: "BRSS237",
    country: "Brazil",
    customsCongestion: 65,
    coldChainReliability: 72,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 10 risk planning."
  },
  {
    port: "IEOR238",
    country: "Ireland",
    customsCongestion: 19,
    coldChainReliability: 90,
    strikeAlert: true,
    note: "Derived lane watchlist entry for month 11 risk planning."
  },
  {
    port: "KRPU239",
    country: "South Korea",
    customsCongestion: 28,
    coldChainReliability: 84,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 12 risk planning."
  },
  {
    port: "SGSI240",
    country: "Singapore",
    customsCongestion: 20,
    coldChainReliability: 90,
    strikeAlert: false,
    note: "Derived lane watchlist entry for month 01 risk planning."
  }
];

export const RECEIVING_MANIFEST_LIBRARY: readonly ShipmentManifestProfile[] = [
  {
    id: "manifest-0001",
    awbBl: "AWB-00000001",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0001",
    quantity: 817,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-06T03:11:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0002",
    awbBl: "AWB-00000002",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0002",
    quantity: 834,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-11T06:22:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0003",
    awbBl: "AWB-00000003",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0003",
    quantity: 851,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-16T09:33:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0004",
    awbBl: "AWB-00000004",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0004",
    quantity: 868,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-21T12:44:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0005",
    awbBl: "AWB-00000005",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0005",
    quantity: 885,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-26T15:55:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0006",
    awbBl: "AWB-00000006",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0006",
    quantity: 902,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-04T18:07:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0007",
    awbBl: "AWB-00000007",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0007",
    quantity: 919,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-09T21:18:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0008",
    awbBl: "AWB-00000008",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0008",
    quantity: 936,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-14T01:29:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0009",
    awbBl: "AWB-00000009",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0009",
    quantity: 953,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-19T04:40:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0010",
    awbBl: "AWB-00000010",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0010",
    quantity: 970,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-24T07:51:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0011",
    awbBl: "AWB-00000011",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0011",
    quantity: 987,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-02T10:03:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0012",
    awbBl: "AWB-00000012",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0012",
    quantity: 1004,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-07T13:14:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0013",
    awbBl: "AWB-00000013",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0013",
    quantity: 1021,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-12T16:25:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0014",
    awbBl: "AWB-00000014",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0014",
    quantity: 1038,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-17T19:36:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0015",
    awbBl: "AWB-00000015",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0015",
    quantity: 1055,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-22T22:47:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0016",
    awbBl: "AWB-00000016",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0016",
    quantity: 1072,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-27T02:58:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0017",
    awbBl: "AWB-00000017",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0017",
    quantity: 1089,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-05T05:10:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0018",
    awbBl: "AWB-00000018",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0018",
    quantity: 1106,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-10T08:21:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0019",
    awbBl: "AWB-00000019",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0019",
    quantity: 1123,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-15T11:32:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0020",
    awbBl: "AWB-00000020",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0020",
    quantity: 1140,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-20T14:43:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0021",
    awbBl: "AWB-00000021",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0021",
    quantity: 1157,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-25T17:54:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0022",
    awbBl: "AWB-00000022",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0022",
    quantity: 1174,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-03T20:06:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0023",
    awbBl: "AWB-00000023",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0023",
    quantity: 1191,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-08T00:17:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0024",
    awbBl: "AWB-00000024",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0024",
    quantity: 1208,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-13T03:28:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0025",
    awbBl: "AWB-00000025",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0025",
    quantity: 1225,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-18T06:39:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0026",
    awbBl: "AWB-00000026",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0026",
    quantity: 1242,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-23T09:50:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0027",
    awbBl: "AWB-00000027",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0027",
    quantity: 1259,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-01T12:02:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0028",
    awbBl: "AWB-00000028",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0028",
    quantity: 1276,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-06T15:13:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0029",
    awbBl: "AWB-00000029",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0029",
    quantity: 1293,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-11T18:24:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0030",
    awbBl: "AWB-00000030",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0030",
    quantity: 1310,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-16T21:35:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0031",
    awbBl: "AWB-00000031",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0031",
    quantity: 1327,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-21T01:46:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0032",
    awbBl: "AWB-00000032",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0032",
    quantity: 1344,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-26T04:57:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0033",
    awbBl: "AWB-00000033",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0033",
    quantity: 1361,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-04T07:09:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0034",
    awbBl: "AWB-00000034",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0034",
    quantity: 1378,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-09T10:20:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0035",
    awbBl: "AWB-00000035",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0035",
    quantity: 1395,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-14T13:31:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0036",
    awbBl: "AWB-00000036",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0036",
    quantity: 1412,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-19T16:42:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0037",
    awbBl: "AWB-00000037",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0037",
    quantity: 1429,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-24T19:53:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0038",
    awbBl: "AWB-00000038",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0038",
    quantity: 1446,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-02T22:05:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0039",
    awbBl: "AWB-00000039",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0039",
    quantity: 1463,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-07T02:16:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0040",
    awbBl: "AWB-00000040",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0040",
    quantity: 1480,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-12T05:27:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0041",
    awbBl: "AWB-00000041",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0041",
    quantity: 1497,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-17T08:38:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0042",
    awbBl: "AWB-00000042",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0042",
    quantity: 1514,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-22T11:49:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0043",
    awbBl: "AWB-00000043",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0043",
    quantity: 1531,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-27T14:01:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0044",
    awbBl: "AWB-00000044",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0044",
    quantity: 1548,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-05T17:12:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0045",
    awbBl: "AWB-00000045",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0045",
    quantity: 1565,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-10T20:23:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0046",
    awbBl: "AWB-00000046",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0046",
    quantity: 1582,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-15T00:34:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0047",
    awbBl: "AWB-00000047",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0047",
    quantity: 1599,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-20T03:45:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0048",
    awbBl: "AWB-00000048",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0048",
    quantity: 1616,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-25T06:56:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0049",
    awbBl: "AWB-00000049",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0049",
    quantity: 1633,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-03T09:08:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0050",
    awbBl: "AWB-00000050",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0050",
    quantity: 1650,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-08T12:19:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0051",
    awbBl: "AWB-00000051",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0051",
    quantity: 1667,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-13T15:30:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0052",
    awbBl: "AWB-00000052",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0052",
    quantity: 1684,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-18T18:41:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0053",
    awbBl: "AWB-00000053",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0053",
    quantity: 1701,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-23T21:52:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0054",
    awbBl: "AWB-00000054",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0054",
    quantity: 1718,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-01T01:04:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0055",
    awbBl: "AWB-00000055",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0055",
    quantity: 1735,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-06T04:15:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0056",
    awbBl: "AWB-00000056",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0056",
    quantity: 1752,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-11T07:26:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0057",
    awbBl: "AWB-00000057",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0057",
    quantity: 1769,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-16T10:37:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0058",
    awbBl: "AWB-00000058",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0058",
    quantity: 1786,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-21T13:48:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0059",
    awbBl: "AWB-00000059",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0059",
    quantity: 1803,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-26T16:00:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0060",
    awbBl: "AWB-00000060",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0060",
    quantity: 1820,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-04T19:11:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0061",
    awbBl: "AWB-00000061",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0061",
    quantity: 1837,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-09T22:22:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0062",
    awbBl: "AWB-00000062",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0062",
    quantity: 1854,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-14T02:33:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0063",
    awbBl: "AWB-00000063",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0063",
    quantity: 1871,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-19T05:44:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0064",
    awbBl: "AWB-00000064",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0064",
    quantity: 1888,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-24T08:55:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0065",
    awbBl: "AWB-00000065",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0065",
    quantity: 1905,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-02T11:07:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0066",
    awbBl: "AWB-00000066",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0066",
    quantity: 1922,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-07T14:18:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0067",
    awbBl: "AWB-00000067",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0067",
    quantity: 1939,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-12T17:29:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0068",
    awbBl: "AWB-00000068",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0068",
    quantity: 1956,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-17T20:40:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0069",
    awbBl: "AWB-00000069",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0069",
    quantity: 1973,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-22T00:51:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0070",
    awbBl: "AWB-00000070",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0070",
    quantity: 1990,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-27T03:03:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0071",
    awbBl: "AWB-00000071",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0071",
    quantity: 2007,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-05T06:14:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0072",
    awbBl: "AWB-00000072",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0072",
    quantity: 2024,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-10T09:25:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0073",
    awbBl: "AWB-00000073",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0073",
    quantity: 2041,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-15T12:36:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0074",
    awbBl: "AWB-00000074",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0074",
    quantity: 2058,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-20T15:47:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0075",
    awbBl: "AWB-00000075",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0075",
    quantity: 2075,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-25T18:58:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0076",
    awbBl: "AWB-00000076",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0076",
    quantity: 2092,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-03T21:10:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0077",
    awbBl: "AWB-00000077",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0077",
    quantity: 2109,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-08T01:21:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0078",
    awbBl: "AWB-00000078",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0078",
    quantity: 2126,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-13T04:32:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0079",
    awbBl: "AWB-00000079",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0079",
    quantity: 2143,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-18T07:43:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0080",
    awbBl: "AWB-00000080",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0080",
    quantity: 2160,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-23T10:54:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0081",
    awbBl: "AWB-00000081",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0081",
    quantity: 2177,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-01T13:06:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0082",
    awbBl: "AWB-00000082",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0082",
    quantity: 2194,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-06T16:17:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0083",
    awbBl: "AWB-00000083",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0083",
    quantity: 2211,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-11T19:28:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0084",
    awbBl: "AWB-00000084",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0084",
    quantity: 2228,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-16T22:39:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0085",
    awbBl: "AWB-00000085",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0085",
    quantity: 2245,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-21T02:50:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0086",
    awbBl: "AWB-00000086",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0086",
    quantity: 2262,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-26T05:02:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0087",
    awbBl: "AWB-00000087",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0087",
    quantity: 2279,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-04T08:13:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0088",
    awbBl: "AWB-00000088",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0088",
    quantity: 2296,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-09T11:24:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0089",
    awbBl: "AWB-00000089",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0089",
    quantity: 2313,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-14T14:35:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0090",
    awbBl: "AWB-00000090",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0090",
    quantity: 2330,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-19T17:46:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0091",
    awbBl: "AWB-00000091",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0091",
    quantity: 2347,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-24T20:57:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0092",
    awbBl: "AWB-00000092",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0092",
    quantity: 2364,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-02T00:09:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0093",
    awbBl: "AWB-00000093",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0093",
    quantity: 2381,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-07T03:20:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0094",
    awbBl: "AWB-00000094",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0094",
    quantity: 2398,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-12T06:31:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0095",
    awbBl: "AWB-00000095",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0095",
    quantity: 2415,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-17T09:42:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0096",
    awbBl: "AWB-00000096",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0096",
    quantity: 2432,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-22T12:53:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0097",
    awbBl: "AWB-00000097",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0097",
    quantity: 2449,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-27T15:05:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0098",
    awbBl: "AWB-00000098",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0098",
    quantity: 2466,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-05T18:16:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0099",
    awbBl: "AWB-00000099",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0099",
    quantity: 2483,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-10T21:27:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0100",
    awbBl: "AWB-00000100",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0100",
    quantity: 2500,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-15T01:38:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0101",
    awbBl: "AWB-00000101",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0101",
    quantity: 2517,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-20T04:49:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0102",
    awbBl: "AWB-00000102",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0102",
    quantity: 2534,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-25T07:01:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0103",
    awbBl: "AWB-00000103",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0103",
    quantity: 2551,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-03T10:12:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0104",
    awbBl: "AWB-00000104",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0104",
    quantity: 2568,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-08T13:23:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0105",
    awbBl: "AWB-00000105",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0105",
    quantity: 2585,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-13T16:34:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0106",
    awbBl: "AWB-00000106",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0106",
    quantity: 2602,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-18T19:45:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0107",
    awbBl: "AWB-00000107",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0107",
    quantity: 2619,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-23T22:56:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0108",
    awbBl: "AWB-00000108",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0108",
    quantity: 2636,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-01T02:08:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0109",
    awbBl: "AWB-00000109",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0109",
    quantity: 2653,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-06T05:19:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0110",
    awbBl: "AWB-00000110",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0110",
    quantity: 2670,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-11T08:30:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0111",
    awbBl: "AWB-00000111",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0111",
    quantity: 2687,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-16T11:41:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0112",
    awbBl: "AWB-00000112",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0112",
    quantity: 2704,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-21T14:52:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0113",
    awbBl: "AWB-00000113",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0113",
    quantity: 2721,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-26T17:04:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0114",
    awbBl: "AWB-00000114",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0114",
    quantity: 2738,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-04T20:15:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0115",
    awbBl: "AWB-00000115",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0115",
    quantity: 2755,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-09T00:26:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0116",
    awbBl: "AWB-00000116",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0116",
    quantity: 2772,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-14T03:37:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0117",
    awbBl: "AWB-00000117",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0117",
    quantity: 2789,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-19T06:48:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0118",
    awbBl: "AWB-00000118",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0118",
    quantity: 2806,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-24T09:00:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0119",
    awbBl: "AWB-00000119",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0119",
    quantity: 2823,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-02T12:11:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0120",
    awbBl: "AWB-00000120",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0120",
    quantity: 2840,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-07T15:22:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0121",
    awbBl: "AWB-00000121",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0121",
    quantity: 2857,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-12T18:33:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0122",
    awbBl: "AWB-00000122",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0122",
    quantity: 2874,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-17T21:44:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0123",
    awbBl: "AWB-00000123",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0123",
    quantity: 2891,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-22T01:55:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0124",
    awbBl: "AWB-00000124",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0124",
    quantity: 2908,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-27T04:07:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0125",
    awbBl: "AWB-00000125",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0125",
    quantity: 2925,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-05T07:18:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0126",
    awbBl: "AWB-00000126",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0126",
    quantity: 2942,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-10T10:29:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0127",
    awbBl: "AWB-00000127",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0127",
    quantity: 2959,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-15T13:40:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0128",
    awbBl: "AWB-00000128",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0128",
    quantity: 2976,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-20T16:51:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0129",
    awbBl: "AWB-00000129",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0129",
    quantity: 2993,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-25T19:03:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0130",
    awbBl: "AWB-00000130",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0130",
    quantity: 3010,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-03T22:14:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0131",
    awbBl: "AWB-00000131",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0131",
    quantity: 3027,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-08T02:25:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0132",
    awbBl: "AWB-00000132",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0132",
    quantity: 3044,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-13T05:36:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0133",
    awbBl: "AWB-00000133",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0133",
    quantity: 3061,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-18T08:47:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0134",
    awbBl: "AWB-00000134",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0134",
    quantity: 3078,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-23T11:58:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0135",
    awbBl: "AWB-00000135",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0135",
    quantity: 3095,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-01T14:10:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0136",
    awbBl: "AWB-00000136",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0136",
    quantity: 3112,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-06T17:21:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0137",
    awbBl: "AWB-00000137",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0137",
    quantity: 3129,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-11T20:32:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0138",
    awbBl: "AWB-00000138",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0138",
    quantity: 3146,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-16T00:43:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0139",
    awbBl: "AWB-00000139",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0139",
    quantity: 3163,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-21T03:54:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0140",
    awbBl: "AWB-00000140",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0140",
    quantity: 3180,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-26T06:06:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0141",
    awbBl: "AWB-00000141",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0141",
    quantity: 3197,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-04T09:17:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0142",
    awbBl: "AWB-00000142",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0142",
    quantity: 3214,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-09T12:28:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0143",
    awbBl: "AWB-00000143",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0143",
    quantity: 3231,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-14T15:39:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0144",
    awbBl: "AWB-00000144",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0144",
    quantity: 3248,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-19T18:50:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0145",
    awbBl: "AWB-00000145",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0145",
    quantity: 3265,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-24T21:02:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0146",
    awbBl: "AWB-00000146",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0146",
    quantity: 3282,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-02T01:13:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0147",
    awbBl: "AWB-00000147",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0147",
    quantity: 3299,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-07T04:24:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0148",
    awbBl: "AWB-00000148",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0148",
    quantity: 3316,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-12T07:35:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0149",
    awbBl: "AWB-00000149",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0149",
    quantity: 3333,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-17T10:46:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0150",
    awbBl: "AWB-00000150",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0150",
    quantity: 3350,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-22T13:57:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0151",
    awbBl: "AWB-00000151",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0151",
    quantity: 3367,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-27T16:09:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0152",
    awbBl: "AWB-00000152",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0152",
    quantity: 3384,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-05T19:20:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0153",
    awbBl: "AWB-00000153",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0153",
    quantity: 3401,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-10T22:31:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0154",
    awbBl: "AWB-00000154",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0154",
    quantity: 3418,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-15T02:42:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0155",
    awbBl: "AWB-00000155",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0155",
    quantity: 3435,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-20T05:53:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0156",
    awbBl: "AWB-00000156",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0156",
    quantity: 3452,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-25T08:05:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0157",
    awbBl: "AWB-00000157",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0157",
    quantity: 3469,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-03T11:16:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0158",
    awbBl: "AWB-00000158",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0158",
    quantity: 3486,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-08T14:27:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0159",
    awbBl: "AWB-00000159",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0159",
    quantity: 3503,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-13T17:38:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0160",
    awbBl: "AWB-00000160",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0160",
    quantity: 3520,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-18T20:49:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0161",
    awbBl: "AWB-00000161",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0161",
    quantity: 3537,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-23T00:01:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0162",
    awbBl: "AWB-00000162",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0162",
    quantity: 3554,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-01T03:12:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0163",
    awbBl: "AWB-00000163",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0163",
    quantity: 3571,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-06T06:23:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0164",
    awbBl: "AWB-00000164",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0164",
    quantity: 3588,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-11T09:34:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0165",
    awbBl: "AWB-00000165",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0165",
    quantity: 3605,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-16T12:45:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0166",
    awbBl: "AWB-00000166",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0166",
    quantity: 3622,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-21T15:56:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0167",
    awbBl: "AWB-00000167",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0167",
    quantity: 3639,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-26T18:08:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0168",
    awbBl: "AWB-00000168",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0168",
    quantity: 3656,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-04T21:19:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0169",
    awbBl: "AWB-00000169",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0169",
    quantity: 3673,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-09T01:30:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0170",
    awbBl: "AWB-00000170",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0170",
    quantity: 3690,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-14T04:41:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0171",
    awbBl: "AWB-00000171",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0171",
    quantity: 3707,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-19T07:52:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0172",
    awbBl: "AWB-00000172",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0172",
    quantity: 3724,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-24T10:04:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0173",
    awbBl: "AWB-00000173",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0173",
    quantity: 3741,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-02T13:15:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0174",
    awbBl: "AWB-00000174",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0174",
    quantity: 3758,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-07T16:26:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0175",
    awbBl: "AWB-00000175",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0175",
    quantity: 3775,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-12T19:37:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0176",
    awbBl: "AWB-00000176",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0176",
    quantity: 3792,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-17T22:48:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0177",
    awbBl: "AWB-00000177",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0177",
    quantity: 3809,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-22T02:00:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0178",
    awbBl: "AWB-00000178",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0178",
    quantity: 3826,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-27T05:11:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0179",
    awbBl: "AWB-00000179",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0179",
    quantity: 3843,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-05T08:22:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0180",
    awbBl: "AWB-00000180",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0180",
    quantity: 3860,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-10T11:33:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0181",
    awbBl: "AWB-00000181",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0181",
    quantity: 3877,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-15T14:44:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0182",
    awbBl: "AWB-00000182",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0182",
    quantity: 3894,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-20T17:55:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0183",
    awbBl: "AWB-00000183",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0183",
    quantity: 3911,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-25T20:07:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0184",
    awbBl: "AWB-00000184",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0184",
    quantity: 3928,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-03T00:18:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0185",
    awbBl: "AWB-00000185",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0185",
    quantity: 3945,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-08T03:29:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0186",
    awbBl: "AWB-00000186",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0186",
    quantity: 3962,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-13T06:40:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0187",
    awbBl: "AWB-00000187",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0187",
    quantity: 3979,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-18T09:51:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0188",
    awbBl: "AWB-00000188",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0188",
    quantity: 3996,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-23T12:03:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0189",
    awbBl: "AWB-00000189",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0189",
    quantity: 4013,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-01T15:14:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0190",
    awbBl: "AWB-00000190",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0190",
    quantity: 4030,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-06T18:25:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0191",
    awbBl: "AWB-00000191",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0191",
    quantity: 4047,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-11T21:36:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0192",
    awbBl: "AWB-00000192",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0192",
    quantity: 4064,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-16T01:47:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0193",
    awbBl: "AWB-00000193",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0193",
    quantity: 4081,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-21T04:58:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0194",
    awbBl: "AWB-00000194",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0194",
    quantity: 4098,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-26T07:10:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0195",
    awbBl: "AWB-00000195",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0195",
    quantity: 4115,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-04T10:21:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0196",
    awbBl: "AWB-00000196",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0196",
    quantity: 4132,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-09T13:32:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0197",
    awbBl: "AWB-00000197",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0197",
    quantity: 4149,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-14T16:43:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0198",
    awbBl: "AWB-00000198",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0198",
    quantity: 4166,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-19T19:54:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0199",
    awbBl: "AWB-00000199",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0199",
    quantity: 4183,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-24T22:06:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0200",
    awbBl: "AWB-00000200",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0200",
    quantity: 4200,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-02T02:17:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0201",
    awbBl: "AWB-00000201",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0201",
    quantity: 4217,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-07T05:28:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0202",
    awbBl: "AWB-00000202",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0202",
    quantity: 4234,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-12T08:39:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0203",
    awbBl: "AWB-00000203",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0203",
    quantity: 4251,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-17T11:50:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0204",
    awbBl: "AWB-00000204",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0204",
    quantity: 4268,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-22T14:02:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0205",
    awbBl: "AWB-00000205",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0205",
    quantity: 4285,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-27T17:13:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0206",
    awbBl: "AWB-00000206",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0206",
    quantity: 4302,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-05T20:24:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0207",
    awbBl: "AWB-00000207",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0207",
    quantity: 4319,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-10T00:35:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0208",
    awbBl: "AWB-00000208",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0208",
    quantity: 4336,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-15T03:46:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0209",
    awbBl: "AWB-00000209",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0209",
    quantity: 4353,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-20T06:57:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0210",
    awbBl: "AWB-00000210",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0210",
    quantity: 4370,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-25T09:09:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0211",
    awbBl: "AWB-00000211",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0211",
    quantity: 4387,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-03T12:20:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0212",
    awbBl: "AWB-00000212",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0212",
    quantity: 804,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-08T15:31:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0213",
    awbBl: "AWB-00000213",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0213",
    quantity: 821,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-13T18:42:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0214",
    awbBl: "AWB-00000214",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0214",
    quantity: 838,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-18T21:53:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0215",
    awbBl: "AWB-00000215",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0215",
    quantity: 855,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-23T01:05:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0216",
    awbBl: "AWB-00000216",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0216",
    quantity: 872,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-01T04:16:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0217",
    awbBl: "AWB-00000217",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0217",
    quantity: 889,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-06T07:27:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0218",
    awbBl: "AWB-00000218",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0218",
    quantity: 906,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-11T10:38:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0219",
    awbBl: "AWB-00000219",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0219",
    quantity: 923,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-16T13:49:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0220",
    awbBl: "AWB-00000220",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0220",
    quantity: 940,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-21T16:01:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0221",
    awbBl: "AWB-00000221",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0221",
    quantity: 957,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-26T19:12:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0222",
    awbBl: "AWB-00000222",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0222",
    quantity: 974,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-04T22:23:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0223",
    awbBl: "AWB-00000223",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0223",
    quantity: 991,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-09T02:34:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0224",
    awbBl: "AWB-00000224",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0224",
    quantity: 1008,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-14T05:45:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0225",
    awbBl: "AWB-00000225",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0225",
    quantity: 1025,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-19T08:56:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0226",
    awbBl: "AWB-00000226",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0226",
    quantity: 1042,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-24T11:08:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0227",
    awbBl: "AWB-00000227",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0227",
    quantity: 1059,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-02T14:19:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0228",
    awbBl: "AWB-00000228",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0228",
    quantity: 1076,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-07T17:30:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0229",
    awbBl: "AWB-00000229",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0229",
    quantity: 1093,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-12T20:41:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0230",
    awbBl: "AWB-00000230",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0230",
    quantity: 1110,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-17T00:52:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0231",
    awbBl: "AWB-00000231",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0231",
    quantity: 1127,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-22T03:04:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0232",
    awbBl: "AWB-00000232",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0232",
    quantity: 1144,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-27T06:15:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0233",
    awbBl: "AWB-00000233",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0233",
    quantity: 1161,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-05T09:26:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0234",
    awbBl: "AWB-00000234",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0234",
    quantity: 1178,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-10T12:37:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0235",
    awbBl: "AWB-00000235",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0235",
    quantity: 1195,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-15T15:48:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0236",
    awbBl: "AWB-00000236",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0236",
    quantity: 1212,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-20T18:00:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0237",
    awbBl: "AWB-00000237",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0237",
    quantity: 1229,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-25T21:11:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0238",
    awbBl: "AWB-00000238",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0238",
    quantity: 1246,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-03T01:22:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0239",
    awbBl: "AWB-00000239",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0239",
    quantity: 1263,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-08T04:33:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0240",
    awbBl: "AWB-00000240",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0240",
    quantity: 1280,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-13T07:44:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0241",
    awbBl: "AWB-00000241",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0241",
    quantity: 1297,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-18T10:55:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0242",
    awbBl: "AWB-00000242",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0242",
    quantity: 1314,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-23T13:07:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0243",
    awbBl: "AWB-00000243",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0243",
    quantity: 1331,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-01T16:18:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0244",
    awbBl: "AWB-00000244",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0244",
    quantity: 1348,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-06T19:29:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0245",
    awbBl: "AWB-00000245",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0245",
    quantity: 1365,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-11T22:40:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0246",
    awbBl: "AWB-00000246",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0246",
    quantity: 1382,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-16T02:51:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0247",
    awbBl: "AWB-00000247",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0247",
    quantity: 1399,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-21T05:03:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0248",
    awbBl: "AWB-00000248",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0248",
    quantity: 1416,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-26T08:14:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0249",
    awbBl: "AWB-00000249",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0249",
    quantity: 1433,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-04T11:25:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0250",
    awbBl: "AWB-00000250",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0250",
    quantity: 1450,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-09T14:36:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0251",
    awbBl: "AWB-00000251",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0251",
    quantity: 1467,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-14T17:47:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0252",
    awbBl: "AWB-00000252",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0252",
    quantity: 1484,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-19T20:58:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0253",
    awbBl: "AWB-00000253",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0253",
    quantity: 1501,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-24T00:10:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0254",
    awbBl: "AWB-00000254",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0254",
    quantity: 1518,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-02T03:21:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0255",
    awbBl: "AWB-00000255",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0255",
    quantity: 1535,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-07T06:32:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0256",
    awbBl: "AWB-00000256",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0256",
    quantity: 1552,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-12T09:43:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0257",
    awbBl: "AWB-00000257",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0257",
    quantity: 1569,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-17T12:54:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0258",
    awbBl: "AWB-00000258",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0258",
    quantity: 1586,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-22T15:06:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0259",
    awbBl: "AWB-00000259",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0259",
    quantity: 1603,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-27T18:17:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0260",
    awbBl: "AWB-00000260",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0260",
    quantity: 1620,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-05T21:28:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0261",
    awbBl: "AWB-00000261",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0261",
    quantity: 1637,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-10T01:39:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0262",
    awbBl: "AWB-00000262",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0262",
    quantity: 1654,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-15T04:50:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0263",
    awbBl: "AWB-00000263",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0263",
    quantity: 1671,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-20T07:02:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0264",
    awbBl: "AWB-00000264",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0264",
    quantity: 1688,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-25T10:13:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0265",
    awbBl: "AWB-00000265",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0265",
    quantity: 1705,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-03T13:24:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0266",
    awbBl: "AWB-00000266",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0266",
    quantity: 1722,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-08T16:35:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0267",
    awbBl: "AWB-00000267",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0267",
    quantity: 1739,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-13T19:46:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0268",
    awbBl: "AWB-00000268",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0268",
    quantity: 1756,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-18T22:57:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0269",
    awbBl: "AWB-00000269",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0269",
    quantity: 1773,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-23T02:09:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0270",
    awbBl: "AWB-00000270",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0270",
    quantity: 1790,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-01T05:20:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0271",
    awbBl: "AWB-00000271",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0271",
    quantity: 1807,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-06T08:31:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0272",
    awbBl: "AWB-00000272",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0272",
    quantity: 1824,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-11T11:42:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0273",
    awbBl: "AWB-00000273",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0273",
    quantity: 1841,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-16T14:53:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0274",
    awbBl: "AWB-00000274",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0274",
    quantity: 1858,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-21T17:05:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0275",
    awbBl: "AWB-00000275",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0275",
    quantity: 1875,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-26T20:16:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0276",
    awbBl: "AWB-00000276",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0276",
    quantity: 1892,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-04T00:27:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0277",
    awbBl: "AWB-00000277",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0277",
    quantity: 1909,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-09T03:38:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0278",
    awbBl: "AWB-00000278",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0278",
    quantity: 1926,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-14T06:49:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0279",
    awbBl: "AWB-00000279",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0279",
    quantity: 1943,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-19T09:01:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0280",
    awbBl: "AWB-00000280",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0280",
    quantity: 1960,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-24T12:12:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0281",
    awbBl: "AWB-00000281",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0281",
    quantity: 1977,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-02T15:23:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0282",
    awbBl: "AWB-00000282",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0282",
    quantity: 1994,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-07T18:34:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0283",
    awbBl: "AWB-00000283",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0283",
    quantity: 2011,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-12T21:45:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0284",
    awbBl: "AWB-00000284",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0284",
    quantity: 2028,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-17T01:56:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0285",
    awbBl: "AWB-00000285",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0285",
    quantity: 2045,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-22T04:08:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0286",
    awbBl: "AWB-00000286",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0286",
    quantity: 2062,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-27T07:19:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0287",
    awbBl: "AWB-00000287",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0287",
    quantity: 2079,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-05T10:30:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0288",
    awbBl: "AWB-00000288",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0288",
    quantity: 2096,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-10T13:41:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0289",
    awbBl: "AWB-00000289",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0289",
    quantity: 2113,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-15T16:52:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0290",
    awbBl: "AWB-00000290",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0290",
    quantity: 2130,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-20T19:04:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0291",
    awbBl: "AWB-00000291",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0291",
    quantity: 2147,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-25T22:15:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0292",
    awbBl: "AWB-00000292",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0292",
    quantity: 2164,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-03T02:26:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0293",
    awbBl: "AWB-00000293",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0293",
    quantity: 2181,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-08T05:37:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0294",
    awbBl: "AWB-00000294",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0294",
    quantity: 2198,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-13T08:48:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0295",
    awbBl: "AWB-00000295",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0295",
    quantity: 2215,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-18T11:00:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0296",
    awbBl: "AWB-00000296",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0296",
    quantity: 2232,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-23T14:11:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0297",
    awbBl: "AWB-00000297",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0297",
    quantity: 2249,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-01T17:22:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0298",
    awbBl: "AWB-00000298",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0298",
    quantity: 2266,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-06T20:33:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0299",
    awbBl: "AWB-00000299",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0299",
    quantity: 2283,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-11T00:44:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0300",
    awbBl: "AWB-00000300",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0300",
    quantity: 2300,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-16T03:55:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0301",
    awbBl: "AWB-00000301",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0301",
    quantity: 2317,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-21T06:07:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0302",
    awbBl: "AWB-00000302",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0302",
    quantity: 2334,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-26T09:18:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0303",
    awbBl: "AWB-00000303",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0303",
    quantity: 2351,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-04T12:29:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0304",
    awbBl: "AWB-00000304",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0304",
    quantity: 2368,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-09T15:40:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0305",
    awbBl: "AWB-00000305",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0305",
    quantity: 2385,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-14T18:51:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0306",
    awbBl: "AWB-00000306",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0306",
    quantity: 2402,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-19T21:03:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0307",
    awbBl: "AWB-00000307",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0307",
    quantity: 2419,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-24T01:14:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0308",
    awbBl: "AWB-00000308",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0308",
    quantity: 2436,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-02T04:25:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0309",
    awbBl: "AWB-00000309",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0309",
    quantity: 2453,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-07T07:36:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0310",
    awbBl: "AWB-00000310",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0310",
    quantity: 2470,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-12T10:47:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0311",
    awbBl: "AWB-00000311",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0311",
    quantity: 2487,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-17T13:58:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0312",
    awbBl: "AWB-00000312",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0312",
    quantity: 2504,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-22T16:10:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0313",
    awbBl: "AWB-00000313",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0313",
    quantity: 2521,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-27T19:21:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0314",
    awbBl: "AWB-00000314",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0314",
    quantity: 2538,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-05T22:32:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0315",
    awbBl: "AWB-00000315",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0315",
    quantity: 2555,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-10T02:43:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0316",
    awbBl: "AWB-00000316",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0316",
    quantity: 2572,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-15T05:54:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0317",
    awbBl: "AWB-00000317",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0317",
    quantity: 2589,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-20T08:06:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0318",
    awbBl: "AWB-00000318",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0318",
    quantity: 2606,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-25T11:17:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0319",
    awbBl: "AWB-00000319",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0319",
    quantity: 2623,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-03T14:28:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0320",
    awbBl: "AWB-00000320",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0320",
    quantity: 2640,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-08T17:39:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0321",
    awbBl: "AWB-00000321",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0321",
    quantity: 2657,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-13T20:50:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0322",
    awbBl: "AWB-00000322",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0322",
    quantity: 2674,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-18T00:02:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0323",
    awbBl: "AWB-00000323",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0323",
    quantity: 2691,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-23T03:13:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0324",
    awbBl: "AWB-00000324",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0324",
    quantity: 2708,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-01T06:24:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0325",
    awbBl: "AWB-00000325",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0325",
    quantity: 2725,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-06T09:35:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0326",
    awbBl: "AWB-00000326",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0326",
    quantity: 2742,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-11T12:46:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0327",
    awbBl: "AWB-00000327",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0327",
    quantity: 2759,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-16T15:57:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0328",
    awbBl: "AWB-00000328",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0328",
    quantity: 2776,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-21T18:09:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0329",
    awbBl: "AWB-00000329",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0329",
    quantity: 2793,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-26T21:20:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0330",
    awbBl: "AWB-00000330",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0330",
    quantity: 2810,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-04T01:31:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0331",
    awbBl: "AWB-00000331",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0331",
    quantity: 2827,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-09T04:42:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0332",
    awbBl: "AWB-00000332",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0332",
    quantity: 2844,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-14T07:53:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0333",
    awbBl: "AWB-00000333",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0333",
    quantity: 2861,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-19T10:05:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0334",
    awbBl: "AWB-00000334",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0334",
    quantity: 2878,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-24T13:16:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0335",
    awbBl: "AWB-00000335",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0335",
    quantity: 2895,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-02T16:27:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0336",
    awbBl: "AWB-00000336",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0336",
    quantity: 2912,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-07T19:38:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0337",
    awbBl: "AWB-00000337",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0337",
    quantity: 2929,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-12T22:49:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0338",
    awbBl: "AWB-00000338",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0338",
    quantity: 2946,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-17T02:01:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0339",
    awbBl: "AWB-00000339",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0339",
    quantity: 2963,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-22T05:12:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0340",
    awbBl: "AWB-00000340",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0340",
    quantity: 2980,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-27T08:23:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0341",
    awbBl: "AWB-00000341",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0341",
    quantity: 2997,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-05T11:34:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0342",
    awbBl: "AWB-00000342",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0342",
    quantity: 3014,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-10T14:45:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0343",
    awbBl: "AWB-00000343",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0343",
    quantity: 3031,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-15T17:56:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0344",
    awbBl: "AWB-00000344",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0344",
    quantity: 3048,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-20T20:08:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0345",
    awbBl: "AWB-00000345",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0345",
    quantity: 3065,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-25T00:19:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0346",
    awbBl: "AWB-00000346",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0346",
    quantity: 3082,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-03T03:30:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0347",
    awbBl: "AWB-00000347",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0347",
    quantity: 3099,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-08T06:41:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0348",
    awbBl: "AWB-00000348",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0348",
    quantity: 3116,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-13T09:52:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0349",
    awbBl: "AWB-00000349",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0349",
    quantity: 3133,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-18T12:04:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0350",
    awbBl: "AWB-00000350",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0350",
    quantity: 3150,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-23T15:15:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0351",
    awbBl: "AWB-00000351",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0351",
    quantity: 3167,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-01T18:26:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0352",
    awbBl: "AWB-00000352",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0352",
    quantity: 3184,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-06T21:37:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0353",
    awbBl: "AWB-00000353",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0353",
    quantity: 3201,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-11T01:48:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0354",
    awbBl: "AWB-00000354",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0354",
    quantity: 3218,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-16T04:00:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0355",
    awbBl: "AWB-00000355",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0355",
    quantity: 3235,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-21T07:11:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0356",
    awbBl: "AWB-00000356",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0356",
    quantity: 3252,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-26T10:22:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0357",
    awbBl: "AWB-00000357",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0357",
    quantity: 3269,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-04T13:33:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0358",
    awbBl: "AWB-00000358",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0358",
    quantity: 3286,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-09T16:44:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0359",
    awbBl: "AWB-00000359",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0359",
    quantity: 3303,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-14T19:55:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0360",
    awbBl: "AWB-00000360",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0360",
    quantity: 3320,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-19T22:07:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0361",
    awbBl: "AWB-00000361",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0361",
    quantity: 3337,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-24T02:18:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0362",
    awbBl: "AWB-00000362",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0362",
    quantity: 3354,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-02T05:29:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0363",
    awbBl: "AWB-00000363",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0363",
    quantity: 3371,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-07T08:40:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0364",
    awbBl: "AWB-00000364",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0364",
    quantity: 3388,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-12T11:51:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0365",
    awbBl: "AWB-00000365",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0365",
    quantity: 3405,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-17T14:03:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0366",
    awbBl: "AWB-00000366",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0366",
    quantity: 3422,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-22T17:14:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0367",
    awbBl: "AWB-00000367",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0367",
    quantity: 3439,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-27T20:25:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0368",
    awbBl: "AWB-00000368",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0368",
    quantity: 3456,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-05T00:36:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0369",
    awbBl: "AWB-00000369",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0369",
    quantity: 3473,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-10T03:47:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0370",
    awbBl: "AWB-00000370",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0370",
    quantity: 3490,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-15T06:58:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0371",
    awbBl: "AWB-00000371",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0371",
    quantity: 3507,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-20T09:10:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0372",
    awbBl: "AWB-00000372",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0372",
    quantity: 3524,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-25T12:21:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0373",
    awbBl: "AWB-00000373",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0373",
    quantity: 3541,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-03T15:32:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0374",
    awbBl: "AWB-00000374",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0374",
    quantity: 3558,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-08T18:43:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0375",
    awbBl: "AWB-00000375",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0375",
    quantity: 3575,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-13T21:54:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0376",
    awbBl: "AWB-00000376",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0376",
    quantity: 3592,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-18T01:06:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0377",
    awbBl: "AWB-00000377",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0377",
    quantity: 3609,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-23T04:17:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0378",
    awbBl: "AWB-00000378",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0378",
    quantity: 3626,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-01T07:28:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0379",
    awbBl: "AWB-00000379",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0379",
    quantity: 3643,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-06T10:39:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0380",
    awbBl: "AWB-00000380",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0380",
    quantity: 3660,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-11T13:50:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0381",
    awbBl: "AWB-00000381",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0381",
    quantity: 3677,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-16T16:02:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0382",
    awbBl: "AWB-00000382",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0382",
    quantity: 3694,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-21T19:13:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0383",
    awbBl: "AWB-00000383",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0383",
    quantity: 3711,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-26T22:24:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0384",
    awbBl: "AWB-00000384",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0384",
    quantity: 3728,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-04T02:35:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0385",
    awbBl: "AWB-00000385",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0385",
    quantity: 3745,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-09T05:46:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0386",
    awbBl: "AWB-00000386",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0386",
    quantity: 3762,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-14T08:57:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0387",
    awbBl: "AWB-00000387",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0387",
    quantity: 3779,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-19T11:09:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0388",
    awbBl: "AWB-00000388",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0388",
    quantity: 3796,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-24T14:20:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0389",
    awbBl: "AWB-00000389",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0389",
    quantity: 3813,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-02T17:31:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0390",
    awbBl: "AWB-00000390",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0390",
    quantity: 3830,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-07T20:42:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0391",
    awbBl: "AWB-00000391",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0391",
    quantity: 3847,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-12T00:53:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0392",
    awbBl: "AWB-00000392",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0392",
    quantity: 3864,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-17T03:05:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0393",
    awbBl: "AWB-00000393",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0393",
    quantity: 3881,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-22T06:16:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0394",
    awbBl: "AWB-00000394",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0394",
    quantity: 3898,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-27T09:27:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0395",
    awbBl: "AWB-00000395",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0395",
    quantity: 3915,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-05T12:38:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0396",
    awbBl: "AWB-00000396",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0396",
    quantity: 3932,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-10T15:49:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0397",
    awbBl: "AWB-00000397",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0397",
    quantity: 3949,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-15T18:01:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0398",
    awbBl: "AWB-00000398",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0398",
    quantity: 3966,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-20T21:12:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0399",
    awbBl: "AWB-00000399",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0399",
    quantity: 3983,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-25T01:23:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0400",
    awbBl: "AWB-00000400",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0400",
    quantity: 4000,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-03T04:34:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0401",
    awbBl: "AWB-00000401",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0401",
    quantity: 4017,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-08T07:45:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0402",
    awbBl: "AWB-00000402",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0402",
    quantity: 4034,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-13T10:56:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0403",
    awbBl: "AWB-00000403",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0403",
    quantity: 4051,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-18T13:08:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0404",
    awbBl: "AWB-00000404",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0404",
    quantity: 4068,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-23T16:19:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0405",
    awbBl: "AWB-00000405",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0405",
    quantity: 4085,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-01T19:30:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0406",
    awbBl: "AWB-00000406",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0406",
    quantity: 4102,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-06T22:41:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0407",
    awbBl: "AWB-00000407",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0407",
    quantity: 4119,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-11T02:52:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0408",
    awbBl: "AWB-00000408",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0408",
    quantity: 4136,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-16T05:04:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0409",
    awbBl: "AWB-00000409",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0409",
    quantity: 4153,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-21T08:15:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0410",
    awbBl: "AWB-00000410",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0410",
    quantity: 4170,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-26T11:26:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0411",
    awbBl: "AWB-00000411",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0411",
    quantity: 4187,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-04T14:37:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0412",
    awbBl: "AWB-00000412",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0412",
    quantity: 4204,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-09T17:48:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0413",
    awbBl: "AWB-00000413",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0413",
    quantity: 4221,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-14T20:00:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0414",
    awbBl: "AWB-00000414",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0414",
    quantity: 4238,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-19T00:11:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0415",
    awbBl: "AWB-00000415",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0415",
    quantity: 4255,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-24T03:22:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0416",
    awbBl: "AWB-00000416",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0416",
    quantity: 4272,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-02T06:33:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0417",
    awbBl: "AWB-00000417",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0417",
    quantity: 4289,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-07T09:44:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0418",
    awbBl: "AWB-00000418",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0418",
    quantity: 4306,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-12T12:55:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0419",
    awbBl: "AWB-00000419",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0419",
    quantity: 4323,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-17T15:07:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0420",
    awbBl: "AWB-00000420",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0420",
    quantity: 4340,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-22T18:18:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0421",
    awbBl: "AWB-00000421",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0421",
    quantity: 4357,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-27T21:29:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0422",
    awbBl: "AWB-00000422",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0422",
    quantity: 4374,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-05T01:40:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0423",
    awbBl: "AWB-00000423",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0423",
    quantity: 4391,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-10T04:51:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0424",
    awbBl: "AWB-00000424",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0424",
    quantity: 808,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-15T07:03:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0425",
    awbBl: "AWB-00000425",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0425",
    quantity: 825,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-20T10:14:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0426",
    awbBl: "AWB-00000426",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0426",
    quantity: 842,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-25T13:25:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0427",
    awbBl: "AWB-00000427",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0427",
    quantity: 859,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-03T16:36:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0428",
    awbBl: "AWB-00000428",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0428",
    quantity: 876,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-08T19:47:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0429",
    awbBl: "AWB-00000429",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0429",
    quantity: 893,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-13T22:58:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0430",
    awbBl: "AWB-00000430",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0430",
    quantity: 910,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-18T02:10:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0431",
    awbBl: "AWB-00000431",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0431",
    quantity: 927,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-23T05:21:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0432",
    awbBl: "AWB-00000432",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0432",
    quantity: 944,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-01T08:32:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0433",
    awbBl: "AWB-00000433",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0433",
    quantity: 961,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-06T11:43:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0434",
    awbBl: "AWB-00000434",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0434",
    quantity: 978,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-11T14:54:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0435",
    awbBl: "AWB-00000435",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0435",
    quantity: 995,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-16T17:06:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0436",
    awbBl: "AWB-00000436",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0436",
    quantity: 1012,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-21T20:17:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0437",
    awbBl: "AWB-00000437",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0437",
    quantity: 1029,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-26T00:28:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0438",
    awbBl: "AWB-00000438",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0438",
    quantity: 1046,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-04T03:39:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0439",
    awbBl: "AWB-00000439",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0439",
    quantity: 1063,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-09T06:50:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0440",
    awbBl: "AWB-00000440",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0440",
    quantity: 1080,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-14T09:02:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0441",
    awbBl: "AWB-00000441",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0441",
    quantity: 1097,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-19T12:13:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0442",
    awbBl: "AWB-00000442",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0442",
    quantity: 1114,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-24T15:24:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0443",
    awbBl: "AWB-00000443",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0443",
    quantity: 1131,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-02T18:35:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0444",
    awbBl: "AWB-00000444",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0444",
    quantity: 1148,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-07T21:46:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0445",
    awbBl: "AWB-00000445",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0445",
    quantity: 1165,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-12T01:57:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0446",
    awbBl: "AWB-00000446",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0446",
    quantity: 1182,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-17T04:09:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0447",
    awbBl: "AWB-00000447",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0447",
    quantity: 1199,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-22T07:20:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0448",
    awbBl: "AWB-00000448",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0448",
    quantity: 1216,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-27T10:31:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0449",
    awbBl: "AWB-00000449",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0449",
    quantity: 1233,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-05T13:42:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0450",
    awbBl: "AWB-00000450",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0450",
    quantity: 1250,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-10T16:53:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0451",
    awbBl: "AWB-00000451",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0451",
    quantity: 1267,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-15T19:05:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0452",
    awbBl: "AWB-00000452",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0452",
    quantity: 1284,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-20T22:16:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0453",
    awbBl: "AWB-00000453",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0453",
    quantity: 1301,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-25T02:27:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0454",
    awbBl: "AWB-00000454",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0454",
    quantity: 1318,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-03T05:38:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0455",
    awbBl: "AWB-00000455",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0455",
    quantity: 1335,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-08T08:49:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0456",
    awbBl: "AWB-00000456",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0456",
    quantity: 1352,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-13T11:01:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0457",
    awbBl: "AWB-00000457",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0457",
    quantity: 1369,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-18T14:12:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0458",
    awbBl: "AWB-00000458",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0458",
    quantity: 1386,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-23T17:23:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0459",
    awbBl: "AWB-00000459",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0459",
    quantity: 1403,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-01T20:34:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0460",
    awbBl: "AWB-00000460",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0460",
    quantity: 1420,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-06T00:45:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0461",
    awbBl: "AWB-00000461",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0461",
    quantity: 1437,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-11T03:56:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0462",
    awbBl: "AWB-00000462",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0462",
    quantity: 1454,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-16T06:08:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0463",
    awbBl: "AWB-00000463",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0463",
    quantity: 1471,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-21T09:19:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0464",
    awbBl: "AWB-00000464",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0464",
    quantity: 1488,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-26T12:30:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0465",
    awbBl: "AWB-00000465",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0465",
    quantity: 1505,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-04T15:41:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0466",
    awbBl: "AWB-00000466",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0466",
    quantity: 1522,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-09T18:52:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0467",
    awbBl: "AWB-00000467",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0467",
    quantity: 1539,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-14T21:04:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0468",
    awbBl: "AWB-00000468",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0468",
    quantity: 1556,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-19T01:15:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0469",
    awbBl: "AWB-00000469",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0469",
    quantity: 1573,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-24T04:26:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0470",
    awbBl: "AWB-00000470",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0470",
    quantity: 1590,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-02T07:37:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0471",
    awbBl: "AWB-00000471",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0471",
    quantity: 1607,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-07T10:48:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0472",
    awbBl: "AWB-00000472",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0472",
    quantity: 1624,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-12T13:00:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0473",
    awbBl: "AWB-00000473",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0473",
    quantity: 1641,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-17T16:11:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0474",
    awbBl: "AWB-00000474",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0474",
    quantity: 1658,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-22T19:22:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0475",
    awbBl: "AWB-00000475",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0475",
    quantity: 1675,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-27T22:33:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0476",
    awbBl: "AWB-00000476",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0476",
    quantity: 1692,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-05T02:44:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0477",
    awbBl: "AWB-00000477",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0477",
    quantity: 1709,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-10T05:55:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0478",
    awbBl: "AWB-00000478",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0478",
    quantity: 1726,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-15T08:07:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0479",
    awbBl: "AWB-00000479",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0479",
    quantity: 1743,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-20T11:18:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0480",
    awbBl: "AWB-00000480",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0480",
    quantity: 1760,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-25T14:29:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0481",
    awbBl: "AWB-00000481",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0481",
    quantity: 1777,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-03T17:40:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0482",
    awbBl: "AWB-00000482",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0482",
    quantity: 1794,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-08T20:51:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0483",
    awbBl: "AWB-00000483",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0483",
    quantity: 1811,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-13T00:03:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0484",
    awbBl: "AWB-00000484",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0484",
    quantity: 1828,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-18T03:14:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0485",
    awbBl: "AWB-00000485",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0485",
    quantity: 1845,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-23T06:25:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0486",
    awbBl: "AWB-00000486",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0486",
    quantity: 1862,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-01T09:36:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0487",
    awbBl: "AWB-00000487",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0487",
    quantity: 1879,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-06T12:47:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0488",
    awbBl: "AWB-00000488",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0488",
    quantity: 1896,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-11T15:58:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0489",
    awbBl: "AWB-00000489",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0489",
    quantity: 1913,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-16T18:10:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0490",
    awbBl: "AWB-00000490",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0490",
    quantity: 1930,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-21T21:21:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0491",
    awbBl: "AWB-00000491",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0491",
    quantity: 1947,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-26T01:32:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0492",
    awbBl: "AWB-00000492",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0492",
    quantity: 1964,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-04T04:43:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0493",
    awbBl: "AWB-00000493",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0493",
    quantity: 1981,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-09T07:54:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0494",
    awbBl: "AWB-00000494",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0494",
    quantity: 1998,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-14T10:06:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0495",
    awbBl: "AWB-00000495",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0495",
    quantity: 2015,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-19T13:17:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0496",
    awbBl: "AWB-00000496",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0496",
    quantity: 2032,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-24T16:28:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0497",
    awbBl: "AWB-00000497",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0497",
    quantity: 2049,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-02T19:39:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0498",
    awbBl: "AWB-00000498",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0498",
    quantity: 2066,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-07T22:50:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0499",
    awbBl: "AWB-00000499",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0499",
    quantity: 2083,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-12T02:02:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0500",
    awbBl: "AWB-00000500",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0500",
    quantity: 2100,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-17T05:13:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0501",
    awbBl: "AWB-00000501",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0501",
    quantity: 2117,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-12-22T08:24:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0502",
    awbBl: "AWB-00000502",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0502",
    quantity: 2134,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-01-27T11:35:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0503",
    awbBl: "AWB-00000503",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0503",
    quantity: 2151,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-02-05T14:46:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0504",
    awbBl: "AWB-00000504",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0504",
    quantity: 2168,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-03-10T17:57:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0505",
    awbBl: "AWB-00000505",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0505",
    quantity: 2185,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-04-15T20:09:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0506",
    awbBl: "AWB-00000506",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0506",
    quantity: 2202,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-05-20T00:20:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0507",
    awbBl: "AWB-00000507",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0507",
    quantity: 2219,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-06-25T03:31:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0508",
    awbBl: "AWB-00000508",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0508",
    quantity: 2236,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-07-03T06:42:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0509",
    awbBl: "AWB-00000509",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0509",
    quantity: 2253,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-08-08T09:53:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0510",
    awbBl: "AWB-00000510",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0510",
    quantity: 2270,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-09-13T12:05:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0511",
    awbBl: "AWB-00000511",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0511",
    quantity: 2287,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-10-18T15:16:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0512",
    awbBl: "AWB-00000512",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0512",
    quantity: 2304,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-11-23T18:27:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0513",
    awbBl: "AWB-00000513",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0513",
    quantity: 2321,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-12-01T21:38:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0514",
    awbBl: "AWB-00000514",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0514",
    quantity: 2338,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-01-06T01:49:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0515",
    awbBl: "AWB-00000515",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0515",
    quantity: 2355,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-02-11T04:01:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0516",
    awbBl: "AWB-00000516",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0516",
    quantity: 2372,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-03-16T07:12:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0517",
    awbBl: "AWB-00000517",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0517",
    quantity: 2389,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-04-21T10:23:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0518",
    awbBl: "AWB-00000518",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0518",
    quantity: 2406,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-05-26T13:34:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0519",
    awbBl: "AWB-00000519",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0519",
    quantity: 2423,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-06-04T16:45:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0520",
    awbBl: "AWB-00000520",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0520",
    quantity: 2440,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-07-09T19:56:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0521",
    awbBl: "AWB-00000521",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0521",
    quantity: 2457,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-08-14T22:08:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0522",
    awbBl: "AWB-00000522",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0522",
    quantity: 2474,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-09-19T02:19:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0523",
    awbBl: "AWB-00000523",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0523",
    quantity: 2491,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-10-24T05:30:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0524",
    awbBl: "AWB-00000524",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0524",
    quantity: 2508,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-11-02T08:41:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0525",
    awbBl: "AWB-00000525",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0525",
    quantity: 2525,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-12-07T11:52:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0526",
    awbBl: "AWB-00000526",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0526",
    quantity: 2542,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-01-12T14:04:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0527",
    awbBl: "AWB-00000527",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0527",
    quantity: 2559,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-02-17T17:15:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0528",
    awbBl: "AWB-00000528",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0528",
    quantity: 2576,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-03-22T20:26:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0529",
    awbBl: "AWB-00000529",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0529",
    quantity: 2593,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-04-27T00:37:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0530",
    awbBl: "AWB-00000530",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0530",
    quantity: 2610,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-05-05T03:48:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0531",
    awbBl: "AWB-00000531",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0531",
    quantity: 2627,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-06-10T06:00:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0532",
    awbBl: "AWB-00000532",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0532",
    quantity: 2644,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-07-15T09:11:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0533",
    awbBl: "AWB-00000533",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0533",
    quantity: 2661,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-08-20T12:22:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0534",
    awbBl: "AWB-00000534",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0534",
    quantity: 2678,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-09-25T15:33:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0535",
    awbBl: "AWB-00000535",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0535",
    quantity: 2695,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-10-03T18:44:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0536",
    awbBl: "AWB-00000536",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0536",
    quantity: 2712,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-11-08T21:55:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0537",
    awbBl: "AWB-00000537",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0537",
    quantity: 2729,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-12-13T01:07:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0538",
    awbBl: "AWB-00000538",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0538",
    quantity: 2746,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-01-18T04:18:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0539",
    awbBl: "AWB-00000539",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0539",
    quantity: 2763,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-02-23T07:29:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0540",
    awbBl: "AWB-00000540",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0540",
    quantity: 2780,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-03-01T10:40:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0541",
    awbBl: "AWB-00000541",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0541",
    quantity: 2797,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-04-06T13:51:00Z",
    carrier: "Apex Cold Chain",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0542",
    awbBl: "AWB-00000542",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0542",
    quantity: 2814,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-05-11T16:03:00Z",
    carrier: "Mercury Air Cargo",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0543",
    awbBl: "AWB-00000543",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0543",
    quantity: 2831,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-06-16T19:14:00Z",
    carrier: "PharmaTransit Global",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0544",
    awbBl: "AWB-00000544",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0544",
    quantity: 2848,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-07-21T22:25:00Z",
    carrier: "Polar Bridge Logistics",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0545",
    awbBl: "AWB-00000545",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0545",
    quantity: 2865,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-08-26T02:36:00Z",
    carrier: "Northlane Freight",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0546",
    awbBl: "AWB-00000546",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0546",
    quantity: 2882,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-09-04T05:47:00Z",
    carrier: "Apex Cold Chain",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0547",
    awbBl: "AWB-00000547",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0547",
    quantity: 2899,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-10-09T08:58:00Z",
    carrier: "Mercury Air Cargo",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0548",
    awbBl: "AWB-00000548",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0548",
    quantity: 2916,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-11-14T11:10:00Z",
    carrier: "PharmaTransit Global",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0549",
    awbBl: "AWB-00000549",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0549",
    quantity: 2933,
    unit: "shipper",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-12-19T14:21:00Z",
    carrier: "Polar Bridge Logistics",
    status: "RECEIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0550",
    awbBl: "AWB-00000550",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0550",
    quantity: 2950,
    unit: "vial",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-01-24T17:32:00Z",
    carrier: "Northlane Freight",
    status: "QUARANTINE",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0551",
    awbBl: "AWB-00000551",
    product: "Amoxicillin 500mg Capsules",
    lot: "LOT-R2-0551",
    quantity: 2967,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Mexico City",
    destinationPort: "DEHAM",
    eta: "2026-02-02T20:43:00Z",
    carrier: "Apex Cold Chain",
    status: "ARRIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0552",
    awbBl: "AWB-00000552",
    product: "Insulin Glargine Pens",
    lot: "LOT-R2-0552",
    quantity: 2984,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Houston",
    destinationPort: "INBOM",
    eta: "2026-03-07T00:54:00Z",
    carrier: "Mercury Air Cargo",
    status: "DOCS_HOLD",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0553",
    awbBl: "AWB-00000553",
    product: "Monoclonal Antibody Vials",
    lot: "LOT-R2-0553",
    quantity: 3001,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Hamburg",
    destinationPort: "BRSSZ",
    eta: "2026-04-12T03:06:00Z",
    carrier: "PharmaTransit Global",
    status: "RECEIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0554",
    awbBl: "AWB-00000554",
    product: "Oncology Lyophilized Kit",
    lot: "LOT-R2-0554",
    quantity: 3018,
    unit: "carton",
    tempProfile: "2C-8C",
    origin: "Mumbai",
    destinationPort: "IEORK",
    eta: "2026-05-17T06:17:00Z",
    carrier: "Polar Bridge Logistics",
    status: "QUARANTINE",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0555",
    awbBl: "AWB-00000555",
    product: "mRNA Vaccine Bulk",
    lot: "LOT-R2-0555",
    quantity: 3035,
    unit: "shipper",
    tempProfile: "-20C",
    origin: "Sao Paulo",
    destinationPort: "KRPUS",
    eta: "2026-06-22T09:28:00Z",
    carrier: "Northlane Freight",
    status: "ARRIVED",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0556",
    awbBl: "AWB-00000556",
    product: "Sterile Saline Ampoules",
    lot: "LOT-R2-0556",
    quantity: 3052,
    unit: "vial",
    tempProfile: "2C-8C",
    origin: "Dublin",
    destinationPort: "SGSIN",
    eta: "2026-07-27T12:39:00Z",
    carrier: "Apex Cold Chain",
    status: "DOCS_HOLD",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0557",
    awbBl: "AWB-00000557",
    product: "Heparin Sodium Injection",
    lot: "LOT-R2-0557",
    quantity: 3069,
    unit: "carton",
    tempProfile: "15C-25C",
    origin: "Busan",
    destinationPort: "MXMEX",
    eta: "2026-08-05T15:50:00Z",
    carrier: "Mercury Air Cargo",
    status: "RECEIVED",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0558",
    awbBl: "AWB-00000558",
    product: "Antiviral Suspension",
    lot: "LOT-R2-0558",
    quantity: 3086,
    unit: "shipper",
    tempProfile: "2C-8C",
    origin: "Singapore",
    destinationPort: "MXVER",
    eta: "2026-09-10T18:02:00Z",
    carrier: "PharmaTransit Global",
    status: "QUARANTINE",
    laneRisk: "high",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0559",
    awbBl: "AWB-00000559",
    product: "Cold-Chain Diagnostics Cartridge",
    lot: "LOT-R2-0559",
    quantity: 3103,
    unit: "vial",
    tempProfile: "15C-25C",
    origin: "Zurich",
    destinationPort: "USLAX",
    eta: "2026-10-15T21:13:00Z",
    carrier: "Polar Bridge Logistics",
    status: "ARRIVED",
    laneRisk: "low",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  },
  {
    id: "manifest-0560",
    awbBl: "AWB-00000560",
    product: "Critical Care Infusion Set",
    lot: "LOT-R2-0560",
    quantity: 3120,
    unit: "carton",
    tempProfile: "-20C",
    origin: "Tokyo",
    destinationPort: "USIAH",
    eta: "2026-11-20T01:24:00Z",
    carrier: "Northlane Freight",
    status: "DOCS_HOLD",
    laneRisk: "medium",
    notes: [
      "Manifest linked to customs packet and receiving lot ledger.",
      "Requires deterministic gate evaluation before inventory posting."
    ]
  }
];
