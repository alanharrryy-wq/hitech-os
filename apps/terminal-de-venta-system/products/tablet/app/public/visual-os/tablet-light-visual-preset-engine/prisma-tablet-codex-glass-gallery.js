// PRISMA Tablet Codex Native Glass Gallery Demo
(function () {
  const cards = Array.from(document.querySelectorAll("[data-cg-card]"));
  const filters = Array.from(document.querySelectorAll("[data-filter]"));
  const search = document.querySelector("[data-search]");
  const detail = document.querySelector("[data-detail]");
  const toast = document.querySelector("[data-toast]");
  const reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const panelData = window.PRISMA_CODEX_GALLERY || [];

  function setToast(text) {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add("is-visible");
    window.clearTimeout(setToast._timer);
    setToast._timer = window.setTimeout(() => toast.classList.remove("is-visible"), 2500);
  }

  function applyFilter(group) {
    const query = (search?.value || "").toLowerCase().trim();
    cards.forEach((card) => {
      const matchGroup = group === "all" || card.dataset.group === group;
      const text = card.textContent.toLowerCase();
      const matchQuery = !query || text.includes(query);
      card.classList.toggle("is-hidden", !(matchGroup && matchQuery));
    });
  }

  filters.forEach((button) => {
    button.addEventListener("click", () => {
      filters.forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      applyFilter(button.dataset.filter);
      setToast(`Filtro activo: ${button.textContent.trim()}`);
    });
  });

  if (search) {
    search.addEventListener("input", () => {
      const active = document.querySelector("[data-filter].is-active");
      applyFilter(active?.dataset.filter || "all");
    });
  }

  document.addEventListener("click", (event) => {
    const open = event.target.closest("[data-open-detail]");
    if (!open) return;
    const id = open.getAttribute("data-open-detail");
    const found = panelData.find((p) => p.id === id);
    if (!found || !detail) return;

    detail.innerHTML = `
      <button class="cg-icon-button" data-close-detail style="float:right">×</button>
      <span class="cg-kicker">${found.group} · ${found.variant}</span>
      <h3>${found.title}</h3>
      <p>${found.desc}</p>
      <pre>${JSON.stringify({
        id: found.id,
        codex: found.codex,
        libraries: found.library,
        className: found.class
      }, null, 2)}</pre>
    `;
    detail.classList.add("is-open");
    setToast(`Detalle abierto: ${found.title}`);
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-close-detail]")) {
      detail?.classList.remove("is-open");
    }
  });

  if (!reduced) {
    cards.forEach((card) => {
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

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.animate(
          [
            { opacity: 0, transform: "translateY(16px) scale(.985)" },
            { opacity: 1, transform: "translateY(0) scale(1)" }
          ],
          { duration: 420, easing: "cubic-bezier(.2,.8,.2,1)", fill: "both" }
        );
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.1 });

    cards.forEach((card) => observer.observe(card));
  }

  const demoButton = document.querySelector("[data-run-demo]");
  demoButton?.addEventListener("click", () => {
    setToast("Demo motion: sheen, tilt, filters y drawer listos ✨");
    cards.slice(0, 10).forEach((card, index) => {
      card.animate(
        [
          { transform: "translateY(0) scale(1)" },
          { transform: "translateY(-10px) scale(1.012)" },
          { transform: "translateY(0) scale(1)" }
        ],
        { delay: index * 55, duration: 620, easing: "cubic-bezier(.2,.8,.2,1)" }
      );
    });
  });
})();