
import { isTypingTarget } from '../../sistema-ui/js/utilidades/accesibilidad.js';

const slides = [...document.querySelectorAll('.slide')];
const dots = [...document.querySelectorAll('.dot')];
const progress = document.getElementById('progress');
const current = document.getElementById('current');
const notes = document.getElementById('notesPanel');
const notesButton = document.getElementById('notesBtn');
const previous = document.getElementById('prevBtn');
const nextButton = document.getElementById('nextBtn');
let index = 0;

function go(next) {
  index = Math.max(0, Math.min(slides.length - 1, next));
  slides.forEach((slide, position) => {
    const active = position === index;
    slide.classList.toggle('active', active);
    slide.setAttribute('aria-hidden', String(!active));
  });
  dots.forEach((dot, position) => {
    const active = position === index;
    dot.classList.toggle('active', active);
    dot.setAttribute('aria-current', active ? 'step' : 'false');
  });
  if (progress) progress.style.width = `${((index + 1) / slides.length) * 100}%`;
  if (current) current.textContent = String(index + 1).padStart(2, '0');
  if (previous) previous.disabled = index === 0;
  if (nextButton) nextButton.disabled = index === slides.length - 1;
  history.replaceState(null, '', `#slide-${String(index + 1).padStart(2, '0')}`);
}

function toggleNotes(force) {
  if (!notes) return;
  const open = typeof force === 'boolean' ? force : !notes.classList.contains('open');
  notes.classList.toggle('open', open);
  notes.setAttribute('aria-hidden', String(!open));
  notesButton?.setAttribute('aria-expanded', String(open));
  if (open) notes.querySelector('h2')?.focus?.();
}

document.querySelectorAll('[data-goto]').forEach(button => {
  button.addEventListener('click', () => go(Number(button.dataset.goto)));
});
dots.forEach(dot => dot.addEventListener('click', () => go(Number(dot.dataset.goto))));
previous?.addEventListener('click', () => go(index - 1));
nextButton?.addEventListener('click', () => go(index + 1));
notesButton?.addEventListener('click', () => toggleNotes());
document.getElementById('printBtn')?.addEventListener('click', () => window.print());

window.addEventListener('keydown', event => {
  if (isTypingTarget(event.target)) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown' || event.key === ' ') {
    event.preventDefault();
    go(index + 1);
  }
  if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
    event.preventDefault();
    go(index - 1);
  }
  if (event.key.toLowerCase() === 'n') toggleNotes();
  if (event.key === 'Escape') toggleNotes(false);
});

const match = location.hash.match(/slide-(\d+)/);
go(match ? Number(match[1]) - 1 : 0);
toggleNotes(false);
