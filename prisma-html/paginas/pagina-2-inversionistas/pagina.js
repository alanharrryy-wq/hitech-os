const slides = [...document.querySelectorAll('.investor-slide')];
const previous = document.getElementById('prevSlide');
const next = document.getElementById('nextSlide');
const current = document.getElementById('currentSlide');
const progress = document.getElementById('investorProgress');
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
}

previous.addEventListener('click', () => showSlide(index - 1));
next.addEventListener('click', () => showSlide(index + 1));

document.addEventListener('keydown', (event) => {
  if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') showSlide(index + 1);
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') showSlide(index - 1);
  if (event.key === 'Home') showSlide(0);
  if (event.key === 'End') showSlide(slides.length - 1);
});

showSlide(0);
