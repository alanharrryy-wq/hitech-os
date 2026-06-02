(function () {
  "use strict";
  const BAD_SELECTORS = [
    "#prismo-visual-recipe-force-task2",
    "#prismoVisualRecipeForceTask2",
    'link[href*="prismo_visual_recipe_force_task2"]',
    'link[href*="prismo_visual_recipe_overlay_task2"]',
    'link[href*="prisma_cc_public_bundle_fix4.css"]'
  ];
  function removeForcedVisualRecipe() {
    BAD_SELECTORS.forEach((selector) => {
      document.querySelectorAll(selector).forEach((node) => node.remove());
    });
  }
  function applyLegacyFlags() {
    if (!document.body) return;
    document.body.removeAttribute("data-prismo-visual-recipe");
    document.body.dataset.prismoVisualPresets = "legacy-atmosphere-v76";
    document.body.classList.add("prisma-atmosphere-ready", "prisma-v56-active");
    const surface = document.getElementById("prismo-console");
    if (surface) {
      surface.dataset.prismoVisualBridge = "legacy-atmosphere-v76";
      if (!surface.querySelector(".prismo-atmosphere")) {
        const atmosphere = document.createElement("div");
        atmosphere.className = "prismo-atmosphere";
        atmosphere.setAttribute("aria-hidden", "true");
        surface.prepend(atmosphere);
      }
    }
  }
  function boot() { removeForcedVisualRecipe(); applyLegacyFlags(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });
  else boot();
  window.addEventListener("pageshow", boot);
})();
