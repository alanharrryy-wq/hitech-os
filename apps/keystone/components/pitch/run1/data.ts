import type {
  FoundationLotProfile,
  Incoterm,
  InventoryFoundationFields,
  RbacMatrixRow,
  SupplierProfile,
  TemperatureExcursionRecord,
  VaultDocumentDefinition
} from "./types";

export const FOUNDATION_DEFAULT_FIELDS: InventoryFoundationFields = {
  sku: "SKU-BASE-0001",
  lot: "LOT-FOUND-001",
  batch: "BATCH-FOUND-001",
  barcode: "7501234500012",
  supplierCode: "SUP-MX-0001",
  incoterm: "DAP",
  temperatureProfile: "2C-8C",
  storageCondition: "Cold Room A"
};

export const FOUNDATION_RBAC_ROWS: readonly RbacMatrixRow[] = [
  {
    role: "operator",
    displayName: "Warehouse Operator",
    defaultGate: "review",
    tooltip:
      "Executes receiving and putaway. Cannot clear critical compliance holds without admin sign-off.",
    capabilities: [
      {
        id: "receive.shipment",
        label: "Receive shipment",
        domain: "receiving",
        neededDocuments: ["doc-commercial-invoice", "doc-packing-list", "doc-coa"],
        reason: "Requires customs pack + CoA before posting inventory."
      },
      {
        id: "scan.sku",
        label: "Scan SKU/Lot/Batch",
        domain: "receiving",
        neededDocuments: ["doc-coa", "doc-temperature-report"],
        reason: "Traceability chain needs compliant lot metadata and cold-chain evidence."
      },
      {
        id: "set.quarantine",
        label: "Set quarantine",
        domain: "quality",
        neededDocuments: ["doc-temperature-report", "doc-import-permit"],
        reason: "Excursions and import permit gaps require temporary isolation."
      }
    ]
  },
  {
    role: "admin",
    displayName: "Control Room Admin",
    defaultGate: "open",
    tooltip:
      "Owns supplier onboarding and release decisioning. May override route only with full compliance pack.",
    capabilities: [
      {
        id: "approve.supplier",
        label: "Approve supplier",
        domain: "release",
        neededDocuments: ["doc-certificate-origin", "doc-hs-classification", "doc-import-permit"],
        reason: "Supplier activation requires customs identity + regulatory entitlement."
      },
      {
        id: "release.inventory",
        label: "Release inventory",
        domain: "release",
        neededDocuments: ["doc-coa", "doc-temperature-report", "doc-commercial-invoice"],
        reason: "QA and finance evidence must be present before release to available stock."
      },
      {
        id: "assign.deviation",
        label: "Assign deviation",
        domain: "quality",
        neededDocuments: ["doc-temperature-report"],
        reason: "Deviation workflow anchors to objective temperature data."
      }
    ]
  },
  {
    role: "auditor",
    displayName: "Compliance Auditor",
    defaultGate: "open",
    tooltip:
      "Read-only role for evidence review. Can issue findings but cannot mutate receiving state.",
    capabilities: [
      {
        id: "view.vault",
        label: "View vault evidence",
        domain: "vault",
        neededDocuments: ["doc-coa", "doc-temperature-report", "doc-import-permit"],
        reason: "Audit trail requires full visibility across quality and customs docs."
      },
      {
        id: "download.audit-pack",
        label: "Download audit pack",
        domain: "vault",
        neededDocuments: ["doc-commercial-invoice", "doc-packing-list", "doc-certificate-origin"],
        reason: "Outbound package must include core shipping and provenance records."
      },
      {
        id: "publish.finding",
        label: "Publish finding",
        domain: "quality",
        neededDocuments: ["doc-temperature-report"],
        reason: "Finding references monitored chain-of-custody events."
      }
    ]
  }
];

export const FOUNDATION_INCOTERM_RISK: Readonly<Record<Incoterm, number>> = {
  EXW: 22,
  FCA: 18,
  CPT: 15,
  CIP: 14,
  DAP: 10,
  DDP: 8
};

export const FOUNDATION_SUPPLIERS: readonly SupplierProfile[] = [
  {
    code: "SUP-MX-0001",
    legalName: "SUP-MX-ALPHA",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 94,
    leadTimeDays: 6,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-12-14",
    tempExcursions90d: 0,
    notes: [
      "Primary domestic lane with bonded cold chain and 24h response SLA.",
      "CAPA backlog zero for last two quarterly audits."
    ]
  },
  {
    code: "SUP-US-0002",
    legalName: "SUP-US-BETA",
    lifecycle: "active",
    country: "United States",
    qaScore: 88,
    leadTimeDays: 9,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-09",
    tempExcursions90d: 1,
    notes: [
      "Cross-border GDP lane with customs pre-clearance.",
      "One moderate excursion closed with validated CAPA."
    ]
  },
  {
    code: "SUP-CN-0003",
    legalName: "SUP-CN-GAMMA",
    lifecycle: "blocked",
    country: "China",
    qaScore: 74,
    leadTimeDays: 18,
    route: "CHN->MEX",
    gmpLevel: "B",
    activeLots: 5,
    lastAuditDate: "2025-10-02",
    tempExcursions90d: 3,
    notes: [
      "Blocked pending corrective action on import permit mismatch.",
      "Escalated to compliance committee for route requalification."
    ]
  },
  {
    code: "SUP-IN-0004",
    legalName: "ApexSterile Biologics Lotline 4",
    lifecycle: "blocked",
    country: "India",
    qaScore: 72,
    leadTimeDays: 7,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-BR-0005",
    legalName: "HelixSource Biologics Lotline 5",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 73,
    leadTimeDays: 8,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IE-0006",
    legalName: "VertexAPI Biologics Lotline 6",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 74,
    leadTimeDays: 9,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-KR-0007",
    legalName: "LumenLabs Biologics Lotline 7",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 75,
    leadTimeDays: 10,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-SG-0008",
    legalName: "PolarisPharma Biologics Lotline 8",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 76,
    leadTimeDays: 11,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-CH-0009",
    legalName: "OncoCure Biologics Lotline 9",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 77,
    leadTimeDays: 12,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-JP-0010",
    legalName: "VitaChem Biologics Lotline 10",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 78,
    leadTimeDays: 13,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-MX-0011",
    legalName: "BioSyn Biologics Lotline 11",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 79,
    leadTimeDays: 14,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-US-0012",
    legalName: "NovaPharm Biologics Lotline 12",
    lifecycle: "active",
    country: "United States",
    qaScore: 80,
    leadTimeDays: 15,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-DE-0013",
    legalName: "CryoMed Biologics Lotline 13",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 81,
    leadTimeDays: 16,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IN-0014",
    legalName: "ApexSterile Biologics Lotline 14",
    lifecycle: "approved",
    country: "India",
    qaScore: 82,
    leadTimeDays: 17,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-BR-0015",
    legalName: "HelixSource Biologics Lotline 15",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 83,
    leadTimeDays: 18,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IE-0016",
    legalName: "VertexAPI Biologics Lotline 16",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 84,
    leadTimeDays: 3,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-KR-0017",
    legalName: "LumenLabs Biologics Lotline 17",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 85,
    leadTimeDays: 4,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-SG-0018",
    legalName: "PolarisPharma Biologics Lotline 18",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 86,
    leadTimeDays: 5,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-CH-0019",
    legalName: "OncoCure Biologics Lotline 19",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 87,
    leadTimeDays: 6,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-JP-0020",
    legalName: "VitaChem Biologics Lotline 20",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 88,
    leadTimeDays: 7,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-MX-0021",
    legalName: "BioSyn Biologics Lotline 21",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 89,
    leadTimeDays: 8,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-US-0022",
    legalName: "NovaPharm Biologics Lotline 22",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 90,
    leadTimeDays: 9,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-DE-0023",
    legalName: "CryoMed Biologics Lotline 23",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 91,
    leadTimeDays: 10,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IN-0024",
    legalName: "ApexSterile Biologics Lotline 24",
    lifecycle: "active",
    country: "India",
    qaScore: 92,
    leadTimeDays: 11,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-BR-0025",
    legalName: "HelixSource Biologics Lotline 25",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 93,
    leadTimeDays: 12,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IE-0026",
    legalName: "VertexAPI Biologics Lotline 26",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 94,
    leadTimeDays: 13,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-KR-0027",
    legalName: "LumenLabs Biologics Lotline 27",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 95,
    leadTimeDays: 14,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-SG-0028",
    legalName: "PolarisPharma Biologics Lotline 28",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 68,
    leadTimeDays: 15,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-CH-0029",
    legalName: "OncoCure Biologics Lotline 29",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 69,
    leadTimeDays: 16,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-JP-0030",
    legalName: "VitaChem Biologics Lotline 30",
    lifecycle: "active",
    country: "Japan",
    qaScore: 70,
    leadTimeDays: 17,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-MX-0031",
    legalName: "BioSyn Biologics Lotline 31",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 71,
    leadTimeDays: 18,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-US-0032",
    legalName: "NovaPharm Biologics Lotline 32",
    lifecycle: "approved",
    country: "United States",
    qaScore: 72,
    leadTimeDays: 3,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-DE-0033",
    legalName: "CryoMed Biologics Lotline 33",
    lifecycle: "active",
    country: "Germany",
    qaScore: 73,
    leadTimeDays: 4,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IN-0034",
    legalName: "ApexSterile Biologics Lotline 34",
    lifecycle: "blocked",
    country: "India",
    qaScore: 74,
    leadTimeDays: 5,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-BR-0035",
    legalName: "HelixSource Biologics Lotline 35",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 75,
    leadTimeDays: 6,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IE-0036",
    legalName: "VertexAPI Biologics Lotline 36",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 76,
    leadTimeDays: 7,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-KR-0037",
    legalName: "LumenLabs Biologics Lotline 37",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 77,
    leadTimeDays: 8,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-SG-0038",
    legalName: "PolarisPharma Biologics Lotline 38",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 78,
    leadTimeDays: 9,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-CH-0039",
    legalName: "OncoCure Biologics Lotline 39",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 79,
    leadTimeDays: 10,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-JP-0040",
    legalName: "VitaChem Biologics Lotline 40",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 80,
    leadTimeDays: 11,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-MX-0041",
    legalName: "BioSyn Biologics Lotline 41",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 81,
    leadTimeDays: 12,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-US-0042",
    legalName: "NovaPharm Biologics Lotline 42",
    lifecycle: "active",
    country: "United States",
    qaScore: 82,
    leadTimeDays: 13,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-DE-0043",
    legalName: "CryoMed Biologics Lotline 43",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 83,
    leadTimeDays: 14,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IN-0044",
    legalName: "ApexSterile Biologics Lotline 44",
    lifecycle: "approved",
    country: "India",
    qaScore: 84,
    leadTimeDays: 15,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-BR-0045",
    legalName: "HelixSource Biologics Lotline 45",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 85,
    leadTimeDays: 16,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IE-0046",
    legalName: "VertexAPI Biologics Lotline 46",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 86,
    leadTimeDays: 17,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-KR-0047",
    legalName: "LumenLabs Biologics Lotline 47",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 87,
    leadTimeDays: 18,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-SG-0048",
    legalName: "PolarisPharma Biologics Lotline 48",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 88,
    leadTimeDays: 3,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-CH-0049",
    legalName: "OncoCure Biologics Lotline 49",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 89,
    leadTimeDays: 4,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-JP-0050",
    legalName: "VitaChem Biologics Lotline 50",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 90,
    leadTimeDays: 5,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-MX-0051",
    legalName: "BioSyn Biologics Lotline 51",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 91,
    leadTimeDays: 6,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-US-0052",
    legalName: "NovaPharm Biologics Lotline 52",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 92,
    leadTimeDays: 7,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-DE-0053",
    legalName: "CryoMed Biologics Lotline 53",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 93,
    leadTimeDays: 8,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IN-0054",
    legalName: "ApexSterile Biologics Lotline 54",
    lifecycle: "active",
    country: "India",
    qaScore: 94,
    leadTimeDays: 9,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-BR-0055",
    legalName: "HelixSource Biologics Lotline 55",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 95,
    leadTimeDays: 10,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IE-0056",
    legalName: "VertexAPI Biologics Lotline 56",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 68,
    leadTimeDays: 11,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-KR-0057",
    legalName: "LumenLabs Biologics Lotline 57",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 69,
    leadTimeDays: 12,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-SG-0058",
    legalName: "PolarisPharma Biologics Lotline 58",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 70,
    leadTimeDays: 13,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-CH-0059",
    legalName: "OncoCure Biologics Lotline 59",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 71,
    leadTimeDays: 14,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-JP-0060",
    legalName: "VitaChem Biologics Lotline 60",
    lifecycle: "active",
    country: "Japan",
    qaScore: 72,
    leadTimeDays: 15,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-MX-0061",
    legalName: "BioSyn Biologics Lotline 61",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 73,
    leadTimeDays: 16,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-US-0062",
    legalName: "NovaPharm Biologics Lotline 62",
    lifecycle: "approved",
    country: "United States",
    qaScore: 74,
    leadTimeDays: 17,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-DE-0063",
    legalName: "CryoMed Biologics Lotline 63",
    lifecycle: "active",
    country: "Germany",
    qaScore: 75,
    leadTimeDays: 18,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IN-0064",
    legalName: "ApexSterile Biologics Lotline 64",
    lifecycle: "blocked",
    country: "India",
    qaScore: 76,
    leadTimeDays: 3,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-BR-0065",
    legalName: "HelixSource Biologics Lotline 65",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 77,
    leadTimeDays: 4,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IE-0066",
    legalName: "VertexAPI Biologics Lotline 66",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 78,
    leadTimeDays: 5,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-KR-0067",
    legalName: "LumenLabs Biologics Lotline 67",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 79,
    leadTimeDays: 6,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-SG-0068",
    legalName: "PolarisPharma Biologics Lotline 68",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 80,
    leadTimeDays: 7,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-CH-0069",
    legalName: "OncoCure Biologics Lotline 69",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 81,
    leadTimeDays: 8,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-JP-0070",
    legalName: "VitaChem Biologics Lotline 70",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 82,
    leadTimeDays: 9,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-MX-0071",
    legalName: "BioSyn Biologics Lotline 71",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 83,
    leadTimeDays: 10,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-US-0072",
    legalName: "NovaPharm Biologics Lotline 72",
    lifecycle: "active",
    country: "United States",
    qaScore: 84,
    leadTimeDays: 11,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-DE-0073",
    legalName: "CryoMed Biologics Lotline 73",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 85,
    leadTimeDays: 12,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IN-0074",
    legalName: "ApexSterile Biologics Lotline 74",
    lifecycle: "approved",
    country: "India",
    qaScore: 86,
    leadTimeDays: 13,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-BR-0075",
    legalName: "HelixSource Biologics Lotline 75",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 87,
    leadTimeDays: 14,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IE-0076",
    legalName: "VertexAPI Biologics Lotline 76",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 88,
    leadTimeDays: 15,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-KR-0077",
    legalName: "LumenLabs Biologics Lotline 77",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 89,
    leadTimeDays: 16,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-SG-0078",
    legalName: "PolarisPharma Biologics Lotline 78",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 90,
    leadTimeDays: 17,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-CH-0079",
    legalName: "OncoCure Biologics Lotline 79",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 91,
    leadTimeDays: 18,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-JP-0080",
    legalName: "VitaChem Biologics Lotline 80",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 92,
    leadTimeDays: 3,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-MX-0081",
    legalName: "BioSyn Biologics Lotline 81",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 93,
    leadTimeDays: 4,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-US-0082",
    legalName: "NovaPharm Biologics Lotline 82",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 94,
    leadTimeDays: 5,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-DE-0083",
    legalName: "CryoMed Biologics Lotline 83",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 95,
    leadTimeDays: 6,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IN-0084",
    legalName: "ApexSterile Biologics Lotline 84",
    lifecycle: "active",
    country: "India",
    qaScore: 68,
    leadTimeDays: 7,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-BR-0085",
    legalName: "HelixSource Biologics Lotline 85",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 69,
    leadTimeDays: 8,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IE-0086",
    legalName: "VertexAPI Biologics Lotline 86",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 70,
    leadTimeDays: 9,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-KR-0087",
    legalName: "LumenLabs Biologics Lotline 87",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 71,
    leadTimeDays: 10,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-SG-0088",
    legalName: "PolarisPharma Biologics Lotline 88",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 72,
    leadTimeDays: 11,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-CH-0089",
    legalName: "OncoCure Biologics Lotline 89",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 73,
    leadTimeDays: 12,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-JP-0090",
    legalName: "VitaChem Biologics Lotline 90",
    lifecycle: "active",
    country: "Japan",
    qaScore: 74,
    leadTimeDays: 13,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-MX-0091",
    legalName: "BioSyn Biologics Lotline 91",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 75,
    leadTimeDays: 14,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-US-0092",
    legalName: "NovaPharm Biologics Lotline 92",
    lifecycle: "approved",
    country: "United States",
    qaScore: 76,
    leadTimeDays: 15,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-DE-0093",
    legalName: "CryoMed Biologics Lotline 93",
    lifecycle: "active",
    country: "Germany",
    qaScore: 77,
    leadTimeDays: 16,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IN-0094",
    legalName: "ApexSterile Biologics Lotline 94",
    lifecycle: "blocked",
    country: "India",
    qaScore: 78,
    leadTimeDays: 17,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-BR-0095",
    legalName: "HelixSource Biologics Lotline 95",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 79,
    leadTimeDays: 18,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IE-0096",
    legalName: "VertexAPI Biologics Lotline 96",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 80,
    leadTimeDays: 3,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-KR-0097",
    legalName: "LumenLabs Biologics Lotline 97",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 81,
    leadTimeDays: 4,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-SG-0098",
    legalName: "PolarisPharma Biologics Lotline 98",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 82,
    leadTimeDays: 5,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-CH-0099",
    legalName: "OncoCure Biologics Lotline 99",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 83,
    leadTimeDays: 6,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-JP-0100",
    legalName: "VitaChem Biologics Lotline 100",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 84,
    leadTimeDays: 7,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-MX-0101",
    legalName: "BioSyn Biologics Lotline 101",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 85,
    leadTimeDays: 8,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-US-0102",
    legalName: "NovaPharm Biologics Lotline 102",
    lifecycle: "active",
    country: "United States",
    qaScore: 86,
    leadTimeDays: 9,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-DE-0103",
    legalName: "CryoMed Biologics Lotline 103",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 87,
    leadTimeDays: 10,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IN-0104",
    legalName: "ApexSterile Biologics Lotline 104",
    lifecycle: "approved",
    country: "India",
    qaScore: 88,
    leadTimeDays: 11,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-BR-0105",
    legalName: "HelixSource Biologics Lotline 105",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 89,
    leadTimeDays: 12,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IE-0106",
    legalName: "VertexAPI Biologics Lotline 106",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 90,
    leadTimeDays: 13,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-KR-0107",
    legalName: "LumenLabs Biologics Lotline 107",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 91,
    leadTimeDays: 14,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-SG-0108",
    legalName: "PolarisPharma Biologics Lotline 108",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 92,
    leadTimeDays: 15,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-CH-0109",
    legalName: "OncoCure Biologics Lotline 109",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 93,
    leadTimeDays: 16,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-JP-0110",
    legalName: "VitaChem Biologics Lotline 110",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 94,
    leadTimeDays: 17,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-MX-0111",
    legalName: "BioSyn Biologics Lotline 111",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 95,
    leadTimeDays: 18,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-US-0112",
    legalName: "NovaPharm Biologics Lotline 112",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 68,
    leadTimeDays: 3,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-DE-0113",
    legalName: "CryoMed Biologics Lotline 113",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 69,
    leadTimeDays: 4,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IN-0114",
    legalName: "ApexSterile Biologics Lotline 114",
    lifecycle: "active",
    country: "India",
    qaScore: 70,
    leadTimeDays: 5,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-BR-0115",
    legalName: "HelixSource Biologics Lotline 115",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 71,
    leadTimeDays: 6,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IE-0116",
    legalName: "VertexAPI Biologics Lotline 116",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 72,
    leadTimeDays: 7,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-KR-0117",
    legalName: "LumenLabs Biologics Lotline 117",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 73,
    leadTimeDays: 8,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-SG-0118",
    legalName: "PolarisPharma Biologics Lotline 118",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 74,
    leadTimeDays: 9,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-CH-0119",
    legalName: "OncoCure Biologics Lotline 119",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 75,
    leadTimeDays: 10,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-JP-0120",
    legalName: "VitaChem Biologics Lotline 120",
    lifecycle: "active",
    country: "Japan",
    qaScore: 76,
    leadTimeDays: 11,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-MX-0121",
    legalName: "BioSyn Biologics Lotline 121",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 77,
    leadTimeDays: 12,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-US-0122",
    legalName: "NovaPharm Biologics Lotline 122",
    lifecycle: "approved",
    country: "United States",
    qaScore: 78,
    leadTimeDays: 13,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-DE-0123",
    legalName: "CryoMed Biologics Lotline 123",
    lifecycle: "active",
    country: "Germany",
    qaScore: 79,
    leadTimeDays: 14,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IN-0124",
    legalName: "ApexSterile Biologics Lotline 124",
    lifecycle: "blocked",
    country: "India",
    qaScore: 80,
    leadTimeDays: 15,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-BR-0125",
    legalName: "HelixSource Biologics Lotline 125",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 81,
    leadTimeDays: 16,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IE-0126",
    legalName: "VertexAPI Biologics Lotline 126",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 82,
    leadTimeDays: 17,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-KR-0127",
    legalName: "LumenLabs Biologics Lotline 127",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 83,
    leadTimeDays: 18,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-SG-0128",
    legalName: "PolarisPharma Biologics Lotline 128",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 84,
    leadTimeDays: 3,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-CH-0129",
    legalName: "OncoCure Biologics Lotline 129",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 85,
    leadTimeDays: 4,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-JP-0130",
    legalName: "VitaChem Biologics Lotline 130",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 86,
    leadTimeDays: 5,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-MX-0131",
    legalName: "BioSyn Biologics Lotline 131",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 87,
    leadTimeDays: 6,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-US-0132",
    legalName: "NovaPharm Biologics Lotline 132",
    lifecycle: "active",
    country: "United States",
    qaScore: 88,
    leadTimeDays: 7,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-DE-0133",
    legalName: "CryoMed Biologics Lotline 133",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 89,
    leadTimeDays: 8,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IN-0134",
    legalName: "ApexSterile Biologics Lotline 134",
    lifecycle: "approved",
    country: "India",
    qaScore: 90,
    leadTimeDays: 9,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-BR-0135",
    legalName: "HelixSource Biologics Lotline 135",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 91,
    leadTimeDays: 10,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IE-0136",
    legalName: "VertexAPI Biologics Lotline 136",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 92,
    leadTimeDays: 11,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-KR-0137",
    legalName: "LumenLabs Biologics Lotline 137",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 93,
    leadTimeDays: 12,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-SG-0138",
    legalName: "PolarisPharma Biologics Lotline 138",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 94,
    leadTimeDays: 13,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-CH-0139",
    legalName: "OncoCure Biologics Lotline 139",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 95,
    leadTimeDays: 14,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-JP-0140",
    legalName: "VitaChem Biologics Lotline 140",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 68,
    leadTimeDays: 15,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-MX-0141",
    legalName: "BioSyn Biologics Lotline 141",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 69,
    leadTimeDays: 16,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-US-0142",
    legalName: "NovaPharm Biologics Lotline 142",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 70,
    leadTimeDays: 17,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-DE-0143",
    legalName: "CryoMed Biologics Lotline 143",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 71,
    leadTimeDays: 18,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IN-0144",
    legalName: "ApexSterile Biologics Lotline 144",
    lifecycle: "active",
    country: "India",
    qaScore: 72,
    leadTimeDays: 3,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-BR-0145",
    legalName: "HelixSource Biologics Lotline 145",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 73,
    leadTimeDays: 4,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IE-0146",
    legalName: "VertexAPI Biologics Lotline 146",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 74,
    leadTimeDays: 5,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-KR-0147",
    legalName: "LumenLabs Biologics Lotline 147",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 75,
    leadTimeDays: 6,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-SG-0148",
    legalName: "PolarisPharma Biologics Lotline 148",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 76,
    leadTimeDays: 7,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-CH-0149",
    legalName: "OncoCure Biologics Lotline 149",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 77,
    leadTimeDays: 8,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-JP-0150",
    legalName: "VitaChem Biologics Lotline 150",
    lifecycle: "active",
    country: "Japan",
    qaScore: 78,
    leadTimeDays: 9,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-MX-0151",
    legalName: "BioSyn Biologics Lotline 151",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 79,
    leadTimeDays: 10,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-US-0152",
    legalName: "NovaPharm Biologics Lotline 152",
    lifecycle: "approved",
    country: "United States",
    qaScore: 80,
    leadTimeDays: 11,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-DE-0153",
    legalName: "CryoMed Biologics Lotline 153",
    lifecycle: "active",
    country: "Germany",
    qaScore: 81,
    leadTimeDays: 12,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IN-0154",
    legalName: "ApexSterile Biologics Lotline 154",
    lifecycle: "blocked",
    country: "India",
    qaScore: 82,
    leadTimeDays: 13,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-BR-0155",
    legalName: "HelixSource Biologics Lotline 155",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 83,
    leadTimeDays: 14,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IE-0156",
    legalName: "VertexAPI Biologics Lotline 156",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 84,
    leadTimeDays: 15,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-KR-0157",
    legalName: "LumenLabs Biologics Lotline 157",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 85,
    leadTimeDays: 16,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-SG-0158",
    legalName: "PolarisPharma Biologics Lotline 158",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 86,
    leadTimeDays: 17,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-CH-0159",
    legalName: "OncoCure Biologics Lotline 159",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 87,
    leadTimeDays: 18,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-JP-0160",
    legalName: "VitaChem Biologics Lotline 160",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 88,
    leadTimeDays: 3,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-MX-0161",
    legalName: "BioSyn Biologics Lotline 161",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 89,
    leadTimeDays: 4,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-US-0162",
    legalName: "NovaPharm Biologics Lotline 162",
    lifecycle: "active",
    country: "United States",
    qaScore: 90,
    leadTimeDays: 5,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-DE-0163",
    legalName: "CryoMed Biologics Lotline 163",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 91,
    leadTimeDays: 6,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IN-0164",
    legalName: "ApexSterile Biologics Lotline 164",
    lifecycle: "approved",
    country: "India",
    qaScore: 92,
    leadTimeDays: 7,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-BR-0165",
    legalName: "HelixSource Biologics Lotline 165",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 93,
    leadTimeDays: 8,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IE-0166",
    legalName: "VertexAPI Biologics Lotline 166",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 94,
    leadTimeDays: 9,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-KR-0167",
    legalName: "LumenLabs Biologics Lotline 167",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 95,
    leadTimeDays: 10,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-SG-0168",
    legalName: "PolarisPharma Biologics Lotline 168",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 68,
    leadTimeDays: 11,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-CH-0169",
    legalName: "OncoCure Biologics Lotline 169",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 69,
    leadTimeDays: 12,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-JP-0170",
    legalName: "VitaChem Biologics Lotline 170",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 70,
    leadTimeDays: 13,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-MX-0171",
    legalName: "BioSyn Biologics Lotline 171",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 71,
    leadTimeDays: 14,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-US-0172",
    legalName: "NovaPharm Biologics Lotline 172",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 72,
    leadTimeDays: 15,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-DE-0173",
    legalName: "CryoMed Biologics Lotline 173",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 73,
    leadTimeDays: 16,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IN-0174",
    legalName: "ApexSterile Biologics Lotline 174",
    lifecycle: "active",
    country: "India",
    qaScore: 74,
    leadTimeDays: 17,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-BR-0175",
    legalName: "HelixSource Biologics Lotline 175",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 75,
    leadTimeDays: 18,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IE-0176",
    legalName: "VertexAPI Biologics Lotline 176",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 76,
    leadTimeDays: 3,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-KR-0177",
    legalName: "LumenLabs Biologics Lotline 177",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 77,
    leadTimeDays: 4,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-SG-0178",
    legalName: "PolarisPharma Biologics Lotline 178",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 78,
    leadTimeDays: 5,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-CH-0179",
    legalName: "OncoCure Biologics Lotline 179",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 79,
    leadTimeDays: 6,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-JP-0180",
    legalName: "VitaChem Biologics Lotline 180",
    lifecycle: "active",
    country: "Japan",
    qaScore: 80,
    leadTimeDays: 7,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-MX-0181",
    legalName: "BioSyn Biologics Lotline 181",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 81,
    leadTimeDays: 8,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-US-0182",
    legalName: "NovaPharm Biologics Lotline 182",
    lifecycle: "approved",
    country: "United States",
    qaScore: 82,
    leadTimeDays: 9,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-DE-0183",
    legalName: "CryoMed Biologics Lotline 183",
    lifecycle: "active",
    country: "Germany",
    qaScore: 83,
    leadTimeDays: 10,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IN-0184",
    legalName: "ApexSterile Biologics Lotline 184",
    lifecycle: "blocked",
    country: "India",
    qaScore: 84,
    leadTimeDays: 11,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-BR-0185",
    legalName: "HelixSource Biologics Lotline 185",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 85,
    leadTimeDays: 12,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IE-0186",
    legalName: "VertexAPI Biologics Lotline 186",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 86,
    leadTimeDays: 13,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-KR-0187",
    legalName: "LumenLabs Biologics Lotline 187",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 87,
    leadTimeDays: 14,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-SG-0188",
    legalName: "PolarisPharma Biologics Lotline 188",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 88,
    leadTimeDays: 15,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-CH-0189",
    legalName: "OncoCure Biologics Lotline 189",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 89,
    leadTimeDays: 16,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-JP-0190",
    legalName: "VitaChem Biologics Lotline 190",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 90,
    leadTimeDays: 17,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-MX-0191",
    legalName: "BioSyn Biologics Lotline 191",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 91,
    leadTimeDays: 18,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-US-0192",
    legalName: "NovaPharm Biologics Lotline 192",
    lifecycle: "active",
    country: "United States",
    qaScore: 92,
    leadTimeDays: 3,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-DE-0193",
    legalName: "CryoMed Biologics Lotline 193",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 93,
    leadTimeDays: 4,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IN-0194",
    legalName: "ApexSterile Biologics Lotline 194",
    lifecycle: "approved",
    country: "India",
    qaScore: 94,
    leadTimeDays: 5,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-BR-0195",
    legalName: "HelixSource Biologics Lotline 195",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 95,
    leadTimeDays: 6,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IE-0196",
    legalName: "VertexAPI Biologics Lotline 196",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 68,
    leadTimeDays: 7,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-KR-0197",
    legalName: "LumenLabs Biologics Lotline 197",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 69,
    leadTimeDays: 8,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-SG-0198",
    legalName: "PolarisPharma Biologics Lotline 198",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 70,
    leadTimeDays: 9,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-CH-0199",
    legalName: "OncoCure Biologics Lotline 199",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 71,
    leadTimeDays: 10,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-JP-0200",
    legalName: "VitaChem Biologics Lotline 200",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 72,
    leadTimeDays: 11,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-MX-0201",
    legalName: "BioSyn Biologics Lotline 201",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 73,
    leadTimeDays: 12,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-US-0202",
    legalName: "NovaPharm Biologics Lotline 202",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 74,
    leadTimeDays: 13,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-DE-0203",
    legalName: "CryoMed Biologics Lotline 203",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 75,
    leadTimeDays: 14,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IN-0204",
    legalName: "ApexSterile Biologics Lotline 204",
    lifecycle: "active",
    country: "India",
    qaScore: 76,
    leadTimeDays: 15,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-BR-0205",
    legalName: "HelixSource Biologics Lotline 205",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 77,
    leadTimeDays: 16,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IE-0206",
    legalName: "VertexAPI Biologics Lotline 206",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 78,
    leadTimeDays: 17,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-KR-0207",
    legalName: "LumenLabs Biologics Lotline 207",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 79,
    leadTimeDays: 18,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-SG-0208",
    legalName: "PolarisPharma Biologics Lotline 208",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 80,
    leadTimeDays: 3,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-CH-0209",
    legalName: "OncoCure Biologics Lotline 209",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 81,
    leadTimeDays: 4,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-JP-0210",
    legalName: "VitaChem Biologics Lotline 210",
    lifecycle: "active",
    country: "Japan",
    qaScore: 82,
    leadTimeDays: 5,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-MX-0211",
    legalName: "BioSyn Biologics Lotline 211",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 83,
    leadTimeDays: 6,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-US-0212",
    legalName: "NovaPharm Biologics Lotline 212",
    lifecycle: "approved",
    country: "United States",
    qaScore: 84,
    leadTimeDays: 7,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-DE-0213",
    legalName: "CryoMed Biologics Lotline 213",
    lifecycle: "active",
    country: "Germany",
    qaScore: 85,
    leadTimeDays: 8,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IN-0214",
    legalName: "ApexSterile Biologics Lotline 214",
    lifecycle: "blocked",
    country: "India",
    qaScore: 86,
    leadTimeDays: 9,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-BR-0215",
    legalName: "HelixSource Biologics Lotline 215",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 87,
    leadTimeDays: 10,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IE-0216",
    legalName: "VertexAPI Biologics Lotline 216",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 88,
    leadTimeDays: 11,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-KR-0217",
    legalName: "LumenLabs Biologics Lotline 217",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 89,
    leadTimeDays: 12,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-SG-0218",
    legalName: "PolarisPharma Biologics Lotline 218",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 90,
    leadTimeDays: 13,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-CH-0219",
    legalName: "OncoCure Biologics Lotline 219",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 91,
    leadTimeDays: 14,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-JP-0220",
    legalName: "VitaChem Biologics Lotline 220",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 92,
    leadTimeDays: 15,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-MX-0221",
    legalName: "BioSyn Biologics Lotline 221",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 93,
    leadTimeDays: 16,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-US-0222",
    legalName: "NovaPharm Biologics Lotline 222",
    lifecycle: "active",
    country: "United States",
    qaScore: 94,
    leadTimeDays: 17,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-DE-0223",
    legalName: "CryoMed Biologics Lotline 223",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 95,
    leadTimeDays: 18,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IN-0224",
    legalName: "ApexSterile Biologics Lotline 224",
    lifecycle: "approved",
    country: "India",
    qaScore: 68,
    leadTimeDays: 3,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-BR-0225",
    legalName: "HelixSource Biologics Lotline 225",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 69,
    leadTimeDays: 4,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IE-0226",
    legalName: "VertexAPI Biologics Lotline 226",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 70,
    leadTimeDays: 5,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-KR-0227",
    legalName: "LumenLabs Biologics Lotline 227",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 71,
    leadTimeDays: 6,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-SG-0228",
    legalName: "PolarisPharma Biologics Lotline 228",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 72,
    leadTimeDays: 7,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-CH-0229",
    legalName: "OncoCure Biologics Lotline 229",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 73,
    leadTimeDays: 8,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-JP-0230",
    legalName: "VitaChem Biologics Lotline 230",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 74,
    leadTimeDays: 9,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-MX-0231",
    legalName: "BioSyn Biologics Lotline 231",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 75,
    leadTimeDays: 10,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-US-0232",
    legalName: "NovaPharm Biologics Lotline 232",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 76,
    leadTimeDays: 11,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-DE-0233",
    legalName: "CryoMed Biologics Lotline 233",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 77,
    leadTimeDays: 12,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IN-0234",
    legalName: "ApexSterile Biologics Lotline 234",
    lifecycle: "active",
    country: "India",
    qaScore: 78,
    leadTimeDays: 13,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-BR-0235",
    legalName: "HelixSource Biologics Lotline 235",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 79,
    leadTimeDays: 14,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IE-0236",
    legalName: "VertexAPI Biologics Lotline 236",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 80,
    leadTimeDays: 15,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-KR-0237",
    legalName: "LumenLabs Biologics Lotline 237",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 81,
    leadTimeDays: 16,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-SG-0238",
    legalName: "PolarisPharma Biologics Lotline 238",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 82,
    leadTimeDays: 17,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-CH-0239",
    legalName: "OncoCure Biologics Lotline 239",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 83,
    leadTimeDays: 18,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-JP-0240",
    legalName: "VitaChem Biologics Lotline 240",
    lifecycle: "active",
    country: "Japan",
    qaScore: 84,
    leadTimeDays: 3,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-MX-0241",
    legalName: "BioSyn Biologics Lotline 241",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 85,
    leadTimeDays: 4,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-US-0242",
    legalName: "NovaPharm Biologics Lotline 242",
    lifecycle: "approved",
    country: "United States",
    qaScore: 86,
    leadTimeDays: 5,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-DE-0243",
    legalName: "CryoMed Biologics Lotline 243",
    lifecycle: "active",
    country: "Germany",
    qaScore: 87,
    leadTimeDays: 6,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IN-0244",
    legalName: "ApexSterile Biologics Lotline 244",
    lifecycle: "blocked",
    country: "India",
    qaScore: 88,
    leadTimeDays: 7,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-BR-0245",
    legalName: "HelixSource Biologics Lotline 245",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 89,
    leadTimeDays: 8,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IE-0246",
    legalName: "VertexAPI Biologics Lotline 246",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 90,
    leadTimeDays: 9,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-KR-0247",
    legalName: "LumenLabs Biologics Lotline 247",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 91,
    leadTimeDays: 10,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-SG-0248",
    legalName: "PolarisPharma Biologics Lotline 248",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 92,
    leadTimeDays: 11,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-CH-0249",
    legalName: "OncoCure Biologics Lotline 249",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 93,
    leadTimeDays: 12,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-JP-0250",
    legalName: "VitaChem Biologics Lotline 250",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 94,
    leadTimeDays: 13,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-MX-0251",
    legalName: "BioSyn Biologics Lotline 251",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 95,
    leadTimeDays: 14,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-US-0252",
    legalName: "NovaPharm Biologics Lotline 252",
    lifecycle: "active",
    country: "United States",
    qaScore: 68,
    leadTimeDays: 15,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-DE-0253",
    legalName: "CryoMed Biologics Lotline 253",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 69,
    leadTimeDays: 16,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-IN-0254",
    legalName: "ApexSterile Biologics Lotline 254",
    lifecycle: "approved",
    country: "India",
    qaScore: 70,
    leadTimeDays: 17,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-BR-0255",
    legalName: "HelixSource Biologics Lotline 255",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 71,
    leadTimeDays: 18,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IE-0256",
    legalName: "VertexAPI Biologics Lotline 256",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 72,
    leadTimeDays: 3,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-KR-0257",
    legalName: "LumenLabs Biologics Lotline 257",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 73,
    leadTimeDays: 4,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-SG-0258",
    legalName: "PolarisPharma Biologics Lotline 258",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 74,
    leadTimeDays: 5,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-CH-0259",
    legalName: "OncoCure Biologics Lotline 259",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 75,
    leadTimeDays: 6,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-JP-0260",
    legalName: "VitaChem Biologics Lotline 260",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 76,
    leadTimeDays: 7,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-MX-0261",
    legalName: "BioSyn Biologics Lotline 261",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 77,
    leadTimeDays: 8,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-US-0262",
    legalName: "NovaPharm Biologics Lotline 262",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 78,
    leadTimeDays: 9,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-DE-0263",
    legalName: "CryoMed Biologics Lotline 263",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 79,
    leadTimeDays: 10,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-IN-0264",
    legalName: "ApexSterile Biologics Lotline 264",
    lifecycle: "active",
    country: "India",
    qaScore: 80,
    leadTimeDays: 11,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-BR-0265",
    legalName: "HelixSource Biologics Lotline 265",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 81,
    leadTimeDays: 12,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IE-0266",
    legalName: "VertexAPI Biologics Lotline 266",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 82,
    leadTimeDays: 13,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-KR-0267",
    legalName: "LumenLabs Biologics Lotline 267",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 83,
    leadTimeDays: 14,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-SG-0268",
    legalName: "PolarisPharma Biologics Lotline 268",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 84,
    leadTimeDays: 15,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-CH-0269",
    legalName: "OncoCure Biologics Lotline 269",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 85,
    leadTimeDays: 16,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-JP-0270",
    legalName: "VitaChem Biologics Lotline 270",
    lifecycle: "active",
    country: "Japan",
    qaScore: 86,
    leadTimeDays: 17,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-MX-0271",
    legalName: "BioSyn Biologics Lotline 271",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 87,
    leadTimeDays: 18,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-US-0272",
    legalName: "NovaPharm Biologics Lotline 272",
    lifecycle: "approved",
    country: "United States",
    qaScore: 88,
    leadTimeDays: 3,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-DE-0273",
    legalName: "CryoMed Biologics Lotline 273",
    lifecycle: "active",
    country: "Germany",
    qaScore: 89,
    leadTimeDays: 4,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-IN-0274",
    legalName: "ApexSterile Biologics Lotline 274",
    lifecycle: "blocked",
    country: "India",
    qaScore: 90,
    leadTimeDays: 5,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-BR-0275",
    legalName: "HelixSource Biologics Lotline 275",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 91,
    leadTimeDays: 6,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IE-0276",
    legalName: "VertexAPI Biologics Lotline 276",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 92,
    leadTimeDays: 7,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-KR-0277",
    legalName: "LumenLabs Biologics Lotline 277",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 93,
    leadTimeDays: 8,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-SG-0278",
    legalName: "PolarisPharma Biologics Lotline 278",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 94,
    leadTimeDays: 9,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-CH-0279",
    legalName: "OncoCure Biologics Lotline 279",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 95,
    leadTimeDays: 10,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-JP-0280",
    legalName: "VitaChem Biologics Lotline 280",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 68,
    leadTimeDays: 11,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-MX-0281",
    legalName: "BioSyn Biologics Lotline 281",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 69,
    leadTimeDays: 12,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-US-0282",
    legalName: "NovaPharm Biologics Lotline 282",
    lifecycle: "active",
    country: "United States",
    qaScore: 70,
    leadTimeDays: 13,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-DE-0283",
    legalName: "CryoMed Biologics Lotline 283",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 71,
    leadTimeDays: 14,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-IN-0284",
    legalName: "ApexSterile Biologics Lotline 284",
    lifecycle: "approved",
    country: "India",
    qaScore: 72,
    leadTimeDays: 15,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-BR-0285",
    legalName: "HelixSource Biologics Lotline 285",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 73,
    leadTimeDays: 16,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-19",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IE-0286",
    legalName: "VertexAPI Biologics Lotline 286",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 74,
    leadTimeDays: 17,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-22",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-KR-0287",
    legalName: "LumenLabs Biologics Lotline 287",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 75,
    leadTimeDays: 18,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-25",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-SG-0288",
    legalName: "PolarisPharma Biologics Lotline 288",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 76,
    leadTimeDays: 3,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-01",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-CH-0289",
    legalName: "OncoCure Biologics Lotline 289",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 77,
    leadTimeDays: 4,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-04",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-JP-0290",
    legalName: "VitaChem Biologics Lotline 290",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 78,
    leadTimeDays: 5,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-07",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-MX-0291",
    legalName: "BioSyn Biologics Lotline 291",
    lifecycle: "active",
    country: "Mexico",
    qaScore: 79,
    leadTimeDays: 6,
    route: "MEX->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-10",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-US-0292",
    legalName: "NovaPharm Biologics Lotline 292",
    lifecycle: "blocked",
    country: "United States",
    qaScore: 80,
    leadTimeDays: 7,
    route: "USA->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-13",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-DE-0293",
    legalName: "CryoMed Biologics Lotline 293",
    lifecycle: "approved",
    country: "Germany",
    qaScore: 81,
    leadTimeDays: 8,
    route: "DEU->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-16",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 81 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-IN-0294",
    legalName: "ApexSterile Biologics Lotline 294",
    lifecycle: "active",
    country: "India",
    qaScore: 82,
    leadTimeDays: 9,
    route: "IND->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-19",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 82 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-BR-0295",
    legalName: "HelixSource Biologics Lotline 295",
    lifecycle: "blocked",
    country: "Brazil",
    qaScore: 83,
    leadTimeDays: 10,
    route: "BRA->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-22",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 83 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IE-0296",
    legalName: "VertexAPI Biologics Lotline 296",
    lifecycle: "approved",
    country: "Ireland",
    qaScore: 84,
    leadTimeDays: 11,
    route: "IRL->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-25",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 84 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-KR-0297",
    legalName: "LumenLabs Biologics Lotline 297",
    lifecycle: "active",
    country: "South Korea",
    qaScore: 85,
    leadTimeDays: 12,
    route: "KOR->MEX",
    gmpLevel: "C",
    activeLots: 10,
    lastAuditDate: "2025-10-01",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 85 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-SG-0298",
    legalName: "PolarisPharma Biologics Lotline 298",
    lifecycle: "blocked",
    country: "Singapore",
    qaScore: 86,
    leadTimeDays: 13,
    route: "SGP->MEX",
    gmpLevel: "A",
    activeLots: 11,
    lastAuditDate: "2025-11-04",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 86 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-CH-0299",
    legalName: "OncoCure Biologics Lotline 299",
    lifecycle: "approved",
    country: "Switzerland",
    qaScore: 87,
    leadTimeDays: 14,
    route: "CHE->MEX",
    gmpLevel: "B",
    activeLots: 12,
    lastAuditDate: "2025-12-07",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 87 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-JP-0300",
    legalName: "VitaChem Biologics Lotline 300",
    lifecycle: "active",
    country: "Japan",
    qaScore: 88,
    leadTimeDays: 15,
    route: "JPN->MEX",
    gmpLevel: "C",
    activeLots: 13,
    lastAuditDate: "2025-01-10",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 88 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-MX-0301",
    legalName: "BioSyn Biologics Lotline 301",
    lifecycle: "blocked",
    country: "Mexico",
    qaScore: 89,
    leadTimeDays: 16,
    route: "MEX->MEX",
    gmpLevel: "A",
    activeLots: 14,
    lastAuditDate: "2025-02-13",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 89 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-US-0302",
    legalName: "NovaPharm Biologics Lotline 302",
    lifecycle: "approved",
    country: "United States",
    qaScore: 90,
    leadTimeDays: 17,
    route: "USA->MEX",
    gmpLevel: "B",
    activeLots: 15,
    lastAuditDate: "2025-03-16",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 90 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-DE-0303",
    legalName: "CryoMed Biologics Lotline 303",
    lifecycle: "active",
    country: "Germany",
    qaScore: 91,
    leadTimeDays: 18,
    route: "DEU->MEX",
    gmpLevel: "C",
    activeLots: 16,
    lastAuditDate: "2025-04-19",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 91 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-IN-0304",
    legalName: "ApexSterile Biologics Lotline 304",
    lifecycle: "blocked",
    country: "India",
    qaScore: 92,
    leadTimeDays: 3,
    route: "IND->MEX",
    gmpLevel: "A",
    activeLots: 17,
    lastAuditDate: "2025-05-22",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 92 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-BR-0305",
    legalName: "HelixSource Biologics Lotline 305",
    lifecycle: "approved",
    country: "Brazil",
    qaScore: 93,
    leadTimeDays: 4,
    route: "BRA->MEX",
    gmpLevel: "B",
    activeLots: 18,
    lastAuditDate: "2025-06-25",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 93 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-IE-0306",
    legalName: "VertexAPI Biologics Lotline 306",
    lifecycle: "active",
    country: "Ireland",
    qaScore: 94,
    leadTimeDays: 5,
    route: "IRL->MEX",
    gmpLevel: "C",
    activeLots: 19,
    lastAuditDate: "2025-07-01",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 94 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-KR-0307",
    legalName: "LumenLabs Biologics Lotline 307",
    lifecycle: "blocked",
    country: "South Korea",
    qaScore: 95,
    leadTimeDays: 6,
    route: "KOR->MEX",
    gmpLevel: "A",
    activeLots: 20,
    lastAuditDate: "2025-08-04",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 95 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-SG-0308",
    legalName: "PolarisPharma Biologics Lotline 308",
    lifecycle: "approved",
    country: "Singapore",
    qaScore: 68,
    leadTimeDays: 7,
    route: "SGP->MEX",
    gmpLevel: "B",
    activeLots: 21,
    lastAuditDate: "2025-09-07",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 68 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-CH-0309",
    legalName: "OncoCure Biologics Lotline 309",
    lifecycle: "active",
    country: "Switzerland",
    qaScore: 69,
    leadTimeDays: 8,
    route: "CHE->MEX",
    gmpLevel: "C",
    activeLots: 22,
    lastAuditDate: "2025-10-10",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 69 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-JP-0310",
    legalName: "VitaChem Biologics Lotline 310",
    lifecycle: "blocked",
    country: "Japan",
    qaScore: 70,
    leadTimeDays: 9,
    route: "JPN->MEX",
    gmpLevel: "A",
    activeLots: 23,
    lastAuditDate: "2025-11-13",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 70 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-MX-0311",
    legalName: "BioSyn Biologics Lotline 311",
    lifecycle: "approved",
    country: "Mexico",
    qaScore: 71,
    leadTimeDays: 10,
    route: "MEX->MEX",
    gmpLevel: "B",
    activeLots: 24,
    lastAuditDate: "2025-12-16",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for MEX->MEX with quarterly review cadence.",
      "QA score trend registered at 71 with CAPA protocol version 6."
    ]
  },
  {
    code: "SUP-US-0312",
    legalName: "NovaPharm Biologics Lotline 312",
    lifecycle: "active",
    country: "United States",
    qaScore: 72,
    leadTimeDays: 11,
    route: "USA->MEX",
    gmpLevel: "C",
    activeLots: 1,
    lastAuditDate: "2025-01-19",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for USA->MEX with quarterly review cadence.",
      "QA score trend registered at 72 with CAPA protocol version 7."
    ]
  },
  {
    code: "SUP-DE-0313",
    legalName: "CryoMed Biologics Lotline 313",
    lifecycle: "blocked",
    country: "Germany",
    qaScore: 73,
    leadTimeDays: 12,
    route: "DEU->MEX",
    gmpLevel: "A",
    activeLots: 2,
    lastAuditDate: "2025-02-22",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for DEU->MEX with quarterly review cadence.",
      "QA score trend registered at 73 with CAPA protocol version 8."
    ]
  },
  {
    code: "SUP-IN-0314",
    legalName: "ApexSterile Biologics Lotline 314",
    lifecycle: "approved",
    country: "India",
    qaScore: 74,
    leadTimeDays: 13,
    route: "IND->MEX",
    gmpLevel: "B",
    activeLots: 3,
    lastAuditDate: "2025-03-25",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for IND->MEX with quarterly review cadence.",
      "QA score trend registered at 74 with CAPA protocol version 9."
    ]
  },
  {
    code: "SUP-BR-0315",
    legalName: "HelixSource Biologics Lotline 315",
    lifecycle: "active",
    country: "Brazil",
    qaScore: 75,
    leadTimeDays: 14,
    route: "BRA->MEX",
    gmpLevel: "C",
    activeLots: 4,
    lastAuditDate: "2025-04-01",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for BRA->MEX with quarterly review cadence.",
      "QA score trend registered at 75 with CAPA protocol version 1."
    ]
  },
  {
    code: "SUP-IE-0316",
    legalName: "VertexAPI Biologics Lotline 316",
    lifecycle: "blocked",
    country: "Ireland",
    qaScore: 76,
    leadTimeDays: 15,
    route: "IRL->MEX",
    gmpLevel: "A",
    activeLots: 5,
    lastAuditDate: "2025-05-04",
    tempExcursions90d: 1,
    notes: [
      "GDP lane validated for IRL->MEX with quarterly review cadence.",
      "QA score trend registered at 76 with CAPA protocol version 2."
    ]
  },
  {
    code: "SUP-KR-0317",
    legalName: "LumenLabs Biologics Lotline 317",
    lifecycle: "approved",
    country: "South Korea",
    qaScore: 77,
    leadTimeDays: 16,
    route: "KOR->MEX",
    gmpLevel: "B",
    activeLots: 6,
    lastAuditDate: "2025-06-07",
    tempExcursions90d: 2,
    notes: [
      "GDP lane validated for KOR->MEX with quarterly review cadence.",
      "QA score trend registered at 77 with CAPA protocol version 3."
    ]
  },
  {
    code: "SUP-SG-0318",
    legalName: "PolarisPharma Biologics Lotline 318",
    lifecycle: "active",
    country: "Singapore",
    qaScore: 78,
    leadTimeDays: 17,
    route: "SGP->MEX",
    gmpLevel: "C",
    activeLots: 7,
    lastAuditDate: "2025-07-10",
    tempExcursions90d: 3,
    notes: [
      "GDP lane validated for SGP->MEX with quarterly review cadence.",
      "QA score trend registered at 78 with CAPA protocol version 4."
    ]
  },
  {
    code: "SUP-CH-0319",
    legalName: "OncoCure Biologics Lotline 319",
    lifecycle: "blocked",
    country: "Switzerland",
    qaScore: 79,
    leadTimeDays: 18,
    route: "CHE->MEX",
    gmpLevel: "A",
    activeLots: 8,
    lastAuditDate: "2025-08-13",
    tempExcursions90d: 4,
    notes: [
      "GDP lane validated for CHE->MEX with quarterly review cadence.",
      "QA score trend registered at 79 with CAPA protocol version 5."
    ]
  },
  {
    code: "SUP-JP-0320",
    legalName: "VitaChem Biologics Lotline 320",
    lifecycle: "approved",
    country: "Japan",
    qaScore: 80,
    leadTimeDays: 3,
    route: "JPN->MEX",
    gmpLevel: "B",
    activeLots: 9,
    lastAuditDate: "2025-09-16",
    tempExcursions90d: 0,
    notes: [
      "GDP lane validated for JPN->MEX with quarterly review cadence.",
      "QA score trend registered at 80 with CAPA protocol version 6."
    ]
  }
];

