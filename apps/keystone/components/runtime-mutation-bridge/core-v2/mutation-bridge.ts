import {
  applySceneLookPatch,
  commitDraftDocument,
  discardDraftToBaseline,
  insertWidgetFromPrefab,
  moveLayoutNode,
  removeWidget,
  reorderLayoutNode,
  resetTargetFromBaseline,
  resizeLayoutNode,
  updateWidgetProps,
  updateWidgetStyle,
  type SceneDocument,
  type SelectionTarget,
} from "./scene-domain";
import type { RuntimeMutationCommand } from "./mutation-contract";
import { createAcceptedMutationResult, createRejectedMutationResult, type RuntimeMutationResult } from "./mutation-result";
import type { RuntimeMutationBridgeAdapter } from "./runtime-adapter";
import { createInMemoryPreviewAdapter } from "./preview-adapter";
import { validateRuntimeMutationCommand } from "./mutation-validator";

export interface RuntimeMutationExecutionContext {
  readonly baseline: SceneDocument;
  readonly draft: SceneDocument;
  readonly currentSelection: SelectionTarget | null;
}

export function applyRuntimeMutationThroughBridge(
  context: RuntimeMutationExecutionContext,
  command: RuntimeMutationCommand,
  adapter: RuntimeMutationBridgeAdapter = createInMemoryPreviewAdapter()
): RuntimeMutationResult {
  const validation = validateRuntimeMutationCommand(command, context.baseline, context.draft);
  const baselineSnapshot = adapter.snapshot(context.baseline);
  const draftSnapshot = adapter.snapshot(context.draft);
  const fallbackCommandId = command.commandId;
  const fallbackCommandType = command.type;

  if (!validation.accepted) {
    adapter.reject({
      commandId: command.commandId,
      commandType: command.type,
      phase: "rejection",
      document: draftSnapshot,
      issues: validation.issues,
    });
    return createRejectedMutationResult({
      commandId: command.commandId,
      commandType: command.type,
      baseline: baselineSnapshot,
      draft: draftSnapshot,
      preview: adapter.snapshot(draftSnapshot),
      issues: validation.issues,
    });
  }

  switch (command.type) {
    case "scene.look.update": {
      const effect = applySceneLookPatch(draftSnapshot, command.payload.patch);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Scene look patch accepted through core-v2.",
      });
    }

    case "layout.node.move": {
      const effect = moveLayoutNode(draftSnapshot, command.target.id, command.payload.deltaX, command.payload.deltaY);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Layout move accepted through core-v2.",
      });
    }

    case "layout.node.resize": {
      const effect = resizeLayoutNode(draftSnapshot, command.target.id, command.payload.widthDelta, command.payload.heightDelta);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Layout resize accepted through core-v2.",
      });
    }

    case "layout.node.reorder": {
      const effect = reorderLayoutNode(draftSnapshot, command.target.id, command.payload.toIndex);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Layout reorder accepted through core-v2.",
      });
    }

    case "widget.insert-from-prefab": {
      const effect = insertWidgetFromPrefab(draftSnapshot, command.payload.slotId, command.payload.prefab);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Widget insertion accepted through core-v2.",
      });
    }

    case "widget.update-props": {
      const effect = updateWidgetProps(draftSnapshot, command.target.id, command.payload.patch);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Widget props update accepted through core-v2.",
      });
    }

    case "widget.update-style": {
      const effect = updateWidgetStyle(draftSnapshot, command.target.id, command.payload.patch);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "preview",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Widget style update accepted through core-v2.",
      });
    }

    case "widget.remove": {
      const effect = removeWidget(draftSnapshot, command.payload.widgetId);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Widget removal accepted through core-v2.",
      });
    }

    case "selection.reset": {
      if (command.target.kind === "draft") {
        return createRejectedMutationResult({
          commandId: command.commandId,
          commandType: command.type,
          baseline: baselineSnapshot,
          draft: draftSnapshot,
          preview: adapter.snapshot(draftSnapshot),
          issues: [{ code: "invalid-target", message: "Selection reset cannot target the draft." }],
        });
      }
      const effect = resetTargetFromBaseline(draftSnapshot, baselineSnapshot, command.target);
      const preview = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        changedTargets: effect.changedTargets,
        document: effect.document,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "draft-update",
        baseline: baselineSnapshot,
        draft: effect.document,
        preview,
        changedTargets: effect.changedTargets,
        message: "Selection reset accepted through core-v2.",
      });
    }

    case "draft.commit": {
      const committed = commitDraftDocument(draftSnapshot);
      const published = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "commit",
        changedTargets: [committed.scene.id],
        document: committed,
      });
      const normalized = adapter.snapshot(published);
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "commit",
        baseline: normalized,
        draft: adapter.snapshot(normalized),
        preview: adapter.snapshot(normalized),
        changedTargets: [committed.scene.id],
        message: "Draft committed to baseline through core-v2.",
      });
    }

    case "draft.discard": {
      const reset = discardDraftToBaseline(baselineSnapshot);
      const published = adapter.publish({
        commandId: command.commandId,
        commandType: command.type,
        phase: "discard",
        changedTargets: [baselineSnapshot.scene.id],
        document: reset,
      });
      return createAcceptedMutationResult({
        commandId: command.commandId,
        commandType: command.type,
        phase: "discard",
        baseline: baselineSnapshot,
        draft: published,
        preview: adapter.snapshot(published),
        changedTargets: [baselineSnapshot.scene.id],
        message: "Draft discarded and baseline restored through core-v2.",
      });
    }

    default: {
      return createRejectedMutationResult({
        commandId: fallbackCommandId,
        commandType: fallbackCommandType,
        baseline: baselineSnapshot,
        draft: draftSnapshot,
        preview: adapter.snapshot(draftSnapshot),
        issues: [{ code: "invalid-command", message: `Unhandled runtime mutation ${fallbackCommandType}.` }],
      });
    }
  }
}
