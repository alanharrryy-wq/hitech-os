import { mergeSceneLookModel } from "../../live-scene-composer/scene-look-model";
import type {
  MutationFeedback,
  SceneDocument,
  SelectionTarget,
  SlotEntity,
  WidgetEntity,
} from "../../live-scene-composer/authoring-workbench-v1/authoring-workbench-contracts";
import { cloneSceneDocument, coerceStylePatch, createWidgetFromPrefab } from "../../live-scene-composer/authoring-workbench-v1/model/scene-graph";
import type { RuntimeMutationBridgeAdapter } from "./adapters/in-memory-preview-adapter";
import type { RuntimeMutationCommand, RuntimeMutationExecutionContext, RuntimeMutationResult, RuntimeMutationValidationError } from "./contract";
import { validateRuntimeMutationCommand } from "./validateRuntimeMutationCommand";

type MutableSceneDocument = any;

function createFeedback(commandType: string, accepted: boolean, message: string, code: string, changedTargets: readonly string[]): MutationFeedback {
  return {
    commandType,
    level: accepted ? "success" : "error",
    message,
    code,
    changedTargets,
    recordedAtIso: new Date().toISOString(),
  };
}

function acceptedResult(
  command: RuntimeMutationCommand,
  baseline: SceneDocument,
  draft: SceneDocument,
  preview: SceneDocument,
  changedTargets: readonly string[],
  message: string
): RuntimeMutationResult {
  return {
    accepted: true,
    baseline,
    draft,
    preview,
    feedback: createFeedback(command.type, true, message, "accepted", changedTargets),
    changedTargets,
    validationErrors: [],
  };
}

function rejectedResult(
  command: RuntimeMutationCommand,
  baseline: SceneDocument,
  draft: SceneDocument,
  errors: readonly RuntimeMutationValidationError[]
): RuntimeMutationResult {
  return {
    accepted: false,
    baseline,
    draft,
    preview: cloneSceneDocument(draft),
    feedback: createFeedback(command.type, false, errors.map((error) => error.message).join(" "), errors[0]?.code ?? "rejected", []),
    changedTargets: [],
    validationErrors: errors,
  };
}

function removeWidgetFromSlot(slot: SlotEntity, widgetId: string): SlotEntity {
  return {
    ...slot,
    widgetIds: slot.widgetIds.filter((candidate) => candidate !== widgetId),
  };
}

function ensureWidgetReset(nextDraft: MutableSceneDocument, baseline: MutableSceneDocument, widgetId: string): void {
  const baselineWidget = baseline.widgets[widgetId];
  const currentWidget = nextDraft.widgets[widgetId];
  if (baselineWidget) {
    nextDraft.widgets[widgetId] = JSON.parse(JSON.stringify(baselineWidget)) as WidgetEntity;
    const slotId = baselineWidget.slotId;
    const baselineSlot = baseline.slots[slotId];
    if (baselineSlot) {
      nextDraft.slots[slotId] = JSON.parse(JSON.stringify(baselineSlot)) as SlotEntity;
      baselineSlot.widgetIds.forEach((baselineWidgetId) => {
        if (baseline.widgets[baselineWidgetId]) {
          nextDraft.widgets[baselineWidgetId] = JSON.parse(JSON.stringify(baseline.widgets[baselineWidgetId])) as WidgetEntity;
        }
      });
    }
    return;
  }
  if (currentWidget) {
    const slot = nextDraft.slots[currentWidget.slotId];
    if (slot) {
      nextDraft.slots[currentWidget.slotId] = removeWidgetFromSlot(slot, widgetId);
    }
    delete nextDraft.widgets[widgetId];
  }
}

