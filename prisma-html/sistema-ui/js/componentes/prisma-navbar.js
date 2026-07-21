
export function initNavbar(root = document) {
  root.querySelectorAll('[data-prisma-nav-toggle]').forEach(button => {
    if (button.dataset.prismaNavReady) return;
    button.dataset.prismaNavReady = 'true';
    const target = document.getElementById(button.getAttribute('aria-controls'));
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') === 'true';
      button.setAttribute('aria-expanded', String(!open));
      if (target) target.hidden = open;
    });
  });
}