export const FOUNDATION_DOCUMENTS: readonly VaultDocumentDefinition[] = [
  {
    id: "doc-coa",
    label: "Certificate of Analysis",
    category: "quality",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-11-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report",
    label: "Temperature Report",
    category: "quality",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-10-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit",
    label: "Import Permit",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-07-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification",
    label: "HS Classification Sheet",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-08-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-origin",
    label: "Certificate of Origin",
    category: "customs",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-09-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list",
    label: "Packing List",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-12-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice",
    label: "Commercial Invoice",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-12-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill",
    label: "Air Waybill",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-06-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-lading",
    label: "Bill of Lading",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-06-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate",
    label: "Insurance Certificate",
    category: "finance",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-05-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-001",
    label: "Certificate of Analysis dossier 001",
    category: "quality",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-04-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-002",
    label: "Temperature Report dossier 002",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-05-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-003",
    label: "Import Permit dossier 003",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-06-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-004",
    label: "HS Classification Sheet dossier 004",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-005",
    label: "Certificate of Origin dossier 005",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-006",
    label: "Packing List dossier 006",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-007",
    label: "Commercial Invoice dossier 007",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-008",
    label: "Bill of Lading dossier 008",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-009",
    label: "Air Waybill dossier 009",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-010",
    label: "Dangerous Goods Declaration dossier 010",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-011",
    label: "Validated Cleaning Certificate dossier 011",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-012",
    label: "Sterility Assurance Report dossier 012",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-013",
    label: "Batch Manufacturing Record dossier 013",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-014",
    label: "Customs Broker Authorization dossier 014",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-015",
    label: "Insurance Certificate dossier 015",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-016",
    label: "Cold Chain Qualification dossier 016",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-017",
    label: "Excursion Investigation dossier 017",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-018",
    label: "Deviation Closure Memo dossier 018",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-019",
    label: "CAPA Summary dossier 019",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-020",
    label: "Sanitary Registration dossier 020",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-021",
    label: "Certificate of Analysis dossier 021",
    category: "quality",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-12-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-022",
    label: "Temperature Report dossier 022",
    category: "logistics",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-01-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-023",
    label: "Import Permit dossier 023",
    category: "customs",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-02-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-024",
    label: "HS Classification Sheet dossier 024",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-025",
    label: "Certificate of Origin dossier 025",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-026",
    label: "Packing List dossier 026",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-027",
    label: "Commercial Invoice dossier 027",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-028",
    label: "Bill of Lading dossier 028",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-029",
    label: "Air Waybill dossier 029",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-030",
    label: "Dangerous Goods Declaration dossier 030",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-031",
    label: "Validated Cleaning Certificate dossier 031",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-032",
    label: "Sterility Assurance Report dossier 032",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-033",
    label: "Batch Manufacturing Record dossier 033",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-034",
    label: "Customs Broker Authorization dossier 034",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-035",
    label: "Insurance Certificate dossier 035",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-036",
    label: "Cold Chain Qualification dossier 036",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-037",
    label: "Excursion Investigation dossier 037",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-038",
    label: "Deviation Closure Memo dossier 038",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-039",
    label: "CAPA Summary dossier 039",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-040",
    label: "Sanitary Registration dossier 040",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-041",
    label: "Certificate of Analysis dossier 041",
    category: "quality",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-08-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-042",
    label: "Temperature Report dossier 042",
    category: "logistics",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-09-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-043",
    label: "Import Permit dossier 043",
    category: "customs",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-10-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-044",
    label: "HS Classification Sheet dossier 044",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-045",
    label: "Certificate of Origin dossier 045",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-046",
    label: "Packing List dossier 046",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-047",
    label: "Commercial Invoice dossier 047",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-048",
    label: "Bill of Lading dossier 048",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-049",
    label: "Air Waybill dossier 049",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-050",
    label: "Dangerous Goods Declaration dossier 050",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-051",
    label: "Validated Cleaning Certificate dossier 051",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-052",
    label: "Sterility Assurance Report dossier 052",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-053",
    label: "Batch Manufacturing Record dossier 053",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-054",
    label: "Customs Broker Authorization dossier 054",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-055",
    label: "Insurance Certificate dossier 055",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-056",
    label: "Cold Chain Qualification dossier 056",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-057",
    label: "Excursion Investigation dossier 057",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-058",
    label: "Deviation Closure Memo dossier 058",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-059",
    label: "CAPA Summary dossier 059",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-060",
    label: "Sanitary Registration dossier 060",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-061",
    label: "Certificate of Analysis dossier 061",
    category: "quality",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-04-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-062",
    label: "Temperature Report dossier 062",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-05-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-063",
    label: "Import Permit dossier 063",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-06-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-064",
    label: "HS Classification Sheet dossier 064",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-065",
    label: "Certificate of Origin dossier 065",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-066",
    label: "Packing List dossier 066",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-067",
    label: "Commercial Invoice dossier 067",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-068",
    label: "Bill of Lading dossier 068",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-069",
    label: "Air Waybill dossier 069",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-070",
    label: "Dangerous Goods Declaration dossier 070",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-071",
    label: "Validated Cleaning Certificate dossier 071",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-072",
    label: "Sterility Assurance Report dossier 072",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-073",
    label: "Batch Manufacturing Record dossier 073",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-074",
    label: "Customs Broker Authorization dossier 074",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-075",
    label: "Insurance Certificate dossier 075",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-076",
    label: "Cold Chain Qualification dossier 076",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-077",
    label: "Excursion Investigation dossier 077",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-078",
    label: "Deviation Closure Memo dossier 078",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-079",
    label: "CAPA Summary dossier 079",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-080",
    label: "Sanitary Registration dossier 080",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-081",
    label: "Certificate of Analysis dossier 081",
    category: "quality",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-12-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-082",
    label: "Temperature Report dossier 082",
    category: "logistics",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-01-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-083",
    label: "Import Permit dossier 083",
    category: "customs",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-02-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-084",
    label: "HS Classification Sheet dossier 084",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-085",
    label: "Certificate of Origin dossier 085",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-086",
    label: "Packing List dossier 086",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-087",
    label: "Commercial Invoice dossier 087",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-088",
    label: "Bill of Lading dossier 088",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-089",
    label: "Air Waybill dossier 089",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-090",
    label: "Dangerous Goods Declaration dossier 090",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-091",
    label: "Validated Cleaning Certificate dossier 091",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-092",
    label: "Sterility Assurance Report dossier 092",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-093",
    label: "Batch Manufacturing Record dossier 093",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-094",
    label: "Customs Broker Authorization dossier 094",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-095",
    label: "Insurance Certificate dossier 095",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-096",
    label: "Cold Chain Qualification dossier 096",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-097",
    label: "Excursion Investigation dossier 097",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-098",
    label: "Deviation Closure Memo dossier 098",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-099",
    label: "CAPA Summary dossier 099",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-100",
    label: "Sanitary Registration dossier 100",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-101",
    label: "Certificate of Analysis dossier 101",
    category: "quality",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-08-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-102",
    label: "Temperature Report dossier 102",
    category: "logistics",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-09-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-103",
    label: "Import Permit dossier 103",
    category: "customs",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-10-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-104",
    label: "HS Classification Sheet dossier 104",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-105",
    label: "Certificate of Origin dossier 105",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-106",
    label: "Packing List dossier 106",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-107",
    label: "Commercial Invoice dossier 107",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-108",
    label: "Bill of Lading dossier 108",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-109",
    label: "Air Waybill dossier 109",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-110",
    label: "Dangerous Goods Declaration dossier 110",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-111",
    label: "Validated Cleaning Certificate dossier 111",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-112",
    label: "Sterility Assurance Report dossier 112",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-113",
    label: "Batch Manufacturing Record dossier 113",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-114",
    label: "Customs Broker Authorization dossier 114",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-115",
    label: "Insurance Certificate dossier 115",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-116",
    label: "Cold Chain Qualification dossier 116",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-117",
    label: "Excursion Investigation dossier 117",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-118",
    label: "Deviation Closure Memo dossier 118",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-119",
    label: "CAPA Summary dossier 119",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-120",
    label: "Sanitary Registration dossier 120",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-121",
    label: "Certificate of Analysis dossier 121",
    category: "quality",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-04-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-122",
    label: "Temperature Report dossier 122",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-05-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-123",
    label: "Import Permit dossier 123",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-06-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-124",
    label: "HS Classification Sheet dossier 124",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-125",
    label: "Certificate of Origin dossier 125",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-126",
    label: "Packing List dossier 126",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-127",
    label: "Commercial Invoice dossier 127",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-128",
    label: "Bill of Lading dossier 128",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-129",
    label: "Air Waybill dossier 129",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-130",
    label: "Dangerous Goods Declaration dossier 130",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-131",
    label: "Validated Cleaning Certificate dossier 131",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-132",
    label: "Sterility Assurance Report dossier 132",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-133",
    label: "Batch Manufacturing Record dossier 133",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-134",
    label: "Customs Broker Authorization dossier 134",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-135",
    label: "Insurance Certificate dossier 135",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-136",
    label: "Cold Chain Qualification dossier 136",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-137",
    label: "Excursion Investigation dossier 137",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-138",
    label: "Deviation Closure Memo dossier 138",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-139",
    label: "CAPA Summary dossier 139",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-140",
    label: "Sanitary Registration dossier 140",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-141",
    label: "Certificate of Analysis dossier 141",
    category: "quality",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-12-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-142",
    label: "Temperature Report dossier 142",
    category: "logistics",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-01-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-143",
    label: "Import Permit dossier 143",
    category: "customs",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-02-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-144",
    label: "HS Classification Sheet dossier 144",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-145",
    label: "Certificate of Origin dossier 145",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-146",
    label: "Packing List dossier 146",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-147",
    label: "Commercial Invoice dossier 147",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-148",
    label: "Bill of Lading dossier 148",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-149",
    label: "Air Waybill dossier 149",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-150",
    label: "Dangerous Goods Declaration dossier 150",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-151",
    label: "Validated Cleaning Certificate dossier 151",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-152",
    label: "Sterility Assurance Report dossier 152",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-153",
    label: "Batch Manufacturing Record dossier 153",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-154",
    label: "Customs Broker Authorization dossier 154",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-155",
    label: "Insurance Certificate dossier 155",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-156",
    label: "Cold Chain Qualification dossier 156",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-157",
    label: "Excursion Investigation dossier 157",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-158",
    label: "Deviation Closure Memo dossier 158",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-159",
    label: "CAPA Summary dossier 159",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-160",
    label: "Sanitary Registration dossier 160",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-161",
    label: "Certificate of Analysis dossier 161",
    category: "quality",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-08-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-162",
    label: "Temperature Report dossier 162",
    category: "logistics",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-09-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-163",
    label: "Import Permit dossier 163",
    category: "customs",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-10-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-164",
    label: "HS Classification Sheet dossier 164",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-165",
    label: "Certificate of Origin dossier 165",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-166",
    label: "Packing List dossier 166",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-167",
    label: "Commercial Invoice dossier 167",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-168",
    label: "Bill of Lading dossier 168",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-169",
    label: "Air Waybill dossier 169",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-170",
    label: "Dangerous Goods Declaration dossier 170",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-171",
    label: "Validated Cleaning Certificate dossier 171",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-172",
    label: "Sterility Assurance Report dossier 172",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-173",
    label: "Batch Manufacturing Record dossier 173",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-174",
    label: "Customs Broker Authorization dossier 174",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-175",
    label: "Insurance Certificate dossier 175",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-176",
    label: "Cold Chain Qualification dossier 176",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-177",
    label: "Excursion Investigation dossier 177",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-178",
    label: "Deviation Closure Memo dossier 178",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-179",
    label: "CAPA Summary dossier 179",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-180",
    label: "Sanitary Registration dossier 180",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-181",
    label: "Certificate of Analysis dossier 181",
    category: "quality",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-04-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-182",
    label: "Temperature Report dossier 182",
    category: "logistics",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-05-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-183",
    label: "Import Permit dossier 183",
    category: "customs",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-06-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-184",
    label: "HS Classification Sheet dossier 184",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-185",
    label: "Certificate of Origin dossier 185",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-186",
    label: "Packing List dossier 186",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-187",
    label: "Commercial Invoice dossier 187",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-188",
    label: "Bill of Lading dossier 188",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-189",
    label: "Air Waybill dossier 189",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-190",
    label: "Dangerous Goods Declaration dossier 190",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-191",
    label: "Validated Cleaning Certificate dossier 191",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-192",
    label: "Sterility Assurance Report dossier 192",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-193",
    label: "Batch Manufacturing Record dossier 193",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-194",
    label: "Customs Broker Authorization dossier 194",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-195",
    label: "Insurance Certificate dossier 195",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-196",
    label: "Cold Chain Qualification dossier 196",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-197",
    label: "Excursion Investigation dossier 197",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-198",
    label: "Deviation Closure Memo dossier 198",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-199",
    label: "CAPA Summary dossier 199",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-200",
    label: "Sanitary Registration dossier 200",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-201",
    label: "Certificate of Analysis dossier 201",
    category: "quality",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-12-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-202",
    label: "Temperature Report dossier 202",
    category: "logistics",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-01-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-203",
    label: "Import Permit dossier 203",
    category: "customs",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-02-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-204",
    label: "HS Classification Sheet dossier 204",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-205",
    label: "Certificate of Origin dossier 205",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-206",
    label: "Packing List dossier 206",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-207",
    label: "Commercial Invoice dossier 207",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-208",
    label: "Bill of Lading dossier 208",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-209",
    label: "Air Waybill dossier 209",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-210",
    label: "Dangerous Goods Declaration dossier 210",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-211",
    label: "Validated Cleaning Certificate dossier 211",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-212",
    label: "Sterility Assurance Report dossier 212",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-213",
    label: "Batch Manufacturing Record dossier 213",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-214",
    label: "Customs Broker Authorization dossier 214",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-18",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-215",
    label: "Insurance Certificate dossier 215",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-23",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-216",
    label: "Cold Chain Qualification dossier 216",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-01",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-217",
    label: "Excursion Investigation dossier 217",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-06",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-218",
    label: "Deviation Closure Memo dossier 218",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-11",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-219",
    label: "CAPA Summary dossier 219",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-16",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-220",
    label: "Sanitary Registration dossier 220",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-21",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-analysis-221",
    label: "Certificate of Analysis dossier 221",
    category: "quality",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-08-26",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-temperature-report-222",
    label: "Temperature Report dossier 222",
    category: "logistics",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-09-04",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-import-permit-223",
    label: "Import Permit dossier 223",
    category: "customs",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-10-09",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-hs-classification-sheet-224",
    label: "HS Classification Sheet dossier 224",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-14",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-certificate-of-origin-225",
    label: "Certificate of Origin dossier 225",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-19",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-packing-list-226",
    label: "Packing List dossier 226",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-24",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-commercial-invoice-227",
    label: "Commercial Invoice dossier 227",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-02",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-bill-of-lading-228",
    label: "Bill of Lading dossier 228",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-07",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-air-waybill-229",
    label: "Air Waybill dossier 229",
    category: "quality",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-04-12",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-dangerous-goods-declaration-230",
    label: "Dangerous Goods Declaration dossier 230",
    category: "logistics",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-05-17",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-validated-cleaning-certificate-231",
    label: "Validated Cleaning Certificate dossier 231",
    category: "customs",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-06-22",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sterility-assurance-report-232",
    label: "Sterility Assurance Report dossier 232",
    category: "finance",
    critical: true,
    ownerRole: "auditor",
    expiryDate: "2026-07-27",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-batch-manufacturing-record-233",
    label: "Batch Manufacturing Record dossier 233",
    category: "quality",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-08-05",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-customs-broker-authorization-234",
    label: "Customs Broker Authorization dossier 234",
    category: "logistics",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-09-10",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-insurance-certificate-235",
    label: "Insurance Certificate dossier 235",
    category: "customs",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-10-15",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-cold-chain-qualification-236",
    label: "Cold Chain Qualification dossier 236",
    category: "finance",
    critical: true,
    ownerRole: "operator",
    expiryDate: "2026-11-20",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-excursion-investigation-237",
    label: "Excursion Investigation dossier 237",
    category: "quality",
    critical: false,
    ownerRole: "admin",
    expiryDate: "2026-12-25",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-deviation-closure-memo-238",
    label: "Deviation Closure Memo dossier 238",
    category: "logistics",
    critical: false,
    ownerRole: "auditor",
    expiryDate: "2026-01-03",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-capa-summary-239",
    label: "CAPA Summary dossier 239",
    category: "customs",
    critical: false,
    ownerRole: "operator",
    expiryDate: "2026-02-08",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  },
  {
    id: "doc-sanitary-registration-240",
    label: "Sanitary Registration dossier 240",
    category: "finance",
    critical: true,
    ownerRole: "admin",
    expiryDate: "2026-03-13",
    linkedSupplierCodes: ["SUP-MX-0001", "SUP-US-0002", "SUP-DE-0043"],
    actionPlaybook: [
      "Validate document hash and version against customs bundle.",
      "Confirm lot linkage and update QA evidence reference.",
      "Escalate to compliance lead if status remains unresolved for 4h."
    ]
  }
];

