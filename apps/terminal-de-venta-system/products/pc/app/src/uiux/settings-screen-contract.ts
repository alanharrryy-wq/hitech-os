export const settingsScreenContract = {
  title: "Configuración",
  subtitle: "Ajustes seguros para negocio, usuarios, equipos y preferencias sin romper la operación.",
  status: "Ajustes bajo control",
  lastUpdated: "listo para revisar",
  summaryCards: [
    {
      eyebrow: "Negocio",
      title: "Datos protegidos",
      tone: "ok" as const,
      lines: ["Nombre, sucursal y reglas visibles", "Cambios importantes con confirmación"]
    },
    {
      eyebrow: "Usuarios",
      title: "Permisos claros",
      tone: "info" as const,
      lines: ["Roles separados por operación", "Accesos sensibles cerrados por defecto"]
    },
    {
      eyebrow: "Equipos",
      title: "Terminales cuidadas",
      tone: "warn" as const,
      lines: ["Revisar equipos antes de cambios globales", "Licencia y tablet con rutas separadas"]
    }
  ],
  recommendedAction: {
    title: "Revisa ajustes avanzados sólo cuando haya una razón clara.",
    motive: "un cambio global puede afectar venta, sincronización o acceso de usuarios.",
    actions: [
      { label: "Revisar licencia", href: "/settings/license", primary: true },
      { label: "Ver glosario", href: "/glosario" },
      { label: "Revisar sistema", href: "/data-quality" }
    ]
  },
  tableTitle: "Áreas configurables",
  tableSubtitle: "Todo cambio sensible debe explicar alcance, impacto y si requiere confirmación.",
  columns: ["Área", "Qué puedes ajustar", "Nivel", "Acción"],
  rows: [
    { Área: "Negocio", "Qué puedes ajustar": "Datos visibles, sucursal y preferencias generales", Nivel: "Seguro", Acción: "Revisar" },
    { Área: "Usuarios", "Qué puedes ajustar": "Roles, permisos y accesos operativos", Nivel: "Requiere cuidado", Acción: "Ver usuarios" },
    { Área: "Equipos", "Qué puedes ajustar": "Terminales, tablet y dispositivos vinculados", Nivel: "Requiere revisión", Acción: "Ver equipos" },
    { Área: "Preferencias", "Qué puedes ajustar": "Idioma visible, formato y lectura de pantallas", Nivel: "Seguro", Acción: "Ajustar" },
    { Área: "Licencia", "Qué puedes ajustar": "Funciones activas y continuidad del servicio", Nivel: "Requiere cuidado", Acción: "Ver licencia" },
    { Área: "Avanzado", "Qué puedes ajustar": "Opciones sensibles cerradas por defecto", Nivel: "Alto cuidado", Acción: "Ver técnica" }
  ],
  evidence: [
    { kind: "governance" as const,  label: "Fuente", value: "configuración local, licencia y reglas de navegación" },
    { kind: "governance" as const,  label: "Criterio", value: "Todo cambio sensible debe explicar alcance antes de guardar cambios" },
    { kind: "governance" as const,  label: "Confianza", value: "alta cuando la configuración del proyecto se conserva sin cambios" },
    { kind: "governance" as const,  label: "Rutas", value: "/settings, /settings/license y /glosario" }
  ]
};

