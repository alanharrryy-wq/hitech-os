import type {
  DraftRecordRef,
  FormFieldErrors,
  FormPluginDefinition,
  FormValues
} from "@/lib/forms/contracts";
import {
  createDraftRecord,
  submitRecordByToken,
  updateDraftByToken,
  uploadAttachmentForRecord
} from "@/lib/forms/transport";

export interface StepPersistResult {
  recordRef: DraftRecordRef;
}

export interface FinalSubmitResult {
  recordRef: DraftRecordRef;
}

export function validateCurrentStep(
  plugin: FormPluginDefinition,
  stepId: string,
  values: FormValues,
  files: Record<string, File | null>
): FormFieldErrors {
  return plugin.validateStep(stepId, values, files);
}

export async function persistStepDraft(params: {
  plugin: FormPluginDefinition;
  stepId: string;
  values: FormValues;
  existingRef: DraftRecordRef | null;
}): Promise<StepPersistResult> {
  const { plugin, stepId, values, existingRef } = params;

  if (!existingRef) {
    const createdRef = await createDraftRecord(plugin.formTypeId, plugin.buildCreatePayload(values));
    return { recordRef: createdRef };
  }

  await updateDraftByToken(plugin.formTypeId, existingRef.secureToken, plugin.buildUpdatePayload(values, stepId));
  return { recordRef: existingRef };
}

export async function submitFinalRecord(params: {
  plugin: FormPluginDefinition;
  stepId: string;
  values: FormValues;
  files: Record<string, File | null>;
  recordRef: DraftRecordRef;
}): Promise<FinalSubmitResult> {
  const { plugin, stepId, values, files, recordRef } = params;

  await updateDraftByToken(plugin.formTypeId, recordRef.secureToken, plugin.buildUpdatePayload(values, stepId));

  for (const rule of plugin.attachmentRules ?? []) {
    const shouldRequire = rule.requiredWhen?.(values) ?? false;
    const selectedFile = files[rule.fieldId];

    if (shouldRequire && !selectedFile) {
      throw new Error("Missing required attachment before final submit");
    }

    if (selectedFile) {
      await uploadAttachmentForRecord(plugin.formTypeId, recordRef.recordId, selectedFile);
    }
  }

  await submitRecordByToken(
    plugin.formTypeId,
    recordRef.secureToken,
    plugin.buildSubmitPayload(values, stepId)
  );

  return { recordRef };
}

