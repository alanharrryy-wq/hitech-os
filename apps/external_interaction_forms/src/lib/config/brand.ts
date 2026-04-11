export const brandConfig = {
  appName: "Hitech External Intake",
  tagline: "Formulario publico para solicitudes compartidas por WhatsApp",
  storageKey: "hitech.external_interaction_forms.draft.v1",
  successTitle: "Solicitud enviada",
  successDescription:
    "Tu solicitud fue registrada correctamente. El equipo de operaciones la revisara en breve.",
  defaults: {
    apiBaseUrl: "http://127.0.0.1:3100",
    prodApiBaseUrl: "https://engine.hitechrts.com",
    appUrl: "http://127.0.0.1:3200",
    prodAppUrl: "https://forms.hitechrts.com"
  }
} as const;
