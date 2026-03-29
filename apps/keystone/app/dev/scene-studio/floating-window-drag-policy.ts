export const FLOATING_WINDOW_DRAG_HANDLE_ATTR = "data-floating-window-drag-handle";
export const FLOATING_WINDOW_NO_DRAG_ATTR = "data-floating-window-no-drag";

export type FloatingWindowDragNode = {
  tagName?: string | null;
  role?: string | null;
  dragHandle?: boolean;
  noDrag?: boolean;
  contentEditable?: boolean;
  draggable?: boolean;
};

const INTERACTIVE_TAGS = new Set(["button", "input", "select", "textarea", "option", "label", "summary", "details", "a"]);
const INTERACTIVE_ROLES = new Set([
  "button",
  "link",
  "menuitem",
  "option",
  "checkbox",
  "radio",
  "switch",
  "tab",
  "slider",
  "textbox",
  "combobox",
  "spinbutton"
]);

function normalizeTagName(tagName: string | null | undefined): string {
  return (tagName ?? "").toLowerCase();
}

function normalizeRole(role: string | null | undefined): string {
  return (role ?? "").toLowerCase();
}

export function isFloatingWindowInteractiveNode(node: FloatingWindowDragNode): boolean {
  const tagName = normalizeTagName(node.tagName);
  if (INTERACTIVE_TAGS.has(tagName)) {
    return true;
  }

  const role = normalizeRole(node.role);
  if (INTERACTIVE_ROLES.has(role)) {
    return true;
  }

  if (node.contentEditable) {
    return true;
  }

  if (node.draggable) {
    return true;
  }

  return false;
}

export function canStartFloatingWindowDrag(path: readonly FloatingWindowDragNode[]): boolean {
  let hasDragHandle = false;

  for (const node of path) {
    if (node.noDrag) {
      return false;
    }

    if (isFloatingWindowInteractiveNode(node)) {
      return false;
    }

    if (node.dragHandle) {
      hasDragHandle = true;
    }
  }

  return hasDragHandle;
}

export function buildFloatingWindowDragPath(
  target: EventTarget | null,
  root: HTMLElement | null
): FloatingWindowDragNode[] {
  if (!root || !(target instanceof Element)) {
    return [];
  }

  if (target !== root && !root.contains(target)) {
    return [];
  }

  const path: FloatingWindowDragNode[] = [];
  let current: Element | null = target;

  while (current) {
    const htmlElement = current instanceof HTMLElement ? current : null;

    path.push({
      tagName: current.tagName,
      role: current.getAttribute("role"),
      dragHandle: current.getAttribute(FLOATING_WINDOW_DRAG_HANDLE_ATTR) === "true",
      noDrag: current.getAttribute(FLOATING_WINDOW_NO_DRAG_ATTR) === "true",
      contentEditable: htmlElement?.isContentEditable ?? false,
      draggable: htmlElement?.draggable ?? false
    });

    if (current === root) {
      return path;
    }

    current = current.parentElement;
  }

  return [];
}
