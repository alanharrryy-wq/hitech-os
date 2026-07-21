
import './componentes/prisma-modal.js';
import './componentes/prisma-tabs.js';
import './componentes/prisma-acordeon.js';
import { initNavbar } from './componentes/prisma-navbar.js';
import { initTooltips } from './componentes/prisma-tooltip.js';
import { initMenu } from './comportamientos/menu.js';
import { initScroll } from './comportamientos/scroll.js';
import { initNavigation } from './comportamientos/navegacion.js';
import { initForms } from './comportamientos/formularios.js';
import { initPrismaNarrative } from './componentes/prisma-narrative.js';

export function initPrismaUI(root = document) {
  initNavbar(root);
  initTooltips(root);
  initMenu(root);
  initScroll(root);
  initNavigation(root);
  initForms(root);
  initPrismaNarrative(root);
  document.documentElement.dataset.prismaUiReady = 'true';
  document.dispatchEvent(new CustomEvent('prisma-ui:ready'));
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => initPrismaUI(), { once: true });
} else {
  initPrismaUI();
}
