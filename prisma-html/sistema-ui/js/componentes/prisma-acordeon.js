
export class PrismaAccordion extends HTMLElement {
  connectedCallback() {
    if (this.dataset.ready) return;
    this.dataset.ready = 'true';
    this.querySelectorAll('.prisma-accordion-trigger').forEach(trigger => {
      const panel = document.getElementById(trigger.getAttribute('aria-controls'));
      trigger.addEventListener('click', () => {
        const open = trigger.getAttribute('aria-expanded') === 'true';
        trigger.setAttribute('aria-expanded', String(!open));
        if (panel) panel.hidden = open;
      });
    });
  }
}

if (!customElements.get('prisma-accordion')) customElements.define('prisma-accordion', PrismaAccordion);
