
export function initNavigation(root = document) {
  root.querySelectorAll('[aria-current="page"]').forEach(node => node.setAttribute('aria-current', 'page'));
}
