function syncMobileNavigation(widget, tabs, activeTab) {
  const mobile = widget.querySelector('.prisma-mobile-tab-nav');
  if (!mobile) return;

  const index = Math.max(0, tabs.indexOf(activeTab));
  const select = mobile.querySelector('select');
  const previous = mobile.querySelector('[data-mobile-previous]');
  const next = mobile.querySelector('[data-mobile-next]');
  const count = mobile.querySelector('[data-mobile-count]');

  if (select) select.value = String(index);
  if (previous) previous.disabled = index === 0;
  if (next) next.disabled = index === tabs.length - 1;
  if (count) count.textContent = `${String(index + 1).padStart(2, '0')} / ${String(tabs.length).padStart(2, '0')}`;
}

function activateTab(tab, tabs, panels, moveFocus = false) {
  const targetId = tab.getAttribute('aria-controls');
  const widget = tab.closest('[data-prisma-tabs], [data-prisma-stepper]');

  tabs.forEach((candidate) => {
    const selected = candidate === tab;
    candidate.setAttribute('aria-selected', String(selected));
    candidate.tabIndex = selected ? 0 : -1;
  });

  panels.forEach((panel) => {
    panel.hidden = panel.id !== targetId;
  });

  widget?.setAttribute('data-prisma-interacted', 'true');
  if (widget) syncMobileNavigation(widget, tabs, tab);
  if (moveFocus) tab.focus();

  tab.dispatchEvent(new CustomEvent('prisma:selection', {
    bubbles: true,
    detail: { value: tab.dataset.value ?? targetId }
  }));
}

function buildMobileNavigation(widget, tabs, panels) {
  if (widget.querySelector('.prisma-mobile-tab-nav')) return;

  const list = widget.querySelector('[role="tablist"]');
  if (!list) return;

  const navigation = document.createElement('div');
  navigation.className = 'prisma-mobile-tab-nav';
  navigation.setAttribute('aria-label', list.getAttribute('aria-label') || 'Navegación de opciones');

  const previous = document.createElement('button');
  previous.type = 'button';
  previous.dataset.mobilePrevious = '';
  previous.setAttribute('aria-label', 'Opción anterior');
  previous.textContent = '←';

  const label = document.createElement('label');
  label.className = 'prisma-mobile-tab-select';
  const hiddenLabel = document.createElement('span');
  hiddenLabel.className = 'prisma-sr-only';
  hiddenLabel.textContent = list.getAttribute('aria-label') || 'Seleccionar opción';
  const select = document.createElement('select');
  select.setAttribute('aria-label', hiddenLabel.textContent);

  tabs.forEach((tab, index) => {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = tab.textContent.trim();
    select.append(option);
  });

  label.append(hiddenLabel, select);

  const next = document.createElement('button');
  next.type = 'button';
  next.dataset.mobileNext = '';
  next.setAttribute('aria-label', 'Opción siguiente');
  next.textContent = '→';

  const count = document.createElement('span');
  count.dataset.mobileCount = '';
  count.className = 'prisma-mobile-tab-count';
  count.setAttribute('aria-live', 'polite');

  navigation.append(previous, label, next, count);
  list.insertAdjacentElement('afterend', navigation);

  const activeIndex = () => Math.max(0, tabs.findIndex((tab) => tab.getAttribute('aria-selected') === 'true'));

  previous.addEventListener('click', () => {
    const index = activeIndex();
    if (index > 0) activateTab(tabs[index - 1], tabs, panels);
  });

  next.addEventListener('click', () => {
    const index = activeIndex();
    if (index < tabs.length - 1) activateTab(tabs[index + 1], tabs, panels);
  });

  select.addEventListener('change', () => {
    const index = Number(select.value);
    if (tabs[index]) activateTab(tabs[index], tabs, panels);
  });
}

function initSelectable(root, selector) {
  root.querySelectorAll(selector).forEach((widget) => {
    if (widget.dataset.prismaReady === 'true') return;
    widget.dataset.prismaReady = 'true';

    const tabs = [...widget.querySelectorAll('[role="tab"]')];
    const panels = [...widget.querySelectorAll('[role="tabpanel"]')];
    if (!tabs.length || !panels.length) return;

    buildMobileNavigation(widget, tabs, panels);

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activateTab(tab, tabs, panels));
      tab.addEventListener('keydown', (event) => {
        let next = null;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next === null) return;
        event.preventDefault();
        activateTab(tabs[next], tabs, panels, true);
      });
    });

    const active = tabs.find((tab) => tab.getAttribute('aria-selected') === 'true') ?? tabs[0];
    activateTab(active, tabs, panels);
  });
}

function initSceneProgress(root) {
  const scenes = [...root.querySelectorAll('.prisma-scene')];
  const dots = [...root.querySelectorAll('.prisma-narrative-progress i')];
  if (!scenes.length || !dots.length || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;

    const index = scenes.indexOf(visible.target);
    dots.forEach((dot, position) => {
      if (position === index) dot.setAttribute('aria-current', 'step');
      else dot.removeAttribute('aria-current');
    });
  }, { threshold: [0.35, 0.6] });

  scenes.forEach((scene) => observer.observe(scene));
}

export function initPrismaNarrative(root = document) {
  initSelectable(root, '[data-prisma-tabs]');
  initSelectable(root, '[data-prisma-stepper]');
  initSceneProgress(root);
}
