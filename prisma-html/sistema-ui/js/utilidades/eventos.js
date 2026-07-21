
export function on(element, type, handler, options) {
  element?.addEventListener(type, handler, options);
  return () => element?.removeEventListener(type, handler, options);
}

export function emit(element, name, detail = {}) {
  return element?.dispatchEvent(new CustomEvent(name, { bubbles: true, detail })) ?? false;
}
