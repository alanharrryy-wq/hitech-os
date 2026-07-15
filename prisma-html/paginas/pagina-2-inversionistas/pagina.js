const slides = [...document.querySelectorAll('.investor-slide')];
const previous = document.getElementById('prevSlide');
const next = document.getElementById('nextSlide');
const current = document.getElementById('currentSlide');
const progress = document.getElementById('investorProgress');
const chaptersButton = document.getElementById('chaptersButton');
const chaptersMenu = document.getElementById('chaptersMenu');
let index = 0;

function showSlide(nextIndex) {
  index = Math.max(0, Math.min(slides.length - 1, nextIndex));
  slides.forEach((slide, position) => {
    const active = position === index;
    slide.classList.toggle('is-active', active);
    slide.setAttribute('aria-hidden', String(!active));
  });
  current.textContent = String(index + 1).padStart(2, '0');
  progress.style.width = `${((index + 1) / slides.length) * 100}%`;
  previous.disabled = index === 0;
  next.disabled = index === slides.length - 1;
  chaptersMenu.hidden = true;
  chaptersButton.setAttribute('aria-expanded', 'false');
}

previous.addEventListener('click', () => showSlide(index - 1));
next.addEventListener('click', () => showSlide(index + 1));
chaptersButton.addEventListener('click', () => {
  const open = chaptersMenu.hidden;
  chaptersMenu.hidden = !open;
  chaptersButton.setAttribute('aria-expanded', String(open));
});

document.querySelectorAll('[data-goto]').forEach((button) => {
  button.addEventListener('click', () => showSlide(Number(button.dataset.goto)));
});

document.addEventListener('keydown', (event) => {
  if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') showSlide(index + 1);
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') showSlide(index - 1);
  if (event.key === 'Escape') {
    chaptersMenu.hidden = true;
    chaptersButton.setAttribute('aria-expanded', 'false');
  }
});

showSlide(0);
