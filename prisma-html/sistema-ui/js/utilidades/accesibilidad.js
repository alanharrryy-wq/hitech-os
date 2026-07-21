
const FOCUSABLE = 'button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])';

export function focusFirst(root) {
  root?.querySelector(FOCUSABLE)?.focus();
}

export function isTypingTarget(element) {
  return Boolean(element?.closest('input,textarea,select,[contenteditable="true"]'));
}

export function trapFocus(event, root) {
  if (event.key !== 'Tab' || !root) return;
  const nodes = [...root.querySelectorAll(FOCUSABLE)].filter(node => !node.disabled && !node.hidden);
  if (!nodes.length) return;
  const first = nodes[0];
  const last = nodes[nodes.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}
