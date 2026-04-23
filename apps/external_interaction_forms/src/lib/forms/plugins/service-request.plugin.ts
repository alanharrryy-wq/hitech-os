import type { FormPluginDefinition } from "@/lib/forms/contracts";

function requiredText(value: string | undefined): boolean {
  return Boolean(value && value.trim().length > 0);
}

function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

export const serviceRequestFormPlugin: FormPluginDefinition = {
  formTypeId: "service_request_public",
  schemaId: "service_request",
  display: {
    menuLabel: "Service Request",
    appName: "Hitech External Intake",
    tagline: "Formulario publico para solicitudes compartidas por WhatsApp",
    successTitle: "Solicitud enviada",
    successDescription: "Tu solicitud fue registrada correctamente. El equipo de operaciones la revisara en breve."
  },
  steps: [
    {
      id: "requester",
      title: "Tus datos y solicitud",
      description: "Comparte la informacion principal para crear un borrador seguro.",
      submitLabel: "Guardar y continuar",
      fields: [
        { id: "request_title", label: "Titulo de la solicitud", kind: "text", required: true, placeholder: "Ej. Solicitud de apoyo operativo" },
        { id: "request_description", label: "Descripcion", kind: "textarea", required: true, placeholder: "Explica brevemente que necesitas y por que." },
        {
          id: "request_priority",
          label: "Prioridad",
          kind: "select",
          required: true,
          options: [
            { value: "low", label: "low" },
            { value: "medium", label: "medium" },
            { value: "high", label: "high" },
            { value: "urgent", label: "urgent" }
          ]
        },
        { id: "requester_name", label: "Nombre", kind: "text", required: true, placeholder: "Tu nombre completo" },
        { id: "requester_email", label: "Correo", kind: "email", required: true, placeholder: "nombre@empresa.com" }
      ]
    },
    {
      id: "context",
      title: "Contexto",
      description: "Completa el contexto opcional antes del envio final.",
      submitLabel: "Enviar solicitud",
      fields: [
        { id: "required_by", label: "Fecha requerida", kind: "date" },
        {
          id: "region",
          label: "Region",
          kind: "select",
          options: [
            { value: "", label: "Sin region" },
            { value: "north", label: "north" },
            { value: "south", label: "south" },
            { value: "east", label: "east" },
            { value: "west", label: "west" },
            { value: "global", label: "global" }
          ]
        },
        { id: "needs_attachment", label: "Necesito agregar un archivo adjunto", kind: "checkbox" },
        {
          id: "attachments",
          label: "Archivo adjunto",
          kind: "file",
          helpText: "Si recargas la pagina, deberas seleccionar el archivo otra vez.",
          visibleWhen: (values) => values["needs_attachment"] === true
        }
      ]
    }
  ],
  defaults: () => ({
    request_title: "",
    request_description: "",
    request_priority: "medium",
    requester_name: "",
    requester_email: "",
    required_by: "",
    region: "",
    needs_attachment: false
  }),
  attachmentRules: [
    {
      fieldId: "attachments",
      requiredWhen: (values) => values["needs_attachment"] === true
    }
  ],
  validateStep: (stepId, values, files) => {
    const errors: Record<string, string> = {};

    if (stepId === "requester") {
      if (!requiredText(String(values["request_title"] ?? ""))) {
        errors["request_title"] = "Escribe un titulo para tu solicitud.";
      }
      if (!requiredText(String(values["request_description"] ?? ""))) {
        errors["request_description"] = "Describe la solicitud con un poco mas de detalle.";
      }
      if (!requiredText(String(values["requester_name"] ?? ""))) {
        errors["requester_name"] = "Comparte tu nombre.";
      }
      const email = String(values["requester_email"] ?? "");
      if (!requiredText(email)) {
        errors["requester_email"] = "Comparte un correo de contacto.";
      } else if (!isValidEmail(email)) {
        errors["requester_email"] = "Ingresa un correo valido.";
      }
    }

    if (stepId === "context" && values["needs_attachment"] === true && !files["attachments"]) {
      errors["attachments"] = "Selecciona un archivo para continuar.";
    }

    return errors;
  },
  buildCreatePayload: (values) => ({
    schemaId: "service_request",
    title: String(values["request_title"] ?? "").trim(),
    fields: {
      request_title: values["request_title"],
      request_description: values["request_description"],
      request_priority: values["request_priority"],
      requester_name: values["requester_name"],
      requester_email: values["requester_email"]
    },
    stepId: "requester",
    submit: false
  }),
  buildUpdatePayload: (values, stepId) => {
    if (stepId === "requester") {
      return {
        fields: {
          request_title: values["request_title"],
          request_description: values["request_description"],
          request_priority: values["request_priority"],
          requester_name: values["requester_name"],
          requester_email: values["requester_email"]
        },
        stepId
      };
    }

    return {
      fields: {
        required_by: String(values["required_by"] ?? "") || undefined,
        region: String(values["region"] ?? "") || undefined,
        needs_attachment: values["needs_attachment"] === true
      },
      stepId: "context"
    };
  },
  buildSubmitPayload: (values, stepId) => ({
    ...serviceRequestFormPlugin.buildUpdatePayload(values, stepId),
    state: "submitted"
  })
};
