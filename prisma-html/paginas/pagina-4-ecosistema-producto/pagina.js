const surfaceButtons = [...document.querySelectorAll('[data-surface-select]')];

surfaceButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const tab = document.getElementById(button.dataset.surfaceSelect);
    tab?.click();
    document.getElementById('superficies')?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  });
});
