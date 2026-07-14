
import { focusFirst, trapFocus } from '../utilidades/accesibilidad.js';

export class PrismaModal extends HTMLElement {
  connectedCallback() {
    if (this.dataset.ready) return;
    this.dataset.ready = 'true';
    this.hidden = true;
    this.setAttribute('role', 'dialog');
    this.setAttribute('aria-modal', 'true');
    this.addEventListener('click', event => {
      if (event.target === this || event.target.closest('[data-prisma-modal-close]')) this.close();
    });
    this.addEventListener('keydown', event => {
      if (event.key === 'Escape') this.close();
      trapFocus(event, this);
    });
    document.querySelectorAll(`[data-prisma-modal-open="${this.id}"]`).forEach(button => {
      button.addEventListener('click', () => this.open(button));
    });
  }

  open(trigger) {
    this.trigger = trigger;
    this.hidden = false;
    this.classList.add('prisma-modal-backdrop');
    focusFirst(this);
  }

  close() {
    this.hidden = true;
    this.classList.remove('prisma-modal-backdrop');
    this.trigger?.focus();
  }
}

if (!customElements.get('prisma-modal')) customElements.define('prisma-modal', PrismaModal);
