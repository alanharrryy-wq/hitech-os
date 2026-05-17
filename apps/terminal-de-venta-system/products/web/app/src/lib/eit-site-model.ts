// PRISMA_CTX_WEB_EIT_GENERATED_V1
export type EitSitePillar = {
  title: string;
  body: string;
};

export type EitSiteModel = {
  eyebrow: string;
  title: string;
  subtitle: string;
  rule: string;
  pillars: EitSitePillar[];
  routes: string[];
};

export const eitSiteModel: EitSiteModel = {
  eyebrow: "PRISMA EIT / Executive Intelligence Terminal",
  title: "Operaciones reales convertidas en inteligencia auditable.",
  subtitle:
    "PRISMA no es un POS encogido. Es un Knowledge OS operativo: entidades, eventos, responsables, estados, evidencias, alertas, reportes e historial verificable.",
  rule: "Tablet opera · PC gobierna · Mobile supervisa · Core registra · Control audita",
  pillars: [
    {
      title: "Contexto vivo",
      body: "Cada frente conserva evidencia, frescura, estado y trazabilidad para que el equipo no dependa de memoria ni capturas sueltas.",
    },
    {
      title: "Gobierno operativo",
      body: "Los gates, manifiestos, perfiles y reportes convierten el trabajo diario en historial revisable.",
    },
    {
      title: "Supervisión accionable",
      body: "Mobile y Control no adornan dashboards: priorizan decisiones, responsables y acciones con evidencia.",
    },
  ],
  routes: ["/", "/status", "/prisma", "/control", "/contact"],
};