export const FOUNDATION_LOT_CATALOG: readonly FoundationLotProfile[] = [
  {
    id: "foundation-lot-0001",
    sku: "SKU-PHARMA-0001",
    lot: "LOT-R1-0001",
    batch: "BT-R1-0003",
    barcode: "7501234000018",
    supplierCode: "SUP-MX-0001",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-08",
    mfgDate: "2025-03-03",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0002",
    sku: "SKU-PHARMA-0002",
    lot: "LOT-R1-0002",
    batch: "BT-R1-0005",
    barcode: "7501234000035",
    supplierCode: "SUP-MX-0002",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-15",
    mfgDate: "2025-04-05",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0003",
    sku: "SKU-PHARMA-0003",
    lot: "LOT-R1-0003",
    batch: "BT-R1-0007",
    barcode: "7501234000052",
    supplierCode: "SUP-MX-0003",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-22",
    mfgDate: "2025-05-07",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0004",
    sku: "SKU-PHARMA-0004",
    lot: "LOT-R1-0004",
    batch: "BT-R1-0009",
    barcode: "7501234000069",
    supplierCode: "SUP-MX-0004",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-02",
    mfgDate: "2025-06-09",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0005",
    sku: "SKU-PHARMA-0005",
    lot: "LOT-R1-0005",
    batch: "BT-R1-0011",
    barcode: "7501234000086",
    supplierCode: "SUP-MX-0005",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-09",
    mfgDate: "2025-07-11",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0006",
    sku: "SKU-PHARMA-0006",
    lot: "LOT-R1-0006",
    batch: "BT-R1-0013",
    barcode: "7501234000103",
    supplierCode: "SUP-MX-0006",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-16",
    mfgDate: "2025-08-13",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0007",
    sku: "SKU-PHARMA-0007",
    lot: "LOT-R1-0007",
    batch: "BT-R1-0015",
    barcode: "7501234000120",
    supplierCode: "SUP-MX-0007",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-23",
    mfgDate: "2025-09-15",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0008",
    sku: "SKU-PHARMA-0008",
    lot: "LOT-R1-0008",
    batch: "BT-R1-0017",
    barcode: "7501234000137",
    supplierCode: "SUP-MX-0008",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-03",
    mfgDate: "2025-10-17",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0009",
    sku: "SKU-PHARMA-0009",
    lot: "LOT-R1-0009",
    batch: "BT-R1-0019",
    barcode: "7501234000154",
    supplierCode: "SUP-MX-0009",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-10",
    mfgDate: "2025-11-19",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0010",
    sku: "SKU-PHARMA-0010",
    lot: "LOT-R1-0010",
    batch: "BT-R1-0021",
    barcode: "7501234000171",
    supplierCode: "SUP-MX-0010",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-17",
    mfgDate: "2025-12-21",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0011",
    sku: "SKU-PHARMA-0011",
    lot: "LOT-R1-0011",
    batch: "BT-R1-0023",
    barcode: "7501234000188",
    supplierCode: "SUP-MX-0011",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-24",
    mfgDate: "2025-01-23",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0012",
    sku: "SKU-PHARMA-0012",
    lot: "LOT-R1-0012",
    batch: "BT-R1-0025",
    barcode: "7501234000205",
    supplierCode: "SUP-MX-0012",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-04",
    mfgDate: "2025-02-25",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0013",
    sku: "SKU-PHARMA-0013",
    lot: "LOT-R1-0013",
    batch: "BT-R1-0027",
    barcode: "7501234000222",
    supplierCode: "SUP-MX-0013",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-11",
    mfgDate: "2025-03-27",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0014",
    sku: "SKU-PHARMA-0014",
    lot: "LOT-R1-0014",
    batch: "BT-R1-0029",
    barcode: "7501234000239",
    supplierCode: "SUP-MX-0014",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-18",
    mfgDate: "2025-04-02",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0015",
    sku: "SKU-PHARMA-0015",
    lot: "LOT-R1-0015",
    batch: "BT-R1-0031",
    barcode: "7501234000256",
    supplierCode: "SUP-MX-0015",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-25",
    mfgDate: "2025-05-04",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0016",
    sku: "SKU-PHARMA-0016",
    lot: "LOT-R1-0016",
    batch: "BT-R1-0033",
    barcode: "7501234000273",
    supplierCode: "SUP-MX-0016",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-05",
    mfgDate: "2025-06-06",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0017",
    sku: "SKU-PHARMA-0017",
    lot: "LOT-R1-0017",
    batch: "BT-R1-0035",
    barcode: "7501234000290",
    supplierCode: "SUP-MX-0017",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-12",
    mfgDate: "2025-07-08",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0018",
    sku: "SKU-PHARMA-0018",
    lot: "LOT-R1-0018",
    batch: "BT-R1-0037",
    barcode: "7501234000307",
    supplierCode: "SUP-MX-0018",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-19",
    mfgDate: "2025-08-10",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0019",
    sku: "SKU-PHARMA-0019",
    lot: "LOT-R1-0019",
    batch: "BT-R1-0039",
    barcode: "7501234000324",
    supplierCode: "SUP-MX-0019",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-26",
    mfgDate: "2025-09-12",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0020",
    sku: "SKU-PHARMA-0020",
    lot: "LOT-R1-0020",
    batch: "BT-R1-0041",
    barcode: "7501234000341",
    supplierCode: "SUP-MX-0020",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-06",
    mfgDate: "2025-10-14",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0021",
    sku: "SKU-PHARMA-0021",
    lot: "LOT-R1-0021",
    batch: "BT-R1-0043",
    barcode: "7501234000358",
    supplierCode: "SUP-MX-0021",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-13",
    mfgDate: "2025-11-16",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0022",
    sku: "SKU-PHARMA-0022",
    lot: "LOT-R1-0022",
    batch: "BT-R1-0045",
    barcode: "7501234000375",
    supplierCode: "SUP-MX-0022",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-20",
    mfgDate: "2025-12-18",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0023",
    sku: "SKU-PHARMA-0023",
    lot: "LOT-R1-0023",
    batch: "BT-R1-0047",
    barcode: "7501234000392",
    supplierCode: "SUP-MX-0023",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-27",
    mfgDate: "2025-01-20",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0024",
    sku: "SKU-PHARMA-0024",
    lot: "LOT-R1-0024",
    batch: "BT-R1-0049",
    barcode: "7501234000409",
    supplierCode: "SUP-MX-0024",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-07",
    mfgDate: "2025-02-22",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0025",
    sku: "SKU-PHARMA-0025",
    lot: "LOT-R1-0025",
    batch: "BT-R1-0051",
    barcode: "7501234000426",
    supplierCode: "SUP-MX-0025",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-14",
    mfgDate: "2025-03-24",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0026",
    sku: "SKU-PHARMA-0026",
    lot: "LOT-R1-0026",
    batch: "BT-R1-0053",
    barcode: "7501234000443",
    supplierCode: "SUP-MX-0026",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-21",
    mfgDate: "2025-04-26",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0027",
    sku: "SKU-PHARMA-0027",
    lot: "LOT-R1-0027",
    batch: "BT-R1-0055",
    barcode: "7501234000460",
    supplierCode: "SUP-MX-0027",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-01",
    mfgDate: "2025-05-01",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0028",
    sku: "SKU-PHARMA-0028",
    lot: "LOT-R1-0028",
    batch: "BT-R1-0057",
    barcode: "7501234000477",
    supplierCode: "SUP-MX-0028",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-08",
    mfgDate: "2025-06-03",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0029",
    sku: "SKU-PHARMA-0029",
    lot: "LOT-R1-0029",
    batch: "BT-R1-0059",
    barcode: "7501234000494",
    supplierCode: "SUP-MX-0029",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-15",
    mfgDate: "2025-07-05",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0030",
    sku: "SKU-PHARMA-0030",
    lot: "LOT-R1-0030",
    batch: "BT-R1-0061",
    barcode: "7501234000511",
    supplierCode: "SUP-MX-0030",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-22",
    mfgDate: "2025-08-07",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0031",
    sku: "SKU-PHARMA-0031",
    lot: "LOT-R1-0031",
    batch: "BT-R1-0063",
    barcode: "7501234000528",
    supplierCode: "SUP-MX-0031",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-02",
    mfgDate: "2025-09-09",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0032",
    sku: "SKU-PHARMA-0032",
    lot: "LOT-R1-0032",
    batch: "BT-R1-0065",
    barcode: "7501234000545",
    supplierCode: "SUP-MX-0032",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-09",
    mfgDate: "2025-10-11",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0033",
    sku: "SKU-PHARMA-0033",
    lot: "LOT-R1-0033",
    batch: "BT-R1-0067",
    barcode: "7501234000562",
    supplierCode: "SUP-MX-0033",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-16",
    mfgDate: "2025-11-13",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0034",
    sku: "SKU-PHARMA-0034",
    lot: "LOT-R1-0034",
    batch: "BT-R1-0069",
    barcode: "7501234000579",
    supplierCode: "SUP-MX-0034",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-23",
    mfgDate: "2025-12-15",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0035",
    sku: "SKU-PHARMA-0035",
    lot: "LOT-R1-0035",
    batch: "BT-R1-0071",
    barcode: "7501234000596",
    supplierCode: "SUP-MX-0035",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-03",
    mfgDate: "2025-01-17",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0036",
    sku: "SKU-PHARMA-0036",
    lot: "LOT-R1-0036",
    batch: "BT-R1-0073",
    barcode: "7501234000613",
    supplierCode: "SUP-MX-0036",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-10",
    mfgDate: "2025-02-19",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0037",
    sku: "SKU-PHARMA-0037",
    lot: "LOT-R1-0037",
    batch: "BT-R1-0075",
    barcode: "7501234000630",
    supplierCode: "SUP-MX-0037",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-17",
    mfgDate: "2025-03-21",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0038",
    sku: "SKU-PHARMA-0038",
    lot: "LOT-R1-0038",
    batch: "BT-R1-0077",
    barcode: "7501234000647",
    supplierCode: "SUP-MX-0038",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-24",
    mfgDate: "2025-04-23",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0039",
    sku: "SKU-PHARMA-0039",
    lot: "LOT-R1-0039",
    batch: "BT-R1-0079",
    barcode: "7501234000664",
    supplierCode: "SUP-MX-0039",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-04",
    mfgDate: "2025-05-25",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0040",
    sku: "SKU-PHARMA-0040",
    lot: "LOT-R1-0040",
    batch: "BT-R1-0081",
    barcode: "7501234000681",
    supplierCode: "SUP-MX-0040",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-11",
    mfgDate: "2025-06-27",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0041",
    sku: "SKU-PHARMA-0041",
    lot: "LOT-R1-0041",
    batch: "BT-R1-0083",
    barcode: "7501234000698",
    supplierCode: "SUP-MX-0041",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-18",
    mfgDate: "2025-07-02",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0042",
    sku: "SKU-PHARMA-0042",
    lot: "LOT-R1-0042",
    batch: "BT-R1-0085",
    barcode: "7501234000715",
    supplierCode: "SUP-MX-0042",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-25",
    mfgDate: "2025-08-04",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0043",
    sku: "SKU-PHARMA-0043",
    lot: "LOT-R1-0043",
    batch: "BT-R1-0087",
    barcode: "7501234000732",
    supplierCode: "SUP-MX-0043",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-05",
    mfgDate: "2025-09-06",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0044",
    sku: "SKU-PHARMA-0044",
    lot: "LOT-R1-0044",
    batch: "BT-R1-0089",
    barcode: "7501234000749",
    supplierCode: "SUP-MX-0044",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-12",
    mfgDate: "2025-10-08",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0045",
    sku: "SKU-PHARMA-0045",
    lot: "LOT-R1-0045",
    batch: "BT-R1-0091",
    barcode: "7501234000766",
    supplierCode: "SUP-MX-0045",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-19",
    mfgDate: "2025-11-10",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0046",
    sku: "SKU-PHARMA-0046",
    lot: "LOT-R1-0046",
    batch: "BT-R1-0093",
    barcode: "7501234000783",
    supplierCode: "SUP-MX-0046",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-26",
    mfgDate: "2025-12-12",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0047",
    sku: "SKU-PHARMA-0047",
    lot: "LOT-R1-0047",
    batch: "BT-R1-0095",
    barcode: "7501234000800",
    supplierCode: "SUP-MX-0047",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-06",
    mfgDate: "2025-01-14",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0048",
    sku: "SKU-PHARMA-0048",
    lot: "LOT-R1-0048",
    batch: "BT-R1-0097",
    barcode: "7501234000817",
    supplierCode: "SUP-MX-0048",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-13",
    mfgDate: "2025-02-16",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0049",
    sku: "SKU-PHARMA-0049",
    lot: "LOT-R1-0049",
    batch: "BT-R1-0099",
    barcode: "7501234000834",
    supplierCode: "SUP-MX-0049",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-20",
    mfgDate: "2025-03-18",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0050",
    sku: "SKU-PHARMA-0050",
    lot: "LOT-R1-0050",
    batch: "BT-R1-0101",
    barcode: "7501234000851",
    supplierCode: "SUP-MX-0050",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-27",
    mfgDate: "2025-04-20",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0051",
    sku: "SKU-PHARMA-0051",
    lot: "LOT-R1-0051",
    batch: "BT-R1-0103",
    barcode: "7501234000868",
    supplierCode: "SUP-MX-0051",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-07",
    mfgDate: "2025-05-22",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0052",
    sku: "SKU-PHARMA-0052",
    lot: "LOT-R1-0052",
    batch: "BT-R1-0105",
    barcode: "7501234000885",
    supplierCode: "SUP-MX-0052",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-14",
    mfgDate: "2025-06-24",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0053",
    sku: "SKU-PHARMA-0053",
    lot: "LOT-R1-0053",
    batch: "BT-R1-0107",
    barcode: "7501234000902",
    supplierCode: "SUP-MX-0053",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-21",
    mfgDate: "2025-07-26",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0054",
    sku: "SKU-PHARMA-0054",
    lot: "LOT-R1-0054",
    batch: "BT-R1-0109",
    barcode: "7501234000919",
    supplierCode: "SUP-MX-0054",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-01",
    mfgDate: "2025-08-01",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0055",
    sku: "SKU-PHARMA-0055",
    lot: "LOT-R1-0055",
    batch: "BT-R1-0111",
    barcode: "7501234000936",
    supplierCode: "SUP-MX-0055",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-08",
    mfgDate: "2025-09-03",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0056",
    sku: "SKU-PHARMA-0056",
    lot: "LOT-R1-0056",
    batch: "BT-R1-0113",
    barcode: "7501234000953",
    supplierCode: "SUP-MX-0056",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-15",
    mfgDate: "2025-10-05",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0057",
    sku: "SKU-PHARMA-0057",
    lot: "LOT-R1-0057",
    batch: "BT-R1-0115",
    barcode: "7501234000970",
    supplierCode: "SUP-MX-0057",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-22",
    mfgDate: "2025-11-07",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0058",
    sku: "SKU-PHARMA-0058",
    lot: "LOT-R1-0058",
    batch: "BT-R1-0117",
    barcode: "7501234000987",
    supplierCode: "SUP-MX-0058",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-02",
    mfgDate: "2025-12-09",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0059",
    sku: "SKU-PHARMA-0059",
    lot: "LOT-R1-0059",
    batch: "BT-R1-0119",
    barcode: "7501234001004",
    supplierCode: "SUP-MX-0059",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-09",
    mfgDate: "2025-01-11",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0060",
    sku: "SKU-PHARMA-0060",
    lot: "LOT-R1-0060",
    batch: "BT-R1-0121",
    barcode: "7501234001021",
    supplierCode: "SUP-MX-0060",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-16",
    mfgDate: "2025-02-13",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0061",
    sku: "SKU-PHARMA-0061",
    lot: "LOT-R1-0061",
    batch: "BT-R1-0123",
    barcode: "7501234001038",
    supplierCode: "SUP-MX-0061",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-23",
    mfgDate: "2025-03-15",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0062",
    sku: "SKU-PHARMA-0062",
    lot: "LOT-R1-0062",
    batch: "BT-R1-0125",
    barcode: "7501234001055",
    supplierCode: "SUP-MX-0062",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-03",
    mfgDate: "2025-04-17",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0063",
    sku: "SKU-PHARMA-0063",
    lot: "LOT-R1-0063",
    batch: "BT-R1-0127",
    barcode: "7501234001072",
    supplierCode: "SUP-MX-0063",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-10",
    mfgDate: "2025-05-19",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0064",
    sku: "SKU-PHARMA-0064",
    lot: "LOT-R1-0064",
    batch: "BT-R1-0129",
    barcode: "7501234001089",
    supplierCode: "SUP-MX-0064",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-17",
    mfgDate: "2025-06-21",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0065",
    sku: "SKU-PHARMA-0065",
    lot: "LOT-R1-0065",
    batch: "BT-R1-0131",
    barcode: "7501234001106",
    supplierCode: "SUP-MX-0065",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-24",
    mfgDate: "2025-07-23",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0066",
    sku: "SKU-PHARMA-0066",
    lot: "LOT-R1-0066",
    batch: "BT-R1-0133",
    barcode: "7501234001123",
    supplierCode: "SUP-MX-0066",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-04",
    mfgDate: "2025-08-25",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0067",
    sku: "SKU-PHARMA-0067",
    lot: "LOT-R1-0067",
    batch: "BT-R1-0135",
    barcode: "7501234001140",
    supplierCode: "SUP-MX-0067",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-11",
    mfgDate: "2025-09-27",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0068",
    sku: "SKU-PHARMA-0068",
    lot: "LOT-R1-0068",
    batch: "BT-R1-0137",
    barcode: "7501234001157",
    supplierCode: "SUP-MX-0068",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-18",
    mfgDate: "2025-10-02",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0069",
    sku: "SKU-PHARMA-0069",
    lot: "LOT-R1-0069",
    batch: "BT-R1-0139",
    barcode: "7501234001174",
    supplierCode: "SUP-MX-0069",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-25",
    mfgDate: "2025-11-04",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0070",
    sku: "SKU-PHARMA-0070",
    lot: "LOT-R1-0070",
    batch: "BT-R1-0141",
    barcode: "7501234001191",
    supplierCode: "SUP-MX-0070",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-05",
    mfgDate: "2025-12-06",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0071",
    sku: "SKU-PHARMA-0071",
    lot: "LOT-R1-0071",
    batch: "BT-R1-0143",
    barcode: "7501234001208",
    supplierCode: "SUP-MX-0071",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-12",
    mfgDate: "2025-01-08",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0072",
    sku: "SKU-PHARMA-0072",
    lot: "LOT-R1-0072",
    batch: "BT-R1-0145",
    barcode: "7501234001225",
    supplierCode: "SUP-MX-0072",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-19",
    mfgDate: "2025-02-10",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0073",
    sku: "SKU-PHARMA-0073",
    lot: "LOT-R1-0073",
    batch: "BT-R1-0147",
    barcode: "7501234001242",
    supplierCode: "SUP-MX-0073",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-26",
    mfgDate: "2025-03-12",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0074",
    sku: "SKU-PHARMA-0074",
    lot: "LOT-R1-0074",
    batch: "BT-R1-0149",
    barcode: "7501234001259",
    supplierCode: "SUP-MX-0074",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-06",
    mfgDate: "2025-04-14",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0075",
    sku: "SKU-PHARMA-0075",
    lot: "LOT-R1-0075",
    batch: "BT-R1-0151",
    barcode: "7501234001276",
    supplierCode: "SUP-MX-0075",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-13",
    mfgDate: "2025-05-16",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0076",
    sku: "SKU-PHARMA-0076",
    lot: "LOT-R1-0076",
    batch: "BT-R1-0153",
    barcode: "7501234001293",
    supplierCode: "SUP-MX-0076",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-20",
    mfgDate: "2025-06-18",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0077",
    sku: "SKU-PHARMA-0077",
    lot: "LOT-R1-0077",
    batch: "BT-R1-0155",
    barcode: "7501234001310",
    supplierCode: "SUP-MX-0077",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-27",
    mfgDate: "2025-07-20",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0078",
    sku: "SKU-PHARMA-0078",
    lot: "LOT-R1-0078",
    batch: "BT-R1-0157",
    barcode: "7501234001327",
    supplierCode: "SUP-MX-0078",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-07",
    mfgDate: "2025-08-22",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0079",
    sku: "SKU-PHARMA-0079",
    lot: "LOT-R1-0079",
    batch: "BT-R1-0159",
    barcode: "7501234001344",
    supplierCode: "SUP-MX-0079",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-14",
    mfgDate: "2025-09-24",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0080",
    sku: "SKU-PHARMA-0080",
    lot: "LOT-R1-0080",
    batch: "BT-R1-0161",
    barcode: "7501234001361",
    supplierCode: "SUP-MX-0080",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-21",
    mfgDate: "2025-10-26",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0081",
    sku: "SKU-PHARMA-0081",
    lot: "LOT-R1-0081",
    batch: "BT-R1-0163",
    barcode: "7501234001378",
    supplierCode: "SUP-MX-0081",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-01",
    mfgDate: "2025-11-01",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0082",
    sku: "SKU-PHARMA-0082",
    lot: "LOT-R1-0082",
    batch: "BT-R1-0165",
    barcode: "7501234001395",
    supplierCode: "SUP-MX-0082",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-08",
    mfgDate: "2025-12-03",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0083",
    sku: "SKU-PHARMA-0083",
    lot: "LOT-R1-0083",
    batch: "BT-R1-0167",
    barcode: "7501234001412",
    supplierCode: "SUP-MX-0083",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-15",
    mfgDate: "2025-01-05",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0084",
    sku: "SKU-PHARMA-0084",
    lot: "LOT-R1-0084",
    batch: "BT-R1-0169",
    barcode: "7501234001429",
    supplierCode: "SUP-MX-0084",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-22",
    mfgDate: "2025-02-07",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0085",
    sku: "SKU-PHARMA-0085",
    lot: "LOT-R1-0085",
    batch: "BT-R1-0171",
    barcode: "7501234001446",
    supplierCode: "SUP-MX-0085",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-02",
    mfgDate: "2025-03-09",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0086",
    sku: "SKU-PHARMA-0086",
    lot: "LOT-R1-0086",
    batch: "BT-R1-0173",
    barcode: "7501234001463",
    supplierCode: "SUP-MX-0086",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-09",
    mfgDate: "2025-04-11",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0087",
    sku: "SKU-PHARMA-0087",
    lot: "LOT-R1-0087",
    batch: "BT-R1-0175",
    barcode: "7501234001480",
    supplierCode: "SUP-MX-0087",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-16",
    mfgDate: "2025-05-13",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0088",
    sku: "SKU-PHARMA-0088",
    lot: "LOT-R1-0088",
    batch: "BT-R1-0177",
    barcode: "7501234001497",
    supplierCode: "SUP-MX-0088",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-23",
    mfgDate: "2025-06-15",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0089",
    sku: "SKU-PHARMA-0089",
    lot: "LOT-R1-0089",
    batch: "BT-R1-0179",
    barcode: "7501234001514",
    supplierCode: "SUP-MX-0089",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-03",
    mfgDate: "2025-07-17",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0090",
    sku: "SKU-PHARMA-0090",
    lot: "LOT-R1-0090",
    batch: "BT-R1-0181",
    barcode: "7501234001531",
    supplierCode: "SUP-MX-0090",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-10",
    mfgDate: "2025-08-19",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0091",
    sku: "SKU-PHARMA-0091",
    lot: "LOT-R1-0091",
    batch: "BT-R1-0183",
    barcode: "7501234001548",
    supplierCode: "SUP-MX-0091",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-17",
    mfgDate: "2025-09-21",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0092",
    sku: "SKU-PHARMA-0092",
    lot: "LOT-R1-0092",
    batch: "BT-R1-0185",
    barcode: "7501234001565",
    supplierCode: "SUP-MX-0092",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-24",
    mfgDate: "2025-10-23",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0093",
    sku: "SKU-PHARMA-0093",
    lot: "LOT-R1-0093",
    batch: "BT-R1-0187",
    barcode: "7501234001582",
    supplierCode: "SUP-MX-0093",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-04",
    mfgDate: "2025-11-25",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0094",
    sku: "SKU-PHARMA-0094",
    lot: "LOT-R1-0094",
    batch: "BT-R1-0189",
    barcode: "7501234001599",
    supplierCode: "SUP-MX-0094",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-11",
    mfgDate: "2025-12-27",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0095",
    sku: "SKU-PHARMA-0095",
    lot: "LOT-R1-0095",
    batch: "BT-R1-0191",
    barcode: "7501234001616",
    supplierCode: "SUP-MX-0095",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-18",
    mfgDate: "2025-01-02",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0096",
    sku: "SKU-PHARMA-0096",
    lot: "LOT-R1-0096",
    batch: "BT-R1-0193",
    barcode: "7501234001633",
    supplierCode: "SUP-MX-0096",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-25",
    mfgDate: "2025-02-04",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0097",
    sku: "SKU-PHARMA-0097",
    lot: "LOT-R1-0097",
    batch: "BT-R1-0195",
    barcode: "7501234001650",
    supplierCode: "SUP-MX-0097",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-05",
    mfgDate: "2025-03-06",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0098",
    sku: "SKU-PHARMA-0098",
    lot: "LOT-R1-0098",
    batch: "BT-R1-0197",
    barcode: "7501234001667",
    supplierCode: "SUP-MX-0098",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-12",
    mfgDate: "2025-04-08",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0099",
    sku: "SKU-PHARMA-0099",
    lot: "LOT-R1-0099",
    batch: "BT-R1-0199",
    barcode: "7501234001684",
    supplierCode: "SUP-MX-0099",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-19",
    mfgDate: "2025-05-10",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0100",
    sku: "SKU-PHARMA-0100",
    lot: "LOT-R1-0100",
    batch: "BT-R1-0201",
    barcode: "7501234001701",
    supplierCode: "SUP-MX-0100",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-26",
    mfgDate: "2025-06-12",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0101",
    sku: "SKU-PHARMA-0101",
    lot: "LOT-R1-0101",
    batch: "BT-R1-0203",
    barcode: "7501234001718",
    supplierCode: "SUP-MX-0101",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-06",
    mfgDate: "2025-07-14",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0102",
    sku: "SKU-PHARMA-0102",
    lot: "LOT-R1-0102",
    batch: "BT-R1-0205",
    barcode: "7501234001735",
    supplierCode: "SUP-MX-0102",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-13",
    mfgDate: "2025-08-16",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0103",
    sku: "SKU-PHARMA-0103",
    lot: "LOT-R1-0103",
    batch: "BT-R1-0207",
    barcode: "7501234001752",
    supplierCode: "SUP-MX-0103",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-20",
    mfgDate: "2025-09-18",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0104",
    sku: "SKU-PHARMA-0104",
    lot: "LOT-R1-0104",
    batch: "BT-R1-0209",
    barcode: "7501234001769",
    supplierCode: "SUP-MX-0104",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-27",
    mfgDate: "2025-10-20",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0105",
    sku: "SKU-PHARMA-0105",
    lot: "LOT-R1-0105",
    batch: "BT-R1-0211",
    barcode: "7501234001786",
    supplierCode: "SUP-MX-0105",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-07",
    mfgDate: "2025-11-22",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0106",
    sku: "SKU-PHARMA-0106",
    lot: "LOT-R1-0106",
    batch: "BT-R1-0213",
    barcode: "7501234001803",
    supplierCode: "SUP-MX-0106",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-14",
    mfgDate: "2025-12-24",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0107",
    sku: "SKU-PHARMA-0107",
    lot: "LOT-R1-0107",
    batch: "BT-R1-0215",
    barcode: "7501234001820",
    supplierCode: "SUP-MX-0107",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-21",
    mfgDate: "2025-01-26",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0108",
    sku: "SKU-PHARMA-0108",
    lot: "LOT-R1-0108",
    batch: "BT-R1-0217",
    barcode: "7501234001837",
    supplierCode: "SUP-MX-0108",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-01",
    mfgDate: "2025-02-01",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0109",
    sku: "SKU-PHARMA-0109",
    lot: "LOT-R1-0109",
    batch: "BT-R1-0219",
    barcode: "7501234001854",
    supplierCode: "SUP-MX-0109",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-08",
    mfgDate: "2025-03-03",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0110",
    sku: "SKU-PHARMA-0110",
    lot: "LOT-R1-0110",
    batch: "BT-R1-0221",
    barcode: "7501234001871",
    supplierCode: "SUP-MX-0110",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-15",
    mfgDate: "2025-04-05",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0111",
    sku: "SKU-PHARMA-0111",
    lot: "LOT-R1-0111",
    batch: "BT-R1-0223",
    barcode: "7501234001888",
    supplierCode: "SUP-MX-0111",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-22",
    mfgDate: "2025-05-07",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0112",
    sku: "SKU-PHARMA-0112",
    lot: "LOT-R1-0112",
    batch: "BT-R1-0225",
    barcode: "7501234001905",
    supplierCode: "SUP-MX-0112",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-02",
    mfgDate: "2025-06-09",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0113",
    sku: "SKU-PHARMA-0113",
    lot: "LOT-R1-0113",
    batch: "BT-R1-0227",
    barcode: "7501234001922",
    supplierCode: "SUP-MX-0113",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-09",
    mfgDate: "2025-07-11",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0114",
    sku: "SKU-PHARMA-0114",
    lot: "LOT-R1-0114",
    batch: "BT-R1-0229",
    barcode: "7501234001939",
    supplierCode: "SUP-MX-0114",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-16",
    mfgDate: "2025-08-13",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0115",
    sku: "SKU-PHARMA-0115",
    lot: "LOT-R1-0115",
    batch: "BT-R1-0231",
    barcode: "7501234001956",
    supplierCode: "SUP-MX-0115",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-23",
    mfgDate: "2025-09-15",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0116",
    sku: "SKU-PHARMA-0116",
    lot: "LOT-R1-0116",
    batch: "BT-R1-0233",
    barcode: "7501234001973",
    supplierCode: "SUP-MX-0116",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-03",
    mfgDate: "2025-10-17",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0117",
    sku: "SKU-PHARMA-0117",
    lot: "LOT-R1-0117",
    batch: "BT-R1-0235",
    barcode: "7501234001990",
    supplierCode: "SUP-MX-0117",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-10",
    mfgDate: "2025-11-19",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0118",
    sku: "SKU-PHARMA-0118",
    lot: "LOT-R1-0118",
    batch: "BT-R1-0237",
    barcode: "7501234002007",
    supplierCode: "SUP-MX-0118",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-17",
    mfgDate: "2025-12-21",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0119",
    sku: "SKU-PHARMA-0119",
    lot: "LOT-R1-0119",
    batch: "BT-R1-0239",
    barcode: "7501234002024",
    supplierCode: "SUP-MX-0119",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-24",
    mfgDate: "2025-01-23",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0120",
    sku: "SKU-PHARMA-0120",
    lot: "LOT-R1-0120",
    batch: "BT-R1-0241",
    barcode: "7501234002041",
    supplierCode: "SUP-MX-0120",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-04",
    mfgDate: "2025-02-25",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0121",
    sku: "SKU-PHARMA-0121",
    lot: "LOT-R1-0121",
    batch: "BT-R1-0243",
    barcode: "7501234002058",
    supplierCode: "SUP-MX-0121",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-11",
    mfgDate: "2025-03-27",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0122",
    sku: "SKU-PHARMA-0122",
    lot: "LOT-R1-0122",
    batch: "BT-R1-0245",
    barcode: "7501234002075",
    supplierCode: "SUP-MX-0122",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-18",
    mfgDate: "2025-04-02",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0123",
    sku: "SKU-PHARMA-0123",
    lot: "LOT-R1-0123",
    batch: "BT-R1-0247",
    barcode: "7501234002092",
    supplierCode: "SUP-MX-0123",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-25",
    mfgDate: "2025-05-04",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0124",
    sku: "SKU-PHARMA-0124",
    lot: "LOT-R1-0124",
    batch: "BT-R1-0249",
    barcode: "7501234002109",
    supplierCode: "SUP-MX-0124",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-05",
    mfgDate: "2025-06-06",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0125",
    sku: "SKU-PHARMA-0125",
    lot: "LOT-R1-0125",
    batch: "BT-R1-0251",
    barcode: "7501234002126",
    supplierCode: "SUP-MX-0125",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-12",
    mfgDate: "2025-07-08",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0126",
    sku: "SKU-PHARMA-0126",
    lot: "LOT-R1-0126",
    batch: "BT-R1-0253",
    barcode: "7501234002143",
    supplierCode: "SUP-MX-0126",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-19",
    mfgDate: "2025-08-10",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0127",
    sku: "SKU-PHARMA-0127",
    lot: "LOT-R1-0127",
    batch: "BT-R1-0255",
    barcode: "7501234002160",
    supplierCode: "SUP-MX-0127",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-26",
    mfgDate: "2025-09-12",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0128",
    sku: "SKU-PHARMA-0128",
    lot: "LOT-R1-0128",
    batch: "BT-R1-0257",
    barcode: "7501234002177",
    supplierCode: "SUP-MX-0128",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-06",
    mfgDate: "2025-10-14",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0129",
    sku: "SKU-PHARMA-0129",
    lot: "LOT-R1-0129",
    batch: "BT-R1-0259",
    barcode: "7501234002194",
    supplierCode: "SUP-MX-0129",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-13",
    mfgDate: "2025-11-16",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0130",
    sku: "SKU-PHARMA-0130",
    lot: "LOT-R1-0130",
    batch: "BT-R1-0261",
    barcode: "7501234002211",
    supplierCode: "SUP-MX-0130",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-20",
    mfgDate: "2025-12-18",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0131",
    sku: "SKU-PHARMA-0131",
    lot: "LOT-R1-0131",
    batch: "BT-R1-0263",
    barcode: "7501234002228",
    supplierCode: "SUP-MX-0131",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-27",
    mfgDate: "2025-01-20",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0132",
    sku: "SKU-PHARMA-0132",
    lot: "LOT-R1-0132",
    batch: "BT-R1-0265",
    barcode: "7501234002245",
    supplierCode: "SUP-MX-0132",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-07",
    mfgDate: "2025-02-22",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0133",
    sku: "SKU-PHARMA-0133",
    lot: "LOT-R1-0133",
    batch: "BT-R1-0267",
    barcode: "7501234002262",
    supplierCode: "SUP-MX-0133",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-14",
    mfgDate: "2025-03-24",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0134",
    sku: "SKU-PHARMA-0134",
    lot: "LOT-R1-0134",
    batch: "BT-R1-0269",
    barcode: "7501234002279",
    supplierCode: "SUP-MX-0134",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-21",
    mfgDate: "2025-04-26",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0135",
    sku: "SKU-PHARMA-0135",
    lot: "LOT-R1-0135",
    batch: "BT-R1-0271",
    barcode: "7501234002296",
    supplierCode: "SUP-MX-0135",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-01",
    mfgDate: "2025-05-01",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0136",
    sku: "SKU-PHARMA-0136",
    lot: "LOT-R1-0136",
    batch: "BT-R1-0273",
    barcode: "7501234002313",
    supplierCode: "SUP-MX-0136",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-08",
    mfgDate: "2025-06-03",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0137",
    sku: "SKU-PHARMA-0137",
    lot: "LOT-R1-0137",
    batch: "BT-R1-0275",
    barcode: "7501234002330",
    supplierCode: "SUP-MX-0137",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-15",
    mfgDate: "2025-07-05",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0138",
    sku: "SKU-PHARMA-0138",
    lot: "LOT-R1-0138",
    batch: "BT-R1-0277",
    barcode: "7501234002347",
    supplierCode: "SUP-MX-0138",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-22",
    mfgDate: "2025-08-07",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0139",
    sku: "SKU-PHARMA-0139",
    lot: "LOT-R1-0139",
    batch: "BT-R1-0279",
    barcode: "7501234002364",
    supplierCode: "SUP-MX-0139",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-02",
    mfgDate: "2025-09-09",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0140",
    sku: "SKU-PHARMA-0140",
    lot: "LOT-R1-0140",
    batch: "BT-R1-0281",
    barcode: "7501234002381",
    supplierCode: "SUP-MX-0140",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-09",
    mfgDate: "2025-10-11",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0141",
    sku: "SKU-PHARMA-0141",
    lot: "LOT-R1-0141",
    batch: "BT-R1-0283",
    barcode: "7501234002398",
    supplierCode: "SUP-MX-0141",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-16",
    mfgDate: "2025-11-13",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0142",
    sku: "SKU-PHARMA-0142",
    lot: "LOT-R1-0142",
    batch: "BT-R1-0285",
    barcode: "7501234002415",
    supplierCode: "SUP-MX-0142",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-23",
    mfgDate: "2025-12-15",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0143",
    sku: "SKU-PHARMA-0143",
    lot: "LOT-R1-0143",
    batch: "BT-R1-0287",
    barcode: "7501234002432",
    supplierCode: "SUP-MX-0143",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-03",
    mfgDate: "2025-01-17",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0144",
    sku: "SKU-PHARMA-0144",
    lot: "LOT-R1-0144",
    batch: "BT-R1-0289",
    barcode: "7501234002449",
    supplierCode: "SUP-MX-0144",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-10",
    mfgDate: "2025-02-19",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0145",
    sku: "SKU-PHARMA-0145",
    lot: "LOT-R1-0145",
    batch: "BT-R1-0291",
    barcode: "7501234002466",
    supplierCode: "SUP-MX-0145",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-17",
    mfgDate: "2025-03-21",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0146",
    sku: "SKU-PHARMA-0146",
    lot: "LOT-R1-0146",
    batch: "BT-R1-0293",
    barcode: "7501234002483",
    supplierCode: "SUP-MX-0146",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-24",
    mfgDate: "2025-04-23",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0147",
    sku: "SKU-PHARMA-0147",
    lot: "LOT-R1-0147",
    batch: "BT-R1-0295",
    barcode: "7501234002500",
    supplierCode: "SUP-MX-0147",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-04",
    mfgDate: "2025-05-25",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0148",
    sku: "SKU-PHARMA-0148",
    lot: "LOT-R1-0148",
    batch: "BT-R1-0297",
    barcode: "7501234002517",
    supplierCode: "SUP-MX-0148",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-11",
    mfgDate: "2025-06-27",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0149",
    sku: "SKU-PHARMA-0149",
    lot: "LOT-R1-0149",
    batch: "BT-R1-0299",
    barcode: "7501234002534",
    supplierCode: "SUP-MX-0149",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-18",
    mfgDate: "2025-07-02",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0150",
    sku: "SKU-PHARMA-0150",
    lot: "LOT-R1-0150",
    batch: "BT-R1-0301",
    barcode: "7501234002551",
    supplierCode: "SUP-MX-0150",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-25",
    mfgDate: "2025-08-04",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0151",
    sku: "SKU-PHARMA-0151",
    lot: "LOT-R1-0151",
    batch: "BT-R1-0303",
    barcode: "7501234002568",
    supplierCode: "SUP-MX-0151",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-05",
    mfgDate: "2025-09-06",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0152",
    sku: "SKU-PHARMA-0152",
    lot: "LOT-R1-0152",
    batch: "BT-R1-0305",
    barcode: "7501234002585",
    supplierCode: "SUP-MX-0152",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-12",
    mfgDate: "2025-10-08",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0153",
    sku: "SKU-PHARMA-0153",
    lot: "LOT-R1-0153",
    batch: "BT-R1-0307",
    barcode: "7501234002602",
    supplierCode: "SUP-MX-0153",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-19",
    mfgDate: "2025-11-10",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0154",
    sku: "SKU-PHARMA-0154",
    lot: "LOT-R1-0154",
    batch: "BT-R1-0309",
    barcode: "7501234002619",
    supplierCode: "SUP-MX-0154",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-26",
    mfgDate: "2025-12-12",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0155",
    sku: "SKU-PHARMA-0155",
    lot: "LOT-R1-0155",
    batch: "BT-R1-0311",
    barcode: "7501234002636",
    supplierCode: "SUP-MX-0155",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-06",
    mfgDate: "2025-01-14",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0156",
    sku: "SKU-PHARMA-0156",
    lot: "LOT-R1-0156",
    batch: "BT-R1-0313",
    barcode: "7501234002653",
    supplierCode: "SUP-MX-0156",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-13",
    mfgDate: "2025-02-16",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0157",
    sku: "SKU-PHARMA-0157",
    lot: "LOT-R1-0157",
    batch: "BT-R1-0315",
    barcode: "7501234002670",
    supplierCode: "SUP-MX-0157",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-20",
    mfgDate: "2025-03-18",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0158",
    sku: "SKU-PHARMA-0158",
    lot: "LOT-R1-0158",
    batch: "BT-R1-0317",
    barcode: "7501234002687",
    supplierCode: "SUP-MX-0158",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-27",
    mfgDate: "2025-04-20",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0159",
    sku: "SKU-PHARMA-0159",
    lot: "LOT-R1-0159",
    batch: "BT-R1-0319",
    barcode: "7501234002704",
    supplierCode: "SUP-MX-0159",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-07",
    mfgDate: "2025-05-22",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0160",
    sku: "SKU-PHARMA-0160",
    lot: "LOT-R1-0160",
    batch: "BT-R1-0321",
    barcode: "7501234002721",
    supplierCode: "SUP-MX-0160",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-14",
    mfgDate: "2025-06-24",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0161",
    sku: "SKU-PHARMA-0001",
    lot: "LOT-R1-0161",
    batch: "BT-R1-0323",
    barcode: "7501234002738",
    supplierCode: "SUP-MX-0161",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-21",
    mfgDate: "2025-07-26",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0162",
    sku: "SKU-PHARMA-0002",
    lot: "LOT-R1-0162",
    batch: "BT-R1-0325",
    barcode: "7501234002755",
    supplierCode: "SUP-MX-0162",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-01",
    mfgDate: "2025-08-01",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0163",
    sku: "SKU-PHARMA-0003",
    lot: "LOT-R1-0163",
    batch: "BT-R1-0327",
    barcode: "7501234002772",
    supplierCode: "SUP-MX-0163",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-08",
    mfgDate: "2025-09-03",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0164",
    sku: "SKU-PHARMA-0004",
    lot: "LOT-R1-0164",
    batch: "BT-R1-0329",
    barcode: "7501234002789",
    supplierCode: "SUP-MX-0164",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-15",
    mfgDate: "2025-10-05",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0165",
    sku: "SKU-PHARMA-0005",
    lot: "LOT-R1-0165",
    batch: "BT-R1-0331",
    barcode: "7501234002806",
    supplierCode: "SUP-MX-0165",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-22",
    mfgDate: "2025-11-07",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0166",
    sku: "SKU-PHARMA-0006",
    lot: "LOT-R1-0166",
    batch: "BT-R1-0333",
    barcode: "7501234002823",
    supplierCode: "SUP-MX-0166",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-02",
    mfgDate: "2025-12-09",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0167",
    sku: "SKU-PHARMA-0007",
    lot: "LOT-R1-0167",
    batch: "BT-R1-0335",
    barcode: "7501234002840",
    supplierCode: "SUP-MX-0167",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-09",
    mfgDate: "2025-01-11",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0168",
    sku: "SKU-PHARMA-0008",
    lot: "LOT-R1-0168",
    batch: "BT-R1-0337",
    barcode: "7501234002857",
    supplierCode: "SUP-MX-0168",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-16",
    mfgDate: "2025-02-13",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0169",
    sku: "SKU-PHARMA-0009",
    lot: "LOT-R1-0169",
    batch: "BT-R1-0339",
    barcode: "7501234002874",
    supplierCode: "SUP-MX-0169",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-23",
    mfgDate: "2025-03-15",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0170",
    sku: "SKU-PHARMA-0010",
    lot: "LOT-R1-0170",
    batch: "BT-R1-0341",
    barcode: "7501234002891",
    supplierCode: "SUP-MX-0170",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-03",
    mfgDate: "2025-04-17",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0171",
    sku: "SKU-PHARMA-0011",
    lot: "LOT-R1-0171",
    batch: "BT-R1-0343",
    barcode: "7501234002908",
    supplierCode: "SUP-MX-0171",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-10",
    mfgDate: "2025-05-19",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0172",
    sku: "SKU-PHARMA-0012",
    lot: "LOT-R1-0172",
    batch: "BT-R1-0345",
    barcode: "7501234002925",
    supplierCode: "SUP-MX-0172",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-17",
    mfgDate: "2025-06-21",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0173",
    sku: "SKU-PHARMA-0013",
    lot: "LOT-R1-0173",
    batch: "BT-R1-0347",
    barcode: "7501234002942",
    supplierCode: "SUP-MX-0173",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-24",
    mfgDate: "2025-07-23",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0174",
    sku: "SKU-PHARMA-0014",
    lot: "LOT-R1-0174",
    batch: "BT-R1-0349",
    barcode: "7501234002959",
    supplierCode: "SUP-MX-0174",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-04",
    mfgDate: "2025-08-25",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0175",
    sku: "SKU-PHARMA-0015",
    lot: "LOT-R1-0175",
    batch: "BT-R1-0351",
    barcode: "7501234002976",
    supplierCode: "SUP-MX-0175",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-11",
    mfgDate: "2025-09-27",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0176",
    sku: "SKU-PHARMA-0016",
    lot: "LOT-R1-0176",
    batch: "BT-R1-0353",
    barcode: "7501234002993",
    supplierCode: "SUP-MX-0176",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-18",
    mfgDate: "2025-10-02",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0177",
    sku: "SKU-PHARMA-0017",
    lot: "LOT-R1-0177",
    batch: "BT-R1-0355",
    barcode: "7501234003010",
    supplierCode: "SUP-MX-0177",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-25",
    mfgDate: "2025-11-04",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0178",
    sku: "SKU-PHARMA-0018",
    lot: "LOT-R1-0178",
    batch: "BT-R1-0357",
    barcode: "7501234003027",
    supplierCode: "SUP-MX-0178",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-05",
    mfgDate: "2025-12-06",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0179",
    sku: "SKU-PHARMA-0019",
    lot: "LOT-R1-0179",
    batch: "BT-R1-0359",
    barcode: "7501234003044",
    supplierCode: "SUP-MX-0179",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-12",
    mfgDate: "2025-01-08",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0180",
    sku: "SKU-PHARMA-0020",
    lot: "LOT-R1-0180",
    batch: "BT-R1-0361",
    barcode: "7501234003061",
    supplierCode: "SUP-MX-0180",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-19",
    mfgDate: "2025-02-10",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0181",
    sku: "SKU-PHARMA-0021",
    lot: "LOT-R1-0181",
    batch: "BT-R1-0363",
    barcode: "7501234003078",
    supplierCode: "SUP-MX-0181",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-26",
    mfgDate: "2025-03-12",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0182",
    sku: "SKU-PHARMA-0022",
    lot: "LOT-R1-0182",
    batch: "BT-R1-0365",
    barcode: "7501234003095",
    supplierCode: "SUP-MX-0182",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-06",
    mfgDate: "2025-04-14",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0183",
    sku: "SKU-PHARMA-0023",
    lot: "LOT-R1-0183",
    batch: "BT-R1-0367",
    barcode: "7501234003112",
    supplierCode: "SUP-MX-0183",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-13",
    mfgDate: "2025-05-16",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0184",
    sku: "SKU-PHARMA-0024",
    lot: "LOT-R1-0184",
    batch: "BT-R1-0369",
    barcode: "7501234003129",
    supplierCode: "SUP-MX-0184",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-20",
    mfgDate: "2025-06-18",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0185",
    sku: "SKU-PHARMA-0025",
    lot: "LOT-R1-0185",
    batch: "BT-R1-0371",
    barcode: "7501234003146",
    supplierCode: "SUP-MX-0185",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-27",
    mfgDate: "2025-07-20",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0186",
    sku: "SKU-PHARMA-0026",
    lot: "LOT-R1-0186",
    batch: "BT-R1-0373",
    barcode: "7501234003163",
    supplierCode: "SUP-MX-0186",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-07",
    mfgDate: "2025-08-22",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0187",
    sku: "SKU-PHARMA-0027",
    lot: "LOT-R1-0187",
    batch: "BT-R1-0375",
    barcode: "7501234003180",
    supplierCode: "SUP-MX-0187",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-14",
    mfgDate: "2025-09-24",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0188",
    sku: "SKU-PHARMA-0028",
    lot: "LOT-R1-0188",
    batch: "BT-R1-0377",
    barcode: "7501234003197",
    supplierCode: "SUP-MX-0188",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-21",
    mfgDate: "2025-10-26",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0189",
    sku: "SKU-PHARMA-0029",
    lot: "LOT-R1-0189",
    batch: "BT-R1-0379",
    barcode: "7501234003214",
    supplierCode: "SUP-MX-0189",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-01",
    mfgDate: "2025-11-01",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0190",
    sku: "SKU-PHARMA-0030",
    lot: "LOT-R1-0190",
    batch: "BT-R1-0381",
    barcode: "7501234003231",
    supplierCode: "SUP-MX-0190",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-08",
    mfgDate: "2025-12-03",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0191",
    sku: "SKU-PHARMA-0031",
    lot: "LOT-R1-0191",
    batch: "BT-R1-0383",
    barcode: "7501234003248",
    supplierCode: "SUP-MX-0191",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-15",
    mfgDate: "2025-01-05",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0192",
    sku: "SKU-PHARMA-0032",
    lot: "LOT-R1-0192",
    batch: "BT-R1-0385",
    barcode: "7501234003265",
    supplierCode: "SUP-MX-0192",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-22",
    mfgDate: "2025-02-07",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0193",
    sku: "SKU-PHARMA-0033",
    lot: "LOT-R1-0193",
    batch: "BT-R1-0387",
    barcode: "7501234003282",
    supplierCode: "SUP-MX-0193",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-02",
    mfgDate: "2025-03-09",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0194",
    sku: "SKU-PHARMA-0034",
    lot: "LOT-R1-0194",
    batch: "BT-R1-0389",
    barcode: "7501234003299",
    supplierCode: "SUP-MX-0194",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-09",
    mfgDate: "2025-04-11",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0195",
    sku: "SKU-PHARMA-0035",
    lot: "LOT-R1-0195",
    batch: "BT-R1-0391",
    barcode: "7501234003316",
    supplierCode: "SUP-MX-0195",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-16",
    mfgDate: "2025-05-13",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0196",
    sku: "SKU-PHARMA-0036",
    lot: "LOT-R1-0196",
    batch: "BT-R1-0393",
    barcode: "7501234003333",
    supplierCode: "SUP-MX-0196",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-23",
    mfgDate: "2025-06-15",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0197",
    sku: "SKU-PHARMA-0037",
    lot: "LOT-R1-0197",
    batch: "BT-R1-0395",
    barcode: "7501234003350",
    supplierCode: "SUP-MX-0197",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-03",
    mfgDate: "2025-07-17",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0198",
    sku: "SKU-PHARMA-0038",
    lot: "LOT-R1-0198",
    batch: "BT-R1-0397",
    barcode: "7501234003367",
    supplierCode: "SUP-MX-0198",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-10",
    mfgDate: "2025-08-19",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0199",
    sku: "SKU-PHARMA-0039",
    lot: "LOT-R1-0199",
    batch: "BT-R1-0399",
    barcode: "7501234003384",
    supplierCode: "SUP-MX-0199",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-17",
    mfgDate: "2025-09-21",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0200",
    sku: "SKU-PHARMA-0040",
    lot: "LOT-R1-0200",
    batch: "BT-R1-0401",
    barcode: "7501234003401",
    supplierCode: "SUP-MX-0200",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-24",
    mfgDate: "2025-10-23",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0201",
    sku: "SKU-PHARMA-0041",
    lot: "LOT-R1-0201",
    batch: "BT-R1-0403",
    barcode: "7501234003418",
    supplierCode: "SUP-MX-0201",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-04",
    mfgDate: "2025-11-25",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0202",
    sku: "SKU-PHARMA-0042",
    lot: "LOT-R1-0202",
    batch: "BT-R1-0405",
    barcode: "7501234003435",
    supplierCode: "SUP-MX-0202",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-11",
    mfgDate: "2025-12-27",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0203",
    sku: "SKU-PHARMA-0043",
    lot: "LOT-R1-0203",
    batch: "BT-R1-0407",
    barcode: "7501234003452",
    supplierCode: "SUP-MX-0203",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-18",
    mfgDate: "2025-01-02",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0204",
    sku: "SKU-PHARMA-0044",
    lot: "LOT-R1-0204",
    batch: "BT-R1-0409",
    barcode: "7501234003469",
    supplierCode: "SUP-MX-0204",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-25",
    mfgDate: "2025-02-04",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0205",
    sku: "SKU-PHARMA-0045",
    lot: "LOT-R1-0205",
    batch: "BT-R1-0411",
    barcode: "7501234003486",
    supplierCode: "SUP-MX-0205",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-05",
    mfgDate: "2025-03-06",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0206",
    sku: "SKU-PHARMA-0046",
    lot: "LOT-R1-0206",
    batch: "BT-R1-0413",
    barcode: "7501234003503",
    supplierCode: "SUP-MX-0206",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-12",
    mfgDate: "2025-04-08",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0207",
    sku: "SKU-PHARMA-0047",
    lot: "LOT-R1-0207",
    batch: "BT-R1-0415",
    barcode: "7501234003520",
    supplierCode: "SUP-MX-0207",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-19",
    mfgDate: "2025-05-10",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0208",
    sku: "SKU-PHARMA-0048",
    lot: "LOT-R1-0208",
    batch: "BT-R1-0417",
    barcode: "7501234003537",
    supplierCode: "SUP-MX-0208",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-26",
    mfgDate: "2025-06-12",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0209",
    sku: "SKU-PHARMA-0049",
    lot: "LOT-R1-0209",
    batch: "BT-R1-0419",
    barcode: "7501234003554",
    supplierCode: "SUP-MX-0209",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-06",
    mfgDate: "2025-07-14",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0210",
    sku: "SKU-PHARMA-0050",
    lot: "LOT-R1-0210",
    batch: "BT-R1-0421",
    barcode: "7501234003571",
    supplierCode: "SUP-MX-0210",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-13",
    mfgDate: "2025-08-16",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0211",
    sku: "SKU-PHARMA-0051",
    lot: "LOT-R1-0211",
    batch: "BT-R1-0423",
    barcode: "7501234003588",
    supplierCode: "SUP-MX-0211",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-20",
    mfgDate: "2025-09-18",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0212",
    sku: "SKU-PHARMA-0052",
    lot: "LOT-R1-0212",
    batch: "BT-R1-0425",
    barcode: "7501234003605",
    supplierCode: "SUP-MX-0212",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-27",
    mfgDate: "2025-10-20",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0213",
    sku: "SKU-PHARMA-0053",
    lot: "LOT-R1-0213",
    batch: "BT-R1-0427",
    barcode: "7501234003622",
    supplierCode: "SUP-MX-0213",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-07",
    mfgDate: "2025-11-22",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0214",
    sku: "SKU-PHARMA-0054",
    lot: "LOT-R1-0214",
    batch: "BT-R1-0429",
    barcode: "7501234003639",
    supplierCode: "SUP-MX-0214",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-14",
    mfgDate: "2025-12-24",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0215",
    sku: "SKU-PHARMA-0055",
    lot: "LOT-R1-0215",
    batch: "BT-R1-0431",
    barcode: "7501234003656",
    supplierCode: "SUP-MX-0215",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-21",
    mfgDate: "2025-01-26",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0216",
    sku: "SKU-PHARMA-0056",
    lot: "LOT-R1-0216",
    batch: "BT-R1-0433",
    barcode: "7501234003673",
    supplierCode: "SUP-MX-0216",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-01",
    mfgDate: "2025-02-01",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0217",
    sku: "SKU-PHARMA-0057",
    lot: "LOT-R1-0217",
    batch: "BT-R1-0435",
    barcode: "7501234003690",
    supplierCode: "SUP-MX-0217",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-08",
    mfgDate: "2025-03-03",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0218",
    sku: "SKU-PHARMA-0058",
    lot: "LOT-R1-0218",
    batch: "BT-R1-0437",
    barcode: "7501234003707",
    supplierCode: "SUP-MX-0218",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-15",
    mfgDate: "2025-04-05",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0219",
    sku: "SKU-PHARMA-0059",
    lot: "LOT-R1-0219",
    batch: "BT-R1-0439",
    barcode: "7501234003724",
    supplierCode: "SUP-MX-0219",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-22",
    mfgDate: "2025-05-07",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0220",
    sku: "SKU-PHARMA-0060",
    lot: "LOT-R1-0220",
    batch: "BT-R1-0441",
    barcode: "7501234003741",
    supplierCode: "SUP-MX-0220",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-02",
    mfgDate: "2025-06-09",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0221",
    sku: "SKU-PHARMA-0061",
    lot: "LOT-R1-0221",
    batch: "BT-R1-0443",
    barcode: "7501234003758",
    supplierCode: "SUP-MX-0221",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-09",
    mfgDate: "2025-07-11",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0222",
    sku: "SKU-PHARMA-0062",
    lot: "LOT-R1-0222",
    batch: "BT-R1-0445",
    barcode: "7501234003775",
    supplierCode: "SUP-MX-0222",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-16",
    mfgDate: "2025-08-13",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0223",
    sku: "SKU-PHARMA-0063",
    lot: "LOT-R1-0223",
    batch: "BT-R1-0447",
    barcode: "7501234003792",
    supplierCode: "SUP-MX-0223",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-23",
    mfgDate: "2025-09-15",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0224",
    sku: "SKU-PHARMA-0064",
    lot: "LOT-R1-0224",
    batch: "BT-R1-0449",
    barcode: "7501234003809",
    supplierCode: "SUP-MX-0224",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-03",
    mfgDate: "2025-10-17",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0225",
    sku: "SKU-PHARMA-0065",
    lot: "LOT-R1-0225",
    batch: "BT-R1-0451",
    barcode: "7501234003826",
    supplierCode: "SUP-MX-0225",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-10",
    mfgDate: "2025-11-19",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0226",
    sku: "SKU-PHARMA-0066",
    lot: "LOT-R1-0226",
    batch: "BT-R1-0453",
    barcode: "7501234003843",
    supplierCode: "SUP-MX-0226",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-17",
    mfgDate: "2025-12-21",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0227",
    sku: "SKU-PHARMA-0067",
    lot: "LOT-R1-0227",
    batch: "BT-R1-0455",
    barcode: "7501234003860",
    supplierCode: "SUP-MX-0227",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-24",
    mfgDate: "2025-01-23",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0228",
    sku: "SKU-PHARMA-0068",
    lot: "LOT-R1-0228",
    batch: "BT-R1-0457",
    barcode: "7501234003877",
    supplierCode: "SUP-MX-0228",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-04",
    mfgDate: "2025-02-25",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0229",
    sku: "SKU-PHARMA-0069",
    lot: "LOT-R1-0229",
    batch: "BT-R1-0459",
    barcode: "7501234003894",
    supplierCode: "SUP-MX-0229",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-11",
    mfgDate: "2025-03-27",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0230",
    sku: "SKU-PHARMA-0070",
    lot: "LOT-R1-0230",
    batch: "BT-R1-0461",
    barcode: "7501234003911",
    supplierCode: "SUP-MX-0230",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-18",
    mfgDate: "2025-04-02",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0231",
    sku: "SKU-PHARMA-0071",
    lot: "LOT-R1-0231",
    batch: "BT-R1-0463",
    barcode: "7501234003928",
    supplierCode: "SUP-MX-0231",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-25",
    mfgDate: "2025-05-04",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0232",
    sku: "SKU-PHARMA-0072",
    lot: "LOT-R1-0232",
    batch: "BT-R1-0465",
    barcode: "7501234003945",
    supplierCode: "SUP-MX-0232",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-05",
    mfgDate: "2025-06-06",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0233",
    sku: "SKU-PHARMA-0073",
    lot: "LOT-R1-0233",
    batch: "BT-R1-0467",
    barcode: "7501234003962",
    supplierCode: "SUP-MX-0233",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-12",
    mfgDate: "2025-07-08",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0234",
    sku: "SKU-PHARMA-0074",
    lot: "LOT-R1-0234",
    batch: "BT-R1-0469",
    barcode: "7501234003979",
    supplierCode: "SUP-MX-0234",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-19",
    mfgDate: "2025-08-10",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0235",
    sku: "SKU-PHARMA-0075",
    lot: "LOT-R1-0235",
    batch: "BT-R1-0471",
    barcode: "7501234003996",
    supplierCode: "SUP-MX-0235",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-26",
    mfgDate: "2025-09-12",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0236",
    sku: "SKU-PHARMA-0076",
    lot: "LOT-R1-0236",
    batch: "BT-R1-0473",
    barcode: "7501234004013",
    supplierCode: "SUP-MX-0236",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-06",
    mfgDate: "2025-10-14",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0237",
    sku: "SKU-PHARMA-0077",
    lot: "LOT-R1-0237",
    batch: "BT-R1-0475",
    barcode: "7501234004030",
    supplierCode: "SUP-MX-0237",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-13",
    mfgDate: "2025-11-16",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0238",
    sku: "SKU-PHARMA-0078",
    lot: "LOT-R1-0238",
    batch: "BT-R1-0477",
    barcode: "7501234004047",
    supplierCode: "SUP-MX-0238",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-20",
    mfgDate: "2025-12-18",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0239",
    sku: "SKU-PHARMA-0079",
    lot: "LOT-R1-0239",
    batch: "BT-R1-0479",
    barcode: "7501234004064",
    supplierCode: "SUP-MX-0239",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-27",
    mfgDate: "2025-01-20",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0240",
    sku: "SKU-PHARMA-0080",
    lot: "LOT-R1-0240",
    batch: "BT-R1-0481",
    barcode: "7501234004081",
    supplierCode: "SUP-MX-0240",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-07",
    mfgDate: "2025-02-22",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0241",
    sku: "SKU-PHARMA-0081",
    lot: "LOT-R1-0241",
    batch: "BT-R1-0483",
    barcode: "7501234004098",
    supplierCode: "SUP-MX-0241",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-14",
    mfgDate: "2025-03-24",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0242",
    sku: "SKU-PHARMA-0082",
    lot: "LOT-R1-0242",
    batch: "BT-R1-0485",
    barcode: "7501234004115",
    supplierCode: "SUP-MX-0242",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-21",
    mfgDate: "2025-04-26",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0243",
    sku: "SKU-PHARMA-0083",
    lot: "LOT-R1-0243",
    batch: "BT-R1-0487",
    barcode: "7501234004132",
    supplierCode: "SUP-MX-0243",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-01",
    mfgDate: "2025-05-01",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0244",
    sku: "SKU-PHARMA-0084",
    lot: "LOT-R1-0244",
    batch: "BT-R1-0489",
    barcode: "7501234004149",
    supplierCode: "SUP-MX-0244",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-08",
    mfgDate: "2025-06-03",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0245",
    sku: "SKU-PHARMA-0085",
    lot: "LOT-R1-0245",
    batch: "BT-R1-0491",
    barcode: "7501234004166",
    supplierCode: "SUP-MX-0245",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-15",
    mfgDate: "2025-07-05",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0246",
    sku: "SKU-PHARMA-0086",
    lot: "LOT-R1-0246",
    batch: "BT-R1-0493",
    barcode: "7501234004183",
    supplierCode: "SUP-MX-0246",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-22",
    mfgDate: "2025-08-07",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0247",
    sku: "SKU-PHARMA-0087",
    lot: "LOT-R1-0247",
    batch: "BT-R1-0495",
    barcode: "7501234004200",
    supplierCode: "SUP-MX-0247",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-02",
    mfgDate: "2025-09-09",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0248",
    sku: "SKU-PHARMA-0088",
    lot: "LOT-R1-0248",
    batch: "BT-R1-0497",
    barcode: "7501234004217",
    supplierCode: "SUP-MX-0248",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-09",
    mfgDate: "2025-10-11",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0249",
    sku: "SKU-PHARMA-0089",
    lot: "LOT-R1-0249",
    batch: "BT-R1-0499",
    barcode: "7501234004234",
    supplierCode: "SUP-MX-0249",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-16",
    mfgDate: "2025-11-13",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0250",
    sku: "SKU-PHARMA-0090",
    lot: "LOT-R1-0250",
    batch: "BT-R1-0501",
    barcode: "7501234004251",
    supplierCode: "SUP-MX-0250",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-23",
    mfgDate: "2025-12-15",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0251",
    sku: "SKU-PHARMA-0091",
    lot: "LOT-R1-0251",
    batch: "BT-R1-0503",
    barcode: "7501234004268",
    supplierCode: "SUP-MX-0251",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-03",
    mfgDate: "2025-01-17",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0252",
    sku: "SKU-PHARMA-0092",
    lot: "LOT-R1-0252",
    batch: "BT-R1-0505",
    barcode: "7501234004285",
    supplierCode: "SUP-MX-0252",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-10",
    mfgDate: "2025-02-19",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0253",
    sku: "SKU-PHARMA-0093",
    lot: "LOT-R1-0253",
    batch: "BT-R1-0507",
    barcode: "7501234004302",
    supplierCode: "SUP-MX-0253",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-17",
    mfgDate: "2025-03-21",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0254",
    sku: "SKU-PHARMA-0094",
    lot: "LOT-R1-0254",
    batch: "BT-R1-0509",
    barcode: "7501234004319",
    supplierCode: "SUP-MX-0254",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-24",
    mfgDate: "2025-04-23",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0255",
    sku: "SKU-PHARMA-0095",
    lot: "LOT-R1-0255",
    batch: "BT-R1-0511",
    barcode: "7501234004336",
    supplierCode: "SUP-MX-0255",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-04",
    mfgDate: "2025-05-25",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0256",
    sku: "SKU-PHARMA-0096",
    lot: "LOT-R1-0256",
    batch: "BT-R1-0513",
    barcode: "7501234004353",
    supplierCode: "SUP-MX-0256",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-11",
    mfgDate: "2025-06-27",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0257",
    sku: "SKU-PHARMA-0097",
    lot: "LOT-R1-0257",
    batch: "BT-R1-0515",
    barcode: "7501234004370",
    supplierCode: "SUP-MX-0257",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-18",
    mfgDate: "2025-07-02",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0258",
    sku: "SKU-PHARMA-0098",
    lot: "LOT-R1-0258",
    batch: "BT-R1-0517",
    barcode: "7501234004387",
    supplierCode: "SUP-MX-0258",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-25",
    mfgDate: "2025-08-04",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0259",
    sku: "SKU-PHARMA-0099",
    lot: "LOT-R1-0259",
    batch: "BT-R1-0519",
    barcode: "7501234004404",
    supplierCode: "SUP-MX-0259",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-05",
    mfgDate: "2025-09-06",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0260",
    sku: "SKU-PHARMA-0100",
    lot: "LOT-R1-0260",
    batch: "BT-R1-0521",
    barcode: "7501234004421",
    supplierCode: "SUP-MX-0260",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-12",
    mfgDate: "2025-10-08",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0261",
    sku: "SKU-PHARMA-0101",
    lot: "LOT-R1-0261",
    batch: "BT-R1-0523",
    barcode: "7501234004438",
    supplierCode: "SUP-MX-0261",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-19",
    mfgDate: "2025-11-10",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0262",
    sku: "SKU-PHARMA-0102",
    lot: "LOT-R1-0262",
    batch: "BT-R1-0525",
    barcode: "7501234004455",
    supplierCode: "SUP-MX-0262",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-26",
    mfgDate: "2025-12-12",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0263",
    sku: "SKU-PHARMA-0103",
    lot: "LOT-R1-0263",
    batch: "BT-R1-0527",
    barcode: "7501234004472",
    supplierCode: "SUP-MX-0263",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-06",
    mfgDate: "2025-01-14",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0264",
    sku: "SKU-PHARMA-0104",
    lot: "LOT-R1-0264",
    batch: "BT-R1-0529",
    barcode: "7501234004489",
    supplierCode: "SUP-MX-0264",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-13",
    mfgDate: "2025-02-16",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0265",
    sku: "SKU-PHARMA-0105",
    lot: "LOT-R1-0265",
    batch: "BT-R1-0531",
    barcode: "7501234004506",
    supplierCode: "SUP-MX-0265",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-20",
    mfgDate: "2025-03-18",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0266",
    sku: "SKU-PHARMA-0106",
    lot: "LOT-R1-0266",
    batch: "BT-R1-0533",
    barcode: "7501234004523",
    supplierCode: "SUP-MX-0266",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-27",
    mfgDate: "2025-04-20",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0267",
    sku: "SKU-PHARMA-0107",
    lot: "LOT-R1-0267",
    batch: "BT-R1-0535",
    barcode: "7501234004540",
    supplierCode: "SUP-MX-0267",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-07",
    mfgDate: "2025-05-22",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0268",
    sku: "SKU-PHARMA-0108",
    lot: "LOT-R1-0268",
    batch: "BT-R1-0537",
    barcode: "7501234004557",
    supplierCode: "SUP-MX-0268",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-14",
    mfgDate: "2025-06-24",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0269",
    sku: "SKU-PHARMA-0109",
    lot: "LOT-R1-0269",
    batch: "BT-R1-0539",
    barcode: "7501234004574",
    supplierCode: "SUP-MX-0269",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-21",
    mfgDate: "2025-07-26",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0270",
    sku: "SKU-PHARMA-0110",
    lot: "LOT-R1-0270",
    batch: "BT-R1-0541",
    barcode: "7501234004591",
    supplierCode: "SUP-MX-0270",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-01",
    mfgDate: "2025-08-01",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0271",
    sku: "SKU-PHARMA-0111",
    lot: "LOT-R1-0271",
    batch: "BT-R1-0543",
    barcode: "7501234004608",
    supplierCode: "SUP-MX-0271",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-08",
    mfgDate: "2025-09-03",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0272",
    sku: "SKU-PHARMA-0112",
    lot: "LOT-R1-0272",
    batch: "BT-R1-0545",
    barcode: "7501234004625",
    supplierCode: "SUP-MX-0272",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-15",
    mfgDate: "2025-10-05",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0273",
    sku: "SKU-PHARMA-0113",
    lot: "LOT-R1-0273",
    batch: "BT-R1-0547",
    barcode: "7501234004642",
    supplierCode: "SUP-MX-0273",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-22",
    mfgDate: "2025-11-07",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0274",
    sku: "SKU-PHARMA-0114",
    lot: "LOT-R1-0274",
    batch: "BT-R1-0549",
    barcode: "7501234004659",
    supplierCode: "SUP-MX-0274",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-02",
    mfgDate: "2025-12-09",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0275",
    sku: "SKU-PHARMA-0115",
    lot: "LOT-R1-0275",
    batch: "BT-R1-0551",
    barcode: "7501234004676",
    supplierCode: "SUP-MX-0275",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-09",
    mfgDate: "2025-01-11",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0276",
    sku: "SKU-PHARMA-0116",
    lot: "LOT-R1-0276",
    batch: "BT-R1-0553",
    barcode: "7501234004693",
    supplierCode: "SUP-MX-0276",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-16",
    mfgDate: "2025-02-13",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0277",
    sku: "SKU-PHARMA-0117",
    lot: "LOT-R1-0277",
    batch: "BT-R1-0555",
    barcode: "7501234004710",
    supplierCode: "SUP-MX-0277",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-23",
    mfgDate: "2025-03-15",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0278",
    sku: "SKU-PHARMA-0118",
    lot: "LOT-R1-0278",
    batch: "BT-R1-0557",
    barcode: "7501234004727",
    supplierCode: "SUP-MX-0278",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-03",
    mfgDate: "2025-04-17",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0279",
    sku: "SKU-PHARMA-0119",
    lot: "LOT-R1-0279",
    batch: "BT-R1-0559",
    barcode: "7501234004744",
    supplierCode: "SUP-MX-0279",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-10",
    mfgDate: "2025-05-19",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0280",
    sku: "SKU-PHARMA-0120",
    lot: "LOT-R1-0280",
    batch: "BT-R1-0561",
    barcode: "7501234004761",
    supplierCode: "SUP-MX-0280",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-17",
    mfgDate: "2025-06-21",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0281",
    sku: "SKU-PHARMA-0121",
    lot: "LOT-R1-0281",
    batch: "BT-R1-0563",
    barcode: "7501234004778",
    supplierCode: "SUP-MX-0281",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-24",
    mfgDate: "2025-07-23",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0282",
    sku: "SKU-PHARMA-0122",
    lot: "LOT-R1-0282",
    batch: "BT-R1-0565",
    barcode: "7501234004795",
    supplierCode: "SUP-MX-0282",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-04",
    mfgDate: "2025-08-25",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0283",
    sku: "SKU-PHARMA-0123",
    lot: "LOT-R1-0283",
    batch: "BT-R1-0567",
    barcode: "7501234004812",
    supplierCode: "SUP-MX-0283",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-11",
    mfgDate: "2025-09-27",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0284",
    sku: "SKU-PHARMA-0124",
    lot: "LOT-R1-0284",
    batch: "BT-R1-0569",
    barcode: "7501234004829",
    supplierCode: "SUP-MX-0284",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-18",
    mfgDate: "2025-10-02",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0285",
    sku: "SKU-PHARMA-0125",
    lot: "LOT-R1-0285",
    batch: "BT-R1-0571",
    barcode: "7501234004846",
    supplierCode: "SUP-MX-0285",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-25",
    mfgDate: "2025-11-04",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0286",
    sku: "SKU-PHARMA-0126",
    lot: "LOT-R1-0286",
    batch: "BT-R1-0573",
    barcode: "7501234004863",
    supplierCode: "SUP-MX-0286",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-05",
    mfgDate: "2025-12-06",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0287",
    sku: "SKU-PHARMA-0127",
    lot: "LOT-R1-0287",
    batch: "BT-R1-0575",
    barcode: "7501234004880",
    supplierCode: "SUP-MX-0287",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-12",
    mfgDate: "2025-01-08",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0288",
    sku: "SKU-PHARMA-0128",
    lot: "LOT-R1-0288",
    batch: "BT-R1-0577",
    barcode: "7501234004897",
    supplierCode: "SUP-MX-0288",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-19",
    mfgDate: "2025-02-10",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0289",
    sku: "SKU-PHARMA-0129",
    lot: "LOT-R1-0289",
    batch: "BT-R1-0579",
    barcode: "7501234004914",
    supplierCode: "SUP-MX-0289",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-26",
    mfgDate: "2025-03-12",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0290",
    sku: "SKU-PHARMA-0130",
    lot: "LOT-R1-0290",
    batch: "BT-R1-0581",
    barcode: "7501234004931",
    supplierCode: "SUP-MX-0290",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-06",
    mfgDate: "2025-04-14",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0291",
    sku: "SKU-PHARMA-0131",
    lot: "LOT-R1-0291",
    batch: "BT-R1-0583",
    barcode: "7501234004948",
    supplierCode: "SUP-MX-0291",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-13",
    mfgDate: "2025-05-16",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0292",
    sku: "SKU-PHARMA-0132",
    lot: "LOT-R1-0292",
    batch: "BT-R1-0585",
    barcode: "7501234004965",
    supplierCode: "SUP-MX-0292",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-20",
    mfgDate: "2025-06-18",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0293",
    sku: "SKU-PHARMA-0133",
    lot: "LOT-R1-0293",
    batch: "BT-R1-0587",
    barcode: "7501234004982",
    supplierCode: "SUP-MX-0293",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-27",
    mfgDate: "2025-07-20",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0294",
    sku: "SKU-PHARMA-0134",
    lot: "LOT-R1-0294",
    batch: "BT-R1-0589",
    barcode: "7501234004999",
    supplierCode: "SUP-MX-0294",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-07",
    mfgDate: "2025-08-22",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0295",
    sku: "SKU-PHARMA-0135",
    lot: "LOT-R1-0295",
    batch: "BT-R1-0591",
    barcode: "7501234005016",
    supplierCode: "SUP-MX-0295",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-14",
    mfgDate: "2025-09-24",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0296",
    sku: "SKU-PHARMA-0136",
    lot: "LOT-R1-0296",
    batch: "BT-R1-0593",
    barcode: "7501234005033",
    supplierCode: "SUP-MX-0296",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-21",
    mfgDate: "2025-10-26",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0297",
    sku: "SKU-PHARMA-0137",
    lot: "LOT-R1-0297",
    batch: "BT-R1-0595",
    barcode: "7501234005050",
    supplierCode: "SUP-MX-0297",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-01",
    mfgDate: "2025-11-01",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0298",
    sku: "SKU-PHARMA-0138",
    lot: "LOT-R1-0298",
    batch: "BT-R1-0597",
    barcode: "7501234005067",
    supplierCode: "SUP-MX-0298",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-08",
    mfgDate: "2025-12-03",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0299",
    sku: "SKU-PHARMA-0139",
    lot: "LOT-R1-0299",
    batch: "BT-R1-0599",
    barcode: "7501234005084",
    supplierCode: "SUP-MX-0299",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-15",
    mfgDate: "2025-01-05",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0300",
    sku: "SKU-PHARMA-0140",
    lot: "LOT-R1-0300",
    batch: "BT-R1-0601",
    barcode: "7501234005101",
    supplierCode: "SUP-MX-0300",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-22",
    mfgDate: "2025-02-07",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0301",
    sku: "SKU-PHARMA-0141",
    lot: "LOT-R1-0301",
    batch: "BT-R1-0603",
    barcode: "7501234005118",
    supplierCode: "SUP-MX-0301",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-02",
    mfgDate: "2025-03-09",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0302",
    sku: "SKU-PHARMA-0142",
    lot: "LOT-R1-0302",
    batch: "BT-R1-0605",
    barcode: "7501234005135",
    supplierCode: "SUP-MX-0302",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-09",
    mfgDate: "2025-04-11",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0303",
    sku: "SKU-PHARMA-0143",
    lot: "LOT-R1-0303",
    batch: "BT-R1-0607",
    barcode: "7501234005152",
    supplierCode: "SUP-MX-0303",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-16",
    mfgDate: "2025-05-13",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0304",
    sku: "SKU-PHARMA-0144",
    lot: "LOT-R1-0304",
    batch: "BT-R1-0609",
    barcode: "7501234005169",
    supplierCode: "SUP-MX-0304",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-23",
    mfgDate: "2025-06-15",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0305",
    sku: "SKU-PHARMA-0145",
    lot: "LOT-R1-0305",
    batch: "BT-R1-0611",
    barcode: "7501234005186",
    supplierCode: "SUP-MX-0305",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-03",
    mfgDate: "2025-07-17",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0306",
    sku: "SKU-PHARMA-0146",
    lot: "LOT-R1-0306",
    batch: "BT-R1-0613",
    barcode: "7501234005203",
    supplierCode: "SUP-MX-0306",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-10",
    mfgDate: "2025-08-19",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0307",
    sku: "SKU-PHARMA-0147",
    lot: "LOT-R1-0307",
    batch: "BT-R1-0615",
    barcode: "7501234005220",
    supplierCode: "SUP-MX-0307",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-17",
    mfgDate: "2025-09-21",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0308",
    sku: "SKU-PHARMA-0148",
    lot: "LOT-R1-0308",
    batch: "BT-R1-0617",
    barcode: "7501234005237",
    supplierCode: "SUP-MX-0308",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-24",
    mfgDate: "2025-10-23",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0309",
    sku: "SKU-PHARMA-0149",
    lot: "LOT-R1-0309",
    batch: "BT-R1-0619",
    barcode: "7501234005254",
    supplierCode: "SUP-MX-0309",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-04",
    mfgDate: "2025-11-25",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0310",
    sku: "SKU-PHARMA-0150",
    lot: "LOT-R1-0310",
    batch: "BT-R1-0621",
    barcode: "7501234005271",
    supplierCode: "SUP-MX-0310",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-11",
    mfgDate: "2025-12-27",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0311",
    sku: "SKU-PHARMA-0151",
    lot: "LOT-R1-0311",
    batch: "BT-R1-0623",
    barcode: "7501234005288",
    supplierCode: "SUP-MX-0311",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-18",
    mfgDate: "2025-01-02",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0312",
    sku: "SKU-PHARMA-0152",
    lot: "LOT-R1-0312",
    batch: "BT-R1-0625",
    barcode: "7501234005305",
    supplierCode: "SUP-MX-0312",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-25",
    mfgDate: "2025-02-04",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0313",
    sku: "SKU-PHARMA-0153",
    lot: "LOT-R1-0313",
    batch: "BT-R1-0627",
    barcode: "7501234005322",
    supplierCode: "SUP-MX-0313",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-05",
    mfgDate: "2025-03-06",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0314",
    sku: "SKU-PHARMA-0154",
    lot: "LOT-R1-0314",
    batch: "BT-R1-0629",
    barcode: "7501234005339",
    supplierCode: "SUP-MX-0314",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-12",
    mfgDate: "2025-04-08",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0315",
    sku: "SKU-PHARMA-0155",
    lot: "LOT-R1-0315",
    batch: "BT-R1-0631",
    barcode: "7501234005356",
    supplierCode: "SUP-MX-0315",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-19",
    mfgDate: "2025-05-10",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0316",
    sku: "SKU-PHARMA-0156",
    lot: "LOT-R1-0316",
    batch: "BT-R1-0633",
    barcode: "7501234005373",
    supplierCode: "SUP-MX-0316",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-26",
    mfgDate: "2025-06-12",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0317",
    sku: "SKU-PHARMA-0157",
    lot: "LOT-R1-0317",
    batch: "BT-R1-0635",
    barcode: "7501234005390",
    supplierCode: "SUP-MX-0317",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-06",
    mfgDate: "2025-07-14",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0318",
    sku: "SKU-PHARMA-0158",
    lot: "LOT-R1-0318",
    batch: "BT-R1-0637",
    barcode: "7501234005407",
    supplierCode: "SUP-MX-0318",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-13",
    mfgDate: "2025-08-16",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0319",
    sku: "SKU-PHARMA-0159",
    lot: "LOT-R1-0319",
    batch: "BT-R1-0639",
    barcode: "7501234005424",
    supplierCode: "SUP-MX-0319",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-20",
    mfgDate: "2025-09-18",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0320",
    sku: "SKU-PHARMA-0160",
    lot: "LOT-R1-0320",
    batch: "BT-R1-0641",
    barcode: "7501234005441",
    supplierCode: "SUP-MX-0320",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-27",
    mfgDate: "2025-10-20",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0321",
    sku: "SKU-PHARMA-0001",
    lot: "LOT-R1-0321",
    batch: "BT-R1-0643",
    barcode: "7501234005458",
    supplierCode: "SUP-MX-0001",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-07",
    mfgDate: "2025-11-22",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0322",
    sku: "SKU-PHARMA-0002",
    lot: "LOT-R1-0322",
    batch: "BT-R1-0645",
    barcode: "7501234005475",
    supplierCode: "SUP-MX-0002",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-14",
    mfgDate: "2025-12-24",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0323",
    sku: "SKU-PHARMA-0003",
    lot: "LOT-R1-0323",
    batch: "BT-R1-0647",
    barcode: "7501234005492",
    supplierCode: "SUP-MX-0003",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-21",
    mfgDate: "2025-01-26",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0324",
    sku: "SKU-PHARMA-0004",
    lot: "LOT-R1-0324",
    batch: "BT-R1-0649",
    barcode: "7501234005509",
    supplierCode: "SUP-MX-0004",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-01",
    mfgDate: "2025-02-01",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0325",
    sku: "SKU-PHARMA-0005",
    lot: "LOT-R1-0325",
    batch: "BT-R1-0651",
    barcode: "7501234005526",
    supplierCode: "SUP-MX-0005",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-08",
    mfgDate: "2025-03-03",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0326",
    sku: "SKU-PHARMA-0006",
    lot: "LOT-R1-0326",
    batch: "BT-R1-0653",
    barcode: "7501234005543",
    supplierCode: "SUP-MX-0006",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-15",
    mfgDate: "2025-04-05",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0327",
    sku: "SKU-PHARMA-0007",
    lot: "LOT-R1-0327",
    batch: "BT-R1-0655",
    barcode: "7501234005560",
    supplierCode: "SUP-MX-0007",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-22",
    mfgDate: "2025-05-07",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0328",
    sku: "SKU-PHARMA-0008",
    lot: "LOT-R1-0328",
    batch: "BT-R1-0657",
    barcode: "7501234005577",
    supplierCode: "SUP-MX-0008",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-02",
    mfgDate: "2025-06-09",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0329",
    sku: "SKU-PHARMA-0009",
    lot: "LOT-R1-0329",
    batch: "BT-R1-0659",
    barcode: "7501234005594",
    supplierCode: "SUP-MX-0009",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-09",
    mfgDate: "2025-07-11",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0330",
    sku: "SKU-PHARMA-0010",
    lot: "LOT-R1-0330",
    batch: "BT-R1-0661",
    barcode: "7501234005611",
    supplierCode: "SUP-MX-0010",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-16",
    mfgDate: "2025-08-13",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0331",
    sku: "SKU-PHARMA-0011",
    lot: "LOT-R1-0331",
    batch: "BT-R1-0663",
    barcode: "7501234005628",
    supplierCode: "SUP-MX-0011",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-23",
    mfgDate: "2025-09-15",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0332",
    sku: "SKU-PHARMA-0012",
    lot: "LOT-R1-0332",
    batch: "BT-R1-0665",
    barcode: "7501234005645",
    supplierCode: "SUP-MX-0012",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-03",
    mfgDate: "2025-10-17",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0333",
    sku: "SKU-PHARMA-0013",
    lot: "LOT-R1-0333",
    batch: "BT-R1-0667",
    barcode: "7501234005662",
    supplierCode: "SUP-MX-0013",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-10",
    mfgDate: "2025-11-19",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0334",
    sku: "SKU-PHARMA-0014",
    lot: "LOT-R1-0334",
    batch: "BT-R1-0669",
    barcode: "7501234005679",
    supplierCode: "SUP-MX-0014",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-17",
    mfgDate: "2025-12-21",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0335",
    sku: "SKU-PHARMA-0015",
    lot: "LOT-R1-0335",
    batch: "BT-R1-0671",
    barcode: "7501234005696",
    supplierCode: "SUP-MX-0015",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-24",
    mfgDate: "2025-01-23",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0336",
    sku: "SKU-PHARMA-0016",
    lot: "LOT-R1-0336",
    batch: "BT-R1-0673",
    barcode: "7501234005713",
    supplierCode: "SUP-MX-0016",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-04",
    mfgDate: "2025-02-25",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0337",
    sku: "SKU-PHARMA-0017",
    lot: "LOT-R1-0337",
    batch: "BT-R1-0675",
    barcode: "7501234005730",
    supplierCode: "SUP-MX-0017",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-11",
    mfgDate: "2025-03-27",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0338",
    sku: "SKU-PHARMA-0018",
    lot: "LOT-R1-0338",
    batch: "BT-R1-0677",
    barcode: "7501234005747",
    supplierCode: "SUP-MX-0018",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-18",
    mfgDate: "2025-04-02",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0339",
    sku: "SKU-PHARMA-0019",
    lot: "LOT-R1-0339",
    batch: "BT-R1-0679",
    barcode: "7501234005764",
    supplierCode: "SUP-MX-0019",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-25",
    mfgDate: "2025-05-04",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0340",
    sku: "SKU-PHARMA-0020",
    lot: "LOT-R1-0340",
    batch: "BT-R1-0681",
    barcode: "7501234005781",
    supplierCode: "SUP-MX-0020",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-05",
    mfgDate: "2025-06-06",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0341",
    sku: "SKU-PHARMA-0021",
    lot: "LOT-R1-0341",
    batch: "BT-R1-0683",
    barcode: "7501234005798",
    supplierCode: "SUP-MX-0021",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-12",
    mfgDate: "2025-07-08",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0342",
    sku: "SKU-PHARMA-0022",
    lot: "LOT-R1-0342",
    batch: "BT-R1-0685",
    barcode: "7501234005815",
    supplierCode: "SUP-MX-0022",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-19",
    mfgDate: "2025-08-10",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0343",
    sku: "SKU-PHARMA-0023",
    lot: "LOT-R1-0343",
    batch: "BT-R1-0687",
    barcode: "7501234005832",
    supplierCode: "SUP-MX-0023",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-26",
    mfgDate: "2025-09-12",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0344",
    sku: "SKU-PHARMA-0024",
    lot: "LOT-R1-0344",
    batch: "BT-R1-0689",
    barcode: "7501234005849",
    supplierCode: "SUP-MX-0024",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-06",
    mfgDate: "2025-10-14",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0345",
    sku: "SKU-PHARMA-0025",
    lot: "LOT-R1-0345",
    batch: "BT-R1-0691",
    barcode: "7501234005866",
    supplierCode: "SUP-MX-0025",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-13",
    mfgDate: "2025-11-16",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0346",
    sku: "SKU-PHARMA-0026",
    lot: "LOT-R1-0346",
    batch: "BT-R1-0693",
    barcode: "7501234005883",
    supplierCode: "SUP-MX-0026",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-20",
    mfgDate: "2025-12-18",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0347",
    sku: "SKU-PHARMA-0027",
    lot: "LOT-R1-0347",
    batch: "BT-R1-0695",
    barcode: "7501234005900",
    supplierCode: "SUP-MX-0027",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-27",
    mfgDate: "2025-01-20",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0348",
    sku: "SKU-PHARMA-0028",
    lot: "LOT-R1-0348",
    batch: "BT-R1-0697",
    barcode: "7501234005917",
    supplierCode: "SUP-MX-0028",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-07",
    mfgDate: "2025-02-22",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0349",
    sku: "SKU-PHARMA-0029",
    lot: "LOT-R1-0349",
    batch: "BT-R1-0699",
    barcode: "7501234005934",
    supplierCode: "SUP-MX-0029",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-14",
    mfgDate: "2025-03-24",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0350",
    sku: "SKU-PHARMA-0030",
    lot: "LOT-R1-0350",
    batch: "BT-R1-0701",
    barcode: "7501234005951",
    supplierCode: "SUP-MX-0030",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-21",
    mfgDate: "2025-04-26",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0351",
    sku: "SKU-PHARMA-0031",
    lot: "LOT-R1-0351",
    batch: "BT-R1-0703",
    barcode: "7501234005968",
    supplierCode: "SUP-MX-0031",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-01",
    mfgDate: "2025-05-01",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0352",
    sku: "SKU-PHARMA-0032",
    lot: "LOT-R1-0352",
    batch: "BT-R1-0705",
    barcode: "7501234005985",
    supplierCode: "SUP-MX-0032",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-08",
    mfgDate: "2025-06-03",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0353",
    sku: "SKU-PHARMA-0033",
    lot: "LOT-R1-0353",
    batch: "BT-R1-0707",
    barcode: "7501234006002",
    supplierCode: "SUP-MX-0033",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-15",
    mfgDate: "2025-07-05",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0354",
    sku: "SKU-PHARMA-0034",
    lot: "LOT-R1-0354",
    batch: "BT-R1-0709",
    barcode: "7501234006019",
    supplierCode: "SUP-MX-0034",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-22",
    mfgDate: "2025-08-07",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0355",
    sku: "SKU-PHARMA-0035",
    lot: "LOT-R1-0355",
    batch: "BT-R1-0711",
    barcode: "7501234006036",
    supplierCode: "SUP-MX-0035",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-02",
    mfgDate: "2025-09-09",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0356",
    sku: "SKU-PHARMA-0036",
    lot: "LOT-R1-0356",
    batch: "BT-R1-0713",
    barcode: "7501234006053",
    supplierCode: "SUP-MX-0036",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-09",
    mfgDate: "2025-10-11",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0357",
    sku: "SKU-PHARMA-0037",
    lot: "LOT-R1-0357",
    batch: "BT-R1-0715",
    barcode: "7501234006070",
    supplierCode: "SUP-MX-0037",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-16",
    mfgDate: "2025-11-13",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0358",
    sku: "SKU-PHARMA-0038",
    lot: "LOT-R1-0358",
    batch: "BT-R1-0717",
    barcode: "7501234006087",
    supplierCode: "SUP-MX-0038",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-23",
    mfgDate: "2025-12-15",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0359",
    sku: "SKU-PHARMA-0039",
    lot: "LOT-R1-0359",
    batch: "BT-R1-0719",
    barcode: "7501234006104",
    supplierCode: "SUP-MX-0039",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-03",
    mfgDate: "2025-01-17",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0360",
    sku: "SKU-PHARMA-0040",
    lot: "LOT-R1-0360",
    batch: "BT-R1-0721",
    barcode: "7501234006121",
    supplierCode: "SUP-MX-0040",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-10",
    mfgDate: "2025-02-19",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0361",
    sku: "SKU-PHARMA-0041",
    lot: "LOT-R1-0361",
    batch: "BT-R1-0723",
    barcode: "7501234006138",
    supplierCode: "SUP-MX-0041",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-17",
    mfgDate: "2025-03-21",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0362",
    sku: "SKU-PHARMA-0042",
    lot: "LOT-R1-0362",
    batch: "BT-R1-0725",
    barcode: "7501234006155",
    supplierCode: "SUP-MX-0042",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-24",
    mfgDate: "2025-04-23",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0363",
    sku: "SKU-PHARMA-0043",
    lot: "LOT-R1-0363",
    batch: "BT-R1-0727",
    barcode: "7501234006172",
    supplierCode: "SUP-MX-0043",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-04",
    mfgDate: "2025-05-25",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0364",
    sku: "SKU-PHARMA-0044",
    lot: "LOT-R1-0364",
    batch: "BT-R1-0729",
    barcode: "7501234006189",
    supplierCode: "SUP-MX-0044",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-11",
    mfgDate: "2025-06-27",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0365",
    sku: "SKU-PHARMA-0045",
    lot: "LOT-R1-0365",
    batch: "BT-R1-0731",
    barcode: "7501234006206",
    supplierCode: "SUP-MX-0045",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-18",
    mfgDate: "2025-07-02",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0366",
    sku: "SKU-PHARMA-0046",
    lot: "LOT-R1-0366",
    batch: "BT-R1-0733",
    barcode: "7501234006223",
    supplierCode: "SUP-MX-0046",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-25",
    mfgDate: "2025-08-04",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0367",
    sku: "SKU-PHARMA-0047",
    lot: "LOT-R1-0367",
    batch: "BT-R1-0735",
    barcode: "7501234006240",
    supplierCode: "SUP-MX-0047",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-05",
    mfgDate: "2025-09-06",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0368",
    sku: "SKU-PHARMA-0048",
    lot: "LOT-R1-0368",
    batch: "BT-R1-0737",
    barcode: "7501234006257",
    supplierCode: "SUP-MX-0048",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-12",
    mfgDate: "2025-10-08",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0369",
    sku: "SKU-PHARMA-0049",
    lot: "LOT-R1-0369",
    batch: "BT-R1-0739",
    barcode: "7501234006274",
    supplierCode: "SUP-MX-0049",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-19",
    mfgDate: "2025-11-10",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0370",
    sku: "SKU-PHARMA-0050",
    lot: "LOT-R1-0370",
    batch: "BT-R1-0741",
    barcode: "7501234006291",
    supplierCode: "SUP-MX-0050",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-26",
    mfgDate: "2025-12-12",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0371",
    sku: "SKU-PHARMA-0051",
    lot: "LOT-R1-0371",
    batch: "BT-R1-0743",
    barcode: "7501234006308",
    supplierCode: "SUP-MX-0051",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-06",
    mfgDate: "2025-01-14",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0372",
    sku: "SKU-PHARMA-0052",
    lot: "LOT-R1-0372",
    batch: "BT-R1-0745",
    barcode: "7501234006325",
    supplierCode: "SUP-MX-0052",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-13",
    mfgDate: "2025-02-16",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0373",
    sku: "SKU-PHARMA-0053",
    lot: "LOT-R1-0373",
    batch: "BT-R1-0747",
    barcode: "7501234006342",
    supplierCode: "SUP-MX-0053",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-20",
    mfgDate: "2025-03-18",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0374",
    sku: "SKU-PHARMA-0054",
    lot: "LOT-R1-0374",
    batch: "BT-R1-0749",
    barcode: "7501234006359",
    supplierCode: "SUP-MX-0054",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-27",
    mfgDate: "2025-04-20",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0375",
    sku: "SKU-PHARMA-0055",
    lot: "LOT-R1-0375",
    batch: "BT-R1-0751",
    barcode: "7501234006376",
    supplierCode: "SUP-MX-0055",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-07",
    mfgDate: "2025-05-22",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0376",
    sku: "SKU-PHARMA-0056",
    lot: "LOT-R1-0376",
    batch: "BT-R1-0753",
    barcode: "7501234006393",
    supplierCode: "SUP-MX-0056",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-14",
    mfgDate: "2025-06-24",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0377",
    sku: "SKU-PHARMA-0057",
    lot: "LOT-R1-0377",
    batch: "BT-R1-0755",
    barcode: "7501234006410",
    supplierCode: "SUP-MX-0057",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-21",
    mfgDate: "2025-07-26",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0378",
    sku: "SKU-PHARMA-0058",
    lot: "LOT-R1-0378",
    batch: "BT-R1-0757",
    barcode: "7501234006427",
    supplierCode: "SUP-MX-0058",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-01",
    mfgDate: "2025-08-01",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0379",
    sku: "SKU-PHARMA-0059",
    lot: "LOT-R1-0379",
    batch: "BT-R1-0759",
    barcode: "7501234006444",
    supplierCode: "SUP-MX-0059",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-08",
    mfgDate: "2025-09-03",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0380",
    sku: "SKU-PHARMA-0060",
    lot: "LOT-R1-0380",
    batch: "BT-R1-0761",
    barcode: "7501234006461",
    supplierCode: "SUP-MX-0060",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-15",
    mfgDate: "2025-10-05",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0381",
    sku: "SKU-PHARMA-0061",
    lot: "LOT-R1-0381",
    batch: "BT-R1-0763",
    barcode: "7501234006478",
    supplierCode: "SUP-MX-0061",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-22",
    mfgDate: "2025-11-07",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0382",
    sku: "SKU-PHARMA-0062",
    lot: "LOT-R1-0382",
    batch: "BT-R1-0765",
    barcode: "7501234006495",
    supplierCode: "SUP-MX-0062",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-02",
    mfgDate: "2025-12-09",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0383",
    sku: "SKU-PHARMA-0063",
    lot: "LOT-R1-0383",
    batch: "BT-R1-0767",
    barcode: "7501234006512",
    supplierCode: "SUP-MX-0063",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-09",
    mfgDate: "2025-01-11",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0384",
    sku: "SKU-PHARMA-0064",
    lot: "LOT-R1-0384",
    batch: "BT-R1-0769",
    barcode: "7501234006529",
    supplierCode: "SUP-MX-0064",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-16",
    mfgDate: "2025-02-13",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0385",
    sku: "SKU-PHARMA-0065",
    lot: "LOT-R1-0385",
    batch: "BT-R1-0771",
    barcode: "7501234006546",
    supplierCode: "SUP-MX-0065",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-23",
    mfgDate: "2025-03-15",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0386",
    sku: "SKU-PHARMA-0066",
    lot: "LOT-R1-0386",
    batch: "BT-R1-0773",
    barcode: "7501234006563",
    supplierCode: "SUP-MX-0066",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-03",
    mfgDate: "2025-04-17",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0387",
    sku: "SKU-PHARMA-0067",
    lot: "LOT-R1-0387",
    batch: "BT-R1-0775",
    barcode: "7501234006580",
    supplierCode: "SUP-MX-0067",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-10",
    mfgDate: "2025-05-19",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0388",
    sku: "SKU-PHARMA-0068",
    lot: "LOT-R1-0388",
    batch: "BT-R1-0777",
    barcode: "7501234006597",
    supplierCode: "SUP-MX-0068",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-17",
    mfgDate: "2025-06-21",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0389",
    sku: "SKU-PHARMA-0069",
    lot: "LOT-R1-0389",
    batch: "BT-R1-0779",
    barcode: "7501234006614",
    supplierCode: "SUP-MX-0069",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-24",
    mfgDate: "2025-07-23",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0390",
    sku: "SKU-PHARMA-0070",
    lot: "LOT-R1-0390",
    batch: "BT-R1-0781",
    barcode: "7501234006631",
    supplierCode: "SUP-MX-0070",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-04",
    mfgDate: "2025-08-25",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0391",
    sku: "SKU-PHARMA-0071",
    lot: "LOT-R1-0391",
    batch: "BT-R1-0783",
    barcode: "7501234006648",
    supplierCode: "SUP-MX-0071",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-11",
    mfgDate: "2025-09-27",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0392",
    sku: "SKU-PHARMA-0072",
    lot: "LOT-R1-0392",
    batch: "BT-R1-0785",
    barcode: "7501234006665",
    supplierCode: "SUP-MX-0072",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-18",
    mfgDate: "2025-10-02",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0393",
    sku: "SKU-PHARMA-0073",
    lot: "LOT-R1-0393",
    batch: "BT-R1-0787",
    barcode: "7501234006682",
    supplierCode: "SUP-MX-0073",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-25",
    mfgDate: "2025-11-04",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0394",
    sku: "SKU-PHARMA-0074",
    lot: "LOT-R1-0394",
    batch: "BT-R1-0789",
    barcode: "7501234006699",
    supplierCode: "SUP-MX-0074",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-05",
    mfgDate: "2025-12-06",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0395",
    sku: "SKU-PHARMA-0075",
    lot: "LOT-R1-0395",
    batch: "BT-R1-0791",
    barcode: "7501234006716",
    supplierCode: "SUP-MX-0075",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-12",
    mfgDate: "2025-01-08",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0396",
    sku: "SKU-PHARMA-0076",
    lot: "LOT-R1-0396",
    batch: "BT-R1-0793",
    barcode: "7501234006733",
    supplierCode: "SUP-MX-0076",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-19",
    mfgDate: "2025-02-10",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0397",
    sku: "SKU-PHARMA-0077",
    lot: "LOT-R1-0397",
    batch: "BT-R1-0795",
    barcode: "7501234006750",
    supplierCode: "SUP-MX-0077",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-26",
    mfgDate: "2025-03-12",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0398",
    sku: "SKU-PHARMA-0078",
    lot: "LOT-R1-0398",
    batch: "BT-R1-0797",
    barcode: "7501234006767",
    supplierCode: "SUP-MX-0078",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-06",
    mfgDate: "2025-04-14",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0399",
    sku: "SKU-PHARMA-0079",
    lot: "LOT-R1-0399",
    batch: "BT-R1-0799",
    barcode: "7501234006784",
    supplierCode: "SUP-MX-0079",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-13",
    mfgDate: "2025-05-16",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0400",
    sku: "SKU-PHARMA-0080",
    lot: "LOT-R1-0400",
    batch: "BT-R1-0801",
    barcode: "7501234006801",
    supplierCode: "SUP-MX-0080",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-20",
    mfgDate: "2025-06-18",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0401",
    sku: "SKU-PHARMA-0081",
    lot: "LOT-R1-0401",
    batch: "BT-R1-0803",
    barcode: "7501234006818",
    supplierCode: "SUP-MX-0081",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-27",
    mfgDate: "2025-07-20",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0402",
    sku: "SKU-PHARMA-0082",
    lot: "LOT-R1-0402",
    batch: "BT-R1-0805",
    barcode: "7501234006835",
    supplierCode: "SUP-MX-0082",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-07",
    mfgDate: "2025-08-22",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0403",
    sku: "SKU-PHARMA-0083",
    lot: "LOT-R1-0403",
    batch: "BT-R1-0807",
    barcode: "7501234006852",
    supplierCode: "SUP-MX-0083",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-14",
    mfgDate: "2025-09-24",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0404",
    sku: "SKU-PHARMA-0084",
    lot: "LOT-R1-0404",
    batch: "BT-R1-0809",
    barcode: "7501234006869",
    supplierCode: "SUP-MX-0084",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-21",
    mfgDate: "2025-10-26",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0405",
    sku: "SKU-PHARMA-0085",
    lot: "LOT-R1-0405",
    batch: "BT-R1-0811",
    barcode: "7501234006886",
    supplierCode: "SUP-MX-0085",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-01",
    mfgDate: "2025-11-01",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0406",
    sku: "SKU-PHARMA-0086",
    lot: "LOT-R1-0406",
    batch: "BT-R1-0813",
    barcode: "7501234006903",
    supplierCode: "SUP-MX-0086",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-08",
    mfgDate: "2025-12-03",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0407",
    sku: "SKU-PHARMA-0087",
    lot: "LOT-R1-0407",
    batch: "BT-R1-0815",
    barcode: "7501234006920",
    supplierCode: "SUP-MX-0087",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-15",
    mfgDate: "2025-01-05",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0408",
    sku: "SKU-PHARMA-0088",
    lot: "LOT-R1-0408",
    batch: "BT-R1-0817",
    barcode: "7501234006937",
    supplierCode: "SUP-MX-0088",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-22",
    mfgDate: "2025-02-07",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0409",
    sku: "SKU-PHARMA-0089",
    lot: "LOT-R1-0409",
    batch: "BT-R1-0819",
    barcode: "7501234006954",
    supplierCode: "SUP-MX-0089",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-02",
    mfgDate: "2025-03-09",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0410",
    sku: "SKU-PHARMA-0090",
    lot: "LOT-R1-0410",
    batch: "BT-R1-0821",
    barcode: "7501234006971",
    supplierCode: "SUP-MX-0090",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-09",
    mfgDate: "2025-04-11",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0411",
    sku: "SKU-PHARMA-0091",
    lot: "LOT-R1-0411",
    batch: "BT-R1-0823",
    barcode: "7501234006988",
    supplierCode: "SUP-MX-0091",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-16",
    mfgDate: "2025-05-13",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0412",
    sku: "SKU-PHARMA-0092",
    lot: "LOT-R1-0412",
    batch: "BT-R1-0825",
    barcode: "7501234007005",
    supplierCode: "SUP-MX-0092",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-23",
    mfgDate: "2025-06-15",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0413",
    sku: "SKU-PHARMA-0093",
    lot: "LOT-R1-0413",
    batch: "BT-R1-0827",
    barcode: "7501234007022",
    supplierCode: "SUP-MX-0093",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-03",
    mfgDate: "2025-07-17",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0414",
    sku: "SKU-PHARMA-0094",
    lot: "LOT-R1-0414",
    batch: "BT-R1-0829",
    barcode: "7501234007039",
    supplierCode: "SUP-MX-0094",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-10",
    mfgDate: "2025-08-19",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0415",
    sku: "SKU-PHARMA-0095",
    lot: "LOT-R1-0415",
    batch: "BT-R1-0831",
    barcode: "7501234007056",
    supplierCode: "SUP-MX-0095",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-17",
    mfgDate: "2025-09-21",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0416",
    sku: "SKU-PHARMA-0096",
    lot: "LOT-R1-0416",
    batch: "BT-R1-0833",
    barcode: "7501234007073",
    supplierCode: "SUP-MX-0096",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-24",
    mfgDate: "2025-10-23",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0417",
    sku: "SKU-PHARMA-0097",
    lot: "LOT-R1-0417",
    batch: "BT-R1-0835",
    barcode: "7501234007090",
    supplierCode: "SUP-MX-0097",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-04",
    mfgDate: "2025-11-25",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0418",
    sku: "SKU-PHARMA-0098",
    lot: "LOT-R1-0418",
    batch: "BT-R1-0837",
    barcode: "7501234007107",
    supplierCode: "SUP-MX-0098",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-11",
    mfgDate: "2025-12-27",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0419",
    sku: "SKU-PHARMA-0099",
    lot: "LOT-R1-0419",
    batch: "BT-R1-0839",
    barcode: "7501234007124",
    supplierCode: "SUP-MX-0099",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-18",
    mfgDate: "2025-01-02",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0420",
    sku: "SKU-PHARMA-0100",
    lot: "LOT-R1-0420",
    batch: "BT-R1-0841",
    barcode: "7501234007141",
    supplierCode: "SUP-MX-0100",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-25",
    mfgDate: "2025-02-04",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0421",
    sku: "SKU-PHARMA-0101",
    lot: "LOT-R1-0421",
    batch: "BT-R1-0843",
    barcode: "7501234007158",
    supplierCode: "SUP-MX-0101",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-07-05",
    mfgDate: "2025-03-06",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0422",
    sku: "SKU-PHARMA-0102",
    lot: "LOT-R1-0422",
    batch: "BT-R1-0845",
    barcode: "7501234007175",
    supplierCode: "SUP-MX-0102",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-08-12",
    mfgDate: "2025-04-08",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0423",
    sku: "SKU-PHARMA-0103",
    lot: "LOT-R1-0423",
    batch: "BT-R1-0847",
    barcode: "7501234007192",
    supplierCode: "SUP-MX-0103",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-09-19",
    mfgDate: "2025-05-10",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0424",
    sku: "SKU-PHARMA-0104",
    lot: "LOT-R1-0424",
    batch: "BT-R1-0849",
    barcode: "7501234007209",
    supplierCode: "SUP-MX-0104",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-10-26",
    mfgDate: "2025-06-12",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0425",
    sku: "SKU-PHARMA-0105",
    lot: "LOT-R1-0425",
    batch: "BT-R1-0851",
    barcode: "7501234007226",
    supplierCode: "SUP-MX-0105",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-11-06",
    mfgDate: "2025-07-14",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0426",
    sku: "SKU-PHARMA-0106",
    lot: "LOT-R1-0426",
    batch: "BT-R1-0853",
    barcode: "7501234007243",
    supplierCode: "SUP-MX-0106",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-12-13",
    mfgDate: "2025-08-16",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0427",
    sku: "SKU-PHARMA-0107",
    lot: "LOT-R1-0427",
    batch: "BT-R1-0855",
    barcode: "7501234007260",
    supplierCode: "SUP-MX-0107",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-01-20",
    mfgDate: "2025-09-18",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0428",
    sku: "SKU-PHARMA-0108",
    lot: "LOT-R1-0428",
    batch: "BT-R1-0857",
    barcode: "7501234007277",
    supplierCode: "SUP-MX-0108",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-02-27",
    mfgDate: "2025-10-20",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0429",
    sku: "SKU-PHARMA-0109",
    lot: "LOT-R1-0429",
    batch: "BT-R1-0859",
    barcode: "7501234007294",
    supplierCode: "SUP-MX-0109",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-03-07",
    mfgDate: "2025-11-22",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0430",
    sku: "SKU-PHARMA-0110",
    lot: "LOT-R1-0430",
    batch: "BT-R1-0861",
    barcode: "7501234007311",
    supplierCode: "SUP-MX-0110",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-04-14",
    mfgDate: "2025-12-24",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0431",
    sku: "SKU-PHARMA-0111",
    lot: "LOT-R1-0431",
    batch: "BT-R1-0863",
    barcode: "7501234007328",
    supplierCode: "SUP-MX-0111",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-05-21",
    mfgDate: "2025-01-26",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0432",
    sku: "SKU-PHARMA-0112",
    lot: "LOT-R1-0432",
    batch: "BT-R1-0865",
    barcode: "7501234007345",
    supplierCode: "SUP-MX-0112",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-06-01",
    mfgDate: "2025-02-01",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0433",
    sku: "SKU-PHARMA-0113",
    lot: "LOT-R1-0433",
    batch: "BT-R1-0867",
    barcode: "7501234007362",
    supplierCode: "SUP-MX-0113",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-07-08",
    mfgDate: "2025-03-03",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0434",
    sku: "SKU-PHARMA-0114",
    lot: "LOT-R1-0434",
    batch: "BT-R1-0869",
    barcode: "7501234007379",
    supplierCode: "SUP-MX-0114",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-08-15",
    mfgDate: "2025-04-05",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0435",
    sku: "SKU-PHARMA-0115",
    lot: "LOT-R1-0435",
    batch: "BT-R1-0871",
    barcode: "7501234007396",
    supplierCode: "SUP-MX-0115",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-09-22",
    mfgDate: "2025-05-07",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0436",
    sku: "SKU-PHARMA-0116",
    lot: "LOT-R1-0436",
    batch: "BT-R1-0873",
    barcode: "7501234007413",
    supplierCode: "SUP-MX-0116",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-10-02",
    mfgDate: "2025-06-09",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0437",
    sku: "SKU-PHARMA-0117",
    lot: "LOT-R1-0437",
    batch: "BT-R1-0875",
    barcode: "7501234007430",
    supplierCode: "SUP-MX-0117",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-11-09",
    mfgDate: "2025-07-11",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0438",
    sku: "SKU-PHARMA-0118",
    lot: "LOT-R1-0438",
    batch: "BT-R1-0877",
    barcode: "7501234007447",
    supplierCode: "SUP-MX-0118",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-12-16",
    mfgDate: "2025-08-13",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0439",
    sku: "SKU-PHARMA-0119",
    lot: "LOT-R1-0439",
    batch: "BT-R1-0879",
    barcode: "7501234007464",
    supplierCode: "SUP-MX-0119",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-01-23",
    mfgDate: "2025-09-15",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0440",
    sku: "SKU-PHARMA-0120",
    lot: "LOT-R1-0440",
    batch: "BT-R1-0881",
    barcode: "7501234007481",
    supplierCode: "SUP-MX-0120",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-02-03",
    mfgDate: "2025-10-17",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0441",
    sku: "SKU-PHARMA-0121",
    lot: "LOT-R1-0441",
    batch: "BT-R1-0883",
    barcode: "7501234007498",
    supplierCode: "SUP-MX-0121",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-03-10",
    mfgDate: "2025-11-19",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0442",
    sku: "SKU-PHARMA-0122",
    lot: "LOT-R1-0442",
    batch: "BT-R1-0885",
    barcode: "7501234007515",
    supplierCode: "SUP-MX-0122",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-04-17",
    mfgDate: "2025-12-21",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0443",
    sku: "SKU-PHARMA-0123",
    lot: "LOT-R1-0443",
    batch: "BT-R1-0887",
    barcode: "7501234007532",
    supplierCode: "SUP-MX-0123",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-05-24",
    mfgDate: "2025-01-23",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0444",
    sku: "SKU-PHARMA-0124",
    lot: "LOT-R1-0444",
    batch: "BT-R1-0889",
    barcode: "7501234007549",
    supplierCode: "SUP-MX-0124",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-06-04",
    mfgDate: "2025-02-25",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0445",
    sku: "SKU-PHARMA-0125",
    lot: "LOT-R1-0445",
    batch: "BT-R1-0891",
    barcode: "7501234007566",
    supplierCode: "SUP-MX-0125",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-07-11",
    mfgDate: "2025-03-27",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0446",
    sku: "SKU-PHARMA-0126",
    lot: "LOT-R1-0446",
    batch: "BT-R1-0893",
    barcode: "7501234007583",
    supplierCode: "SUP-MX-0126",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-08-18",
    mfgDate: "2025-04-02",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0447",
    sku: "SKU-PHARMA-0127",
    lot: "LOT-R1-0447",
    batch: "BT-R1-0895",
    barcode: "7501234007600",
    supplierCode: "SUP-MX-0127",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-09-25",
    mfgDate: "2025-05-04",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0448",
    sku: "SKU-PHARMA-0128",
    lot: "LOT-R1-0448",
    batch: "BT-R1-0897",
    barcode: "7501234007617",
    supplierCode: "SUP-MX-0128",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-10-05",
    mfgDate: "2025-06-06",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0449",
    sku: "SKU-PHARMA-0129",
    lot: "LOT-R1-0449",
    batch: "BT-R1-0899",
    barcode: "7501234007634",
    supplierCode: "SUP-MX-0129",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-11-12",
    mfgDate: "2025-07-08",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0450",
    sku: "SKU-PHARMA-0130",
    lot: "LOT-R1-0450",
    batch: "BT-R1-0901",
    barcode: "7501234007651",
    supplierCode: "SUP-MX-0130",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-12-19",
    mfgDate: "2025-08-10",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0451",
    sku: "SKU-PHARMA-0131",
    lot: "LOT-R1-0451",
    batch: "BT-R1-0903",
    barcode: "7501234007668",
    supplierCode: "SUP-MX-0131",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-01-26",
    mfgDate: "2025-09-12",
    excursionCount30d: 3,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0452",
    sku: "SKU-PHARMA-0132",
    lot: "LOT-R1-0452",
    batch: "BT-R1-0905",
    barcode: "7501234007685",
    supplierCode: "SUP-MX-0132",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-02-06",
    mfgDate: "2025-10-14",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0453",
    sku: "SKU-PHARMA-0133",
    lot: "LOT-R1-0453",
    batch: "BT-R1-0907",
    barcode: "7501234007702",
    supplierCode: "SUP-MX-0133",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-03-13",
    mfgDate: "2025-11-16",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0454",
    sku: "SKU-PHARMA-0134",
    lot: "LOT-R1-0454",
    batch: "BT-R1-0909",
    barcode: "7501234007719",
    supplierCode: "SUP-MX-0134",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-04-20",
    mfgDate: "2025-12-18",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0455",
    sku: "SKU-PHARMA-0135",
    lot: "LOT-R1-0455",
    batch: "BT-R1-0911",
    barcode: "7501234007736",
    supplierCode: "SUP-MX-0135",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-05-27",
    mfgDate: "2025-01-20",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0456",
    sku: "SKU-PHARMA-0136",
    lot: "LOT-R1-0456",
    batch: "BT-R1-0913",
    barcode: "7501234007753",
    supplierCode: "SUP-MX-0136",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-06-07",
    mfgDate: "2025-02-22",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0457",
    sku: "SKU-PHARMA-0137",
    lot: "LOT-R1-0457",
    batch: "BT-R1-0915",
    barcode: "7501234007770",
    supplierCode: "SUP-MX-0137",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-07-14",
    mfgDate: "2025-03-24",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0458",
    sku: "SKU-PHARMA-0138",
    lot: "LOT-R1-0458",
    batch: "BT-R1-0917",
    barcode: "7501234007787",
    supplierCode: "SUP-MX-0138",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-08-21",
    mfgDate: "2025-04-26",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0459",
    sku: "SKU-PHARMA-0139",
    lot: "LOT-R1-0459",
    batch: "BT-R1-0919",
    barcode: "7501234007804",
    supplierCode: "SUP-MX-0139",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-09-01",
    mfgDate: "2025-05-01",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0460",
    sku: "SKU-PHARMA-0140",
    lot: "LOT-R1-0460",
    batch: "BT-R1-0921",
    barcode: "7501234007821",
    supplierCode: "SUP-MX-0140",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-10-08",
    mfgDate: "2025-06-03",
    excursionCount30d: 0,
    holdFlag: true,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0461",
    sku: "SKU-PHARMA-0141",
    lot: "LOT-R1-0461",
    batch: "BT-R1-0923",
    barcode: "7501234007838",
    supplierCode: "SUP-MX-0141",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-11-15",
    mfgDate: "2025-07-05",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0462",
    sku: "SKU-PHARMA-0142",
    lot: "LOT-R1-0462",
    batch: "BT-R1-0925",
    barcode: "7501234007855",
    supplierCode: "SUP-MX-0142",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-12-22",
    mfgDate: "2025-08-07",
    excursionCount30d: 2,
    holdFlag: true,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0463",
    sku: "SKU-PHARMA-0143",
    lot: "LOT-R1-0463",
    batch: "BT-R1-0927",
    barcode: "7501234007872",
    supplierCode: "SUP-MX-0143",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-01-02",
    mfgDate: "2025-09-09",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0464",
    sku: "SKU-PHARMA-0144",
    lot: "LOT-R1-0464",
    batch: "BT-R1-0929",
    barcode: "7501234007889",
    supplierCode: "SUP-MX-0144",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-02-09",
    mfgDate: "2025-10-11",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0465",
    sku: "SKU-PHARMA-0145",
    lot: "LOT-R1-0465",
    batch: "BT-R1-0931",
    barcode: "7501234007906",
    supplierCode: "SUP-MX-0145",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-03-16",
    mfgDate: "2025-11-13",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0466",
    sku: "SKU-PHARMA-0146",
    lot: "LOT-R1-0466",
    batch: "BT-R1-0933",
    barcode: "7501234007923",
    supplierCode: "SUP-MX-0146",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-04-23",
    mfgDate: "2025-12-15",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0467",
    sku: "SKU-PHARMA-0147",
    lot: "LOT-R1-0467",
    batch: "BT-R1-0935",
    barcode: "7501234007940",
    supplierCode: "SUP-MX-0147",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-05-03",
    mfgDate: "2025-01-17",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0468",
    sku: "SKU-PHARMA-0148",
    lot: "LOT-R1-0468",
    batch: "BT-R1-0937",
    barcode: "7501234007957",
    supplierCode: "SUP-MX-0148",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-06-10",
    mfgDate: "2025-02-19",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0469",
    sku: "SKU-PHARMA-0149",
    lot: "LOT-R1-0469",
    batch: "BT-R1-0939",
    barcode: "7501234007974",
    supplierCode: "SUP-MX-0149",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-07-17",
    mfgDate: "2025-03-21",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0470",
    sku: "SKU-PHARMA-0150",
    lot: "LOT-R1-0470",
    batch: "BT-R1-0941",
    barcode: "7501234007991",
    supplierCode: "SUP-MX-0150",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-08-24",
    mfgDate: "2025-04-23",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0471",
    sku: "SKU-PHARMA-0151",
    lot: "LOT-R1-0471",
    batch: "BT-R1-0943",
    barcode: "7501234008008",
    supplierCode: "SUP-MX-0151",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-09-04",
    mfgDate: "2025-05-25",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 36
  },
  {
    id: "foundation-lot-0472",
    sku: "SKU-PHARMA-0152",
    lot: "LOT-R1-0472",
    batch: "BT-R1-0945",
    barcode: "7501234008025",
    supplierCode: "SUP-MX-0152",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-10-11",
    mfgDate: "2025-06-27",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 40
  },
  {
    id: "foundation-lot-0473",
    sku: "SKU-PHARMA-0153",
    lot: "LOT-R1-0473",
    batch: "BT-R1-0947",
    barcode: "7501234008042",
    supplierCode: "SUP-MX-0153",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-11-18",
    mfgDate: "2025-07-02",
    excursionCount30d: 1,
    holdFlag: true,
    releaseWindowHours: 44
  },
  {
    id: "foundation-lot-0474",
    sku: "SKU-PHARMA-0154",
    lot: "LOT-R1-0474",
    batch: "BT-R1-0949",
    barcode: "7501234008059",
    supplierCode: "SUP-MX-0154",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-12-25",
    mfgDate: "2025-08-04",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 48
  },
  {
    id: "foundation-lot-0475",
    sku: "SKU-PHARMA-0155",
    lot: "LOT-R1-0475",
    batch: "BT-R1-0951",
    barcode: "7501234008076",
    supplierCode: "SUP-MX-0155",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-01-05",
    mfgDate: "2025-09-06",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 52
  },
  {
    id: "foundation-lot-0476",
    sku: "SKU-PHARMA-0156",
    lot: "LOT-R1-0476",
    batch: "BT-R1-0953",
    barcode: "7501234008093",
    supplierCode: "SUP-MX-0156",
    temperatureProfile: "2C-8C",
    storageCondition: "Ambient Cage",
    expiryDate: "2027-02-12",
    mfgDate: "2025-10-08",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 56
  },
  {
    id: "foundation-lot-0477",
    sku: "SKU-PHARMA-0157",
    lot: "LOT-R1-0477",
    batch: "BT-R1-0955",
    barcode: "7501234008110",
    supplierCode: "SUP-MX-0157",
    temperatureProfile: "15C-25C",
    storageCondition: "Quarantine Bay",
    expiryDate: "2027-03-19",
    mfgDate: "2025-11-10",
    excursionCount30d: 1,
    holdFlag: false,
    releaseWindowHours: 24
  },
  {
    id: "foundation-lot-0478",
    sku: "SKU-PHARMA-0158",
    lot: "LOT-R1-0478",
    batch: "BT-R1-0957",
    barcode: "7501234008127",
    supplierCode: "SUP-MX-0158",
    temperatureProfile: "-20C",
    storageCondition: "DEA Cage",
    expiryDate: "2027-04-26",
    mfgDate: "2025-12-12",
    excursionCount30d: 2,
    holdFlag: false,
    releaseWindowHours: 28
  },
  {
    id: "foundation-lot-0479",
    sku: "SKU-PHARMA-0159",
    lot: "LOT-R1-0479",
    batch: "BT-R1-0959",
    barcode: "7501234008144",
    supplierCode: "SUP-MX-0159",
    temperatureProfile: "-70C",
    storageCondition: "Cold Room A",
    expiryDate: "2027-05-06",
    mfgDate: "2025-01-14",
    excursionCount30d: 3,
    holdFlag: false,
    releaseWindowHours: 32
  },
  {
    id: "foundation-lot-0480",
    sku: "SKU-PHARMA-0160",
    lot: "LOT-R1-0480",
    batch: "BT-R1-0961",
    barcode: "7501234008161",
    supplierCode: "SUP-MX-0160",
    temperatureProfile: "Ambient Controlled",
    storageCondition: "Cold Room B",
    expiryDate: "2027-06-13",
    mfgDate: "2025-02-16",
    excursionCount30d: 0,
    holdFlag: false,
    releaseWindowHours: 36
  }
];

