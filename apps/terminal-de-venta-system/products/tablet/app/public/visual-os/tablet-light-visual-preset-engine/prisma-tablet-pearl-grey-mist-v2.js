// PRISMA Tablet · Pearl Grey Mist v2
// Tiny motion helper. Pure JS, no dependencies.

(function () {
  const root = document.querySelector("[data-pgm-root]");
  const cards = document.querySelectorAll("[data-pgm-tilt]");
  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!root || reduced) return;

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  cards.forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      const px = (event.clientX - rect.left) / rect.width;
      const py = (event.clientY - rect.top) / rect.height;
      const rx = clamp((0.5 - py) * 3.5, -3.5, 3.5);
      const ry = clamp((px - 0.5) * 4.5, -4.5, 4.5);
      card.style.transform = `translateY(-3px) rotateX(${rx}deg) rotateY(${ry}deg)`;
    });

    card.addEventListener("pointerleave", () => {
      card.style.transform = "";
    });
  });

  let ticking = false;
  window.addEventListener("pointermove", (event) => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      const x = (event.clientX / window.innerWidth - 0.5) * 2;
      const y = (event.clientY / window.innerHeight - 0.5) * 2;
      root.style.setProperty("--pgm-pointer-x", x.toFixed(3));
      root.style.setProperty("--pgm-pointer-y", y.toFixed(3));
      ticking = false;
    });
  });
})();