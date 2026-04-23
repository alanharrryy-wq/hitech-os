export type PublicFormCapability = "create" | "update" | "submit" | "attachments";

export interface PublicFormRegistration {
  formTypeId: string;
  schemaId: string;
  createStepId: string;
  updateStepIds: readonly string[];
  attachmentsAllowed: boolean;
}

const PUBLIC_FORM_REGISTRATIONS: readonly PublicFormRegistration[] = [
  {
    formTypeId: "service_request_public",
    schemaId: "service_request",
    createStepId: "requester",
    updateStepIds: ["requester", "context"],
    attachmentsAllowed: true
  },
  {
    formTypeId: "approval_packet_public",
    schemaId: "approval_packet",
    createStepId: "packet",
    updateStepIds: ["packet", "decision"],
    attachmentsAllowed: false
  }
];

function assertPublicFormRegistry(registrations: readonly PublicFormRegistration[]) {
  const ids = new Set<string>();
  for (const entry of registrations) {
    if (ids.has(entry.formTypeId)) {
      throw new Error(`Duplicate public form registration: '${entry.formTypeId}'`);
    }
    ids.add(entry.formTypeId);
  }
}

assertPublicFormRegistry(PUBLIC_FORM_REGISTRATIONS);

const PUBLIC_FORM_MAP = new Map(PUBLIC_FORM_REGISTRATIONS.map((entry) => [entry.formTypeId, entry]));

export function listPublicFormRegistrations(): readonly PublicFormRegistration[] {
  return PUBLIC_FORM_REGISTRATIONS;
}

export function getPublicFormRegistration(formTypeId: string): PublicFormRegistration {
  const registration = PUBLIC_FORM_MAP.get(formTypeId);
  if (!registration) {
    throw new Error(`Unknown public form type '${formTypeId}'`);
  }
  return registration;
}

export function validatePublicFormOperation(params: {
  formTypeId?: string | null;
  schemaId: string;
  stepId?: string;
  capability: PublicFormCapability;
}): void {
  const { formTypeId, schemaId, stepId, capability } = params;

  if (!formTypeId) {
    return;
  }

  const registration = getPublicFormRegistration(formTypeId);
  if (registration.schemaId !== schemaId) {
    throw new Error(
      `Public form '${formTypeId}' is bound to schema '${registration.schemaId}', not '${schemaId}'`
    );
  }

  if (capability === "create" && stepId && stepId !== registration.createStepId) {
    throw new Error(
      `Public form '${formTypeId}' create step must be '${registration.createStepId}', received '${stepId}'`
    );
  }

  if ((capability === "update" || capability === "submit") && stepId) {
    if (!registration.updateStepIds.includes(stepId)) {
      throw new Error(
        `Public form '${formTypeId}' does not allow step '${stepId}' for ${capability}`
      );
    }
  }

  if (capability === "attachments" && !registration.attachmentsAllowed) {
    throw new Error(`Public form '${formTypeId}' does not allow attachments`);
  }
}

