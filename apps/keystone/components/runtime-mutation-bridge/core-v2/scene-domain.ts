import type { SceneLookModel, SceneLookModelPatch } from "../../live-scene-composer/scene-look-model";
import { mergeSceneLookModel } from "../../live-scene-composer/scene-look-model";

export type { SceneLookModel, SceneLookModelPatch };

export type AuthoringMode = "safe" | "advanced";
export type SelectionSurface = "canvas" | "structure" | "inspector" | "system";
export type TargetKind = "scene" | "layout-node" | "slot" | "widget" | "draft";
export type LayoutNodeKind = "root" | "stack" | "grid" | "container" | "slot-reference";
export type SlotKind = "content" | "metric" | "chart" | "media" | "container" | "custom";
export type WidgetType = "text" | "kpi" | "chart" | "image" | "container";
export type WidgetCapability = "textual" | "metric" | "chart" | "media" | "layout-container";
export type FeedbackLevel = "info" | "success" | "warning" | "error";

export type SceneId = string;
export type LayoutNodeId = string;
export type SlotId = string;
export type WidgetId = string;
export type PrefabId = string;

export interface FrameBox {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface WidgetStyle {
  readonly background: string;
  readonly foreground: string;
  readonly borderStyle: "none" | "solid" | "glass";
  readonly radius: number;
  readonly emphasis: "subtle" | "default" | "strong";
}

export type WidgetStylePatch = Partial<WidgetStyle>;
export type WidgetPropsPatch = Readonly<Record<string, unknown>>;

export interface SceneEntity {
  readonly id: SceneId;
  readonly title: string;
  readonly description: string;
  readonly look: SceneLookModel;
}

export interface LayoutNode {
  readonly id: LayoutNodeId;
  readonly title: string;
  readonly kind: LayoutNodeKind;
  readonly parentId: LayoutNodeId | null;
  readonly childIds: readonly LayoutNodeId[];
  readonly orderIndex: number;
  readonly slotId: SlotId | null;
  readonly frame: FrameBox;
  readonly locked: boolean;
}

export interface SlotEntity {
  readonly id: SlotId;
  readonly title: string;
  readonly kind: SlotKind;
  readonly acceptedWidgetTypes: readonly WidgetType[];
  readonly acceptedCapabilities: readonly WidgetCapability[];
  readonly widgetIds: readonly WidgetId[];
  readonly maxWidgets: number;
  readonly locked: boolean;
}

export interface WidgetEntity {
  readonly id: WidgetId;
  readonly title: string;
  readonly type: WidgetType;
  readonly slotId: SlotId;
  readonly prefabId: PrefabId | null;
  readonly capabilities: readonly WidgetCapability[];
  readonly props: Readonly<Record<string, unknown>>;
  readonly style: WidgetStyle;
  readonly visible: boolean;
  readonly locked: boolean;
}

export interface PrefabDefinition {
  readonly id: PrefabId;
  readonly title: string;
  readonly widgetType: WidgetType;
  readonly acceptedSlotKinds: readonly SlotKind[];
  readonly acceptedCapabilities: readonly WidgetCapability[];
  readonly defaultProps: Readonly<Record<string, unknown>>;
  readonly defaultStyle: WidgetStyle;
  readonly description: string;
  readonly tags: readonly string[];
}

export interface DocumentMeta {
  readonly revision: number;
  readonly nextId: number;
  readonly lastCommittedAtIso: string | null;
}

export interface SceneDocument {
  readonly scene: SceneEntity;
  readonly rootLayoutId: LayoutNodeId;
  readonly layoutNodes: Readonly<Record<LayoutNodeId, LayoutNode>>;
  readonly slots: Readonly<Record<SlotId, SlotEntity>>;
  readonly widgets: Readonly<Record<WidgetId, WidgetEntity>>;
  readonly meta: DocumentMeta;
}

export interface SelectionTarget {
  readonly kind: Exclude<TargetKind, "draft">;
  readonly id: string;
  readonly sceneId: SceneId;
}

export interface SelectionState {
  readonly primaryTarget: SelectionTarget | null;
  readonly sourceSurface: SelectionSurface;
  readonly mode: AuthoringMode;
  readonly lastUpdatedAtIso: string;
}

export interface RuntimeObservedBounds {
  readonly targetKind: Exclude<TargetKind, "draft">;
  readonly targetId: string;
  readonly frame: FrameBox;
}

export interface RuntimeObservationSnapshot {
  readonly sceneId: SceneId;
  readonly bounds: readonly RuntimeObservedBounds[];
  readonly measuredAtIso: string;
}

export interface MutationFeedback {
  readonly commandType: string;
  readonly level: FeedbackLevel;
  readonly message: string;
  readonly code: string;
  readonly changedTargets: readonly string[];
  readonly recordedAtIso: string;
}

export interface CanvasBox {
  readonly id: string;
  readonly kind: "layout-node" | "slot" | "widget";
  readonly title: string;
  readonly frame: FrameBox;
  readonly selected: boolean;
  readonly slotId: string | null;
  readonly widgetIds: readonly string[];
}

export interface StructureTreeEntry {
  readonly id: string;
  readonly kind: "scene" | "layout-node" | "slot" | "widget";
  readonly title: string;
  readonly depth: number;
  readonly parentId: string | null;
  readonly selectionTarget: SelectionTarget;
  readonly childIds: readonly string[];
}

export interface DocumentMutationEffect {
  readonly document: SceneDocument;
  readonly changedTargets: readonly string[];
}

export type PrefabCompatibilityIssue = "slot-kind" | "widget-type" | "capability" | "capacity";

function deepClone<T>(value: T): T {
  if (typeof globalThis.structuredClone === "function") {
    return globalThis.structuredClone(value);
  }
  return JSON.parse(JSON.stringify(value)) as T;
}

export function cloneSceneDocument(document: SceneDocument): SceneDocument {
  return deepClone(document);
}

export function createSelectionState(sceneId: SceneId, mode: AuthoringMode = "safe"): SelectionState {
  return {
    primaryTarget: {
      kind: "scene",
      id: sceneId,
      sceneId,
    },
    sourceSurface: "system",
    mode,
    lastUpdatedAtIso: new Date().toISOString(),
  };
}

export function setSelection(
  previous: SelectionState,
  target: SelectionTarget | null,
  sourceSurface: SelectionSurface,
  mode: AuthoringMode = previous.mode
): SelectionState {
  return {
    primaryTarget: target,
    sourceSurface,
    mode,
    lastUpdatedAtIso: new Date().toISOString(),
  };
}

export function selectionExistsInDocument(document: SceneDocument, selection: SelectionTarget | null): boolean {
  if (!selection) {
    return false;
  }
  switch (selection.kind) {
    case "scene":
      return selection.id === document.scene.id;
    case "layout-node":
      return Boolean(document.layoutNodes[selection.id]);
    case "slot":
      return Boolean(document.slots[selection.id]);
    case "widget":
      return Boolean(document.widgets[selection.id]);
    default:
      return false;
  }
}

export function reconcileSelectionState(document: SceneDocument, selection: SelectionState): SelectionState {
  if (selectionExistsInDocument(document, selection.primaryTarget)) {
    return selection;
  }
  return createSelectionState(document.scene.id, selection.mode);
}

export function isDraftDirty(baseline: SceneDocument, draft: SceneDocument): boolean {
  return JSON.stringify(baseline) !== JSON.stringify(draft);
}

export function getLayoutNode(document: SceneDocument, layoutNodeId: LayoutNodeId): LayoutNode | null {
  return document.layoutNodes[layoutNodeId] ?? null;
}

export function getSlot(document: SceneDocument, slotId: SlotId): SlotEntity | null {
  return document.slots[slotId] ?? null;
}

export function getWidget(document: SceneDocument, widgetId: WidgetId): WidgetEntity | null {
  return document.widgets[widgetId] ?? null;
}

export function getWidgetsForSlot(document: SceneDocument, slotId: SlotId): readonly WidgetEntity[] {
  const slot = document.slots[slotId];
  if (!slot) {
    return [];
  }
  return slot.widgetIds
    .map((widgetId) => document.widgets[widgetId])
    .filter((widget): widget is WidgetEntity => Boolean(widget));
}

export function getPrefabCompatibilityIssues(slot: SlotEntity, prefab: PrefabDefinition): readonly PrefabCompatibilityIssue[] {
  const issues: PrefabCompatibilityIssue[] = [];
  if (!prefab.acceptedSlotKinds.includes(slot.kind)) {
    issues.push("slot-kind");
  }
  if (slot.acceptedWidgetTypes.length > 0 && !slot.acceptedWidgetTypes.includes(prefab.widgetType)) {
    issues.push("widget-type");
  }
  if (!prefab.acceptedCapabilities.some((capability) => slot.acceptedCapabilities.includes(capability))) {
    issues.push("capability");
  }
  if (slot.widgetIds.length >= slot.maxWidgets) {
    issues.push("capacity");
  }
  return issues;
}

export function createWidgetFromPrefab(prefab: PrefabDefinition, slotId: SlotId, nextId: number): WidgetEntity {
  const widgetId = `widget-${nextId}`;
  return {
    id: widgetId,
    title: prefab.title,
    type: prefab.widgetType,
    slotId,
    prefabId: prefab.id,
    capabilities: [...prefab.acceptedCapabilities],
    props: { ...prefab.defaultProps },
    style: { ...prefab.defaultStyle },
    visible: true,
    locked: false,
  };
}

export function coerceWidgetStylePatch(previous: WidgetStyle, patch: WidgetStylePatch): WidgetStyle {
  return {
    background: patch.background ?? previous.background,
    foreground: patch.foreground ?? previous.foreground,
    borderStyle: patch.borderStyle ?? previous.borderStyle,
    radius: typeof patch.radius === "number" ? patch.radius : previous.radius,
    emphasis: patch.emphasis ?? previous.emphasis,
  };
}

export function applySceneLookPatch(document: SceneDocument, patch: SceneLookModelPatch): DocumentMutationEffect {
  return {
    document: {
      ...document,
      scene: {
        ...document.scene,
        look: mergeSceneLookModel(document.scene.look, patch),
      },
    },
    changedTargets: [document.scene.id],
  };
}

export function moveLayoutNode(document: SceneDocument, layoutNodeId: LayoutNodeId, deltaX: number, deltaY: number): DocumentMutationEffect {
  const node = document.layoutNodes[layoutNodeId];
  if (!node) {
    return { document, changedTargets: [] };
  }
  return {
    document: {
      ...document,
      layoutNodes: {
        ...document.layoutNodes,
        [layoutNodeId]: {
          ...node,
          frame: {
            ...node.frame,
            x: node.frame.x + deltaX,
            y: node.frame.y + deltaY,
          },
        },
      },
    },
    changedTargets: [layoutNodeId],
  };
}

export function resizeLayoutNode(
  document: SceneDocument,
  layoutNodeId: LayoutNodeId,
  widthDelta: number,
  heightDelta: number
): DocumentMutationEffect {
  const node = document.layoutNodes[layoutNodeId];
  if (!node) {
    return { document, changedTargets: [] };
  }
  return {
    document: {
      ...document,
      layoutNodes: {
        ...document.layoutNodes,
        [layoutNodeId]: {
          ...node,
          frame: {
            ...node.frame,
            width: Math.max(48, node.frame.width + widthDelta),
            height: Math.max(32, node.frame.height + heightDelta),
          },
        },
      },
    },
    changedTargets: [layoutNodeId],
  };
}

export function reorderLayoutNode(document: SceneDocument, layoutNodeId: LayoutNodeId, toIndex: number): DocumentMutationEffect {
  const node = document.layoutNodes[layoutNodeId];
  if (!node || !node.parentId) {
    return { document, changedTargets: [] };
  }
  const parent = document.layoutNodes[node.parentId];
  if (!parent) {
    return { document, changedTargets: [] };
  }
  const childIds = parent.childIds.filter((childId) => childId !== layoutNodeId);
  childIds.splice(toIndex, 0, layoutNodeId);
  const layoutNodes: Record<LayoutNodeId, LayoutNode> = {
    ...document.layoutNodes,
    [parent.id]: {
      ...parent,
      childIds,
    },
  };
  childIds.forEach((childId, index) => {
    const child = document.layoutNodes[childId];
    if (child) {
      layoutNodes[childId] = {
        ...child,
        orderIndex: index,
      };
    }
  });
  return {
    document: {
      ...document,
      layoutNodes,
    },
    changedTargets: [parent.id, layoutNodeId],
  };
}

export function insertWidgetFromPrefab(document: SceneDocument, slotId: SlotId, prefab: PrefabDefinition): DocumentMutationEffect {
  const slot = document.slots[slotId];
  if (!slot) {
    return { document, changedTargets: [] };
  }
  const widget = createWidgetFromPrefab(prefab, slotId, document.meta.nextId);
  return {
    document: {
      ...document,
      slots: {
        ...document.slots,
        [slotId]: {
          ...slot,
          widgetIds: [...slot.widgetIds, widget.id],
        },
      },
      widgets: {
        ...document.widgets,
        [widget.id]: widget,
      },
      meta: {
        ...document.meta,
        nextId: document.meta.nextId + 1,
      },
    },
    changedTargets: [slotId, widget.id],
  };
}

export function updateWidgetProps(document: SceneDocument, widgetId: WidgetId, patch: WidgetPropsPatch): DocumentMutationEffect {
  const widget = document.widgets[widgetId];
  if (!widget) {
    return { document, changedTargets: [] };
  }
  return {
    document: {
      ...document,
      widgets: {
        ...document.widgets,
        [widgetId]: {
          ...widget,
          props: {
            ...widget.props,
            ...patch,
          },
        },
      },
    },
    changedTargets: [widgetId],
  };
}

export function updateWidgetStyle(document: SceneDocument, widgetId: WidgetId, patch: WidgetStylePatch): DocumentMutationEffect {
  const widget = document.widgets[widgetId];
  if (!widget) {
    return { document, changedTargets: [] };
  }
  return {
    document: {
      ...document,
      widgets: {
        ...document.widgets,
        [widgetId]: {
          ...widget,
          style: coerceWidgetStylePatch(widget.style, patch),
        },
      },
    },
    changedTargets: [widgetId],
  };
}

export function removeWidget(document: SceneDocument, widgetId: WidgetId): DocumentMutationEffect {
  const widget = document.widgets[widgetId];
  if (!widget) {
    return { document, changedTargets: [] };
  }
  const remainingWidgets = { ...document.widgets };
  delete remainingWidgets[widgetId];
  const slot = document.slots[widget.slotId];
  return {
    document: {
      ...document,
      slots: slot
        ? {
            ...document.slots,
            [widget.slotId]: {
              ...slot,
              widgetIds: slot.widgetIds.filter((candidate) => candidate !== widgetId),
            },
          }
        : document.slots,
      widgets: remainingWidgets,
    },
    changedTargets: [widgetId],
  };
}

export function resetTargetFromBaseline(
  draft: SceneDocument,
  baseline: SceneDocument,
  target: SelectionTarget
): DocumentMutationEffect {
  if (target.kind === "scene") {
    return {
      document: {
        ...draft,
        scene: deepClone(baseline.scene),
      },
      changedTargets: [baseline.scene.id],
    };
  }

  if (target.kind === "layout-node") {
    const baselineNode = baseline.layoutNodes[target.id];
    if (!baselineNode) {
      return { document: draft, changedTargets: [] };
    }
    return {
      document: {
        ...draft,
        layoutNodes: {
          ...draft.layoutNodes,
          [target.id]: deepClone(baselineNode),
        },
      },
      changedTargets: [target.id],
    };
  }

  if (target.kind === "slot") {
    const baselineSlot = baseline.slots[target.id];
    if (!baselineSlot) {
      return { document: draft, changedTargets: [] };
    }

    const widgets: Record<WidgetId, WidgetEntity> = { ...draft.widgets };
    const currentSlot = draft.slots[target.id];
    if (currentSlot) {
      currentSlot.widgetIds.forEach((widgetId) => {
        if (!baselineSlot.widgetIds.includes(widgetId)) {
          delete widgets[widgetId];
        }
      });
    }
    baselineSlot.widgetIds.forEach((widgetId) => {
      const baselineWidget = baseline.widgets[widgetId];
      if (baselineWidget) {
        widgets[widgetId] = deepClone(baselineWidget);
      }
    });

    return {
      document: {
        ...draft,
        slots: {
          ...draft.slots,
          [target.id]: deepClone(baselineSlot),
        },
        widgets,
      },
      changedTargets: [target.id, ...baselineSlot.widgetIds],
    };
  }

  const baselineWidget = baseline.widgets[target.id];
  const currentWidget = draft.widgets[target.id];
  if (baselineWidget) {
    const slotId = baselineWidget.slotId;
    const baselineSlot = baseline.slots[slotId];
    const widgets = {
      ...draft.widgets,
      [target.id]: deepClone(baselineWidget),
    };
    const slots = baselineSlot
      ? {
          ...draft.slots,
          [slotId]: deepClone(baselineSlot),
        }
      : draft.slots;

    if (baselineSlot) {
      baselineSlot.widgetIds.forEach((widgetId) => {
        const widget = baseline.widgets[widgetId];
        if (widget) {
          widgets[widgetId] = deepClone(widget);
        }
      });
    }

    return {
      document: {
        ...draft,
        slots,
        widgets,
      },
      changedTargets: [target.id],
    };
  }

  if (!currentWidget) {
    return { document: draft, changedTargets: [] };
  }

  const slot = draft.slots[currentWidget.slotId];
  const remainingWidgets = { ...draft.widgets };
  delete remainingWidgets[target.id];
  return {
    document: {
      ...draft,
      slots: slot
        ? {
            ...draft.slots,
            [currentWidget.slotId]: {
              ...slot,
              widgetIds: slot.widgetIds.filter((widgetId) => widgetId !== target.id),
            },
          }
        : draft.slots,
      widgets: remainingWidgets,
    },
    changedTargets: [target.id],
  };
}

export function commitDraftDocument(document: SceneDocument, committedAtIso: string = new Date().toISOString()): SceneDocument {
  return {
    ...cloneSceneDocument(document),
    meta: {
      ...document.meta,
      revision: document.meta.revision + 1,
      lastCommittedAtIso: committedAtIso,
    },
  };
}

export function discardDraftToBaseline(baseline: SceneDocument): SceneDocument {
  return cloneSceneDocument(baseline);
}

export function listStructureEntries(document: SceneDocument): readonly StructureTreeEntry[] {
  const entries: StructureTreeEntry[] = [];
  const visitLayout = (layoutNodeId: LayoutNodeId, depth: number, parentId: string | null): void => {
    const layoutNode = document.layoutNodes[layoutNodeId];
    if (!layoutNode) {
      return;
    }
    entries.push({
      id: layoutNode.id,
      kind: "layout-node",
      title: layoutNode.title,
      depth,
      parentId,
      selectionTarget: { kind: "layout-node", id: layoutNode.id, sceneId: document.scene.id },
      childIds: [...layoutNode.childIds, ...(layoutNode.slotId ? [layoutNode.slotId] : [])],
    });
    if (layoutNode.slotId) {
      const slot = document.slots[layoutNode.slotId];
      if (slot) {
        entries.push({
          id: slot.id,
          kind: "slot",
          title: slot.title,
          depth: depth + 1,
          parentId: layoutNode.id,
          selectionTarget: { kind: "slot", id: slot.id, sceneId: document.scene.id },
          childIds: [...slot.widgetIds],
        });
        slot.widgetIds.forEach((widgetId) => {
          const widget = document.widgets[widgetId];
          if (widget) {
            entries.push({
              id: widget.id,
              kind: "widget",
              title: widget.title,
              depth: depth + 2,
              parentId: slot.id,
              selectionTarget: { kind: "widget", id: widget.id, sceneId: document.scene.id },
              childIds: [],
            });
          }
        });
      }
    }
    layoutNode.childIds.forEach((childId) => visitLayout(childId, depth + 1, layoutNode.id));
  };

  entries.push({
    id: document.scene.id,
    kind: "scene",
    title: document.scene.title,
    depth: 0,
    parentId: null,
    selectionTarget: { kind: "scene", id: document.scene.id, sceneId: document.scene.id },
    childIds: [document.rootLayoutId],
  });
  visitLayout(document.rootLayoutId, 1, document.scene.id);
  return entries;
}

export function buildCanvasBoxes(document: SceneDocument, selection: SelectionTarget | null): readonly CanvasBox[] {
  const boxes: CanvasBox[] = [];
  Object.values(document.layoutNodes).forEach((layoutNode) => {
    boxes.push({
      id: layoutNode.id,
      kind: "layout-node",
      title: layoutNode.title,
      frame: layoutNode.frame,
      selected: selection?.kind === "layout-node" && selection.id === layoutNode.id,
      slotId: layoutNode.slotId,
      widgetIds: layoutNode.slotId ? [...(document.slots[layoutNode.slotId]?.widgetIds ?? [])] : [],
    });

    if (!layoutNode.slotId) {
      return;
    }

    const slot = document.slots[layoutNode.slotId];
    if (!slot) {
      return;
    }

    boxes.push({
      id: slot.id,
      kind: "slot",
      title: slot.title,
      frame: layoutNode.frame,
      selected: selection?.kind === "slot" && selection.id === slot.id,
      slotId: slot.id,
      widgetIds: [...slot.widgetIds],
    });

    getWidgetsForSlot(document, slot.id).forEach((widget, index) => {
      boxes.push({
        id: widget.id,
        kind: "widget",
        title: widget.title,
        frame: {
          x: layoutNode.frame.x + 8,
          y: layoutNode.frame.y + 8 + index * 56,
          width: Math.max(layoutNode.frame.width - 16, 40),
          height: 48,
        },
        selected: selection?.kind === "widget" && selection.id === widget.id,
        slotId: slot.id,
        widgetIds: [widget.id],
      });
    });
  });
  return boxes;
}

export function createRuntimeObservationSnapshot(document: SceneDocument, selection: SelectionTarget | null): RuntimeObservationSnapshot {
  return {
    sceneId: document.scene.id,
    bounds: buildCanvasBoxes(document, selection).map((box) => ({
      targetKind: box.kind,
      targetId: box.id,
      frame: box.frame,
    })),
    measuredAtIso: new Date().toISOString(),
  };
}

export function getObservedBounds(snapshot: RuntimeObservationSnapshot, target: SelectionTarget | null): RuntimeObservedBounds | null {
  if (!target) {
    return null;
  }
  return snapshot.bounds.find((item) => item.targetKind === target.kind && item.targetId === target.id) ?? null;
}
