(async function(){
  const summary = document.getElementById("mcJsonSummary");
  const stats = document.getElementById("mcStats");
  function count(obj, keys){for (const key of keys){const value = obj && obj[key]; if (Array.isArray(value)) return value.length; if (value && typeof value === "object") return Object.keys(value).length;} return "n/a";}
  function card(label, value, text){return `<article class="mc-card mc-double"><span>${label}</span><strong style="display:block;font-size:42px;line-height:1">${value}</strong><p>${text}</p></article>`;}
  try {
    const res = await fetch("/visual-os/materiality-catalog/prisma.materiality-catalog.registry.3000-3150.json", { cache: "no-store" });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    const top = Object.keys(data).sort();
    const payload = {schema:data.schema_name||data.schema||data.name||"materiality-catalog",version:data.schema_version||data.version||"unknown",size_hint:"loaded from public Visual OS materiality route",top_level_keys:top,counts:{atmosphere_assets:count(data,["atmosphere_assets","assets","background_assets"]),background_recipes:count(data,["background_presets_from_gallery","background_recipes","background_presets"]),panel_presets:count(data,["panel_presets_from_gallery","panel_material_presets","panel_presets"]),ultra_codex_layers:count(data,["codex_layer_presets_preserved","layer_presets"]),governor_gates:count(data,["governor_gates","quality_gates"])}};
    summary.textContent = JSON.stringify(payload, null, 2);
    stats.innerHTML = card("Atmosphere Assets", payload.counts.atmosphere_assets, "Fondos reales gobernados como B1 Cloud/Image Field.") + card("Panel Presets", payload.counts.panel_presets, "Glass, rim, glow, motion y bundles de galería.") + card("Codex Layers", payload.counts.ultra_codex_layers, "Ultra Parametric preservado, no downgrade.");
  } catch (error) {
    summary.textContent = "No se pudo cargar registry: " + (error && error.message ? error.message : String(error));
    stats.innerHTML = card("Registry", "FAIL", "No se pudo leer el JSON público. Revisa que el inyector haya copiado payload/materiality-catalog.");
  }
})();
