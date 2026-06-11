// PRISMA PC UIUX V02 route adoption contracts.
// Complete file, installed by PRISMA_PC_UIUX_ROUTE_ADOPTION_GATE_20260525_v02.

export type PcUiuxGroup =
  | "hoy"
  | "ventas-caja"
  | "inventario"
  | "compras"
  | "proveedores"
  | "sincronizacion"
  | "reportes"
  | "analisis"
  | "sistema"
  | "configuracion"
  | "ayuda";

export type PcUiuxRole = "dueno" | "gerente" | "auditor" | "soporte";
export type PcUiuxBlock = "decisionHeader" | "attentionSummary" | "nextBestAction" | "actionableTable" | "evidenceDrawer" | "emptyState" | "errorState";
export type PcDataSourceKind = "real" | "demo" | "hybrid" | "static";
export type PcRouteStatus = "primary" | "secondary" | "internal" | "lab";

export type PcEvidenceRecord = {
  label: string;
  value: string;
  kind: "operational" | "technical" | "governance";
};

export type PcHumanEmptyState = {
  title: string;
  explanation: string;
  actionLabel: string;
  actionHref: string;
};

export type PcHumanErrorState = {
  title: string;
  explanation: string;
  recovery: string;
  actionLabel: string;
  actionHref: string;
};

export type PcPageContract = {
  route: string;
  humanName: string;
  group: PcUiuxGroup;
  status: PcRouteStatus;
  primaryQuestion: string;
  routeIntent: string;
  subtitle: string;
  userRoles: PcUiuxRole[];
  requiredBlocks: PcUiuxBlock[];
  primaryAction: string;
  secondaryActions: string[];
  dataSourceKind: PcDataSourceKind;
  allowsTechnicalTermsOnlyInsideEvidence: boolean;
  evidence: PcEvidenceRecord[];
  emptyState: PcHumanEmptyState;
  errorState: PcHumanErrorState;
};

