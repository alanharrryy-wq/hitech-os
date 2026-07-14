
export const one = (selector, root = document) => root.querySelector(selector);
export const all = (selector, root = document) => [...root.querySelectorAll(selector)];
export const closest = (element, selector) => element?.closest(selector) ?? null;
export const setHidden = (element, hidden) => { if (element) element.hidden = Boolean(hidden); };
