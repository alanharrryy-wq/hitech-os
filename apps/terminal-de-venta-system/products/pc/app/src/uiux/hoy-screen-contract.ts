export const hoyScreenContract = {
  screen: "Hoy",
  route: "/dashboard",
  marketingRoute: "/",
  contract: "ansi-decision-center",
  requiredSections: [
    "HOY",
    "Resumen de lo que necesita atención antes de vender, comprar o cerrar caja.",
    "Urgente",
    "Revisar",
    "Bien",
    "ACCIÓN RECOMENDADA",
    "Pendiente",
    "Gravedad",
    "Qué pasa",
    "Acción",
    "Ver evidencia técnica"
  ],
  routeOrder: [
    "Marketing",
    "Hoy",
    "Ventas y caja",
    "Inventario",
    "Compras",
    "Proveedores",
    "Sincronización",
    "Reportes",
    "Análisis",
    "Sistema",
    "Configuración"
  ],
  notes: [
    "La ruta / conserva la pantalla de marketing.",
    "La ruta /dashboard es la primera pantalla operativa.",
    "La pantalla usa datos operativos existentes y no inventa métricas reales.",
    "La evidencia técnica queda colapsada."
  ]
} as const;