export function applyRuntimeMutationThroughBridge(
  context: RuntimeMutationExecutionContext,
  command: RuntimeMutationCommand,
  adapter?: RuntimeMutationBridgeAdapter
): RuntimeMutationResult {
  const validation = validateRuntimeMutationCommand(command, context.baseline, context.draft);
  if (!validation.accepted) {
    adapter?.record(command, "rejection", context.draft);
    return rejectedResult(command, context.baseline, context.draft, validation.errors);
  }
  const nextDraft = cloneSceneDocument(context.draft) as MutableSceneDocument;
  const baseline = cloneSceneDocument(context.baseline) as MutableSceneDocument;
  let changedTargets: string[] = [];
  switch (command.type) {
    case "scene.look.update": {
      nextDraft.scene = {
        ...nextDraft.scene,
        look: mergeSceneLookModel(nextDraft.scene.look, command.payload.patch),
      };
      changedTargets = [nextDraft.scene.id];
      break;
    }
    case "layout.node.move": {
      const node = nextDraft.layoutNodes[command.target.id];
      nextDraft.layoutNodes[command.target.id] = {
        ...node,
        frame: {
          ...node.frame,
          x: node.frame.x + command.payload.deltaX,
          y: node.frame.y + command.payload.deltaY,
        },
      };
      changedTargets = [command.target.id];
      break;
    }
    case "layout.node.resize": {
      const node = nextDraft.layoutNodes[command.target.id];
      nextDraft.layoutNodes[command.target.id] = {
        ...node,
        frame: {
          ...node.frame,
          width: Math.max(48, node.frame.width + command.payload.widthDelta),
          height: Math.max(32, node.frame.height + command.payload.heightDelta),
        },
      };
      changedTargets = [command.target.id];
      break;
    }
    case "layout.node.reorder": {
      const node = nextDraft.layoutNodes[command.target.id];
      if (node.parentId) {
        const parent = nextDraft.layoutNodes[node.parentId];
        const childIds = parent.childIds.filter((childId) => childId !== node.id);
        childIds.splice(command.payload.toIndex, 0, node.id);
        nextDraft.layoutNodes[node.parentId] = {
          ...parent,
          childIds,
        };
        childIds.forEach((childId, index) => {
          const child = nextDraft.layoutNodes[childId];
          nextDraft.layoutNodes[childId] = {
            ...child,
            orderIndex: index,
          };
        });
        changedTargets = [node.parentId, node.id];
      }
      break;
    }
    case "widget.insert-from-prefab": {
      const widget = createWidgetFromPrefab(command.payload.prefab, command.payload.slotId, nextDraft.meta.nextId);
      nextDraft.widgets[widget.id] = widget;
      const slot = nextDraft.slots[command.payload.slotId];
      nextDraft.slots[command.payload.slotId] = {
        ...slot,
        widgetIds: [...slot.widgetIds, widget.id],
      };
      nextDraft.meta = {
        ...nextDraft.meta,
        nextId: nextDraft.meta.nextId + 1,
      };
      changedTargets = [command.payload.slotId, widget.id];
      break;
    }
    case "widget.update-props": {
      const widget = nextDraft.widgets[command.target.id];
      nextDraft.widgets[command.target.id] = {
        ...widget,
        props: {
          ...widget.props,
          ...command.payload.patch,
        },
      };
      changedTargets = [command.target.id];
      break;
    }
    case "widget.update-style": {
      const widget = nextDraft.widgets[command.target.id];
      nextDraft.widgets[command.target.id] = {
        ...widget,
        style: coerceStylePatch(widget.style, command.payload.patch),
      };
      changedTargets = [command.target.id];
      break;
    }
    case "widget.remove": {
      const widget = nextDraft.widgets[command.payload.widgetId];
      if (widget) {
        const slot = nextDraft.slots[widget.slotId];
        if (slot) {
          nextDraft.slots[widget.slotId] = removeWidgetFromSlot(slot, widget.id);
        }
        delete nextDraft.widgets[command.payload.widgetId];
      }
      changedTargets = [command.payload.widgetId];
      break;
    }
    case "selection.reset": {
      if (command.target.kind === "scene") {
        nextDraft.scene = JSON.parse(JSON.stringify(baseline.scene));
        changedTargets = [baseline.scene.id];
      } else if (command.target.kind === "layout-node") {
        const baselineNode = baseline.layoutNodes[command.target.id];
        if (baselineNode) {
          nextDraft.layoutNodes[command.target.id] = JSON.parse(JSON.stringify(baselineNode));
          changedTargets = [command.target.id];
        }
      } else if (command.target.kind === "slot") {
        const baselineSlot = baseline.slots[command.target.id];
        if (baselineSlot) {
          const draftSlot = nextDraft.slots[command.target.id];
          if (draftSlot) {
            for (const widgetId of draftSlot.widgetIds) {
              if (!baselineSlot.widgetIds.includes(widgetId)) {
                delete nextDraft.widgets[widgetId];
              }
            }
          }
          nextDraft.slots[command.target.id] = JSON.parse(JSON.stringify(baselineSlot));
          baselineSlot.widgetIds.forEach((widgetId) => {
            const baselineWidget = baseline.widgets[widgetId];
            if (baselineWidget) {
              nextDraft.widgets[widgetId] = JSON.parse(JSON.stringify(baselineWidget));
            }
          });
          changedTargets = [command.target.id, ...baselineSlot.widgetIds];
        }
      } else if (command.target.kind === "widget") {
        ensureWidgetReset(nextDraft, baseline, command.target.id);
        changedTargets = [command.target.id];
      }
      break;
    }
    case "draft.commit": {
      const committed = cloneSceneDocument(nextDraft) as MutableSceneDocument;
      committed.meta = {
        ...committed.meta,
        revision: committed.meta.revision + 1,
        lastCommittedAtIso: new Date().toISOString(),
      };
      adapter?.record(command, "commit", committed);
      return acceptedResult(command, committed, cloneSceneDocument(committed), cloneSceneDocument(committed), [committed.scene.id], "Draft committed to baseline.");
    }
    case "draft.discard": {
      const reset = cloneSceneDocument(baseline) as MutableSceneDocument;
      adapter?.record(command, "discard", reset);
      return acceptedResult(command, baseline, reset, cloneSceneDocument(reset), [baseline.scene.id], "Draft discarded and baseline restored.");
    }
    default:
      break;
  }
  const preview = cloneSceneDocument(nextDraft);
  const phase = command.scope === "preview-only" ? "preview" : "draft-update";
  adapter?.record(command, phase, preview);
  return acceptedResult(command, baseline, nextDraft, preview, changedTargets, `${command.type} applied through runtime-mutation-bridge.`);
}
