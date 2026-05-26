// PRISMA Tablet Codex Background Gallery
(function () {
  const lab = document.querySelector("[data-bg-lab]");
  const title = document.querySelector("[data-bg-title]");
  const desc = document.querySelector("[data-bg-desc]");
  const codex = document.querySelector("[data-bg-codex]");
  const adapter = document.querySelector("[data-bg-adapter]");
  const route = document.querySelector("[data-bg-route]");
  const toast = document.querySelector("[data-bg-toast]");
  const buttons = Array.from(document.querySelectorAll("[data-bg]"));
  const data = window.PRISMA_CODEX_BACKGROUNDS || [];

  if (!lab) return;

  function showToast(text) {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add("is-visible");
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => toast.classList.remove("is-visible"), 2200);
  }

  function applyBackground(className, id) {
    const found = data.find((item) => item.id === id || item.className === className);
    const allClasses = data.map((item) => item.className);
    lab.classList.remove(...allClasses);
    lab.classList.add(className);

    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.getAttribute("data-id") === id || button.getAttribute("data-bg") === className);
    });

    if (found) {
      title.textContent = found.title;
      desc.textContent = found.mood;
      codex.textContent = found.codexBase.join(" + ");
      adapter.textContent = found.adapter;
      route.textContent = found.recommendedFor.slice(0, 4).join(" · ");
      showToast(`Background aplicado: ${found.title}`);
    }
  }

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-bg]");
    if (!trigger) return;
    applyBackground(trigger.getAttribute("data-bg"), trigger.getAttribute("data-id"));
  });

  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduced) {
    document.querySelectorAll(".bg-preview-card, .bg-spec-card").forEach((card) => {
      card.addEventListener("pointermove", (event) => {
        const rect = card.getBoundingClientRect();
        const px = (event.clientX - rect.left) / rect.width;
        const py = (event.clientY - rect.top) / rect.height;
        const rx = (0.5 - py) * 4;
        const ry = (px - 0.5) * 5;
        card.style.transform = `translateY(-4px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
      });
      card.addEventListener("pointerleave", () => {
        card.style.transform = "";
      });
    });
  }
})();