export const settingsLicenseScreenContract = {
  title: "Licencia y funciones",
  subtitle: "Revisa qué está activo, cuándo actualizar y qué funciones están disponibles.",
  status: "Licencia revisable",
  lastUpdated: "listo para confirmar",
  summaryCards: [
    {
      eyebrow: "Licencia",
      title: "Estado visible",
      tone: "info" as const,
      lines: ["Vigencia y continuidad en una sola vista", "Sin cambios automáticos por revisar"]
    },
    {
      eyebrow: "Funciones",
      title: "Acceso claro",
      tone: "ok" as const,
      lines: ["Herramientas activas separadas", "Bloqueos explicados en lenguaje humano"]
    },
    {
      eyebrow: "Seguridad",
      title: "Sin interrupciones",
      tone: "warn" as const,
      lines: ["Actualizar sólo con operación tranquila", "Confirmar antes de aplicar cambios"]
    }
  ],
  recommendedAction: {
    title: "Verifica la licencia antes de cambiar funciones para todos.",
    motive: "si una función no está disponible, conviene explicarlo antes de mover permisos o equipos.",
    actions: [
      { label: "Actualizar estado", href: "/settings/license", primary: true },
      { label: "Revisar sistema", href: "/data-quality" },
      { label: "Volver a configuración", href: "/settings" }
    ]
  },
  tableTitle: "Lectura de licencia",
  tableSubtitle: "Lo importante es saber qué está activo y qué requiere revisión.",
  columns: ["Elemento", "Estado", "Qué pasa", "Acción"],
  rows: [
    { Elemento: "Licencia", Estado: "Revisable", "Qué pasa": "Estado disponible para confirmar", Acción: "Actualizar" },
    { Elemento: "Funciones", Estado: "Bien", "Qué pasa": "Lista de herramientas visible", Acción: "Ver detalle" },
    { Elemento: "Continuidad", Estado: "Atención", "Qué pasa": "Conviene revisar antes de cambios globales", Acción: "Revisar" }
  ],
  evidence: [
    { kind: "governance" as const,  label: "Fuente", value: "servicio local de licencia y estado de actualización" },
    { kind: "governance" as const,  label: "Criterio", value: "ningún cambio sensible se aplica sin confirmación visible" },
    { kind: "governance" as const,  label: "Confianza", value: "alta cuando el estado local responde correctamente" },
    { kind: "governance" as const,  label: "Ruta", value: "/settings/license" }
  ]
};

export const settingsGlossaryScreenContract = {
  title: "Glosario",
  subtitle: "Traducciones visibles para que el sistema hable negocio y no ingeniería.",
  status: "Lenguaje alineado",
  lastUpdated: "listo para usar",
  summaryCards: [
    {
      eyebrow: "Operación",
      title: "Términos humanos",
      tone: "ok" as const,
      lines: ["Ventas, compras e inventario con nombres claros", "Sin tecnicismos como primera lectura"]
    },
    {
      eyebrow: "Soporte",
      title: "Técnica traducida",
      tone: "info" as const,
      lines: ["Detalle disponible bajo evidencia", "Lenguaje técnico sólo cuando se necesita"]
    },
    {
      eyebrow: "Consistencia",
      title: "Mismo idioma",
      tone: "ok" as const,
      lines: ["Pantallas con la misma estructura", "Acciones con verbos claros"]
    }
  ],
  recommendedAction: {
    title: "Usa el glosario como referencia antes de nombrar nuevas pantallas.",
    motive: "mantiene consistencia entre operación, soporte y reportes.",
    actions: [
      { label: "Ver configuración", href: "/settings", primary: true },
      { label: "Ver sistema", href: "/data-quality" },
      { label: "Ver reportes", href: "/exportables" }
    ]
  },
  tableTitle: "Términos visibles",
  tableSubtitle: "Palabras permitidas para pantallas, acciones y explicaciones.",
  columns: ["Término", "Uso", "Nota", "Acción"],
  rows: [
    { Término: "Sincronización", Uso: "Estado entre equipos", Nota: "Preferido", Acción: "Usar" },
    { Término: "Código de barras", Uso: "Catálogo e inventario", Nota: "Preferido", Acción: "Usar" },
    { Término: "Base principal", Uso: "Evidencia técnica", Nota: "Sólo en detalle", Acción: "Explicar" },
    { Término: "Historial", Uso: "Auditoría y cambios", Nota: "Preferido", Acción: "Usar" }
  ],
  evidence: [
    { kind: "governance" as const,  label: "Fuente", value: "diccionario visible de PRISMA PC" },
    { kind: "governance" as const,  label: "Criterio", value: "términos técnicos se traducen antes de mostrarse al usuario" },
    { kind: "governance" as const,  label: "Confianza", value: "alta cuando botones y estados usan palabras permitidas" },
    { kind: "governance" as const,  label: "Ruta", value: "/glosario" }
  ]
};
