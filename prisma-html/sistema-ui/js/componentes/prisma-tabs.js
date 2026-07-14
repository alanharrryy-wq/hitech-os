
export class PrismaTabs extends HTMLElement {
  connectedCallback() {
    if (this.dataset.ready) return;
    this.dataset.ready = 'true';
    this.tabs = [...this.querySelectorAll('[role="tab"]')];
    this.panels = [...this.querySelectorAll('[role="tabpanel"]')];
    this.tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => this.select(index));
      tab.addEventListener('keydown', event => this.handleKeydown(event, index));
    });
    const selected = Math.max(0, this.tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true'));
    this.select(selected);
  }

  handleKeydown(event, index) {
    if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index + (event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0);
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = this.tabs.length - 1;
    next = (next + this.tabs.length) % this.tabs.length;
    this.select(next);
    this.tabs[next].focus();
  }

  select(index) {
    this.tabs.forEach((tab, position) => {
      const selected = position === index;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    this.panels.forEach((panel, position) => { panel.hidden = position !== index; });
  }
}

if (!customElements.get('prisma-tabs')) customElements.define('prisma-tabs', PrismaTabs);
