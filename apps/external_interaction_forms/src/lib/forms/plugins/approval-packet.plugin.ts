import type { FormPluginDefinition } from "@/lib/forms/contracts";

function requiredText(value: string | undefined): boolean {
  return Boolean(value && value.trim().length > 0);
}

export const approvalPacketFormPlugin: FormPluginDefinition = {
  formTypeId: "approval_packet_public",
  schemaId: "approval_packet",
  display: {
    menuLabel: "Approval Packet",
    appName: "Hitech Approval Intake",
    tagline: "Formulario publico para revision de paquetes de aprobacion por token.",
    successTitle: "Paquete enviado",
    successDescription: "El paquete fue enviado para revision. Te contactaremos con el resultado."
  },
  steps: [
    {
      id: "packet",
      title: "Datos del paquete",
      description: "Comparte el contexto base para crear el borrador del paquete.",
      submitLabel: "Guardar y continuar",
      fields: [
        { id: "packet_title", label: "Titulo del paquete", kind: "text", required: true, placeholder: "Ej. Renovacion de proveedor Q3" },
        { id: "packet_owner", label: "Responsable", kind: "text", required: true, placeholder: "Nombre del responsable" },
        { id: "packet_scope", label: "Alcance", kind: "textarea", required: true, placeholder: "Resume el alcance del paquete." },
        { id: "packet_due_date", label: "Fecha limite", kind: "date" }
      ]
    },
    {
      id: "decision",
      title: "Inputs de decision",
      description: "Completa el checklist requerido antes del envio final.",
      submitLabel: "Enviar paquete",
      fields: [
        {
          id: "risk_level",
          label: "Nivel de riesgo",
          kind: "select",
          required: true,
          options: [
            { value: "low", label: "low" },
            { value: "moderate", label: "moderate" },
            { value: "high", label: "high" }
          ]
        },
        { id: "compliance_reviewed", label: "Cumplimiento revisado", kind: "checkbox", required: true },
        { id: "decision_notes", label: "Notas de decision", kind: "textarea", placeholder: "Comentarios adicionales para el revisor." }
      ]
    }
  ],
  defaults: () => ({
    packet_title: "",
    packet_owner: "",
    packet_scope: "",
    packet_due_date: "",
    risk_level: "moderate",
    compliance_reviewed: false,
    decision_notes: ""
  }),
  validateStep: (stepId, values) => {
    const errors: Record<string, string> = {};

    if (stepId === "packet") {
      if (!requiredText(String(values["packet_title"] ?? ""))) {
        errors["packet_title"] = "Escribe un titulo para el paquete.";
      }
      if (!requiredText(String(values["packet_owner"] ?? ""))) {
        errors["packet_owner"] = "Comparte quien es responsable.";
      }
      if (!requiredText(String(values["packet_scope"] ?? ""))) {
        errors["packet_scope"] = "Describe el alcance del paquete.";
      }
    }

    if (stepId === "decision" && values["compliance_reviewed"] !== true) {
      errors["compliance_reviewed"] = "Debes confirmar que cumplimiento fue revisado.";
    }

    return errors;
  },
  buildCreatePayload: (values) => ({
    schemaId: "approval_packet",
    title: String(values["packet_title"] ?? "").trim(),
    fields: {
      packet_title: values["packet_title"],
      packet_owner: values["packet_owner"],
      packet_scope: values["packet_scope"],
      packet_due_date: String(values["packet_due_date"] ?? "") || undefined
    },
    stepId: "packet",
    submit: false
  }),
  buildUpdatePayload: (values, stepId) => {
    if (stepId === "packet") {
      return {
        fields: {
          packet_title: values["packet_title"],
          packet_owner: values["packet_owner"],
          packet_scope: values["packet_scope"],
          packet_due_date: String(values["packet_due_date"] ?? "") || undefined
        },
        stepId
      };
    }

    return {
      fields: {
        risk_level: values["risk_level"],
        compliance_reviewed: values["compliance_reviewed"] === true,
        decision_notes: String(values["decision_notes"] ?? "") || undefined
      },
      stepId: "decision"
    };
  },
  buildSubmitPayload: (values, stepId) => ({
    ...approvalPacketFormPlugin.buildUpdatePayload(values, stepId),
    state: "submitted"
  })
};