export const PC_PAGE_CONTRACTS = [
  {
    "route": "/",
    "humanName": "Entrada",
    "group": "hoy",
    "status": "primary",
    "primaryQuestion": "¿Qué debo atender ahora?",
    "routeIntent": "¿Qué debo atender ahora?",
    "subtitle": "Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar prioridades",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Entrada",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/"
    },
    "errorState": {
      "title": "No se pudo cargar Entrada",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/"
    }
  },
  {
    "route": "/acciones-masivas",
    "humanName": "Acciones masivas",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Acciones masivas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/acciones-masivas"
    },
    "errorState": {
      "title": "No se pudo cargar Acciones masivas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/acciones-masivas"
    }
  },
  {
    "route": "/ajustes-inventario",
    "humanName": "Ajustes de inventario",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Ajustes de inventario",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/ajustes-inventario"
    },
    "errorState": {
      "title": "No se pudo cargar Ajustes de inventario",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/ajustes-inventario"
    }
  },
  {
    "route": "/alertas-ejecutivas",
    "humanName": "Alertas ejecutivas",
    "group": "hoy",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo atender ahora?",
    "routeIntent": "¿Qué debo atender ahora?",
    "subtitle": "Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar prioridades",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Alertas ejecutivas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/alertas-ejecutivas"
    },
    "errorState": {
      "title": "No se pudo cargar Alertas ejecutivas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/alertas-ejecutivas"
    }
  },
  {
    "route": "/alertas-operativas",
    "humanName": "Alertas operativas",
    "group": "hoy",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo atender ahora?",
    "routeIntent": "¿Qué debo atender ahora?",
    "subtitle": "Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar prioridades",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Alertas operativas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/alertas-operativas"
    },
    "errorState": {
      "title": "No se pudo cargar Alertas operativas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/alertas-operativas"
    }
  },
  {
    "route": "/audit",
    "humanName": "Historial y auditoría",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Historial y auditoría",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/audit"
    },
    "errorState": {
      "title": "No se pudo cargar Historial y auditoría",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/audit"
    }
  },
  {
    "route": "/auditoria-inventario",
    "humanName": "Historial de inventario",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Historial de inventario",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/auditoria-inventario"
    },
    "errorState": {
      "title": "No se pudo cargar Historial de inventario",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/auditoria-inventario"
    }
  },
  {
    "route": "/cash-sessions",
    "humanName": "Cortes de caja",
    "group": "ventas-caja",
    "status": "secondary",
    "primaryQuestion": "¿Cómo va la venta y el dinero?",
    "routeIntent": "¿Cómo va la venta y el dinero?",
    "subtitle": "Ventas, caja y cortes en lenguaje de negocio.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar ventas",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Cortes de caja",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/cash-sessions"
    },
    "errorState": {
      "title": "No se pudo cargar Cortes de caja",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/cash-sessions"
    }
  },
  {
    "route": "/catalog",
    "humanName": "Catálogo",
    "group": "inventario",
    "status": "primary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Catálogo",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/catalog"
    },
    "errorState": {
      "title": "No se pudo cargar Catálogo",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/catalog"
    }
  },
  {
    "route": "/catalogo-activo",
    "humanName": "Productos activos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Productos activos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/catalogo-activo"
    },
    "errorState": {
      "title": "No se pudo cargar Productos activos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/catalogo-activo"
    }
  },
  {
    "route": "/conteos-operativos",
    "humanName": "Conteos operativos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Conteos operativos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/conteos-operativos"
    },
    "errorState": {
      "title": "No se pudo cargar Conteos operativos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/conteos-operativos"
    }
  },
  {
    "route": "/contratos-reporte",
    "humanName": "Contratos de reporte",
    "group": "reportes",
    "status": "secondary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Contratos de reporte",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/contratos-reporte"
    },
    "errorState": {
      "title": "No se pudo cargar Contratos de reporte",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/contratos-reporte"
    }
  },
  {
    "route": "/counts",
    "humanName": "Conteos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Conteos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/counts"
    },
    "errorState": {
      "title": "No se pudo cargar Conteos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/counts"
    }
  },
  {
    "route": "/dashboard",
    "humanName": "Hoy",
    "group": "hoy",
    "status": "primary",
    "primaryQuestion": "¿Qué debo atender ahora?",
    "routeIntent": "¿Qué debo atender ahora?",
    "subtitle": "Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar prioridades",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Hoy",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/dashboard"
    },
    "errorState": {
      "title": "No se pudo cargar Hoy",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/dashboard"
    }
  },
  {
    "route": "/data-quality",
    "humanName": "Revisión de datos",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Revisión de datos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/data-quality"
    },
    "errorState": {
      "title": "No se pudo cargar Revisión de datos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/data-quality"
    }
  },
  {
    "route": "/detalle-registros",
    "humanName": "Detalle de registros",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Detalle de registros",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/detalle-registros"
    },
    "errorState": {
      "title": "No se pudo cargar Detalle de registros",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/detalle-registros"
    }
  },
  {
    "route": "/devices",
    "humanName": "Equipos",
    "group": "sistema",
    "status": "primary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Equipos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/devices"
    },
    "errorState": {
      "title": "No se pudo cargar Equipos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/devices"
    }
  },
  {
    "route": "/estados-operativos",
    "humanName": "Estados operativos",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Estados operativos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/estados-operativos"
    },
    "errorState": {
      "title": "No se pudo cargar Estados operativos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/estados-operativos"
    }
  },
  {
    "route": "/existencias-criticas",
    "humanName": "Productos críticos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Productos críticos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/existencias-criticas"
    },
    "errorState": {
      "title": "No se pudo cargar Productos críticos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/existencias-criticas"
    }
  },
  {
    "route": "/exportables",
    "humanName": "Descargas",
    "group": "reportes",
    "status": "primary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Descargas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/exportables"
    },
    "errorState": {
      "title": "No se pudo cargar Descargas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/exportables"
    }
  },
  {
    "route": "/filtros-avanzados",
    "humanName": "Filtros avanzados",
    "group": "sistema",
    "status": "internal",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Filtros avanzados",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/filtros-avanzados"
    },
    "errorState": {
      "title": "No se pudo cargar Filtros avanzados",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/filtros-avanzados"
    }
  },
  {
    "route": "/filtros-fecha",
    "humanName": "Filtros por fecha",
    "group": "sistema",
    "status": "internal",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Filtros por fecha",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/filtros-fecha"
    },
    "errorState": {
      "title": "No se pudo cargar Filtros por fecha",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/filtros-fecha"
    }
  },
  {
    "route": "/forecast-basico",
    "humanName": "Pronóstico básico",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Pronóstico básico",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/forecast-basico"
    },
    "errorState": {
      "title": "No se pudo cargar Pronóstico básico",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/forecast-basico"
    }
  },
  {
    "route": "/glosario",
    "humanName": "Glosario",
    "group": "ayuda",
    "status": "primary",
    "primaryQuestion": "¿Qué significa esto y cómo se usa?",
    "routeIntent": "¿Qué significa esto y cómo se usa?",
    "subtitle": "Referencia técnica traducida a lenguaje humano.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Ver guía",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Glosario",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/glosario"
    },
    "errorState": {
      "title": "No se pudo cargar Glosario",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/glosario"
    }
  },
  {
    "route": "/gobierno",
    "humanName": "Gobierno",
    "group": "sistema",
    "status": "internal",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Gobierno",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/gobierno"
    },
    "errorState": {
      "title": "No se pudo cargar Gobierno",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/gobierno"
    }
  },
  {
    "route": "/incidencias-recepcion",
    "humanName": "Diferencias de recepción",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Diferencias de recepción",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/incidencias-recepcion"
    },
    "errorState": {
      "title": "No se pudo cargar Diferencias de recepción",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/incidencias-recepcion"
    }
  },
  {
    "route": "/integridad-barcodes",
    "humanName": "Códigos repetidos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Códigos repetidos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/integridad-barcodes"
    },
    "errorState": {
      "title": "No se pudo cargar Códigos repetidos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/integridad-barcodes"
    }
  },
  {
    "route": "/license-runtime",
    "humanName": "Licencia",
    "group": "sistema",
    "status": "secondary",
    "primaryQuestion": "¿La plataforma está sana?",
    "routeIntent": "¿La plataforma está sana?",
    "subtitle": "Salud de plataforma, equipos, licencia y auditoría bajo demanda.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar salud del sistema",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Licencia",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/license-runtime"
    },
    "errorState": {
      "title": "No se pudo cargar Licencia",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/license-runtime"
    }
  },
  {
    "route": "/metricas-dia",
    "humanName": "Métricas del día",
    "group": "ventas-caja",
    "status": "secondary",
    "primaryQuestion": "¿Cómo va la venta y el dinero?",
    "routeIntent": "¿Cómo va la venta y el dinero?",
    "subtitle": "Ventas, caja y cortes en lenguaje de negocio.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar ventas",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Métricas del día",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/metricas-dia"
    },
    "errorState": {
      "title": "No se pudo cargar Métricas del día",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/metricas-dia"
    }
  },
  {
    "route": "/movements",
    "humanName": "Movimientos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Movimientos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/movements"
    },
    "errorState": {
      "title": "No se pudo cargar Movimientos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/movements"
    }
  },
  {
    "route": "/ordenes-compra",
    "humanName": "Órdenes de compra",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Órdenes de compra",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/ordenes-compra"
    },
    "errorState": {
      "title": "No se pudo cargar Órdenes de compra",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/ordenes-compra"
    }
  },
  {
    "route": "/outbox-operativo",
    "humanName": "Cambios pendientes",
    "group": "sincronizacion",
    "status": "secondary",
    "primaryQuestion": "¿Todo está actualizado entre equipos?",
    "routeIntent": "¿Todo está actualizado entre equipos?",
    "subtitle": "Estado de cambios entre PC, tablet y operación local.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar sincronización",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Cambios pendientes",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/outbox-operativo"
    },
    "errorState": {
      "title": "No se pudo cargar Cambios pendientes",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/outbox-operativo"
    }
  },
  {
    "route": "/politica-precios",
    "humanName": "Política de precios",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Política de precios",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/politica-precios"
    },
    "errorState": {
      "title": "No se pudo cargar Política de precios",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/politica-precios"
    }
  },
  {
    "route": "/prisma-insights",
    "humanName": "Análisis",
    "group": "analisis",
    "status": "primary",
    "primaryQuestion": "¿Qué patrón explica lo que está pasando?",
    "routeIntent": "¿Qué patrón explica lo que está pasando?",
    "subtitle": "Lecturas visuales para entender patrones y decisiones.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Ver análisis",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Análisis",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/prisma-insights"
    },
    "errorState": {
      "title": "No se pudo cargar Análisis",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/prisma-insights"
    }
  },
  {
    "route": "/prisma-insights/chart-lab",
    "humanName": "Chart Lab",
    "group": "analisis",
    "status": "lab",
    "primaryQuestion": "¿Qué patrón explica lo que está pasando?",
    "routeIntent": "¿Qué patrón explica lo que está pasando?",
    "subtitle": "Lecturas visuales para entender patrones y decisiones.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Ver análisis",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Chart Lab",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/prisma-insights/chart-lab"
    },
    "errorState": {
      "title": "No se pudo cargar Chart Lab",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/prisma-insights/chart-lab"
    }
  },
  {
    "route": "/proveedores",
    "humanName": "Proveedores",
    "group": "proveedores",
    "status": "primary",
    "primaryQuestion": "¿Con quién debo actuar hoy?",
    "routeIntent": "¿Con quién debo actuar hoy?",
    "subtitle": "Acciones con proveedores, pagos y seguimiento operativo.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar proveedor",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Proveedores",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/proveedores"
    },
    "errorState": {
      "title": "No se pudo cargar Proveedores",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/proveedores"
    }
  },
  {
    "route": "/purchasing",
    "humanName": "Compras",
    "group": "compras",
    "status": "primary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Pedidos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/purchasing"
    },
    "errorState": {
      "title": "No se pudo cargar Pedidos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/purchasing"
    }
  },
  {
    "route": "/receiving",
    "humanName": "Recepción",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Recepción",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/receiving"
    },
    "errorState": {
      "title": "No se pudo cargar Recepción",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/receiving"
    }
  },
  {
    "route": "/recepcion-proveedor",
    "humanName": "Recibir proveedor",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Recibir proveedor",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/recepcion-proveedor"
    },
    "errorState": {
      "title": "No se pudo cargar Recibir proveedor",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/recepcion-proveedor"
    }
  },
  {
    "route": "/referencia-visual",
    "humanName": "Referencia visual",
    "group": "ayuda",
    "status": "internal",
    "primaryQuestion": "¿Qué significa esto y cómo se usa?",
    "routeIntent": "¿Qué significa esto y cómo se usa?",
    "subtitle": "Referencia técnica traducida a lenguaje humano.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Ver guía",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Referencia visual",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/referencia-visual"
    },
    "errorState": {
      "title": "No se pudo cargar Referencia visual",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/referencia-visual"
    }
  },
  {
    "route": "/replenishment",
    "humanName": "Reabasto",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Reabasto",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/replenishment"
    },
    "errorState": {
      "title": "No se pudo cargar Reabasto",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/replenishment"
    }
  },
  {
    "route": "/sales-control",
    "humanName": "Ventas",
    "group": "ventas-caja",
    "status": "primary",
    "primaryQuestion": "¿Cómo va la venta y el dinero?",
    "routeIntent": "¿Cómo va la venta y el dinero?",
    "subtitle": "Ventas, caja y cortes en lenguaje de negocio.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar ventas",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Ventas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/sales-control"
    },
    "errorState": {
      "title": "No se pudo cargar Ventas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/sales-control"
    }
  },
  {
    "route": "/salud-barcodes",
    "humanName": "Salud de códigos",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Salud de códigos",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/salud-barcodes"
    },
    "errorState": {
      "title": "No se pudo cargar Salud de códigos",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/salud-barcodes"
    }
  },
  {
    "route": "/scorecards-negocio",
    "humanName": "Indicadores de negocio",
    "group": "reportes",
    "status": "secondary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Indicadores de negocio",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/scorecards-negocio"
    },
    "errorState": {
      "title": "No se pudo cargar Indicadores de negocio",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/scorecards-negocio"
    }
  },
  {
    "route": "/senal-reabasto",
    "humanName": "Señal de reabasto",
    "group": "compras",
    "status": "secondary",
    "primaryQuestion": "¿Qué debo pedir o recibir?",
    "routeIntent": "¿Qué debo pedir o recibir?",
    "subtitle": "Pedidos, recepción y reabasto con prioridad clara.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar pedidos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Señal de reabasto",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/senal-reabasto"
    },
    "errorState": {
      "title": "No se pudo cargar Señal de reabasto",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/senal-reabasto"
    }
  },
  {
    "route": "/settings",
    "humanName": "Configuración",
    "group": "configuracion",
    "status": "primary",
    "primaryQuestion": "¿Qué regla o preferencia debo ajustar?",
    "routeIntent": "¿Qué regla o preferencia debo ajustar?",
    "subtitle": "Reglas, preferencias y permisos del sistema.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Guardar configuración",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Configuración",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/settings"
    },
    "errorState": {
      "title": "No se pudo cargar Configuración",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/settings"
    }
  },
  {
    "route": "/settings/license",
    "humanName": "Licencia",
    "group": "configuracion",
    "status": "secondary",
    "primaryQuestion": "¿Qué regla o preferencia debo ajustar?",
    "routeIntent": "¿Qué regla o preferencia debo ajustar?",
    "subtitle": "Reglas, preferencias y permisos del sistema.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Guardar configuración",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Licencia",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/settings/license"
    },
    "errorState": {
      "title": "No se pudo cargar Licencia",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/settings/license"
    }
  },
  {
    "route": "/stock",
    "humanName": "Existencias",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Existencias",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/stock"
    },
    "errorState": {
      "title": "No se pudo cargar Existencias",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/stock"
    }
  },
  {
    "route": "/sync",
    "humanName": "Sincronización",
    "group": "sincronizacion",
    "status": "primary",
    "primaryQuestion": "¿Todo está actualizado entre equipos?",
    "routeIntent": "¿Todo está actualizado entre equipos?",
    "subtitle": "Estado de cambios entre PC, tablet y operación local.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar sincronización",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Sincronización",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/sync"
    },
    "errorState": {
      "title": "No se pudo cargar Sincronización",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/sync"
    }
  },
  {
    "route": "/sync-operativo",
    "humanName": "Sincronización operativa",
    "group": "sincronizacion",
    "status": "secondary",
    "primaryQuestion": "¿Todo está actualizado entre equipos?",
    "routeIntent": "¿Todo está actualizado entre equipos?",
    "subtitle": "Estado de cambios entre PC, tablet y operación local.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar sincronización",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Sincronización operativa",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/sync-operativo"
    },
    "errorState": {
      "title": "No se pudo cargar Sincronización operativa",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/sync-operativo"
    }
  },
  {
    "route": "/tablas-operativas",
    "humanName": "Tablas operativas",
    "group": "reportes",
    "status": "secondary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Tablas operativas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/tablas-operativas"
    },
    "errorState": {
      "title": "No se pudo cargar Tablas operativas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/tablas-operativas"
    }
  },
  {
    "route": "/tablero-kpi",
    "humanName": "Tablero KPI",
    "group": "reportes",
    "status": "secondary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Tablero KPI",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/tablero-kpi"
    },
    "errorState": {
      "title": "No se pudo cargar Tablero KPI",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/tablero-kpi"
    }
  },
  {
    "route": "/tablet-communication",
    "humanName": "Tablet",
    "group": "sincronizacion",
    "status": "secondary",
    "primaryQuestion": "¿Todo está actualizado entre equipos?",
    "routeIntent": "¿Todo está actualizado entre equipos?",
    "subtitle": "Estado de cambios entre PC, tablet y operación local.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar sincronización",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Tablet",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/tablet-communication"
    },
    "errorState": {
      "title": "No se pudo cargar Tablet",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/tablet-communication"
    }
  },
  {
    "route": "/validacion-catalogo",
    "humanName": "Validación de catálogo",
    "group": "inventario",
    "status": "secondary",
    "primaryQuestion": "¿Qué productos necesitan atención?",
    "routeIntent": "¿Qué productos necesitan atención?",
    "subtitle": "Productos, existencias y señales que pueden afectar la venta.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Revisar productos críticos",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Validación de catálogo",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/validacion-catalogo"
    },
    "errorState": {
      "title": "No se pudo cargar Validación de catálogo",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/validacion-catalogo"
    }
  },
  {
    "route": "/vistas-ejecutivas",
    "humanName": "Vistas ejecutivas",
    "group": "reportes",
    "status": "secondary",
    "primaryQuestion": "¿Qué pasó y cómo lo descargo?",
    "routeIntent": "¿Qué pasó y cómo lo descargo?",
    "subtitle": "Evidencia descargable, contratos y resúmenes útiles.",
    "userRoles": [
      "dueno",
      "gerente",
      "auditor",
      "soporte"
    ],
    "requiredBlocks": [
      "decisionHeader",
      "attentionSummary",
      "nextBestAction",
      "actionableTable",
      "evidenceDrawer",
      "emptyState",
      "errorState"
    ],
    "primaryAction": "Descargar reporte",
    "secondaryActions": [
      "Ver detalle",
      "Ver evidencia"
    ],
    "dataSourceKind": "real",
    "allowsTechnicalTermsOnlyInsideEvidence": true,
    "evidence": [
      {
        "label": "Fuente",
        "value": "Base principal o servicio del módulo",
        "kind": "operational"
      },
      {
        "label": "Confianza",
        "value": "Alta si la lectura viene de datos reales; incompleta si falta fuente",
        "kind": "technical"
      },
      {
        "label": "Última actualización",
        "value": "Se muestra con formato humano cuando la ruta entrega fecha",
        "kind": "operational"
      }
    ],
    "emptyState": {
      "title": "Sin pendientes en Vistas ejecutivas",
      "explanation": "No se detectaron elementos que requieran atención inmediata.",
      "actionLabel": "Ver detalle",
      "actionHref": "/vistas-ejecutivas"
    },
    "errorState": {
      "title": "No se pudo cargar Vistas ejecutivas",
      "explanation": "La información necesaria no estuvo disponible en esta lectura.",
      "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
      "actionLabel": "Reintentar",
      "actionHref": "/vistas-ejecutivas"
    }
  },
  {
      "route": "/laboratorio-pc",
      "humanName": "Laboratorio PC",
      "group": "ayuda",
      "status": "lab",
      "primaryQuestion": "¿Qué experimento visual o técnico debo revisar?",
      "routeIntent": "¿Qué experimento visual o técnico debo revisar?",
      "subtitle": "Laboratorio interno de PC para validar referencias sin contaminar pantallas productivas.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Abrir laboratorio",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Laboratorio PC",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc"
      },
      "errorState": {
          "title": "No se pudo cargar Laboratorio PC",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc"
      }
  },
  {
      "route": "/laboratorio-pc/chart-lab",
      "humanName": "Chart Lab",
      "group": "analisis",
      "status": "lab",
      "primaryQuestion": "¿Qué visualización experimental debo evaluar?",
      "routeIntent": "¿Qué visualización experimental debo evaluar?",
      "subtitle": "Laboratorio de gráficas y exploración visual, separado de operación diaria.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Revisar gráfica",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/chart-lab",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Chart Lab",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc/chart-lab"
      },
      "errorState": {
          "title": "No se pudo cargar Chart Lab",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc/chart-lab"
      }
  },
  {
      "route": "/laboratorio-pc/dashboard-governor",
      "humanName": "Dashboard Governor Lab",
      "group": "ayuda",
      "status": "lab",
      "primaryQuestion": "¿Qué regla visual del dashboard debo comprobar?",
      "routeIntent": "¿Qué regla visual del dashboard debo comprobar?",
      "subtitle": "Laboratorio de gobierno visual para dashboard PC.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Revisar gobierno",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/dashboard-governor",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Dashboard Governor Lab",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc/dashboard-governor"
      },
      "errorState": {
          "title": "No se pudo cargar Dashboard Governor Lab",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc/dashboard-governor"
      }
  },
  {
      "route": "/laboratorio-pc/referencia-visual",
      "humanName": "Referencia visual PC",
      "group": "ayuda",
      "status": "lab",
      "primaryQuestion": "¿Qué referencia visual debo consultar?",
      "routeIntent": "¿Qué referencia visual debo consultar?",
      "subtitle": "Galería interna para comparar tratamientos visuales PC sin mezclar operación productiva.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Ver referencia",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/referencia-visual",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Referencia visual PC",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc/referencia-visual"
      },
      "errorState": {
          "title": "No se pudo cargar Referencia visual PC",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc/referencia-visual"
      }
  },
  {
      "route": "/laboratorio-pc/referencia-visual/liquid-glass",
      "humanName": "Liquid Glass Lab",
      "group": "ayuda",
      "status": "lab",
      "primaryQuestion": "¿Qué comportamiento liquid glass debo validar?",
      "routeIntent": "¿Qué comportamiento liquid glass debo validar?",
      "subtitle": "Referencia técnica visual de liquid glass para PC.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Ver liquid glass",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/referencia-visual/liquid-glass",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Liquid Glass Lab",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc/referencia-visual/liquid-glass"
      },
      "errorState": {
          "title": "No se pudo cargar Liquid Glass Lab",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc/referencia-visual/liquid-glass"
      }
  },
  {
      "route": "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
      "humanName": "Glass Capsules Lab",
      "group": "ayuda",
      "status": "lab",
      "primaryQuestion": "¿Qué cápsula glass debo validar?",
      "routeIntent": "¿Qué cápsula glass debo validar?",
      "subtitle": "Referencia técnica visual de cápsulas glass para PC.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Ver cápsulas",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Glass Capsules Lab",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/laboratorio-pc/referencia-visual/liquid-glass-capsules"
      },
      "errorState": {
          "title": "No se pudo cargar Glass Capsules Lab",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/laboratorio-pc/referencia-visual/liquid-glass-capsules"
      }
  },
  {
      "route": "/referencia-visual/liquid-glass",
      "humanName": "Liquid Glass Lab alias",
      "group": "ayuda",
      "status": "internal",
      "primaryQuestion": "¿Qué alias visual redirige a laboratorio?",
      "routeIntent": "¿Qué alias visual redirige a laboratorio?",
      "subtitle": "Alias interno que canonicaliza hacia /laboratorio-pc/referencia-visual/liquid-glass.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Abrir canonical",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/referencia-visual/liquid-glass",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Liquid Glass Lab alias",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/referencia-visual/liquid-glass"
      },
      "errorState": {
          "title": "No se pudo cargar Liquid Glass Lab alias",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/referencia-visual/liquid-glass"
      }
  },
  {
      "route": "/referencia-visual/liquid-glass-capsules",
      "humanName": "Glass Capsules Lab alias",
      "group": "ayuda",
      "status": "internal",
      "primaryQuestion": "¿Qué alias visual redirige a laboratorio?",
      "routeIntent": "¿Qué alias visual redirige a laboratorio?",
      "subtitle": "Alias interno que canonicaliza hacia /laboratorio-pc/referencia-visual/liquid-glass-capsules.",
      "userRoles": [
          "dueno",
          "gerente",
          "auditor",
          "soporte"
      ],
      "requiredBlocks": [
          "decisionHeader",
          "attentionSummary",
          "nextBestAction",
          "actionableTable",
          "evidenceDrawer",
          "emptyState",
          "errorState"
      ],
      "primaryAction": "Abrir canonical",
      "secondaryActions": [
          "Ver detalle",
          "Ver evidencia"
      ],
      "dataSourceKind": "static",
      "allowsTechnicalTermsOnlyInsideEvidence": true,
      "evidence": [
          {
              "label": "Tipo",
              "value": "Ruta interna/laboratorio gobernada",
              "kind": "governance"
          },
          {
              "label": "Alcance",
              "value": "PC solamente; no afecta Tablet ni Mobile",
              "kind": "governance"
          },
          {
              "label": "Canonical",
              "value": "/laboratorio-pc/referencia-visual/liquid-glass-capsules",
              "kind": "technical"
          }
      ],
      "emptyState": {
          "title": "Sin pendientes en Glass Capsules Lab alias",
          "explanation": "No se detectaron elementos que requieran atención inmediata.",
          "actionLabel": "Ver detalle",
          "actionHref": "/referencia-visual/liquid-glass-capsules"
      },
      "errorState": {
          "title": "No se pudo cargar Glass Capsules Lab alias",
          "explanation": "La información necesaria no estuvo disponible en esta lectura.",
          "recovery": "Reintenta y revisa la evidencia técnica si vuelve a fallar.",
          "actionLabel": "Reintentar",
          "actionHref": "/referencia-visual/liquid-glass-capsules"
      }
  }
] as const satisfies readonly PcPageContract[];