export const FOUNDATION_TEMPERATURE_EXCURSIONS: readonly TemperatureExcursionRecord[] = [
  {
    id: "excursion-0001",
    lot: "LOT-R1-0004",
    observedAt: "2026-08-06T02:07:00Z",
    durationMinutes: 11,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0002",
    lot: "LOT-R1-0007",
    observedAt: "2026-09-11T04:14:00Z",
    durationMinutes: 14,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0003",
    lot: "LOT-R1-0010",
    observedAt: "2026-10-16T06:21:00Z",
    durationMinutes: 17,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0004",
    lot: "LOT-R1-0013",
    observedAt: "2026-11-21T08:28:00Z",
    durationMinutes: 20,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0005",
    lot: "LOT-R1-0016",
    observedAt: "2026-12-26T10:35:00Z",
    durationMinutes: 23,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0006",
    lot: "LOT-R1-0019",
    observedAt: "2026-01-04T12:42:00Z",
    durationMinutes: 26,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0007",
    lot: "LOT-R1-0022",
    observedAt: "2026-02-09T14:49:00Z",
    durationMinutes: 29,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0008",
    lot: "LOT-R1-0025",
    observedAt: "2026-03-14T16:56:00Z",
    durationMinutes: 32,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0009",
    lot: "LOT-R1-0028",
    observedAt: "2026-04-19T18:04:00Z",
    durationMinutes: 35,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0010",
    lot: "LOT-R1-0031",
    observedAt: "2026-05-24T20:11:00Z",
    durationMinutes: 38,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0011",
    lot: "LOT-R1-0034",
    observedAt: "2026-06-02T22:18:00Z",
    durationMinutes: 41,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0012",
    lot: "LOT-R1-0037",
    observedAt: "2026-07-07T01:25:00Z",
    durationMinutes: 44,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0013",
    lot: "LOT-R1-0040",
    observedAt: "2026-08-12T03:32:00Z",
    durationMinutes: 47,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0014",
    lot: "LOT-R1-0043",
    observedAt: "2026-09-17T05:39:00Z",
    durationMinutes: 50,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0015",
    lot: "LOT-R1-0046",
    observedAt: "2026-10-22T07:46:00Z",
    durationMinutes: 53,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0016",
    lot: "LOT-R1-0049",
    observedAt: "2026-11-27T09:53:00Z",
    durationMinutes: 56,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0017",
    lot: "LOT-R1-0052",
    observedAt: "2026-12-05T11:01:00Z",
    durationMinutes: 59,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0018",
    lot: "LOT-R1-0055",
    observedAt: "2026-01-10T13:08:00Z",
    durationMinutes: 62,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0019",
    lot: "LOT-R1-0058",
    observedAt: "2026-02-15T15:15:00Z",
    durationMinutes: 65,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0020",
    lot: "LOT-R1-0061",
    observedAt: "2026-03-20T17:22:00Z",
    durationMinutes: 68,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0021",
    lot: "LOT-R1-0064",
    observedAt: "2026-04-25T19:29:00Z",
    durationMinutes: 71,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0022",
    lot: "LOT-R1-0067",
    observedAt: "2026-05-03T21:36:00Z",
    durationMinutes: 74,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0023",
    lot: "LOT-R1-0070",
    observedAt: "2026-06-08T00:43:00Z",
    durationMinutes: 77,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0024",
    lot: "LOT-R1-0073",
    observedAt: "2026-07-13T02:50:00Z",
    durationMinutes: 80,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0025",
    lot: "LOT-R1-0076",
    observedAt: "2026-08-18T04:57:00Z",
    durationMinutes: 83,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0026",
    lot: "LOT-R1-0079",
    observedAt: "2026-09-23T06:05:00Z",
    durationMinutes: 86,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0027",
    lot: "LOT-R1-0082",
    observedAt: "2026-10-01T08:12:00Z",
    durationMinutes: 89,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0028",
    lot: "LOT-R1-0085",
    observedAt: "2026-11-06T10:19:00Z",
    durationMinutes: 92,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0029",
    lot: "LOT-R1-0088",
    observedAt: "2026-12-11T12:26:00Z",
    durationMinutes: 95,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0030",
    lot: "LOT-R1-0091",
    observedAt: "2026-01-16T14:33:00Z",
    durationMinutes: 98,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0031",
    lot: "LOT-R1-0094",
    observedAt: "2026-02-21T16:40:00Z",
    durationMinutes: 101,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0032",
    lot: "LOT-R1-0097",
    observedAt: "2026-03-26T18:47:00Z",
    durationMinutes: 104,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0033",
    lot: "LOT-R1-0100",
    observedAt: "2026-04-04T20:54:00Z",
    durationMinutes: 107,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0034",
    lot: "LOT-R1-0103",
    observedAt: "2026-05-09T22:02:00Z",
    durationMinutes: 110,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0035",
    lot: "LOT-R1-0106",
    observedAt: "2026-06-14T01:09:00Z",
    durationMinutes: 113,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0036",
    lot: "LOT-R1-0109",
    observedAt: "2026-07-19T03:16:00Z",
    durationMinutes: 116,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0037",
    lot: "LOT-R1-0112",
    observedAt: "2026-08-24T05:23:00Z",
    durationMinutes: 119,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0038",
    lot: "LOT-R1-0115",
    observedAt: "2026-09-02T07:30:00Z",
    durationMinutes: 122,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0039",
    lot: "LOT-R1-0118",
    observedAt: "2026-10-07T09:37:00Z",
    durationMinutes: 125,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0040",
    lot: "LOT-R1-0121",
    observedAt: "2026-11-12T11:44:00Z",
    durationMinutes: 8,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0041",
    lot: "LOT-R1-0124",
    observedAt: "2026-12-17T13:51:00Z",
    durationMinutes: 11,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0042",
    lot: "LOT-R1-0127",
    observedAt: "2026-01-22T15:58:00Z",
    durationMinutes: 14,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0043",
    lot: "LOT-R1-0130",
    observedAt: "2026-02-27T17:06:00Z",
    durationMinutes: 17,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0044",
    lot: "LOT-R1-0133",
    observedAt: "2026-03-05T19:13:00Z",
    durationMinutes: 20,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0045",
    lot: "LOT-R1-0136",
    observedAt: "2026-04-10T21:20:00Z",
    durationMinutes: 23,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0046",
    lot: "LOT-R1-0139",
    observedAt: "2026-05-15T00:27:00Z",
    durationMinutes: 26,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0047",
    lot: "LOT-R1-0142",
    observedAt: "2026-06-20T02:34:00Z",
    durationMinutes: 29,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0048",
    lot: "LOT-R1-0145",
    observedAt: "2026-07-25T04:41:00Z",
    durationMinutes: 32,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0049",
    lot: "LOT-R1-0148",
    observedAt: "2026-08-03T06:48:00Z",
    durationMinutes: 35,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0050",
    lot: "LOT-R1-0151",
    observedAt: "2026-09-08T08:55:00Z",
    durationMinutes: 38,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0051",
    lot: "LOT-R1-0154",
    observedAt: "2026-10-13T10:03:00Z",
    durationMinutes: 41,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0052",
    lot: "LOT-R1-0157",
    observedAt: "2026-11-18T12:10:00Z",
    durationMinutes: 44,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0053",
    lot: "LOT-R1-0160",
    observedAt: "2026-12-23T14:17:00Z",
    durationMinutes: 47,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0054",
    lot: "LOT-R1-0163",
    observedAt: "2026-01-01T16:24:00Z",
    durationMinutes: 50,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0055",
    lot: "LOT-R1-0166",
    observedAt: "2026-02-06T18:31:00Z",
    durationMinutes: 53,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0056",
    lot: "LOT-R1-0169",
    observedAt: "2026-03-11T20:38:00Z",
    durationMinutes: 56,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0057",
    lot: "LOT-R1-0172",
    observedAt: "2026-04-16T22:45:00Z",
    durationMinutes: 59,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0058",
    lot: "LOT-R1-0175",
    observedAt: "2026-05-21T01:52:00Z",
    durationMinutes: 62,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0059",
    lot: "LOT-R1-0178",
    observedAt: "2026-06-26T03:00:00Z",
    durationMinutes: 65,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0060",
    lot: "LOT-R1-0181",
    observedAt: "2026-07-04T05:07:00Z",
    durationMinutes: 68,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0061",
    lot: "LOT-R1-0184",
    observedAt: "2026-08-09T07:14:00Z",
    durationMinutes: 71,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0062",
    lot: "LOT-R1-0187",
    observedAt: "2026-09-14T09:21:00Z",
    durationMinutes: 74,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0063",
    lot: "LOT-R1-0190",
    observedAt: "2026-10-19T11:28:00Z",
    durationMinutes: 77,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0064",
    lot: "LOT-R1-0193",
    observedAt: "2026-11-24T13:35:00Z",
    durationMinutes: 80,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0065",
    lot: "LOT-R1-0196",
    observedAt: "2026-12-02T15:42:00Z",
    durationMinutes: 83,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0066",
    lot: "LOT-R1-0199",
    observedAt: "2026-01-07T17:49:00Z",
    durationMinutes: 86,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0067",
    lot: "LOT-R1-0202",
    observedAt: "2026-02-12T19:56:00Z",
    durationMinutes: 89,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0068",
    lot: "LOT-R1-0205",
    observedAt: "2026-03-17T21:04:00Z",
    durationMinutes: 92,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0069",
    lot: "LOT-R1-0208",
    observedAt: "2026-04-22T00:11:00Z",
    durationMinutes: 95,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0070",
    lot: "LOT-R1-0211",
    observedAt: "2026-05-27T02:18:00Z",
    durationMinutes: 98,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0071",
    lot: "LOT-R1-0214",
    observedAt: "2026-06-05T04:25:00Z",
    durationMinutes: 101,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0072",
    lot: "LOT-R1-0217",
    observedAt: "2026-07-10T06:32:00Z",
    durationMinutes: 104,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0073",
    lot: "LOT-R1-0220",
    observedAt: "2026-08-15T08:39:00Z",
    durationMinutes: 107,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0074",
    lot: "LOT-R1-0223",
    observedAt: "2026-09-20T10:46:00Z",
    durationMinutes: 110,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0075",
    lot: "LOT-R1-0226",
    observedAt: "2026-10-25T12:53:00Z",
    durationMinutes: 113,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0076",
    lot: "LOT-R1-0229",
    observedAt: "2026-11-03T14:01:00Z",
    durationMinutes: 116,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0077",
    lot: "LOT-R1-0232",
    observedAt: "2026-12-08T16:08:00Z",
    durationMinutes: 119,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0078",
    lot: "LOT-R1-0235",
    observedAt: "2026-01-13T18:15:00Z",
    durationMinutes: 122,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0079",
    lot: "LOT-R1-0238",
    observedAt: "2026-02-18T20:22:00Z",
    durationMinutes: 125,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0080",
    lot: "LOT-R1-0241",
    observedAt: "2026-03-23T22:29:00Z",
    durationMinutes: 8,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0081",
    lot: "LOT-R1-0244",
    observedAt: "2026-04-01T01:36:00Z",
    durationMinutes: 11,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0082",
    lot: "LOT-R1-0247",
    observedAt: "2026-05-06T03:43:00Z",
    durationMinutes: 14,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0083",
    lot: "LOT-R1-0250",
    observedAt: "2026-06-11T05:50:00Z",
    durationMinutes: 17,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0084",
    lot: "LOT-R1-0253",
    observedAt: "2026-07-16T07:57:00Z",
    durationMinutes: 20,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0085",
    lot: "LOT-R1-0256",
    observedAt: "2026-08-21T09:05:00Z",
    durationMinutes: 23,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0086",
    lot: "LOT-R1-0259",
    observedAt: "2026-09-26T11:12:00Z",
    durationMinutes: 26,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0087",
    lot: "LOT-R1-0262",
    observedAt: "2026-10-04T13:19:00Z",
    durationMinutes: 29,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0088",
    lot: "LOT-R1-0265",
    observedAt: "2026-11-09T15:26:00Z",
    durationMinutes: 32,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0089",
    lot: "LOT-R1-0268",
    observedAt: "2026-12-14T17:33:00Z",
    durationMinutes: 35,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0090",
    lot: "LOT-R1-0271",
    observedAt: "2026-01-19T19:40:00Z",
    durationMinutes: 38,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0091",
    lot: "LOT-R1-0274",
    observedAt: "2026-02-24T21:47:00Z",
    durationMinutes: 41,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0092",
    lot: "LOT-R1-0277",
    observedAt: "2026-03-02T00:54:00Z",
    durationMinutes: 44,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0093",
    lot: "LOT-R1-0280",
    observedAt: "2026-04-07T02:02:00Z",
    durationMinutes: 47,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0094",
    lot: "LOT-R1-0283",
    observedAt: "2026-05-12T04:09:00Z",
    durationMinutes: 50,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0095",
    lot: "LOT-R1-0286",
    observedAt: "2026-06-17T06:16:00Z",
    durationMinutes: 53,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0096",
    lot: "LOT-R1-0289",
    observedAt: "2026-07-22T08:23:00Z",
    durationMinutes: 56,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0097",
    lot: "LOT-R1-0292",
    observedAt: "2026-08-27T10:30:00Z",
    durationMinutes: 59,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0098",
    lot: "LOT-R1-0295",
    observedAt: "2026-09-05T12:37:00Z",
    durationMinutes: 62,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0099",
    lot: "LOT-R1-0298",
    observedAt: "2026-10-10T14:44:00Z",
    durationMinutes: 65,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0100",
    lot: "LOT-R1-0301",
    observedAt: "2026-11-15T16:51:00Z",
    durationMinutes: 68,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0101",
    lot: "LOT-R1-0304",
    observedAt: "2026-12-20T18:58:00Z",
    durationMinutes: 71,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0102",
    lot: "LOT-R1-0307",
    observedAt: "2026-01-25T20:06:00Z",
    durationMinutes: 74,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0103",
    lot: "LOT-R1-0310",
    observedAt: "2026-02-03T22:13:00Z",
    durationMinutes: 77,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0104",
    lot: "LOT-R1-0313",
    observedAt: "2026-03-08T01:20:00Z",
    durationMinutes: 80,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0105",
    lot: "LOT-R1-0316",
    observedAt: "2026-04-13T03:27:00Z",
    durationMinutes: 83,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0106",
    lot: "LOT-R1-0319",
    observedAt: "2026-05-18T05:34:00Z",
    durationMinutes: 86,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0107",
    lot: "LOT-R1-0322",
    observedAt: "2026-06-23T07:41:00Z",
    durationMinutes: 89,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0108",
    lot: "LOT-R1-0325",
    observedAt: "2026-07-01T09:48:00Z",
    durationMinutes: 92,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0109",
    lot: "LOT-R1-0328",
    observedAt: "2026-08-06T11:55:00Z",
    durationMinutes: 95,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0110",
    lot: "LOT-R1-0331",
    observedAt: "2026-09-11T13:03:00Z",
    durationMinutes: 98,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0111",
    lot: "LOT-R1-0334",
    observedAt: "2026-10-16T15:10:00Z",
    durationMinutes: 101,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0112",
    lot: "LOT-R1-0337",
    observedAt: "2026-11-21T17:17:00Z",
    durationMinutes: 104,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0113",
    lot: "LOT-R1-0340",
    observedAt: "2026-12-26T19:24:00Z",
    durationMinutes: 107,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0114",
    lot: "LOT-R1-0343",
    observedAt: "2026-01-04T21:31:00Z",
    durationMinutes: 110,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0115",
    lot: "LOT-R1-0346",
    observedAt: "2026-02-09T00:38:00Z",
    durationMinutes: 113,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0116",
    lot: "LOT-R1-0349",
    observedAt: "2026-03-14T02:45:00Z",
    durationMinutes: 116,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0117",
    lot: "LOT-R1-0352",
    observedAt: "2026-04-19T04:52:00Z",
    durationMinutes: 119,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0118",
    lot: "LOT-R1-0355",
    observedAt: "2026-05-24T06:00:00Z",
    durationMinutes: 122,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0119",
    lot: "LOT-R1-0358",
    observedAt: "2026-06-02T08:07:00Z",
    durationMinutes: 125,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0120",
    lot: "LOT-R1-0361",
    observedAt: "2026-07-07T10:14:00Z",
    durationMinutes: 8,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0121",
    lot: "LOT-R1-0364",
    observedAt: "2026-08-12T12:21:00Z",
    durationMinutes: 11,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0122",
    lot: "LOT-R1-0367",
    observedAt: "2026-09-17T14:28:00Z",
    durationMinutes: 14,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0123",
    lot: "LOT-R1-0370",
    observedAt: "2026-10-22T16:35:00Z",
    durationMinutes: 17,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0124",
    lot: "LOT-R1-0373",
    observedAt: "2026-11-27T18:42:00Z",
    durationMinutes: 20,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0125",
    lot: "LOT-R1-0376",
    observedAt: "2026-12-05T20:49:00Z",
    durationMinutes: 23,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0126",
    lot: "LOT-R1-0379",
    observedAt: "2026-01-10T22:56:00Z",
    durationMinutes: 26,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0127",
    lot: "LOT-R1-0382",
    observedAt: "2026-02-15T01:04:00Z",
    durationMinutes: 29,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0128",
    lot: "LOT-R1-0385",
    observedAt: "2026-03-20T03:11:00Z",
    durationMinutes: 32,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0129",
    lot: "LOT-R1-0388",
    observedAt: "2026-04-25T05:18:00Z",
    durationMinutes: 35,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0130",
    lot: "LOT-R1-0391",
    observedAt: "2026-05-03T07:25:00Z",
    durationMinutes: 38,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0131",
    lot: "LOT-R1-0394",
    observedAt: "2026-06-08T09:32:00Z",
    durationMinutes: 41,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0132",
    lot: "LOT-R1-0397",
    observedAt: "2026-07-13T11:39:00Z",
    durationMinutes: 44,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0133",
    lot: "LOT-R1-0400",
    observedAt: "2026-08-18T13:46:00Z",
    durationMinutes: 47,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0134",
    lot: "LOT-R1-0403",
    observedAt: "2026-09-23T15:53:00Z",
    durationMinutes: 50,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0135",
    lot: "LOT-R1-0406",
    observedAt: "2026-10-01T17:01:00Z",
    durationMinutes: 53,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0136",
    lot: "LOT-R1-0409",
    observedAt: "2026-11-06T19:08:00Z",
    durationMinutes: 56,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0137",
    lot: "LOT-R1-0412",
    observedAt: "2026-12-11T21:15:00Z",
    durationMinutes: 59,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0138",
    lot: "LOT-R1-0415",
    observedAt: "2026-01-16T00:22:00Z",
    durationMinutes: 62,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0139",
    lot: "LOT-R1-0418",
    observedAt: "2026-02-21T02:29:00Z",
    durationMinutes: 65,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0140",
    lot: "LOT-R1-0421",
    observedAt: "2026-03-26T04:36:00Z",
    durationMinutes: 68,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0141",
    lot: "LOT-R1-0424",
    observedAt: "2026-04-04T06:43:00Z",
    durationMinutes: 71,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0142",
    lot: "LOT-R1-0427",
    observedAt: "2026-05-09T08:50:00Z",
    durationMinutes: 74,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0143",
    lot: "LOT-R1-0430",
    observedAt: "2026-06-14T10:57:00Z",
    durationMinutes: 77,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0144",
    lot: "LOT-R1-0433",
    observedAt: "2026-07-19T12:05:00Z",
    durationMinutes: 80,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0145",
    lot: "LOT-R1-0436",
    observedAt: "2026-08-24T14:12:00Z",
    durationMinutes: 83,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0146",
    lot: "LOT-R1-0439",
    observedAt: "2026-09-02T16:19:00Z",
    durationMinutes: 86,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0147",
    lot: "LOT-R1-0442",
    observedAt: "2026-10-07T18:26:00Z",
    durationMinutes: 89,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0148",
    lot: "LOT-R1-0445",
    observedAt: "2026-11-12T20:33:00Z",
    durationMinutes: 92,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0149",
    lot: "LOT-R1-0448",
    observedAt: "2026-12-17T22:40:00Z",
    durationMinutes: 95,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0150",
    lot: "LOT-R1-0451",
    observedAt: "2026-01-22T01:47:00Z",
    durationMinutes: 98,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0151",
    lot: "LOT-R1-0454",
    observedAt: "2026-02-27T03:54:00Z",
    durationMinutes: 101,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0152",
    lot: "LOT-R1-0457",
    observedAt: "2026-03-05T05:02:00Z",
    durationMinutes: 104,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0153",
    lot: "LOT-R1-0460",
    observedAt: "2026-04-10T07:09:00Z",
    durationMinutes: 107,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0154",
    lot: "LOT-R1-0463",
    observedAt: "2026-05-15T09:16:00Z",
    durationMinutes: 110,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0155",
    lot: "LOT-R1-0466",
    observedAt: "2026-06-20T11:23:00Z",
    durationMinutes: 113,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0156",
    lot: "LOT-R1-0469",
    observedAt: "2026-07-25T13:30:00Z",
    durationMinutes: 116,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0157",
    lot: "LOT-R1-0472",
    observedAt: "2026-08-03T15:37:00Z",
    durationMinutes: 119,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0158",
    lot: "LOT-R1-0475",
    observedAt: "2026-09-08T17:44:00Z",
    durationMinutes: 122,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0159",
    lot: "LOT-R1-0478",
    observedAt: "2026-10-13T19:51:00Z",
    durationMinutes: 125,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0160",
    lot: "LOT-R1-0001",
    observedAt: "2026-11-18T21:58:00Z",
    durationMinutes: 8,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0161",
    lot: "LOT-R1-0004",
    observedAt: "2026-12-23T00:06:00Z",
    durationMinutes: 11,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0162",
    lot: "LOT-R1-0007",
    observedAt: "2026-01-01T02:13:00Z",
    durationMinutes: 14,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0163",
    lot: "LOT-R1-0010",
    observedAt: "2026-02-06T04:20:00Z",
    durationMinutes: 17,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0164",
    lot: "LOT-R1-0013",
    observedAt: "2026-03-11T06:27:00Z",
    durationMinutes: 20,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0165",
    lot: "LOT-R1-0016",
    observedAt: "2026-04-16T08:34:00Z",
    durationMinutes: 23,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0166",
    lot: "LOT-R1-0019",
    observedAt: "2026-05-21T10:41:00Z",
    durationMinutes: 26,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0167",
    lot: "LOT-R1-0022",
    observedAt: "2026-06-26T12:48:00Z",
    durationMinutes: 29,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0168",
    lot: "LOT-R1-0025",
    observedAt: "2026-07-04T14:55:00Z",
    durationMinutes: 32,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0169",
    lot: "LOT-R1-0028",
    observedAt: "2026-08-09T16:03:00Z",
    durationMinutes: 35,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0170",
    lot: "LOT-R1-0031",
    observedAt: "2026-09-14T18:10:00Z",
    durationMinutes: 38,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0171",
    lot: "LOT-R1-0034",
    observedAt: "2026-10-19T20:17:00Z",
    durationMinutes: 41,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0172",
    lot: "LOT-R1-0037",
    observedAt: "2026-11-24T22:24:00Z",
    durationMinutes: 44,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0173",
    lot: "LOT-R1-0040",
    observedAt: "2026-12-02T01:31:00Z",
    durationMinutes: 47,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0174",
    lot: "LOT-R1-0043",
    observedAt: "2026-01-07T03:38:00Z",
    durationMinutes: 50,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0175",
    lot: "LOT-R1-0046",
    observedAt: "2026-02-12T05:45:00Z",
    durationMinutes: 53,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0176",
    lot: "LOT-R1-0049",
    observedAt: "2026-03-17T07:52:00Z",
    durationMinutes: 56,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0177",
    lot: "LOT-R1-0052",
    observedAt: "2026-04-22T09:00:00Z",
    durationMinutes: 59,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0178",
    lot: "LOT-R1-0055",
    observedAt: "2026-05-27T11:07:00Z",
    durationMinutes: 62,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0179",
    lot: "LOT-R1-0058",
    observedAt: "2026-06-05T13:14:00Z",
    durationMinutes: 65,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0180",
    lot: "LOT-R1-0061",
    observedAt: "2026-07-10T15:21:00Z",
    durationMinutes: 68,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0181",
    lot: "LOT-R1-0064",
    observedAt: "2026-08-15T17:28:00Z",
    durationMinutes: 71,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0182",
    lot: "LOT-R1-0067",
    observedAt: "2026-09-20T19:35:00Z",
    durationMinutes: 74,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0183",
    lot: "LOT-R1-0070",
    observedAt: "2026-10-25T21:42:00Z",
    durationMinutes: 77,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0184",
    lot: "LOT-R1-0073",
    observedAt: "2026-11-03T00:49:00Z",
    durationMinutes: 80,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0185",
    lot: "LOT-R1-0076",
    observedAt: "2026-12-08T02:56:00Z",
    durationMinutes: 83,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0186",
    lot: "LOT-R1-0079",
    observedAt: "2026-01-13T04:04:00Z",
    durationMinutes: 86,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0187",
    lot: "LOT-R1-0082",
    observedAt: "2026-02-18T06:11:00Z",
    durationMinutes: 89,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0188",
    lot: "LOT-R1-0085",
    observedAt: "2026-03-23T08:18:00Z",
    durationMinutes: 92,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0189",
    lot: "LOT-R1-0088",
    observedAt: "2026-04-01T10:25:00Z",
    durationMinutes: 95,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0190",
    lot: "LOT-R1-0091",
    observedAt: "2026-05-06T12:32:00Z",
    durationMinutes: 98,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0191",
    lot: "LOT-R1-0094",
    observedAt: "2026-06-11T14:39:00Z",
    durationMinutes: 101,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0192",
    lot: "LOT-R1-0097",
    observedAt: "2026-07-16T16:46:00Z",
    durationMinutes: 104,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0193",
    lot: "LOT-R1-0100",
    observedAt: "2026-08-21T18:53:00Z",
    durationMinutes: 107,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0194",
    lot: "LOT-R1-0103",
    observedAt: "2026-09-26T20:01:00Z",
    durationMinutes: 110,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0195",
    lot: "LOT-R1-0106",
    observedAt: "2026-10-04T22:08:00Z",
    durationMinutes: 113,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0196",
    lot: "LOT-R1-0109",
    observedAt: "2026-11-09T01:15:00Z",
    durationMinutes: 116,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0197",
    lot: "LOT-R1-0112",
    observedAt: "2026-12-14T03:22:00Z",
    durationMinutes: 119,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0198",
    lot: "LOT-R1-0115",
    observedAt: "2026-01-19T05:29:00Z",
    durationMinutes: 122,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0199",
    lot: "LOT-R1-0118",
    observedAt: "2026-02-24T07:36:00Z",
    durationMinutes: 125,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0200",
    lot: "LOT-R1-0121",
    observedAt: "2026-03-02T09:43:00Z",
    durationMinutes: 8,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0201",
    lot: "LOT-R1-0124",
    observedAt: "2026-04-07T11:50:00Z",
    durationMinutes: 11,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0202",
    lot: "LOT-R1-0127",
    observedAt: "2026-05-12T13:57:00Z",
    durationMinutes: 14,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0203",
    lot: "LOT-R1-0130",
    observedAt: "2026-06-17T15:05:00Z",
    durationMinutes: 17,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0204",
    lot: "LOT-R1-0133",
    observedAt: "2026-07-22T17:12:00Z",
    durationMinutes: 20,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0205",
    lot: "LOT-R1-0136",
    observedAt: "2026-08-27T19:19:00Z",
    durationMinutes: 23,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0206",
    lot: "LOT-R1-0139",
    observedAt: "2026-09-05T21:26:00Z",
    durationMinutes: 26,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0207",
    lot: "LOT-R1-0142",
    observedAt: "2026-10-10T00:33:00Z",
    durationMinutes: 29,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0208",
    lot: "LOT-R1-0145",
    observedAt: "2026-11-15T02:40:00Z",
    durationMinutes: 32,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0209",
    lot: "LOT-R1-0148",
    observedAt: "2026-12-20T04:47:00Z",
    durationMinutes: 35,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0210",
    lot: "LOT-R1-0151",
    observedAt: "2026-01-25T06:54:00Z",
    durationMinutes: 38,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0211",
    lot: "LOT-R1-0154",
    observedAt: "2026-02-03T08:02:00Z",
    durationMinutes: 41,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0212",
    lot: "LOT-R1-0157",
    observedAt: "2026-03-08T10:09:00Z",
    durationMinutes: 44,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0213",
    lot: "LOT-R1-0160",
    observedAt: "2026-04-13T12:16:00Z",
    durationMinutes: 47,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0214",
    lot: "LOT-R1-0163",
    observedAt: "2026-05-18T14:23:00Z",
    durationMinutes: 50,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0215",
    lot: "LOT-R1-0166",
    observedAt: "2026-06-23T16:30:00Z",
    durationMinutes: 53,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0216",
    lot: "LOT-R1-0169",
    observedAt: "2026-07-01T18:37:00Z",
    durationMinutes: 56,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0217",
    lot: "LOT-R1-0172",
    observedAt: "2026-08-06T20:44:00Z",
    durationMinutes: 59,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0218",
    lot: "LOT-R1-0175",
    observedAt: "2026-09-11T22:51:00Z",
    durationMinutes: 62,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0219",
    lot: "LOT-R1-0178",
    observedAt: "2026-10-16T01:58:00Z",
    durationMinutes: 65,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0220",
    lot: "LOT-R1-0181",
    observedAt: "2026-11-21T03:06:00Z",
    durationMinutes: 68,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0221",
    lot: "LOT-R1-0184",
    observedAt: "2026-12-26T05:13:00Z",
    durationMinutes: 71,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0222",
    lot: "LOT-R1-0187",
    observedAt: "2026-01-04T07:20:00Z",
    durationMinutes: 74,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0223",
    lot: "LOT-R1-0190",
    observedAt: "2026-02-09T09:27:00Z",
    durationMinutes: 77,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0224",
    lot: "LOT-R1-0193",
    observedAt: "2026-03-14T11:34:00Z",
    durationMinutes: 80,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0225",
    lot: "LOT-R1-0196",
    observedAt: "2026-04-19T13:41:00Z",
    durationMinutes: 83,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0226",
    lot: "LOT-R1-0199",
    observedAt: "2026-05-24T15:48:00Z",
    durationMinutes: 86,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0227",
    lot: "LOT-R1-0202",
    observedAt: "2026-06-02T17:55:00Z",
    durationMinutes: 89,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0228",
    lot: "LOT-R1-0205",
    observedAt: "2026-07-07T19:03:00Z",
    durationMinutes: 92,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0229",
    lot: "LOT-R1-0208",
    observedAt: "2026-08-12T21:10:00Z",
    durationMinutes: 95,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0230",
    lot: "LOT-R1-0211",
    observedAt: "2026-09-17T00:17:00Z",
    durationMinutes: 98,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0231",
    lot: "LOT-R1-0214",
    observedAt: "2026-10-22T02:24:00Z",
    durationMinutes: 101,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0232",
    lot: "LOT-R1-0217",
    observedAt: "2026-11-27T04:31:00Z",
    durationMinutes: 104,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0233",
    lot: "LOT-R1-0220",
    observedAt: "2026-12-05T06:38:00Z",
    durationMinutes: 107,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0234",
    lot: "LOT-R1-0223",
    observedAt: "2026-01-10T08:45:00Z",
    durationMinutes: 110,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0235",
    lot: "LOT-R1-0226",
    observedAt: "2026-02-15T10:52:00Z",
    durationMinutes: 113,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0236",
    lot: "LOT-R1-0229",
    observedAt: "2026-03-20T12:00:00Z",
    durationMinutes: 116,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0237",
    lot: "LOT-R1-0232",
    observedAt: "2026-04-25T14:07:00Z",
    durationMinutes: 119,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0238",
    lot: "LOT-R1-0235",
    observedAt: "2026-05-03T16:14:00Z",
    durationMinutes: 122,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0239",
    lot: "LOT-R1-0238",
    observedAt: "2026-06-08T18:21:00Z",
    durationMinutes: 125,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0240",
    lot: "LOT-R1-0241",
    observedAt: "2026-07-13T20:28:00Z",
    durationMinutes: 8,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0241",
    lot: "LOT-R1-0244",
    observedAt: "2026-08-18T22:35:00Z",
    durationMinutes: 11,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0242",
    lot: "LOT-R1-0247",
    observedAt: "2026-09-23T01:42:00Z",
    durationMinutes: 14,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0243",
    lot: "LOT-R1-0250",
    observedAt: "2026-10-01T03:49:00Z",
    durationMinutes: 17,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0244",
    lot: "LOT-R1-0253",
    observedAt: "2026-11-06T05:56:00Z",
    durationMinutes: 20,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0245",
    lot: "LOT-R1-0256",
    observedAt: "2026-12-11T07:04:00Z",
    durationMinutes: 23,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0246",
    lot: "LOT-R1-0259",
    observedAt: "2026-01-16T09:11:00Z",
    durationMinutes: 26,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0247",
    lot: "LOT-R1-0262",
    observedAt: "2026-02-21T11:18:00Z",
    durationMinutes: 29,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0248",
    lot: "LOT-R1-0265",
    observedAt: "2026-03-26T13:25:00Z",
    durationMinutes: 32,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0249",
    lot: "LOT-R1-0268",
    observedAt: "2026-04-04T15:32:00Z",
    durationMinutes: 35,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0250",
    lot: "LOT-R1-0271",
    observedAt: "2026-05-09T17:39:00Z",
    durationMinutes: 38,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0251",
    lot: "LOT-R1-0274",
    observedAt: "2026-06-14T19:46:00Z",
    durationMinutes: 41,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0252",
    lot: "LOT-R1-0277",
    observedAt: "2026-07-19T21:53:00Z",
    durationMinutes: 44,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0253",
    lot: "LOT-R1-0280",
    observedAt: "2026-08-24T00:01:00Z",
    durationMinutes: 47,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0254",
    lot: "LOT-R1-0283",
    observedAt: "2026-09-02T02:08:00Z",
    durationMinutes: 50,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0255",
    lot: "LOT-R1-0286",
    observedAt: "2026-10-07T04:15:00Z",
    durationMinutes: 53,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0256",
    lot: "LOT-R1-0289",
    observedAt: "2026-11-12T06:22:00Z",
    durationMinutes: 56,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0257",
    lot: "LOT-R1-0292",
    observedAt: "2026-12-17T08:29:00Z",
    durationMinutes: 59,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0258",
    lot: "LOT-R1-0295",
    observedAt: "2026-01-22T10:36:00Z",
    durationMinutes: 62,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0259",
    lot: "LOT-R1-0298",
    observedAt: "2026-02-27T12:43:00Z",
    durationMinutes: 65,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0260",
    lot: "LOT-R1-0301",
    observedAt: "2026-03-05T14:50:00Z",
    durationMinutes: 68,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0261",
    lot: "LOT-R1-0304",
    observedAt: "2026-04-10T16:57:00Z",
    durationMinutes: 71,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0262",
    lot: "LOT-R1-0307",
    observedAt: "2026-05-15T18:05:00Z",
    durationMinutes: 74,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0263",
    lot: "LOT-R1-0310",
    observedAt: "2026-06-20T20:12:00Z",
    durationMinutes: 77,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0264",
    lot: "LOT-R1-0313",
    observedAt: "2026-07-25T22:19:00Z",
    durationMinutes: 80,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0265",
    lot: "LOT-R1-0316",
    observedAt: "2026-08-03T01:26:00Z",
    durationMinutes: 83,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0266",
    lot: "LOT-R1-0319",
    observedAt: "2026-09-08T03:33:00Z",
    durationMinutes: 86,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0267",
    lot: "LOT-R1-0322",
    observedAt: "2026-10-13T05:40:00Z",
    durationMinutes: 89,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0268",
    lot: "LOT-R1-0325",
    observedAt: "2026-11-18T07:47:00Z",
    durationMinutes: 92,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0269",
    lot: "LOT-R1-0328",
    observedAt: "2026-12-23T09:54:00Z",
    durationMinutes: 95,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0270",
    lot: "LOT-R1-0331",
    observedAt: "2026-01-01T11:02:00Z",
    durationMinutes: 98,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0271",
    lot: "LOT-R1-0334",
    observedAt: "2026-02-06T13:09:00Z",
    durationMinutes: 101,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0272",
    lot: "LOT-R1-0337",
    observedAt: "2026-03-11T15:16:00Z",
    durationMinutes: 104,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0273",
    lot: "LOT-R1-0340",
    observedAt: "2026-04-16T17:23:00Z",
    durationMinutes: 107,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0274",
    lot: "LOT-R1-0343",
    observedAt: "2026-05-21T19:30:00Z",
    durationMinutes: 110,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0275",
    lot: "LOT-R1-0346",
    observedAt: "2026-06-26T21:37:00Z",
    durationMinutes: 113,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0276",
    lot: "LOT-R1-0349",
    observedAt: "2026-07-04T00:44:00Z",
    durationMinutes: 116,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0277",
    lot: "LOT-R1-0352",
    observedAt: "2026-08-09T02:51:00Z",
    durationMinutes: 119,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0278",
    lot: "LOT-R1-0355",
    observedAt: "2026-09-14T04:58:00Z",
    durationMinutes: 122,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0279",
    lot: "LOT-R1-0358",
    observedAt: "2026-10-19T06:06:00Z",
    durationMinutes: 125,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0280",
    lot: "LOT-R1-0361",
    observedAt: "2026-11-24T08:13:00Z",
    durationMinutes: 8,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0281",
    lot: "LOT-R1-0364",
    observedAt: "2026-12-02T10:20:00Z",
    durationMinutes: 11,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0282",
    lot: "LOT-R1-0367",
    observedAt: "2026-01-07T12:27:00Z",
    durationMinutes: 14,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0283",
    lot: "LOT-R1-0370",
    observedAt: "2026-02-12T14:34:00Z",
    durationMinutes: 17,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0284",
    lot: "LOT-R1-0373",
    observedAt: "2026-03-17T16:41:00Z",
    durationMinutes: 20,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0285",
    lot: "LOT-R1-0376",
    observedAt: "2026-04-22T18:48:00Z",
    durationMinutes: 23,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0286",
    lot: "LOT-R1-0379",
    observedAt: "2026-05-27T20:55:00Z",
    durationMinutes: 26,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0287",
    lot: "LOT-R1-0382",
    observedAt: "2026-06-05T22:03:00Z",
    durationMinutes: 29,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0288",
    lot: "LOT-R1-0385",
    observedAt: "2026-07-10T01:10:00Z",
    durationMinutes: 32,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0289",
    lot: "LOT-R1-0388",
    observedAt: "2026-08-15T03:17:00Z",
    durationMinutes: 35,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0290",
    lot: "LOT-R1-0391",
    observedAt: "2026-09-20T05:24:00Z",
    durationMinutes: 38,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0291",
    lot: "LOT-R1-0394",
    observedAt: "2026-10-25T07:31:00Z",
    durationMinutes: 41,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0292",
    lot: "LOT-R1-0397",
    observedAt: "2026-11-03T09:38:00Z",
    durationMinutes: 44,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0293",
    lot: "LOT-R1-0400",
    observedAt: "2026-12-08T11:45:00Z",
    durationMinutes: 47,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0294",
    lot: "LOT-R1-0403",
    observedAt: "2026-01-13T13:52:00Z",
    durationMinutes: 50,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0295",
    lot: "LOT-R1-0406",
    observedAt: "2026-02-18T15:00:00Z",
    durationMinutes: 53,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0296",
    lot: "LOT-R1-0409",
    observedAt: "2026-03-23T17:07:00Z",
    durationMinutes: 56,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0297",
    lot: "LOT-R1-0412",
    observedAt: "2026-04-01T19:14:00Z",
    durationMinutes: 59,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0298",
    lot: "LOT-R1-0415",
    observedAt: "2026-05-06T21:21:00Z",
    durationMinutes: 62,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0299",
    lot: "LOT-R1-0418",
    observedAt: "2026-06-11T00:28:00Z",
    durationMinutes: 65,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0300",
    lot: "LOT-R1-0421",
    observedAt: "2026-07-16T02:35:00Z",
    durationMinutes: 68,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0301",
    lot: "LOT-R1-0424",
    observedAt: "2026-08-21T04:42:00Z",
    durationMinutes: 71,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0302",
    lot: "LOT-R1-0427",
    observedAt: "2026-09-26T06:49:00Z",
    durationMinutes: 74,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0303",
    lot: "LOT-R1-0430",
    observedAt: "2026-10-04T08:56:00Z",
    durationMinutes: 77,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0304",
    lot: "LOT-R1-0433",
    observedAt: "2026-11-09T10:04:00Z",
    durationMinutes: 80,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0305",
    lot: "LOT-R1-0436",
    observedAt: "2026-12-14T12:11:00Z",
    durationMinutes: 83,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0306",
    lot: "LOT-R1-0439",
    observedAt: "2026-01-19T14:18:00Z",
    durationMinutes: 86,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0307",
    lot: "LOT-R1-0442",
    observedAt: "2026-02-24T16:25:00Z",
    durationMinutes: 89,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0308",
    lot: "LOT-R1-0445",
    observedAt: "2026-03-02T18:32:00Z",
    durationMinutes: 92,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0309",
    lot: "LOT-R1-0448",
    observedAt: "2026-04-07T20:39:00Z",
    durationMinutes: 95,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0310",
    lot: "LOT-R1-0451",
    observedAt: "2026-05-12T22:46:00Z",
    durationMinutes: 98,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0311",
    lot: "LOT-R1-0454",
    observedAt: "2026-06-17T01:53:00Z",
    durationMinutes: 101,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0312",
    lot: "LOT-R1-0457",
    observedAt: "2026-07-22T03:01:00Z",
    durationMinutes: 104,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0313",
    lot: "LOT-R1-0460",
    observedAt: "2026-08-27T05:08:00Z",
    durationMinutes: 107,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0314",
    lot: "LOT-R1-0463",
    observedAt: "2026-09-05T07:15:00Z",
    durationMinutes: 110,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0315",
    lot: "LOT-R1-0466",
    observedAt: "2026-10-10T09:22:00Z",
    durationMinutes: 113,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0316",
    lot: "LOT-R1-0469",
    observedAt: "2026-11-15T11:29:00Z",
    durationMinutes: 116,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0317",
    lot: "LOT-R1-0472",
    observedAt: "2026-12-20T13:36:00Z",
    durationMinutes: 119,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0318",
    lot: "LOT-R1-0475",
    observedAt: "2026-01-25T15:43:00Z",
    durationMinutes: 122,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0319",
    lot: "LOT-R1-0478",
    observedAt: "2026-02-03T17:50:00Z",
    durationMinutes: 125,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0320",
    lot: "LOT-R1-0001",
    observedAt: "2026-03-08T19:57:00Z",
    durationMinutes: 8,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0321",
    lot: "LOT-R1-0004",
    observedAt: "2026-04-13T21:05:00Z",
    durationMinutes: 11,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0322",
    lot: "LOT-R1-0007",
    observedAt: "2026-05-18T00:12:00Z",
    durationMinutes: 14,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0323",
    lot: "LOT-R1-0010",
    observedAt: "2026-06-23T02:19:00Z",
    durationMinutes: 17,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0324",
    lot: "LOT-R1-0013",
    observedAt: "2026-07-01T04:26:00Z",
    durationMinutes: 20,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0325",
    lot: "LOT-R1-0016",
    observedAt: "2026-08-06T06:33:00Z",
    durationMinutes: 23,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0326",
    lot: "LOT-R1-0019",
    observedAt: "2026-09-11T08:40:00Z",
    durationMinutes: 26,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0327",
    lot: "LOT-R1-0022",
    observedAt: "2026-10-16T10:47:00Z",
    durationMinutes: 29,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0328",
    lot: "LOT-R1-0025",
    observedAt: "2026-11-21T12:54:00Z",
    durationMinutes: 32,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0329",
    lot: "LOT-R1-0028",
    observedAt: "2026-12-26T14:02:00Z",
    durationMinutes: 35,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0330",
    lot: "LOT-R1-0031",
    observedAt: "2026-01-04T16:09:00Z",
    durationMinutes: 38,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0331",
    lot: "LOT-R1-0034",
    observedAt: "2026-02-09T18:16:00Z",
    durationMinutes: 41,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0332",
    lot: "LOT-R1-0037",
    observedAt: "2026-03-14T20:23:00Z",
    durationMinutes: 44,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0333",
    lot: "LOT-R1-0040",
    observedAt: "2026-04-19T22:30:00Z",
    durationMinutes: 47,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0334",
    lot: "LOT-R1-0043",
    observedAt: "2026-05-24T01:37:00Z",
    durationMinutes: 50,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0335",
    lot: "LOT-R1-0046",
    observedAt: "2026-06-02T03:44:00Z",
    durationMinutes: 53,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0336",
    lot: "LOT-R1-0049",
    observedAt: "2026-07-07T05:51:00Z",
    durationMinutes: 56,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0337",
    lot: "LOT-R1-0052",
    observedAt: "2026-08-12T07:58:00Z",
    durationMinutes: 59,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0338",
    lot: "LOT-R1-0055",
    observedAt: "2026-09-17T09:06:00Z",
    durationMinutes: 62,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0339",
    lot: "LOT-R1-0058",
    observedAt: "2026-10-22T11:13:00Z",
    durationMinutes: 65,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0340",
    lot: "LOT-R1-0061",
    observedAt: "2026-11-27T13:20:00Z",
    durationMinutes: 68,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0341",
    lot: "LOT-R1-0064",
    observedAt: "2026-12-05T15:27:00Z",
    durationMinutes: 71,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0342",
    lot: "LOT-R1-0067",
    observedAt: "2026-01-10T17:34:00Z",
    durationMinutes: 74,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0343",
    lot: "LOT-R1-0070",
    observedAt: "2026-02-15T19:41:00Z",
    durationMinutes: 77,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0344",
    lot: "LOT-R1-0073",
    observedAt: "2026-03-20T21:48:00Z",
    durationMinutes: 80,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0345",
    lot: "LOT-R1-0076",
    observedAt: "2026-04-25T00:55:00Z",
    durationMinutes: 83,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0346",
    lot: "LOT-R1-0079",
    observedAt: "2026-05-03T02:03:00Z",
    durationMinutes: 86,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0347",
    lot: "LOT-R1-0082",
    observedAt: "2026-06-08T04:10:00Z",
    durationMinutes: 89,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0348",
    lot: "LOT-R1-0085",
    observedAt: "2026-07-13T06:17:00Z",
    durationMinutes: 92,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0349",
    lot: "LOT-R1-0088",
    observedAt: "2026-08-18T08:24:00Z",
    durationMinutes: 95,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0350",
    lot: "LOT-R1-0091",
    observedAt: "2026-09-23T10:31:00Z",
    durationMinutes: 98,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0351",
    lot: "LOT-R1-0094",
    observedAt: "2026-10-01T12:38:00Z",
    durationMinutes: 101,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0352",
    lot: "LOT-R1-0097",
    observedAt: "2026-11-06T14:45:00Z",
    durationMinutes: 104,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0353",
    lot: "LOT-R1-0100",
    observedAt: "2026-12-11T16:52:00Z",
    durationMinutes: 107,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0354",
    lot: "LOT-R1-0103",
    observedAt: "2026-01-16T18:00:00Z",
    durationMinutes: 110,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0355",
    lot: "LOT-R1-0106",
    observedAt: "2026-02-21T20:07:00Z",
    durationMinutes: 113,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0356",
    lot: "LOT-R1-0109",
    observedAt: "2026-03-26T22:14:00Z",
    durationMinutes: 116,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0357",
    lot: "LOT-R1-0112",
    observedAt: "2026-04-04T01:21:00Z",
    durationMinutes: 119,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0358",
    lot: "LOT-R1-0115",
    observedAt: "2026-05-09T03:28:00Z",
    durationMinutes: 122,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0359",
    lot: "LOT-R1-0118",
    observedAt: "2026-06-14T05:35:00Z",
    durationMinutes: 125,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0360",
    lot: "LOT-R1-0121",
    observedAt: "2026-07-19T07:42:00Z",
    durationMinutes: 8,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0361",
    lot: "LOT-R1-0124",
    observedAt: "2026-08-24T09:49:00Z",
    durationMinutes: 11,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0362",
    lot: "LOT-R1-0127",
    observedAt: "2026-09-02T11:56:00Z",
    durationMinutes: 14,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0363",
    lot: "LOT-R1-0130",
    observedAt: "2026-10-07T13:04:00Z",
    durationMinutes: 17,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0364",
    lot: "LOT-R1-0133",
    observedAt: "2026-11-12T15:11:00Z",
    durationMinutes: 20,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0365",
    lot: "LOT-R1-0136",
    observedAt: "2026-12-17T17:18:00Z",
    durationMinutes: 23,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0366",
    lot: "LOT-R1-0139",
    observedAt: "2026-01-22T19:25:00Z",
    durationMinutes: 26,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0367",
    lot: "LOT-R1-0142",
    observedAt: "2026-02-27T21:32:00Z",
    durationMinutes: 29,
    peakCelsius: -16,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0368",
    lot: "LOT-R1-0145",
    observedAt: "2026-03-05T00:39:00Z",
    durationMinutes: 32,
    peakCelsius: 13,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0369",
    lot: "LOT-R1-0148",
    observedAt: "2026-04-10T02:46:00Z",
    durationMinutes: 35,
    peakCelsius: -14,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0370",
    lot: "LOT-R1-0151",
    observedAt: "2026-05-15T04:53:00Z",
    durationMinutes: 38,
    peakCelsius: 15,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0371",
    lot: "LOT-R1-0154",
    observedAt: "2026-06-20T06:01:00Z",
    durationMinutes: 41,
    peakCelsius: -19,
    thresholdCelsius: -20,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0372",
    lot: "LOT-R1-0157",
    observedAt: "2026-07-25T08:08:00Z",
    durationMinutes: 44,
    peakCelsius: 10,
    thresholdCelsius: 8,
    action: "Monitored event logged with no immediate release block."
  },
  {
    id: "excursion-0373",
    lot: "LOT-R1-0160",
    observedAt: "2026-08-03T10:15:00Z",
    durationMinutes: 47,
    peakCelsius: -17,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0374",
    lot: "LOT-R1-0163",
    observedAt: "2026-09-08T12:22:00Z",
    durationMinutes: 50,
    peakCelsius: 12,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0375",
    lot: "LOT-R1-0166",
    observedAt: "2026-10-13T14:29:00Z",
    durationMinutes: 53,
    peakCelsius: -15,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0376",
    lot: "LOT-R1-0169",
    observedAt: "2026-11-18T16:36:00Z",
    durationMinutes: 56,
    peakCelsius: 14,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0377",
    lot: "LOT-R1-0172",
    observedAt: "2026-12-23T18:43:00Z",
    durationMinutes: 59,
    peakCelsius: -13,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0378",
    lot: "LOT-R1-0175",
    observedAt: "2026-01-01T20:50:00Z",
    durationMinutes: 62,
    peakCelsius: 9,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0379",
    lot: "LOT-R1-0178",
    observedAt: "2026-02-06T22:57:00Z",
    durationMinutes: 65,
    peakCelsius: -18,
    thresholdCelsius: -20,
    action: "Auto quarantine and QA investigation opened."
  },
  {
    id: "excursion-0380",
    lot: "LOT-R1-0181",
    observedAt: "2026-03-11T01:05:00Z",
    durationMinutes: 68,
    peakCelsius: 11,
    thresholdCelsius: 8,
    action: "Auto quarantine and QA investigation opened."
  }
];
