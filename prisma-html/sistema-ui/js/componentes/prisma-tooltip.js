
export function initTooltips(root = document) {
  let tooltip = null;
  const hide = () => { tooltip?.remove(); tooltip = null; };
  root.querySelectorAll('[data-prisma-tooltip]').forEach(element => {
    if (element.dataset.prismaTooltipReady) return;
    element.dataset.prismaTooltipReady = 'true';
    const show = () => {
      hide();
      tooltip = document.createElement('div');
      tooltip.className = 'prisma-tooltip';
      tooltip.textContent = element.dataset.prismaTooltip;
      document.body.append(tooltip);
      const rect = element.getBoundingClientRect();
      tooltip.style.left = `${Math.max(8, rect.left)}px`;
      tooltip.style.top = `${Math.max(8, rect.bottom + 8)}px`;
    };
    element.addEventListener('mouseenter', show);
    element.addEventListener('focus', show);
    element.addEventListener('mouseleave', hide);
    element.addEventListener('blur', hide);
  });
}
