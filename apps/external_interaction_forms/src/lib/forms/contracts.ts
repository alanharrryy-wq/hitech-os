export type FormFieldKind = "text" | "textarea" | "email" | "date" | "select" | "checkbox" | "file";

export type FormScalarValue = string | boolean;

export type FormValues = Record<string, FormScalarValue>;

export type FormFieldErrors = Record<string, string>;

export interface FormFieldOption {
  value: string;
  label: string;
}

export interface FormFieldDefinition {
  id: string;
  label: string;
  kind: FormFieldKind;
  required?: boolean;
  placeholder?: string;
  helpText?: string;
  options?: readonly FormFieldOption[];
  visibleWhen?: (values: FormValues) => boolean;
}

export interface FormStepDefinition {
  id: string;
  title: string;
  description: string;
  submitLabel: string;
  fields: readonly FormFieldDefinition[];
}

export interface FormAttachmentRule {
  fieldId: string;
  requiredWhen?: (values: FormValues) => boolean;
}

export interface FormDisplayMetadata {
  menuLabel: string;
  appName: string;
  tagline: string;
  successTitle: string;
  successDescription: string;
}

export interface DraftRecordRef {
  recordId: string;
  secureToken: string;
}

export interface CreateRecordPayload {
  schemaId: string;
  title?: string;
  fields: Record<string, unknown>;
  stepId: string;
  submit: false;
}

export interface UpdateRecordPayload {
  fields: Record<string, unknown>;
  stepId: string;
}

export interface SubmitRecordPayload extends UpdateRecordPayload {
  state: "submitted";
}

export interface FormPluginDefinition {
  formTypeId: string;
  schemaId: string;
  display: FormDisplayMetadata;
  steps: readonly FormStepDefinition[];
  defaults: () => FormValues;
  attachmentRules?: readonly FormAttachmentRule[];
  validateStep: (stepId: string, values: FormValues, files: Record<string, File | null>) => FormFieldErrors;
  buildCreatePayload: (values: FormValues) => CreateRecordPayload;
  buildUpdatePayload: (values: FormValues, stepId: string) => UpdateRecordPayload;
  buildSubmitPayload: (values: FormValues, stepId: string) => SubmitRecordPayload;
}
