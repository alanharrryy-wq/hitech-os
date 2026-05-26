(function () {
  const ABS_STORM_IMAGE = "/visual-os/tablet-light-visual-preset-engine/assets/backgrounds/storm-cloud-operations-real.jpg";
  const ABS_DISPLACEMENT_IMAGE = "/visual-os/tablet-light-visual-preset-engine/assets/backgrounds/liquid-operations-smoke.svg";
  const ABS_LIQUID_UI_IMAGE = "/visual-os/tablet-light-visual-preset-engine/assets/backgrounds/liquid-operations-ui-reference.png";

  const reducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const stage = document.querySelector("[data-liq-stage]");
  const title = document.querySelector("[data-liq-title]");
  const desc = document.querySelector("[data-liq-desc]");
  const tone = document.querySelector("[data-liq-tone]");
  const motion = document.querySelector("[data-liq-motion]");
  const buttons = Array.from(document.querySelectorAll("[data-liq-preset]"));
  const canvasEl = document.querySelector("[data-liq-vapor-canvas]");

  let pixiApp = null;
  let vaporTimeline = null;
  let vaporContainer = null;
  let vaporImage = null;
  let displacementSprite = null;
  let displacementFilter = null;
  let resizeHandlerBound = false;

  const presets = {
    "storm-cloud-operations-real": {
      title: "Hoy",
      tone: "Real storm image / vapor displacement",
      motion: reducedMotion
        ? "Static storm frame with frozen vapor"
        : "PixiJS displacement + GSAP stronger slow drift",
      desc:
        "Centro de decisiones con tormenta real más oscura, displacement vapor más visible y cristal con blur mínimo.",
      vapor: true,
      vaporImage: ABS_STORM_IMAGE
    },
    "liquid-operations-ui-reference": {
      title: "Liquid Ops",
      tone: "UI reference image / vapor showcase",
      motion: reducedMotion ? "Static UI reference frame" : "UI reference with more visible vapor",
      desc:
        "Imagen de referencia visual para Liquid Ops con vapor displacement más notorio y atmósfera más oscura.",
      vapor: true,
      vaporImage: ABS_LIQUID_UI_IMAGE
    },
    "tablet-soft-gray-clouds": {
      title: "Soft Clouds",
      tone: "Light / Tablet-safe candidate",
      motion: reducedMotion ? "Static reduced-motion frame" : "Still light comparison",
      desc:
        "Comparativo claro light-first para Tablet productiva. Sigue siendo el candidato seguro de producto.",
      vapor: false,
      vaporImage: ABS_STORM_IMAGE
    },
    "obsidian-cloud-motion": {
      title: "Obsidian Cloud",
      tone: "Dark / showcase only",
      motion: reducedMotion ? "Static cinematic frame" : "Dark cinematic comparison",
      desc:
        "Comparativo oscuro de showcase con nube procedural, sin activar vapor displacement.",
      vapor: false,
      vaporImage: ABS_STORM_IMAGE
    },
    "aurora-slate-veil": {
      title: "Aurora Slate",
      tone: "Dark / showcase only",
      motion: reducedMotion ? "Static cinematic frame" : "Dark aurora comparison",
      desc:
        "Pizarra oscura con aurora tenue y color frío controlado para comparar composición.",
      vapor: false,
      vaporImage: ABS_STORM_IMAGE
    }
  };

  async function ensurePixiVapor() {
    if (!canvasEl || !window.PIXI || pixiApp) return;

    try {
      pixiApp = new window.PIXI.Application();
      await pixiApp.init({
        canvas: canvasEl,
        width: canvasEl.clientWidth || window.innerWidth,
        height: canvasEl.clientHeight || window.innerHeight,
        resizeTo: canvasEl.parentElement,
        backgroundAlpha: 0,
        antialias: true,
        autoDensity: true,
        resolution: Math.min(window.devicePixelRatio || 1, 2)
      });

      vaporContainer = new window.PIXI.Container();
      pixiApp.stage.addChild(vaporContainer);

      const stormTexture = await window.PIXI.Assets.load(ABS_STORM_IMAGE);
      vaporImage = new window.PIXI.Sprite(stormTexture);
      vaporImage.anchor.set(0.5);
      vaporContainer.addChild(vaporImage);

      const displacementTexture = await window.PIXI.Assets.load(ABS_DISPLACEMENT_IMAGE);
      displacementSprite = new window.PIXI.Sprite(displacementTexture);
      displacementSprite.anchor.set(0.5);
      displacementSprite.alpha = 0.001;
      pixiApp.stage.addChild(displacementSprite);

      displacementFilter = new window.PIXI.DisplacementFilter(displacementSprite);
      displacementFilter.scale.x = reducedMotion ? 14 : 32;
      displacementFilter.scale.y = reducedMotion ? 10 : 22;
      vaporContainer.filters = [displacementFilter];

      const resize = function () {
        if (!pixiApp || !vaporImage || !displacementSprite) return;
        const host = canvasEl.parentElement;
        if (!host) return;
        const w = host.clientWidth || window.innerWidth;
        const h = host.clientHeight || window.innerHeight;
        const texture = vaporImage.texture;
        const tw = texture.width || 1;
        const th = texture.height || 1;
        const coverScale = Math.max(w / tw, h / th) * 1.04;
        vaporImage.scale.set(coverScale);
        vaporImage.position.set(w * 0.5, h * 0.52);
        displacementSprite.width = w * 1.4;
        displacementSprite.height = h * 1.4;
        displacementSprite.position.set(w * 0.5, h * 0.5);
      };

      resize();
      if (!resizeHandlerBound) {
        window.addEventListener("resize", resize);
        resizeHandlerBound = true;
      }

      if (!reducedMotion && window.gsap) {
        vaporTimeline = window.gsap.timeline({ repeat: -1, yoyo: true, defaults: { ease: "sine.inOut" } });
        vaporTimeline
          .to(displacementSprite, { x: "+=42", y: "-=20", rotation: 0.04, duration: 16 }, 0)
          .to(displacementFilter.scale, { x: 42, y: 28, duration: 14 }, 0)
          .to(displacementSprite, { x: "-=34", y: "+=18", rotation: -0.03, duration: 18 }, 16)
          .to(displacementFilter.scale, { x: 26, y: 18, duration: 18 }, 16)
          .to(vaporContainer, { alpha: 0.88, duration: 10 }, 0)
          .to(vaporContainer, { alpha: 0.62, duration: 12 }, 10);
      }
    } catch (error) {
      console.error("[PRISMA][storm-vapor-v14] Pixi init failed", error);
      stage && stage.setAttribute("data-vapor-enabled", "false");
    }
  }

  async function setVaporImage(src) {
    if (!window.PIXI || !vaporImage || !src) return;
    try {
      const tex = await window.PIXI.Assets.load(src);
      vaporImage.texture = tex;
      const host = canvasEl.parentElement;
      if (!host) return;
      const w = host.clientWidth || window.innerWidth;
      const h = host.clientHeight || window.innerHeight;
      const tw = tex.width || 1;
      const th = tex.height || 1;
      const coverScale = Math.max(w / tw, h / th) * 1.04;
      vaporImage.scale.set(coverScale);
      vaporImage.position.set(w * 0.5, h * 0.52);
    } catch (error) {
      console.error("[PRISMA][storm-vapor-v14] setVaporImage failed", error);
    }
  }

  function enableVapor(enabled) {
    if (!stage) return;
    stage.setAttribute("data-vapor-enabled", enabled ? "true" : "false");
    if (!enabled && vaporTimeline) {
      vaporTimeline.pause(0);
    } else if (enabled && vaporTimeline && !reducedMotion) {
      vaporTimeline.play();
    }
  }

  function setPreset(id) {
    const preset = presets[id] || presets["storm-cloud-operations-real"];
    if (stage) stage.setAttribute("data-preset", id);
    if (title) title.textContent = preset.title;
    if (desc) desc.textContent = preset.desc;
    if (tone) tone.textContent = preset.tone;
    if (motion) motion.textContent = preset.motion;
    buttons.forEach((btn) => {
      const active = btn.getAttribute("data-liq-preset") === id;
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
    setVaporImage(preset.vaporImage);
    enableVapor(!!preset.vapor);
  }

  buttons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const id = btn.getAttribute("data-liq-preset");
      if (!id) return;
      setPreset(id);
    });
  });

  ensurePixiVapor().finally(function () {
    setPreset("storm-cloud-operations-real");
  });
})();
