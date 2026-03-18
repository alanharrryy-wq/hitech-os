import { type PreviewDiffInput, type PreviewPatchSummary } from "./contracts";

export function summarizePreviewDiff(input: PreviewDiffInput): PreviewPatchSummary {
  const baselineKeys = new Set(Object.keys(input.baseline));
  const stagedKeys = new Set(Object.keys(input.staged));
  const draftKeys = new Set(Object.keys(input.draft));
  const changedFields = [...stagedKeys].filter((key) => input.staged[key] !== input.draft[key] || input.staged[key] !== input.baseline[key]);
  const addedEntityIds = [...stagedKeys].filter((key) => !baselineKeys.has(key));
  const removedEntityIds = [...baselineKeys].filter((key) => !stagedKeys.has(key));
  const movedEntityIds = [...draftKeys].filter((key) => key.endsWith(".position") && input.staged[key] !== input.baseline[key]);

  return {
    changedFields,
    changeCount: changedFields.length,
    addedEntityIds,
    removedEntityIds,
    movedEntityIds
  };
}
