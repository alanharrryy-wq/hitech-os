const body = document.body;
const select = document.getElementById('themeSelect');
const search = document.getElementById('catalogSearch');
const items = [...document.querySelectorAll('[data-catalog-item]')];
const filterButtons = [...document.querySelectorAll('[data-filter]')];
const densityButtons = [...document.querySelectorAll('[data-density]')];
const visibleCount = document.getElementById('visibleCount');
const toast = document.getElementById('catalogToast');
const progress = document.getElementById('scrollProgress');
let activeFilter = 'all';
let toastTimer = 0;

function showToast(message) {
  if (!toast) return;
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.hidden = false;
  toastTimer = window.setTimeout(() => { toast.hidden = true; }, 2200);
}

function applyFilters() {
  const query = search?.value.trim().toLocaleLowerCase('es') ?? '';
  let count = 0;
  items.forEach(item => {
    const haystack = `${item.textContent} ${item.dataset.tags ?? ''}`.toLocaleLowerCase('es');
    const categoryMatch = activeFilter === 'all' || item.dataset.category === activeFilter;
    const searchMatch = !query || haystack.includes(query);
    item.hidden = !(categoryMatch && searchMatch);
    if (!item.hidden) count += 1;
  });
  if (visibleCount) visibleCount.textContent = String(count);
}

select?.addEventListener('change', () => {
  body.dataset.prismaTheme = select.value;
  showToast(`Tema ${select.options[select.selectedIndex].text} activado`);
});

filterButtons.forEach(button => {
  button.addEventListener('click', () => {
    activeFilter = button.dataset.filter ?? 'all';
    filterButtons.forEach(candidate => candidate.setAttribute('aria-pressed', String(candidate === button)));
    applyFilters();
  });
});

search?.addEventListener('input', applyFilters);

densityButtons.forEach(button => {
  button.addEventListener('click', () => {
    body.dataset.catalogDensity = button.dataset.density;
    densityButtons.forEach(candidate => candidate.setAttribute('aria-pressed', String(candidate === button)));
  });
});

document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.target.closest('input,textarea,select,[contenteditable="true"]')) {
    event.preventDefault();
    search?.focus();
  }
  if (event.key === 'Escape' && document.activeElement === search) {
    search.value = '';
    search.blur();
    applyFilters();
  }
});

document.querySelectorAll('[data-copy-text]').forEach(button => {
  button.addEventListener('click', async () => {
    const text = button.dataset.copyText ?? '';
    try {
      await navigator.clipboard.writeText(text);
      showToast('Código copiado al portapapeles');
    } catch {
      showToast('No se pudo copiar automáticamente');
    }
  });
});

const lab = {
  alpha: document.getElementById('alphaRange'),
  blur: document.getElementById('blurRange'),
  radius: document.getElementById('radiusRange'),
  shine: document.getElementById('shineRange'),
  specimen: document.getElementById('glassSpecimen')
};

function updateLab() {
  if (!lab.specimen) return;
  const alpha = Number(lab.alpha?.value ?? 12);
  const blur = Number(lab.blur?.value ?? 30);
  const radius = Number(lab.radius?.value ?? 34);
  const shine = Number(lab.shine?.value ?? 50);
  lab.specimen.style.setProperty('--lab-alpha', String(alpha / 100));
  lab.specimen.style.setProperty('--lab-blur', `${blur}px`);
  lab.specimen.style.setProperty('--lab-radius', `${radius}px`);
  lab.specimen.style.setProperty('--lab-shine', String(shine / 100));
  document.getElementById('alphaValue').textContent = `${alpha}%`;
  document.getElementById('blurValue').textContent = `${blur}px`;
  document.getElementById('radiusValue').textContent = `${radius}px`;
  document.getElementById('shineValue').textContent = `${shine}%`;
}

[lab.alpha, lab.blur, lab.radius, lab.shine].forEach(control => control?.addEventListener('input', updateLab));

document.getElementById('resetLab')?.addEventListener('click', () => {
  lab.alpha.value = '12';
  lab.blur.value = '30';
  lab.radius.value = '34';
  lab.shine.value = '50';
  updateLab();
  showToast('Glass Lab restablecido');
});

document.querySelectorAll('.catalogo-segmented button').forEach(button => {
  button.addEventListener('click', () => {
    button.parentElement.querySelectorAll('button').forEach(candidate => candidate.setAttribute('aria-pressed', String(candidate === button)));
  });
});

document.getElementById('catalogDemoForm')?.addEventListener('submit', event => {
  event.preventDefault();
  if (event.currentTarget.checkValidity()) showToast('Configuración de demostración guardada');
});

function updateProgress() {
  if (!progress) return;
  const available = document.documentElement.scrollHeight - window.innerHeight;
  const value = available > 0 ? Math.min(100, (window.scrollY / available) * 100) : 0;
  progress.style.width = `${value}%`;
}

window.addEventListener('scroll', updateProgress, { passive: true });
body.dataset.catalogDensity = 'comfortable';
applyFilters();
updateLab();
updateProgress();
