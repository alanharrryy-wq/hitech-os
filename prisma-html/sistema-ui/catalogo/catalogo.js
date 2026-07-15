const themeSelect = document.getElementById('themeSelect');
const atmosphereSelect = document.getElementById('atmosphereSelect');
const alphaRange = document.getElementById('alphaRange');
const blurRange = document.getElementById('blurRange');
const alphaOutput = document.getElementById('alphaOutput');
const blurOutput = document.getElementById('blurOutput');
const lab = document.getElementById('catalogLab');
const surface = lab?.querySelector('.catalog-lab-surface');
const readout = document.getElementById('labReadout');

function renderLab() {
  const alpha = Number(alphaRange.value);
  const blur = Number(blurRange.value);
  const atmosphere = atmosphereSelect.value;
  lab.dataset.atmosphere = atmosphere;
  surface.style.setProperty('--lab-alpha', String(alpha / 100));
  surface.style.setProperty('--lab-blur', `${blur}px`);
  alphaOutput.value = String(alpha);
  blurOutput.value = String(blur);
  readout.textContent = `${atmosphere === 'liquid' ? 'Liquid' : 'Aurora'} · alpha ${alpha} · blur ${blur}`;
}

themeSelect.addEventListener('change', () => { document.body.dataset.prismaTheme = themeSelect.value; });
atmosphereSelect.addEventListener('change', renderLab);
alphaRange.addEventListener('input', renderLab);
blurRange.addEventListener('input', renderLab);
renderLab();
